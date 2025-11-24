import os
import base64
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

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
    if "nameplate" in text or "size" in text:
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
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        return jsonify({"status": "success", "message": f"File {file.filename} uploaded"}), 200

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
        command_payload = {
            "action": "sequence",
            "steps": [
                {"type": "notification", "message": "Starting FlexiSIGN automation..."},
                {"type": "open_app", "path": "notepad.exe"}, # Mocking FlexiSIGN with Notepad for safety
                {"type": "type_text", "text": f"Name: {extracted_text}\nSize: {intent_data['params']['size']}"}
            ]
        }
        
        # 4. Send to Local Client via WebSocket
        print("Sending command to local client...")
        socketio.emit('command', command_payload)
        
        return jsonify({
            "status": "success", 
            "response": f"I'm on it. Creating draft for {extracted_text} with size {intent_data['params']['size']}."
        })

    return jsonify({"status": "success", "response": "I heard you, but I don't know how to do that yet."})

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

if __name__ == '__main__':
    # Host 0.0.0.0 allows access from other devices/emulator
    # socketio.run replaces app.run
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
