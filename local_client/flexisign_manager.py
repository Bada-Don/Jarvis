"""
FlexiSign Manager - Robust automation for FlexiSign Pro with loader/patcher
Ensures FlexiSign Pro never runs in restricted/demo mode
"""
import json
import time
import os
import subprocess
import psutil
import win32gui
import win32con
import win32process
import pyautogui
from typing import Optional, List, Dict, Tuple


class FlexiSignManager:
    def __init__(self, config_path=None, status_callback=None):
        """Initialize the FlexiSign Manager with configuration."""
        if config_path is None:
            # Default to flexisign_config.json in the same directory as this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, 'flexisign_config.json')
        self.config = self._load_config(config_path)
        self.verbose = self.config['debug']['verbose_logging']
        self.status_callback = status_callback
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "DEBUG": "🔍"
        }.get(level, "•")
        print(f"[{timestamp}] {prefix} {message}")
    
    def send_progress(self, message: str, progress: int, status: str = "running"):
        """Send progress update via callback."""
        if self.status_callback:
            self.status_callback({
                'message': message,
                'progress': progress,
                'status': status
            })
    
    def is_process_running(self, process_names: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Check if any of the given process names is running.
        Returns: (is_running, actual_process_name)
        """
        if isinstance(process_names, str):
            process_names = [process_names]
        
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name']
                for target_name in process_names:
                    if target_name.lower() in proc_name.lower():
                        if self.verbose:
                            self.log(f"Found process: {proc_name}", "DEBUG")
                        return True, proc_name
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        return False, None
    
    def find_windows_by_title(self, titles: List[str], exact_match: bool = False) -> List[int]:
        """
        Find all windows matching any of the given titles.
        Returns: List of window handles (hwnd)
        """
        if isinstance(titles, str):
            titles = [titles]
        
        found_windows = []
        
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    for title in titles:
                        if exact_match:
                            if window_text.lower() == title.lower():
                                windows.append(hwnd)
                                if self.verbose:
                                    self.log(f"Found window (exact): '{window_text}'", "DEBUG")
                        else:
                            if title.lower() in window_text.lower():
                                windows.append(hwnd)
                                if self.verbose:
                                    self.log(f"Found window (partial): '{window_text}'", "DEBUG")
            return True
        
        win32gui.EnumWindows(callback, found_windows)
        return found_windows
    
    def close_window(self, hwnd: int) -> bool:
        """Close a window gracefully."""
        try:
            window_title = win32gui.GetWindowText(hwnd)
            self.log(f"Closing window: '{window_title}'", "INFO")
            
            # Try graceful close first (WM_CLOSE)
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            time.sleep(0.5)
            
            # Check if window still exists
            if win32gui.IsWindow(hwnd):
                # Force close if still open
                self.log(f"Force closing window: '{window_title}'", "WARNING")
                win32gui.DestroyWindow(hwnd)
            
            return True
        except Exception as e:
            self.log(f"Error closing window: {e}", "ERROR")
            return False
    
    def bring_window_to_front(self, hwnd: int, maximize: bool = True):
        """Bring a window to the foreground and optionally maximize it."""
        try:
            window_title = win32gui.GetWindowText(hwnd)
            self.log(f"Bringing window to front: '{window_title}'", "INFO")
            
            # Restore window if minimized
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)
            
            # Maximize the window for consistent UI element positions
            if maximize:
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                time.sleep(0.3)
                self.log("Window maximized", "INFO")
            
            # Try to set foreground (may fail due to Windows restrictions)
            try:
                win32gui.SetForegroundWindow(hwnd)
            except Exception as e:
                # Fallback: use Alt key trick to bypass Windows restrictions
                if self.verbose:
                    self.log(f"SetForegroundWindow failed, using fallback method", "DEBUG")
                
                # Simulate Alt key press to allow window switching
                import win32api
                import win32con as wcon
                
                # Get current foreground window
                current_hwnd = win32gui.GetForegroundWindow()
                
                # Attach to the thread that owns the foreground window
                current_thread = win32process.GetWindowThreadProcessId(current_hwnd)[0]
                target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
                
                if current_thread != target_thread:
                    win32process.AttachThreadInput(current_thread, target_thread, True)
                    win32gui.SetForegroundWindow(hwnd)
                    win32process.AttachThreadInput(current_thread, target_thread, False)
                else:
                    win32gui.SetForegroundWindow(hwnd)
            
            time.sleep(0.3)
            self.log(f"Window brought to front successfully", "SUCCESS")
            
        except Exception as e:
            self.log(f"Error bringing window to front: {e}", "WARNING")
            # Not critical - window is still accessible
    
    def wait_for_modal_and_click(self, modal_title: str, timeout: int = 15) -> bool:
        """
        Wait for a modal dialog and click OK (press Enter).
        Returns: True if modal was handled, False if timeout
        """
        self.log(f"Waiting for modal: '{modal_title}' (timeout: {timeout}s)", "INFO")
        start_time = time.time()
        check_interval = self.config['timing']['modal_check_interval']
        
        while (time.time() - start_time) < timeout:
            modal_hwnd = self.find_windows_by_title([modal_title])
            
            if modal_hwnd:
                self.log(f"Modal detected: '{modal_title}'", "SUCCESS")
                self.bring_window_to_front(modal_hwnd[0])
                time.sleep(0.3)
                
                # Press Enter to click OK
                pyautogui.press('enter')
                time.sleep(0.5)
                
                # Verify modal is closed
                if not self.find_windows_by_title([modal_title]):
                    self.log("Modal closed successfully", "SUCCESS")
                    return True
            
            time.sleep(check_interval)
        
        self.log(f"Modal timeout: '{modal_title}' not found", "WARNING")
        return False
    
    def start_loader_patcher(self) -> bool:
        """
        Start the loader/patcher process and handle its startup modal.
        Returns: True if successful
        """
        config = self.config['loader_patcher']
        
        self.log("Starting loader/patcher...", "INFO")
        
        try:
            # Try to start with admin privileges on Windows
            import ctypes
            
            # Check if we're already running as admin
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            except:
                is_admin = False
            
            if is_admin:
                # We have admin rights, start normally
                subprocess.Popen([config['exe_path']])
            else:
                # Try to start with elevated privileges using ShellExecute
                self.log("Requesting administrator privileges...", "WARNING")
                ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",  # Request elevation
                    config['exe_path'],
                    None,
                    None,
                    1  # SW_SHOWNORMAL
                )
            
            time.sleep(config['wait_after_start'])
            
            # Handle startup modal if configured
            if config['startup_modal']['enabled']:
                self.wait_for_modal_and_click(
                    config['startup_modal']['title'],
                    config['startup_modal']['timeout']
                )
            
            # Verify process is running
            is_running, _ = self.is_process_running([config['process_name']])
            if is_running:
                self.log("Loader/patcher started successfully", "SUCCESS")
                return True
            else:
                self.log("Loader/patcher process not detected after start", "ERROR")
                self.log("Please start the loader/patcher manually with admin rights", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Failed to start loader/patcher: {e}", "ERROR")
            self.log("Please start the loader/patcher manually with admin rights", "WARNING")
            return False
    
    def close_all_flexisign_windows(self) -> bool:
        """
        Close all FlexiSign Pro windows.
        Returns: True if all windows were closed
        """
        config = self.config['flexisign_pro']
        windows = self.find_windows_by_title(config['window_titles'])
        
        if not windows:
            self.log("No FlexiSign windows to close", "INFO")
            return True
        
        self.log(f"Closing {len(windows)} FlexiSign window(s)...", "INFO")
        
        for hwnd in windows:
            self.close_window(hwnd)
        
        # Wait for windows to close
        time.sleep(self.config['timing']['window_close_wait'])
        
        # Verify all windows are closed
        remaining = self.find_windows_by_title(config['window_titles'])
        if remaining:
            self.log(f"Warning: {len(remaining)} window(s) still open", "WARNING")
            return False
        
        self.log("All FlexiSign windows closed", "SUCCESS")
        return True
    
    def kill_flexisign_processes(self) -> bool:
        """
        Force kill all FlexiSign Pro processes.
        Use as last resort if windows won't close gracefully.
        """
        config = self.config['flexisign_pro']
        killed = False
        
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                proc_name = proc.info['name']
                for target_name in config['process_names']:
                    if target_name.lower() in proc_name.lower():
                        self.log(f"Force killing process: {proc_name} (PID: {proc.info['pid']})", "WARNING")
                        proc.kill()
                        killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if killed:
            time.sleep(2)
            self.log("FlexiSign processes terminated", "SUCCESS")
        
        return killed
    
    def start_flexisign_pro(self) -> bool:
        """
        Start FlexiSign Pro (only if loader/patcher is running).
        Returns: True if successful
        """
        config = self.config['flexisign_pro']
        
        self.log("Starting FlexiSign Pro...", "INFO")
        
        try:
            subprocess.Popen([config['exe_path']])
            time.sleep(config['wait_after_start'])
            
            # Verify window appeared
            windows = self.find_windows_by_title(config['window_titles'])
            if windows:
                self.log("FlexiSign Pro started successfully", "SUCCESS")
                return True
            else:
                self.log("FlexiSign Pro window not detected after start", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Failed to start FlexiSign Pro: {e}", "ERROR")
            return False
    
    def ensure_proper_state(self) -> bool:
        """
        Main method: Ensure FlexiSign Pro is running properly with loader/patcher.
        
        Logic:
        1. Check if loader/patcher is running
           - If not: start it and handle modal
        2. Check if FlexiSign Pro windows exist
           - If loader was not running: close all FlexiSign windows (they're in demo mode)
        3. Check if FlexiSign Pro is running properly
           - If not: start it
           - If yes: bring to front
        
        Returns: True if FlexiSign Pro is ready to use
        """
        self.log("=" * 60, "INFO")
        self.log("Starting FlexiSign Pro automation...", "INFO")
        self.log("=" * 60, "INFO")
        
        self.send_progress("Starting FlexiSign Pro workflow...", 0)
        
        # Step 1: Ensure loader/patcher is running
        self.send_progress("Checking loader/patcher status...", 10)
        loader_config = self.config['loader_patcher']
        loader_was_running, _ = self.is_process_running([loader_config['process_name']])
        
        if loader_was_running:
            self.log("Loader/patcher is already running ✓", "SUCCESS")
            self.send_progress("Loader/patcher confirmed active", 30)
        else:
            self.log("Loader/patcher is NOT running - starting it now", "WARNING")
            self.send_progress("Launching loader/patcher utility...", 15)
            if not self.start_loader_patcher():
                self.log("CRITICAL: Failed to start loader/patcher", "ERROR")
                
                # Check one more time if it's running (user might have started it manually)
                time.sleep(2)
                is_running_now, _ = self.is_process_running([loader_config['process_name']])
                
                if is_running_now:
                    self.log("Loader/patcher detected running now!", "SUCCESS")
                    self.send_progress("Loader/patcher confirmed active", 30)
                else:
                    error_msg = "Please start the loader/patcher manually (requires admin rights)"
                    self.send_progress(error_msg, 100, "error")
                    return False
            else:
                self.send_progress("Loader/patcher started successfully", 30)
        
        # Step 2: Check for existing FlexiSign windows
        self.send_progress("Checking for existing FlexiSign windows...", 40)
        flexisign_config = self.config['flexisign_pro']
        existing_windows = self.find_windows_by_title(flexisign_config['window_titles'])
        
        if existing_windows and not loader_was_running:
            # FlexiSign is open but loader wasn't running = DEMO MODE
            self.log("CRITICAL: FlexiSign is running in DEMO MODE (loader was not active)", "ERROR")
            self.log("Closing all FlexiSign windows to restart properly...", "WARNING")
            self.send_progress("Closing demo mode windows...", 45)
            
            if not self.close_all_flexisign_windows():
                self.log("Failed to close windows gracefully, force killing...", "WARNING")
                self.kill_flexisign_processes()
            
            # Wait a bit before restarting
            time.sleep(2)
            existing_windows = []
            self.send_progress("Demo mode windows closed", 50)
        
        # Step 3: Ensure FlexiSign Pro is running (now that loader is active)
        if not existing_windows:
            self.log("FlexiSign Pro is not running - starting it now", "INFO")
            self.send_progress("Starting FlexiSign Pro...", 60)
            if not self.start_flexisign_pro():
                self.log("Failed to start FlexiSign Pro", "ERROR")
                self.send_progress("Failed to start FlexiSign Pro", 100, "error")
                return False
            
            self.send_progress("Waiting for FlexiSign Pro window...", 80)
            # Get the new window
            existing_windows = self.find_windows_by_title(flexisign_config['window_titles'])
        
        # Step 4: Bring FlexiSign to front
        if existing_windows:
            # Show which window was found
            window_title = win32gui.GetWindowText(existing_windows[0])
            self.log(f"Found FlexiSign window: '{window_title}'", "INFO")
            
            self.send_progress("Bringing FlexiSign to front...", 90)
            self.bring_window_to_front(existing_windows[0])
            
            self.log("=" * 60, "INFO")
            self.log("FlexiSign Pro is ready! ✓", "SUCCESS")
            self.log("=" * 60, "INFO")
            
            self.send_progress("FlexiSign Pro is ready!", 100, "success")
            return True
        else:
            self.log("Failed to get FlexiSign Pro window", "ERROR")
            self.send_progress("Failed to find FlexiSign window", 100, "error")
            return False


# Standalone test function
def test_flexisign_manager():
    """Test the FlexiSign Manager."""
    manager = FlexiSignManager()
    success = manager.ensure_proper_state()
    
    if success:
        print("\n✅ FlexiSign Pro is ready to use!")
    else:
        print("\n❌ Failed to start FlexiSign Pro properly")
    
    return success


if __name__ == '__main__':
    test_flexisign_manager()
