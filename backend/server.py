import os
import base64
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=50 * 1024 * 1024)

UPLOAD_FOLDER = 'uploads'
LOG_FILE = 'logs.txt'

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Mock AI Logic ---
def mock_router(text):
    """
    Analyzes text and returns an intent.
    For MVP, we look for keywords.
    """
    text = text.lower()
    
    # FlexiSIGN keywords
    flexisign_keywords = ["nameplate", "numberplate", "sticker", "logo"]
    
    if any(keyword in text for keyword in flexisign_keywords):
        return {
            "intent": "create_draft",
            "software": "flexisign",
            "params": {"size": "15x10", "color": "silver"} # Extracted from text in real scenario
        }
    
    return {"intent": "unknown", "message": "I didn't understand that."}


def mock_vision_ocr(image_path):
    """
    Mock OCR. In real life, sends to ChatGPT/Vision API.
    """
    return "Dr. A.K. Sharma"

# --- Endpoints ---

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
        # Generate a filename if none provided
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Detect file type from content type
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
        
        # If it's an audio file, we could transcribe it here (future feature)
        if 'audio' in (request.files['file'].content_type or ''):
            print(f"🎤 Audio file detected: {filename}")
            # TODO: Add speech-to-text transcription here
            # transcribed_text = transcribe_audio(filepath)
        
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
    Main entry point for the Agent.
    Receives: { "text": "...", "image": "..." (optional base64 or filename) }
    """
    data = request.json
    text = data.get('text', '')
    image_data = data.get('image', None) # Could be base64 or just a flag that an image was uploaded previously
    
    print(f"Received instruction: {text}")

    # 1. Router Analysis
    intent_data = mock_router(text)
    
    if intent_data['intent'] == 'create_draft':
        # 2. If there's an image (handwritten note), do OCR
        # For this MVP, we assume the image was uploaded via /api/upload and we might have the filename
        # Or we just mock the OCR result directly for now.
        extracted_text = mock_vision_ocr("dummy_path")
        
        # 3. Construct the Command for the Local Client
        # The FlexiSign Manager handles all startup logic automatically
        command_payload = {
            "action": "flexisign_workflow",
            "steps": [
                {"type": "notification", "message": f"Yes sir! On it. Creating draft for {extracted_text}..."},
                # FlexiSign Manager automatically handles:
                # - Loader/patcher startup and modal
                # - Closing demo mode windows
                # - Starting FlexiSign Pro properly
                # - Bringing window to front
                
                # Your actual workflow steps go here:
                {"type": "press_key", "key": "t"},
                {"type": "click_center"},
                {"type": "type_text", "text": extracted_text}
            ],
            "extracted_text": extracted_text
        }
        
        # 4. Send to Local Client via WebSocket
        print("Sending command to local client...")
        socketio.emit('command', command_payload)
        
        return jsonify({
            "status": "success", 
            "response": f"Yes sir! On it. Creating draft for {extracted_text} with size {intent_data['params']['size']}."
        })

    return jsonify({"status": "success", "response": "I didn't understand that."})

# --- SocketIO Events ---

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'data': 'Connected to Brain'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('screen_update')
def handle_screen_update(data):
    print("Received screen update (size: {})".format(len(data.get('image', ''))))
    # Here we would pass the image to SpiritSight
    pass

@socketio.on('status_update')
def handle_status_update(data):
    """Receive status updates from local client and broadcast to mobile app."""
    message = data.get('message', '')
    status_type = data.get('type', 'info')
    
    # Check if message is a dict with progress data
    if isinstance(message, dict) and 'progress' in message:
        print(f"📱 Progress Update: {message.get('message')} ({message.get('progress')}%)")
        # Send progress data directly
        socketio.emit('jarvis_status', {
            'progress': message.get('progress'),
            'message': message.get('message'),
            'status': message.get('status', 'running'),
            'error': message.get('error'),
            'timestamp': data.get('timestamp')
        })
    else:
        print(f"📱 Status Update [{status_type}]: {message}")
        # Send regular status message
        socketio.emit('jarvis_status', {
            'message': message,
            'type': status_type,
            'timestamp': data.get('timestamp')
        })

if __name__ == '__main__':
    # Host 0.0.0.0 allows access from other devices/emulator
    # socketio.run replaces app.run
    # use_reloader=True enables auto-reload on code changes
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=True)
