"""
Direct Path Executor Module for Direct Path Automation

This module executes file operations (save, open) using direct path typing
instead of UI navigation. It leverages the fact that Windows file dialogs
accept full absolute paths in the filename field.

Requirements: 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 5.1
"""

import time
from dataclasses import dataclass
from typing import Optional, Callable

import pyautogui

# Configure pyautogui
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

try:
    from path_config import PathConfig
    PATH_CONFIG_AVAILABLE = True
except ImportError:
    PATH_CONFIG_AVAILABLE = False

try:
    from ocr_service import OCRService
    OCR_SERVICE_AVAILABLE = True
except ImportError:
    OCR_SERVICE_AVAILABLE = False

try:
    import numpy as np
    from PIL import ImageGrab
    import cv2
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False


@dataclass
class ExecutionResult:
    """
    Result of a direct path operation.
    
    Attributes:
        success: Whether the operation completed successfully
        operation: Type of operation ("save", "open", "navigate", "click_text")
        path: The path that was used in the operation
        error_type: Type of error if failed (e.g., "file_exists", "path_not_found")
        error_message: Human-readable error description
        dialog_detected: Text from any error/confirmation dialog
    
    Requirements: 5.2, 5.3
    """
    success: bool
    operation: str
    path: Optional[str]
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    dialog_detected: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'operation': self.operation,
            'path': self.path,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'dialog_detected': self.dialog_detected
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ExecutionResult':
        """Create from dictionary."""
        return cls(
            success=data['success'],
            operation=data['operation'],
            path=data.get('path'),
            error_type=data.get('error_type'),
            error_message=data.get('error_message'),
            dialog_detected=data.get('dialog_detected')
        )


def create_success_result(operation: str, path: str) -> ExecutionResult:
    """Create a successful ExecutionResult."""
    return ExecutionResult(
        success=True,
        operation=operation,
        path=path
    )


def create_error_result(
    operation: str,
    path: str,
    error_type: str,
    error_message: str,
    dialog_detected: Optional[str] = None
) -> ExecutionResult:
    """
    Create an error ExecutionResult with proper error reporting.
    
    Requirements: 5.2, 5.3
    """
    return ExecutionResult(
        success=False,
        operation=operation,
        path=path,
        error_type=error_type,
        error_message=error_message,
        dialog_detected=dialog_detected
    )


class DirectPathExecutor:
    """
    Executes file save/open operations via direct path typing.
    
    This class provides methods to perform file operations by typing
    full absolute paths directly into Windows file dialogs, bypassing
    the need for complex UI navigation.
    
    Requirements: 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 5.1
    """
    
    # Timing configuration (seconds)
    DELAY_AFTER_HOTKEY = 0.5        # Delay after Ctrl+S, Ctrl+O, Ctrl+L
    DELAY_AFTER_TYPING = 0.2        # Delay after typing path
    DELAY_AFTER_ENTER = 0.5         # Delay after pressing Enter
    DELAY_DIALOG_CHECK = 0.3        # Delay between dialog checks
    DEFAULT_DIALOG_TIMEOUT = 2.0    # Default timeout for dialog detection
    
    # Dialog detection keywords
    OVERWRITE_KEYWORDS = [
        'already exists', 'replace', 'overwrite', 'confirm save as',
        'do you want to replace', 'file exists'
    ]
    
    ERROR_KEYWORDS = [
        'cannot find', 'not found', 'does not exist', 'path does not exist',
        'access denied', 'permission denied', 'invalid path', 'error'
    ]
    
    def __init__(
        self, 
        config: Optional['PathConfig'] = None,
        status_callback: Optional[Callable] = None
    ):
        """
        Initialize DirectPathExecutor.
        
        Args:
            config: PathConfig instance for default paths and policies.
                   If None, loads default configuration.
            status_callback: Optional callback for progress updates.
        """
        if PATH_CONFIG_AVAILABLE:
            self.config = config if config else PathConfig.load()
        else:
            self.config = None
            
        self.status_callback = status_callback or (lambda msg, status="info": print(f"[{status}] {msg}"))
        
        # OCR service for dialog detection
        self._ocr_service: Optional['OCRService'] = None
        if OCR_SERVICE_AVAILABLE:
            try:
                self._ocr_service = OCRService()
            except Exception:
                pass
    
    def _send_status(self, message: str, status_type: str = "info"):
        """Send status update via callback."""
        self.status_callback(message, status_type)
    
    def _capture_screenshot(self) -> Optional['np.ndarray']:
        """Capture a screenshot for dialog detection."""
        if not SCREENSHOT_AVAILABLE:
            return None
        
        try:
            screenshot = ImageGrab.grab()
            screenshot_np = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            return screenshot_bgr
        except Exception:
            return None
    
    def _detect_dialog_text(self) -> Optional[str]:
        """
        Detect text in any visible dialog using OCR.
        
        Returns:
            Detected dialog text, or None if no dialog detected
        """
        if not self._ocr_service:
            return None
        
        screenshot = self._capture_screenshot()
        if screenshot is None:
            return None
        
        try:
            all_text = self._ocr_service.get_all_detected_text(screenshot)
            return ' '.join(all_text).lower()
        except Exception:
            return None
    
    def _wait_for_dialog(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for a file dialog to appear.
        
        Uses a simple heuristic: wait for the specified timeout and assume
        the dialog has appeared. More sophisticated detection could use
        window enumeration or OCR.
        
        Args:
            timeout: Maximum time to wait in seconds. Uses config default if None.
        
        Returns:
            True if dialog is assumed to be ready, False on timeout
        
        Requirements: 1.1, 2.1
        """
        wait_time = timeout
        if wait_time is None:
            wait_time = self.config.dialog_wait_timeout if self.config else self.DEFAULT_DIALOG_TIMEOUT
        
        # Simple wait - in production, could use window detection
        time.sleep(wait_time)
        return True
    
    def _check_for_overwrite_dialog(self) -> bool:
        """
        Check if an overwrite confirmation dialog is visible.
        
        Returns:
            True if overwrite dialog detected
        """
        dialog_text = self._detect_dialog_text()
        if not dialog_text:
            return False
        
        return any(keyword in dialog_text for keyword in self.OVERWRITE_KEYWORDS)
    
    def _check_for_error_dialog(self) -> Optional[str]:
        """
        Check if an error dialog is visible.
        
        Returns:
            Error message if error dialog detected, None otherwise
        """
        dialog_text = self._detect_dialog_text()
        if not dialog_text:
            return None
        
        for keyword in self.ERROR_KEYWORDS:
            if keyword in dialog_text:
                return dialog_text
        
        return None

    
    def _handle_overwrite_dialog(self) -> bool:
        """
        Handle file overwrite confirmation dialog based on configured policy.
        
        Returns:
            True if handled successfully (either confirmed or cancelled as per policy)
        
        Requirements: 5.1
        """
        if not self.config:
            # No config, default to prompt (do nothing, let user decide)
            self._send_status("Overwrite dialog detected, awaiting user input", "warning")
            return False
        
        policy = self.config.overwrite_policy
        
        if policy == "overwrite":
            # Click Yes/Replace - typically Tab to select Yes, then Enter
            # Or just press 'y' for Yes in many dialogs
            self._send_status("Overwrite policy: replacing existing file", "info")
            pyautogui.press('tab')
            time.sleep(0.1)
            pyautogui.press('enter')
            time.sleep(self.DELAY_AFTER_ENTER)
            return True
        
        elif policy == "abort":
            # Click No/Cancel - press Escape or 'n'
            self._send_status("Overwrite policy: aborting save operation", "info")
            pyautogui.press('escape')
            time.sleep(self.DELAY_AFTER_ENTER)
            return True
        
        elif policy == "rename":
            # This would require modifying the filename - complex to implement
            # For now, treat as abort and report
            self._send_status("Overwrite policy: rename not yet implemented, aborting", "warning")
            pyautogui.press('escape')
            time.sleep(self.DELAY_AFTER_ENTER)
            return False
        
        else:  # "prompt" or unknown
            # Do nothing, let user handle it
            self._send_status("Overwrite dialog detected, awaiting user input", "warning")
            return False
    
    def execute_save(self, full_path: str) -> ExecutionResult:
        """
        Execute a save operation using direct path typing.
        
        Sequence:
        1. Press Ctrl+S to open Save dialog
        2. Wait for dialog to appear
        3. Type the full absolute path
        4. Press Enter to confirm
        5. Handle any error/confirmation dialogs
        
        Args:
            full_path: Full absolute path including filename and extension
                      (e.g., "C:\\Users\\harsh\\OneDrive\\Desktop\\document.txt")
        
        Returns:
            ExecutionResult with success status and any error details
        
        Requirements: 1.1, 1.2, 5.1
        """
        if not full_path:
            return create_error_result(
                operation="save",
                path=full_path,
                error_type="invalid_path",
                error_message="Path cannot be empty"
            )
        
        self._send_status(f"Executing save to: {full_path}", "info")
        
        try:
            # Step 1: Press Ctrl+S to open Save dialog
            self._send_status("Opening Save dialog (Ctrl+S)...", "info")
            pyautogui.hotkey('ctrl', 's')
            time.sleep(self.DELAY_AFTER_HOTKEY)
            
            # Step 2: Wait for dialog
            if not self._wait_for_dialog():
                return create_error_result(
                    operation="save",
                    path=full_path,
                    error_type="dialog_timeout",
                    error_message="Save dialog did not appear within timeout"
                )
            
            # Step 3: Type the full path
            self._send_status(f"Typing path: {full_path}", "info")
            # Clear any existing text first
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            
            # Type the path character by character for reliability
            pyautogui.typewrite(full_path, interval=0.02)
            time.sleep(self.DELAY_AFTER_TYPING)
            
            # Step 4: Press Enter to confirm
            self._send_status("Confirming save (Enter)...", "info")
            pyautogui.press('enter')
            time.sleep(self.DELAY_AFTER_ENTER)
            
            # Step 5: Check for dialogs
            # Check for overwrite dialog
            if self._check_for_overwrite_dialog():
                self._send_status("Overwrite dialog detected", "info")
                if not self._handle_overwrite_dialog():
                    return create_error_result(
                        operation="save",
                        path=full_path,
                        error_type="file_exists",
                        error_message="File already exists and overwrite was not confirmed",
                        dialog_detected="overwrite confirmation"
                    )
            
            # Check for error dialog
            error_text = self._check_for_error_dialog()
            if error_text:
                # Determine error type from text
                error_type = "unknown_error"
                if "not found" in error_text or "does not exist" in error_text:
                    error_type = "path_not_found"
                elif "access denied" in error_text or "permission" in error_text:
                    error_type = "permission_denied"
                elif "invalid" in error_text:
                    error_type = "invalid_path"
                
                return create_error_result(
                    operation="save",
                    path=full_path,
                    error_type=error_type,
                    error_message=f"Save operation failed: {error_text}",
                    dialog_detected=error_text
                )
            
            self._send_status(f"Save completed: {full_path}", "success")
            return create_success_result(operation="save", path=full_path)
            
        except Exception as e:
            return create_error_result(
                operation="save",
                path=full_path,
                error_type="execution_error",
                error_message=f"Error during save execution: {str(e)}"
            )

    
    def execute_open(self, full_path: str) -> ExecutionResult:
        """
        Execute an open operation using direct path typing.
        
        Sequence:
        1. Press Ctrl+O to open Open dialog
        2. Wait for dialog to appear
        3. Type the full absolute path
        4. Press Enter to confirm
        5. Handle any error dialogs
        
        Args:
            full_path: Full absolute path to the file to open
                      (e.g., "C:\\Users\\harsh\\Documents\\report.pdf")
        
        Returns:
            ExecutionResult with success status and any error details
        
        Requirements: 2.1, 2.2
        """
        if not full_path:
            return create_error_result(
                operation="open",
                path=full_path,
                error_type="invalid_path",
                error_message="Path cannot be empty"
            )
        
        self._send_status(f"Executing open: {full_path}", "info")
        
        try:
            # Step 1: Press Ctrl+O to open Open dialog
            self._send_status("Opening Open dialog (Ctrl+O)...", "info")
            pyautogui.hotkey('ctrl', 'o')
            time.sleep(self.DELAY_AFTER_HOTKEY)
            
            # Step 2: Wait for dialog
            if not self._wait_for_dialog():
                return create_error_result(
                    operation="open",
                    path=full_path,
                    error_type="dialog_timeout",
                    error_message="Open dialog did not appear within timeout"
                )
            
            # Step 3: Type the full path
            self._send_status(f"Typing path: {full_path}", "info")
            # Clear any existing text first
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            
            # Type the path
            pyautogui.typewrite(full_path, interval=0.02)
            time.sleep(self.DELAY_AFTER_TYPING)
            
            # Step 4: Press Enter to confirm
            self._send_status("Confirming open (Enter)...", "info")
            pyautogui.press('enter')
            time.sleep(self.DELAY_AFTER_ENTER)
            
            # Step 5: Check for error dialog
            error_text = self._check_for_error_dialog()
            if error_text:
                error_type = "unknown_error"
                if "not found" in error_text or "does not exist" in error_text:
                    error_type = "file_not_found"
                elif "access denied" in error_text or "permission" in error_text:
                    error_type = "permission_denied"
                elif "invalid" in error_text:
                    error_type = "invalid_path"
                
                return create_error_result(
                    operation="open",
                    path=full_path,
                    error_type=error_type,
                    error_message=f"Open operation failed: {error_text}",
                    dialog_detected=error_text
                )
            
            self._send_status(f"Open completed: {full_path}", "success")
            return create_success_result(operation="open", path=full_path)
            
        except Exception as e:
            return create_error_result(
                operation="open",
                path=full_path,
                error_type="execution_error",
                error_message=f"Error during open execution: {str(e)}"
            )
    
    def navigate_explorer(self, directory_path: str) -> ExecutionResult:
        """
        Navigate File Explorer to a directory using the address bar.
        
        Sequence:
        1. Press Ctrl+L to focus the address bar
        2. Type the directory path
        3. Press Enter to navigate
        
        Args:
            directory_path: Full path to the directory to navigate to
                           (e.g., "C:\\Users\\harsh\\Downloads")
        
        Returns:
            ExecutionResult with success status and any error details
        
        Requirements: 3.1, 3.2
        """
        if not directory_path:
            return create_error_result(
                operation="navigate",
                path=directory_path,
                error_type="invalid_path",
                error_message="Directory path cannot be empty"
            )
        
        self._send_status(f"Navigating to: {directory_path}", "info")
        
        try:
            # Step 1: Press Ctrl+L to focus address bar
            self._send_status("Focusing address bar (Ctrl+L)...", "info")
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(self.DELAY_AFTER_HOTKEY)
            
            # Step 2: Type the directory path
            self._send_status(f"Typing path: {directory_path}", "info")
            # The address bar should already be selected, but clear just in case
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            
            # Type the path
            pyautogui.typewrite(directory_path, interval=0.02)
            time.sleep(self.DELAY_AFTER_TYPING)
            
            # Step 3: Press Enter to navigate
            self._send_status("Navigating (Enter)...", "info")
            pyautogui.press('enter')
            time.sleep(self.DELAY_AFTER_ENTER)
            
            # Check for error dialog (e.g., path doesn't exist)
            error_text = self._check_for_error_dialog()
            if error_text:
                error_type = "path_not_found"
                if "access denied" in error_text or "permission" in error_text:
                    error_type = "permission_denied"
                
                return create_error_result(
                    operation="navigate",
                    path=directory_path,
                    error_type=error_type,
                    error_message=f"Navigation failed: {error_text}",
                    dialog_detected=error_text
                )
            
            self._send_status(f"Navigation completed: {directory_path}", "success")
            return create_success_result(operation="navigate", path=directory_path)
            
        except Exception as e:
            return create_error_result(
                operation="navigate",
                path=directory_path,
                error_type="execution_error",
                error_message=f"Error during navigation: {str(e)}"
            )
    
    def get_dialog_timeout(self) -> float:
        """Get the configured dialog wait timeout."""
        if self.config:
            return self.config.dialog_wait_timeout
        return self.DEFAULT_DIALOG_TIMEOUT
    
    def get_overwrite_policy(self) -> str:
        """Get the configured overwrite policy."""
        if self.config:
            return self.config.overwrite_policy
        return "prompt"
