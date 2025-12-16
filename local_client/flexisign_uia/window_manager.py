"""
Window detection and activation utilities for FlexiSIGN.
"""

import time
from typing import Optional

# Import window activation utilities from modular file
from force_activate_flexisign import (
    find_flexisign_window,
    get_pid_from_window,
    force_activate_window
)


class WindowManager:
    """Handles FlexiSIGN window detection and activation."""
    
    def __init__(self, uia_instance, root_refresh_callback):
        """
        Initialize window manager.
        
        Args:
            uia_instance: Reference to UIA COM object
            root_refresh_callback: Callback to refresh root element after activation
        """
        self._uia = uia_instance
        self._refresh_root = root_refresh_callback
        self._pid: Optional[int] = None
    
    @property
    def pid(self) -> Optional[int]:
        """Get the current FlexiSIGN process ID."""
        return self._pid
    
    def find_and_activate_window(self, get_root_callback) -> bool:
        """
        Find FlexiSIGN window and bring to foreground.
        Implements retry logic with 5-second wait.
        Uses modular functions from force_activate_flexisign module.
        
        Args:
            get_root_callback: Callback function to get current root element
        
        Returns:
            True if successful, False otherwise.
        """
        # First attempt
        window = find_flexisign_window()
        if window:
            pid = get_pid_from_window(window)
            if pid:
                self._pid = pid
                print(f"Found FlexiSIGN with PID: {pid}")
                if force_activate_window(window, verbose=True):
                    self._refresh_root()
                    if get_root_callback() is not None:
                        print("Window activated and root element found successfully")
                        return True
                    else:
                        print("Window activated but root element not found, retrying...")
        
        # Wait 5 seconds and retry once
        print("Waiting 5 seconds before retry...")
        time.sleep(5)
        
        window = find_flexisign_window()
        if window:
            pid = get_pid_from_window(window)
            if pid:
                self._pid = pid
                print(f"Retry: Found FlexiSIGN with PID: {pid}")
                if force_activate_window(window, verbose=True):
                    self._refresh_root()
                    if get_root_callback() is not None:
                        print("Window activated and root element found successfully on retry")
                        return True
                    else:
                        print("ERROR: Window activated but root element still not found")
        
        print("ERROR: Failed to find and activate FlexiSIGN window")
        return False
