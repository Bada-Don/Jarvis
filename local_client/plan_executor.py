"""
Plan Executor for Two-Model Pipeline
Executes execution plans using keyboard/mouse actions with vision-guided clicking.
Includes robust window activation and timing management.
"""

import time
import re
from typing import Callable, Optional

import pyautogui

# Safety settings
pyautogui.FAILSAFE = False  # Disable fail-safe (corner abort) for uninterrupted automation
pyautogui.PAUSE = 0.05  # Minimal pause, we handle timing ourselves

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
        r'^win$',           # Windows key alone (Start menu)
        r'^enter$',         # Enter after typing app name
        r'^win\+r$',        # Run dialog
        r'^ctrl\+n$',       # New window in many apps
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
        
        # Cached vision data (single-pass architecture)
        self._id_map: Optional[dict] = None
        self._box_map: Optional[dict] = None
        self._screenshot_taken: bool = False
        self._mode: str = "general"
        
        # Track app launches for window activation
        self._pending_app_name: Optional[str] = None
        self._last_typed_text: Optional[str] = None
    
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

    def execute_plan(self, plan: dict) -> bool:
        """
        Execute an execution plan from the Planner Model.
        Routes to direct or vision mode based on plan['mode'].
        
        Args:
            plan: Execution plan dict with "sequence" array and optional "mode"
        
        Returns:
            bool: True if all steps completed successfully
        """
        sequence = plan.get('sequence', [])
        if not sequence:
            self._send_status("Empty execution plan", "warning")
            return False
        
        mode = plan.get('mode', 'vision')
        
        # Route to appropriate execution mode
        # 'direct' or 'flexisign' both use direct automation
        if mode in ('direct', 'flexisign'):
            return self._execute_direct_plan(plan)
        else:
            return self._execute_vision_plan(plan)
    
    def _execute_direct_plan(self, plan: dict) -> bool:
        """
        Execute plan using UIA (no vision/screenshots).
        
        Args:
            plan: Execution plan dict with "sequence" array
            
        Returns:
            bool: True if all steps completed successfully
        """
        if not FLEXISIGN_UIA_AVAILABLE:
            self._send_status("FlexiSIGN UIA module not available", "error")
            return False
        
        sequence = plan.get('sequence', [])
        total_steps = len(sequence)
        
        self._send_status(f"Starting direct automation of {total_steps} steps", "info", progress=0)
        
        # Initialize UIA if needed
        if self._flexisign_uia is None:
            try:
                self._flexisign_uia = FlexiSignUIA()
            except Exception as e:
                self._send_status(f"Failed to initialize FlexiSIGN UIA: {e}", "error")
                return False
        
        # Activate FlexiSIGN window
        if not self._flexisign_uia.find_and_activate_window():
            self._send_status("Failed to activate FlexiSIGN window", "error")
            return False
        
        self._send_status("FlexiSIGN window activated", "info", progress=5)
        
        # Execute each step
        for i, step in enumerate(sequence):
            step_order = step.get('order', i + 1)
            step_desc = step.get('desc', f"Step {step_order}")
            
            progress = int(((i + 1) / total_steps) * 90) + 5
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
        
        self._send_status("Direct automation complete!", "success", progress=100)
        return True
    
    def _execute_vision_plan(self, plan: dict) -> bool:
        """
        Execute plan using vision-based pipeline (existing logic).
        
        Args:
            plan: Execution plan dict with "sequence" array
            
        Returns:
            bool: True if all steps completed successfully
        """
        sequence = plan.get('sequence', [])
        self._mode = plan.get('mode', 'general')
        
        total_steps = len(sequence)
        self._send_status(f"Starting execution of {total_steps} steps (mode: {self._mode})", "info", progress=0)
        
        # Reset state for new plan
        self._id_map = None
        self._box_map = None
        self._screenshot_taken = False
        self._pending_app_name = None
        self._last_typed_text = None
        
        # Collect all visual targets for batch mapping
        visual_targets = self._collect_visual_targets(sequence)
        
        # Execute steps
        for i, step in enumerate(sequence):
            step_order = step.get('order', i + 1)
            step_type = step.get('type')
            step_desc = step.get('desc', f"Step {step_order}")
            
            progress = int(((i + 1) / total_steps) * 85) + 10
            self._send_status(f"Step {step_order}: {step_desc}", "info", progress=progress)
            
            try:
                if step_type == 'keyboard':
                    self._execute_keyboard_step(step, sequence, i)
                    if DEBUG_LOGGER_AVAILABLE:
                        get_debug_logger().log_step_execution(
                            step_order, "keyboard", 
                            f"value='{step.get('value', '')}' desc='{step_desc}'"
                        )
                    
                elif step_type == 'visual_click':
                    # Single-pass: take screenshot and map targets on first visual click
                    if not self._screenshot_taken and visual_targets:
                        self._perform_vision_pass(visual_targets)
                    
                    target_name = step.get('target_name')
                    if target_name:
                        self._execute_visual_click(target_name)
                        if DEBUG_LOGGER_AVAILABLE:
                            element_id = self._id_map.get(target_name) if self._id_map else None
                            get_debug_logger().log_step_execution(
                                step_order, "visual_click",
                                f"target='{target_name}' id={element_id} desc='{step_desc}'"
                            )
                    else:
                        self._send_status(f"Missing target_name in step {step_order}", "warning")
                
                else:
                    self._send_status(f"Unknown step type: {step_type}", "warning")
                
            except Exception as e:
                self._send_status(f"Error in step {step_order}: {e}", "error")
                if DEBUG_LOGGER_AVAILABLE:
                    get_debug_logger().log_step_execution(
                        step_order, step_type, f"ERROR: {e}", success=False
                    )
                continue
        
        self._send_status("Execution complete!", "success", progress=100)
        return True
    
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
    
    def _perform_vision_pass(self, targets: list[str]):
        """Perform single-pass vision: screenshot, SoM detection, and target mapping."""
        self._send_status("Capturing screen...", "info")
        
        # Wait for any UI transitions to complete
        time.sleep(0.5)
        
        # Ensure window is focused before screenshot
        if self.window_manager:
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
                    # Check if there was a Win key press before
                    for j in range(current_index - 1, -1, -1):
                        check_val = sequence[j].get('value', '').lower()
                        if check_val == 'win' or check_val == 'windows':
                            return True
                        # Stop if we hit another Enter (different context)
                        if check_val == 'enter':
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
        """
        # Look backwards for typed text
        for i in range(current_index - 1, max(-1, current_index - 5), -1):
            step = sequence[i]
            if step.get('type') == 'keyboard':
                value = step.get('value', '')
                # Skip special keys and shortcuts
                if not self._is_special_key(value.lower()) and '+' not in value and len(value) > 1:
                    return value
        
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
        
        # Ensure window is focused before keyboard input
        if self.window_manager:
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
        """
        if not self.window_manager:
            # Fallback: just wait
            self._send_status("Waiting for application to start...", "info")
            time.sleep(self.DELAY_AFTER_APP_LAUNCH)
            return
        
        # Try to determine what app was launched
        app_name = self._get_app_name_from_context(sequence, current_index)
        
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
        # Ensure window is focused before clicking
        if self.window_manager:
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
