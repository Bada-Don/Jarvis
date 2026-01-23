"""
Readiness Detection System for JARVIS
Provides deterministic state detection for web browsers, desktop applications, and file system operations.
Eliminates timing-dependent automation by waiting for explicit readiness signals.
"""

import time
import os
import subprocess
import psutil
import win32gui
import win32con
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ReadinessState(Enum):
    """Possible readiness states for applications and operations."""
    READY = "ready"
    LOADING = "loading"
    NOT_FOUND = "not_found"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class ReadinessResult:
    """Result of a readiness check."""
    state: ReadinessState
    message: str
    elapsed_time: float
    metadata: Dict[str, Any] = None
    
    @property
    def is_ready(self) -> bool:
        return self.state == ReadinessState.READY


class BrowserReadinessDetector:
    """
    Detects when a web browser has finished loading a page.
    Uses multiple strategies to ensure page is fully interactive.
    """
    
    def __init__(self, status_callback: Optional[Callable] = None):
        self.status_callback = status_callback or (lambda msg, status="info": print(f"[Browser] {msg}"))
    
    def wait_for_page_load(
        self, 
        browser_name: str = "chrome",
        timeout: float = 30.0,
        min_stable_time: float = 1.0
    ) -> ReadinessResult:
        """
        Wait for browser page to finish loading.
        
        Strategy:
        1. Wait for window to exist and be visible
        2. Monitor window title changes (indicates navigation/loading)
        3. Wait for title to stabilize (no changes for min_stable_time)
        4. Additional settle time for JavaScript/rendering
        
        Args:
            browser_name: Name of browser (chrome, firefox, edge)
            timeout: Maximum time to wait
            min_stable_time: How long title must remain unchanged
        
        Returns:
            ReadinessResult indicating if page is ready
        """
        start_time = time.time()
        self.status_callback(f"Waiting for {browser_name} page to load...", "info")
        
        # Step 1: Find browser window
        hwnd = self._find_browser_window(browser_name, timeout=5.0)
        if not hwnd:
            return ReadinessResult(
                state=ReadinessState.NOT_FOUND,
                message=f"Browser window not found: {browser_name}",
                elapsed_time=time.time() - start_time
            )
        
        # Step 2: Wait for window to be visible and enabled
        if not self._wait_for_window_visible(hwnd, timeout=5.0):
            return ReadinessResult(
                state=ReadinessState.ERROR,
                message="Browser window not visible",
                elapsed_time=time.time() - start_time
            )
        
        # Step 3: Monitor title stability (indicates page finished loading)
        last_title = ""
        stable_since = None
        
        while (time.time() - start_time) < timeout:
            try:
                current_title = win32gui.GetWindowText(hwnd)
                
                # Check if title changed
                if current_title != last_title:
                    last_title = current_title
                    stable_since = time.time()
                    self.status_callback(f"Page loading: {current_title[:50]}...", "info")
                
                # Check if title has been stable long enough
                elif stable_since and (time.time() - stable_since) >= min_stable_time:
                    # Title stable - page likely loaded
                    # Determine settle time based on page type
                    settle_time = self._get_settle_time(current_title)
                    
                    self.status_callback(f"Page ready: {current_title[:50]}", "success")
                    self.status_callback(f"Waiting {settle_time}s for page to fully render...", "info")
                    time.sleep(settle_time)
                    
                    elapsed = time.time() - start_time
                    self.status_callback(f"✓ Page ready ({elapsed:.1f}s)", "success")
                    
                    return ReadinessResult(
                        state=ReadinessState.READY,
                        message=f"Page loaded successfully",
                        elapsed_time=elapsed,
                        metadata={"title": current_title, "hwnd": hwnd}
                    )
                
                time.sleep(0.2)
                
            except Exception as e:
                return ReadinessResult(
                    state=ReadinessState.ERROR,
                    message=f"Error monitoring browser: {e}",
                    elapsed_time=time.time() - start_time
                )
        
        # Timeout
        return ReadinessResult(
            state=ReadinessState.TIMEOUT,
            message=f"Page load timeout after {timeout}s",
            elapsed_time=time.time() - start_time
        )
    
    def _find_browser_window(self, browser_name: str, timeout: float = 5.0) -> Optional[int]:
        """Find browser window handle."""
        browser_patterns = {
            'chrome': ['Google Chrome', 'Chrome'],
            'firefox': ['Mozilla Firefox', 'Firefox'],
            'edge': ['Microsoft Edge', 'Edge']
        }
        
        patterns = browser_patterns.get(browser_name.lower(), [browser_name])
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            results = []
            
            # Define callback outside to avoid recreation issues
            def enum_callback(hwnd, results_list):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title:  # Only check non-empty titles
                            for pattern in patterns:
                                if pattern.lower() in title.lower():
                                    results_list.append(hwnd)
                                    return False  # Stop enumeration
                except:
                    pass  # Ignore errors for individual windows
                return True  # Continue enumeration
            
            try:
                win32gui.EnumWindows(enum_callback, results)
            except Exception as e:
                # If EnumWindows fails, wait and retry
                print(f"[BrowserDetector] EnumWindows error: {e}, retrying...")
                time.sleep(0.3)
                continue
            
            if results:
                return results[0]
            
            time.sleep(0.2)
        
        return None
    
    def _get_settle_time(self, page_title: str) -> float:
        """
        Determine appropriate settle time based on page type.
        Heavy JavaScript applications need more time to render after title stabilizes.
        
        Args:
            page_title: Current page title
            
        Returns:
            Settle time in seconds
        """
        title_lower = page_title.lower()
        
        # Heavy web applications that need extra rendering time
        heavy_apps = {
            'gmail': 3.0,
            'google docs': 3.0,
            'google sheets': 3.0,
            'google slides': 3.0,
            'google drive': 2.5,
            'outlook': 3.0,
            'office 365': 3.0,
            'teams': 3.0,
            'slack': 2.5,
            'notion': 2.5,
            'figma': 3.0,
            'miro': 2.5,
        }
        
        # Check if page matches any heavy app
        for app_name, settle_time in heavy_apps.items():
            if app_name in title_lower:
                return settle_time
        
        # Default settle time for regular pages
        return 1.0
    
    def _wait_for_window_visible(self, hwnd: int, timeout: float = 5.0) -> bool:
        """Wait for window to be visible and enabled."""
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            try:
                if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                    return True
            except:
                pass
            time.sleep(0.1)
        
        return False


class DesktopAppReadinessDetector:
    """
    Detects when a desktop application is fully loaded and ready for interaction.
    Uses UI Automation and process monitoring for deterministic detection.
    """
    
    def __init__(self, status_callback: Optional[Callable] = None):
        self.status_callback = status_callback or (lambda msg, status="info": print(f"[DesktopApp] {msg}"))
        
        # Try to import uiautomation
        try:
            import uiautomation as auto
            self.uia = auto
            self.uia_available = True
        except ImportError:
            self.uia = None
            self.uia_available = False
            print("⚠️ Warning: uiautomation not available. Install with: pip install uiautomation")
    
    def wait_for_app_ready(
        self,
        window_title_pattern: str,
        timeout: float = 30.0,
        check_cpu_stable: bool = True,
        min_control_count: int = 5
    ) -> ReadinessResult:
        """
        Wait for desktop application to be fully loaded and ready.
        
        Strategy:
        1. Find window by title pattern
        2. Verify window is visible and enabled
        3. Check UI Automation tree is accessible
        4. Verify minimum number of controls exist (proves UI is populated)
        5. Optionally wait for CPU usage to stabilize
        6. Additional settle time for rendering
        
        Args:
            window_title_pattern: Window title or pattern to match
            timeout: Maximum time to wait
            check_cpu_stable: Whether to wait for CPU to stabilize
            min_control_count: Minimum number of UI controls expected
        
        Returns:
            ReadinessResult indicating if app is ready
        """
        start_time = time.time()
        self.status_callback(f"Waiting for application: {window_title_pattern}", "info")
        
        # Step 1: Find window
        hwnd = self._find_window(window_title_pattern, timeout=10.0)
        if not hwnd:
            return ReadinessResult(
                state=ReadinessState.NOT_FOUND,
                message=f"Window not found: {window_title_pattern}",
                elapsed_time=time.time() - start_time
            )
        
        window_title = win32gui.GetWindowText(hwnd)
        self.status_callback(f"Found window: {window_title}", "info")
        
        # Step 2: Wait for window to be visible and enabled
        if not self._wait_for_window_state(hwnd, timeout=5.0):
            return ReadinessResult(
                state=ReadinessState.ERROR,
                message="Window not in ready state (visible/enabled)",
                elapsed_time=time.time() - start_time
            )
        
        # Step 3: Check UI Automation tree (if available)
        if self.uia_available:
            control_count = self._wait_for_ui_controls(hwnd, min_control_count, timeout=10.0)
            if control_count < min_control_count:
                return ReadinessResult(
                    state=ReadinessState.ERROR,
                    message=f"UI not fully loaded (found {control_count} controls, expected {min_control_count})",
                    elapsed_time=time.time() - start_time
                )
            self.status_callback(f"UI loaded: {control_count} controls detected", "info")
        
        # Step 4: Wait for CPU to stabilize (optional)
        if check_cpu_stable:
            if not self._wait_for_cpu_stable(hwnd, timeout=10.0):
                self.status_callback("CPU still high, but continuing...", "warning")
        
        # Step 5: Final settle time
        time.sleep(0.5)
        
        elapsed = time.time() - start_time
        self.status_callback(f"Application ready: {window_title}", "success")
        
        return ReadinessResult(
            state=ReadinessState.READY,
            message="Application fully loaded and ready",
            elapsed_time=elapsed,
            metadata={"title": window_title, "hwnd": hwnd}
        )
    
    def _find_window(self, title_pattern: str, timeout: float = 10.0) -> Optional[int]:
        """Find window by title pattern."""
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            results = []
            
            # Define callback outside to avoid recreation issues
            def enum_callback(hwnd, results_list):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title and title_pattern.lower() in title.lower():
                            results_list.append(hwnd)
                            return False  # Stop enumeration
                except:
                    pass  # Ignore errors for individual windows
                return True  # Continue enumeration
            
            try:
                win32gui.EnumWindows(enum_callback, results)
            except Exception as e:
                # If EnumWindows fails, wait and retry
                print(f"[DesktopAppDetector] EnumWindows error: {e}, retrying...")
                time.sleep(0.3)
                continue
            
            if results:
                return results[0]
            
            time.sleep(0.3)
        
        return None
    
    def _wait_for_window_state(self, hwnd: int, timeout: float = 5.0) -> bool:
        """Wait for window to be visible, enabled, and not minimized."""
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    time.sleep(0.1)
                    continue
                
                if not win32gui.IsWindowEnabled(hwnd):
                    time.sleep(0.1)
                    continue
                
                # Check not minimized
                placement = win32gui.GetWindowPlacement(hwnd)
                if placement[1] == win32con.SW_SHOWMINIMIZED:
                    time.sleep(0.1)
                    continue
                
                return True
                
            except:
                pass
            
            time.sleep(0.1)
        
        return False
    
    def _wait_for_ui_controls(self, hwnd: int, min_count: int, timeout: float = 10.0) -> int:
        """Wait for UI Automation tree to be populated with controls."""
        if not self.uia_available:
            return min_count  # Assume ready if UIA not available
        
        start_time = time.time()
        max_count = 0
        
        while (time.time() - start_time) < timeout:
            try:
                # Get window control
                window_control = self.uia.ControlFromHandle(hwnd)
                if not window_control:
                    time.sleep(0.2)
                    continue
                
                # Count descendant controls
                controls = window_control.GetChildren()
                count = len(controls)
                max_count = max(max_count, count)
                
                if count >= min_count:
                    return count
                
                time.sleep(0.3)
                
            except Exception as e:
                time.sleep(0.2)
        
        return max_count
    
    def _wait_for_cpu_stable(self, hwnd: int, timeout: float = 10.0, threshold: float = 10.0) -> bool:
        """Wait for process CPU usage to drop below threshold."""
        try:
            # Get process ID from window
            import win32process
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            
            start_time = time.time()
            stable_since = None
            
            while (time.time() - start_time) < timeout:
                cpu_percent = process.cpu_percent(interval=0.2)
                
                if cpu_percent < threshold:
                    if stable_since is None:
                        stable_since = time.time()
                    elif (time.time() - stable_since) >= 1.0:
                        # CPU stable for 1 second
                        return True
                else:
                    stable_since = None
                
                time.sleep(0.2)
            
            return False
            
        except Exception as e:
            # If we can't check CPU, assume it's fine
            return True


class FileSystemReadinessDetector:
    """
    Verifies file system operations have completed successfully.
    Provides retry logic with exponential backoff.
    """
    
    def __init__(self, status_callback: Optional[Callable] = None):
        self.status_callback = status_callback or (lambda msg, status="info": print(f"[FileSystem] {msg}"))
    
    def wait_for_path_exists(
        self,
        path: str,
        timeout: float = 5.0,
        poll_interval: float = 0.2
    ) -> ReadinessResult:
        """
        Wait for a file or folder to exist.
        
        Args:
            path: Path to check
            timeout: Maximum time to wait
            poll_interval: How often to check
        
        Returns:
            ReadinessResult indicating if path exists
        """
        start_time = time.time()
        normalized_path = os.path.normpath(path)
        
        self.status_callback(f"Waiting for path: {os.path.basename(normalized_path)}", "info")
        
        while (time.time() - start_time) < timeout:
            if os.path.exists(normalized_path):
                elapsed = time.time() - start_time
                self.status_callback(f"Path exists: {os.path.basename(normalized_path)}", "success")
                
                return ReadinessResult(
                    state=ReadinessState.READY,
                    message="Path exists",
                    elapsed_time=elapsed,
                    metadata={"path": normalized_path, "is_dir": os.path.isdir(normalized_path)}
                )
            
            time.sleep(poll_interval)
        
        return ReadinessResult(
            state=ReadinessState.TIMEOUT,
            message=f"Path not found after {timeout}s",
            elapsed_time=time.time() - start_time
        )
    
    def wait_for_folder_accessible(
        self,
        folder_path: str,
        timeout: float = 5.0
    ) -> ReadinessResult:
        """
        Wait for folder to exist and be accessible (can list contents).
        
        Args:
            folder_path: Folder path to check
            timeout: Maximum time to wait
        
        Returns:
            ReadinessResult indicating if folder is accessible
        """
        # First wait for existence
        exists_result = self.wait_for_path_exists(folder_path, timeout)
        if not exists_result.is_ready:
            return exists_result
        
        # Verify it's a directory
        if not os.path.isdir(folder_path):
            return ReadinessResult(
                state=ReadinessState.ERROR,
                message="Path exists but is not a directory",
                elapsed_time=exists_result.elapsed_time
            )
        
        # Try to list contents
        try:
            os.listdir(folder_path)
            return ReadinessResult(
                state=ReadinessState.READY,
                message="Folder accessible",
                elapsed_time=exists_result.elapsed_time,
                metadata={"path": folder_path}
            )
        except Exception as e:
            return ReadinessResult(
                state=ReadinessState.ERROR,
                message=f"Folder not accessible: {e}",
                elapsed_time=exists_result.elapsed_time
            )


# Singleton instances
_browser_detector: Optional[BrowserReadinessDetector] = None
_desktop_detector: Optional[DesktopAppReadinessDetector] = None
_filesystem_detector: Optional[FileSystemReadinessDetector] = None


def get_browser_detector(status_callback: Optional[Callable] = None) -> BrowserReadinessDetector:
    """Get or create singleton BrowserReadinessDetector."""
    global _browser_detector
    if _browser_detector is None:
        _browser_detector = BrowserReadinessDetector(status_callback)
    return _browser_detector


def get_desktop_detector(status_callback: Optional[Callable] = None) -> DesktopAppReadinessDetector:
    """Get or create singleton DesktopAppReadinessDetector."""
    global _desktop_detector
    if _desktop_detector is None:
        _desktop_detector = DesktopAppReadinessDetector(status_callback)
    return _desktop_detector


def get_filesystem_detector(status_callback: Optional[Callable] = None) -> FileSystemReadinessDetector:
    """Get or create singleton FileSystemReadinessDetector."""
    global _filesystem_detector
    if _filesystem_detector is None:
        _filesystem_detector = FileSystemReadinessDetector(status_callback)
    return _filesystem_detector
