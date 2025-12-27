"""
Mouse Operations Module

Provides functions for mouse automation including clicking, double-clicking, right-clicking,
moving the mouse, and dragging. Reuses patterns from mouse_controller.py and includes
coordinate bounds validation for all operations.

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 8.4
"""

import time
import logging
from typing import Dict, Tuple

import pyautogui

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Timing configuration (reused from mouse_controller.py)
# Requirements: 8.4
DELAY_AFTER_CLICK = 0.1         # Small delay after click operations
DELAY_AFTER_MOVE = 0.05         # Minimal delay after mouse movement


def setup_pyautogui():
    """
    Configure pyautogui settings.
    
    Reused from mouse_controller.py
    
    Requirements: 8.4
    """
    # Disable fail-safes as requested
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0  # No automatic pause between actions


def get_screen_size() -> Tuple[int, int]:
    """
    Get the current screen dimensions.
    
    Returns:
        (width, height) tuple
        
    Requirements: 6.6
    """
    return pyautogui.size()


def validate_coordinates(x: int, y: int) -> Tuple[bool, str]:
    """
    Validate that coordinates are within screen bounds.
    
    Args:
        x: X coordinate
        y: Y coordinate
        
    Returns:
        (is_valid, error_message) tuple
        
    Requirements: 6.6, 10.1 (Descriptive error messages for invalid parameters)
    """
    try:
        screen_width, screen_height = get_screen_size()
        
        # Requirement 10.1: Descriptive error messages
        if x < 0 or x >= screen_width:
            error_msg = (
                f"X coordinate {x} is out of bounds. "
                f"Valid range: 0 to {screen_width - 1} (screen width: {screen_width})"
            )
            logger.warning(error_msg)
            return False, error_msg
        
        if y < 0 or y >= screen_height:
            error_msg = (
                f"Y coordinate {y} is out of bounds. "
                f"Valid range: 0 to {screen_height - 1} (screen height: {screen_height})"
            )
            logger.warning(error_msg)
            return False, error_msg
        
        return True, ""
        
    except Exception as e:
        # Requirement 10.2: Logging with context for all failures
        error_msg = f"Failed to validate coordinates ({x}, {y}): {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def click(x: int, y: int) -> Dict[str, any]:
    """
    Click at screen coordinates.
    
    Uses: pyautogui.click()
    Reuses: Coordinate validation logic
    
    Args:
        x: X coordinate (must be within screen bounds)
        y: Y coordinate (must be within screen bounds)
        
    Returns:
        {"success": bool, "message": str, "x": int, "y": int}
        
    Requirements: 6.1, 6.6, 8.4, 10.1, 10.2
    """
    try:
        # Requirement 10.1: Descriptive error messages for invalid parameters
        if not isinstance(x, int):
            error_msg = f"X coordinate must be an integer, got: {type(x).__name__} (value: {x})"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "x": x,
                "y": y
            }
        
        if not isinstance(y, int):
            error_msg = f"Y coordinate must be an integer, got: {type(y).__name__} (value: {y})"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "x": x,
                "y": y
            }
        
        # Validate coordinates are within screen bounds
        is_valid, error_msg = validate_coordinates(x, y)
        if not is_valid:
            # Requirement 10.2: Logging with context already done in validate_coordinates
            return {
                "success": False,
                "message": error_msg,
                "x": x,
                "y": y
            }
        
        # Configure pyautogui
        setup_pyautogui()
        
        # Perform the click using pyautogui
        logger.info(f"Clicking at ({x}, {y})")
        pyautogui.click(x, y)
        
        # Small delay after click
        time.sleep(DELAY_AFTER_CLICK)
        
        logger.info(f"✓ Click at ({x}, {y}) successful")
        return {
            "success": True,
            "message": f"Clicked at ({x}, {y}) successfully",
            "x": x,
            "y": y
        }
        
    except Exception as e:
        # Requirement 10.2: Logging with context for all failures
        error_msg = f"Failed to click at ({x}, {y}): {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "success": False,
            "message": error_msg,
            "x": x if 'x' in locals() else None,
            "y": y if 'y' in locals() else None
        }


def double_click(x: int, y: int) -> Dict[str, any]:
    """
    Double-click at screen coordinates.
    
    Uses: pyautogui.doubleClick()
    
    Args:
        x: X coordinate (must be within screen bounds)
        y: Y coordinate (must be within screen bounds)
        
    Returns:
        {"success": bool, "message": str, "x": int, "y": int}
        
    Requirements: 6.2, 6.6, 8.4
    """
    try:
        # Validate coordinate types
        if not isinstance(x, int):
            return {
                "success": False,
                "message": f"X coordinate must be an integer, got: {type(x).__name__}",
                "x": x,
                "y": y
            }
        
        if not isinstance(y, int):
            return {
                "success": False,
                "message": f"Y coordinate must be an integer, got: {type(y).__name__}",
                "x": x,
                "y": y
            }
        
        # Validate coordinates are within screen bounds
        is_valid, error_msg = validate_coordinates(x, y)
        if not is_valid:
            return {
                "success": False,
                "message": error_msg,
                "x": x,
                "y": y
            }
        
        # Configure pyautogui
        setup_pyautogui()
        
        # Perform the double-click using pyautogui
        pyautogui.doubleClick(x, y)
        
        # Small delay after double-click
        time.sleep(DELAY_AFTER_CLICK)
        
        return {
            "success": True,
            "message": f"Double-clicked at ({x}, {y}) successfully",
            "x": x,
            "y": y
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to double-click: {str(e)}",
            "x": x if 'x' in locals() else None,
            "y": y if 'y' in locals() else None
        }


def right_click(x: int, y: int) -> Dict[str, any]:
    """
    Right-click at screen coordinates.
    
    Uses: pyautogui.rightClick()
    
    Args:
        x: X coordinate (must be within screen bounds)
        y: Y coordinate (must be within screen bounds)
        
    Returns:
        {"success": bool, "message": str, "x": int, "y": int}
        
    Requirements: 6.3, 6.6, 8.4
    """
    try:
        # Validate coordinate types
        if not isinstance(x, int):
            return {
                "success": False,
                "message": f"X coordinate must be an integer, got: {type(x).__name__}",
                "x": x,
                "y": y
            }
        
        if not isinstance(y, int):
            return {
                "success": False,
                "message": f"Y coordinate must be an integer, got: {type(y).__name__}",
                "x": x,
                "y": y
            }
        
        # Validate coordinates are within screen bounds
        is_valid, error_msg = validate_coordinates(x, y)
        if not is_valid:
            return {
                "success": False,
                "message": error_msg,
                "x": x,
                "y": y
            }
        
        # Configure pyautogui
        setup_pyautogui()
        
        # Perform the right-click using pyautogui
        pyautogui.rightClick(x, y)
        
        # Small delay after right-click
        time.sleep(DELAY_AFTER_CLICK)
        
        return {
            "success": True,
            "message": f"Right-clicked at ({x}, {y}) successfully",
            "x": x,
            "y": y
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to right-click: {str(e)}",
            "x": x if 'x' in locals() else None,
            "y": y if 'y' in locals() else None
        }


def move_mouse(x: int, y: int, duration: float = 0.0) -> Dict[str, any]:
    """
    Move mouse to coordinates.
    
    Uses: pyautogui.moveTo()
    
    Args:
        x: X coordinate (must be within screen bounds)
        y: Y coordinate (must be within screen bounds)
        duration: Movement duration in seconds (0 for instant)
        
    Returns:
        {"success": bool, "message": str, "x": int, "y": int, "duration": float}
        
    Requirements: 6.4, 6.6, 8.4
    """
    try:
        # Validate coordinate types
        if not isinstance(x, int):
            return {
                "success": False,
                "message": f"X coordinate must be an integer, got: {type(x).__name__}",
                "x": x,
                "y": y,
                "duration": duration
            }
        
        if not isinstance(y, int):
            return {
                "success": False,
                "message": f"Y coordinate must be an integer, got: {type(y).__name__}",
                "x": x,
                "y": y,
                "duration": duration
            }
        
        # Validate duration
        if not isinstance(duration, (int, float)):
            return {
                "success": False,
                "message": f"Duration must be a number, got: {type(duration).__name__}",
                "x": x,
                "y": y,
                "duration": duration
            }
        
        if duration < 0:
            return {
                "success": False,
                "message": f"Duration must be non-negative, got: {duration}",
                "x": x,
                "y": y,
                "duration": duration
            }
        
        # Validate coordinates are within screen bounds
        is_valid, error_msg = validate_coordinates(x, y)
        if not is_valid:
            return {
                "success": False,
                "message": error_msg,
                "x": x,
                "y": y,
                "duration": duration
            }
        
        # Configure pyautogui
        setup_pyautogui()
        
        # Move the mouse using pyautogui
        pyautogui.moveTo(x, y, duration=duration)
        
        # Small delay after movement
        time.sleep(DELAY_AFTER_MOVE)
        
        return {
            "success": True,
            "message": f"Moved mouse to ({x}, {y}) in {duration}s successfully",
            "x": x,
            "y": y,
            "duration": duration
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to move mouse: {str(e)}",
            "x": x if 'x' in locals() else None,
            "y": y if 'y' in locals() else None,
            "duration": duration if 'duration' in locals() else None
        }


def drag(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> Dict[str, any]:
    """
    Drag from start to end coordinates.
    
    Uses: pyautogui.moveTo() and pyautogui.drag()
    Reuses: Coordinate validation logic
    
    Args:
        start_x: Starting X coordinate (must be within screen bounds)
        start_y: Starting Y coordinate (must be within screen bounds)
        end_x: Ending X coordinate (must be within screen bounds)
        end_y: Ending Y coordinate (must be within screen bounds)
        duration: Drag duration in seconds (default 0.5s)
        
    Returns:
        {"success": bool, "message": str, "start_x": int, "start_y": int, 
         "end_x": int, "end_y": int, "duration": float}
        
    Requirements: 6.5, 6.6, 8.4
    """
    try:
        # Validate coordinate types
        if not isinstance(start_x, int):
            return {
                "success": False,
                "message": f"Start X coordinate must be an integer, got: {type(start_x).__name__}",
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "duration": duration
            }
        
        if not isinstance(start_y, int):
            return {
                "success": False,
                "message": f"Start Y coordinate must be an integer, got: {type(start_y).__name__}",
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "duration": duration
            }
        
        if not isinstance(end_x, int):
            return {
                "success": False,
                "message": f"End X coordinate must be an integer, got: {type(end_x).__name__}",
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "duration": duration
            }
        
        if not isinstance(end_y, int):
            return {
                "success": False,
                "message": f"End Y coordinate must be an integer, got: {type(end_y).__name__}",
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "duration": duration
            }
        
        # Validate duration
        if not isinstance(duration, (int, float)):
            return {
                "success": False,
                "message": f"Duration must be a number, got: {type(duration).__name__}",
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "duration": duration
            }
        
        if duration < 0:
            return {
                "success": False,
                "message": f"Duration must be non-negative, got: {duration}",
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "duration": duration
            }
        
        # Validate start coordinates are within screen bounds
        is_valid, error_msg = validate_coordinates(start_x, start_y)
        if not is_valid:
            return {
                "success": False,
                "message": f"Start coordinates invalid: {error_msg}",
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "duration": duration
            }
        
        # Validate end coordinates are within screen bounds
        is_valid, error_msg = validate_coordinates(end_x, end_y)
        if not is_valid:
            return {
                "success": False,
                "message": f"End coordinates invalid: {error_msg}",
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "duration": duration
            }
        
        # Configure pyautogui
        setup_pyautogui()
        
        # Move to start position first
        pyautogui.moveTo(start_x, start_y, duration=0)
        
        # Calculate relative drag distance
        drag_x = end_x - start_x
        drag_y = end_y - start_y
        
        # Perform the drag using pyautogui
        pyautogui.drag(drag_x, drag_y, duration=duration, button='left')
        
        # Small delay after drag
        time.sleep(DELAY_AFTER_CLICK)
        
        return {
            "success": True,
            "message": f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y}) in {duration}s successfully",
            "start_x": start_x,
            "start_y": start_y,
            "end_x": end_x,
            "end_y": end_y,
            "duration": duration
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to drag: {str(e)}",
            "start_x": start_x if 'start_x' in locals() else None,
            "start_y": start_y if 'start_y' in locals() else None,
            "end_x": end_x if 'end_x' in locals() else None,
            "end_y": end_y if 'end_y' in locals() else None,
            "duration": duration if 'duration' in locals() else None
        }
