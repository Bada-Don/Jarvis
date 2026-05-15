# Firebase Backend Operations

> 37 nodes · cohesion 0.06

## Key Concepts

- **FirebaseService** (16 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **.get_device_info()** (4 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **.is_device_paired()** (4 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **.__init__()** (3 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **.listen_for_status()** (3 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **.mark_command_processed()** (3 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **.cleanup_old_messages()** (3 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **.close()** (3 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **firebase_service.py** (2 connections) — `backend\firebase_service.py`
- **.set_device_id()** (2 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **.register_device()** (2 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **.update_presence()** (2 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **.send_command()** (2 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **.send_status()** (2 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **.listen_for_commands()** (2 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **Firebase Service for JARVIS Backend Handles Firebase Admin SDK initialization, d** (2 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **firebase_service.py** (2 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **Firebase service for backend server.     Manages device authentication, real-tim** (1 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **Initialize Firebase Admin SDK.                  Args:             credentials_pa** (1 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **Set the device ID for this backend instance.                  Args:** (1 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **Register a device in Firebase.                  Args:             device_id: Uni** (1 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **Update device last-seen timestamp.                  Args:             device_id:** (1 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **Send a command to a device.                  Args:             device_id: Target** (1 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **Send a status update to a device.                  Args:             device_id:** (1 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- **Listen for incoming commands for a device.                  Args:             de** (1 connections) — `Jarvis-aws-migration\backend\firebase_service.py`
- *... and 12 more nodes in this community*

## Relationships

- [[Application Launcher & Lifecycle]] (1 shared connections)

## Source Files

- `Jarvis-aws-migration\backend\firebase_service.py`
- `backend\firebase_service.py`

## Audit Trail

- EXTRACTED: 76 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*