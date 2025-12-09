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

# Import debug logger
try:
    from debug_logger import create_new_session, get_debug_logger
    DEBUG_LOGGER_AVAILABLE = True
except ImportError:
    DEBUG_LOGGER_AVAILABLE = False

# Initialize SocketIO Client
sio = socketio.Client()


@sio.event
def connect():
    print('✅ Connected to JARVIS Server')


@sio.event
def disconnect():
    print('❌ Disconnected from Server')


@sio.event
def command(data):
    print(f'📥 Received command: {data.get("action", "unknown")}')
    execute_command(data)


def send_status(message, status_type="info"):
    """Send status update to server."""
    try:
        if isinstance(message, dict):
            sio.emit('status_update', {
                'message': message,
                'type': message.get('status', status_type),
                'timestamp': time.time()
            })
            print(f"📤 Progress: {message.get('message', '')} ({message.get('progress', 0)}%)")
        else:
            sio.emit('status_update', {
                'message': message,
                'type': status_type,
                'timestamp': time.time()
            })
            print(f"📤 Status: {message}")
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
        retry_count: Current retry attempt (max 2 retries)
    """
    MAX_RETRIES = 2
    
    if not TWO_MODEL_PIPELINE_AVAILABLE:
        send_status("Two-Model Pipeline not available. Missing dependencies.", "error")
        return
    
    plan = command_data.get('plan')
    user_command = command_data.get('user_command', '')
    mode = command_data.get('mode', plan.get('mode', 'general'))
    enable_verification = command_data.get('verify', True)  # Enable by default
    
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
                'progress': 15,
                'status': 'info'
            }, "info")
        except Exception as e:
            send_status(f"Vision service error: {e}", "error")
            return
        
        # Initialize Plan Executor
        executor = PlanExecutor(vision_service, status_callback=send_status)
        
        # Log execution start
        sequence = plan.get('sequence', [])
        expected_state = plan.get('expected_final_state', '')
        print(f"📋 Executing {len(sequence)} steps for: {user_command}")
        if expected_state:
            print(f"📋 Expected final state: {expected_state}")
        
        # Execute the plan with verification
        result = executor.execute_plan(plan, verify=enable_verification)
        
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
            
            # Wait before retry
            time.sleep(1.5)
            
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
        print(f"❌ Execution error: {e}")
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
    print("=" * 50)
    print("🤖 JARVIS Local Client Starting...")
    print("=" * 50)
    print(f"Server URL: {SERVER_URL}")
    print(f"FlexiSign Manager: {'✅' if FLEXISIGN_MANAGER_AVAILABLE else '❌'}")
    print(f"Two-Model Pipeline: {'✅' if TWO_MODEL_PIPELINE_AVAILABLE else '❌'}")
    print(f"Debug Logger: {'✅' if DEBUG_LOGGER_AVAILABLE else '❌'}")
    print("=" * 50)
    
    try:
        sio.connect(SERVER_URL)
        sio.wait()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        sio.disconnect()
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)
        main()


if __name__ == '__main__':
    main()
