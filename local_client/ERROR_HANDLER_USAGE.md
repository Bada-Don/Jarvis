# Error Handler Usage Guide

This document explains how to use the JARVIS Error Handler system for consistent error handling across all components.

## Overview

The Error Handler provides:
- **Error categorization** (Configuration, Network, Component, Pairing, Runtime)
- **User-friendly error messages** displayed in the UI
- **Automatic error logging** to files
- **Recovery procedures** with callbacks
- **Status updates** sent to the UI

## Quick Start

### 1. Import the Error Handler

```python
from error_handler import (
    ErrorHandler,
    ConfigurationError,
    NetworkError,
    ComponentError,
    PairingError,
    RuntimeError as JarvisRuntimeError,
    get_error_handler,
    set_error_handler
)
```

### 2. Initialize the Error Handler

```python
# Create error handler with optional status callback
def send_status_to_ui(status_data):
    # Your UI update logic here
    print(f"Status: {status_data['message']}")

error_handler = ErrorHandler(
    log_dir=Path("data/logs"),  # Optional, defaults to data/logs
    status_callback=send_status_to_ui  # Optional
)

# Set as global instance
set_error_handler(error_handler)
```

### 3. Use Specific Error Types

#### Configuration Errors

```python
try:
    # Load configuration
    config = load_config()
except Exception as e:
    error = ConfigurationError(
        "Failed to load configuration",
        details={
            'type': 'corrupted_config',  # or 'missing_api_key', 'invalid_path', etc.
            'path': config_path
        }
    )
    error_handler.handle_configuration_error(error, recovery_callback=restore_from_backup)
```

#### Network Errors

```python
try:
    # Connect to Firebase
    firebase.connect()
except Exception as e:
    error = NetworkError(
        "Failed to connect to Firebase",
        details={
            'type': 'firebase_connection',
            'server_url': firebase_url
        }
    )
    error_handler.handle_network_error(error, retry_callback=retry_connection)
```

#### Component Crashes

```python
# In application launcher monitoring loop
if process.poll() is not None:
    error = ComponentError(
        f"Backend server crashed with exit code {process.returncode}",
        component="Backend Server",
        details={
            'exit_code': process.returncode,
            'restart_count': restart_count
        }
    )
    
    def restart_callback(err):
        return restart_component("backend")
    
    success = error_handler.handle_component_crash(error, restart_callback)
```

#### Pairing Errors

```python
try:
    # Verify pairing token
    if token_expired(token):
        error = PairingError(
            "Pairing token has expired",
            details={'type': 'expired_token'}
        )
        error_handler.handle_pairing_error(error, regenerate_callback=generate_new_token)
except Exception as e:
    error = PairingError(
        f"Pairing failed: {str(e)}",
        details={'type': 'invalid_token'}
    )
    error_handler.handle_pairing_error(error)
```

#### Runtime Errors

```python
try:
    # Perform file operation
    with open(file_path, 'w') as f:
        f.write(data)
except PermissionError as e:
    error = RuntimeError(
        "Permission denied when writing file",
        details={
            'type': 'permission_denied',
            'path': file_path
        }
    )
    error_handler.handle_runtime_error(error)
```

### 4. Handle Generic Exceptions

For exceptions that don't fit specific categories:

```python
try:
    # Some operation
    result = complex_operation()
except Exception as e:
    error_handler.handle_generic_error(
        e,
        category=ErrorCategory.RUNTIME,
        context="Complex operation execution"
    )
```

## Error Types and User Messages

The error handler automatically provides user-friendly messages based on error types:

### Configuration Error Types
- `missing_api_key` → "API key is missing. Please configure your API keys in Settings."
- `invalid_api_key` → "API key is invalid. Please check your API key and try again."
- `invalid_path` → "System path is invalid. Please verify the path exists."
- `corrupted_config` → "Configuration file is corrupted. Attempting to restore from backup..."
- `missing_firebase` → "Firebase credentials are missing. Please configure Firebase settings."

### Network Error Types
- `firebase_connection` → "Unable to connect to Firebase. Retrying..."
- `api_unreachable` → "API endpoint is unreachable. Check your internet connection."
- `timeout` → "Request timed out. Please try again."
- `rate_limit` → "Rate limit exceeded. Please wait before trying again."

### Pairing Error Types
- `expired_token` → "Pairing code has expired. Generating a new code..."
- `invalid_token` → "Invalid pairing code. Please scan the QR code again."
- `already_paired` → "Device is already paired. Unpair first to pair with a new device."
- `scan_failure` → "Failed to scan QR code. Please try again or enter the code manually."

### Runtime Error Types
- `permission_denied` → "Permission denied. Please run JARVIS with appropriate permissions."
- `disk_space` → "Insufficient disk space. Please free up space and try again."
- `memory` → "Insufficient memory. Please close other applications and try again."
- `dependency_missing` → "Required dependency is missing. Please reinstall JARVIS."

## Recovery Callbacks

Recovery callbacks allow automatic error recovery:

```python
def recovery_callback(error: JarvisError):
    """
    Recovery callback for configuration errors.
    
    Args:
        error: The error that occurred
    """
    # Attempt to restore from backup
    if restore_from_backup():
        return True
    
    # If backup fails, use defaults
    use_default_config()
    return True

error_handler.handle_configuration_error(error, recovery_callback=recovery_callback)
```

## Error Statistics

Track error counts by category:

```python
# Get error statistics
stats = error_handler.get_error_statistics()
print(f"Configuration errors: {stats['configuration']}")
print(f"Network errors: {stats['network']}")

# Clear statistics
error_handler.clear_statistics()
```

## Global Error Handler

Use the global error handler instance:

```python
# Get global instance
error_handler = get_error_handler()

# Use it anywhere in your code
error_handler.handle_generic_error(exception, context="Some operation")
```

## Error Logs

Error logs are automatically written to:
- Location: `data/logs/errors_YYYYMMDD.log`
- Format: Timestamped entries with category, severity, message, and details
- Full details: JSON format with traceback (if available)

Example log entry:
```
2026-02-09 22:30:15 - ERROR - [configuration] - Failed to load configuration | Details: {"type": "corrupted_config", "path": "config.py"}
```

## Best Practices

1. **Always use specific error types** when possible (ConfigurationError, NetworkError, etc.)
2. **Provide detailed error information** in the `details` dictionary
3. **Use recovery callbacks** for automatic error recovery
4. **Set up status callbacks** to update the UI with error messages
5. **Check error logs** regularly for debugging
6. **Use the global error handler** for consistency across components

## Integration Examples

### In client.py
```python
# Initialize error handler on connect
error_handler = ErrorHandler(status_callback=send_status)
set_error_handler(error_handler)

# Use in exception handling
try:
    execute_plan(plan)
except Exception as e:
    error_handler.handle_generic_error(e, context="Plan execution")
```

### In application_launcher.py
```python
# Initialize in __init__
self.error_handler = ErrorHandler()
set_error_handler(self.error_handler)

# Use in component monitoring
if process.poll() is not None:
    error = ComponentError(...)
    success = self.error_handler.handle_component_crash(error, restart_callback)
```

### In settings_app.py
```python
# Initialize in SettingsAPI.__init__
self.error_handler = ErrorHandler()

# Use in API methods
try:
    settings = self.config_manager.read_config()
except Exception as e:
    error = ConfigurationError(...)
    self.error_handler.handle_configuration_error(error)
```

## Testing Error Handling

Test error handling by triggering specific error conditions:

```python
# Test configuration error
error = ConfigurationError("Test error", details={'type': 'missing_api_key'})
error_handler.handle_configuration_error(error)

# Test network error with retry
error = NetworkError("Test connection failure", details={'type': 'firebase_connection'})
error_handler.handle_network_error(error, retry_callback=lambda e: print("Retrying..."))

# Verify error was logged
stats = error_handler.get_error_statistics()
assert stats['configuration'] == 1
assert stats['network'] == 1
```
