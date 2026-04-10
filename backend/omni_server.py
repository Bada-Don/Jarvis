"""
OmniParser API Server
Persistent Flask server wrapping the YOLO icon_detect model for fast UI element detection.

Architecture:
 - Model is loaded ONCE on startup and kept in GPU memory.
 - GPU warmup is performed so the first real request is also fast.
 - POST /detect  → accepts a multipart image, returns JSON bounding boxes.

Why Flask instead of FastAPI:
 - Flask is already a project dependency (used by backend/server.py).
 - No additional ASGI/uvicorn dependency needed.
"""

import io
import time
from pathlib import Path

import cv2
import numpy as np
import torch
from flask import Flask, request, jsonify
from ultralytics import YOLO

# ─────────────────────────────────────────────
#  Configuration
# ─────────────────────────────────────────────
PORT = 8000
MODEL_PATH = Path(__file__).parent / "weights" / "icon_detect" / "model.pt"

# Inference settings (tuned from reference implementation)
CONF_THRESHOLD = 0.2
IOU_THRESHOLD = 0.5
IMG_SIZE = 960        # Sweet spot between accuracy and speed

# ─────────────────────────────────────────────
#  Model Loading & GPU Warmup
# ─────────────────────────────────────────────
app = Flask(__name__)

print(f"[OmniServer] Loading YOLO model from: {MODEL_PATH}")
if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"OmniParser model not found at {MODEL_PATH}. "
        "Expected: backend/weights/icon_detect/model.pt"
    )

model = YOLO(str(MODEL_PATH))

if torch.cuda.is_available():
    model.to("cuda")
    device_name = torch.cuda.get_device_name(0)
    print(f"[OmniServer] 🔥 Running on CUDA: {device_name}")
else:
    print("[OmniServer] ⚠️  CUDA not available — running on CPU (inference will be slower)")

# Warmup: run a dummy forward pass so PyTorch initialises its memory allocator.
# This ensures the FIRST real request is also fast.
print("[OmniServer] Warming up GPU...")
_dummy = np.zeros((IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)
model(_dummy, imgsz=IMG_SIZE, verbose=False)
print("[OmniServer] ✅ Server is READY — awaiting requests on port", PORT)


# ─────────────────────────────────────────────
#  Endpoint: POST /detect
# ─────────────────────────────────────────────
@app.route("/detect", methods=["POST"])
def detect():
    """
    Accept a screenshot image (multipart/form-data, field name 'file'),
    run YOLO inference, and return raw bounding boxes as JSON.

    The client is responsible for:
      - Filtering noisy/huge boxes
      - Drawing the red SoM annotations on the image

    Returns:
        {
            "count": <int>,
            "boxes": [[x1, y1, x2, y2], ...],   # float pixel coordinates
            "timing": {
                "image_read_ms": <float>,
                "ai_inference_ms": <float>
            }
        }
    """
    t0 = time.time()

    # ── 1. Read uploaded image from request ──────────────────────────────────
    if "file" not in request.files:
        return jsonify({"error": "No 'file' field in request"}), 400

    file_bytes = request.files["file"].read()
    nparr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return jsonify({"error": "Could not decode image"}), 400

    t1 = time.time()

    # ── 2. Run YOLO inference ────────────────────────────────────────────────
    results = model(
        image,
        conf=CONF_THRESHOLD,
        iou=IOU_THRESHOLD,
        imgsz=IMG_SIZE,
        verbose=False
    )

    boxes = (
        results[0].boxes.xyxy.cpu().numpy().tolist()
        if results[0].boxes is not None
        else []
    )

    t2 = time.time()

    return jsonify({
        "count": len(boxes),
        "boxes": boxes,
        "timing": {
            "image_read_ms":  round((t1 - t0) * 1000, 2),
            "ai_inference_ms": round((t2 - t1) * 1000, 2),
        }
    })


# ─────────────────────────────────────────────
#  Health check
# ─────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    """Simple health check so the launcher can verify the server is up."""
    return jsonify({
        "status": "ok",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "model": str(MODEL_PATH.name)
    })


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # threaded=False keeps inference on the main thread which is required for CUDA
    app.run(host="0.0.0.0", port=PORT, threaded=False, debug=False)
