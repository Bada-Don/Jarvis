"""
FastSAM UI Marker - Vision Pre-processor
Detects UI elements and draws Set-of-Mark annotations
"""

import os
import json
from pathlib import Path
from ultralytics import FastSAM
import cv2
import numpy as np


def load_input_image(input_dir: str = "inputs") -> tuple[np.ndarray, str]:
    """Load input image (png or jpg)"""
    for ext in ["png", "jpg", "jpeg"]:
        path = Path(input_dir) / f"input.{ext}"
        if path.exists():
            return cv2.imread(str(path)), str(path)
    raise FileNotFoundError("No input.png or input.jpg found in inputs/")


def filter_boxes(boxes: np.ndarray, img_width: int, img_height: int) -> np.ndarray:
    """Filter out too small or too large boxes"""
    img_area = img_width * img_height
    filtered = []
    
    for box in boxes:
        x1, y1, x2, y2 = box[:4]
        w, h = x2 - x1, y2 - y1
        box_area = w * h
        
        # Skip tiny boxes (noise) - minimum 15x15 pixels for UI elements
        if w < 15 or h < 15:
            continue
        # Skip huge boxes (background windows)
        if box_area > 0.9 * img_area:
            continue
            
        filtered.append(box)
    
    return np.array(filtered) if filtered else np.array([])


def draw_annotations(image: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    """Draw Set-of-Mark annotations: red boxes with white ID numbers"""
    annotated = image.copy()
    
    # CONFIG FOR DRAWING
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.4  # Much smaller text
    font_thickness = 1
    box_thickness = 1  # Thinner box lines
    text_padding = 2
    
    for i, box in enumerate(boxes):
        # Get coordinates
        x1, y1, x2, y2 = map(int, box[:4])
        w, h = x2 - x1, y2 - y1
        
        # 1. DRAW THE BOX (Thinner)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), box_thickness)
        
        # Prepare the ID text
        label_text = str(i + 1)
        (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, font_thickness)
        
        # 2. SMART LABEL POSITIONING
        # Logic: If the box is too small, draw the text ABOVE the box.
        # Otherwise, draw it inside the top-left corner.
        
        # Check if there is space above the box to draw the tag
        if y1 - text_h - text_padding * 2 > 0:
            # Draw Outside (Above)
            text_bg_y1 = y1 - text_h - (text_padding * 2)
            text_bg_y2 = y1
        else:
            # Draw Inside (Top-Left) - Fallback if at very top of screen
            text_bg_y1 = y1
            text_bg_y2 = y1 + text_h + (text_padding * 2)
        
        text_bg_x1 = x1
        text_bg_x2 = x1 + text_w + (text_padding * 2)
        
        # 3. DRAW SEMI-TRANSPARENT TEXT BACKGROUND
        # Extract the region of interest (ROI) where the text background will go
        # Ensure coordinates are within image bounds
        roi_y1 = max(0, text_bg_y1)
        roi_y2 = min(annotated.shape[0], text_bg_y2)
        roi_x1 = max(0, text_bg_x1)
        roi_x2 = min(annotated.shape[1], text_bg_x2)
        
        if roi_y2 > roi_y1 and roi_x2 > roi_x1:
            overlay = annotated[roi_y1:roi_y2, roi_x1:roi_x2].copy()
            cv2.rectangle(overlay, (0, 0), (roi_x2-roi_x1, roi_y2-roi_y1), (0, 0, 255), -1)
            
            # Apply opacity (0.6 means 60% solid, 40% transparent)
            alpha = 0.6
            annotated[roi_y1:roi_y2, roi_x1:roi_x2] = cv2.addWeighted(
                overlay, alpha, 
                annotated[roi_y1:roi_y2, roi_x1:roi_x2], 1 - alpha, 0
            )
        
        # 4. DRAW TEXT
        # Adjust text position based on where we drew the background
        text_x = text_bg_x1 + text_padding
        text_y = text_bg_y2 - text_padding - baseline + 2  # slight offset adjustment
        cv2.putText(annotated, label_text, (text_x, text_y), font, font_scale, 
                   (255, 255, 255), font_thickness, cv2.LINE_AA)
    
    return annotated


def main():
    # Create output directory
    os.makedirs("outputs", exist_ok=True)
    
    # Load model
    print("Loading FastSAM model...")
    model = FastSAM("weights/FastSAM-s.pt")
    
    # Load input image
    print("Loading input image...")
    image, img_path = load_input_image()
    img_height, img_width = image.shape[:2]
    print(f"Image size: {img_width}x{img_height}")
    
    # Run inference with UI-optimized parameters
    print("Running inference...")
    results = model(
        img_path,
        conf=0.25,  # Lower confidence to catch faint buttons
        iou=0.4,    # Lower IoU to reduce overlapping duplicates
        imgsz=1024,
        retina_masks=True
    )
    
    # Extract bounding boxes
    boxes = results[0].boxes.xyxy.cpu().numpy() if results[0].boxes is not None else np.array([])
    print(f"Raw detections: {len(boxes)}")
    
    # Filter boxes
    filtered_boxes = filter_boxes(boxes, img_width, img_height)
    print(f"After filtering: {len(filtered_boxes)}")
    
    # Draw annotations
    annotated_image = draw_annotations(image, filtered_boxes)
    
    # Save output
    output_path = "outputs/marked_output.png"
    cv2.imwrite(output_path, annotated_image)
    
    # Export bounding box mapping for mouse controller
    box_map = {}
    for i, box in enumerate(filtered_boxes):
        element_id = i + 1
        x1, y1, x2, y2 = map(float, box[:4])
        box_map[element_id] = [x1, y1, x2, y2]
    
    box_map_path = "outputs/box_mapping.json"
    with open(box_map_path, 'w') as f:
        json.dump(box_map, f, indent=2)
    
    print(f"\nDetected {len(filtered_boxes)} UI elements")
    print(f"Output saved to: {output_path}")
    print(f"Box mapping saved to: {box_map_path}")


if __name__ == "__main__":
    main()
