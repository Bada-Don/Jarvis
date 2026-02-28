"""
Permission Service for Critical Operations
Handles requesting user permission for critical operations like file deletion.
"""

import uuid
import time
import threading
from typing import Optional, Callable

# Critical operations that require user permission
CRITICAL_OPERATIONS = {
    'delete_file': 'Delete File',
    'delete_folder': 'Delete Folder',
    'format_drive': 'Format Drive',
    'system_shutdown': 'System Shutdown',
    'system_restart': 'System Restart',
    'registry_edit': 'Registry Edit',
    'uninstall_app': 'Uninstall Application',
    'clear_data': 'Clear Data',
    'overwrite_file': 'Overwrite File',
    'ai_edit_text': 'AI File Edit (Text)',
    'ai_edit_excel': 'AI File Edit (Excel)',
    'ai_edit_word': 'AI File Edit (Word)',
}

# Keywords that indicate critical operations in step descriptions
CRITICAL_KEYWORDS = [
    'delete', 'remove', 'erase', 'clear', 'format', 'wipe',
    'shutdown', 'restart', 'reboot', 'uninstall', 'overwrite',
    'rmdir', 'rm -rf', 'del /f', 'rd /s',
]


class PermissionService:
    """
    Service for requesting user permission for critical operations.
    Uses WebSocket to communicate with the mobile app via the backend server.
    """
    
    # Timeout for waiting for permission response (seconds)
    PERMISSION_TIMEOUT = 60.0
    
    def __init__(self, socket_client, status_callback: Optional[Callable] = None):
        """
        Initialize PermissionService.
        
        Args:
            socket_client: SocketIO client instance
            status_callback: Optional callback for status updates
        """
        self.sio = socket_client
        self.status_callback = status_callback or (lambda msg, status="info": print(f"[{status}] {msg}"))
        
        # Pending permission requests
        self._pending_requests = {}
        self._response_events = {}
        
        # Register socket event handler
        self._register_handlers()
    
    def _register_handlers(self):
        """Register socket event handlers for permission responses."""
        @self.sio.on('permission_response_to_client')
        def handle_permission_response(data):
            request_id = data.get('requestId')
            approved = data.get('approved', False)
            
            print(f"🔐 Permission response received: {request_id} - {'APPROVED' if approved else 'DENIED'}")
            
            if request_id in self._pending_requests:
                self._pending_requests[request_id]['approved'] = approved
                self._pending_requests[request_id]['responded'] = True
                
                # Signal the waiting thread
                if request_id in self._response_events:
                    self._response_events[request_id].set()
    
    def is_critical_operation(self, step: dict) -> bool:
        """
        Check if a step represents a critical operation.
        
        Args:
            step: Step dictionary from execution plan
            
        Returns:
            bool: True if the step is a critical operation
        """
        step_type = step.get('type', '').lower()
        step_desc = step.get('desc', '').lower()
        step_value = step.get('value', '').lower()
        
        # Check step type
        if step_type in CRITICAL_OPERATIONS:
            return True
        
        # Check for critical keywords in description or value
        for keyword in CRITICAL_KEYWORDS:
            if keyword in step_desc or keyword in step_value:
                return True
        
        return False
    
    def get_operation_details(self, step: dict) -> tuple:
        """
        Extract operation name and details from a step.
        
        Args:
            step: Step dictionary
            
        Returns:
            tuple: (operation_name, details_string)
        """
        step_type = step.get('type', 'unknown')
        step_desc = step.get('desc', '')
        step_value = step.get('value', '')
        path = step.get('path', '')
        
        # Determine operation name
        operation = CRITICAL_OPERATIONS.get(step_type, 'Critical Operation')
        
        # Build details string
        details_parts = []
        if step_desc:
            details_parts.append(step_desc)
        if path:
            details_parts.append(f"Path: {path}")
        if step_value and step_value != step_desc:
            details_parts.append(f"Command: {step_value}")
        
        details = '\n'.join(details_parts) if details_parts else 'No additional details'
        
        return operation, details
    
    def request_permission(self, operation: str, details: str) -> bool:
        """
        Request permission from the user for a critical operation.
        Blocks until user responds or timeout occurs.
        
        Args:
            operation: Name of the operation (e.g., "Delete File")
            details: Details about the operation
            
        Returns:
            bool: True if approved, False if denied or timeout
        """
        request_id = str(uuid.uuid4())
        
        # Create event for waiting
        response_event = threading.Event()
        self._response_events[request_id] = response_event
        
        # Store pending request
        self._pending_requests[request_id] = {
            'operation': operation,
            'details': details,
            'timestamp': time.time(),
            'approved': False,
            'responded': False,
        }
        
        # Send permission request to server
        self._send_status(f"⚠️ Requesting permission for: {operation}", "warning")
        
        self.sio.emit('permission_request_from_client', {
            'requestId': request_id,
            'operation': operation,
            'details': details,
            'timestamp': time.time(),
        })
        
        # Wait for response with timeout
        self._send_status("Waiting for user approval...", "info")
        response_received = response_event.wait(timeout=self.PERMISSION_TIMEOUT)
        
        # Clean up
        del self._response_events[request_id]
        request_data = self._pending_requests.pop(request_id, {})
        
        if not response_received:
            self._send_status("Permission request timed out - operation denied", "warning")
            return False
        
        approved = request_data.get('approved', False)
        
        if approved:
            self._send_status(f"✓ Permission granted for: {operation}", "success")
        else:
            self._send_status(f"✗ Permission denied for: {operation}", "warning")
        
        return approved
    
    def request_permission_for_step(self, step: dict) -> bool:
        """
        Request permission for a step if it's a critical operation.
        
        Args:
            step: Step dictionary from execution plan
            
        Returns:
            bool: True if approved or not critical, False if denied
        """
        if not self.is_critical_operation(step):
            return True
        
        operation, details = self.get_operation_details(step)
        return self.request_permission(operation, details)
    
    def _send_status(self, message: str, status_type: str = "info"):
        """Send status update via callback."""
        self.status_callback(message, status_type)


# Global abort flag
_abort_requested = False
_abort_lock = threading.Lock()


def is_abort_requested() -> bool:
    """Check if abort has been requested."""
    with _abort_lock:
        return _abort_requested


def set_abort_requested(value: bool):
    """Set the abort flag."""
    global _abort_requested
    with _abort_lock:
        _abort_requested = value


def reset_abort():
    """Reset the abort flag."""
    set_abort_requested(False)


def register_abort_handler(socket_client):
    """
    Register the abort signal handler on the socket client.
    
    Args:
        socket_client: SocketIO client instance
    """
    @socket_client.on('abort_task_to_client')
    def handle_abort(data):
        print("🛑 Abort signal received from server")
        set_abort_requested(True)
