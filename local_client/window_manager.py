"""
Window Manager for JARVIS
Handles window detection, activation, and focus management.
Ensures windows are properly focused before sending keyboard/mouse events.
"""

import time
import win32gui
import win32con
import win32process
import win32api
import ctypes
from typing import Optional, List, Tuple


class WindowManager:
    """
    Manages window detection and activation for automation tasks.
    Ensures target windows are visible and focused before interactions.
    """
    
    # Common app names and their window title patterns
    APP_WINDOW_PATTERNS = {
        'chrome': ['Google Chrome', 'Chrome'],
        'firefox': ['Mozilla Firefox', 'Firefox'],
        'edge': ['Microsoft Edge', 'Edge'],
        'notepad': ['Notepad', 'Untitled - Notepad'],
        'calculator': ['Calculator'],
        'explorer': ['File Explorer', 'This PC'],
        'word': ['Word', 'Document'],
        'excel': ['Excel', 'Book'],
        'code': ['Visual Studio Code'],
        'terminal': ['Terminal', 'Command Prompt', 'PowerShell'],
        'cmd': ['Command Prompt', 'cmd.exe'],
        'powershell': ['PowerShell'],
    }
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._last_activated_hwnd: Optional[int] = None
    
    def log(self, message: str):
        if self.verbose:
            print(f"[WindowManager] {message}")
    
    def find_windows_by_title(self, title_patterns: List[str], partial_match: bool = True) -> List[Tuple[int, str]]:
        """
        Find all windows matching any of the given title patterns.
        
        Returns:
            List of (hwnd, window_title) tuples
        """
        if isinstance(title_patterns, str):
            title_patterns = [title_patterns]
        
        found_windows = []
        
        def callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    for pattern in title_patterns:
                        if partial_match:
                            if pattern.lower() in window_text.lower():
                                results.append((hwnd, window_text))
                                break
                        else:
                            if pattern.lower() == window_text.lower():
                                results.append((hwnd, window_text))
                                break
            return True
        
        win32gui.EnumWindows(callback, found_windows)
        return found_windows
    
    def find_window_for_app(self, app_name: str) -> Optional[Tuple[int, str]]:
        """
        Find a window for a known application.
        
        Args:
            app_name: Application name (e.g., 'chrome', 'notepad')
        
        Returns:
            (hwnd, window_title) or None if not found
        """
        app_lower = app_name.lower()
        
        # Check known patterns first
        patterns = self.APP_WINDOW_PATTERNS.get(app_lower, [app_name])
        
        windows = self.find_windows_by_title(patterns)
        if windows:
            # Return the first match (most recently created usually)
            return windows[0]
        
        # Fallback: search for app name directly
        windows = self.find_windows_by_title([app_name])
        if windows:
            return windows[0]
        
        return None
    
    def is_window_minimized(self, hwnd: int) -> bool:
        """Check if a window is minimized."""
        try:
            placement = win32gui.GetWindowPlacement(hwnd)
            return placement[1] == win32con.SW_SHOWMINIMIZED
        except:
            return False
    
    def is_window_foreground(self, hwnd: int) -> bool:
        """Check if a window is the foreground window."""
        try:
            return win32gui.GetForegroundWindow() == hwnd
        except:
            return False
    
    def activate_window(self, hwnd: int, max_attempts: int = 3) -> bool:
        """
        Bring a window to the foreground and ensure it's active.
        Uses multiple strategies to handle Windows focus restrictions.
        
        Args:
            hwnd: Window handle
            max_attempts: Maximum activation attempts
        
        Returns:
            True if window is now in foreground
        """
        if not win32gui.IsWindow(hwnd):
            self.log(f"Window handle {hwnd} is invalid")
            return False
        
        window_title = win32gui.GetWindowText(hwnd)
        self.log(f"Activating window: '{window_title}'")
        
        for attempt in range(max_attempts):
            try:
                # Step 1: Restore if minimized
                if self.is_window_minimized(hwnd):
                    self.log("Window is minimized, restoring...")
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(0.2)
                
                # Step 2: Show the window
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                time.sleep(0.1)
                
                # Step 3: Try SetForegroundWindow directly
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except Exception as e:
                    self.log(f"SetForegroundWindow failed: {e}, trying alternative method")
                    # Use the Alt key trick to bypass Windows restrictions
                    self._force_foreground(hwnd)
                
                time.sleep(0.2)
                
                # Step 4: Verify activation
                if self.is_window_foreground(hwnd):
                    self.log(f"Window activated successfully on attempt {attempt + 1}")
                    self._last_activated_hwnd = hwnd
                    return True
                
                self.log(f"Activation attempt {attempt + 1} failed, retrying...")
                time.sleep(0.3)
                
            except Exception as e:
                self.log(f"Error during activation attempt {attempt + 1}: {e}")
        
        self.log(f"Failed to activate window after {max_attempts} attempts")
        return False
    
    def _force_foreground(self, hwnd: int):
        """
        Force a window to foreground using thread attachment trick.
        This bypasses Windows' foreground lock.
        """
        try:
            # Get the thread IDs
            current_hwnd = win32gui.GetForegroundWindow()
            current_thread_id = win32process.GetWindowThreadProcessId(current_hwnd)[0]
            target_thread_id = win32process.GetWindowThreadProcessId(hwnd)[0]
            
            # Attach threads if different
            if current_thread_id != target_thread_id:
                win32process.AttachThreadInput(target_thread_id, current_thread_id, True)
                win32gui.SetForegroundWindow(hwnd)
                win32process.AttachThreadInput(target_thread_id, current_thread_id, False)
            else:
                win32gui.SetForegroundWindow(hwnd)
            
            # Also try BringWindowToTop
            win32gui.BringWindowToTop(hwnd)
            
        except Exception as e:
            self.log(f"Force foreground error: {e}")
            # Last resort: simulate Alt key press
            try:
                # Press and release Alt to allow focus change
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32gui.SetForegroundWindow(hwnd)
            except:
                pass
    
    def wait_for_window(self, app_name: str, timeout: float = 10.0, poll_interval: float = 0.5) -> Optional[int]:
        """
        Wait for a window to appear for a given application.
        
        Args:
            app_name: Application name to look for
            timeout: Maximum time to wait in seconds
            poll_interval: How often to check for the window
        
        Returns:
            Window handle if found, None if timeout
        """
        self.log(f"Waiting for window: '{app_name}' (timeout: {timeout}s)")
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            result = self.find_window_for_app(app_name)
            if result:
                hwnd, title = result
                self.log(f"Found window: '{title}' (hwnd: {hwnd})")
                return hwnd
            
            time.sleep(poll_interval)
        
        self.log(f"Timeout waiting for window: '{app_name}'")
        return None
    
    def wait_and_activate(self, app_name: str, timeout: float = 10.0) -> bool:
        """
        Wait for a window to appear and activate it.
        
        Args:
            app_name: Application name to look for
            timeout: Maximum time to wait
        
        Returns:
            True if window was found and activated
        """
        hwnd = self.wait_for_window(app_name, timeout)
        if hwnd:
            return self.activate_window(hwnd)
        return False
    
    def ensure_foreground_before_input(self) -> bool:
        """
        Ensure the last activated window is still in foreground.
        Call this before sending keyboard/mouse input.
        
        Returns:
            True if a window is properly focused
        """
        if self._last_activated_hwnd:
            if not self.is_window_foreground(self._last_activated_hwnd):
                self.log("Window lost focus, re-activating...")
                return self.activate_window(self._last_activated_hwnd)
            return True
        
        # No specific window tracked, check if any window is focused
        fg_hwnd = win32gui.GetForegroundWindow()
        return fg_hwnd != 0
    
    def get_foreground_window_title(self) -> str:
        """Get the title of the current foreground window."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(hwnd)
        except:
            return ""


# Singleton instance for easy access
_window_manager: Optional[WindowManager] = None


def get_window_manager(verbose: bool = False) -> WindowManager:
    """Get or create the singleton WindowManager instance."""
    global _window_manager
    if _window_manager is None:
        _window_manager = WindowManager(verbose=verbose)
    return _window_manager
