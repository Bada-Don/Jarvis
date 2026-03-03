# Eventlet monkey patch MUST be first, before any other imports
import eventlet
eventlet.monkey_patch()

import os
import base64
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime
from newPlanner_service import PlannerService

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size
CORS(app)

# Configure SocketIO with longer timeouts for automation tasks
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    max_http_buffer_size=50 * 1024 * 1024,
    ping_timeout=60,  # Wait 60 seconds for ping response before disconnecting
    ping_interval=25,  # Send ping every 25 seconds to keep connection alive
    async_mode='eventlet'  # Use eventlet for better long-running task support
)

UPLOAD_FOLDER = 'uploads'
LOG_FILE = 'logs.txt'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize Gemini Planner Service
planner_service = None
try:
    planner_service = PlannerService()
    print("✓ Gemini Planner Service initialized successfully", flush=True)
except ValueError as e:
    print(f"⚠ Gemini Planner Service not available: {e}", flush=True)


def get_or_create_device_id():
    """
    Get or create a unique device ID for this backend instance.
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
                    print(f"✓ Using device ID from device_config.json: {device_id}", flush=True)
                    return device_id
        except Exception as e:
            print(f"⚠️ Error reading device_config.json: {e}", flush=True)
    
    # Fall back to legacy device_id.txt
    device_id_path = Path(__file__).parent / 'data' / 'device_id.txt'
    
    # Try to load existing device ID
    if device_id_path.exists():
        try:
            with open(device_id_path, 'r') as f:
                device_id = f.read().strip()
                if device_id:
                    print(f"✓ Using device ID from device_id.txt: {device_id}", flush=True)
                    return device_id
        except Exception as e:
            print(f"⚠️ Error reading device ID: {e}", flush=True)
    
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
        print(f"✓ Generated new device ID and saved to device_config.json: {device_id}", flush=True)
    except Exception as e:
        print(f"⚠️ Error saving device_config.json: {e}", flush=True)
        # Fall back to saving in device_id.txt
        try:
            device_id_path.parent.mkdir(parents=True, exist_ok=True)
            with open(device_id_path, 'w') as f:
                f.write(device_id)
            print(f"✓ Saved device ID to device_id.txt: {device_id}", flush=True)
        except Exception as e:
            print(f"⚠️ Error saving device ID: {e}", flush=True)
    
    return device_id


# Initialize Firebase Service (optional - legacy)
firebase_service = None
firebase_enabled = False
try:
    from firebase_service import FirebaseService
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if Firebase is enabled in environment
    firebase_enabled_env = os.getenv('FIREBASE_ENABLED', 'false').lower() == 'true'
    
    if firebase_enabled_env:
        # Check for Firebase credentials (resolve relative to project root)
        from pathlib import Path
        firebase_creds_path = Path(__file__).parent.parent / 'data' / 'firebase-admin-credentials.json'
        print(f'🔍 Looking for Firebase credentials at: {firebase_creds_path}', flush=True)
        
        if firebase_creds_path.exists():
            firebase_service = FirebaseService(str(firebase_creds_path))
            firebase_enabled = True
            print("✓ Firebase Service initialized successfully", flush=True)
            
            # Get device ID and set it on firebase_service
            device_id = get_or_create_device_id()
            firebase_service.set_device_id(device_id)
            firebase_service.register_device(device_id, device_type="desktop")
            print(f"✓ Backend device ID: {device_id}", flush=True)
        else:
            print(f"⚠ Firebase credentials not found at: {firebase_creds_path}", flush=True)
            print("⚠ Firebase features disabled", flush=True)
    else:
        print("⚠ Firebase disabled in environment (FIREBASE_ENABLED=false)", flush=True)
except Exception as e:
    print(f"⚠ Firebase Service not available: {e}", flush=True)


# Initialize AWS Service Hub (primary)
aws_service = None
aws_enabled = False
try:
    from aws_service_hub import AWSServiceHub
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get AWS configuration from environment
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    dynamodb_table = os.getenv('AWS_DYNAMODB_TABLE_NAME', 'JarvisState')
    s3_bucket = os.getenv('AWS_S3_BUCKET_NAME', 'jarvis-automation-assets')
    
    aws_service = AWSServiceHub(
        region_name=aws_region,
        dynamodb_table_name=dynamodb_table,
        s3_bucket_name=s3_bucket
    )
    aws_enabled = True
    print("✓ AWS Service Hub initialized successfully", flush=True)
    
    # Get device ID and register with AWS
    device_id = get_or_create_device_id()
    aws_service.set_device_id(device_id)
    aws_service.register_device(device_id, device_type="desktop")
    print(f"✓ Backend device ID: {device_id}", flush=True)
    
except Exception as e:
    print(f"⚠ AWS Service Hub not available: {e}", flush=True)
    print("⚠ AWS features disabled - falling back to Firebase if available", flush=True)


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    
    if message:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
            
        return jsonify({"status": "success", "message": "Message logged"}), 200
    return jsonify({"status": "error", "message": "No message provided"}), 400


def send_command_dual(command_payload):
    """
    Send command via both WebSocket and AWS/Firebase.

    Args:
        command_payload: Command data to send
    """
    # Send via WebSocket (existing behavior)
    socketio.emit('command', command_payload)

    # Send via AWS if enabled (primary)
    if aws_enabled and aws_service and aws_service.device_id:
        try:
            import json
            from pathlib import Path
            device_config_path = Path(__file__).parent.parent / 'data' / 'device_config.json'
            if device_config_path.exists():
                with open(device_config_path, 'r') as f:
                    config = json.load(f)
                    paired_mobile_id = config.get('paired_device_id')
                    if paired_mobile_id:
                        aws_service.send_command(paired_mobile_id, command_payload)
                        print(f"📤 AWS command sent to mobile: {paired_mobile_id}", flush=True)
                    else:
                        print(f"⚠️ No paired mobile device ID in config", flush=True)
            else:
                print(f"⚠️ device_config.json not found, skipping AWS command", flush=True)
        except Exception as e:
            print(f"⚠️ Error sending AWS command: {e}", flush=True)

    # Fallback to Firebase if AWS not available
    elif firebase_enabled and firebase_service and firebase_service.device_id:
        try:
            import json
            from pathlib import Path
            device_config_path = Path(__file__).parent.parent / 'data' / 'device_config.json'
            if device_config_path.exists():
                with open(device_config_path, 'r') as f:
                    config = json.load(f)
                    paired_mobile_id = config.get('paired_device_id')
                    if paired_mobile_id:
                        firebase_service.send_command(paired_mobile_id, command_payload)
                        print(f"📤 Firebase command sent to mobile: {paired_mobile_id}", flush=True)
                    else:
                        print(f"⚠️ No paired mobile device ID found", flush=True)
        except Exception as e:
            print(f"⚠️ Error sending Firebase command: {e}", flush=True)



def send_status_dual(status_data):
    """
    Send status update via both WebSocket and AWS/Firebase.
    
    Args:
        status_data: Status data to send
    """
    # Send via WebSocket (existing behavior)
    socketio.emit('jarvis_status', status_data)
    
    # Send via AWS if enabled (primary)
    if aws_enabled and aws_service and aws_service.device_id:
        try:
            import json
            from pathlib import Path
            device_config_path = Path(__file__).parent.parent / 'data' / 'device_config.json'
            if device_config_path.exists():
                with open(device_config_path, 'r') as f:
                    config = json.load(f)
                    paired_mobile_id = config.get('paired_device_id')
                    if paired_mobile_id:
                        aws_service.send_status(paired_mobile_id, status_data)
                        print(f"📤 AWS status sent to mobile: {paired_mobile_id}", flush=True)
                        
                        # Save to task history if this is a task completion
                        if status_data.get('status') in ['completed', 'error']:
                            task_id = status_data.get('task_id', f"task_{int(time.time())}")
                            aws_service.save_task_history(
                                aws_service.device_id,
                                task_id,
                                status_data
                            )
                    else:
                        print(f"⚠️ No paired mobile device ID in config", flush=True)
            else:
                print(f"⚠️ device_config.json not found, skipping AWS status", flush=True)
        except Exception as e:
            print(f"⚠️ Error sending AWS status: {e}", flush=True)
    
    # Fallback to Firebase if AWS not available
    elif firebase_enabled and firebase_service and firebase_service.device_id:
        try:
            import json
            from pathlib import Path
            device_config_path = Path(__file__).parent.parent / 'data' / 'device_config.json'
            if device_config_path.exists():
                with open(device_config_path, 'r') as f:
                    config = json.load(f)
                    paired_mobile_id = config.get('paired_device_id')
                    if paired_mobile_id:
                        firebase_service.send_status(paired_mobile_id, status_data)
                        print(f"📤 Firebase status sent to mobile: {paired_mobile_id}")
                    else:
                        print(f"⚠️ No paired mobile device ID in config")
            else:
                print(f"⚠️ device_config.json not found, skipping Firebase status")
        except Exception as e:
            print(f"⚠️ Error sending Firebase status: {e}")


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    
    file = request.files['file']
    
    if not file or file.filename == '' or file.filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_type = request.files['file'].content_type
        if 'audio' in content_type:
            filename = f"voice_{timestamp}.m4a"
        elif 'image' in content_type:
            filename = f"image_{timestamp}.jpg"
        else:
            filename = f"upload_{timestamp}"
    else:
        filename = file.filename
    
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        file_size = os.path.getsize(filepath)
        print(f"✓ File saved: {filename} ({file_size} bytes)")
        
        return jsonify({
            "status": "success", 
            "message": f"File {filename} uploaded",
            "filename": filename,
            "size": file_size
        }), 200
    except Exception as e:
        print(f"✗ Upload error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/process', methods=['POST'])
def process_instruction():
    """
    Main entry point for JARVIS.
    Receives: { "text": "...", "image": "..." (optional) }
    
    Uses the Two-Model Pipeline:
    1. Planner Model generates execution plan (auto-detects mode)
    2. Sends plan to Local Client via WebSocket
    3. Local Client uses Vision Mapper for UI element identification
    """
    data = request.json
    text = data.get('text', '')
    image_data = data.get('image', None)
    
    print(f"📥 Received instruction: {text[:200]}{'...' if len(text) > 200 else ''}", flush=True)
    if image_data:
        print(f"📷 Image data included: {len(image_data)} bytes", flush=True)
    
    if planner_service is None:
        print("✗ Planner service not available", flush=True)
        return jsonify({
            "status": "error",
            "response": "Planner service not available. Check GEMINI_API_KEY."
        }), 500
    
    try:
        # Emit status update
        send_status_dual({
            'message': 'Processing your request...',
            'status': 'running',
            'progress': 5
        })
        
        # Generate execution plan (auto-detects mode: general vs flexisign)
        print("🤖 Calling Planner Model...")
        plan = planner_service.generate_plan(text)
        mode = plan.get('mode', 'general')
        step_count = len(plan.get('sequence', []))
        print(f"✓ Plan generated: {step_count} steps (mode: {mode})")
        
        send_status_dual({
            'message': f'Plan ready ({step_count} steps), sending to executor...',
            'status': 'running',
            'progress': 20
        })
        
        # Construct command payload
        command_payload = {
            "action": "execute_plan",
            "plan": plan,
            "user_command": text,
            "mode": mode
        }
        
        # Send to Local Client via WebSocket and Firebase
        print(f"📤 Sending execute_plan command (mode: {mode})...")
        send_command_dual(command_payload)
        
        return jsonify({
            "status": "success",
            "response": f"Processing: {text}",
            "mode": mode,
            "plan_steps": step_count
        })
        
    except ValueError as e:
        import traceback
        error_msg = f"Failed to generate plan: {e}"
        print(f"✗ {error_msg}", flush=True)
        print(f"✗ Traceback:\n{traceback.format_exc()}", flush=True)
        send_status_dual({
            'message': error_msg,
            'status': 'error',
            'error': str(e)
        })
        return jsonify({
            "status": "error",
            "response": "Sorry, I couldn't understand that command. Please try again.",
            "error_type": "ValueError"
        }), 500
        
    except Exception as e:
        import traceback
        error_msg = f"Error processing request: {e}"
        print(f"✗ {error_msg}", flush=True)
        print(f"✗ Full traceback:\n{traceback.format_exc()}", flush=True)
        print(f"✗ Request data: text='{text[:100]}...' (truncated)", flush=True)
        send_status_dual({
            'message': 'An error occurred while processing your request.',
            'status': 'error',
            'error': str(e)
        })
        return jsonify({
            "status": "error",
            "response": "An error occurred. Please try again.",
            "error_type": type(e).__name__
        }), 500


# --- SocketIO Events ---

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'data': 'Connected to JARVIS Brain'})
    
    # Register device with Firebase if enabled
    if firebase_enabled and firebase_service:
        try:
            # Generate or load device ID
            device_id = get_or_create_device_id()
            firebase_service.set_device_id(device_id)
            firebase_service.register_device(device_id, device_type="desktop")
            firebase_service.update_presence(device_id)
            
            # Emit Firebase connection status
            emit('firebase_status', {
                'connected': True,
                'device_id': device_id
            })
        except Exception as e:
            print(f"⚠️ Firebase registration error: {e}")
            emit('firebase_status', {
                'connected': False,
                'error': str(e)
            })

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('screen_update')
def handle_screen_update(data):
    print("Received screen update (size: {})".format(len(data.get('image', ''))))

@socketio.on('status_update')
def handle_status_update(data):
    """Receive status updates from local client and broadcast to mobile app."""
    message = data.get('message', '')
    status_type = data.get('type', 'info')
    
    if isinstance(message, dict) and 'progress' in message:
        print(f"📱 Progress: {message.get('message')} ({message.get('progress')}%)")
        status_data = {
            'progress': message.get('progress'),
            'message': message.get('message'),
            'status': message.get('status', 'running'),
            'error': message.get('error'),
            'timestamp': data.get('timestamp')
        }
        send_status_dual(status_data)
    else:
        print(f"📱 Status [{status_type}]: {message}")
        status_data = {
            'message': message,
            'type': status_type,
            'timestamp': data.get('timestamp')
        }
        send_status_dual(status_data)


# --- Permission Request Handling ---

# Store pending permission requests
pending_permissions = {}

@socketio.on('permission_request_from_client')
def handle_permission_request_from_client(data):
    """Receive permission request from local client and forward to mobile app."""
    request_id = data.get('requestId')
    operation = data.get('operation')
    details = data.get('details')
    
    print(f"🔐 Permission request from client: {operation} - {details}")
    
    # Store the request
    pending_permissions[request_id] = {
        'operation': operation,
        'details': details,
        'timestamp': data.get('timestamp')
    }
    
    # Forward to mobile app
    socketio.emit('permission_request', {
        'requestId': request_id,
        'operation': operation,
        'details': details,
        'timestamp': data.get('timestamp')
    })


@socketio.on('permission_response')
def handle_permission_response(data):
    """Receive permission response from mobile app and forward to local client."""
    request_id = data.get('requestId')
    approved = data.get('approved')
    
    print(f"🔐 Permission response: {request_id} - {'APPROVED' if approved else 'DENIED'}")
    
    # Remove from pending
    if request_id in pending_permissions:
        del pending_permissions[request_id]
    
    # Forward to local client
    socketio.emit('permission_response_to_client', {
        'requestId': request_id,
        'approved': approved,
        'timestamp': data.get('timestamp')
    })


# --- Abort Task Handling ---

@socketio.on('abort_task')
def handle_abort_task(data):
    """Receive abort signal from mobile app and forward to local client."""
    print("🛑 Abort task signal received from mobile app")
    
    # Forward to local client
    socketio.emit('abort_task_to_client', {
        'timestamp': data.get('timestamp')
    })
    
    # Also send status update to mobile app
    socketio.emit('jarvis_status', {
        'message': 'Task abort requested',
        'status': 'error',
        'progress': 0,
        'timestamp': data.get('timestamp')
    })


if __name__ == '__main__':
    print("=" * 50, flush=True)
    print("🤖 JARVIS Backend Server Starting...", flush=True)
    print("=" * 50, flush=True)
    
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=False,
        use_reloader=False,
        log_output=True
    )
