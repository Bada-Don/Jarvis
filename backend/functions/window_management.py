"""
Window Management Module

Provides functions for window management including activating, closing, minimizing,
maximizing windows, and getting the active window. Reuses WindowManager from local_client
for window detection and activation.

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 8.5, 10.1, 10.2, 10.4
"""

import sys
import os
import logging
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add local_client to path to import WindowManager
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'local_client'))

try:
    import win32gui
    import win32con
except ImportError:
    raise ImportError("pywin32 is required for window management. Install with: pip install pywin32")

from window_manager import WindowManager


# Create a singleton WindowManager instance
# Requirements: 8.5
_window_manager = WindowManager(verbose=False)


def activate_window(identifier: str) -> Dict[str, any]:
    """
    Activate a window by title or process name.
    
    Uses: WindowManager.find_window_for_app() and activate_window()
    Reuses: WindowManager from local_client/window_manager.py
    
    Args:
        identifier: Window title or app name (e.g., 'chrome', 'notepad', 'Calculator')
        
    Returns:
        {"success": bool, "message": str, "identifier": str, "window_title": str}
        
    Requirements: 7.1, 7.6, 8.5, 10.1, 10.2, 10.4
    """
    try:
        # Requirement 10.1: Descriptive error messages for invalid parameters
        if not isinstance(identifier, str):
            error_msg = (
                f"Identifier must be a string, got: {type(identifier).__name__} "
                f"(value: {identifier})"
            )
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "identifier": identifier,
                "window_title": None
            }
        
        if not identifier or not identifier.strip():
            error_msg = "Identifier cannot be empty. Provide a window title or app name."
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "identifier": identifier,
                "window_title": None
            }
        
        logger.info(f"Attempting to activate window: '{identifier}'")
        
        # Try to find the window using WindowManager
        result = _window_manager.find_window_for_app(identifier)
        
        if not result:
            # Requirement 10.4: Clear error messages for missing resources
            error_msg = (
                f"Window not found: '{identifier}'. "
                f"No window matching this title or app name is currently open."
            )
            logger.warning(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "identifier": identifier,
                "window_title": None
            }
        
        hwnd, window_title = result
        logger.debug(f"Found window: '{window_title}' (hwnd: {hwnd})")
        
        # Activate the window
        success = _window_manager.activate_window(hwnd)
        
        if success:
            logger.info(f"✓ Activated window: '{window_title}'")
            return {
                "success": True,
                "message": f"Activated window '{window_title}' successfully",
                "identifier": identifier,
                "window_title": window_title
            }
        else:
            # Requirement 10.2: Logging with context for all failures
            error_msg = f"Failed to activate window '{window_title}' (hwnd: {hwnd})"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "identifier": identifier,
                "window_title": window_title
            }
        
    except Exception as e:
        # Requirement 10.2: Logging with context for all failures
        error_msg = f"Failed to activate window '{identifier}': {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "success": False,
            "message": error_msg,
            "identifier": identifier if 'identifier' in locals() else None,
            "window_title": None
        }


def close_window(identifier: str) -> Dict[str, any]:
    """
    Close a window by title or process name.
    
    Uses: WindowManager to find window, then win32gui.PostMessage(WM_CLOSE)
    Reuses: WindowManager from local_client/window_manager.py
    
    Args:
        identifier: Window title or app name
        
    Returns:
        {"success": bool, "message": str, "identifier": str, "window_title": str}
        
    Requirements: 7.2, 7.6, 8.5
    """
    try:
        # Validate identifier
        if not isinstance(identifier, str):
            return {
                "success": False,
                "message": f"Identifier must be a string, got: {type(identifier).__name__}",
                "identifier": identifier,
                "window_title": None
            }
        
        if not identifier or not identifier.strip():
            return {
                "success": False,
                "message": "Identifier cannot be empty",
                "identifier": identifier,
                "window_title": None
            }
        
        # Try to find the window using WindowManager
        result = _window_manager.find_window_for_app(identifier)
        
        if not result:
            # Window not found - handle gracefully
            return {
                "success": False,
                "message": f"Window not found: {identifier}",
                "identifier": identifier,
                "window_title": None
            }
        
        hwnd, window_title = result
        
        # Close the window by posting WM_CLOSE message
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        
        return {
            "success": True,
            "message": f"Closed window '{window_title}' successfully",
            "identifier": identifier,
            "window_title": window_title
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to close window: {str(e)}",
            "identifier": identifier if 'identifier' in locals() else None,
            "window_title": None
        }


def minimize_window(identifier: str) -> Dict[str, any]:
    """
    Minimize a window by title or process name.
    
    Uses: WindowManager + win32gui.ShowWindow(SW_MINIMIZE)
    Reuses: WindowManager from local_client/window_manager.py
    
    Args:
        identifier: Window title or app name
        
    Returns:
        {"success": bool, "message": str, "identifier": str, "window_title": str}
        
    Requirements: 7.3, 7.6, 8.5
    """
    try:
        # Validate identifier
        if not isinstance(identifier, str):
            return {
                "success": False,
                "message": f"Identifier must be a string, got: {type(identifier).__name__}",
                "identifier": identifier,
                "window_title": None
            }
        
        if not identifier or not identifier.strip():
            return {
                "success": False,
                "message": "Identifier cannot be empty",
                "identifier": identifier,
                "window_title": None
            }
        
        # Try to find the window using WindowManager
        result = _window_manager.find_window_for_app(identifier)
        
        if not result:
            # Window not found - handle gracefully
            return {
                "success": False,
                "message": f"Window not found: {identifier}",
                "identifier": identifier,
                "window_title": None
            }
        
        hwnd, window_title = result
        
        # Minimize the window
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        
        return {
            "success": True,
            "message": f"Minimized window '{window_title}' successfully",
            "identifier": identifier,
            "window_title": window_title
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to minimize window: {str(e)}",
            "identifier": identifier if 'identifier' in locals() else None,
            "window_title": None
        }


def maximize_window(identifier: str) -> Dict[str, any]:
    """
    Maximize a window by title or process name.
    
    Uses: WindowManager + win32gui.ShowWindow(SW_MAXIMIZE)
    Reuses: WindowManager from local_client/window_manager.py
    
    Args:
        identifier: Window title or app name
        
    Returns:
        {"success": bool, "message": str, "identifier": str, "window_title": str}
        
    Requirements: 7.4, 7.6, 8.5
    """
    try:
        # Validate identifier
        if not isinstance(identifier, str):
            return {
                "success": False,
                "message": f"Identifier must be a string, got: {type(identifier).__name__}",
                "identifier": identifier,
                "window_title": None
            }
        
        if not identifier or not identifier.strip():
            return {
                "success": False,
                "message": "Identifier cannot be empty",
                "identifier": identifier,
                "window_title": None
            }
        
        # Try to find the window using WindowManager
        result = _window_manager.find_window_for_app(identifier)
        
        if not result:
            # Window not found - handle gracefully
            return {
                "success": False,
                "message": f"Window not found: {identifier}",
                "identifier": identifier,
                "window_title": None
            }
        
        hwnd, window_title = result
        
        # Maximize the window
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        
        return {
            "success": True,
            "message": f"Maximized window '{window_title}' successfully",
            "identifier": identifier,
            "window_title": window_title
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to maximize window: {str(e)}",
            "identifier": identifier if 'identifier' in locals() else None,
            "window_title": None
        }


def get_active_window() -> Dict[str, any]:
    """
    Get the currently active window title.
    
    Uses: WindowManager.get_foreground_window_title()
    Reuses: WindowManager from local_client/window_manager.py
    
    Returns:
        {"success": bool, "title": str, "message": str}
        
    Requirements: 7.5, 8.5
    """
    try:
        # Get the foreground window title using WindowManager
        title = _window_manager.get_foreground_window_title()
        
        if title:
            return {
                "success": True,
                "title": title,
                "message": f"Active window: '{title}'"
            }
        else:
            return {
                "success": False,
                "title": "",
                "message": "No active window found"
            }
        
    except Exception as e:
        return {
            "success": False,
            "title": "",
            "message": f"Failed to get active window: {str(e)}"
        }
