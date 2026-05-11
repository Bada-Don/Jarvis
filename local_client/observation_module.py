"""
Observation Module for ReAct Loop.
Captures the state of the PC after each action: active window, file existence,
terminal output, and provides summarization for long outputs.
"""

import os
import subprocess
import time
from typing import Optional, Dict, List
from pathlib import Path

try:
    import win32gui
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


class ObservationModule:
    """
    Captures PC state observations after each step execution.
    Used by the ReAct loop to build the 'Observe' phase.
    """
    
    def __init__(self, status_callback=None):
        self.status_callback = status_callback or (lambda msg, status="info": print(f"[{status}] {msg}"))
    
    def capture_state(self, step_type: str = "") -> Dict:
        """
        Capture the current state of the PC.
        
        Args:
            step_type: Type of step that was just executed (determines what to capture)
            
        Returns:
            dict: Observation data including active window, screen info, etc.
        """
        observation = {
            'active_window': self.get_active_window_title(),
            'foreground_app': self.get_foreground_app(),
            'timestamp': time.time()
        }
        
        # For UI steps, note that a screenshot may be needed
        if step_type in ('visual_click', 'click_text_fast', 'click_text', 'keyboard'):
            observation['ui_changed'] = True
        
        return observation
    
    def check_file_exists(self, path: str) -> bool:
        """Check if a file exists at the given path."""
        try:
            expanded = os.path.expandvars(path)
            return os.path.exists(expanded)
        except Exception:
            return False
    
    def check_process_running(self, process_name: str) -> bool:
        """Check if a process is currently running."""
        try:
            result = subprocess.run(
                ['tasklist', '/FI', f'IMAGENAME eq {process_name}'],
                capture_output=True, text=True, timeout=5
            )
            return process_name.lower() in result.stdout.lower()
        except Exception:
            return False
    
    def get_active_window_title(self) -> str:
        """Get the title of the currently active window."""
        if not WIN32_AVAILABLE:
            return ""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                return win32gui.GetWindowText(hwnd)
        except Exception:
            pass
        return ""
    
    def get_foreground_app(self) -> str:
        """Get the name of the foreground application."""
        if not WIN32_AVAILABLE:
            return ""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                _, pid = win32gui.GetWindowThreadProcessId(hwnd)
                import psutil
                proc = psutil.Process(pid)
                return proc.name()
        except Exception:
            pass
        return ""
    
    def summarize_output(self, output: str, max_chars: int = 2000) -> str:
        """
        Summarize long tool outputs to save tokens.
        Keeps the beginning and end, truncates the middle.
        
        Args:
            output: Raw output string
            max_chars: Maximum characters to keep
            
        Returns:
            str: Summarized output
        """
        if not output or len(output) <= max_chars:
            return output
        
        # For directory listings, count items and show first/last
        lines = output.split('\n')
        if len(lines) > 20:
            head = '\n'.join(lines[:10])
            tail = '\n'.join(lines[-5:])
            return f"{head}\n... [{len(lines) - 15} more lines omitted] ...\n{tail}"
        
        # For other long output, truncate middle
        half = max_chars // 2
        return f"{output[:half]}\n... [truncated {len(output) - max_chars} chars] ...\n{output[-half:]}"
    
    def build_observation_text(self, step_result_dict: Dict) -> str:
        """
        Build a human-readable observation string from a step result.
        This is what gets sent to the Planner as the 'Observe' phase.
        
        Args:
            step_result_dict: StepResult as dictionary
            
        Returns:
            str: Formatted observation text
        """
        parts = []
        
        if step_result_dict.get('success'):
            parts.append("Step succeeded.")
        else:
            parts.append("Step FAILED.")
        
        # Add relevant output
        stdout = step_result_dict.get('stdout', '')
        stderr = step_result_dict.get('stderr', '')
        
        if stdout:
            parts.append(f"Output: {self.summarize_output(stdout)}")
        if stderr:
            parts.append(f"Error output: {self.summarize_output(stderr, max_chars=1000)}")
        
        error_msg = step_result_dict.get('error_message')
        if error_msg:
            parts.append(f"Error: {error_msg}")
        
        # Add window state
        active_window = step_result_dict.get('active_window', '')
        if active_window:
            parts.append(f"Active window: {active_window}")
        
        # Add file modifications
        files_modified = step_result_dict.get('files_modified', [])
        if files_modified:
            parts.append(f"Files modified: {', '.join(files_modified)}")
        
        return " | ".join(parts)