import os
import sys
import time
import json
import uuid
import traceback
import requests
import pyautogui
import subprocess
import psutil
import win32gui
import win32con
import socketio
from datetime import datetime
from pathlib import Path
from dataclasses import asdict

# Add the script's directory and project root to Python path
script_dir = Path(__file__).parent.resolve()
project_root = script_dir.parent.resolve()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=script_dir / '.env')
except ImportError:
    pass

# Import core modules
from observation_module import ObservationModule

# Timing defaults from environment
ACTION_DELAY = float(os.environ.get('ACTION_DELAY', 0.3))
APP_LAUNCH_WAIT = float(os.environ.get('APP_LAUNCH_WAIT', 3.0))
HOTKEY_DELAY = float(os.environ.get('HOTKEY_DELAY', 0.5))
PRE_TYPE_DELAY = float(os.environ.get('PRE_TYPE_DELAY', 0.2))
SCREENSHOT_DELAY = float(os.environ.get('SCREENSHOT_DELAY', 0.5))
WINDOW_ACTIVATION_TIMEOUT = float(os.environ.get('WINDOW_ACTIVATION_TIMEOUT', 10.0))
WINDOW_POLL_INTERVAL = float(os.environ.get('WINDOW_POLL_INTERVAL', 0.5))
RETRY_DELAY = float(os.environ.get('RETRY_DELAY', 2.0))
VERIFICATION_DELAY = float(os.environ.get('VERIFICATION_DELAY', 1.0))

# Configuration settings
SERVER_URL = os.environ.get('BACKEND_URL', 'http://localhost:5000')
VERIFICATION_ENABLED = os.environ.get('VERIFICATION_ENABLED', 'false').lower() == 'true'
MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 0))
FIREBASE_ENABLED = os.environ.get('FIREBASE_ENABLED', 'true').lower() == 'true'

# Specialized managers and services
try:
    from flexisign_manager import FlexiSignManager
    FLEXISIGN_MANAGER_AVAILABLE = True
except ImportError:
    FLEXISIGN_MANAGER_AVAILABLE = False

try:
    from vision_service import VisionService
    from plan_executor import PlanExecutor
    TWO_MODEL_PIPELINE_AVAILABLE = True
except ImportError:
    TWO_MODEL_PIPELINE_AVAILABLE = False

try:
    from firebase_service import FirebaseService
    FIREBASE_SERVICE_AVAILABLE = True
except ImportError:
    FIREBASE_SERVICE_AVAILABLE = False

try:
    from debug_logger import create_new_session, get_debug_logger
    DEBUG_LOGGER_AVAILABLE = True
except ImportError:
    DEBUG_LOGGER_AVAILABLE = False

try:
    from permission_service import (
        PermissionService, register_abort_handler, 
        is_abort_requested, reset_abort
    )
    PERMISSION_SERVICE_AVAILABLE = True
except ImportError:
    PERMISSION_SERVICE_AVAILABLE = False

try:
    from error_handler import ErrorHandler, set_error_handler, get_error_handler, NetworkError
    ERROR_HANDLER_AVAILABLE = True
except ImportError:
    ERROR_HANDLER_AVAILABLE = False

# Initialize SocketIO Client
sio = socketio.Client(
    reconnection=True,
    reconnection_attempts=0,
    reconnection_delay=1,
    reconnection_delay_max=5,
    logger=False,
    engineio_logger=False
)

# Global instances
permission_service = None
firebase_service = None
firebase_enabled = False
error_handler = None
_global_executor = None

def get_paired_device_id():
    """Get the ID of the paired mobile device from device_config.json."""
    try:
        config_path = project_root / 'data' / 'device_config.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('paired_device_id')
    except Exception:
        pass
    return None

def get_or_create_device_id():
    """Get or create a unique device ID from device_config.json."""
    config_path = project_root / 'data' / 'device_config.json'
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                device_id = config.get('device_id')
                if device_id: return device_id
        except Exception:
            pass
    
    device_id = f"desktop_{uuid.uuid4().hex[:16]}"
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config = {'device_id': device_id, 'device_type': 'desktop', 'created_at': time.time()}
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"⚠️ Error saving device ID: {e}")
    return device_id

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
            if status_type in ['error', 'success', 'warning', 'info']:
                print(f"📤 Status: {message}")
        
        # 1. Send via WebSocket
        if sio.connected:
            sio.emit('status_update', status_data)
        
        # 2. Send via Firebase if enabled
        if firebase_enabled and firebase_service:
            paired_id = get_paired_device_id()
            if paired_id:
                msg_payload = message if isinstance(message, dict) else {'message': message, 'type': status_type}
                firebase_service.send_status(paired_id, msg_payload)
            
    except Exception as e:
        if status_type == 'error':
            print(f"Failed to send status: {e}")

@sio.event
def connect():
    global permission_service, error_handler
    if hasattr(connect, '_initialized'):
        print('✅ Reconnected to JARVIS Server')
        return
        
    print('✅ Connected to JARVIS Server')
    try:
        if ERROR_HANDLER_AVAILABLE and error_handler is None:
            error_handler = ErrorHandler(status_callback=send_status)
            set_error_handler(error_handler)
        
        if PERMISSION_SERVICE_AVAILABLE:
            permission_service = PermissionService(sio, status_callback=send_status)
            register_abort_handler(sio)
            
        connect._initialized = True
        print('✅ Connection setup complete')
    except Exception as e:
        print(f'❌ Error in connect handler: {traceback.format_exc()}')

@sio.event
def disconnect():
    print('❌ Disconnected from Server')

@sio.event
def command(data):
    action = data.get('action')
    print(f'📥 Received command: {action}')
    execute_command(data)

def handle_firebase_command(command_data):
    """Handle commands from Firebase by routing to backend or executing directly."""
    command_type = command_data.get('type', 'unknown')
    command_text = command_data.get('text', '')
    
    if command_type == 'command' and command_text:
        try:
            print(f'🔄 Routing Firebase command to backend: {command_text}')
            response = requests.post(f'{SERVER_URL}/api/process', json={'text': command_text}, timeout=120)
            if response.status_code != 200:
                send_status(f'Backend error: {response.status_code}', "error")
        except Exception as e:
            send_status(f'Routing failed: {e}', "error")
    elif command_data.get('action'):
        execute_command(command_data)

def execute_command(command_data):
    """Execute commands received from the server."""
    action = command_data.get('action')
    if action == 'execute_plan':
        execute_two_model_plan(command_data)
    elif action == 'execute_step':
        execute_single_step(command_data.get('session_id'), command_data.get('step'))
    elif action == 'verify_task':
        execute_verify_task(command_data.get('session_id'), command_data.get('expected_state'))
    elif action == 'flexisign_workflow':
        execute_flexisign_legacy(command_data)
    else:
        print(f"⚠️ Unknown action: {action}")
        send_status(f"Unknown action: {action}", "error")

def execute_two_model_plan(command_data, retry_count: int = 0):
    """Execute a full plan using the Two-Model Pipeline with retries."""
    if PERMISSION_SERVICE_AVAILABLE:
        reset_abort()
    
    if not TWO_MODEL_PIPELINE_AVAILABLE:
        send_status("Two-Model Pipeline not available.", "error")
        return
    
    plan = command_data.get('plan')
    user_command = command_data.get('user_command', '')
    mode = command_data.get('mode', plan.get('mode', 'general'))
    enable_verification = command_data.get('verify', VERIFICATION_ENABLED)
    
    debug_logger = None
    if DEBUG_LOGGER_AVAILABLE:
        try:
            debug_logger = create_new_session()
            debug_logger.set_user_command(user_command)
            debug_logger.log_planner_output(plan)
        except Exception: pass
    
    try:
        retry_msg = f" (retry {retry_count}/{MAX_RETRIES})" if retry_count > 0 else ""
        send_status({'message': f'Starting execution ({mode}){retry_msg}...', 'progress': 5}, "info")
        
        if mode == 'flexisign' and FLEXISIGN_MANAGER_AVAILABLE:
            manager = FlexiSignManager(status_callback=send_status)
            if not manager.ensure_proper_state():
                send_status("Failed to prepare FlexiSIGN", "error")
                return
        
        vision_service = VisionService()
        executor = PlanExecutor(vision_service, status_callback=send_status)
        if PERMISSION_SERVICE_AVAILABLE and permission_service:
            executor.set_permission_service(permission_service)
        
        result = executor.execute_plan(plan, verify=enable_verification)
        
        if result.get("aborted"):
            send_status("Task aborted", "error")
            return
            
        if result.get("success") and result.get("verified", True):
            send_status({'message': 'Task completed!', 'progress': 100}, "success")
            if debug_logger: debug_logger.complete(success=True)
        elif result.get("success") and not result.get("verified") and retry_count < MAX_RETRIES:
            send_status("Verification failed, retrying...", "warning")
            time.sleep(RETRY_DELAY)
            execute_two_model_plan(command_data, retry_count + 1)
        else:
            send_status("Task failed", "error")
            if debug_logger: debug_logger.complete(success=False)
                
    except Exception as e:
        print(f"❌ Execution error: {traceback.format_exc()}")
        send_status(f"Execution error: {str(e)}", "error")

def execute_single_step(session_id: str, step: dict):
    """Execute a single atomic step for ReAct loop."""
    global _global_executor
    try:
        if _global_executor is None:
            if not TWO_MODEL_PIPELINE_AVAILABLE:
                _send_step_result(session_id, step, False, "Pipeline components missing")
                return
            _global_executor = PlanExecutor(VisionService(), status_callback=send_status)
            if PERMISSION_SERVICE_AVAILABLE and permission_service:
                _global_executor.set_permission_service(permission_service)
        
        obs_module = ObservationModule(status_callback=send_status)
        pre_state = obs_module.capture_pre_step_state()
        
        result = _global_executor.execute_single_step(step)
        
        bundle = obs_module.collect_evidence_bundle(pre_state, result, step)
        observation_result = obs_module.verify(bundle, step)
        
        result_with_obs = dict(result)
        result_with_obs.update({
            'success': observation_result.verified,
            'verified': observation_result.verified,
            'confidence': observation_result.confidence,
            'strategy_used': observation_result.strategy_used,
            'reasoning': observation_result.reasoning,
            'evidence': observation_result.evidence,
            'bundle': asdict(bundle) if hasattr(bundle, '__dataclass_fields__') else {},
            'stdout': result.get('stdout', ''),
            'stderr': result.get('stderr', ''),
            'error_message': result.get('error_message')
        })
        
        _send_step_result(session_id, step, observation_result.verified, observation_result.reasoning, result_with_obs)
        
    except Exception as e:
        print(f"✗ Step error: {traceback.format_exc()}")
        _send_step_result(session_id, step, False, f"Error: {str(e)}")

def execute_verify_task(session_id: str, expected_state: str):
    """Perform visual verification for ReAct."""
    global _global_executor
    try:
        if _global_executor is None:
            _global_executor = PlanExecutor(VisionService(), status_callback=send_status)
            
        result = _global_executor.execute_verify_task(expected_state)
        sio.emit('verification_result', {
            'session_id': session_id,
            'success': result.get('success', False),
            'observation': result.get('observation', 'Verification complete'),
            'confidence': result.get('confidence', 0)
        })
    except Exception as e:
        print(f"✗ Verification error: {traceback.format_exc()}")
        sio.emit('verification_result', {
            'session_id': session_id, 'success': False, 'observation': str(e)
        })

def _send_step_result(session_id: str, step: dict, success: bool, observation: str, result_data: dict = None):
    """Report step result back to server."""
    payload = {
        'session_id': session_id,
        'step_order': step.get('order'),
        'step_type': step.get('type'),
        'success': success,
        'observation': observation,
        'timestamp': datetime.now().isoformat()
    }
    if result_data: payload.update(result_data)
    if sio.connected:
        sio.emit('step_result', payload)

def execute_flexisign_legacy(command_data):
    """Legacy FlexiSIGN workflow."""
    if FLEXISIGN_MANAGER_AVAILABLE:
        try:
            send_status("Starting FlexiSign automation...", "info")
            manager = FlexiSignManager(status_callback=send_status)
            if manager.ensure_proper_state():
                send_status("FlexiSign Pro is ready!", "success")
                steps = command_data.get('steps', [])
                for step in steps:
                    step_type = step.get('type')
                    if step_type == 'press_key': pyautogui.press(step.get('key'))
                    elif step_type == 'type_text': pyautogui.write(step.get('text'), interval=0.05)
                    time.sleep(0.5)
        except Exception as e:
            send_status(f"Flexisign error: {e}", "error")

def main():
    global firebase_service, firebase_enabled
    
    print("=" * 50)
    print("🤖 JARVIS Local Client Starting...")
    print("=" * 50)
    
    device_id = get_or_create_device_id()
    print(f"Device ID: {device_id}")
    
    # Show paired device info
    paired_mobile_id = get_paired_device_id()
    if paired_mobile_id:
        print(f"Paired with mobile: {paired_mobile_id}")
    else:
        print("Not paired with mobile device")
    
    # Firebase Setup
    if FIREBASE_ENABLED and FIREBASE_SERVICE_AVAILABLE and device_id:
        try:
            creds_path = project_root / 'data' / 'firebase-admin-credentials.json'
            if creds_path.exists():
                print('🔥 Initializing Firebase service...')
                firebase_service = FirebaseService(str(creds_path))
                firebase_service.set_device_id(device_id)
                firebase_service.register_device(device_id, device_type="desktop")
                if hasattr(firebase_service, 'start_presence_tracking'):
                    firebase_service.start_presence_tracking(device_id)
                firebase_service.listen_for_commands(device_id, handle_firebase_command)
                firebase_enabled = True
                print('✅ Firebase initialized')
            else:
                print(f'⚠️ Firebase credentials missing at: {creds_path}')
        except Exception as e:
            print(f'❌ Firebase initialization error: {traceback.format_exc()}')

    print("=" * 50)
    print(f"🔌 Connecting to {SERVER_URL}...")
    try:
        sio.connect(SERVER_URL, wait_timeout=10)
        sio.wait()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        if ERROR_HANDLER_AVAILABLE:
            get_error_handler().handle_network_error(NetworkError(f"Connection failed: {e}"))

if __name__ == '__main__':
    main()
