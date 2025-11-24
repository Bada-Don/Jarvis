import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
LOG_FILE = 'logs.txt'

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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

if __name__ == '__main__':
    # Host 0.0.0.0 allows access from other devices/emulator
    app.run(host='0.0.0.0', port=5000, debug=True)
