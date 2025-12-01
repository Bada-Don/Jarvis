"""
Plan Executor for Two-Model Pipeline
Executes execution plans using keyboard/mouse actions with vision-guided clicking.

Requirements: 1.3, 5.1, 5.2, 5.3
"""

import time
from typing import Callable, Optional

import pyautogui

# Import VisionService
try:
    from vision_service import VisionService
    VISION_SERVICE_AVAILABLE = True
except ImportError:
    VISION_SERVICE_AVAILABLE = False
    print("⚠️ Warning: vision_service not available")


class PlanExecutor:
    """
    Executes execution plans from the Planner Model.
    
    Implements single-pass architecture:
    1. Execute initial keyboard-only steps (blind steps)
    2. Take screenshot once
    3. Run SoM detection once
    4. Map all visual targets once
    5. Execute remaining steps using cached coordinates
    
    Requirements: 1.3, 5.1, 5.2, 5.3
    """
    
    def __init__(self, vision_service: VisionService, status_callback: Optional[Callable] = None):
        """
        Initialize PlanExecutor.
        
        Args:
            vision_service: VisionService instance for screenshot/SoM/mapping
            status_callback: Optional callback for progress updates
                            Signature: callback(message: str | dict, status_type: str)
        
        Requirements: 1.3
        """
        self.vision_service = vision_service
        self.status_callback = status_callback or (lambda msg, status="info": print(f"[{status}] {msg}"))
        
        # Cached vision data (single-pass architecture)
        self._id_map: Optional[dict] = None
        self._box_map: Optional[dict] = None
        self._screenshot_taken: bool = False
    
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
        
        Implements single-pass architecture:
        1. Execute blind keyboard steps first (before screenshot)
        2. Take screenshot once when first visual_click is encountered
        3. Reuse cached SoM detection and ID map for all subsequent clicks
        
        Args:
            plan: Execution plan dict with "sequence" array of steps
        
        Returns:
            bool: True if all steps completed successfully, False otherwise
        
        Requirements: 1.3, 5.1, 5.2, 5.3
        """
        sequence = plan.get('sequence', [])
        if not sequence:
            self._send_status("Empty execution plan", "warning")
            return False
        
        total_steps = len(sequence)
        self._send_status(f"Starting execution of {total_steps} steps", "info", progress=0)
        
        # Reset cached vision data for new plan
        self._id_map = None
        self._box_map = None
        self._screenshot_taken = False
        
        # Collect all visual targets for batch mapping
        visual_targets = self._collect_visual_targets(sequence)
        
        # Execute steps
        for i, step in enumerate(sequence):
            step_order = step.get('order', i + 1)
            step_type = step.get('type')
            step_desc = step.get('desc', f"Step {step_order}")
            
            progress = int((i / total_steps) * 100)
            self._send_status(f"Executing: {step_desc}", "info", progress=progress)
            
            try:
                if step_type == 'keyboard':
                    self.execute_keyboard_step(step)
                    
                elif step_type == 'visual_click':
                    # Single-pass: take screenshot and map targets on first visual click
                    if not self._screenshot_taken and visual_targets:
                        self._perform_vision_pass(visual_targets)
                    
                    target_name = step.get('target_name')
                    if target_name:
                        self.execute_visual_click(target_name, self._id_map, self._box_map)
                    else:
                        self._send_status(f"Missing target_name in step {step_order}", "warning")
                
                else:
                    self._send_status(f"Unknown step type: {step_type}", "warning")
                
                # Small delay between steps for UI stability
                time.sleep(0.3)
                
            except Exception as e:
                self._send_status(f"Error in step {step_order}: {e}", "error")
                # Continue with remaining steps (graceful degradation)
                continue
        
        self._send_status("Execution complete!", "success", progress=100)
        return True
    
    def _collect_visual_targets(self, sequence: list) -> list[str]:
        """
        Collect all unique visual target names from the sequence.
        
        Args:
            sequence: List of steps from execution plan
        
        Returns:
            list: Unique target names for visual clicks
        """
        targets = []
        for step in sequence:
            if step.get('type') == 'visual_click':
                target = step.get('target_name')
                if target and target not in targets:
                    targets.append(target)
        return targets
    
    def _perform_vision_pass(self, targets: list[str]):
        """
        Perform single-pass vision: screenshot, SoM detection, and target mapping.
        
        Requirements: 5.1, 5.2
        """
        self._send_status("Capturing screen...", "info")
        screenshot = self.vision_service.capture_screenshot()
        
        self._send_status("Analyzing UI elements...", "info")
        annotated_image, self._box_map = self.vision_service.run_som_detection(screenshot)
        
        self._send_status("Identifying targets...", "info")
        self._id_map = self.vision_service.map_targets_to_ids(annotated_image, targets)
        
        self._screenshot_taken = True
        self._send_status(f"Found {len(self._box_map)} UI elements, mapped {len([v for v in self._id_map.values() if v])} targets", "info")

    def execute_keyboard_step(self, step: dict) -> None:
        """
        Execute a keyboard action step.
        
        Handles:
        - Simple key presses (e.g., "enter", "tab")
        - Hotkey combinations (e.g., "ctrl+n", "shift+up")
        - Text typing (e.g., "PB12W3998")
        - Repeated actions via "repeats" field
        
        Args:
            step: Step dict with "value" field and optional "repeats"
        
        Requirements: 1.3
        """
        value = step.get('value', '')
        repeats = step.get('repeats', 1)
        
        if not value:
            return
        
        for _ in range(repeats):
            if '+' in value and self._is_hotkey(value):
                # Hotkey combination (e.g., "ctrl+n", "shift+up")
                self._execute_hotkey(value)
            elif len(value) == 1 or value.lower() in self._get_special_keys():
                # Single key press
                pyautogui.press(value.lower())
            else:
                # Text to type
                pyautogui.write(value, interval=0.02)
            
            # Small delay between repeats
            if repeats > 1:
                time.sleep(0.1)
    
    def _is_hotkey(self, value: str) -> bool:
        """
        Check if value is a hotkey combination vs regular text with '+'.
        
        Hotkeys have modifier keys: ctrl, alt, shift, win/cmd
        """
        modifiers = {'ctrl', 'alt', 'shift', 'win', 'cmd', 'command', 'meta'}
        parts = value.lower().split('+')
        return any(part.strip() in modifiers for part in parts)
    
    def _execute_hotkey(self, hotkey: str) -> None:
        """
        Execute a hotkey combination.
        
        Args:
            hotkey: Hotkey string like "ctrl+n" or "ctrl+shift+s"
        """
        keys = [k.strip().lower() for k in hotkey.split('+')]
        pyautogui.hotkey(*keys)
    
    def _get_special_keys(self) -> set:
        """Return set of special key names recognized by pyautogui."""
        return {
            'enter', 'return', 'tab', 'space', 'backspace', 'delete', 'del',
            'escape', 'esc', 'up', 'down', 'left', 'right',
            'home', 'end', 'pageup', 'pagedown', 'pgup', 'pgdn',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
            'insert', 'pause', 'capslock', 'numlock', 'scrolllock',
            'printscreen', 'prtsc', 'prtscr'
        }
    
    def execute_visual_click(self, target_name: str, id_map: dict, box_map: dict) -> None:
        """
        Execute a visual click on a target element.
        
        Uses the ID map to find the element ID, then the box map to get coordinates.
        Clicks at the center of the bounding box.
        
        Args:
            target_name: Name of the target element (e.g., "text_tool")
            id_map: Mapping of target names to element IDs
            box_map: Mapping of element IDs to coordinates [x1, y1, x2, y2]
        
        Requirements: 4.4, 5.3
        """
        if id_map is None or box_map is None:
            self._send_status(f"Cannot click '{target_name}': vision data not available", "warning")
            return
        
        # Get element ID from id_map
        element_id = id_map.get(target_name)
        if element_id is None:
            self._send_status(f"Target '{target_name}' not found in ID map", "warning")
            return
        
        # Get coordinates from box_map (IDs are stored as strings)
        element_id_str = str(element_id)
        coords = box_map.get(element_id_str)
        if coords is None:
            self._send_status(f"Element ID {element_id} not found in box map", "warning")
            return
        
        # Calculate center point
        # Property 4: cx = (x1 + x2) / 2, cy = (y1 + y2) / 2
        x1, y1, x2, y2 = coords
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        
        # Execute click
        self._send_status(f"Clicking '{target_name}' at ({int(cx)}, {int(cy)})", "info")
        pyautogui.click(int(cx), int(cy))


def get_click_coordinates(element_id: int, box_map: dict) -> tuple[float, float] | None:
    """
    Calculate click coordinates from box map.
    
    This is a standalone utility function for Property 4 testing.
    
    Args:
        element_id: The element ID to look up
        box_map: Mapping of element IDs to coordinates [x1, y1, x2, y2]
    
    Returns:
        tuple: (cx, cy) center coordinates, or None if not found
    
    **Feature: two-model-pipeline, Property 4: Coordinate Lookup Correctness**
    **Validates: Requirements 4.4**
    """
    element_id_str = str(element_id)
    coords = box_map.get(element_id_str)
    
    if coords is None:
        return None
    
    x1, y1, x2, y2 = coords
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    
    return (cx, cy)
