import os
import sys
import base64
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime

# Import config from local_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'local_client'))
import config

# Try to use FunctionGemma (local) first, fall back to Gemini API if not available
USE_LOCAL_MODEL = getattr(config, 'USE_LOCAL_MODEL', True)

if USE_LOCAL_MODEL:
    try:
        from functiongemma_planner_adapter import FunctionGemmaPlannerAdapter
        print("🤖 Using FunctionGemma (local model) for planning")
        PLANNER_CLASS = FunctionGemmaPlannerAdapter
    except Exception as e:
        print(f"⚠ FunctionGemma not available ({e}), falling back to Gemini API")
        from gemini_service import GeminiPlannerService
        PLANNER_CLASS = GeminiPlannerService
else:
    from gemini_service import GeminiPlannerService
    print("🤖 Using Gemini API for planning")
    PLANNER_CLASS = GeminiPlannerService

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=50 * 1024 * 1024)

UPLOAD_FOLDER = 'uploads'
LOG_FILE = 'logs.txt'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize Planner Service (FunctionGemma or Gemini API)
planner_service = None
try:
    planner_service = PLANNER_CLASS()
    service_name = "FunctionGemma (local)" if USE_LOCAL_MODEL else "Gemini API"
    print(f"✓ Planner Service initialized successfully ({service_name})")
except ValueError as e:
    print(f"⚠ Planner Service not available: {e}")
except Exception as e:
    print(f"⚠ Planner Service initialization failed: {e}")


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
            "response": "Planner service not available. Check configuration."
        }), 500
    
    try:
        # Emit status update
        socketio.emit('jarvis_status', {
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
        
        socketio.emit('jarvis_status', {
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
        
        # Send to Local Client via WebSocket
        print(f"📤 Sending execute_plan command (mode: {mode})...")
        socketio.emit('command', command_payload)
        
        return jsonify({
            "status": "success",
            "response": f"Processing: {text}",
            "mode": mode,
            "plan_steps": step_count
        })
        
    except ValueError as e:
        error_msg = f"Failed to generate plan: {e}"
        print(f"✗ {error_msg}")
        socketio.emit('jarvis_status', {
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
        socketio.emit('jarvis_status', {
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
        socketio.emit('jarvis_status', {
            'progress': message.get('progress'),
            'message': message.get('message'),
            'status': message.get('status', 'running'),
            'error': message.get('error'),
            'timestamp': data.get('timestamp')
        })
    else:
        print(f"📱 Status [{status_type}]: {message}")
        socketio.emit('jarvis_status', {
            'message': message,
            'type': status_type,
            'timestamp': data.get('timestamp')
        })


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
    
    # Only watch Python files in the backend directory, not venv
    # This prevents torch library changes from triggering restarts
    extra_dirs = [os.path.dirname(os.path.abspath(__file__))]
    extra_files = []
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            # Skip venv, __pycache__, and other non-code directories
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules', 'weights', 'uploads']]
            for filename in files:
                if filename.endswith('.py'):
                    filepath = os.path.join(dirname, filename)
                    if os.path.isfile(filepath):
                        extra_files.append(filepath)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=True, extra_files=extra_files)
