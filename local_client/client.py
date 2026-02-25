"""
JARVIS Local Client
Connects to the backend server and executes automation commands on the local machine.
Supports both general computer automation and FlexiSIGN-specific tasks.
"""

import socketio
import pyautogui
import time
import os
import subprocess
import psutil
import win32gui
import win32con
import sys
import requests

# Import configuration
try:
    from config import *
except ImportError:
    print("⚠️ Warning: config.py not found, using default settings")
    SERVER_URL = 'http://localhost:5000'

# Import FlexiSign Manager (for FlexiSIGN mode)
try:
    from flexisign_manager import FlexiSignManager
    FLEXISIGN_MANAGER_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: flexisign_manager.py not found")
    FLEXISIGN_MANAGER_AVAILABLE = False

# Import Two-Model Pipeline components
try:
    from vision_service import VisionService
    from plan_executor import PlanExecutor
    TWO_MODEL_PIPELINE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Two-Model Pipeline components not available: {e}")
    TWO_MODEL_PIPELINE_AVAILABLE = False

# Import Firebase Service
try:
    from firebase_service import FirebaseService
    FIREBASE_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Firebase Service not available: {e}")
    FIREBASE_SERVICE_AVAILABLE = False

# Import debug logger
try:
    from debug_logger import create_new_session, get_debug_logger
    DEBUG_LOGGER_AVAILABLE = True
except ImportError:
    DEBUG_LOGGER_AVAILABLE = False

# Import permission service
try:
    from permission_service import (
        PermissionService, 
        register_abort_handler, 
        is_abort_requested, 
        reset_abort
    )
    PERMISSION_SERVICE_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: permission_service.py not found")
    PERMISSION_SERVICE_AVAILABLE = False

# Import error handler
try:
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
    ERROR_HANDLER_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: error_handler.py not found")
    ERROR_HANDLER_AVAILABLE = False

# Initialize SocketIO Client with reconnection settings
sio = socketio.Client(
    reconnection=True,
    reconnection_attempts=0,  # Infinite reconnection attempts
    reconnection_delay=1,  # Start with 1 second delay
    reconnection_delay_max=5,  # Max 5 seconds between attempts
    logger=False,
    engineio_logger=False
)

# Permission service instance (initialized after connection)
permission_service = None

# Firebase service instance (initialized if credentials available)
firebase_service = None
firebase_enabled = False

# Error handler instance
error_handler = None


@sio.event
def connect():
    global permission_service, error_handler
    print('✅ Connected to JARVIS Server')
    
    try:
        # Initialize error handler
        if ERROR_HANDLER_AVAILABLE and error_handler is None:
            error_handler = ErrorHandler(status_callback=send_status)
            set_error_handler(error_handler)
            print('✅ Error handler initialized')
        
        # Initialize permission service after connection
        if PERMISSION_SERVICE_AVAILABLE:
            permission_service = PermissionService(sio, status_callback=send_status)
            register_abort_handler(sio)
            print('✅ Permission service initialized')
        
        print('✅ Connection setup complete')
    except Exception as e:
        print(f'❌ Error in connect handler: {e}')
        import traceback
        traceback.print_exc()


@sio.event
def disconnect():
    print('❌ Disconnected from Server')


@sio.event
def connect_error(data):
    print(f'❌ Connection error: {data}')
    import traceback
    traceback.print_exc()


@sio.event
def command(data):
    print(f'📥 Received command: {data.get("action", "unknown")}')
    execute_command(data)


def get_or_create_device_id():
    """
    Get or create a unique device ID for this client instance.
    Reads from canonical data/device_config.json (created by PairingManager).
    Falls back to data/device_id.txt for backward compatibility.
    """
    from pathlib import Path
    import json
    
    # Try canonical device_config.json first (created by PairingManager)
    device_config_path = Path(__file__).parent.parent / 'data' / 'device_config.json'
    if device_config_path.exists():
        try:
            with open(device_config_path, 'r') as f:
                config = json.load(f)
                device_id = config.get('device_id')
                if device_id:
                    print(f"✓ Using device ID from device_config.json: {device_id}")
                    return device_id
        except Exception as e:
            print(f"⚠️ Error reading device_config.json: {e}")
    
    # Fall back to legacy device_id.txt
    device_id_path = Path(__file__).parent / 'data' / 'device_id.txt'
    
    # Try to load existing device ID
    if device_id_path.exists():
        try:
            with open(device_id_path, 'r') as f:
                device_id = f.read().strip()
                if device_id:
                    print(f"✓ Using device ID from device_id.txt: {device_id}")
                    return device_id
        except Exception as e:
            print(f"⚠️ Error reading device ID: {e}")
    
    # Generate new device ID
    import uuid
    device_id = f"desktop_{uuid.uuid4().hex[:16]}"
    
    # Save to canonical location (device_config.json)
    try:
        device_config_path.parent.mkdir(parents=True, exist_ok=True)
        config = {
            'device_id': device_id,
            'device_type': 'desktop',
            'created_at': time.time()
        }
        with open(device_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✓ Generated new device ID and saved to device_config.json: {device_id}")
    except Exception as e:
        print(f"⚠️ Error saving device_config.json: {e}")
        # Fall back to saving in device_id.txt
        try:
            device_id_path.parent.mkdir(parents=True, exist_ok=True)
            with open(device_id_path, 'w') as f:
                f.write(device_id)
            print(f"✓ Saved device ID to device_id.txt: {device_id}")
        except Exception as e:
            print(f"⚠️ Error saving device ID: {e}")
    
    return device_id


def handle_firebase_command(command_data):
    """
    Handle commands received from Firebase.
    Route raw text commands through the backend planner.
    
    Args:
        command_data: Command data from Firebase
    """
    import requests
    
    # Log the received command
    command_type = command_data.get('type', 'unknown')
    command_text = command_data.get('text', '')
    print(f'📥 Firebase command received: type={command_type}, text={command_text}')
    
    # Check if this is a raw text command (from mobile app)
    if command_type == 'command' and command_text:
        # Route through backend planner to get proper execution plan
        try:
            print(f'🔄 Routing command through backend planner: {command_text}')
            
            # Send to backend's /api/process endpoint
            response = requests.post(
                f'{SERVER_URL}/api/process',
                json={'text': command_text},
                timeout=30
            )
            
            if response.status_code == 200:
                print('✅ Command routed to backend successfully')
                # Backend will send the execution plan via WebSocket/Firebase
                # with proper action: "execute_plan" structure
            else:
                error_msg = f'Backend returned error: {response.status_code}'
                print(f'❌ {error_msg}')
                send_status(error_msg, "error")
                
        except Exception as e:
            error_msg = f'Failed to route command to backend: {e}'
            print(f'❌ {error_msg}')
            send_status(error_msg, "error")
    
    # If it's already a structured command with action field, execute directly
    elif command_data.get('action'):
        print(f'📥 Executing structured command: {command_data.get("action")}')
        execute_command(command_data)
    
    else:
        print(f'⚠️ Unknown command format: {command_data}')
        send_status(f"Unknown command format", "error")


def send_status(message, status_type="info"):
    """Send status update to server via WebSocket and Firebase."""
    try:
        # Prepare status data
        if isinstance(message, dict):
            status_data = {
                'message': message,
                'type': message.get('status', status_type),
                'timestamp': time.time()
            }
            print(f"📤 Progress: {message.get('message', '')} ({message.get('progress', 0)}%)")
        else:
            status_data = {
                'message': message,
                'type': status_type,
                'timestamp': time.time()
            }
            print(f"📤 Status: {message}")
        
        # Send via WebSocket if connected
        if sio.connected:
            sio.emit('status_update', status_data)
        else:
            print(f"⚠️ Socket disconnected, skipping WebSocket status")
        
        # Send via Firebase if enabled
        if firebase_enabled and firebase_service and firebase_service.device_id:
            # Get paired mobile device ID from config
            try:
                from config import FIREBASE_PAIRED_DEVICE_ID
                paired_mobile_id = FIREBASE_PAIRED_DEVICE_ID
            except ImportError:
                paired_mobile_id = None
            
            # If no paired device in config, try reading from device_config.json
            if not paired_mobile_id:
                try:
                    from pathlib import Path
                    import json
                    device_config_path = Path(__file__).parent.parent / 'data' / 'device_config.json'
                    if device_config_path.exists():
                        with open(device_config_path, 'r') as f:
                            config = json.load(f)
                            paired_mobile_id = config.get('paired_device_id')
                except Exception as e:
                    print(f"⚠️ Error reading paired device ID: {e}")
            
            # Send status to paired mobile device (not desktop's own ID)
            if paired_mobile_id:
                firebase_service.send_status(paired_mobile_id, 
                                            message if isinstance(message, dict) else {'message': message, 'type': status_type})
                print(f"📤 Firebase status sent to mobile: {paired_mobile_id}")
            else:
                print(f"⚠️ No paired mobile device ID found, skipping Firebase status")
            
    except Exception as e:
        print(f"Failed to send status: {e}")


def execute_command(command_data):
    """
    Execute commands received from the server.
    Supports:
    - execute_plan: Two-Model Pipeline (general or FlexiSIGN)
    - flexisign_workflow: Legacy FlexiSIGN workflow
    """
    action = command_data.get('action')
    
    if action == 'execute_plan':
        execute_two_model_plan(command_data)
    
    elif action == 'flexisign_workflow':
        # Legacy support
        execute_flexisign_legacy(command_data)
    
    elif action == 'two_model_workflow':
        # Backward compatibility alias
        execute_two_model_plan(command_data)
    
    else:
        print(f"⚠️ Unknown action: {action}")
        send_status(f"Unknown action: {action}", "error")


def execute_two_model_plan(command_data, retry_count: int = 0):
    """
    Execute a plan using the Two-Model Pipeline.
    Works for both general tasks and FlexiSIGN-specific tasks.
    Includes verification and automatic retry on failure.
    
    Args:
        command_data: Command data from server
        retry_count: Current retry attempt (configurable via config.py)
    """
    # Reset abort flag at start of new execution
    if PERMISSION_SERVICE_AVAILABLE:
        reset_abort()
    
    # Load verification settings from config.py
    try:
        from config import (
            VERIFICATION_ENABLED, MAX_RETRIES, RETRY_DELAY, 
            VERIFICATION_DELAY, CONFIDENCE_THRESHOLD
        )
        enable_verification = VERIFICATION_ENABLED
        retry_delay = RETRY_DELAY
    except ImportError:
        # Fallback to defaults if config not available
        MAX_RETRIES = 0
        enable_verification = False  # Disabled by default for faster execution
        retry_delay = 2.0
    
    if not TWO_MODEL_PIPELINE_AVAILABLE:
        send_status("Two-Model Pipeline not available. Missing dependencies.", "error")
        return
    
    plan = command_data.get('plan')
    user_command = command_data.get('user_command', '')
    mode = command_data.get('mode', plan.get('mode', 'general'))
    # Allow command_data to override config (for testing/debugging)
    enable_verification = command_data.get('verify', enable_verification)
    
    if not plan:
        send_status("No execution plan received", "error")
        return
    
    # Initialize debug logger
    debug_logger = None
    if DEBUG_LOGGER_AVAILABLE:
        try:
            debug_logger = create_new_session()
            debug_logger.set_user_command(user_command)
            debug_logger.log_planner_output(plan)
            print(f"📁 Debug session: {debug_logger.session_id}")
        except Exception as e:
            print(f"⚠️ Debug logger error: {e}")
    
    try:
        retry_msg = f" (retry {retry_count}/{MAX_RETRIES})" if retry_count > 0 else ""
        send_status({
            'message': f'Starting execution (mode: {mode}){retry_msg}...',
            'progress': 5,
            'status': 'info'
        }, "info")
        
        # Check for abort before starting
        if PERMISSION_SERVICE_AVAILABLE and is_abort_requested():
            send_status({
                'message': 'Task aborted by user',
                'progress': 0,
                'status': 'error'
            }, "error")
            return
        
        # For FlexiSIGN mode, ensure the app is ready
        if mode == 'flexisign' and FLEXISIGN_MANAGER_AVAILABLE:
            send_status({
                'message': 'Preparing FlexiSIGN...',
                'progress': 8,
                'status': 'info'
            }, "info")
            
            manager = FlexiSignManager(status_callback=send_status)
            if not manager.ensure_proper_state():
                send_status({
                    'message': 'Failed to start FlexiSIGN Pro',
                    'progress': 0,
                    'status': 'error'
                }, "error")
                return
        
        # For general mode, just wait a moment for any app to be ready
        elif mode == 'general':
            time.sleep(0.5)
        
        # Initialize Vision Service
        try:
            vision_service = VisionService()
            send_status({
                'message': 'Vision service ready',
                'progress': 23,
                'status': 'info'
            }, "info")
        except Exception as e:
            send_status(f"Vision service error: {e}", "error")
            return
        
        # Initialize Plan Executor with permission service
        executor = PlanExecutor(vision_service, status_callback=send_status)
        
        # Pass permission service to executor if available
        if PERMISSION_SERVICE_AVAILABLE and permission_service:
            executor.set_permission_service(permission_service)
        
        # Log execution start
        sequence = plan.get('sequence', [])
        expected_state = plan.get('expected_final_state', '')
        print(f"📋 Executing {len(sequence)} steps for: {user_command}")
        if expected_state:
            print(f"📋 Expected final state: {expected_state}")
        
        # Execute the plan with verification
        result = executor.execute_plan(plan, verify=enable_verification)
        
        # Check if aborted
        if result.get("aborted", False):
            send_status({
                'message': 'Task aborted by user',
                'progress': 0,
                'status': 'error'
            }, "error")
            if debug_logger:
                debug_logger.log_error("Task aborted by user")
                debug_logger.complete(success=False)
            return
        
        exec_success = result.get("success", False)
        verified = result.get("verified", True)
        verification_result = result.get("verification_result")
        
        # Handle verification failure with retry
        if exec_success and not verified and retry_count < MAX_RETRIES:
            corrective_actions = []
            if verification_result:
                corrective_actions = verification_result.get("corrective_actions", [])
                current_state = verification_result.get("current_state", "Unknown")
                print(f"⚠️ Verification failed. Current: {current_state}")
                print(f"⚠️ Suggested corrections: {corrective_actions}")
            
            send_status({
                'message': f'Verification failed, retrying... ({retry_count + 1}/{MAX_RETRIES})',
                'progress': 50,
                'status': 'warning'
            }, "warning")
            
            # Log retry attempt
            if debug_logger:
                debug_logger.log_error(f"Verification failed, retry {retry_count + 1}")
            
            # Wait before retry (configurable delay)
            time.sleep(retry_delay)
            
            # Retry execution
            execute_two_model_plan(command_data, retry_count + 1)
            return
        
        # Final status
        if exec_success and verified:
            send_status({
                'message': 'Task completed and verified successfully!',
                'progress': 100,
                'status': 'success'
            }, "success")
            
            if debug_logger:
                debug_logger.complete(success=True)
                
        elif exec_success and not verified:
            # Verification failed after all retries
            send_status({
                'message': 'Task executed but verification failed after retries',
                'progress': 100,
                'status': 'warning'
            }, "warning")
            
            if debug_logger:
                debug_logger.complete(success=False)
        else:
            send_status({
                'message': 'Task execution failed',
                'progress': 100,
                'status': 'error'
            }, "error")
            
            if debug_logger:
                debug_logger.complete(success=False)
                
    except Exception as e:
        error_msg = f"Execution error: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Use error handler if available
        if error_handler:
            error_handler.handle_generic_error(e, context="Two-Model Pipeline execution")
        else:
            send_status({
                'message': f'Error: {str(e)}',
                'progress': 0,
                'status': 'error',
                'error': str(e)
            }, "error")
        
        if debug_logger:
            debug_logger.log_error(str(e))
            debug_logger.complete(success=False)


def execute_flexisign_legacy(command_data):
    """Legacy FlexiSIGN workflow execution."""
    if FLEXISIGN_MANAGER_AVAILABLE:
        try:
            send_status("Starting FlexiSign automation...", "info")
            manager = FlexiSignManager(status_callback=send_status)
            success = manager.ensure_proper_state()
            
            if success:
                send_status("FlexiSign Pro is ready!", "success")
                
                steps = command_data.get('steps', [])
                for step in steps:
                    step_type = step.get('type')
                    
                    if step_type in ['check_process', 'check_window', 'wait_for_modal']:
                        continue
                    
                    if step_type == 'notification':
                        send_status(step.get('message'), "info")
                    elif step_type == 'press_key':
                        pyautogui.press(step.get('key'))
                    elif step_type == 'click_center':
                        cx, cy = pyautogui.size()
                        pyautogui.click(cx // 2, cy // 2)
                    elif step_type == 'type_text':
                        pyautogui.write(step.get('text'), interval=0.05)
                    
                    time.sleep(0.5)
            else:
                send_status("Failed to start FlexiSign Pro", "error")
                
        except Exception as e:
            print(f"Error: {e}")
            send_status(f"Error: {e}", "error")


def main():
    global firebase_service, firebase_enabled
    
    print("=" * 50)
    print("🤖 JARVIS Local Client Starting...")
    print("=" * 50)
    print(f"Server URL: {SERVER_URL}")
    print(f"FlexiSign Manager: {'✅' if FLEXISIGN_MANAGER_AVAILABLE else '❌'}")
    print(f"Two-Model Pipeline: {'✅' if TWO_MODEL_PIPELINE_AVAILABLE else '❌'}")
    print(f"Debug Logger: {'✅' if DEBUG_LOGGER_AVAILABLE else '❌'}")
    print(f"Permission Service: {'✅' if PERMISSION_SERVICE_AVAILABLE else '❌'}")
    print(f"Firebase Service: {'✅' if FIREBASE_SERVICE_AVAILABLE else '❌'}")
    print(f"Error Handler: {'✅' if ERROR_HANDLER_AVAILABLE else '❌'}")
    
    # Show device ID info
    try:
        device_id = get_or_create_device_id()
        print(f"Device ID: {device_id}")
    except Exception as e:
        print(f"⚠️ Could not get device ID: {e}")
        device_id = None
    
    # Show paired device info
    try:
        from config import FIREBASE_PAIRED, FIREBASE_PAIRED_DEVICE_ID
        if FIREBASE_PAIRED and FIREBASE_PAIRED_DEVICE_ID:
            print(f"Paired with mobile: {FIREBASE_PAIRED_DEVICE_ID}")
        else:
            print("Not paired with mobile device")
    except ImportError:
        print("Pairing info not available")
    
    print("=" * 50)
    
    # Initialize Firebase BEFORE connecting to SocketIO
    if FIREBASE_SERVICE_AVAILABLE and device_id:
        try:
            from pathlib import Path
            firebase_creds_path = Path(__file__).parent.parent / 'data' / 'firebase-admin-credentials.json'
            print(f'🔍 Looking for Firebase credentials at: {firebase_creds_path}')
            
            if firebase_creds_path.exists():
                print('🔥 Initializing Firebase service...')
                firebase_service = FirebaseService(str(firebase_creds_path))
                
                firebase_service.set_device_id(device_id)
                firebase_service.register_device(device_id, device_type="desktop")
                
                # Start presence tracking (guarded for compatibility)
                if hasattr(firebase_service, 'start_presence_tracking'):
                    firebase_service.start_presence_tracking(device_id)
                else:
                    print('⚠️ start_presence_tracking not available, skipping')
                
                # Listen for commands from Firebase
                firebase_service.listen_for_commands(device_id, handle_firebase_command)
                
                firebase_enabled = True
                print('✅ Firebase service initialized and listening')
                print(f'   Device ID: {device_id}')
                
                # Log paired device info
                try:
                    from config import FIREBASE_PAIRED_DEVICE_ID
                    if FIREBASE_PAIRED_DEVICE_ID:
                        print(f'   Paired with mobile: {FIREBASE_PAIRED_DEVICE_ID}')
                except ImportError:
                    pass
            else:
                print(f'⚠️ Firebase credentials not found at: {firebase_creds_path}')
                print('⚠️ Firebase features disabled')
        except Exception as e:
            print(f'❌ Firebase initialization error: {e}')
            import traceback
            traceback.print_exc()
    
    print("=" * 50)
    print("🔌 Connecting to backend server...")
    
    max_retries = 5
    retry_delay = 3
    connected = False
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔌 Connection attempt {attempt}/{max_retries}...")
            sio.connect(SERVER_URL, wait_timeout=10)
            print("✅ Connected to backend server")
            connected = True
            sio.wait()
            break
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            
            # Cleanup Firebase
            if firebase_enabled and firebase_service:
                firebase_service.close()
            
            if sio.connected:
                sio.disconnect()
            return
        except Exception as e:
            print(f"❌ Connection attempt {attempt} failed: {e}")
            
            if sio.connected:
                sio.disconnect()
            
            if attempt < max_retries:
                print(f"   Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"❌ All {max_retries} connection attempts failed.")
                
                # Use error handler if available
                if ERROR_HANDLER_AVAILABLE:
                    err_handler = get_error_handler()
                    if err_handler:
                        error = NetworkError(
                            f"Failed to connect to server after {max_retries} attempts: {str(e)}",
                            details={'type': 'api_unreachable', 'server_url': SERVER_URL}
                        )
                        err_handler.handle_network_error(error)


if __name__ == '__main__':
    main()
