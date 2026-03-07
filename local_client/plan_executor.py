"""
Plan Executor for Two-Model Pipeline
Executes execution plans using keyboard/mouse actions with vision-guided clicking.
Includes robust window activation and timing management.
Supports direct path automation for file operations.
"""

import time
import re
import os
from pathlib import Path
from typing import Callable, Optional

import pyautogui

# Safety settings
pyautogui.FAILSAFE = False  # Disable fail-safe (corner abort) for uninterrupted automation
pyautogui.PAUSE = 0.05  # Minimal pause, we handle timing ourselves

# Audio feedback
try:
    from pygame import mixer
    try:
        mixer.init()
        AUDIO_AVAILABLE = True
        
        # Get paths to audio files
        ASSETS_DIR = Path(__file__).parent / "assets"
        START_SOUND = str(ASSETS_DIR / "Start.mp3")
        COMPLETE_SOUND = str(ASSETS_DIR / "Complete.mp3")
        
        # Verify files exist
        if not os.path.exists(START_SOUND) or not os.path.exists(COMPLETE_SOUND):
            print("⚠️ Warning: Audio files not found in assets folder")
            AUDIO_AVAILABLE = False
    except Exception as e:
        AUDIO_AVAILABLE = False
        print(f"⚠️ Warning: pygame audio initialization failed ({e}). Audio feedback disabled.")
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️ Warning: pygame not available for audio feedback. Install with: pip install pygame")

try:
    from vision_service import VisionService
    VISION_SERVICE_AVAILABLE = True
except ImportError:
    VISION_SERVICE_AVAILABLE = False
    print("⚠️ Warning: vision_service not available")

try:
    from window_manager import WindowManager, get_window_manager
    WINDOW_MANAGER_AVAILABLE = True
except ImportError:
    WINDOW_MANAGER_AVAILABLE = False
    print("⚠️ Warning: window_manager not available")

try:
    from debug_logger import get_debug_logger
    DEBUG_LOGGER_AVAILABLE = True
except ImportError:
    DEBUG_LOGGER_AVAILABLE = False

try:
    from flexisign_uia import FlexiSignUIA, FlexiSignUIAError
    FLEXISIGN_UIA_AVAILABLE = True
except ImportError:
    FLEXISIGN_UIA_AVAILABLE = False
    print("⚠️ Warning: flexisign_uia not available")

# Direct Path Automation imports
try:
    from direct_path_executor import DirectPathExecutor, ExecutionResult
    DIRECT_PATH_EXECUTOR_AVAILABLE = True
except ImportError:
    DIRECT_PATH_EXECUTOR_AVAILABLE = False
    print("⚠️ Warning: direct_path_executor not available")

try:
    from text_clicker import TextBasedClicker, ClickResult
    TEXT_CLICKER_AVAILABLE = True
except ImportError:
    TEXT_CLICKER_AVAILABLE = False
    print("⚠️ Warning: text_clicker not available")

try:
    from path_config import PathConfig
    PATH_CONFIG_AVAILABLE = True
except ImportError:
    PATH_CONFIG_AVAILABLE = False
    print("⚠️ Warning: path_config not available")

try:
    from filename_resolver import FilenameResolver, ResolveResult
    FILENAME_RESOLVER_AVAILABLE = True
except ImportError:
    FILENAME_RESOLVER_AVAILABLE = False
    print("⚠️ Warning: filename_resolver not available")

try:
    from path_resolver import PathResolver, PathResolveResult
    PATH_RESOLVER_AVAILABLE = True
except ImportError:
    PATH_RESOLVER_AVAILABLE = False
    print("⚠️ Warning: path_resolver not available")

# Permission service import (optional)
try:
    from permission_service import PermissionService, is_abort_requested
    PERMISSION_SERVICE_AVAILABLE = True
except ImportError:
    PERMISSION_SERVICE_AVAILABLE = False
    def is_abort_requested():
        return False

# Readiness detection imports
try:
    from readiness_detector import (
        get_browser_detector, get_desktop_detector, get_filesystem_detector,
        ReadinessState
    )
    READINESS_DETECTOR_AVAILABLE = True
except ImportError:
    READINESS_DETECTOR_AVAILABLE = False
    print("⚠️ Warning: readiness_detector not available")

# File operations import (Plane 2: Code Workspace Control)
try:
    import sys
    backend_path = Path(__file__).parent.parent / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    from file_operations import write_file, read_file, append_file, create_directory
    FILE_OPERATIONS_AVAILABLE = True
except ImportError:
    FILE_OPERATIONS_AVAILABLE = False
    print("⚠️ Warning: file_operations not available")

# Intelligent file editor import
try:
    import sys
    backend_path = Path(__file__).parent.parent / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    from file_editor import FileEditor
    FILE_EDITOR_AVAILABLE = True
except ImportError:
    FILE_EDITOR_AVAILABLE = False
    print("⚠️ Warning: file_editor not available")

# AI Editor Engine import
try:
    import sys
    backend_path = Path(__file__).parent.parent / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    from ai_editor_engine import AIEditorEngine
    AI_EDITOR_ENGINE_AVAILABLE = True
except ImportError:
    AI_EDITOR_ENGINE_AVAILABLE = False
    print("⚠️ Warning: ai_editor_engine not available")

# Email service import
try:
    import sys
    backend_path = Path(__file__).parent.parent / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    from email_service import send_email_tool
    EMAIL_SERVICE_AVAILABLE = True
except ImportError:
    EMAIL_SERVICE_AVAILABLE = False
    print("⚠️ Warning: email_service not available")


class PlanExecutor:
    """
    Executes execution plans from the Planner Model.
    
    Features:
    - Single-pass vision architecture (screenshot once, reuse coordinates)
    - Robust window activation before keyboard/mouse input
    - Configurable delays for different action types
    - App launch detection with window polling
    """
    
    # Timing configuration (seconds)
    DELAY_AFTER_STEP = 0.3          # Default delay after each step
    DELAY_AFTER_APP_LAUNCH = 3.0    # Extended delay after launching an app
    DELAY_AFTER_HOTKEY = 0.5        # Delay after hotkey combinations
    DELAY_BEFORE_TYPING = 0.2       # Small delay before typing text
    WINDOW_ACTIVATION_TIMEOUT = 10.0  # Max time to wait for window activation
    
    # Patterns that indicate an app launch
    APP_LAUNCH_PATTERNS = [
        r'^win(?!\+)',     # Windows key alone (not win+something like win+r)
        # Note: 'enter' is handled specially in _is_app_launch_step based on context
        # Note: win+r opens Run dialog, not an app directly
        # Note: ctrl+n creates new documents/tabs, not new app windows
    ]
    
    # Keywords in step descriptions that indicate app launch
    APP_LAUNCH_KEYWORDS = [
        'launch', 'open', 'start', 'run',
        'new window', 'new tab'
    ]
    
    def __init__(self, vision_service: VisionService, status_callback: Optional[Callable] = None):
        """
        Initialize PlanExecutor.
        
        Args:
            vision_service: VisionService instance for screenshot/SoM/mapping
            status_callback: Optional callback for progress updates
        """
        self.vision_service = vision_service
        self.status_callback = status_callback or (lambda msg, status="info": print(f"[{status}] {msg}"))
        
        # Window manager for activation
        self.window_manager = get_window_manager(verbose=True) if WINDOW_MANAGER_AVAILABLE else None
        
        # FlexiSIGN UIA module for direct automation
        self._flexisign_uia: Optional['FlexiSignUIA'] = None
        
        # Direct Path Automation components
        self._path_config: Optional['PathConfig'] = None
        self._direct_path_executor: Optional['DirectPathExecutor'] = None
        self._text_clicker: Optional['TextBasedClicker'] = None
        
        # Initialize path config if available
        if PATH_CONFIG_AVAILABLE:
            try:
                self._path_config = PathConfig.load()
            except Exception as e:
                print(f"⚠️ Warning: Could not load path config: {e}")
        
        # Initialize direct path executor if available
        if DIRECT_PATH_EXECUTOR_AVAILABLE:
            try:
                self._direct_path_executor = DirectPathExecutor(
                    config=self._path_config,
                    status_callback=self.status_callback
                )
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize DirectPathExecutor: {e}")
        
        # Initialize text clicker if available
        if TEXT_CLICKER_AVAILABLE:
            try:
                self._text_clicker = TextBasedClicker()
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize TextBasedClicker: {e}")
        
        # Initialize filename resolver if available
        self._filename_resolver: Optional['FilenameResolver'] = None
        if FILENAME_RESOLVER_AVAILABLE:
            try:
                self._filename_resolver = FilenameResolver()
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize FilenameResolver: {e}")
        
        # File content cache for read-modify-write operations
        self.last_read_content = None
        self.last_read_path = None
        
        # Initialize file editor for intelligent editing
        self._file_editor: Optional['FileEditor'] = None
        if FILE_EDITOR_AVAILABLE:
            try:
                self._file_editor = FileEditor()
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize FileEditor: {e}")
        
        # Initialize path resolver if available
        self._path_resolver: Optional['PathResolver'] = None
        if PATH_RESOLVER_AVAILABLE:
            try:
                self._path_resolver = PathResolver()
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize PathResolver: {e}")
        
        # Permission service (set externally via set_permission_service)
        self._permission_service: Optional['PermissionService'] = None
        
        # Cached vision data (single-pass architecture)
        self._id_map: Optional[dict] = None
        self._box_map: Optional[dict] = None
        self._screenshot_taken: bool = False
        self._mode: str = "general"
        
        # Track app launches for window activation
        self._pending_app_name: Optional[str] = None
        self._last_typed_text: Optional[str] = None
        
        # Window manager suppression flag for modal dialogs (Save/Open)
        self._suppress_window_manager: bool = False
        
        # Track UI state changes for adaptive re-scanning
        self._ui_changed_since_scan: bool = False
        self._last_visual_click_index: int = -1
        
        # Readiness detectors
        self._browser_detector = get_browser_detector(self.status_callback) if READINESS_DETECTOR_AVAILABLE else None
        self._desktop_detector = get_desktop_detector(self.status_callback) if READINESS_DETECTOR_AVAILABLE else None
        self._filesystem_detector = get_filesystem_detector(self.status_callback) if READINESS_DETECTOR_AVAILABLE else None
        
        # Track last app launch for readiness detection
        self._last_launched_app: Optional[str] = None
        self._last_launch_step_index: int = -1
        
        # Initialize AI Editor Engine
        self._ai_editor_engine: Optional['AIEditorEngine'] = None
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
        # 'direct' or 'flexisign' both use direct automation
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
            # Load verification delay from config
            try:
                from config import VERIFICATION_DELAY
                verification_delay = VERIFICATION_DELAY
            except ImportError:
                verification_delay = 1.0  # Default fallback
            
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
                verified = False
        
        return {
            "success": exec_success,
            "verified": verified,
            "verification_result": verification_result,
            "aborted": False
        }
    
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
                if step_type == 'keyboard':
                    self._execute_keyboard_step(step, sequence, i)
                    
                    # Mark UI as changed if this was a typing action (not just navigation keys)
                    value = step.get('value', '').lower()
                    if not self._is_special_key(value) or value in ['enter', 'return', 'backspace', 'delete', 'del']:
                        # Typing text or pressing Enter/Backspace can change UI content
                        self._ui_changed_since_scan = True
                    
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "keyboard", 
                            f"value='{step.get('value', '')}' desc='{step_desc}'"
                        )
                    
                elif step_type == 'visual_click':
                    target_name = step.get('target_name')
                    if not target_name:
                        self._send_status(f"Missing target_name in step {step_order}", "warning")
                        continue
                    
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
                    
                    # Mark UI as changed since clicking can trigger navigation or UI updates
                    self._ui_changed_since_scan = True
                    
                    if DEBUG_LOGGER_AVAILABLE:
                        element_id = self._id_map.get(target_name) if self._id_map else None
                        get_debug_logger().log_step_execution(
                            step_order, "visual_click",
                            f"target='{target_name}' id={element_id} desc='{step_desc}'"
                        )
                
                # Direct Path Automation step types
                elif step_type == 'save_file':
                    result = self._execute_save_file_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "save_file",
                            f"path='{step.get('path', '')}' success={result.success} desc='{step_desc}'"
                        )
                
                elif step_type == 'ai_edit_text':
                    self._execute_ai_edit_text_step(step)
                elif step_type == 'ai_edit_excel':
                    self._execute_ai_edit_excel_step(step)
                elif step_type == 'ai_edit_word':
                    self._execute_ai_edit_word_step(step)

                elif step_type == 'open_file':
                    result = self._execute_open_file_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "open_file",
                            f"path_query='{step.get('path', '')}' success={result.success} desc='{step_desc}'"
                        )
                
                elif step_type == 'open_folder':
                    result = self._execute_open_folder_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "open_folder",
                            f"path_query='{step.get('path', '')}' success={result.success} desc='{step_desc}'"
                        )
                
                elif step_type == 'resolve_filename':
                    result = self._execute_resolve_filename_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "resolve_filename",
                            f"directory='{step.get('directory', '')}' query='{step.get('query', '')}' success={result.success} resolved='{result.resolved_name if result.success else 'N/A'}' desc='{step_desc}'"
                        )
                
                elif step_type == 'navigate_explorer':
                    result = self._execute_navigate_explorer_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "navigate_explorer",
                            f"directory='{step.get('directory', '')}' success={result.success} desc='{step_desc}'"
                        )
                    
                    # Add extra delay after navigate_explorer for UI to settle and text to render
                    # This helps OCR-based click_text steps that follow
                    time.sleep(0.5)
                
                elif step_type == 'click_text':
                    # Wait for readiness if UI has changed (e.g., after navigation)
                    if self._ui_changed_since_scan:
                        self._wait_for_readiness_before_vision(sequence, i)
                        self._ui_changed_since_scan = False
                    
                    result = self._execute_click_text_step(step)
                    
                    # Add delay after click to allow UI to respond
                    time.sleep(self.DELAY_AFTER_STEP)
                    
                    # Mark UI as changed since clicking can trigger navigation or UI updates
                    self._ui_changed_since_scan = True
                    
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "click_text",
                            f"text='{step.get('text', '')}' success={result.success} desc='{step_desc}'"
                        )
                
                elif step_type == 'click_text_fast':
                    # Wait for readiness if UI has changed (e.g., after navigation)
                    if self._ui_changed_since_scan:
                        self._wait_for_readiness_before_vision(sequence, i)
                        self._ui_changed_since_scan = False
                    
                    result = self._execute_click_text_fast_step(step)
                    
                    # Add delay after click to allow UI to respond
                    time.sleep(self.DELAY_AFTER_STEP)
                    
                    # Mark UI as changed since clicking can trigger navigation or UI updates
                    self._ui_changed_since_scan = True
                    
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "click_text_fast",
                            f"window='{step.get('window_title', '')}' text='{step.get('text', '')}' success={result.get('success', False)} desc='{step_desc}'"
                        )
                
                # Critical operations that require permission
                elif step_type == 'delete_file':
                    result = self._execute_delete_file_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "delete_file",
                            f"path='{step.get('path', '')}' success={result} desc='{step_desc}'"
                        )
                
                elif step_type == 'delete_folder':
                    result = self._execute_delete_folder_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "delete_folder",
                            f"path='{step.get('path', '')}' success={result} desc='{step_desc}'"
                        )
                
                elif step_type == 'shell_command':
                    result = self._execute_shell_command_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "shell_command",
                            f"command='{step.get('command', '')}' success={result} desc='{step_desc}'"
                        )
                
                # Plane 2: Code Workspace Control operations
                elif step_type == 'write_file':
                    result = self._execute_write_file_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "write_file",
                            f"path='{step.get('path', '')}' success={result} desc='{step_desc}'"
                        )
                
                elif step_type == 'read_file':
                    result = self._execute_read_file_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "read_file",
                            f"path='{step.get('path', '')}' success={result} desc='{step_desc}'"
                        )
                
                elif step_type == 'append_file':
                    result = self._execute_append_file_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "append_file",
                            f"path='{step.get('path', '')}' success={result} desc='{step_desc}'"
                        )
                
                elif step_type == 'create_directory':
                    result = self._execute_create_directory_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "create_directory",
                            f"path='{step.get('path', '')}' success={result} desc='{step_desc}'"
                        )
                
                # Intelligent file editing operations
                elif step_type == 'replace_in_file':
                    result = self._execute_replace_in_file_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "replace_in_file",
                            f"path='{step.get('path', '')}' old='{step.get('old_text', '')[:50]}' new='{step.get('new_text', '')[:50]}' success={result} desc='{step_desc}'"
                        )
                
                elif step_type == 'modify_lines':
                    result = self._execute_modify_lines_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "modify_lines",
                            f"path='{step.get('path', '')}' line={step.get('line_number')} success={result} desc='{step_desc}'"
                        )
                
                elif step_type == 'insert_at_line':
                    result = self._execute_insert_at_line_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "insert_at_line",
                            f"path='{step.get('path', '')}' line={step.get('line_number')} success={result} desc='{step_desc}'"
                        )
                
                elif step_type == 'delete_lines':
                    result = self._execute_delete_lines_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "delete_lines",
                            f"path='{step.get('path', '')}' start={step.get('start_line')} end={step.get('end_line')} success={result} desc='{step_desc}'"
                        )
                
                elif step_type == 'send_email':
                    result = self._execute_send_email_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "send_email",
                            f"to='{step.get('recipient_email', '')}' subject='{step.get('subject', '')}' success={result} desc='{step_desc}'"
                        )
                
                elif step_type == 'web_automation':
                    result = self._execute_web_automation_step(step)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "web_automation",
                            f"prompt='{step.get('prompt', '')[:50]}' success={result} desc='{step_desc}'"
                        )
                
                else:
                    self._send_status(f"Unknown step type: {step_type}", "warning")
                
            except Exception as e:
                self._send_status(f"Error in step {step_order}: {e}", "error")
                if DEBUG_LOGGER_AVAILABLE:
                    get_debug_logger().log_step_execution(
                        step_order, step_type, f"ERROR: {e}", success=False
                    )
                continue
        
        self._send_status("Execution complete!", "info", progress=95)
        
        # Play completion sound
        self._play_sound('complete')
        
        return {"success": True, "aborted": False}
    
    def _execute_direct_step(self, step: dict, sequence: list, current_index: int) -> bool:
        """
        Execute a single direct automation step.
        Dispatches to UIA actions based on step type.
        
        Supports: create_text, set_dimensions, set_font, apply_style, move_object, keyboard, ensure_designcentral
        
        Args:
            step: Step dict with 'type' and type-specific parameters
            sequence: Full sequence list (for keyboard step context)
            current_index: Current step index in sequence
            
        Returns:
            bool: True if step executed successfully
        """
        step_type = step.get('type')
        
        if step_type == 'keyboard':
            # Use existing keyboard execution logic
            self._execute_keyboard_step(step, sequence, current_index)
            return True
        
        elif step_type == 'ensure_designcentral':
            # Ensure DesignCentral panel is open
            if not self._flexisign_uia.ensure_designcentral_open():
                self._send_status("ensure_designcentral: failed to open DesignCentral panel", "warning")
                return False
            return True
        
        elif step_type == 'create_text':
            text = step.get('text', '')
            if not text:
                self._send_status("create_text: missing 'text' parameter", "warning")
                return False
            return self._flexisign_uia.create_text(text)
        
        elif step_type == 'set_dimensions':
            width = step.get('width', '')
            height = step.get('height', '')
            if not width or not height:
                self._send_status("set_dimensions: missing 'width' or 'height' parameter", "warning")
                return False
            return self._flexisign_uia.set_dimensions(str(width), str(height))
        
        elif step_type == 'set_font':
            font_name = step.get('font_name', '')
            if not font_name:
                self._send_status("set_font: missing 'font_name' parameter", "warning")
                return False
            return self._flexisign_uia.set_font(font_name)
        
        elif step_type == 'apply_style':
            style_name = step.get('style_name')  # Optional
            return self._flexisign_uia.apply_style(style_name)
        
        elif step_type == 'move_object':
            direction = step.get('direction', '')
            distance = step.get('distance', 1)
            if not direction:
                self._send_status("move_object: missing 'direction' parameter", "warning")
                return False
            return self._flexisign_uia.move_object(direction, int(distance))
        
        else:
            self._send_status(f"Unknown direct step type: {step_type}", "warning")
            return False
    
    def _collect_visual_targets(self, sequence: list) -> list[str]:
        """Collect all unique visual target names from the sequence."""
        targets = []
        for step in sequence:
            if step.get('type') == 'visual_click':
                target = step.get('target_name')
                if target and target not in targets:
                    targets.append(target)
        return targets
    
    def _collect_remaining_visual_targets(self, sequence: list, current_index: int) -> list[str]:
        """
        Collect visual targets from current_index onwards.
        Used for adaptive re-scanning when UI has changed.
        """
        targets = []
        for i in range(current_index, len(sequence)):
            step = sequence[i]
            if step.get('type') == 'visual_click':
                target = step.get('target_name')
                if target and target not in targets:
                    targets.append(target)
        return targets
    
    def _perform_vision_pass(self, targets: list[str]):
        """Perform single-pass vision: screenshot, SoM detection, and target mapping."""
        self._send_status("Capturing screen...", "info")
        
        # Wait for any UI transitions to complete
        time.sleep(0.5)
        
        # Ensure window is focused before screenshot (unless suppressed for modal dialogs)
        if self.window_manager and not self._suppress_window_manager:
            self.window_manager.ensure_foreground_before_input()
        
        screenshot = self.vision_service.capture_screenshot()
        
        self._send_status("Analyzing UI elements...", "info")
        annotated_image, self._box_map = self.vision_service.run_som_detection(screenshot)
        
        self._send_status("Identifying targets...", "info")
        self._id_map = self.vision_service.map_targets_to_ids(annotated_image, targets, mode=self._mode)
        
        self._screenshot_taken = True
        found_count = len([v for v in self._id_map.values() if v is not None])
        self._send_status(f"Found {len(self._box_map)} UI elements, mapped {found_count}/{len(targets)} targets", "info")

    def _is_app_launch_step(self, step: dict, sequence: list, current_index: int) -> bool:
        """
        Determine if this step is likely to launch an application.
        """
        value = step.get('value', '').lower()
        desc = step.get('desc', '').lower()
        # ------------------------------------------------------------------
        # FIX: Prevent dialog-triggering shortcuts from being treated
        #      as application launches (Ctrl+S, Ctrl+O, Ctrl+P, F12, etc.)
        # ------------------------------------------------------------------
        non_launch_shortcuts = {
            'ctrl+s', 'ctrl+o', 'ctrl+p', 'ctrl+n', 'ctrl+w', 'ctrl+z', 'ctrl+y',
            'ctrl+a', 'ctrl+c', 'ctrl+v', 'ctrl+x', 'ctrl+f', 'ctrl+h',
            'f12', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11',
            'alt+f4', 'alt+tab', 'escape', 'esc'
        }
        if value in non_launch_shortcuts:
            return False
            
        # Check if description mentions launching
        for keyword in self.APP_LAUNCH_KEYWORDS:
            if keyword in desc:
                return True
        
        # Check if this is Enter after typing in Start menu
        if value == 'enter' and current_index > 0:
            prev_step = sequence[current_index - 1]
            prev_value = prev_step.get('value', '').lower()
            
            # If previous step was typing (not a special key) after Win key
            if prev_step.get('type') == 'keyboard':
                if not self._is_special_key(prev_value) and len(prev_value) > 1:
                    # Skip if it's a command-line command (won't create visible window)
                    if any(cmd in prev_value for cmd in ['cmd /c', 'cmd.exe /c', 'mkdir', 'rmdir', 'del ', 'copy ', 'move ', 'ren ']):
                        return False
                    # Skip if it looks like a file path
                    if '\\' in prev_value or '/' in prev_value:
                        return False
                    
                    # Check if there was a Win key press before, but only within the last 3 steps
                    # This prevents false positives when Enter is used in other contexts (like search within apps)
                    for j in range(current_index - 1, max(-1, current_index - 4), -1):
                        check_val = sequence[j].get('value', '').lower()
                        if check_val == 'win' or check_val == 'windows':
                            return True
                        # Stop if we hit another Enter or app launch (different context)
                        if check_val == 'enter':
                            break
                        # Stop if we hit a hotkey that changes context (like Ctrl+F for search)
                        if '+' in check_val and any(mod in check_val for mod in ['ctrl', 'alt']):
                            break
        
        # Check patterns
        for pattern in self.APP_LAUNCH_PATTERNS:
            if re.match(pattern, value, re.IGNORECASE):
                # Win key alone or Win+R
                if value in ['win', 'win+r']:
                    return False  # These open menus, not apps directly
                return True
        
        return False
    
    def _get_app_name_from_context(self, sequence: list, current_index: int) -> Optional[str]:
        """
        Try to determine what app is being launched based on recent typed text.
        Only returns app names that are likely to create visible windows.
        """
        # Look backwards for typed text
        for i in range(current_index - 1, max(-1, current_index - 5), -1):
            step = sequence[i]
            if step.get('type') == 'keyboard':
                value = step.get('value', '')
                # Skip special keys and shortcuts
                if not self._is_special_key(value.lower()) and '+' not in value and len(value) > 1:
                    # Skip command-line commands that don't create visible windows
                    # These are typically run via Win+R and execute silently
                    value_lower = value.lower()
                    if any(cmd in value_lower for cmd in ['cmd /c', 'cmd.exe /c', 'mkdir', 'rmdir', 'del ', 'copy ', 'move ', 'ren ']):
                        continue
                    # Skip if it looks like a file path
                    if '\\' in value or '/' in value:
                        continue
                    # Skip terminal commands (python, node, npm, git, etc.)
                    if any(value_lower.startswith(cmd) for cmd in ['python ', 'node ', 'npm ', 'git ', 'pip ', 'java ', 'javac ', 'gcc ', 'g++ ', 'make ', 'cargo ', 'go ', 'ruby ', 'perl ', 'php ']):
                        continue
                    # Skip if it contains file extensions (likely a command with file argument)
                    if any(ext in value_lower for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.rb', '.go', '.rs', '.sh', '.bat', '.cmd']):
                        continue
                    return value
        
        # Check last typed text with same filters
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
                # Text to type
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

        Behaves correctly with your actual DirectPathExecutor, which:
        - ALWAYS performs its own Ctrl+S internally,
        - waits for the save dialog internally,
        - types the path internally,
        - handles overwrite dialogs internally (based on PathConfig),
        - detects error dialogs via OCR internally.

        This wrapper:
        - Validates inputs safely
        - Sanitises filenames
        - Avoids leaking full paths in logs
        - Enforces overwrite_policy override if provided
        - Ensures window focus before DirectPathExecutor runs
        """

        # ------------------------------------------------------------------
        # Preconditions
        # ------------------------------------------------------------------
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

        # ------------------------------------------------------------------
        # Sanitize + normalise path (without leaking)
        # ------------------------------------------------------------------
        import os
        normalized_path = os.path.normpath(raw_path)

        # Log only filename, never full path
        filename_only = os.path.basename(normalized_path) or "file"

        self._send_status(f"save_file: preparing to save '{filename_only}'", "info")

        # Basic safety check for illegal characters
        if any(c in normalized_path for c in ['*', '?', '"', '<', '>', '|']):
            from direct_path_executor import create_error_result
            return create_error_result(
                operation="save",
                path=normalized_path,
                error_type="invalid_path",
                error_message="Path contains invalid filename characters"
            )

        # ------------------------------------------------------------------
        # Ensure target window is focused (only BEFORE Ctrl+S, not during dialog)
        # ------------------------------------------------------------------
        if self.window_manager and not self._suppress_window_manager:
            self.window_manager.ensure_foreground_before_input()
            time.sleep(0.15)

        # ------------------------------------------------------------------
        # Temporarily override overwrite policy (if provided)
        # ------------------------------------------------------------------
        original_policy = None
        if overwrite_policy is not None and self._direct_path_executor.config:
            original_policy = self._direct_path_executor.config.overwrite_policy
            self._direct_path_executor.config.overwrite_policy = overwrite_policy

        # ------------------------------------------------------------------
        # CRITICAL: Suppress window manager during Save dialog interaction
        # This prevents WindowManager from stealing focus from the modal dialog
        # ------------------------------------------------------------------
        self._suppress_window_manager = True
        
        # Save and clear the last activated window handle to prevent auto-reactivation
        saved_hwnd = None
        if self.window_manager:
            saved_hwnd = self.window_manager._last_activated_hwnd
            self.window_manager._last_activated_hwnd = None
        
        try:
            # ------------------------------------------------------------------
            # Execute save operation (DirectPathExecutor handles everything else)
            # ------------------------------------------------------------------
            self._send_status(f"save_file: executing save for '{filename_only}'", "info")
            result = self._direct_path_executor.execute_save(normalized_path)

        finally:
            # Restore window manager, hwnd tracking, and policy after operation
            self._suppress_window_manager = False
            if self.window_manager and saved_hwnd:
                self.window_manager._last_activated_hwnd = saved_hwnd
            if original_policy is not None and self._direct_path_executor.config:
                self._direct_path_executor.config.overwrite_policy = original_policy

        # ------------------------------------------------------------------
        # Report result without leaking sensitive details
        # ------------------------------------------------------------------
        if result.success:
            self._send_status(f"save_file: saved '{filename_only}' successfully", "success")
        else:
            # Log only safe details (error_message may contain OCR text but not path)
            self._send_status(
                f"save_file failed for '{filename_only}': {result.error_message}",
                "warning"
            )

        return result
    
    def _execute_open_file_step(self, step: dict) -> 'PathResolveResult':
        """
        Execute an open_file step - resolve path and open file directly.
        
        Uses filesystem-based path resolution (no UI/OCR) and opens the file
        with its default application using os.startfile().
        
        Args:
            step: Step dict with 'path' (fuzzy path query)
        
        Returns:
            PathResolveResult with success status
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
        
        # Resolve the path
        self._send_status(f"Resolving file path: '{path_query}'", "info")
        result = self._path_resolver.resolve(path_query)
        
        if not result.success:
            self._send_status(f"✗ Could not resolve path: {result.error_message}", "warning")
            return result
        
        # Show resolution steps
        for step_msg in result.resolution_steps:
            self._send_status(step_msg, "info")
        
        resolved_path = result.resolved_path
        self._send_status(f"✓ Resolved to: {resolved_path}", "success")
        
        # Check if file exists
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
        
        # Open the file with default application
        try:
            self._send_status(f"Opening file: {resolved_path}", "info")
            os.startfile(resolved_path)
            time.sleep(1.0)  # Wait for application to start
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
        
        Uses filesystem-based path resolution (no UI/OCR) and opens the folder
        using 'explorer' command.
        
        Includes retry logic with filesystem readiness detection for newly created folders.
        
        Args:
            step: Step dict with 'path' (fuzzy path query)
        
        Returns:
            PathResolveResult with success status
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
        
        # Resolve the path with retry logic for newly created folders
        self._send_status(f"Resolving folder path: '{path_query}'", "info")
        
        max_retries = 3
        retry_delay = 0.5
        result = None
        
        for attempt in range(max_retries):
            result = self._path_resolver.resolve(path_query)
            
            if result.success:
                break
            
            # If path resolution failed and we have readiness detector, wait for folder to exist
            if attempt < max_retries - 1:
                if READINESS_DETECTOR_AVAILABLE and self._filesystem_detector:
                    # Try to construct expected path for readiness check
                    # This helps when folder was just created
                    self._send_status(f"Path not found, waiting for folder creation (attempt {attempt + 1}/{max_retries})...", "info")
                    time.sleep(retry_delay)
                else:
                    time.sleep(retry_delay)
        
        if not result.success:
            self._send_status(f"✗ Could not resolve path after {max_retries} attempts: {result.error_message}", "warning")
            return result
        
        # Show resolution steps
        for step_msg in result.resolution_steps:
            self._send_status(step_msg, "info")
        
        resolved_path = result.resolved_path
        self._send_status(f"✓ Resolved to: {resolved_path}", "success")
        
        # Verify folder exists and is accessible with readiness detection
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
            # Fallback: simple existence check
            if not os.path.exists(resolved_path):
                result.success = False
                result.error_message = f"Folder does not exist: {resolved_path}"
                self._send_status(f"✗ {result.error_message}", "warning")
                return result
            
            if not os.path.isdir(resolved_path):
                result.success = False
                result.error_message = f"Path is not a folder: {resolved_path}"
                self._send_status(f"✗ {result.error_message}", "warning")
                return result
        
        # Open the folder in Explorer
        try:
            self._send_status(f"Opening folder in Explorer: {resolved_path}", "info")
            subprocess.Popen(['explorer', resolved_path])
            time.sleep(0.5)  # Wait for Explorer to open
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
        
        This bypasses UI/OCR completely by reading directory contents directly
        and using fuzzy matching to find the best filename match.
        
        Args:
            step: Step dict with 'directory' and 'query'
        
        Returns:
            ResolveResult with resolved filename
        
        Requirements: Zero OCR, Zero UI dependency
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
        
        if not directory:
            self._send_status("resolve_filename: missing 'directory' parameter", "warning")
            from filename_resolver import ResolveResult
            return ResolveResult(
                success=False,
                error_message="Directory parameter is required"
            )
        
        if not query:
            self._send_status("resolve_filename: missing 'query' parameter", "warning")
            from filename_resolver import ResolveResult
            return ResolveResult(
                success=False,
                error_message="Query parameter is required"
            )
        
        # Execute the resolution
        self._send_status(f"Resolving filename: '{query}' in {directory}", "info")
        result = self._filename_resolver.resolve(directory, query)
        
        if result.success:
            self._send_status(
                f"✓ Resolved '{query}' → '{result.resolved_name}' (confidence: {result.confidence:.1f}%)",
                "success"
            )
            # Show top candidates
            if result.candidates:
                candidates_str = ", ".join([f"'{name}' ({score:.2f})" for name, score in result.candidates[:3]])
                self._send_status(f"  Top matches: {candidates_str}", "info")
        else:
            self._send_status(f"✗ Could not resolve '{query}': {result.error_message}", "warning")
            if result.candidates:
                candidates_str = ", ".join([f"'{name}' ({score:.2f})" for name, score in result.candidates[:3]])
                self._send_status(f"  Available: {candidates_str}", "info")
        
        return result
    
    def _execute_navigate_explorer_step(self, step: dict) -> 'ExecutionResult':
        """
        Execute a navigate_explorer step using address bar navigation.
        
        Args:
            step: Step dict with 'directory'
        
        Returns:
            ExecutionResult with success status and any error details
        
        Requirements: 3.1, 3.2
        """
        if not DIRECT_PATH_EXECUTOR_AVAILABLE or self._direct_path_executor is None:
            self._send_status("DirectPathExecutor not available for navigate_explorer step", "error")
            from direct_path_executor import create_error_result
            return create_error_result(
                operation="navigate",
                path=step.get('directory', ''),
                error_type="executor_unavailable",
                error_message="DirectPathExecutor is not available"
            )
        
        directory = step.get('directory', '')
        if not directory:
            self._send_status("navigate_explorer: missing 'directory' parameter", "warning")
            from direct_path_executor import create_error_result
            return create_error_result(
                operation="navigate",
                path='',
                error_type="invalid_path",
                error_message="Directory parameter is required"
            )
        
        # Execute the navigation
        self._send_status(f"Executing navigate_explorer: {directory}", "info")
        result = self._direct_path_executor.navigate_explorer(directory)
        
        if result.success:
            self._send_status(f"navigate_explorer completed: {directory}", "success")
        else:
            self._send_status(f"navigate_explorer failed: {result.error_message}", "warning")
        
        return result
    
    def _execute_ai_edit_text_step(self, step: dict) -> bool:
        """Execute AI-powered text editing."""
        if not AI_EDITOR_ENGINE_AVAILABLE or self._ai_editor_engine is None:
            self._send_status("AIEditorEngine not available", "error")
            return False
        
        path_query = step.get('path', '')
        prompt = step.get('prompt', '')
        
        # Resolve path using path_resolver
        resolve_result = self._path_resolver.resolve(path_query)
        if not resolve_result.success:
            self._send_status(f"Could not resolve path: {path_query}", "error")
            return False
        
        file_path = resolve_result.resolved_path
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self._send_status(f"AI is proposing changes to {os.path.basename(file_path)}...", "info")
            edits = self._ai_editor_engine.get_text_edits(content, prompt)
            new_content = self._ai_editor_engine.apply_text_edits(content, edits.edits)
            
            diff = self._ai_editor_engine.generate_text_diff(content, new_content, os.path.basename(file_path))
            
            if self._permission_service:
                self._send_status("Waiting for mobile confirmation...", "info")
                if not self._permission_service.request_permission(
                    "AI Text Edit", 
                    f"File: {file_path}\n\nProposed Changes:\n{diff}"
                ):
                    self._send_status("✗ AI edit denied by user", "warning")
                    return False
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            self._send_status(f"✓ AI edits applied to {os.path.basename(file_path)}", "success")
            return True
        except Exception as e:
            self._send_status(f"AI text edit error: {e}", "error")
            return False

    def _execute_ai_edit_excel_step(self, step: dict) -> bool:
        """Execute AI-powered Excel editing."""
        if not AI_EDITOR_ENGINE_AVAILABLE or self._ai_editor_engine is None:
            self._send_status("AIEditorEngine not available", "error")
            return False
        
        path_query = step.get('path', '')
        prompt = step.get('prompt', '')
        
        resolve_result = self._path_resolver.resolve(path_query)
        if not resolve_result.success:
            self._send_status(f"Could not resolve path: {path_query}", "error")
            return False
        
        file_path = resolve_result.resolved_path
        
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path)
            context = self._ai_editor_engine.extract_excel_context(wb)
            
            self._send_status(f"AI is proposing changes to spreadsheet {os.path.basename(file_path)}...", "info")
            edits = self._ai_editor_engine.get_excel_edits(context, prompt)
            
            # Create a preview of changes
            dummy_wb = openpyxl.load_workbook(file_path)
            diff_records = self._ai_editor_engine.apply_excel_edits(dummy_wb, edits.commands)
            diff_summary = self._ai_editor_engine.generate_excel_diff_summary(diff_records)
            
            if self._permission_service:
                self._send_status("Waiting for mobile confirmation...", "info")
                if not self._permission_service.request_permission(
                    "AI Excel Edit", 
                    f"File: {file_path}\n\nProposed Changes:\n{diff_summary}"
                ):
                    self._send_status("✗ AI edit denied by user", "warning")
                    return False
            
            # Apply to real workbook
            self._ai_editor_engine.apply_excel_edits(wb, edits.commands)
            wb.save(file_path)
                
            self._send_status(f"✓ AI edits applied to {os.path.basename(file_path)}", "success")
            return True
        except Exception as e:
            self._send_status(f"AI excel edit error: {e}", "error")
            return False

    def _execute_ai_edit_word_step(self, step: dict) -> bool:
        """Execute AI-powered Word document editing."""
        if not AI_EDITOR_ENGINE_AVAILABLE or self._ai_editor_engine is None:
            self._send_status("AIEditorEngine not available", "error")
            return False
        
        path_query = step.get('path', '')
        prompt = step.get('prompt', '')
        
        resolve_result = self._path_resolver.resolve(path_query)
        if not resolve_result.success:
            self._send_status(f"Could not resolve path: {path_query}", "error")
            return False
        
        file_path = resolve_result.resolved_path
        
        try:
            import docx
            doc = docx.Document(file_path)
            context = self._ai_editor_engine.extract_word_context(doc)
            
            self._send_status(f"AI is proposing changes to document {os.path.basename(file_path)}...", "info")
            edits = self._ai_editor_engine.get_word_edits(context, prompt)
            
            # Request permission
            if self._permission_service:
                diff_text = "\n".join([f"Replace '{e.search_text}' with '{e.replace_text}'" for e in edits.edits])
                self._send_status("Waiting for mobile confirmation...", "info")
                if not self._permission_service.request_permission(
                    "AI Word Edit", 
                    f"File: {file_path}\n\nProposed Changes:\n{diff_text}"
                ):
                    self._send_status("✗ AI edit denied by user", "warning")
                    return False
            
            self._ai_editor_engine.apply_word_edits(doc, edits.edits)
            doc.save(file_path)
                
            self._send_status(f"✓ AI edits applied to {os.path.basename(file_path)}", "success")
            return True
        except Exception as e:
            self._send_status(f"AI word edit error: {e}", "error")
            return False
    
    def _execute_click_text_step(self, step: dict) -> 'ClickResult':
        """
        Execute a click_text step using OCR-based text detection.
        
        Args:
            step: Step dict with 'text', optional 'double_click', and optional 'region'
        
        Returns:
            ClickResult with success status and click location
        
        Requirements: 3.3, 4.1
        """
        if not TEXT_CLICKER_AVAILABLE or self._text_clicker is None:
            self._send_status("TextBasedClicker not available for click_text step", "error")
            from text_clicker import create_failure_result
            return create_failure_result(
                target_text=step.get('text', ''),
                error_message="TextBasedClicker is not available"
            )
        
        text = step.get('text', '')
        if not text:
            self._send_status("click_text: missing 'text' parameter", "warning")
            from text_clicker import create_failure_result
            return create_failure_result(
                target_text='',
                error_message="Text parameter is required"
            )
        
        double_click = step.get('double_click', False)
        region = step.get('region')
        
        # Convert region from list to tuple if needed
        if region and isinstance(region, list):
            region = tuple(region)
        
        # Execute the click
        self._send_status(f"Executing click_text: '{text}' (double_click={double_click})", "info")
        
        if double_click:
            result = self._text_clicker.double_click_text(text, region=region)
        else:
            result = self._text_clicker.click_text(text, region=region)
        
        if result.success:
            self._send_status(f"click_text completed: '{text}' at {result.clicked_location}", "success")
        else:
            self._send_status(f"click_text failed: {result.error_message}", "warning")
            
            # Log detected text for debugging
            if result.all_matches:
                detected_texts = [m.text for m in result.all_matches[:10]]
                self._send_status(f"Detected text on screen: {detected_texts}", "info")
        
        return result
    
    def _execute_click_text_fast_step(self, step: dict) -> dict:
        """
        Execute a click_text_fast step using fast window-specific OCR.
        
        This is much faster than visual_click because:
        1. Only scans the target window (not entire screen)
        2. Uses lightweight pytesseract directly
        3. No FastSAM model loading or inference
        4. No multimodal LLM calls
        
        Args:
            step: Step dict with 'window_title' and 'text'
        
        Returns:
            dict with success, clicked_location, error_message
        """
        window_title = step.get('window_title', '')
        text = step.get('text', '')
        
        if not window_title:
            self._send_status("click_text_fast: missing 'window_title' parameter", "error")
            return {
                'success': False,
                'clicked_location': None,
                'error_message': "window_title parameter is required"
            }
        
        if not text:
            self._send_status("click_text_fast: missing 'text' parameter", "error")
            return {
                'success': False,
                'clicked_location': None,
                'error_message': "text parameter is required"
            }
        
        # Import the fast text clicker
        try:
            import sys
            from pathlib import Path
            backend_path = Path(__file__).parent.parent / "backend"
            if str(backend_path) not in sys.path:
                sys.path.insert(0, str(backend_path))
            from text_click_fast import FastTextClicker
        except ImportError as e:
            self._send_status(f"FastTextClicker not available: {e}", "error")
            return {
                'success': False,
                'clicked_location': None,
                'error_message': f"FastTextClicker module not available: {e}"
            }
        
        # Execute the fast click
        self._send_status(f"Executing click_text_fast: '{text}' in window '{window_title}'", "info")
        
        clicker = FastTextClicker()
        result = clicker.click_text_in_window(window_title, text)
        
        if result['success']:
            match_type = result.get('match_type', 'exact')
            self._send_status(
                f"click_text_fast completed ({match_type} match): '{result.get('matched_text', text)}' at {result['clicked_location']}", 
                "success"
            )
        else:
            error_msg = result['error_message']
            self._send_status(f"click_text_fast failed: {error_msg}", "warning")
            
            # Show detected texts for debugging
            if result.get('detected_texts'):
                detected = result['detected_texts'][:10]
                self._send_status(f"Detected texts in window: {detected}", "info")
        
        return result


    # =========================================================================
    # Critical Operation Step Handlers (require permission)
    # =========================================================================
    
    def _execute_delete_file_step(self, step: dict) -> bool:
        """
        Execute a delete_file step - deletes a file from the filesystem.
        This is a critical operation that requires user permission.
        
        Args:
            step: Step dict with 'path'
        
        Returns:
            bool: True if file was deleted successfully
        """
        import os
        
        file_path = step.get('path', '')
        
        if not file_path:
            self._send_status("delete_file: missing 'path' parameter", "warning")
            return False
        
        # Normalize path
        file_path = os.path.normpath(file_path)
        
        # Check if file exists
        if not os.path.exists(file_path):
            self._send_status(f"delete_file: file does not exist: {file_path}", "warning")
            return False
        
        if not os.path.isfile(file_path):
            self._send_status(f"delete_file: path is not a file: {file_path}", "warning")
            return False
        
        try:
            self._send_status(f"Deleting file: {os.path.basename(file_path)}", "info")
            os.remove(file_path)
            self._send_status(f"✓ File deleted successfully", "success")
            return True
        except PermissionError:
            self._send_status(f"delete_file: permission denied for {file_path}", "error")
            return False
        except Exception as e:
            self._send_status(f"delete_file: error - {str(e)}", "error")
            return False
    
    def _execute_delete_folder_step(self, step: dict) -> bool:
        """
        Execute a delete_folder step - deletes a folder and its contents.
        This is a critical operation that requires user permission.
        
        Args:
            step: Step dict with 'path'
        
        Returns:
            bool: True if folder was deleted successfully
        """
        import os
        import shutil
        
        folder_path = step.get('path', '')
        
        if not folder_path:
            self._send_status("delete_folder: missing 'path' parameter", "warning")
            return False
        
        # Normalize path
        folder_path = os.path.normpath(folder_path)
        
        # Check if folder exists
        if not os.path.exists(folder_path):
            self._send_status(f"delete_folder: folder does not exist: {folder_path}", "warning")
            return False
        
        if not os.path.isdir(folder_path):
            self._send_status(f"delete_folder: path is not a folder: {folder_path}", "warning")
            return False
        
        try:
            self._send_status(f"Deleting folder: {os.path.basename(folder_path)}", "info")
            shutil.rmtree(folder_path)
            self._send_status(f"✓ Folder deleted successfully", "success")
            return True
        except PermissionError:
            self._send_status(f"delete_folder: permission denied for {folder_path}", "error")
            return False
        except Exception as e:
            self._send_status(f"delete_folder: error - {str(e)}", "error")
            return False
    
    def _execute_shell_command_step(self, step: dict) -> bool:
        """
        Execute a shell_command step - runs a Windows shell command.
        
        This is the core of the "Hybrid CLI" approach for file operations.
        Supports the "Killer Combo" workflow:
        1. Create file/folder with shell command
        2. Open with 'start' command
        3. Edit via keyboard
        4. Save with Ctrl+S (silent because file exists)
        
        CRITICAL: If command contains "start ", waits 3-5 seconds for the
        application window to open before continuing.
        
        Args:
            step: Step dict with 'command' (string)
        
        Returns:
            bool: True if command executed successfully
        """
        import subprocess
        import time
        
        command = step.get('command', '')
        
        if not command:
            self._send_status("shell_command: missing 'command' parameter", "warning")
            return False
        
        try:
            # Log the command (sanitized for security)
            command_preview = command[:100] + '...' if len(command) > 100 else command
            self._send_status(f"Executing shell command: {command_preview}", "info")
            
            # CRITICAL FIX: Expand environment variables before execution
            # This ensures %USERPROFILE% and other vars work correctly with explorer
            expanded_command = os.path.expandvars(command)
            
            # Execute the command using subprocess with shell=True
            # Use cmd.exe explicitly for better Windows compatibility
            result = subprocess.run(
                expanded_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout to prevent hanging
            )
            
            # Check if command contains "start " - indicates app launch
            if "start " in command.lower():
                # Wait for application window to open
                wait_time = 4.0  # 4 seconds default wait
                self._send_status(f"Waiting {wait_time}s for application to open...", "info")
                time.sleep(wait_time)
                
                # Try to activate the window if window manager is available
                if self.window_manager and not self._suppress_window_manager:
                    # Extract app name from "start filename" pattern
                    import re
                    match = re.search(r'start\s+([^\s&|]+)', command, re.IGNORECASE)
                    if match:
                        app_name = match.group(1).strip('"\'')
                        # Track for readiness detection
                        self._last_launched_app = app_name
                        self._send_status(f"Attempting to activate {app_name} window...", "info")
                        # Give window manager a chance to find and activate
                        time.sleep(0.5)
            
            # Check if command launches VS Code
            elif command.lower().startswith('code ') or ' code ' in command.lower():
                # Check if VS Code is already running (faster load time)
                vscode_already_running = False
                if self.window_manager:
                    # Check for existing VS Code window
                    fg_title = self.window_manager.get_foreground_window_title()
                    if fg_title and "visual studio code" in fg_title.lower():
                        vscode_already_running = True
                
                if vscode_already_running:
                    # VS Code already open - just switching/opening folder
                    wait_time = 3.0
                    self._send_status(f"VS Code already running, waiting {wait_time}s...", "info")
                    time.sleep(wait_time)
                else:
                    # First launch - needs more time
                    wait_time = 8.0  # 8 seconds for cold start
                    self._send_status(f"Launching VS Code, waiting {wait_time}s...", "info")
                    time.sleep(wait_time)
                
                # Try to find and activate VS Code window
                if self.window_manager and not self._suppress_window_manager:
                    self._send_status("Looking for VS Code window...", "info")
                    # VS Code window title usually contains "Visual Studio Code"
                    success = self.window_manager.wait_and_activate(
                        "Visual Studio Code",
                        timeout=10.0
                    )
                    if success:
                        self._send_status("✓ VS Code window activated and ready", "success")
                        time.sleep(1.5)  # Extra time for UI to settle and extensions to load
                    else:
                        self._send_status("⚠ Could not detect VS Code window, continuing...", "warning")
                        time.sleep(2.0)  # Extra fallback wait
            
            # Check return code
            if result.returncode == 0:
                self._send_status(f"✓ Command executed successfully", "success")
                if result.stdout:
                    # Log stdout if present (truncated)
                    stdout_preview = result.stdout[:200].strip()
                    if stdout_preview:
                        self._send_status(f"Output: {stdout_preview}", "info")
                return True
            else:
                # Special case: explorer.exe often returns exit code 1 even on success
                # because it delegates to an existing explorer process
                if "explorer" in expanded_command.lower():
                    self._send_status(f"✓ Explorer command executed (exit code {result.returncode} is normal)", "success")
                    return True
                
                # Command failed
                error_msg = result.stderr.strip() if result.stderr else f"Exit code: {result.returncode}"
                self._send_status(f"shell_command failed: {error_msg}", "warning")
                return False
                
        except subprocess.TimeoutExpired:
            self._send_status(f"shell_command: command timed out after 30 seconds", "error")
            return False
        except Exception as e:
            self._send_status(f"shell_command: error - {str(e)}", "error")
            return False
    
    def _wait_for_readiness_before_vision(self, sequence: list, current_step_index: int):
        """
        Wait for application/page readiness before taking screenshot for vision.
        This ensures UI is fully loaded before attempting element detection.
        
        Implements deterministic readiness detection based on:
        - Browser: Page load completion (title stabilization)
        - Desktop App: Window state + UI Automation tree population
        - General: Intelligent delay based on recent actions
        
        Args:
            sequence: Full step sequence
            current_step_index: Index of current visual_click step
        """
        if not READINESS_DETECTOR_AVAILABLE:
            # Fallback: use simple delay
            self._send_status("Readiness detector not available, using fallback delay", "info")
            time.sleep(2.0)
            return
        
        # Determine what type of readiness check to perform
        # based on recently launched app and recent actions
        
        # Check if we recently launched a browser
        if self._last_launched_app and self._last_launch_step_index >= 0:
            steps_since_launch = current_step_index - self._last_launch_step_index
            
            # Only apply readiness if launch was recent (within last 10 steps)
            if steps_since_launch <= 10:
                app_lower = self._last_launched_app.lower()
                
                # Browser readiness detection
                if any(browser in app_lower for browser in ['chrome', 'firefox', 'edge', 'browser']):
                    self._send_status(f"Waiting for {self._last_launched_app} page to load...", "info")
                    result = self._browser_detector.wait_for_page_load(
                        browser_name=app_lower,
                        timeout=15.0,
                        min_stable_time=1.0
                    )
                    
                    if result.is_ready:
                        self._send_status(f"✓ Page ready ({result.elapsed_time:.1f}s)", "success")
                        return
                    else:
                        self._send_status(f"⚠ Page readiness check: {result.message}", "warning")
                        # Continue anyway with fallback delay
                        time.sleep(1.0)
                        return
                
                # Desktop application readiness detection
                elif app_lower not in ['notepad', 'calculator', 'cmd', 'powershell']:
                    # For complex desktop apps, use UI Automation readiness
                    self._send_status(f"Waiting for {self._last_launched_app} to be ready...", "info")
                    
                    # Try to get window title from window manager
                    window_title = self._last_launched_app
                    if self.window_manager:
                        fg_title = self.window_manager.get_foreground_window_title()
                        if fg_title:
                            window_title = fg_title
                    
                    result = self._desktop_detector.wait_for_app_ready(
                        window_title_pattern=window_title,
                        timeout=15.0,
                        check_cpu_stable=False,  # Skip CPU check for speed
                        min_control_count=5
                    )
                    
                    if result.is_ready:
                        self._send_status(f"✓ Application ready ({result.elapsed_time:.1f}s)", "success")
                        return
                    else:
                        self._send_status(f"⚠ App readiness check: {result.message}", "warning")
                        # Continue anyway with fallback delay
                        time.sleep(1.0)
                        return
        
        # Check if we recently navigated (pressed Enter after typing URL/search)
        # Look back a few steps for Enter after typing
        for i in range(max(0, current_step_index - 5), current_step_index):
            step = sequence[i]
            if step.get('type') == 'keyboard':
                value = step.get('value', '').lower()
                desc = step.get('desc', '').lower()
                
                # Check if this was navigation (Enter after URL/search)
                if value == 'enter' and any(keyword in desc for keyword in ['navigate', 'search', 'go to', 'open']):
                    # Recent navigation detected - wait for page load
                    self._send_status("Recent navigation detected, waiting for page load...", "info")
                    
                    # Try browser readiness if we can detect browser
                    if self.window_manager:
                        fg_title = self.window_manager.get_foreground_window_title()
                        if fg_title and any(browser in fg_title.lower() for browser in ['chrome', 'firefox', 'edge']):
                            browser_name = next((b for b in ['chrome', 'firefox', 'edge'] if b in fg_title.lower()), 'chrome')
                            result = self._browser_detector.wait_for_page_load(
                                browser_name=browser_name,
                                timeout=15.0,
                                min_stable_time=1.0
                            )
                            
                            if result.is_ready:
                                self._send_status(f"✓ Page ready ({result.elapsed_time:.1f}s)", "success")
                                return
                    
                    # Fallback: simple delay
                    time.sleep(2.0)
                    return
        
        # No specific readiness check needed - use minimal delay
        self._send_status("No specific readiness check needed, proceeding...", "info")
        time.sleep(0.5)
    
    # ========================================================================
    # PLANE 2: CODE WORKSPACE CONTROL METHODS
    # ========================================================================
    
    def _execute_write_file_step(self, step: dict) -> bool:
        """
        Execute a write_file step - create or overwrite a file with content.
        
        This is the core of Plane 2 workspace control - reliable file creation/editing
        without UI interaction. Much faster and more reliable than UI-based file creation.
        
        Args:
            step: Step dict with 'path' (str) and 'content' (str)
        
        Returns:
            bool: True if file written successfully
        """
        if not FILE_OPERATIONS_AVAILABLE:
            self._send_status("write_file: file_operations module not available", "error")
            return False
        
        path = step.get('path', '')
        content = step.get('content', '')
        desc = step.get('desc', '')
        
        if not path:
            self._send_status("write_file: missing 'path' parameter", "warning")
            return False
        
        # Check if content is a placeholder that needs dynamic generation
        if content == "__JARVIS_NEEDS_CONTENT_UPDATE__":
            self._send_status("Detected content placeholder - generating modified content...", "info")
            
            # Check if we have previously read content
            if not hasattr(self, 'last_read_content') or not self.last_read_content:
                self._send_status("Error: No file content available for modification", "error")
                return False
            
            # Use LLM to generate modified content based on description
            try:
                from llm_provider import OpenAIProvider, GeminiProvider
                import os
                from dotenv import load_dotenv
                load_dotenv()
                
                # Determine which provider to use
                llm_provider = os.getenv('LLM_PROVIDER', 'openai').lower()
                
                if llm_provider == 'openai':
                    api_key = os.getenv('OPENAI_API_KEY')
                    if not api_key:
                        self._send_status("Error: OPENAI_API_KEY not configured", "error")
                        return False
                    provider = OpenAIProvider(api_key=api_key)
                else:
                    api_key = os.getenv('GEMINI_API_KEY')
                    if not api_key:
                        self._send_status("Error: GEMINI_API_KEY not configured", "error")
                        return False
                    provider = GeminiProvider(api_key=api_key)
                
                # Generate modified content
                system_prompt = "You are a file content modifier. Given the original file content and a modification instruction, output ONLY the modified file content. Do not add explanations, markdown formatting, or code fences. Output the exact file content that should be written."
                
                user_prompt = f"""Original file content:
```
{self.last_read_content}
```

Modification instruction: {desc}

Output the complete modified file content (no explanations, no markdown, just the raw content):"""
                
                self._send_status("Calling LLM to generate modified content...", "info")
                content = provider.generate_content(system_prompt=system_prompt, user_prompt=user_prompt)
                
                # Clean up any markdown code fences if present
                if content.startswith('```'):
                    lines = content.split('\n')
                    lines = lines[1:]  # Remove first line (```)
                    if lines and lines[-1].strip() == '```':
                        lines = lines[:-1]  # Remove last line (```)
                    content = '\n'.join(lines)
                
                self._send_status("✓ Modified content generated successfully", "success")
                
            except Exception as e:
                self._send_status(f"Error generating modified content: {e}", "error")
                return False
        
        # Content can be empty string (create empty file)
        
        try:
            success, message = write_file(path, content)
            
            if success:
                # Show truncated content preview
                content_preview = content[:100].replace('\n', '\\n')
                if len(content) > 100:
                    content_preview += '...'
                self._send_status(f"✓ {message}", "success")
                self._send_status(f"Content preview: {content_preview}", "info")
            else:
                self._send_status(f"write_file failed: {message}", "warning")
            
            return success
            
        except Exception as e:
            self._send_status(f"write_file: error - {str(e)}", "error")
            return False
    
    def _execute_read_file_step(self, step: dict) -> bool:
        """
        Execute a read_file step - read content from a file.
        
        Args:
            step: Step dict with 'path' (str)
        
        Returns:
            bool: True if file read successfully
        """
        if not FILE_OPERATIONS_AVAILABLE:
            self._send_status("read_file: file_operations module not available", "error")
            return False
        
        path = step.get('path', '')
        
        if not path:
            self._send_status("read_file: missing 'path' parameter", "warning")
            return False
        
        try:
            success, message, content = read_file(path)
            
            if success:
                # Store content for potential use in subsequent write_file steps
                self.last_read_content = content
                self.last_read_path = path
                
                # Show truncated content preview
                content_preview = content[:200].replace('\n', '\\n') if content else ''
                if content and len(content) > 200:
                    content_preview += '...'
                self._send_status(f"✓ {message}", "success")
                self._send_status(f"Content preview: {content_preview}", "info")
            else:
                self._send_status(f"read_file failed: {message}", "warning")
            
            return success
            
        except Exception as e:
            self._send_status(f"read_file: error - {str(e)}", "error")
            return False
    
    def _execute_append_file_step(self, step: dict) -> bool:
        """
        Execute an append_file step - append content to an existing file.
        
        Args:
            step: Step dict with 'path' (str) and 'content' (str)
        
        Returns:
            bool: True if content appended successfully
        """
        if not FILE_OPERATIONS_AVAILABLE:
            self._send_status("append_file: file_operations module not available", "error")
            return False
        
        path = step.get('path', '')
        content = step.get('content', '')
        
        if not path:
            self._send_status("append_file: missing 'path' parameter", "warning")
            return False
        
        if not content:
            self._send_status("append_file: missing 'content' parameter", "warning")
            return False
        
        try:
            success, message = append_file(path, content)
            
            if success:
                content_preview = content[:100].replace('\n', '\\n')
                if len(content) > 100:
                    content_preview += '...'
                self._send_status(f"✓ {message}", "success")
                self._send_status(f"Appended: {content_preview}", "info")
            else:
                self._send_status(f"append_file failed: {message}", "warning")
            
            return success
            
        except Exception as e:
            self._send_status(f"append_file: error - {str(e)}", "error")
            return False
    
    def _execute_create_directory_step(self, step: dict) -> bool:
        """
        Execute a create_directory step - create a directory.
        
        Args:
            step: Step dict with 'path' (str)
        
        Returns:
            bool: True if directory created successfully
        """
        if not FILE_OPERATIONS_AVAILABLE:
            self._send_status("create_directory: file_operations module not available", "error")
            return False
        
        path = step.get('path', '')
        
        if not path:
            self._send_status("create_directory: missing 'path' parameter", "warning")
            return False
        
        try:
            success, message = create_directory(path)
            
            if success:
                self._send_status(f"✓ {message}", "success")
            else:
                self._send_status(f"create_directory failed: {message}", "warning")
            
            return success
            
        except Exception as e:
            self._send_status(f"create_directory: error - {str(e)}", "error")
            return False
    
    # ========================================================================
    # Intelligent File Editing Operations (Modern IDE-like editing)
    # ========================================================================
    
    def _execute_replace_in_file_step(self, step: dict) -> bool:
        """
        Execute a replace_in_file step - search and replace text in a file.
        Similar to IDE "Find and Replace" functionality.
        
        Args:
            step: Step dict with 'path' (str), 'old_text' (str), 'new_text' (str), 
                  optional 'count' (int, -1 for all)
        
        Returns:
            bool: True if replacement successful
        """
        if not FILE_EDITOR_AVAILABLE:
            self._send_status("replace_in_file: file_editor module not available", "error")
            return False
        
        path = step.get('path', '')
        old_text = step.get('old_text', '')
        new_text = step.get('new_text', '')
        count = step.get('count', -1)
        
        if not path:
            self._send_status("replace_in_file: missing 'path' parameter", "warning")
            return False
        
        if not old_text:
            self._send_status("replace_in_file: missing 'old_text' parameter", "warning")
            return False
        
        try:
            success, message, diff = self._file_editor.replace_in_file(
                path, old_text, new_text, count=count
            )
            
            if success:
                self._send_status(f"✓ {message}", "success")
                if diff:
                    # Show diff preview (first 10 lines)
                    diff_lines = diff.split('\n')[:10]
                    diff_preview = '\n'.join(diff_lines)
                    self._send_status(f"Changes:\n{diff_preview}", "info")
            else:
                self._send_status(f"replace_in_file failed: {message}", "warning")
            
            return success
            
        except Exception as e:
            self._send_status(f"replace_in_file: error - {str(e)}", "error")
            return False
    
    def _execute_modify_lines_step(self, step: dict) -> bool:
        """
        Execute a modify_lines step - modify specific lines in a file.
        
        Args:
            step: Step dict with 'path' (str), 'line_number' (int), 
                  'new_content' (str), optional 'num_lines' (int, default 1)
        
        Returns:
            bool: True if modification successful
        """
        if not FILE_EDITOR_AVAILABLE:
            self._send_status("modify_lines: file_editor module not available", "error")
            return False
        
        path = step.get('path', '')
        line_number = step.get('line_number')
        new_content = step.get('new_content', '')
        num_lines = step.get('num_lines', 1)
        
        if not path:
            self._send_status("modify_lines: missing 'path' parameter", "warning")
            return False
        
        if line_number is None:
            self._send_status("modify_lines: missing 'line_number' parameter", "warning")
            return False
        
        try:
            success, message, diff = self._file_editor.modify_lines(
                path, line_number, new_content, num_lines=num_lines
            )
            
            if success:
                self._send_status(f"✓ {message}", "success")
                if diff:
                    # Show diff preview
                    diff_lines = diff.split('\n')[:10]
                    diff_preview = '\n'.join(diff_lines)
                    self._send_status(f"Changes:\n{diff_preview}", "info")
            else:
                self._send_status(f"modify_lines failed: {message}", "warning")
            
            return success
            
        except Exception as e:
            self._send_status(f"modify_lines: error - {str(e)}", "error")
            return False
    
    def _execute_insert_at_line_step(self, step: dict) -> bool:
        """
        Execute an insert_at_line step - insert content at a specific line.
        
        Args:
            step: Step dict with 'path' (str), 'line_number' (int), 'content' (str)
        
        Returns:
            bool: True if insertion successful
        """
        if not FILE_EDITOR_AVAILABLE:
            self._send_status("insert_at_line: file_editor module not available", "error")
            return False
        
        path = step.get('path', '')
        line_number = step.get('line_number')
        content = step.get('content', '')
        
        if not path:
            self._send_status("insert_at_line: missing 'path' parameter", "warning")
            return False
        
        if line_number is None:
            self._send_status("insert_at_line: missing 'line_number' parameter", "warning")
            return False
        
        try:
            success, message, diff = self._file_editor.insert_at_line(
                path, line_number, content
            )
            
            if success:
                self._send_status(f"✓ {message}", "success")
                if diff:
                    diff_lines = diff.split('\n')[:10]
                    diff_preview = '\n'.join(diff_lines)
                    self._send_status(f"Changes:\n{diff_preview}", "info")
            else:
                self._send_status(f"insert_at_line failed: {message}", "warning")
            
            return success
            
        except Exception as e:
            self._send_status(f"insert_at_line: error - {str(e)}", "error")
            return False
    
    def _execute_delete_lines_step(self, step: dict) -> bool:
        """
        Execute a delete_lines step - delete specific lines from a file.
        
        Args:
            step: Step dict with 'path' (str), 'start_line' (int), 
                  optional 'end_line' (int)
        
        Returns:
            bool: True if deletion successful
        """
        if not FILE_EDITOR_AVAILABLE:
            self._send_status("delete_lines: file_editor module not available", "error")
            return False
        
        path = step.get('path', '')
        start_line = step.get('start_line')
        end_line = step.get('end_line')
        
        if not path:
            self._send_status("delete_lines: missing 'path' parameter", "warning")
            return False
        
        if start_line is None:
            self._send_status("delete_lines: missing 'start_line' parameter", "warning")
            return False
        
        try:
            success, message, diff = self._file_editor.delete_lines(
                path, start_line, end_line
            )
            
            if success:
                self._send_status(f"✓ {message}", "success")
                if diff:
                    diff_lines = diff.split('\n')[:10]
                    diff_preview = '\n'.join(diff_lines)
                    self._send_status(f"Changes:\n{diff_preview}", "info")
            else:
                self._send_status(f"delete_lines failed: {message}", "warning")
            
            return success
            
        except Exception as e:
            self._send_status(f"delete_lines: error - {str(e)}", "error")
            return False

    def _execute_send_email_step(self, step: dict) -> bool:
        """
        Execute a send_email step using the background email service.
        
        Args:
            step: Step dict with 'recipient_email', 'subject', 'body', 
                  and optional 'attachment_filepaths' (list of strings)
        
        Returns:
            bool: True if email was sent successfully
        """
        if not EMAIL_SERVICE_AVAILABLE:
            self._send_status("Email service not available", "error")
            return False
            
        recipient = step.get('recipient_email')
        subject = step.get('subject')
        body = step.get('body')
        attachments = step.get('attachment_filepaths', [])
        
        if not all([recipient, subject, body]):
            self._send_status("send_email: missing required parameters (recipient, subject, or body)", "warning")
            return False
            
        self._send_status(f"Sending email to {recipient}...", "info")
        
        try:
            success, message = send_email_tool(
                recipient_email=recipient,
                subject=subject,
                body=body,
                attachment_filepaths=attachments
            )
            
            if success:
                self._send_status(f"✓ {message}", "success")
                return True
            else:
                self._send_status(f"✗ Failed to send email: {message}", "error")
                return False
        except Exception as e:
            self._send_status(f"✗ Email service error: {str(e)}", "error")
            return False

    def _execute_web_automation_step(self, step: dict) -> bool:
        """
        Execute a web_automation step by delegating to the web-automation-module.
        
        Args:
            step: Step dict with 'prompt' (str)
        
        Returns:
            bool: True if web automation completed successfully
        """
        prompt = step.get('prompt')
        if not prompt:
            self._send_status("web_automation: missing 'prompt' parameter", "warning")
            return False
            
        self._send_status(f"Starting web AI agent: {prompt}", "info")
        
        try:
            import sys
            import asyncio
            from dotenv import load_dotenv
            import subprocess
            
            # Setup path to import from web-automation-module
            web_module_path = Path(__file__).parent.parent / "web-automation-module"
            
            # Load module-specific .env for API keys and LLM settings
            module_env = web_module_path / ".env"
            if module_env.exists():
                load_dotenv(dotenv_path=module_env, override=True)
            else:
                load_dotenv() # Fallback to default .env
            
            src_path = web_module_path / "src"
            
            # Add both web_module_path and src_path to sys.path
            # This is necessary because internal modules in web-automation-module
            # use 'from src.utils import ...' while JARVIS needs direct access to these folders.
            if web_module_path.exists() and str(web_module_path) not in sys.path:
                sys.path.insert(0, str(web_module_path))
            if src_path.exists() and str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))
                
            # Import BrowserUseAgent and related components
            try:
                from utils import llm_provider
                from agent.browser_use.browser_use_agent import BrowserUseAgent
                from browser.custom_browser import CustomBrowser
                from browser_use.browser.browser import BrowserConfig
                from browser_use.browser.context import BrowserContextConfig as BUContextConfig
            except ImportError as e:
                self._send_status(f"web_automation: failed to import agent modules: {e}", "error")
                return False
                
            # Initialize LLM using the module's provider
            provider = os.getenv("DEFAULT_LLM", "google")
            
            # Detect API key from multiple possible sources (local_client uses GEMINI_API_KEY often)
            google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            
            # Safe default model for Gemini (User specifically requested gemini-flash-latest)
            model_name = "gemini-flash-latest" if provider == "google" else "gpt-4o"
            
            # Log the choice and key presence (censored)
            key_info = f" (Key: {google_key[:4]}...{google_key[-4:]})" if google_key else " (NO KEY FOUND)"
            self._send_status(f"Initializing Web AI with {provider} ({model_name}){key_info}", "info")
            
            llm = llm_provider.get_llm_model(
                provider=provider,
                model_name=model_name,
                temperature=0.7,
                api_key=google_key
            )
            
            # Setup Browser and Context
            browser_path = os.getenv("BROWSER_PATH")
            user_data_dir = os.getenv("BROWSER_USER_DATA")
            
            config_kwargs = {"headless": False, "disable_security": True}
            if browser_path:
                config_kwargs["browser_binary_path"] = browser_path
            if user_data_dir:
                config_kwargs["extra_browser_args"] = [f"--user-data-dir={user_data_dir}"]
            
            browser_instance = CustomBrowser(config=BrowserConfig(**config_kwargs))
            
            context_config = BUContextConfig(
                window_width=1280,
                window_height=1100
            )
            
            # Callbacks for JARVIS UI updates
            def step_callback(state, output, step_num):
                msg = output.current_state.next_goal if output and output.current_state else "Thinking..."
                self._send_status(f"Web AI Step {step_num}: {msg}", "info")

            async def step_error_callback(agent):
                """Callback to report internal step errors to the UI"""
                if agent.state.history.history:
                    last_step = agent.state.history.history[-1]
                    errors = [r.error for r in last_step.result if r.error]
                    if errors:
                        error_msg = "; ".join(errors)
                        step_num = len(agent.state.history.history)
                        # Correctly route through internal status helper to avoid double nesting
                        self._send_status(f"Web AI Step {step_num} Error: {error_msg}", "error")

            def done_callback(history):
                self._send_status("Web AI task complete.", "info")

            async def run_agent():
                # Correct way to get context in async
                browser_context = await browser_instance.new_context(config=context_config)
                
                # Initialize Agent correctly matching its API
                agent = BrowserUseAgent(
                    task=prompt,
                    llm=llm,
                    browser=browser_instance,
                    browser_context=browser_context,
                    register_new_step_callback=step_callback,
                    register_done_callback=done_callback,
                    use_vision=True
                )
                
                self._send_status(f"Starting web AI agent: {prompt}", "info")
                return await agent.run(on_step_end=step_error_callback)

            # Execute synchronously
            history = asyncio.run(run_agent())
            
            final_result = history.final_result()
            return f"Web Automation Result: {final_result}"

        except Exception as e:
            self._send_status(f"web_automation: error - {str(e)}", "error")
            return False


def get_click_coordinates(element_id: int, box_map: dict) -> tuple[float, float] | None:
    """
    Calculate click coordinates from box map.
    Utility function for testing.
    """
    element_id_str = str(element_id)
    coords = box_map.get(element_id_str)
    
    if coords is None:
        return None
    
    x1, y1, x2, y2 = coords
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    
    return (cx, cy)



