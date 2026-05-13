import os
import time
import json
import re
import pyautogui
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Union
from importlib import import_module

# Make backend modules (e.g. ai_editor_engine) importable from local_client
_backend_dir = str(Path(__file__).parent.parent / "backend")
if _backend_dir not in os.sys.path:
    os.sys.path.insert(0, _backend_dir)

# Optional imports for specific step types
try:
    from pygame import mixer
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    from flexisign_uia import FlexiSignUIA, FlexiSignUIAError
    FLEXISIGN_UIA_AVAILABLE = True
except ImportError:
    FLEXISIGN_UIA_AVAILABLE = False

try:
    from direct_path_executor import DirectPathExecutor, ExecutionResult
    DIRECT_PATH_EXECUTOR_AVAILABLE = True
except ImportError:
    DIRECT_PATH_EXECUTOR_AVAILABLE = False

try:
    from path_resolver import PathResolver, PathResolveResult
    PATH_RESOLVER_AVAILABLE = True
except ImportError:
    PATH_RESOLVER_AVAILABLE = False

try:
    from filename_resolver import FilenameResolver, ResolveResult
    FILENAME_RESOLVER_AVAILABLE = True
except ImportError:
    FILENAME_RESOLVER_AVAILABLE = False

try:
    from text_clicker import TextBasedClicker, ClickResult
    TEXT_CLICKER_AVAILABLE = True
except ImportError:
    TEXT_CLICKER_AVAILABLE = False

try:
    from readiness_detector import (
        BrowserReadinessDetector, 
        DesktopAppReadinessDetector, 
        FilesystemReadinessDetector,
        ReadinessResult
    )
    READINESS_DETECTOR_AVAILABLE = True
except ImportError:
    READINESS_DETECTOR_AVAILABLE = False

try:
    from file_operations import write_file, read_file, append_file, create_directory
    FILE_OPERATIONS_AVAILABLE = True
except ImportError:
    FILE_OPERATIONS_AVAILABLE = False

try:
    from file_editor import FileEditor
    FILE_EDITOR_AVAILABLE = True
except ImportError:
    FILE_EDITOR_AVAILABLE = False

try:
    from ai_editor_engine import AIEditorEngine, AIEditorEngineType
    AI_EDITOR_ENGINE_AVAILABLE = True
except ImportError:
    AI_EDITOR_ENGINE_AVAILABLE = False

try:
    from email_service import send_email_tool
    EMAIL_SERVICE_AVAILABLE = True
except ImportError:
    EMAIL_SERVICE_AVAILABLE = False

try:
    from debug_logger import get_debug_logger
    DEBUG_LOGGER_AVAILABLE = True
except ImportError:
    DEBUG_LOGGER_AVAILABLE = False

# Constants
START_SOUND = os.path.join(os.path.dirname(__file__), "assets", "start.mp3")
COMPLETE_SOUND = os.path.join(os.path.dirname(__file__), "assets", "complete.mp3")

def is_abort_requested() -> bool:
    """Check if the user has requested to abort the current task."""
    abort_file = Path(os.path.join(os.environ.get('TEMP', ''), 'jarvis_abort'))
    return abort_file.exists()

def _known_user_paths() -> Dict[str, str]:
    """Return stable placeholder values for common user folders."""
    home = Path.home()
    one_drive = os.environ.get("OneDrive") or os.environ.get("OneDriveConsumer")
    desktop = os.environ.get("DESKTOP_PATH")
    if not desktop and one_drive and (Path(one_drive) / "Desktop").exists():
        desktop = str(Path(one_drive) / "Desktop")
    if not desktop:
        desktop = str(home / "Desktop")

    return {
        "DESKTOP_PATH": desktop,
        "DOCUMENTS_PATH": os.environ.get("DOCUMENTS_PATH", str(home / "Documents")),
        "DOWNLOADS_PATH": os.environ.get("DOWNLOADS_PATH", str(home / "Downloads")),
        "WINDOWS_USERNAME": os.environ.get("USERNAME", home.name),
        "USERPROFILE": os.environ.get("USERPROFILE", str(home)),
    }

class PlanExecutor:
    """
    Main execution engine for JARVIS plans.
    Handles sequential execution of plan steps, window management,
    vision-based element identification, and direct automation paths.
    """
    
    # Timing constants
    DELAY_BEFORE_TYPING = 0.5
    DELAY_AFTER_STEP = 1.0
    DELAY_AFTER_HOTKEY = 0.8
    DELAY_AFTER_APP_LAUNCH = 5.0
    WINDOW_ACTIVATION_TIMEOUT = 10.0
    
    def __init__(self, vision_service, status_callback: Callable):
        """
        Initialize the PlanExecutor.
        
        Args:
            vision_service: Service for element detection and verification
            status_callback: Callback function for sending status updates
        """
        self.vision_service = vision_service
        self.status_callback = status_callback
        self.window_manager = None
        self._permission_service = None
        
        # Internal state
        self._id_map = None
        self._box_map = None
        self._screenshot_taken = False
        self._last_typed_text = None
        self._pending_app_name = None
        self._ui_changed_since_scan = False
        self._last_visual_click_index = -1
        self._mode = "vision"  # Default mode
        self._suppress_window_manager = False
        
        # Initialize sub-executors
        self._flexisign_uia = None
        self._direct_path_executor = None
        self._path_resolver = None
        self._filename_resolver = None
        self._text_clicker = None
        self._file_editor = None
        self._browser_detector = None
        self._desktop_detector = None
        self._filesystem_detector = None
        
        if DIRECT_PATH_EXECUTOR_AVAILABLE:
            try:
                self._direct_path_executor = DirectPathExecutor()
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize DirectPathExecutor: {e}")
                
        if PATH_RESOLVER_AVAILABLE:
            self._path_resolver = PathResolver()
            
        if FILENAME_RESOLVER_AVAILABLE:
            self._filename_resolver = FilenameResolver()
            
        if TEXT_CLICKER_AVAILABLE:
            self._text_clicker = TextBasedClicker()
            
        if FILE_EDITOR_AVAILABLE:
            self._file_editor = FileEditor()
            
        if READINESS_DETECTOR_AVAILABLE:
            self._browser_detector = BrowserReadinessDetector()
            self._desktop_detector = DesktopAppReadinessDetector()
            self._filesystem_detector = FilesystemReadinessDetector()

        # Initialize audio if available
        if AUDIO_AVAILABLE:
            try:
                mixer.init()
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize mixer: {e}")
        
        # Track last launched app for window activation
        self._last_launched_app: Optional[str] = None
        self._last_launch_step_index: int = -1
        
        # Initialize AI Editor Engine
        self._ai_editor_engine: Optional[AIEditorEngineType] = None
        if AI_EDITOR_ENGINE_AVAILABLE:
            try:
                self._ai_editor_engine = AIEditorEngine()
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize AIEditorEngine: {e}")
    
    def _send_status(self, message: str, status_type: str = "info", progress: int = None):
        """Send status update via callback."""
        if progress is not None:
            self.status_callback({
                'message': message,
                'progress': progress,
                'status': status_type
            }, status_type)
        else:
            self.status_callback(message, status_type)
    
    def _play_sound(self, sound_type: str):
        """
        Play audio feedback for execution events.
        
        Args:
            sound_type: Either 'start' or 'complete'
        """
        if not AUDIO_AVAILABLE:
            return
        
        try:
            sound_file = START_SOUND if sound_type == 'start' else COMPLETE_SOUND
            mixer.music.load(sound_file)
            mixer.music.play()
            # Don't wait for sound to finish - let it play in background
        except Exception as e:
            # Silently fail if audio playback has issues
            pass

    def _resolve_placeholders(self, value: str) -> str:
        """Resolve both %ENV% variables and planner-style {DESKTOP_PATH} tokens."""
        if not isinstance(value, str):
            return value

        resolved = os.path.expandvars(value)
        for key, path_value in _known_user_paths().items():
            resolved = resolved.replace(f"{{{key}}}", path_value)
        return resolved

    def _run_shell_command(self, command: str, timeout: int = 30) -> dict:
        """Run a shell command with Windows-friendly handling for common file tasks."""
        import subprocess as sp

        expanded = self._resolve_placeholders(command)
        result = {
            'success': False,
            'stdout': '',
            'stderr': '',
            'error_message': None,
            'observation': '',
            'command': expanded,
        }

        stripped = expanded.strip()
        lower = stripped.lower()

        try:
            if lower.startswith("explorer"):
                target = stripped[len("explorer"):].strip()
                if target:
                    target = target.strip('"')
                    sp.Popen(["explorer", target])
                    time.sleep(2.0)
                    result['success'] = True
                    result['observation'] = f"Explorer opened: {target}"
                    return result

            proc = sp.run(expanded, shell=True, capture_output=True, text=True, timeout=timeout)
            result['stdout'] = proc.stdout
            result['stderr'] = proc.stderr

            combined_output = f"{proc.stdout}\n{proc.stderr}".lower()
            mkdir_already_exists = (
                proc.returncode != 0
                and ("mkdir" in lower or lower.startswith("md "))
                and "already exists" in combined_output
            )

            result['success'] = proc.returncode == 0 or mkdir_already_exists
            if result['success']:
                if mkdir_already_exists:
                    result['observation'] = "Directory already exists; treating as complete."
                else:
                    result['observation'] = f"Command succeeded. Output: {proc.stdout[:200]}"
            else:
                result['observation'] = f"Command failed (exit code {proc.returncode}). Error: {proc.stderr[:200]}"

            if lower.startswith("start ") or " start " in lower:
                time.sleep(4.0)

        except sp.TimeoutExpired:
            result['stderr'] = f'Command timed out after {timeout} seconds'
            result['observation'] = 'Shell command timed out'
        except Exception as e:
            result['error_message'] = str(e)
            result['observation'] = f"Shell execution error: {str(e)}"

        return result
    
    def set_permission_service(self, permission_service: 'PermissionService'):
        """Set the permission service for critical operation checks."""
        self._permission_service = permission_service

    def execute_plan(self, plan: dict, verify: bool = True) -> dict:
        """
        Execute an execution plan from the Planner Model.
        Routes to direct or vision mode based on plan['mode'].
        
        Args:
            plan: Execution plan dict with "sequence" array and optional "mode"
            verify: Whether to verify task completion after execution
        
        Returns:
            dict: Execution result with keys:
                - success: bool - whether execution completed
                - verified: bool - whether verification passed (if verify=True)
                - verification_result: dict - full verification details (if verify=True)
                - aborted: bool - whether execution was aborted by user
        """
        sequence = plan.get('sequence', [])
        if not sequence:
            self._send_status("Empty execution plan", "warning")
            return {"success": False, "verified": False, "verification_result": None, "aborted": False}
        
        mode = plan.get('mode', 'vision')
        expected_state = plan.get('expected_final_state', '')
        
        # Check for abort before starting
        if is_abort_requested():
            self._send_status("Task aborted by user", "warning")
            return {"success": False, "verified": False, "verification_result": None, "aborted": True}
        
        # Route to appropriate execution mode
        if mode in ('direct', 'flexisign'):
            exec_result = self._execute_direct_plan(plan)
        else:
            exec_result = self._execute_vision_plan(plan)
        
        # Check if aborted during execution
        if isinstance(exec_result, dict) and exec_result.get("aborted", False):
            return {"success": False, "verified": False, "verification_result": None, "aborted": True}
        
        exec_success = exec_result if isinstance(exec_result, bool) else exec_result.get("success", False)
        
        # Perform verification if requested and expected_state is provided
        verification_result = None
        verified = True  # Default to True if no verification
        
        if verify and expected_state and exec_success:
            # Load verification settings from environment variables
            verification_delay = float(os.environ.get('VERIFICATION_DELAY', 1.0))
            
            self._send_status("Verifying task completion...", "info", progress=92)
            time.sleep(verification_delay)  # Wait for UI to settle (configurable)
            
            try:
                verification_result = self.vision_service.verify_task_completion(expected_state)
                verified = verification_result.get("success", False)
                confidence = verification_result.get("confidence", 0)
                
                if verified:
                    self._send_status(
                        f"✓ Task verified successfully (confidence: {confidence:.0%})", 
                        "success", progress=98
                    )
                else:
                    current_state = verification_result.get("current_state", "Unknown")
                    missing = verification_result.get("missing_elements", [])
                    self._send_status(
                        f"⚠ Verification failed: {current_state}", 
                        "warning", progress=95
                    )
                    if missing:
                        self._send_status(f"Missing: {', '.join(missing)}", "warning")
                        
            except Exception as e:
                self._send_status(f"Verification error: {e}", "warning")
                verification_result = {"success": False, "error": str(e)}
        
        return {
            "success": exec_success,
            "verified": verified,
            "verification_result": verification_result,
            "aborted": False
        }

    def execute_single_step(self, step: dict) -> dict:
        """
        Execute a single atomic step for ReAct loop.
        Maps the step to the correct internal handler and captures feedback.
        """
        step_type = step.get('type')
        step_desc = step.get('desc', f"Executing {step_type}")
        
        self._send_status(f"⚡ Executing step: {step_desc}", "info")
        
        result = {
            'success': False,
            'stdout': '',
            'stderr': '',
            'error_message': None,
            'observation': '',
            'files_modified': []
        }
        
        try:
            # Check for permission on critical operations
            if self._permission_service and self._permission_service.is_critical_operation(step):
                if not self._permission_service.request_permission_for_step(step):
                    result['error_message'] = 'Permission denied by user'
                    result['observation'] = 'Permission denied by user'
                    return result
            
            # Route to correct handler
            if step_type == 'keyboard':
                # For single step, we don't have the sequence context
                self._execute_keyboard_step(step, [step], 0)
                result['success'] = True
                
            elif step_type == 'shell_command':
                cmd = step.get('command', '')
                if not cmd:
                    result['success'] = False
                    result['error_message'] = "Missing 'command' parameter"
                else:
                    result.update(self._run_shell_command(cmd))
                
            elif step_type == 'visual_click':
                target = step.get('target_name')
                if not self._screenshot_taken:
                    self._perform_vision_pass([target])
                self._execute_visual_click(target)
                result['success'] = True
                
            elif step_type == 'write_file':
                result['success'] = self._execute_write_file_step(step)
                if result['success'] and step.get('path'):
                    result['files_modified'] = [step.get('path')]
                
            elif step_type == 'read_file':
                path = self._resolve_placeholders(step.get('path', ''))
                read_performed = False
                if path and os.path.isdir(path):
                    result['success'] = True
                    result['observation'] = f"Directory exists: {path}"
                    result['stdout'] = result['observation']
                else:
                    result['success'] = self._execute_read_file_step(step)
                    read_performed = True
                if read_performed and result['success'] and hasattr(self, 'last_read_content'):
                    result['content'] = self.last_read_content
                    result['stdout'] = self.last_read_content
                    result['observation'] = f"Read file content ({len(self.last_read_content)} chars)"

            elif step_type in ('path_exists', 'directory_exists'):
                path = self._resolve_placeholders(step.get('path', ''))
                exists = os.path.exists(path) if path else False
                is_dir = os.path.isdir(path) if path else False
                result['success'] = is_dir if step_type == 'directory_exists' else exists
                result['stdout'] = f"path={path}; exists={exists}; is_dir={is_dir}"
                result['observation'] = result['stdout']
                    
            elif step_type == 'open_file':
                res = self._execute_open_file_step(step)
                result['success'] = res.success
                result['error_message'] = getattr(res, 'error_message', None)
                
            elif step_type == 'open_folder':
                res = self._execute_open_folder_step(step)
                result['success'] = res.success
                result['error_message'] = getattr(res, 'error_message', None)
            
            # Add other step types as needed...
            else:
                # Fallback to general execute logic if type exists
                handler_name = f"_execute_{step_type}_step"
                if hasattr(self, handler_name):
                    handler = getattr(self, handler_name)
                    res = handler(step)
                    
                    # Robust result handling for different return types (bool, object, dict)
                    if isinstance(res, bool):
                        result['success'] = res
                    elif isinstance(res, dict):
                        result['success'] = res.get('success', False)
                        result['error_message'] = res.get('error_message')
                        result['stdout'] = res.get('stdout', '')
                        result['stderr'] = res.get('stderr', '')
                        if 'observation' in res:
                            result['observation'] = res['observation']
                    else:
                        # Assume object with .success attribute (e.g. ExecutionResult, ClickResult)
                        result['success'] = getattr(res, 'success', False)
                        result['error_message'] = getattr(res, 'error_message', None)
                else:
                    result['success'] = False
                    result['error_message'] = f"Unknown step type: {step_type}"
                    result['observation'] = f"Unknown step type: {step_type}"
                    
        except Exception as e:
            self._send_status(f"Error in single step: {e}", "error")
            result['success'] = False
            result['error_message'] = str(e)
            
        return result

    def execute_verify_task(self, expected_state: str) -> dict:
        """Verify task completion using Vision Service."""
        try:
            self._send_status(f"Verifying state: {expected_state}", "info")
            time.sleep(1.0) # Settle time
            
            res = self.vision_service.verify_task_completion(expected_state)
            return {
                'success': res.get('success', False),
                'observation': res.get('current_state', 'Unknown state'),
                'confidence': res.get('confidence', 0)
            }
        except Exception as e:
            return {'success': False, 'observation': f"Verification error: {str(e)}"}

    def _execute_direct_plan(self, plan: dict) -> dict:
        """
        Execute plan using UIA (no vision/screenshots).
        
        Args:
            plan: Execution plan dict with "sequence" array
            
        Returns:
            dict: Result with 'success' and 'aborted' keys
        """
        if not FLEXISIGN_UIA_AVAILABLE:
            self._send_status("FlexiSIGN UIA module not available", "error")
            return {"success": False, "aborted": False}
        
        sequence = plan.get('sequence', [])
        total_steps = len(sequence)
        
        self._send_status(f"Starting direct automation of {total_steps} steps", "info", progress=25)
        
        # Initialize UIA if needed
        if self._flexisign_uia is None:
            try:
                self._flexisign_uia = FlexiSignUIA()
            except Exception as e:
                self._send_status(f"Failed to initialize FlexiSIGN UIA: {e}", "error")
                return {"success": False, "aborted": False}
        
        # Activate FlexiSIGN window
        if not self._flexisign_uia.find_and_activate_window():
            self._send_status("Failed to activate FlexiSIGN window", "error")
            return {"success": False, "aborted": False}
        
        self._send_status("FlexiSIGN window activated", "info", progress=5)
        
        # Execute each step
        for i, step in enumerate(sequence):
            # Check for abort signal
            if is_abort_requested():
                self._send_status("Task aborted by user", "warning", progress=0)
                return {"success": False, "aborted": True}
            
            step_order = step.get('order', i + 1)
            step_desc = step.get('desc', f"Step {step_order}")
            
            # Check for permission on critical operations
            if self._permission_service and self._permission_service.is_critical_operation(step):
                self._send_status(f"⚠️ Critical operation detected: {step_desc}", "warning")
                if not self._permission_service.request_permission_for_step(step):
                    self._send_status(f"Permission denied for step {step_order}, skipping...", "warning")
                    continue
            
            progress = int(((i + 1) / total_steps) * 65) + 25
            self._send_status(f"Step {step_order}: {step_desc}", "info", progress=progress)
            
            try:
                success = self._execute_direct_step(step, sequence, i)
                if not success:
                    self._send_status(f"Step {step_order} failed", "warning")
                    
                if DEBUG_LOGGER_AVAILABLE:
                    get_debug_logger().log_step_execution(
                        step_order, step.get('type', 'unknown'),
                        f"desc='{step_desc}' success={success}"
                    )
                    
            except FlexiSignUIAError as e:
                self._send_status(f"UIA Error in step {step_order}: {e}", "error")
                if DEBUG_LOGGER_AVAILABLE:
                    get_debug_logger().log_step_execution(
                        step_order, step.get('type', 'unknown'),
                        f"UIA ERROR: {e}", success=False
                    )
                continue
            except Exception as e:
                self._send_status(f"Error in step {step_order}: {e}", "error")
                if DEBUG_LOGGER_AVAILABLE:
                    get_debug_logger().log_step_execution(
                        step_order, step.get('type', 'unknown'),
                        f"ERROR: {e}", success=False
                    )
                continue
        
        self._send_status("Direct automation complete!", "info", progress=95)
        return {"success": True, "aborted": False}
    
    def _execute_vision_plan(self, plan: dict) -> dict:
        """
        Execute plan using vision-based pipeline (existing logic).
        
        Args:
            plan: Execution plan dict with "sequence" array
            
        Returns:
            dict: Result with 'success' and 'aborted' keys
        """
        sequence = plan.get('sequence', [])
        self._mode = plan.get('mode', 'general')
        
        total_steps = len(sequence)
        self._send_status(f"Starting execution of {total_steps} steps (mode: {self._mode})", "info", progress=25)
        
        # Play start sound
        self._play_sound('start')
        
        # Reset state for new plan
        self._id_map = None
        self._box_map = None
        self._screenshot_taken = False
        self._pending_app_name = None
        self._last_typed_text = None
        self._ui_changed_since_scan = False
        self._last_visual_click_index = -1
        
        # Execute steps
        for i, step in enumerate(sequence):
            # Check for abort signal
            if is_abort_requested():
                self._send_status("Task aborted by user", "warning", progress=0)
                return {"success": False, "aborted": True}
            
            step_order = step.get('order', i + 1)
            step_type = step.get('type')
            step_desc = step.get('desc', f"Step {step_order}")
            
            # Check for permission on critical operations
            if self._permission_service and self._permission_service.is_critical_operation(step):
                self._send_status(f"⚠️ Critical operation detected: {step_desc}", "warning")
                if not self._permission_service.request_permission_for_step(step):
                    self._send_status(f"Permission denied for step {step_order}, skipping...", "warning")
                    continue
            
            progress = int(((i + 1) / total_steps) * 65) + 25
            self._send_status(f"Step {step_order}: {step_desc}", "info", progress=progress)
            
            try:
                step_result = True  # Default to success
                
                if step_type == 'keyboard':
                    self._execute_keyboard_step(step, sequence, i)
                    
                    # Mark UI as changed if this was a typing action (not just navigation keys)
                    value = step.get('value', '').lower()
                    if not self._is_special_key(value) or value in ['enter', 'return', 'backspace', 'delete', 'del']:
                        # Typing text or pressing Enter/Backspace can change UI content
                        self._ui_changed_since_scan = True
                    
                elif step_type == 'visual_click':
                    target_name = step.get('target_name')
                    if not target_name:
                        self._send_status(f"Missing target_name in step {step_order}", "warning")
                        step_result = False
                    else:
                        # CRITICAL: Wait for application/page readiness before first visual click
                        if not self._screenshot_taken:
                            self._wait_for_readiness_before_vision(sequence, i)
                        
                        # Adaptive re-scanning: Check if we need to re-scan
                        needs_rescan = False
                        
                        if not self._screenshot_taken:
                            # First visual click - always scan
                            needs_rescan = True
                        elif self._ui_changed_since_scan:
                            # UI has changed since last scan - need to re-scan
                            needs_rescan = True
                            self._send_status("UI changed detected, re-scanning for visual elements...", "info")
                        
                        if needs_rescan:
                            # Collect remaining visual targets from this point forward
                            remaining_targets = self._collect_remaining_visual_targets(sequence, i)
                            if remaining_targets:
                                self._perform_vision_pass(remaining_targets)
                                self._ui_changed_since_scan = False
                        
                        self._execute_visual_click(target_name)
                        self._last_visual_click_index = i
                    
                elif step_type == 'shell_command':
                    res = self._execute_shell_command_step(step)
                    step_result = res.get('success', False)
                    # Shell commands often change UI
                    self._ui_changed_since_scan = True
                    
                elif step_type == 'write_file':
                    step_result = self._execute_write_file_step(step)
                    
                elif step_type == 'read_file':
                    step_result = self._execute_read_file_step(step)
                    
                elif step_type == 'append_file':
                    step_result = self._execute_append_file_step(step)
                    
                elif step_type == 'create_directory':
                    step_result = self._execute_create_directory_step(step)
                    
                elif step_type == 'open_file':
                    res = self._execute_open_file_step(step)
                    step_result = getattr(res, 'success', False)
                    self._ui_changed_since_scan = True
                    
                elif step_type == 'open_folder':
                    res = self._execute_open_folder_step(step)
                    step_result = getattr(res, 'success', False)
                    self._ui_changed_since_scan = True
                    
                elif step_type == 'save_file':
                    res = self._execute_save_file_step(step)
                    step_result = getattr(res, 'success', False)
                    
                elif step_type == 'resolve_filename':
                    res = self._execute_resolve_filename_step(step)
                    step_result = getattr(res, 'success', False)
                    
                elif step_type == 'navigate_explorer':
                    res = self._execute_navigate_explorer_step(step)
                    step_result = getattr(res, 'success', False)
                    self._ui_changed_since_scan = True
                    
                elif step_type == 'click_text':
                    res = self._execute_click_text_step(step)
                    step_result = getattr(res, 'success', False)
                    self._ui_changed_since_scan = True
                    
                elif step_type == 'click_text_fast':
                    res = self._execute_click_text_fast_step(step)
                    step_result = getattr(res, 'success', False)
                    self._ui_changed_since_scan = True
                    
                elif step_type == 'ai_edit_text':
                    step_result = self._execute_ai_edit_text_step(step)
                    
                elif step_type == 'ai_edit_excel':
                    step_result = self._execute_ai_edit_excel_step(step)
                    
                elif step_type == 'ai_edit_word':
                    res = self._execute_ai_edit_word_step(step)
                    step_result = res.get('success', False) if isinstance(res, dict) else res
                    if isinstance(res, dict) and not step_result:
                        self._send_status(f"ai_edit_word failed: {res.get('error_message')}", "error")
                    
                elif step_type == 'delete_file':
                    step_result = self._execute_delete_file_step(step)
                    
                elif step_type == 'delete_folder':
                    step_result = self._execute_delete_folder_step(step)
                    
                elif step_type == 'send_email':
                    step_result = self._execute_send_email_step(step)
                    
                elif step_type == 'web_automation':
                    res = self._execute_web_automation_step(step)
                    step_result = getattr(res, 'success', False)
                    self._ui_changed_since_scan = True
                
                # Check for failure in step result
                if not step_result:
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, step_type, 
                            f"FAILED: {step_desc}", success=False
                        )
                    # For sequential plans, failure in one step often stops the rest
                    # But for now, we'll continue to keep parity with previous behavior, 
                    # but actually LOG the failure.
                    # self._send_status(f"Step {step_order} failed", "warning")
                else:
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, step_type, 
                            f"desc='{step_desc}'", success=True
                        )
                    
            except Exception as e:
                self._send_status(f"Error in step {step_order}: {e}", "error")
                if DEBUG_LOGGER_AVAILABLE:
                    get_debug_logger().log_step_execution(
                        step_order, step_type, 
                        f"ERROR: {e}", success=False
                    )
                # Continue with next step unless it's a critical failure
                continue
                
        # Play complete sound
        self._play_sound('complete')
        self._send_status("Execution complete!", "success", progress=90)
        
        return {"success": True, "aborted": False}

    def _perform_vision_pass(self, targets: List[str]):
        """
        Take a screenshot and detect elements for the given targets.
        
        Args:
            targets: List of element names to detect
        """
        self._send_status(f"Scanning UI for elements: {', '.join(targets[:3])}...", "info")
        
        # Take screenshot
        screenshot_path = self.vision_service.take_screenshot()
        self._screenshot_taken = True
        
        # Detect elements
        detection_result = self.vision_service.detect_elements(screenshot_path, targets)
        
        self._id_map = detection_result.get('id_map', {})
        self._box_map = detection_result.get('box_map', {})
        
        found_count = len(self._id_map)
        self._send_status(f"UI scan complete. Found {found_count}/{len(targets)} elements.", "info")
    
    def _collect_remaining_visual_targets(self, sequence: List[dict], start_index: int) -> List[str]:
        """
        Collect all visual_click targets from the current step onwards.
        Used for batch element detection.
        """
        targets = []
        for i in range(start_index, len(sequence)):
            step = sequence[i]
            if step.get('type') == 'visual_click':
                target = step.get('target_name')
                if target and target not in targets:
                    targets.append(target)
        return targets

    def _get_app_name_from_context(self, sequence: list, current_index: int) -> Optional[str]:
        """
        Try to determine the application name from the current or previous steps.
        Used for intelligent window activation.
        """
        # 1. Check if we're in an 'open_file' or 'open_folder' sequence
        # The Planner often names the app in the 'desc' of the next step
        for i in range(current_index, min(current_index + 3, len(sequence))):
            desc = sequence[i].get('desc', '').lower()
            # Match "Click [element] in [App]"
            match = re.search(r'in ([a-z0-9\s]+)$', desc)
            if match:
                app_name = match.group(1).strip()
                # Skip generic words
                if app_name not in ['the window', 'the screen', 'the app']:
                    return app_name
        
        # 2. Check if we just typed something that looks like an app name
        if self._last_typed_text:
            value = self._last_typed_text.strip()
            value_lower = value.lower()
            # Common apps
            for app in ['excel', 'word', 'powerpoint', 'chrome', 'firefox', 'edge', 'notepad', 'calc', 'cmd', 'powershell', 'vlc', 'flexisign']:
                if app in value_lower:
                    return app
            
            # If it's a short single word, it might be an app name
            if ' ' not in value and 3 <= len(value) <= 15:
                # Skip if it looks like a file path
                if '\\' in value or '/' in value:
                    pass
                # Skip terminal commands (python, node, npm, git, etc.)
                elif any(value_lower.startswith(cmd) for cmd in ['python ', 'node ', 'npm ', 'git ', 'pip ', 'java ', 'javac ', 'gcc ', 'g++ ', 'make ', 'cargo ', 'go ', 'ruby ', 'perl ', 'php ']):
                    pass
                # Skip if it contains file extensions (likely a command with file argument)
                elif any(ext in value_lower for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.rb', '.go', '.rs', '.sh', '.bat', '.cmd']):
                    pass
                else:
                    return value
        
        # 3. Fallback to previously typed text if available
        if self._last_typed_text:
            last_lower = self._last_typed_text.lower()
            if any(cmd in last_lower for cmd in ['cmd /c', 'cmd.exe /c', 'mkdir', 'rmdir', 'del ', 'copy ', 'move ', 'ren ']):
                return None
            if '\\' in self._last_typed_text or '/' in self._last_typed_text:
                return None
            # Skip terminal commands
            if any(last_lower.startswith(cmd) for cmd in ['python ', 'node ', 'npm ', 'git ', 'pip ', 'java ', 'javac ', 'gcc ', 'g++ ', 'make ', 'cargo ', 'go ', 'ruby ', 'perl ', 'php ']):
                return None
            # Skip if it contains file extensions
            if any(ext in last_lower for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.rb', '.go', '.rs', '.sh', '.bat', '.cmd']):
                return None
            
            return self._last_typed_text
        
        return None
    
    def _execute_keyboard_step(self, step: dict, sequence: list, current_index: int) -> None:
        """
        Execute a keyboard action step with proper timing and window management.
        """
        value = step.get('value', '')
        repeats = step.get('repeats', 1)
        desc = step.get('desc', '')
        
        if not value:
            return
        
        # Ensure window is focused before keyboard input (unless suppressed for modal dialogs)
        if self.window_manager and not self._suppress_window_manager:
            self.window_manager.ensure_foreground_before_input()
        
        # Determine if this is an app launch
        is_app_launch = self._is_app_launch_step(step, sequence, current_index)
        
        # Track typed text for app name detection
        if not self._is_special_key(value.lower()) and '+' not in value and len(value) > 1:
            self._last_typed_text = value
        
        # Small delay before typing text (not for special keys)
        if not self._is_special_key(value.lower()) and '+' not in value:
            time.sleep(self.DELAY_BEFORE_TYPING)
        
        # Execute the keyboard action
        for rep in range(repeats):
            if '+' in value and self._is_hotkey(value):
                self._execute_hotkey(value)
                time.sleep(self.DELAY_AFTER_HOTKEY)
            elif self._is_special_key(value.lower()):
                pyautogui.press(value.lower())
                time.sleep(self.DELAY_AFTER_STEP)
            elif len(value) == 1:
                pyautogui.press(value)
                time.sleep(0.05)
            else:
                # Text to type - Handle embedded special keys like {enter}, {tab}
                if '{' in value and '}' in value:
                    parts = re.split(r'(\{enter\}|\{return\}|\{tab\}|\{space\}|\{backspace\}|\{delete\}|\{del\}|\{esc\}|\{escape\}|\{up\}|\{down\}|\{left\}|\{right\})', value, flags=re.IGNORECASE)
                    for part in parts:
                        if not part:
                            continue
                        
                        lower_part = part.lower()
                        if lower_part.startswith('{') and lower_part.endswith('}'):
                            key = lower_part[1:-1]
                            # Normalize aliases
                            if key == 'ret': key = 'return'
                            if key == 'esc': key = 'escape'
                            if key == 'del': key = 'delete'
                            
                            pyautogui.press(key)
                        else:
                            pyautogui.typewrite(part, interval=0.03)
                else:
                    # Regular text without embedded keys
                    pyautogui.typewrite(value, interval=0.03)
                
                time.sleep(self.DELAY_AFTER_STEP)
            
            if repeats > 1 and rep < repeats - 1:
                time.sleep(0.1)
        
        # Handle app launch: wait for window and activate it
        if is_app_launch:
            self._handle_app_launch(sequence, current_index)
    
    def _handle_app_launch(self, sequence: list, current_index: int):
        """
        Handle post-app-launch window activation.
        Tracks launched app for readiness detection.
        """
        # Skip if window manager is suppressed (during modal dialogs)
        if self._suppress_window_manager:
            return
        
        if not self.window_manager:
            # Fallback: just wait
            self._send_status("Waiting for application to start...", "info")
            time.sleep(self.DELAY_AFTER_APP_LAUNCH)
            return
        
        # Try to determine what app was launched
        app_name = self._get_app_name_from_context(sequence, current_index)
        
        # Track for readiness detection
        if app_name:
            self._last_launched_app = app_name.lower()
            self._last_launch_step_index = current_index
        
        if app_name:
            self._send_status(f"Waiting for {app_name} window...", "info")
            
            # Wait for window to appear and activate it
            success = self.window_manager.wait_and_activate(
                app_name, 
                timeout=self.WINDOW_ACTIVATION_TIMEOUT
            )
            
            if success:
                self._send_status(f"{app_name} window activated", "info")
                # Additional settle time
                time.sleep(0.5)
            else:
                self._send_status(f"Could not find {app_name} window, continuing anyway...", "warning")
                time.sleep(self.DELAY_AFTER_APP_LAUNCH)
        else:
            # Unknown app, just wait
            self._send_status("Waiting for application...", "info")
            time.sleep(self.DELAY_AFTER_APP_LAUNCH)
            
            # Try to activate whatever window is now in front
            fg_title = self.window_manager.get_foreground_window_title()
            if fg_title:
                self._send_status(f"Active window: {fg_title}", "info")
    
    def _is_hotkey(self, value: str) -> bool:
        """Check if value is a hotkey combination vs regular text with '+'."""
        modifiers = {'ctrl', 'alt', 'shift', 'win', 'cmd', 'command', 'meta', 'super', 'windows'}
        parts = value.lower().split('+')
        return any(part.strip() in modifiers for part in parts)
    
    def _is_special_key(self, value: str) -> bool:
        """Check if value is a special key name."""
        special_keys = {
            'enter', 'return', 'tab', 'space', 'backspace', 'delete', 'del',
            'escape', 'esc', 'up', 'down', 'left', 'right',
            'home', 'end', 'pageup', 'pagedown', 'pgup', 'pgdn',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
            'insert', 'pause', 'capslock', 'numlock', 'scrolllock',
            'printscreen', 'prtsc', 'prtscr', 'win', 'windows', 'command', 'cmd'
        }
        return value.lower() in special_keys
    
    def _execute_hotkey(self, hotkey: str) -> None:
        """Execute a hotkey combination like 'ctrl+n' or 'win+r'."""
        keys = [k.strip().lower() for k in hotkey.split('+')]
        
        key_map = {
            'win': 'win',
            'windows': 'win',
            'super': 'win',
            'cmd': 'command',
            'ctrl': 'ctrl',
            'control': 'ctrl',
            'alt': 'alt',
            'shift': 'shift',
        }
        
        mapped_keys = [key_map.get(k, k) for k in keys]
        pyautogui.hotkey(*mapped_keys)
    
    def _execute_visual_click(self, target_name: str) -> None:
        """
        Execute a visual click on a target element.
        Ensures window is focused before clicking.
        """
        # Ensure window is focused before clicking (unless suppressed for modal dialogs)
        if self.window_manager and not self._suppress_window_manager:
            self.window_manager.ensure_foreground_before_input()
        
        if self._id_map is None or self._box_map is None:
            self._send_status(f"Cannot click '{target_name}': vision data not available", "warning")
            return
        
        element_id = self._id_map.get(target_name)
        
        # Fallback for canvas_center - use screen center
        if element_id is None and 'canvas' in target_name.lower():
            screen_width, screen_height = pyautogui.size()
            cx = screen_width * 0.5
            cy = screen_height * 0.5
            self._send_status(f"Using screen center fallback for '{target_name}'", "info")
            pyautogui.click(int(cx), int(cy))
            time.sleep(self.DELAY_AFTER_STEP)
            return
        
        if element_id is None:
            self._send_status(f"Target '{target_name}' not found in ID map - skipping", "warning")
            return
        
        # Get coordinates from box_map
        element_id_str = str(element_id)
        coords = self._box_map.get(element_id_str)
        if coords is None:
            self._send_status(f"Element ID {element_id} not found in box map", "warning")
            return
        
        # Calculate center point
        x1, y1, x2, y2 = coords
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        
        self._send_status(f"Clicking '{target_name}' at ({int(cx)}, {int(cy)})", "info")
        pyautogui.click(int(cx), int(cy))
        time.sleep(self.DELAY_AFTER_STEP)
    
    # =========================================================================
    # Direct Path Automation Step Handlers
    # Requirements: 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 3.3, 4.1
    # =========================================================================
    
    def _execute_save_file_step(self, step: dict) -> "ExecutionResult":
        """
        Reliable and log-safe save_file handler.
        """
        if not DIRECT_PATH_EXECUTOR_AVAILABLE or self._direct_path_executor is None:
            from direct_path_executor import create_error_result
            return create_error_result(
                operation="save",
                path=step.get("path", ""),
                error_type="executor_unavailable",
                error_message="DirectPathExecutor is not available"
            )

        raw_path = step.get("path", "")
        overwrite_policy = step.get("overwrite_policy")  # Optional override

        if not raw_path or not isinstance(raw_path, str):
            from direct_path_executor import create_error_result
            return create_error_result(
                operation="save",
                path="",
                error_type="invalid_path",
                error_message="Missing or invalid 'path'"
            )

        import os
        normalized_path = os.path.normpath(raw_path)
        filename_only = os.path.basename(normalized_path) or "file"

        self._send_status(f"save_file: preparing to save '{filename_only}'", "info")

        if any(c in normalized_path for c in ['*', '?', '"', '<', '>', '|']):
            from direct_path_executor import create_error_result
            return create_error_result(
                operation="save",
                path=normalized_path,
                error_type="invalid_path",
                error_message="Path contains invalid filename characters"
            )

        if self.window_manager and not self._suppress_window_manager:
            self.window_manager.ensure_foreground_before_input()
            time.sleep(0.15)

        original_policy = None
        if overwrite_policy is not None and self._direct_path_executor.config:
            original_policy = self._direct_path_executor.config.overwrite_policy
            self._direct_path_executor.config.overwrite_policy = overwrite_policy

        self._suppress_window_manager = True
        
        saved_hwnd = None
        if self.window_manager:
            saved_hwnd = self.window_manager._last_activated_hwnd
            self.window_manager._last_activated_hwnd = None
        
        try:
            self._send_status(f"save_file: executing save for '{filename_only}'", "info")
            result = self._direct_path_executor.execute_save(normalized_path)

        finally:
            self._suppress_window_manager = False
            if self.window_manager and saved_hwnd:
                self.window_manager._last_activated_hwnd = saved_hwnd
            if original_policy is not None and self._direct_path_executor.config:
                self._direct_path_executor.config.overwrite_policy = original_policy

        if result.success:
            self._send_status(f"save_file: saved '{filename_only}' successfully", "success")
        else:
            self._send_status(
                f"save_file failed for '{filename_only}': {result.error_message}",
                "warning"
            )

        return result
    
    def _execute_open_file_step(self, step: dict) -> 'PathResolveResult':
        """
        Execute an open_file step - resolve path and open file directly.
        """
        import os
        import subprocess
        
        if not PATH_RESOLVER_AVAILABLE or self._path_resolver is None:
            self._send_status("PathResolver not available for open_file step", "error")
            from path_resolver import PathResolveResult
            return PathResolveResult(
                success=False,
                error_message="PathResolver is not available"
            )
        
        path_query = step.get('path', '')
        
        if not path_query:
            self._send_status("open_file: missing 'path' parameter", "warning")
            from path_resolver import PathResolveResult
            return PathResolveResult(
                success=False,
                error_message="Path parameter is required"
            )
        
        self._send_status(f"Resolving file path: '{path_query}'", "info")
        result = self._path_resolver.resolve(path_query)
        
        if not result.success:
            self._send_status(f"✗ Could not resolve path: {result.error_message}", "warning")
            return result
        
        for step_msg in result.resolution_steps:
            self._send_status(step_msg, "info")
        
        resolved_path = result.resolved_path
        self._send_status(f"✓ Resolved to: {resolved_path}", "success")
        
        if not os.path.exists(resolved_path):
            result.success = False
            result.error_message = f"File does not exist: {resolved_path}"
            self._send_status(f"✗ {result.error_message}", "warning")
            return result
        
        if not os.path.isfile(resolved_path):
            result.success = False
            result.error_message = f"Path is not a file: {resolved_path}"
            self._send_status(f"✗ {result.error_message}", "warning")
            return result
        
        try:
            self._send_status(f"Opening file: {resolved_path}", "info")
            os.startfile(resolved_path)
            time.sleep(1.0)
            self._send_status(f"✓ File opened successfully", "success")
            return result
        except Exception as e:
            result.success = False
            result.error_message = f"Failed to open file: {str(e)}"
            self._send_status(f"✗ {result.error_message}", "error")
            return result
    
    def _execute_open_folder_step(self, step: dict) -> 'PathResolveResult':
        """
        Execute an open_folder step - resolve path and open folder in Explorer.
        """
        import os
        import subprocess
        
        if not PATH_RESOLVER_AVAILABLE or self._path_resolver is None:
            self._send_status("PathResolver not available for open_folder step", "error")
            from path_resolver import PathResolveResult
            return PathResolveResult(
                success=False,
                error_message="PathResolver is not available"
            )
        
        path_query = step.get('path', '')
        
        if not path_query:
            self._send_status("open_folder: missing 'path' parameter", "warning")
            from path_resolver import PathResolveResult
            return PathResolveResult(
                success=False,
                error_message="Path parameter is required"
            )
        
        self._send_status(f"Resolving folder path: '{path_query}'", "info")
        
        max_retries = 3
        retry_delay = 0.5
        result = None
        
        for attempt in range(max_retries):
            result = self._path_resolver.resolve(path_query)
            if result.success:
                break
            time.sleep(retry_delay)
        
        if not result.success:
            self._send_status(f"✗ Could not resolve path after {max_retries} attempts: {result.error_message}", "warning")
            return result
        
        for step_msg in result.resolution_steps:
            self._send_status(step_msg, "info")
        
        resolved_path = result.resolved_path
        self._send_status(f"✓ Resolved to: {resolved_path}", "success")
        
        if READINESS_DETECTOR_AVAILABLE and self._filesystem_detector:
            readiness_result = self._filesystem_detector.wait_for_folder_accessible(
                resolved_path,
                timeout=3.0
            )
            if not readiness_result.is_ready:
                result.success = False
                result.error_message = f"Folder not accessible: {readiness_result.message}"
                self._send_status(f"✗ {result.error_message}", "warning")
                return result
        else:
            if not os.path.exists(resolved_path):
                result.success = False
                result.error_message = f"Folder does not exist: {resolved_path}"
                self._send_status(f"✗ {result.error_message}", "warning")
                return result
            
        try:
            self._send_status(f"Opening folder in Explorer: {resolved_path}", "info")
            subprocess.Popen(['explorer', resolved_path])
            time.sleep(0.5)
            self._send_status(f"✓ Folder opened successfully", "success")
            return result
        except Exception as e:
            result.success = False
            result.error_message = f"Failed to open folder: {str(e)}"
            self._send_status(f"✗ {result.error_message}", "error")
            return result
    
    def _execute_resolve_filename_step(self, step: dict) -> 'ResolveResult':
        """
        Execute a resolve_filename step using filesystem-based fuzzy matching.
        """
        if not FILENAME_RESOLVER_AVAILABLE or self._filename_resolver is None:
            self._send_status("FilenameResolver not available for resolve_filename step", "error")
            from filename_resolver import ResolveResult
            return ResolveResult(
                success=False,
                error_message="FilenameResolver is not available"
            )
        
        directory = step.get('directory', '')
        query = step.get('query', '')
        
        if not directory or not query:
            from filename_resolver import ResolveResult
            return ResolveResult(success=False, error_message="Directory and query parameters are required")
        
        self._send_status(f"Resolving filename: '{query}' in {directory}", "info")
        result = self._filename_resolver.resolve(directory, query)
        
        if result.success:
            self._send_status(f"✓ Resolved '{query}' → '{result.resolved_name}'", "success")
        else:
            self._send_status(f"✗ Could not resolve '{query}': {result.error_message}", "warning")
        
        return result
    
    def _execute_navigate_explorer_step(self, step: dict) -> 'ExecutionResult':
        """
        Execute a navigate_explorer step using address bar navigation.
        """
        if not DIRECT_PATH_EXECUTOR_AVAILABLE or self._direct_path_executor is None:
            from direct_path_executor import create_error_result
            return create_error_result(operation="navigate", path=step.get('directory', ''), error_type="executor_unavailable")
        
        directory = step.get('directory', '')
        if not directory:
            from direct_path_executor import create_error_result
            return create_error_result(operation="navigate", path='', error_type="invalid_path")
        
        self._send_status(f"Executing navigate_explorer: {directory}", "info")
        result = self._direct_path_executor.navigate_explorer(directory)
        
        if result.success:
            self._send_status(f"navigate_explorer completed: {directory}", "success")
        else:
            self._send_status(f"navigate_explorer failed: {result.error_message}", "warning")
        
        return result
    
    def _execute_ai_edit_text_step(self, step: dict) -> dict:
        """Execute AI-powered text editing."""
        if not AI_EDITOR_ENGINE_AVAILABLE or self._ai_editor_engine is None:
            return {'success': False, 'error_message': 'AI Editor Engine is not available'}
        
        path_query = step.get('path', '')
        prompt = step.get('prompt', '')
        
        resolve_result = self._path_resolver.resolve(path_query)
        if not resolve_result.success:
            return {'success': False, 'error_message': f"Path resolution failed: {resolve_result.error_message}"}
        
        file_path = resolve_result.resolved_path
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self._send_status(f"AI is proposing changes to {os.path.basename(file_path)}...", "info")
            edits = self._ai_editor_engine.get_text_edits(content, prompt)
            new_content = self._ai_editor_engine.apply_text_edits(content, edits.edits)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            self._send_status(f"✓ AI edits applied to {os.path.basename(file_path)}", "success")
            return {'success': True, 'error_message': None}
        except Exception as e:
            self._send_status(f"AI text edit error: {e}", "error")
            return {'success': False, 'error_message': str(e)}

    def _execute_ai_edit_excel_step(self, step: dict) -> dict:
        """Execute AI-powered Excel editing."""
        if not AI_EDITOR_ENGINE_AVAILABLE or self._ai_editor_engine is None:
            return {'success': False, 'error_message': 'AI Editor Engine is not available'}
        
        path_query = step.get('path', '')
        prompt = step.get('prompt', '')
        
        resolve_result = self._path_resolver.resolve(path_query)
        if not resolve_result.success:
            return {'success': False, 'error_message': f"Path resolution failed: {resolve_result.error_message}"}
        
        file_path = resolve_result.resolved_path
        
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path)
            context = self._ai_editor_engine.extract_excel_context(wb)
            edits = self._ai_editor_engine.get_excel_edits(context, prompt)
            
            self._ai_editor_engine.apply_excel_edits(wb, edits.commands)
            wb.save(file_path)
            return {'success': True, 'error_message': None}
        except Exception as e:
            self._send_status(f"AI excel edit error: {e}", "error")
            return {'success': False, 'error_message': str(e)}

    def _execute_ai_edit_word_step(self, step: dict) -> dict:
        """Execute AI-powered Word document editing."""
        if not AI_EDITOR_ENGINE_AVAILABLE or self._ai_editor_engine is None:
            return {'success': False, 'error_message': 'AI Editor Engine is not available'}

        path_query = step.get('path', '')
        prompt = step.get('prompt', '')

        resolve_result = self._path_resolver.resolve(path_query)
        if not resolve_result.success:
            return {'success': False, 'error_message': f"Path resolution failed for '{path_query}': {resolve_result.error_message}"}

        file_path = resolve_result.resolved_path

        try:
            import docx
            import os
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                doc = docx.Document()
                doc.save(file_path)
            else:
                doc = docx.Document(file_path)

            context = self._ai_editor_engine.extract_word_context(doc)
            edits = self._ai_editor_engine.get_word_edits(context, prompt)

            self._ai_editor_engine.apply_word_edits(doc, edits.edits)
            doc.save(file_path)
            return {'success': True, 'error_message': None}
        except Exception as e:
            return {'success': False, 'error_message': f"Word edit failed: {str(e)}"}
    
    def _execute_click_text_step(self, step: dict) -> 'ClickResult':
        """
        Execute a click_text step using OCR-based text detection.
        """
        if not TEXT_CLICKER_AVAILABLE or self._text_clicker is None:
            from text_clicker import create_failure_result
            return create_failure_result(target_text=step.get('text', ''), error_message="TextBasedClicker is not available")
        
        text = step.get('text', '')
        if not text:
            from text_clicker import create_failure_result
            return create_failure_result(target_text='', error_message="Text parameter is required")
        
        double_click = step.get('double_click', False)
        region = step.get('region')
        
        if region and isinstance(region, list):
            region = tuple(region)
        
        self._send_status(f"Executing click_text: '{text}'", "info")
        
        if double_click:
            result = self._text_clicker.double_click_text(text, region=region)
        else:
            result = self._text_clicker.click_text(text, region=region)
        
        if result.success:
            self._send_status(f"click_text completed: '{text}'", "success")
        else:
            self._send_status(f"click_text failed: {result.error_message}", "warning")
        
        return result
    
    def _execute_click_text_fast_step(self, step: dict) -> dict:
        """
        Execute a click_text_fast step using fast window-specific OCR.
        """
        window_title = step.get('window_title', '')
        text = step.get('text', '')
        
        if not window_title or not text:
            return {'success': False, 'error_message': "Missing parameters"}
        
        try:
            FastTextClicker = import_module("backend.text_click_fast").FastTextClicker
            clicker = FastTextClicker()
            result = clicker.click_text_in_window(window_title, text)
            if result['success']:
                self._send_status(f"click_text_fast completed: '{text}'", "success")
            return result
        except Exception as e:
            return {'success': False, 'error_message': str(e)}

    def _execute_delete_file_step(self, step: dict) -> bool:
        """Execute a delete_file step."""
        import os
        file_path = step.get('path', '')
        if not file_path: return False
        file_path = os.path.normpath(file_path)
        if not os.path.isfile(file_path): return False
        try:
            os.remove(file_path)
            self._send_status(f"✓ File deleted: {os.path.basename(file_path)}", "success")
            return True
        except Exception: return False
    
    def _execute_delete_folder_step(self, step: dict) -> bool:
        """Execute a delete_folder step."""
        import os, shutil
        folder_path = step.get('path', '')
        if not folder_path: return False
        folder_path = os.path.normpath(folder_path)
        if not os.path.isdir(folder_path): return False
        try:
            shutil.rmtree(folder_path)
            self._send_status(f"✓ Folder deleted: {os.path.basename(folder_path)}", "success")
            return True
        except Exception: return False
    
    def _execute_shell_command_step(self, step: dict) -> bool:
        """Execute a shell_command step."""
        command = step.get('command', '')
        if not command: return False
        return self._run_shell_command(command).get('success', False)
    
    def _wait_for_readiness_before_vision(self, sequence: list, current_step_index: int):
        """Wait for application/page readiness before taking screenshot for vision."""
        if not READINESS_DETECTOR_AVAILABLE:
            time.sleep(2.0)
            return
        time.sleep(0.5)
    
    def _execute_write_file_step(self, step: dict) -> bool:
        """Execute a write_file step."""
        if not FILE_OPERATIONS_AVAILABLE: return False
        path = step.get('path', '')
        content = step.get('content', '')
        if not path: return False
        try:
            success, _ = write_file(path, content)
            return success
        except Exception: return False
    
    def _execute_read_file_step(self, step: dict) -> bool:
        """Execute a read_file step."""
        if not FILE_OPERATIONS_AVAILABLE: return False
        path = step.get('path', '')
        if not path: return False
        path = self._resolve_placeholders(path)
        if os.path.isdir(path):
            self.last_read_content = f"Directory exists: {path}"
            self.last_read_path = path
            return True
        try:
            success, _, content = read_file(path)
            if success:
                self.last_read_content = content
                self.last_read_path = path
            return success
        except Exception: return False

    def _execute_path_exists_step(self, step: dict) -> bool:
        """Execute a path_exists step."""
        path = self._resolve_placeholders(step.get('path', ''))
        return bool(path and os.path.exists(path))

    def _execute_directory_exists_step(self, step: dict) -> bool:
        """Execute a directory_exists step."""
        path = self._resolve_placeholders(step.get('path', ''))
        return bool(path and os.path.isdir(path))
    
    def _execute_append_file_step(self, step: dict) -> bool:
        """Execute an append_file step."""
        if not FILE_OPERATIONS_AVAILABLE: return False
        path = step.get('path', '')
        content = step.get('content', '')
        if not path or not content: return False
        try:
            success, _ = append_file(path, content)
            return success
        except Exception: return False
    
    def _execute_create_directory_step(self, step: dict) -> bool:
        """Execute a create_directory step."""
        if not FILE_OPERATIONS_AVAILABLE: return False
        path = step.get('path', '')
        if not path: return False
        try:
            success, _ = create_directory(path)
            return success
        except Exception: return False
    
    def _execute_replace_in_file_step(self, step: dict) -> bool:
        """Execute a replace_in_file step."""
        if not FILE_EDITOR_AVAILABLE: return False
        path = step.get('path', '')
        old_text = step.get('old_text', '')
        new_text = step.get('new_text', '')
        if not path or not old_text: return False
        try:
            success, _, _ = self._file_editor.replace_in_file(path, old_text, new_text)
            return success
        except Exception: return False
    
    def _execute_modify_lines_step(self, step: dict) -> bool:
        """Execute a modify_lines step."""
        if not FILE_EDITOR_AVAILABLE: return False
        path = step.get('path', '')
        line_number = step.get('line_number')
        new_content = step.get('new_content', '')
        if not path or line_number is None: return False
        try:
            success, _, _ = self._file_editor.modify_lines(path, line_number, new_content)
            return success
        except Exception: return False
    
    def _execute_insert_at_line_step(self, step: dict) -> bool:
        """Execute an insert_at_line step."""
        if not FILE_EDITOR_AVAILABLE: return False
        path = step.get('path', '')
        line_number = step.get('line_number')
        content = step.get('content', '')
        if not path or line_number is None: return False
        try:
            success, _, _ = self._file_editor.insert_at_line(path, line_number, content)
            return success
        except Exception: return False
    
    def _execute_delete_lines_step(self, step: dict) -> bool:
        """Execute a delete_lines step."""
        if not FILE_EDITOR_AVAILABLE: return False
        path = step.get('path', '')
        start_line = step.get('start_line')
        end_line = step.get('end_line')
        if not path or start_line is None: return False
        try:
            success, _, _ = self._file_editor.delete_lines(path, start_line, end_line)
            return success
        except Exception: return False

    def _execute_send_email_step(self, step: dict) -> bool:
        """Execute a send_email step."""
        if not EMAIL_SERVICE_AVAILABLE: return False
        recipient = step.get('recipient_email')
        subject = step.get('subject')
        body = step.get('body')
        if not all([recipient, subject, body]): return False
        try:
            success, _ = send_email_tool(recipient_email=recipient, subject=subject, body=body)
            return success
        except Exception: return False

    def _execute_web_automation_step(self, step: dict) -> bool:
        """Execute a web_automation step."""
        prompt = step.get('prompt')
        if not prompt: return False
        try:
            # Simplified mock for reconstruction
            self._send_status(f"Starting web AI agent: {prompt}", "info")
            return True
        except Exception: return False

    def _is_app_launch_step(self, step: dict, sequence: list, current_index: int) -> bool:
        """Check if a keyboard step is likely launching an application."""
        value = step.get('value', '').lower()
        if value == 'win' or value == 'command': return True
        return False

    def _execute_direct_step(self, step: dict, sequence: list, index: int) -> bool:
        """Execute a single step in direct automation mode."""
        step_type = step.get('type')
        if step_type == 'keyboard':
            self._execute_keyboard_step(step, sequence, index)
            return True
        elif step_type == 'visual_click':
            # This shouldn't happen in pure direct mode, but handle it
            return False
        return False

def get_click_coordinates(element_id: int, box_map: dict) -> tuple[float, float] | None:
    """Calculate click coordinates from box map."""
    element_id_str = str(element_id)
    coords = box_map.get(element_id_str)
    if coords is None: return None
    x1, y1, x2, y2 = coords
    return ((x1 + x2) / 2, (y1 + y2) / 2)
