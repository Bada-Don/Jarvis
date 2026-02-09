# Eventlet monkey patch MUST be first, before any other imports
import eventlet
eventlet.monkey_patch()

import os
import base64
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime
from planner_service import PlannerService

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
    print("✓ Gemini Planner Service initialized successfully")
except ValueError as e:
    print(f"⚠ Gemini Planner Service not available: {e}")

# Initialize Firebase Service (optional)
firebase_service = None
firebase_enabled = False
try:
    from firebase_service import FirebaseService
    
    # Check for Firebase credentials
    firebase_creds_path = os.path.join('data', 'firebase-admin-credentials.json')
    if os.path.exists(firebase_creds_path):
        firebase_service = FirebaseService(firebase_creds_path)
        firebase_enabled = True
        print("✓ Firebase Service initialized successfully")
    else:
        print("⚠ Firebase credentials not found, Firebase features disabled")
except Exception as e:
    print(f"⚠ Firebase Service not available: {e}")


def get_or_create_device_id():
    """
    Get or create a unique device ID for this backend instance.
    Stored in data/device_id.txt
    """
    device_id_path = os.path.join('data', 'device_id.txt')
    
    # Try to load existing device ID
    if os.path.exists(device_id_path):
        try:
            with open(device_id_path, 'r') as f:
                device_id = f.read().strip()
                if device_id:
                    return device_id
        except Exception as e:
            print(f"⚠️ Error reading device ID: {e}")
    
    # Generate new device ID
    import uuid
    device_id = f"desktop_{uuid.uuid4().hex[:16]}"
    
    # Save device ID
    try:
        os.makedirs('data', exist_ok=True)
        with open(device_id_path, 'w') as f:
            f.write(device_id)
        print(f"✓ Generated new device ID: {device_id}")
    except Exception as e:
        print(f"⚠️ Error saving device ID: {e}")
    
    return device_id


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
    Send command via both WebSocket (for backward compatibility) and Firebase.
    
    Args:
        command_payload: Command data to send
    """
    # Send via WebSocket (existing behavior)
    socketio.emit('command', command_payload)
    
    # Send via Firebase if enabled
    if firebase_enabled and firebase_service and firebase_service.device_id:
        firebase_service.send_command(firebase_service.device_id, command_payload)


def send_status_dual(status_data):
    """
    Send status update via both WebSocket and Firebase.
    
    Args:
        status_data: Status data to send
    """
    # Send via WebSocket (existing behavior)
    socketio.emit('jarvis_status', status_data)
    
    # Send via Firebase if enabled
    if firebase_enabled and firebase_service and firebase_service.device_id:
        firebase_service.send_status(firebase_service.device_id, status_data)


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
    
    print(f"Received instruction: {text}")
    
    if planner_service is None:
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
        error_msg = f"Failed to generate plan: {e}"
        print(f"✗ {error_msg}")
        send_status_dual({
            'message': error_msg,
            'status': 'error',
            'error': str(e)
        })
        return jsonify({
            "status": "error",
            "response": "Sorry, I couldn't understand that command. Please try again."
        }), 500
        
    except Exception as e:
        error_msg = f"Error processing request: {e}"
        print(f"✗ {error_msg}")
        send_status_dual({
            'message': 'An error occurred while processing your request.',
            'status': 'error',
            'error': str(e)
        })
        return jsonify({
            "status": "error",
            "response": "An error occurred. Please try again."
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
    print("=" * 50)
    print("🤖 JARVIS Backend Server Starting...")
    print("=" * 50)
    
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=False,
        use_reloader=False,
        log_output=True
    )
