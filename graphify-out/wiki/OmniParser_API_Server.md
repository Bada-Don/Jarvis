# OmniParser API Server

> 6 nodes · cohesion 0.33

## Key Concepts

- **omni_server.py** (3 connections) — `backend\omni_server.py`
- **detect()** (2 connections) — `backend\omni_server.py`
- **health()** (2 connections) — `backend\omni_server.py`
- **OmniParser API Server Persistent Flask server wrapping the YOLO icon_detect mode** (1 connections) — `backend\omni_server.py`
- **Accept a screenshot image (multipart/form-data, field name 'file'),     run YOLO** (1 connections) — `backend\omni_server.py`
- **Simple health check so the launcher can verify the server is up.** (1 connections) — `backend\omni_server.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `backend\omni_server.py`

## Audit Trail

- EXTRACTED: 10 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*