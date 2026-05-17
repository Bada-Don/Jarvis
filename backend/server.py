# Eventlet monkey patch MUST be first, before any other imports
import eventlet
eventlet.monkey_patch()

import os
import base64
import json
import time
import subprocess
import socket
import re
import uuid
from importlib import import_module
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add local_client to sys.path for shared modules
_root_dir = Path(__file__).parent.parent
_client_dir = _root_dir / "local_client"
if str(_client_dir) not in sys.path:
    sys.path.insert(0, str(_client_dir))

from newPlanner_service import PlannerService

# ReAct Loop imports
from session_manager import (
    SessionManager,
    Session,
    Exchange,
    SESSION_STATUS_RUNNING,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_ABORTED,
    SESSION_STATUS_WAITING_PERMISSION,
    SESSION_STATUS_WAITING_CLARIFICATION,
)
from step_result import StepResult
from summarization_buffer import SummarizationBuffer
import eventlet
from eventlet.event import Event

# ReAct configuration
REACT_ENABLED = os.getenv('REACT_ENABLED', 'true').lower() == 'true'
STEP_RESULT_TIMEOUT = float(os.getenv('STEP_RESULT_TIMEOUT', '120'))  # seconds to wait for step result
CLARIFICATION_TIMEOUT = float(os.getenv('CLARIFICATION_TIMEOUT', '300'))  # seconds for ask_doubt / clarifications

# Initialize Session Manager
session_manager = SessionManager()

# Initialize Summarization Buffer
summarization_buffer = SummarizationBuffer()

# Pending step result events (session_id -> Event)
_pending_step_results = {}  # {session_id: Event}
_pending_step_data = {}     # {session_id: StepResult dict}

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


# Initialize Firebase Service (optional)
firebase_service = None
firebase_enabled = False
try:
    from firebase_service import FirebaseService
    
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
except Exception as e:
    print(f"⚠ Firebase Service not available: {e}", flush=True)


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
        # Get paired mobile device ID from config
        try:
            from pathlib import Path
            import json
            device_config_path = Path(__file__).parent.parent / 'data' / 'device_config.json'
            if device_config_path.exists():
                with open(device_config_path, 'r') as f:
                    config = json.load(f)
                    paired_mobile_id = config.get('paired_device_id')
                    if paired_mobile_id:
                        # Send command to paired mobile device when the loaded Firebase
                        # implementation supports command publishing.
                        if hasattr(firebase_service, 'send_command'):
                            firebase_service.send_command(paired_mobile_id, command_payload)
                            print(f"📤 Firebase command sent to mobile: {paired_mobile_id}", flush=True)
                        else:
                            print("⚠️ Firebase command publishing not available; WebSocket command already sent", flush=True)
                    else:
                        print(f"⚠️ No paired mobile device ID found", flush=True)
        except Exception as e:
            print(f"⚠️ Error sending Firebase command: {e}", flush=True)


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
        # Get paired mobile device ID from config
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


def _get_observation_module_class():
    """Lazily load ObservationModule only when step observations are processed."""
    return import_module("local_client.observation_module").ObservationModule


def _compact_session_history(session: Session, keep_entries: int = 12) -> None:
    """Keep planner context bounded during repeated ReAct replanning."""
    if not session.current_task_id or session.current_task_id not in session.tasks:
        return

    current_task = session.tasks[session.current_task_id]
    exchanges = current_task["exchanges"]

    if len(exchanges) <= keep_entries:
        return

    # Filter out non-observation exchanges and keep only the last `keep_entries` observations
    observations = [e for e in exchanges if "result" in e]
    if len(observations) <= keep_entries:
        return

    older_observations = observations[:-keep_entries]
    recent_observations = observations[-keep_entries:]
    
    # We also want to keep the very first input (the original user command for the task)
    first_input = next((e for e in exchanges if "input" in e), None)
    
    failures = sum(1 for entry in older_observations if entry["result"].get('success') is False)
    successes = sum(1 for entry in older_observations if entry["result"].get('success') is True)
    
    summary_exchange: Exchange = {
        'exchange_id': f"exch_{uuid.uuid4().hex[:12]}",
        'result': {
            'role': 'observation_summary',
            'content': (
                f"[Compacted {len(older_observations)} older ReAct entries: "
                f"{successes} successful observations, {failures} failures. "
                "Recent entries below contain the actionable state.]"
            ),
            'success': failures == 0
        },
        'timestamp': time.time(),
        'parent_task_id': session.current_task_id
    }
    
    new_exchanges = []
    if first_input:
        new_exchanges.append(first_input)
    new_exchanges.append(summary_exchange)
    
    # Find all non-observation exchanges that happened after the last older observation
    last_older_obs_time = older_observations[-1]["timestamp"] if older_observations else 0
    recent_inputs = [e for e in exchanges if "input" in e and e["timestamp"] > last_older_obs_time and e != first_input]
    
    # Merge recent inputs and recent observations, sorted by timestamp
    remaining_exchanges = sorted(recent_inputs + recent_observations, key=lambda x: x["timestamp"])
    new_exchanges.extend(remaining_exchanges)
    
    current_task["exchanges"] = new_exchanges
    
    # Truncate content of individual exchanges if too long
    for exchange in current_task["exchanges"]:
        if "input" in exchange and isinstance(exchange["input"].get('content'), str) and len(exchange["input"]['content']) > 1000:
            exchange["input"]['content'] = summarization_buffer._truncate_output(exchange["input"]['content'], 1000)
        if "result" in exchange and isinstance(exchange["result"].get('content'), str) and len(exchange["result"]['content']) > 1000:
            exchange["result"]['content'] = summarization_buffer._truncate_output(exchange["result"]['content'], 1000)


def _resolve_runtime_path(value: str) -> str:
    """Resolve planner placeholders and environment variables in a local path."""
    if not isinstance(value, str):
        return value

    resolved = os.path.expandvars(value)
    config = getattr(planner_service, 'config', {}) if planner_service else {}
    home = Path.home()
    one_drive = os.environ.get("OneDrive") or os.environ.get("OneDriveConsumer")
    desktop = config.get('DESKTOP_PATH') or os.environ.get('DESKTOP_PATH')
    if (not desktop or desktop.endswith(r'\user\Desktop')) and one_drive and (Path(one_drive) / "Desktop").exists():
        desktop = str(Path(one_drive) / "Desktop")
    if not desktop:
        desktop = str(home / "Desktop")

    replacements = {
        **{k: str(v) for k, v in config.items()},
        "DESKTOP_PATH": desktop,
        "DOCUMENTS_PATH": config.get('DOCUMENTS_PATH') or os.environ.get('DOCUMENTS_PATH', str(home / "Documents")),
        "DOWNLOADS_PATH": config.get('DOWNLOADS_PATH') or os.environ.get('DOWNLOADS_PATH', str(home / "Downloads")),
        "WINDOWS_USERNAME": config.get('WINDOWS_USERNAME') or os.environ.get("USERNAME", home.name),
        "USERPROFILE": os.environ.get("USERPROFILE", str(home)),
    }
    for key, path_value in replacements.items():
        resolved = resolved.replace(f"{{{key}}}", str(path_value))
    return resolved


def _extract_command_paths(command: str, keyword_pattern: str) -> list[str]:
    """Extract quoted or simple bare paths following a Windows command keyword."""
    paths = []
    pattern = rf"(?:^|[&|]\s*){keyword_pattern}\s+(?:\"([^\"]+)\"|([^&|>\r\n]+))"
    for match in re.finditer(pattern, command, flags=re.IGNORECASE):
        path = (match.group(1) or match.group(2) or "").strip()
        if path:
            paths.append(_resolve_runtime_path(path))
    return paths


def _extract_redirect_paths(command: str) -> list[str]:
    """Extract likely output file paths from shell redirections."""
    paths = []
    for match in re.finditer(r">\s*(?:\"([^\"]+)\"|([^&|>\r\n]+))", command, flags=re.IGNORECASE):
        path = (match.group(1) or match.group(2) or "").strip()
        if path:
            paths.append(_resolve_runtime_path(path))
    return paths


def _looks_open_in_explorer(path: str, step_results: list[dict]) -> bool:
    """Best-effort check that Explorer opened the expected folder."""
    if not os.path.exists(path):
        return False
    expected_name = os.path.basename(os.path.normpath(path)).lower()
    for result in reversed(step_results):
        active_window = (result.get('active_window') or '').lower()
        foreground_app = (result.get('foreground_app') or '').lower()
        observation = f"{result.get('observation') or ''} {result.get('raw_observation') or ''}".lower()
        if expected_name and expected_name in active_window:
            return True
        if 'explorer opened' in observation and (not expected_name or expected_name in observation):
            return True
        if 'explorer' in foreground_app and (not expected_name or expected_name in observation):
            return True
    return False


def _check_expected_observation(plan_data: dict, sequence: list[dict], step_results: list[dict]) -> dict:
    """
    Compare the actual post-batch state with expected_observation.

    Deterministic filesystem checks are authoritative. Text overlap is used only
    as a fallback for UI-oriented expectations where no local state probe exists.
    """
    expected = (plan_data.get('expected_observation') or '').strip()
    if not expected:
        return {'matched': True, 'confidence': 'none', 'message': 'No expected_observation provided.'}

    checks = []

    def add_check(label: str, ok: bool, strength: str = "strong"):
        checks.append({'label': label, 'ok': ok, 'strength': strength})
    for step in sequence:
        step_type = (step.get('type') or '').lower()

        if step_type == 'create_directory':
            path = _resolve_runtime_path(step.get('path', ''))
            if path:
                add_check(f"directory exists: {path}", os.path.isdir(path))

        elif step_type in ('path_exists', 'directory_exists'):
            path = _resolve_runtime_path(step.get('path', ''))
            if path:
                if step_type == 'directory_exists':
                    add_check(f"directory exists: {path}", os.path.isdir(path))
                else:
                    add_check(f"path exists: {path}", os.path.exists(path))

        elif step_type == 'write_file':
            path = _resolve_runtime_path(step.get('path', ''))
            if path:
                exists = os.path.isfile(path)
                add_check(f"file exists: {path}", exists)
                content = step.get('content')
                if exists and isinstance(content, str) and content:
                    try:
                        actual = Path(path).read_text(encoding='utf-8', errors='ignore')
                        add_check(f"file contains requested content: {path}", content in actual)
                    except Exception:
                        add_check(f"file readable: {path}", False)

        elif step_type == 'open_folder':
            path = _resolve_runtime_path(step.get('path', ''))
            if path:
                add_check(f"folder exists: {path}", os.path.isdir(path))
                add_check(f"folder appears in Explorer: {path}", _looks_open_in_explorer(path, step_results), "weak")

        elif step_type == 'open_file':
            path = _resolve_runtime_path(step.get('path', ''))
            if path:
                add_check(f"file exists before open: {path}", os.path.isfile(path))

        elif step_type == 'read_file':
            path = _resolve_runtime_path(step.get('path', ''))
            if path:
                if os.path.isdir(path):
                    add_check(f"directory exists: {path}", True)
                else:
                    add_check(f"file exists/readable: {path}", os.path.isfile(path))

        elif step_type in ('word_docs', 'ai_edit_word', 'file_reading', 'pdf_handling',
                           'spreadsheets', 'ai_edit_excel'):
            # Document skill: verify the source file exists and was readable.
            # The actual content extraction is confirmed by the step success flag;
            # we add only a weak check here so a missing source file is caught
            # deterministically, but the planner's vague expected_observation text
            # doesn't cause a false failure when the step succeeded.
            path = _resolve_runtime_path(step.get('path', ''))
            if path:
                add_check(f"document exists: {path}", os.path.isfile(path), "weak")

        elif step_type == 'shell_command':
            command = _resolve_runtime_path(step.get('command', ''))
            for path in _extract_command_paths(command, r"(?:mkdir|md)"):
                add_check(f"directory exists: {path}", os.path.isdir(path))
            for path in _extract_redirect_paths(command):
                add_check(f"file exists: {path}", os.path.isfile(path))
            explorer_paths = _extract_command_paths(command, r"explorer(?:\.exe)?")
            for path in explorer_paths:
                add_check(f"folder exists for Explorer: {path}", os.path.isdir(path))
                add_check(f"Explorer opened/accessed: {path}", _looks_open_in_explorer(path, step_results), "weak")

    if checks:
        strong_failed = [check['label'] for check in checks if not check['ok'] and check['strength'] == 'strong']
        weak_failed = [check['label'] for check in checks if not check['ok'] and check['strength'] == 'weak']
        if strong_failed:
            return {
                'matched': False,
                'confidence': 'deterministic',
                'severity': 'strong',
                'message': "Expected observation not met: " + "; ".join(strong_failed)
            }
        if weak_failed:
            return {
                'matched': True,
                'confidence': 'weak',
                'severity': 'weak',
                'message': "Core state is correct; weak UI signals were missing: " + "; ".join(weak_failed)
            }
        return {
            'matched': True,
            'confidence': 'deterministic',
            'severity': 'strong',
            'message': "Expected observation matched by deterministic checks."
        }

    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'to', 'in', 'on', 'with', 'after',
        'showing', 'visible', 'will', 'be', 'is', 'are', 'step', 'success',
        'successfully', 'window', 'folder', 'file', 'files', 'folders',
        'list', 'listing', 'show', 'showing', 'find', 'finding', 'detailed',
        'details', 'detail', 'full', 'path', 'paths', 'information', 'info',
        'present', 'analyze', 'including', 'length', 'lengths', 'time', 'times',
        'name', 'names'
    }
    expected_tokens = {
        token for token in re.findall(r"[a-z0-9_]+", expected.lower())
        if len(token) > 2 and token not in stop_words
    }
    actual_text = " ".join(
        str(result.get(key, ''))
        for result in step_results
        for key in ('observation', 'raw_observation', 'stdout', 'stderr', 'active_window', 'foreground_app')
    ).lower()

    if not expected_tokens:
        return {'matched': True, 'confidence': 'text', 'message': 'Expected observation had no concrete tokens to compare.'}

    matched_tokens = {token for token in expected_tokens if token in actual_text}
    
    # Use a lower threshold (30%) when the batch actually succeeded.
    # If the output was truncated, be even more lenient (10%).
    any_step_succeeded = any(r.get('success') for r in step_results)
    is_truncated = "[output truncated]" in actual_text
    
    threshold = 0.3 if any_step_succeeded else 0.5
    if is_truncated:
        threshold = 0.1

    required = max(1, min(len(expected_tokens), round(len(expected_tokens) * threshold)))
    if len(matched_tokens) >= required:
        return {'matched': True, 'confidence': 'text', 'message': 'Expected observation matched by text overlap.'}

    missing = sorted(expected_tokens - matched_tokens)
    # If we have NO matches at all, or we are missing critical tokens, it's a STRONG failure.
    # Otherwise, it's weak (might just be a slightly different window title).
    match_rate = len(matched_tokens) / len(expected_tokens)
    severity = 'strong' if match_rate < 0.2 and not is_truncated else 'weak'

    return {
        'matched': False,
        'confidence': 'text',
        'severity': severity,
        'message': f"Actual observation did not match expected_observation. Missing signals: {', '.join(missing[:8])}"
    }


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
    
    If REACT_ENABLED: Uses ReAct loop (Think-Act-Observe)
    Otherwise: Uses legacy single-pass Plan-then-Execute
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
    
    # Check if ReAct mode is requested
    use_react = REACT_ENABLED and data.get('react', True)
    
    if use_react:
        return _process_react(text)
    else:
        return _process_legacy(text)


def _process_legacy(text: str):
    """Legacy single-pass Plan-then-Execute (original behavior)."""
    try:
        send_status_dual({'message': 'Processing your request...', 'status': 'running', 'progress': 5})
        
        # Create a session for legacy mode as well, to track the initial command
        session = session_manager.create_session(user_command=text)
        
        print("🤖 Calling Planner Model (legacy mode)...")
        plan = planner_service.generate_plan(session, text)
        mode = plan.get('mode', 'general')
        step_count = len(plan.get('sequence', []))
        print(f"✓ Plan generated: {step_count} steps (mode: {mode})")
        
        send_status_dual({'message': f'Plan ready ({step_count} steps), sending to executor...', 'status': 'running', 'progress': 20})
        
        command_payload = {
            "action": "execute_plan",
            "plan": plan,
            "user_command": text,
            "mode": mode,
            "session_id": session.session_id # Pass session_id for client tracking
        }
        
        print(f"📤 Sending execute_plan command (mode: {mode})...")
        send_command_dual(command_payload)
        
        return jsonify({"status": "success", "response": f"Processing: {text}", "mode": mode, "plan_steps": step_count})
        
    except ValueError as e:
        import traceback
        error_msg = f"Failed to generate plan: {e}"
        print(f"✗ {error_msg}", flush=True)
        send_status_dual({'message': error_msg, 'status': 'error', 'error': str(e)})
        return jsonify({"status": "error", "response": "Sorry, I couldn't understand that command.", "error_type": "ValueError"}), 500
    except Exception as e:
        import traceback
        error_msg = f"Error processing request: {e}"
        print(f"✗ {error_msg}", flush=True)
        send_status_dual({'message': 'An error occurred.', 'status': 'error', 'error': str(e)})
        return jsonify({"status": "error", "response": "An error occurred.", "error_type": type(e).__name__}), 500


def _process_react(text: str):
    """
    ReAct Loop entry point.
    Creates a session and spawns the Think-Act-Observe loop in a greenlet.
    """
    try:
        # Create session
        session = session_manager.create_session(user_command=text)
        session.create_task(user_command=text)
        session.add_thought(f"User request: {text}")
        
        # Route the command to determine mode and modules
        route_data = planner_service.route_command(text)
        session.mode = route_data.get('mode', 'general')
        session.route_data = route_data
        session_manager.update_session(session)
        
        send_status_dual({
            'message': 'Starting ReAct session...',
            'status': 'running',
            'progress': 5,
            'session_id': session.session_id
        })
        
        # Spawn the ReAct loop in an eventlet greenlet
        eventlet.spawn_n(_react_loop, session.session_id)
        
        return jsonify({
            "status": "success",
            "response": f"Processing (ReAct): {text}",
            "mode": session.mode,
            "session_id": session.session_id
        })
        
    except Exception as e:
        import traceback
        error_msg = f"Error starting ReAct session: {e}"
        print(f"✗ {error_msg}", flush=True)
        print(f"✗ {traceback.format_exc()}", flush=True)
        return jsonify({"status": "error", "response": str(e), "error_type": type(e).__name__}), 500


def _react_loop(session_id: str):
    """
    The core ReAct loop: Think → Act → Observe → Reflect.
    Runs in an eventlet greenlet.
    """
    session = session_manager.get_session(session_id)
    if not session:
        print(f"✗ Session {session_id} not found")
        return
    
    try:
        while not session.is_terminal():
            _compact_session_history(session)
            session_manager.update_session(session)

            # === THINK: Generate next 1-3 steps ===
            try:
                plan_data = planner_service.generate_next_steps(session)
            except Exception as e:
                print(f"✗ Planner error in session {session_id}: {e}")
                session.add_error(f"Planner failed: {str(e)}")
                session.status = SESSION_STATUS_FAILED
                session_manager.update_session(session)
                send_status_dual({'message': f'Planner error: {e}', 'status': 'error', 'session_id': session_id})
                return

            session.current_plan = plan_data
            sequence = plan_data.get('sequence', [])
            is_complete = plan_data.get('is_complete', False)
            expected_observation = plan_data.get('expected_observation', '')
            usage = plan_data.get('usage')

            # If planner signals completion with no steps, verify and exit
            if is_complete and not sequence:
                session.add_thought("Planner signals task is complete. Verifying...", usage=usage)
                _verify_and_complete(session)
                return

            if not sequence:
                print(f"⚠️ Empty sequence from planner in session {session_id}")
                session.add_error("Planner returned empty sequence", usage=usage)
                session.status = SESSION_STATUS_FAILED
                session_manager.update_session(session)
                return

            # Log the plan
            session.add_thought(f"Planned {len(sequence)} steps: {[s.get('desc', s.get('type')) for s in sequence]}", usage=usage)            
            # === ACT + OBSERVE: Execute each step ===
            batch_step_results = []
            for step in sequence:
                if session.status in [SESSION_STATUS_ABORTED, SESSION_STATUS_WAITING_PERMISSION]:
                    break
                
                # Check for high-risk operations (HIL gating)
                if _is_high_risk_step(step):
                    permission_granted = _request_permission(session, step)
                    if not permission_granted:
                        session.add_observation(f"Permission denied for: {step.get('desc', step.get('type'))}", success=False)
                        # Re-plan with the denial as context
                        break
                
                # Check for "ask_doubt" step type
                if step.get('type') == 'ask_doubt':
                    question = step.get('question', 'Please clarify')
                    options = step.get('options')
                    is_multiselect = step.get('is_multiselect', False)

                    auto_answer = _maybe_auto_resolve_ask_doubt(session, step)
                    if auto_answer:
                        session.add_thought(
                            f"Listing already shows target file '{auto_answer}'; skipping user prompt."
                        )
                        answer = auto_answer
                    else:
                        answer = _request_clarification(session, question, options, is_multiselect)

                    session.add_user_response(answer)
                    break  # Re-plan with the answer
                
                # Send step to client
                session.add_action(step)
                session_manager.update_session(session)
                
                progress = min(10 + (session.steps_executed * 10), 90)
                send_status_dual({
                    'message': f'Step {step.get("order", "?")}: {step.get("desc", step.get("type"))}',
                    'status': 'running',
                    'progress': progress,
                    'session_id': session_id
                })
                
                # Create event for step result
                step_event = Event()
                _pending_step_results[session_id] = step_event
                
                # Send step to client
                command_payload = {
                    "action": "execute_step",
                    "step": step,
                    "session_id": session_id,
                    "mode": session.mode,
                    "user_command": session.user_command
                }
                send_command_dual(command_payload)
                
                # === OBSERVE: Wait for step result ===
                try:
                    step_event.wait(timeout=STEP_RESULT_TIMEOUT)
                except Exception:
                    pass  # Timeout handled below
                
                # Get the result
                step_result_dict = _pending_step_data.pop(session_id, None)
                _pending_step_results.pop(session_id, None)
                
                if step_result_dict is None:
                    # Timeout - no response from client
                    step_result_dict = {
                        'session_id': session_id,
                        'step_order': step.get('order', 0),
                        'step_type': step.get('type', ''),
                        'success': False,
                        'stdout': '',
                        'stderr': 'Timeout: No response from client',
                        'active_window': '',
                        'error_message': 'Step execution timed out',
                        'observation': 'Client did not respond within timeout period'
                    }
                
                step_result = StepResult.from_dict(step_result_dict)
                session.add_step_result(step_result_dict)
                batch_step_results.append(step_result_dict)
                
                # Process the observation
                ObservationModule = _get_observation_module_class()
                obs_module = ObservationModule()
                observation_text = obs_module.build_observation_text(step_result_dict)
                
                # Summarize long outputs
                if step_result_dict.get('stdout'):
                    step_result_dict['stdout'] = summarization_buffer.process_output(
                        step_result_dict['stdout'], is_error=False
                    )
                if step_result_dict.get('stderr'):
                    step_result_dict['stderr'] = summarization_buffer.process_output(
                        step_result_dict['stderr'], is_error=True
                    )
                
                if step_result.success:
                    session.add_observation(observation_text, success=True, usage=step_result.usage)
                else:
                    # === REFLECT: Step failed ===
                    session.add_error(step_result.get_error_context(), usage=step_result.usage)
                    
                    if session.can_retry():
                        session.add_thought("Step failed. Re-planning with error context...")
                        send_status_dual({
                            'message': f'Step failed, re-planning (attempt {session.reflection_retries}/{session.max_reflection_retries})...',
                            'status': 'warning',
                            'progress': progress,
                            'session_id': session_id
                        })
                    else:
                        # Max retries exhausted
                        session.status = SESSION_STATUS_FAILED
                        session_manager.update_session(session)
                        send_status_dual({
                            'message': f'Task failed after {session.reflection_retries} retries',
                            'status': 'error',
                            'session_id': session_id
                        })
                        return
                    
                    break  # Break inner loop to re-plan
                
                session_manager.update_session(session)
            else:
                # The full planned batch ran without a step-level failure. Now check
                # the planner's expected post-batch state to catch silent failures.
                expectation_result = _check_expected_observation(plan_data, sequence, batch_step_results)
                if expectation_result.get('matched'):
                    if expected_observation:
                        session.add_observation(
                            f"Expected observation check passed ({expectation_result.get('confidence')}): "
                            f"{expected_observation}",
                            success=True
                        )
                        session_manager.update_session(session)
                else:
                    mismatch = expectation_result.get('message', 'Expected observation was not met.')
                    # Only ignore weak mismatches if we have SOME confidence or if it's a non-critical step
                    # In practice, 'weak' should only be used for minor UI differences.
                    if expectation_result.get('severity') == 'weak' and expectation_result.get('confidence') != 'text':
                        session.add_observation(
                            f"Weak expected_observation mismatch ignored after successful execution. "
                            f"Expected: {expected_observation} | {mismatch}",
                            success=True
                        )
                        session_manager.update_session(session)
                        send_status_dual({
                            'message': 'Execution succeeded; minor observation mismatch ignored',
                            'status': 'warning',
                            'progress': min(10 + (session.steps_executed * 10), 90),
                            'session_id': session_id
                        })
                        continue

                    session.add_error(
                        f"Silent success check failed. Expected: {expected_observation} | {mismatch}"
                    )
                    session_manager.update_session(session)

                    if session.can_retry():
                        send_status_dual({
                            'message': f'Expected observation mismatch, re-planning (attempt {session.reflection_retries}/{session.max_reflection_retries})...',
                            'status': 'warning',
                            'progress': min(10 + (session.steps_executed * 10), 90),
                            'session_id': session_id
                        })
                        continue

                    session.status = SESSION_STATUS_FAILED
                    session_manager.update_session(session)
                    send_status_dual({
                        'message': 'Task failed: expected observation was not met',
                        'status': 'error',
                        'session_id': session_id
                    })
                    return
            
            # If all steps in this batch succeeded, continue the loop
            # The next iteration will call generate_next_steps again
        
        # Loop exited - session should be in terminal state
        if session.status == SESSION_STATUS_RUNNING:
            # Safety: verify and complete if still running
            _verify_and_complete(session)
    
    except Exception as e:
        import traceback
        print(f"✗ ReAct loop error for session {session_id}: {e}")
        print(f"✗ {traceback.format_exc()}")
        session.status = SESSION_STATUS_FAILED
        session_manager.update_session(session)
        send_status_dual({'message': f'ReAct loop error: {e}', 'status': 'error', 'session_id': session_id})


def _verify_and_complete(session: Session):
    """Send verification command to client and finalize session."""
    expected_state = ""
    if session.current_plan:
        expected_state = session.current_plan.get('expected_final_state', '')

    # expected_observation is already checked inside the ReAct loop. Do not send
    # it to visual verification, because that turns weak observation text into a
    # hard failure and causes needless replanning.
    if not expected_state:
        session.status = SESSION_STATUS_COMPLETED
        session.add_observation("Task complete; no separate final visual verification requested.", success=True)
        session_manager.update_session(session)
        send_status_dual({
            'message': 'Task completed!',
            'status': 'success',
            'progress': 100,
            'session_id': session.session_id
        })
        return
    
    if expected_state:
        # Send verification command
        step_event = Event()
        _pending_step_results[session.session_id] = step_event
        
        send_command_dual({
            "action": "verify_task",
            "session_id": session.session_id,
            "expected_state": expected_state
        })
        
        try:
            step_event.wait(timeout=30)
            result = _pending_step_data.pop(session.session_id, None)
            _pending_step_results.pop(session.session_id, None)
            
            if result and result.get('success'):
                session.status = SESSION_STATUS_COMPLETED
                session.add_observation("Verification passed: task completed successfully", success=True)
            else:
                observation = result.get('observation', 'unknown') if result else 'no verification result'
                session.add_observation(f"Verification failed: {observation}", success=False)
                if session.can_retry():
                    session.add_thought("Verification failed. Re-planning corrective actions...")
                    # Will continue in the loop
                    session_manager.update_session(session)
                    return
                else:
                    session.status = SESSION_STATUS_FAILED
        except Exception:
            session.status = SESSION_STATUS_COMPLETED  # Assume success if verification times out
    else:
        session.status = SESSION_STATUS_COMPLETED
    
    session_manager.update_session(session)
    
    if session.status == SESSION_STATUS_COMPLETED:
        send_status_dual({
            'message': 'Task completed and verified!',
            'status': 'success',
            'progress': 100,
            'session_id': session.session_id
        })
    else:
        send_status_dual({
            'message': 'Task failed after verification',
            'status': 'error',
            'session_id': session.session_id
        })


def _collect_session_listing_filenames(session: Session) -> List[str]:
    """Gather filenames from execution log stdout and planner observation history."""
    from listing_context import collect_filenames_from_texts

    texts: List[str] = []
    for entry in session.execution_log:
        texts.append(entry.get('stdout') or '')
        texts.append(entry.get('observation') or '')
        texts.append(entry.get('terminal_snapshot') or '')

    if session.current_task_id and session.current_task_id in session.tasks:
        for exchange in session.tasks[session.current_task_id].get('exchanges', []):
            result = exchange.get('result') or {}
            if result.get('role') == 'observation':
                texts.append(result.get('content') or '')

    return collect_filenames_from_texts(texts)


def _maybe_auto_resolve_ask_doubt(session: Session, step: dict) -> Optional[str]:
    """Skip mobile clarification when a recent listing already names the file."""
    from listing_context import try_resolve_ask_doubt

    question = step.get('question', '')
    filenames = _collect_session_listing_filenames(session)
    return try_resolve_ask_doubt(question, session.user_command, filenames)


def _request_clarification(
    session: Session,
    question: str,
    options: Optional[List[Dict[str, Any]]] = None,
    is_multiselect: bool = False,
) -> str:
    """
    Ask the user (mobile app) for clarification while pausing the ReAct loop.

    Uses pending key ask_{session_id} so this never collides with step_result /
    verification_result waiters that use session_id.
    """
    session_id = session.session_id
    ask_key = f"ask_{session_id}"
    step_event = Event()
    _pending_step_results[ask_key] = step_event

    session.status = SESSION_STATUS_WAITING_CLARIFICATION
    session_manager.update_session(session)

    progress = min(10 + (session.steps_executed * 10), 90)
    send_status_dual({
        'type': 'REQUEST_CLARIFICATION',
        'session_id': session_id,
        'question': question,
        'options': options,
        'is_multiselect': is_multiselect,
        'status': 'running',
        'progress': progress,
    })

    try:
        step_event.wait(timeout=CLARIFICATION_TIMEOUT)
        result = _pending_step_data.pop(ask_key, None)
        if result:
            text = (result.get('response') or result.get('answer') or '').strip()
            if text:
                return text
        return "User provided no response or response timed out."
    except Exception:
        return "User provided no response or response timed out."
    finally:
        _pending_step_results.pop(ask_key, None)
        session.status = SESSION_STATUS_RUNNING
        session_manager.update_session(session)


# Read-only / low-impact shell — never gate behind REQUEST_PERMISSION
_SAFE_SHELL_MARKERS = (
    'get-childitem', 'get-item', 'get-content', 'get-location',
    'test-path', 'resolve-path', 'split-path', 'join-path',
    'dir ', 'dir\t', 'ls ', 'pwd', 'cd ', 'set-location',
    'explorer ', 'start explorer', 'ii ', 'invoke-item ',
    'type ', 'cat ', 'more ', 'head ', 'tail ',
    'echo ', 'write-output', 'out-null',
    'format-list', 'format-table', 'select-object', 'where-object',
    'mkdir ', 'md ', 'new-item',  # folder create on user paths is routine
)
# Disk-format style commands only (NOT PowerShell Format-List / Format-Table)
_DISK_FORMAT_RE = re.compile(
    r'\bformat\s+([a-z]:|/|\?|volume\b)',
    re.IGNORECASE,
)


def _is_safe_shell_command(command: str) -> bool:
    """True when a shell_command is read-only listing/navigation (no permission prompt)."""
    if not command:
        return False
    cmd = command.strip().lower()
    if any(marker in cmd for marker in _SAFE_SHELL_MARKERS):
        return True
    # Bare dir / ls at end of pipeline
    if re.match(r'^(dir|ls|gci|get-childitem)\b', cmd):
        return True
    return False


def _is_high_risk_step(step: dict) -> bool:
    """Check if a step is high-risk and requires human permission."""
    step_type = step.get('type', '').lower()
    step_value = step.get('value', '').lower() if step.get('value') else ''
    step_command = step.get('command', '').lower() if step.get('command') else ''
    step_path = step.get('path', '').lower() if step.get('path') else ''

    # High-risk step types
    if step_type in ('delete_file', 'delete_folder'):
        return True

    if step_type == 'shell_command':
        if _is_safe_shell_command(step_command):
            return False

        high_risk_patterns = [
            'del /s', 'del /q', 'rmdir /s', 'rmdir /q', 'rm -rf',
            'remove-item -recurse', 'remove-item -force',
            'shutdown', 'regedit', 'reg delete',
            'rd /s', 'rd /q',
            'cipher /w', 'diskpart',
        ]
        for pattern in high_risk_patterns:
            if pattern in step_command or pattern in step_value:
                return True

        if _DISK_FORMAT_RE.search(step_command) or _DISK_FORMAT_RE.search(step_value):
            return True

        # Destructive Remove-Item (without safe listing context)
        if re.search(r'\bremove-item\b.*\b(-recurse|-force)\b', step_command):
            return True
        if re.search(r'\bdel\b', step_command) and '/s' not in step_command:
            # bare del can still delete files
            if not _is_safe_shell_command(step_command):
                if re.search(r'\bdel\s+', step_command):
                    return True

    # System directory targets (writes/deletes into protected areas)
    system_dirs = ['c:\\windows', 'c:\\program files', 'c:\\system32']
    combined = f"{step_command} {step_value} {step_path}"
    for d in system_dirs:
        if d in combined:
            # Allow read-only listing under system dirs? Still risky — keep gated.
            if step_type == 'shell_command' and _is_safe_shell_command(step_command):
                continue
            return True

    return False


def _request_permission(session: Session, step: dict) -> bool:
    """
    Request human permission for a high-risk step.
    Sends REQUEST_PERMISSION event to mobile app and waits.
    """
    print(f"🔐 WAITING FOR PERMISSION: {step.get('desc', step.get('type'))} (Session: {session.session_id})")
    print(f"   Details: {step.get('value', step.get('command', step.get('path', 'N/A')))}")
    
    session.status = SESSION_STATUS_WAITING_PERMISSION
    session_manager.update_session(session)
    
    permission_event = Event()
    _pending_step_results[f"perm_{session.session_id}"] = permission_event
    
    send_status_dual({
        'type': 'REQUEST_PERMISSION',
        'session_id': session.session_id,
        'operation': step.get('desc', step.get('type')),
        'details': f"Step: {step.get('type')} | Value: {step.get('value', step.get('command', step.get('path', 'N/A')))}",
        'risk_level': 'high'
    })
    
    # Wait for permission response (up to 120 seconds)
    try:
        print(f"⏳ Waiting up to 120s for user response...")
        permission_event.wait(timeout=120)
        
        result = _pending_step_data.pop(f"perm_{session.session_id}", None)
        _pending_step_results.pop(f"perm_{session.session_id}", None)
        
        session.status = SESSION_STATUS_RUNNING
        session_manager.update_session(session)
        
        if result and result.get('approved'):
            print(f"✅ PERMISSION GRANTED for session {session.session_id}")
            return True
        else:
            print(f"❌ PERMISSION DENIED or TIMEOUT for session {session.session_id}")
    except Exception as e:
        print(f"❌ Error waiting for permission: {e}")
    
    session.status = SESSION_STATUS_RUNNING
    session_manager.update_session(session)
    return False


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


@socketio.on('step_result')
def handle_step_result(data):
    """Receive step execution result from local client."""
    session_id = data.get('session_id')
    success = data.get('success', False)
    step_type = data.get('step_type', 'unknown')
    
    print(f"📊 Step result for session {session_id}: {step_type} {'✓' if success else '✗'}")
    
    # Store the result and signal the waiting event
    if session_id in _pending_step_results:
        _pending_step_data[session_id] = data
        _pending_step_results[session_id].send(True)
    
    # Also forward status to mobile app
    send_status_dual({
        'message': data.get('observation', f"Step {'succeeded' if success else 'failed'}"),
        'status': 'success' if success else 'error',
        'session_id': session_id,
        'step_type': step_type
    })


@socketio.on('verification_result')
def handle_verification_result(data):
    """Receive verification result from local client."""
    session_id = data.get('session_id')
    success = data.get('success', False)
    
    print(f"✅ Verification result for session {session_id}: {'PASSED' if success else 'FAILED'}")
    
    if session_id in _pending_step_results:
        _pending_step_data[session_id] = data
        _pending_step_results[session_id].send(True)


@socketio.on('permission_response_react')
def handle_permission_response_react(data):
    """Handle permission response for ReAct loop (separate from legacy permission flow)."""
    session_id = data.get('session_id')
    approved = data.get('approved', False)
    
    print(f"🔐 ReAct permission response for {session_id}: {'APPROVED' if approved else 'DENIED'}")
    
    perm_key = f"perm_{session_id}"
    if perm_key in _pending_step_results:
        _pending_step_data[perm_key] = {'approved': approved}
        _pending_step_results[perm_key].send(True)


@socketio.on('clarification_response')
def handle_clarification_response(data):
    """Handle clarification response from mobile app (ask_doubt / REQUEST_CLARIFICATION)."""
    session_id = data.get('session_id')
    answer = data.get('answer') or data.get('response') or ''

    print(f"💬 Clarification response for {session_id}: {answer[:100]}")

    ask_key = f"ask_{session_id}"
    if ask_key in _pending_step_results:
        _pending_step_data[ask_key] = {'response': answer}
        _pending_step_results[ask_key].send(True)


def start_omni_server():
    """
    Check if the OmniParser Vision Server is running on port 8000.
    If not, start it as a background process.
    """
    omni_port = 8000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        is_running = s.connect_ex(('127.0.0.1', omni_port)) == 0
    
    if is_running:
        print(f"✓ OmniParser Vision Server is already running on port {omni_port}", flush=True)
        return

    print("🚀 Starting OmniParser Vision Server...", flush=True)
    try:
        from pathlib import Path
        omni_script = Path(__file__).parent / "omni_server.py"
        
        if not omni_script.exists():
            print(f"⚠ Could not find {omni_script}. OmniParser will not be auto-started.", flush=True)
            return

        # Start as a subprocess
        # Use CREATE_NEW_PROCESS_GROUP on Windows to ensure signals are handled correctly
        creation_flags = 0
        if os.name == 'nt':
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

        # Redirect output to log file
        log_dir = Path(__file__).parent.parent / 'data' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'omni_server_auto.log'
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n--- Starting OmniParser at {datetime.now()} ---\n")
            subprocess.Popen(
                [import_sys.executable if 'import_sys' in globals() else "python", str(omni_script)],
                cwd=str(Path(__file__).parent),
                stdout=f,
                stderr=f,
                creationflags=creation_flags
            )
        
        print(f"✓ OmniParser Vision Server started (Logging to {log_file})", flush=True)
    except Exception as e:
        print(f"⚠ Failed to start OmniParser Vision Server: {e}", flush=True)


if __name__ == '__main__':
    # Try to import sys for the executable path
    import sys as import_sys
    
    print("=" * 50, flush=True)
    print("🤖 JARVIS Backend Server Starting...", flush=True)
    print("=" * 50, flush=True)
    
    # Auto-start OmniParser dependency
    start_omni_server()
    
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=False,
        use_reloader=False,
        log_output=True
    )
