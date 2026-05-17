"""
StepResult - Structured result object returned after each step execution in the ReAct loop.
Contains stdout, stderr, visual confirmation, and PC state observations.
"""

import time
from typing import Optional, List


class StepResult:
    """
    Result of a single step execution.
    
    Attributes:
        session_id: ID of the session this step belongs to
        step_order: Order number of the step in the plan
        step_type: Type of step (keyboard, shell_command, visual_click, etc.)
        success: Whether the step completed successfully
        stdout: Captured standard output (for shell commands)
        stderr: Captured standard error (for shell commands)
        screenshot_b64: Base64-encoded screenshot after step execution (for UI steps)
        active_window: Title of the currently active window
        error_message: Human-readable error description if step failed
        files_modified: List of file paths created/modified by this step
        observation: Free-text observation of PC state after step execution
        timestamp: Unix timestamp of when the result was captured
    """
    
    def __init__(
        self,
        session_id: str = "",
        step_order: int = 0,
        step_type: str = "",
        success: bool = False,
        stdout: str = "",
        stderr: str = "",
        screenshot_b64: Optional[str] = None,
        active_window: str = "",
        error_message: Optional[str] = None,
        files_modified: Optional[List[str]] = None,
        observation: str = "",
        usage: Optional[dict] = None,
        timestamp: Optional[float] = None
    ):
        self.session_id = session_id
        self.step_order = step_order
        self.step_type = step_type
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.screenshot_b64 = screenshot_b64
        self.active_window = active_window
        self.error_message = error_message
        self.files_modified = files_modified or []
        self.observation = observation
        self.usage = usage
        self.timestamp = timestamp or time.time()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for WebSocket/JSON serialization."""
        return {
            'session_id': self.session_id,
            'step_order': self.step_order,
            'step_type': self.step_type,
            'success': self.success,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'screenshot_b64': self.screenshot_b64,
            'active_window': self.active_window,
            'error_message': self.error_message,
            'files_modified': self.files_modified,
            'observation': self.observation,
            'usage': self.usage,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StepResult':
        """Create from dictionary (e.g., from WebSocket event)."""
        return cls(
            session_id=data.get('session_id', ''),
            step_order=data.get('step_order', 0),
            step_type=data.get('step_type', ''),
            success=data.get('success', False),
            stdout=data.get('stdout', ''),
            stderr=data.get('stderr', ''),
            screenshot_b64=data.get('screenshot_b64'),
            active_window=data.get('active_window', ''),
            error_message=data.get('error_message'),
            files_modified=data.get('files_modified', []),
            observation=data.get('observation', ''),
            usage=data.get('usage'),
            timestamp=data.get('timestamp', time.time())
        )
    
    def get_error_context(self) -> str:
        """Get a formatted error context string for re-planning."""
        parts = [f"Step {self.step_order} ({self.step_type}) failed."]
        if self.error_message:
            parts.append(f"Error: {self.error_message}")
        if self.stderr:
            parts.append(f"stderr: {self.stderr[:500]}")
        if self.active_window:
            parts.append(f"Active window: {self.active_window}")
        return " | ".join(parts)