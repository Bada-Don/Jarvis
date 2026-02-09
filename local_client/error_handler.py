"""
Error Handler Module for JARVIS Desktop Application

This module provides centralized error handling with categorization,
user-friendly messages, logging, and recovery procedures.
"""

import logging
import traceback
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import json


class ErrorCategory(Enum):
    """Error categories for classification"""
    CONFIGURATION = "configuration"
    NETWORK = "network"
    COMPONENT = "component"
    PAIRING = "pairing"
    RUNTIME = "runtime"


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class JarvisError(Exception):
    """Base exception class for JARVIS errors"""
    def __init__(self, message: str, category: ErrorCategory, severity: ErrorSeverity = ErrorSeverity.ERROR, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.timestamp = datetime.now()


class ConfigurationError(JarvisError):
    """Configuration-related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.CONFIGURATION, ErrorSeverity.ERROR, details)


class NetworkError(JarvisError):
    """Network-related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.NETWORK, ErrorSeverity.WARNING, details)


class ComponentError(JarvisError):
    """Component crash or startup errors"""
    def __init__(self, message: str, component: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details['component'] = component
        super().__init__(message, ErrorCategory.COMPONENT, ErrorSeverity.CRITICAL, details)


class PairingError(JarvisError):
    """Device pairing errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.PAIRING, ErrorSeverity.ERROR, details)


class RuntimeError(JarvisError):
    """Runtime errors (permissions, resources, etc.)"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.RUNTIME, ErrorSeverity.ERROR, details)


class ErrorHandler:
    """
    Centralized error handler for JARVIS application.
    
    Provides:
    - Error categorization
    - User-friendly error messages
    - Error logging to file
    - Recovery procedures
    - Status callbacks for UI updates
    """
    
    def __init__(self, log_dir: Optional[Path] = None, status_callback: Optional[Callable] = None):
        """
        Initialize ErrorHandler
        
        Args:
            log_dir: Directory for error logs (default: data/logs)
            status_callback: Callback function for sending status updates to UI
        """
        self.log_dir = log_dir or Path("data/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.status_callback = status_callback
        self.error_log_path = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Setup logger
        self.logger = self._setup_logger()
        
        # Error statistics
        self.error_counts: Dict[ErrorCategory, int] = {cat: 0 for cat in ErrorCategory}
        
    def _setup_logger(self) -> logging.Logger:
        """Setup file logger for errors"""
        logger = logging.getLogger('jarvis_error_handler')
        logger.setLevel(logging.DEBUG)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # File handler
        file_handler = logging.FileHandler(self.error_log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(category)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        return logger
    
    def _log_error(self, error: JarvisError, exc_info: Optional[Exception] = None) -> None:
        """
        Log error to file with full details
        
        Args:
            error: JarvisError instance
            exc_info: Original exception for traceback
        """
        # Update statistics
        self.error_counts[error.category] += 1
        
        # Prepare log entry
        log_data = {
            'timestamp': error.timestamp.isoformat(),
            'category': error.category.value,
            'severity': error.severity.value,
            'message': error.message,
            'details': error.details
        }
        
        # Add traceback if available
        if exc_info:
            log_data['traceback'] = traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__)
        
        # Log to file
        log_message = f"{error.message} | Details: {json.dumps(error.details)}"
        
        extra = {'category': error.category.value}
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message, extra=extra)
        elif error.severity == ErrorSeverity.ERROR:
            self.logger.error(log_message, extra=extra)
        elif error.severity == ErrorSeverity.WARNING:
            self.logger.warning(log_message, extra=extra)
        else:
            self.logger.info(log_message, extra=extra)
        
        # Log full details as JSON
        self.logger.debug(f"Full error details: {json.dumps(log_data, indent=2)}", extra=extra)
    
    def _send_status(self, message: str, status_type: str = "error") -> None:
        """
        Send status update to UI via callback
        
        Args:
            message: Status message
            status_type: Type of status (error, warning, info)
        """
        if self.status_callback:
            try:
                self.status_callback({
                    'message': message,
                    'type': status_type,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Failed to send status update: {e}")
    
    def handle_configuration_error(self, error: ConfigurationError, recovery_callback: Optional[Callable] = None) -> None:
        """
        Handle configuration errors
        
        Args:
            error: ConfigurationError instance
            recovery_callback: Optional callback for recovery actions
        """
        self._log_error(error)
        
        # User-friendly messages
        user_messages = {
            'missing_api_key': "API key is missing. Please configure your API keys in Settings.",
            'invalid_api_key': "API key is invalid. Please check your API key and try again.",
            'invalid_path': "System path is invalid. Please verify the path exists.",
            'corrupted_config': "Configuration file is corrupted. Attempting to restore from backup...",
            'missing_firebase': "Firebase credentials are missing. Please configure Firebase settings."
        }
        
        # Determine specific error type from details
        error_type = error.details.get('type', 'unknown')
        user_message = user_messages.get(error_type, f"Configuration error: {error.message}")
        
        # Send to UI
        self._send_status(user_message, "error")
        
        # Attempt recovery
        if recovery_callback:
            try:
                recovery_callback(error)
            except Exception as e:
                self.logger.error(f"Recovery callback failed: {e}")
    
    def handle_network_error(self, error: NetworkError, retry_callback: Optional[Callable] = None) -> None:
        """
        Handle network errors with automatic retry
        
        Args:
            error: NetworkError instance
            retry_callback: Optional callback for retry logic
        """
        self._log_error(error)
        
        # User-friendly messages
        user_messages = {
            'firebase_connection': "Unable to connect to Firebase. Retrying...",
            'api_unreachable': "API endpoint is unreachable. Check your internet connection.",
            'timeout': "Request timed out. Please try again.",
            'rate_limit': "Rate limit exceeded. Please wait before trying again."
        }
        
        error_type = error.details.get('type', 'unknown')
        user_message = user_messages.get(error_type, f"Network error: {error.message}")
        
        # Send to UI
        self._send_status(user_message, "warning")
        
        # Queue operations for retry
        if retry_callback:
            try:
                retry_callback(error)
            except Exception as e:
                self.logger.error(f"Retry callback failed: {e}")
    
    def handle_component_crash(self, error: ComponentError, restart_callback: Optional[Callable] = None) -> bool:
        """
        Handle component crashes with automatic restart
        
        Args:
            error: ComponentError instance
            restart_callback: Optional callback for restart logic
            
        Returns:
            bool: True if recovery successful, False otherwise
        """
        self._log_error(error)
        
        component = error.details.get('component', 'Unknown')
        
        # User-friendly message
        user_message = f"{component} has stopped unexpectedly. Attempting to restart..."
        self._send_status(user_message, "error")
        
        # Attempt restart
        if restart_callback:
            try:
                success = restart_callback(error)
                if success:
                    self._send_status(f"{component} restarted successfully.", "info")
                    return True
                else:
                    self._send_status(f"Failed to restart {component}. Please restart manually.", "error")
                    return False
            except Exception as e:
                self.logger.error(f"Restart callback failed: {e}")
                self._send_status(f"Failed to restart {component}: {str(e)}", "error")
                return False
        
        return False
    
    def handle_pairing_error(self, error: PairingError, regenerate_callback: Optional[Callable] = None) -> None:
        """
        Handle device pairing errors
        
        Args:
            error: PairingError instance
            regenerate_callback: Optional callback for regenerating pairing token
        """
        self._log_error(error)
        
        # User-friendly messages
        user_messages = {
            'expired_token': "Pairing code has expired. Generating a new code...",
            'invalid_token': "Invalid pairing code. Please scan the QR code again.",
            'already_paired': "Device is already paired. Unpair first to pair with a new device.",
            'scan_failure': "Failed to scan QR code. Please try again or enter the code manually."
        }
        
        error_type = error.details.get('type', 'unknown')
        user_message = user_messages.get(error_type, f"Pairing error: {error.message}")
        
        # Send to UI
        self._send_status(user_message, "error")
        
        # Attempt recovery (e.g., regenerate token)
        if regenerate_callback and error_type == 'expired_token':
            try:
                regenerate_callback(error)
                self._send_status("New pairing code generated.", "info")
            except Exception as e:
                self.logger.error(f"Regenerate callback failed: {e}")
    
    def handle_runtime_error(self, error: RuntimeError) -> None:
        """
        Handle runtime errors
        
        Args:
            error: RuntimeError instance
        """
        self._log_error(error)
        
        # User-friendly messages
        user_messages = {
            'permission_denied': "Permission denied. Please run JARVIS with appropriate permissions.",
            'disk_space': "Insufficient disk space. Please free up space and try again.",
            'memory': "Insufficient memory. Please close other applications and try again.",
            'dependency_missing': "Required dependency is missing. Please reinstall JARVIS."
        }
        
        error_type = error.details.get('type', 'unknown')
        user_message = user_messages.get(error_type, f"Runtime error: {error.message}")
        
        # Send to UI
        self._send_status(user_message, "error")
    
    def handle_generic_error(self, exception: Exception, category: ErrorCategory = ErrorCategory.RUNTIME, context: Optional[str] = None) -> None:
        """
        Handle generic exceptions that aren't JarvisError instances
        
        Args:
            exception: Any exception
            category: Error category to assign
            context: Optional context description
        """
        # Create JarvisError from generic exception
        message = f"{context}: {str(exception)}" if context else str(exception)
        
        error = JarvisError(
            message=message,
            category=category,
            severity=ErrorSeverity.ERROR,
            details={
                'exception_type': type(exception).__name__,
                'context': context
            }
        )
        
        self._log_error(error, exception)
        self._send_status(f"Error: {message}", "error")
    
    def get_error_statistics(self) -> Dict[str, int]:
        """
        Get error statistics by category
        
        Returns:
            Dictionary of error counts by category
        """
        return {cat.value: count for cat, count in self.error_counts.items()}
    
    def clear_statistics(self) -> None:
        """Clear error statistics"""
        self.error_counts = {cat: 0 for cat in ErrorCategory}


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get or create global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def set_error_handler(handler: ErrorHandler) -> None:
    """Set global error handler instance"""
    global _error_handler
    _error_handler = handler
