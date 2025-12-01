"""
Vision Service for Two-Model Pipeline
Handles screenshot capture, SoM detection, and Vision Mapper model integration.

Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2
"""

import os
import json
import base64
from io import BytesIO
from pathlib import Path

import numpy as np
import cv2
import pyautogui
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import debug logger
try:
    from debug_logger import get_debug_logger
    DEBUG_LOGGER_AVAILABLE = True
except ImportError:
    DEBUG_LOGGER_AVAILABLE = False

# Import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Warning: google-generativeai not installed")

# Import FastSAM
try:
    from ultralytics import FastSAM
    FASTSAM_AVAILABLE = True
except ImportError:
    FASTSAM_AVAILABLE = False
    print("⚠️ Warning: ultralytics not installed")


def filter_boxes(boxes: np.ndarray, img_width: int, img_height: int) -> np.ndarray:
    """
    Filter out too small or too large boxes.
    Reused from backend/SoM.py with identical logic.
    """
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


def draw_annotations(image: np.ndarray, boxes: np.ndarray) -> tuple[np.ndarray, dict]:
    """
    Draw Set-of-Mark annotations: red boxes with white ID numbers.
    Reused from backend/SoM.py with identical logic.
    
    Returns:
        tuple: (annotated_image, box_map)
            - annotated_image: Image with red boxes and ID labels
            - box_map: Dict mapping element IDs to coordinates {id: [x1, y1, x2, y2]}
    """
    annotated = image.copy()
    box_map = {}
    
    # CONFIG FOR DRAWING
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.4  # Much smaller text
    font_thickness = 1
    box_thickness = 1  # Thinner box lines
    text_padding = 2
    
    for i, box in enumerate(boxes):
        element_id = i + 1
        
        # Get coordinates
        x1, y1, x2, y2 = map(int, box[:4])
        
        # Store in box_map
        box_map[str(element_id)] = [float(box[0]), float(box[1]), float(box[2]), float(box[3])]
        
        # 1. DRAW THE BOX (Thinner)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), box_thickness)
        
        # Prepare the ID text
        label_text = str(element_id)
        (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, font_thickness)
        
        # 2. SMART LABEL POSITIONING
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
        roi_y1 = max(0, text_bg_y1)
        roi_y2 = min(annotated.shape[0], text_bg_y2)
        roi_x1 = max(0, text_bg_x1)
        roi_x2 = min(annotated.shape[1], text_bg_x2)
        
        if roi_y2 > roi_y1 and roi_x2 > roi_x1:
            overlay = annotated[roi_y1:roi_y2, roi_x1:roi_x2].copy()
            cv2.rectangle(overlay, (0, 0), (roi_x2-roi_x1, roi_y2-roi_y1), (0, 0, 255), -1)
            
            alpha = 0.6
            annotated[roi_y1:roi_y2, roi_x1:roi_x2] = cv2.addWeighted(
                overlay, alpha, 
                annotated[roi_y1:roi_y2, roi_x1:roi_x2], 1 - alpha, 0
            )
        
        # 4. DRAW TEXT
        text_x = text_bg_x1 + text_padding
        text_y = text_bg_y2 - text_padding - baseline + 2
        cv2.putText(annotated, label_text, (text_x, text_y), font, font_scale, 
                   (255, 255, 255), font_thickness, cv2.LINE_AA)
    
    return annotated, box_map


class VisionService:
    """
    Vision Service for the Two-Model Pipeline.
    Handles screenshot capture, SoM detection, and Vision Mapper model.
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2
    """
    
    def __init__(self, api_key: str = None, som_model_path: str = None):
        """
        Initialize VisionService with API key and FastSAM model.
        
        Args:
            api_key: Gemini API key. If None, loads from GEMINI_API_KEY env var.
            som_model_path: Path to FastSAM weights. Defaults to weights/FastSAM-s.pt
        
        Requirements: 6.2, 6.3
        """
        # Load API key
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not configured. Set GEMINI_API_KEY environment variable.")
        
        # Configure Gemini
        if GEMINI_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.vision_model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.vision_model = None
            print("⚠️ Warning: Gemini not available, Vision Mapper will not work")
        
        # Load FastSAM model
        if som_model_path is None:
            # Try common paths
            possible_paths = [
                Path(__file__).parent / "weights" / "FastSAM-s.pt",
                Path(__file__).parent.parent / "backend" / "weights" / "FastSAM-s.pt",
            ]
            for path in possible_paths:
                if path.exists():
                    som_model_path = str(path)
                    break
        
        if som_model_path and FASTSAM_AVAILABLE:
            print(f"Loading FastSAM model from: {som_model_path}")
            self.som_model = FastSAM(som_model_path)
        else:
            self.som_model = None
            if not FASTSAM_AVAILABLE:
                print("⚠️ Warning: FastSAM not available")
            else:
                print("⚠️ Warning: FastSAM weights not found")
    
    def capture_screenshot(self) -> np.ndarray:
        """
        Capture a screenshot using pyautogui.
        
        Returns:
            np.ndarray: Screenshot as BGR numpy array (OpenCV format)
        
        Requirements: 3.1
        """
        # Capture screenshot using pyautogui
        screenshot = pyautogui.screenshot()
        
        # Convert PIL Image to numpy array (RGB)
        screenshot_np = np.array(screenshot)
        
        # Convert RGB to BGR for OpenCV
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Save to debug log
        if DEBUG_LOGGER_AVAILABLE:
            try:
                get_debug_logger().log_screenshot(screenshot_bgr)
            except Exception as e:
                print(f"⚠️ Debug log error: {e}")
        
        return screenshot_bgr
    
    def run_som_detection(self, image: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Run Set-of-Mark detection on an image.
        
        Args:
            image: Input image as BGR numpy array
        
        Returns:
            tuple: (annotated_image, box_map)
                - annotated_image: Image with red boxes and ID labels
                - box_map: Dict mapping element IDs to coordinates
        
        Requirements: 3.2, 3.3, 3.4
        """
        if self.som_model is None:
            raise RuntimeError("FastSAM model not loaded. Cannot run SoM detection.")
        
        img_height, img_width = image.shape[:2]
        
        # Save image temporarily for FastSAM (it requires a file path)
        temp_path = Path(__file__).parent / "temp_screenshot.png"
        cv2.imwrite(str(temp_path), image)
        
        try:
            # Run FastSAM inference with UI-optimized parameters
            results = self.som_model(
                str(temp_path),
                conf=0.25,  # Lower confidence to catch faint buttons
                iou=0.4,    # Lower IoU to reduce overlapping duplicates
                imgsz=1024,
                retina_masks=True
            )
            
            # Extract bounding boxes
            boxes = results[0].boxes.xyxy.cpu().numpy() if results[0].boxes is not None else np.array([])
            
            # Filter boxes
            filtered_boxes = filter_boxes(boxes, img_width, img_height)
            
            # Draw annotations and get box_map
            annotated_image, box_map = draw_annotations(image, filtered_boxes)
            
            # Save to debug log
            if DEBUG_LOGGER_AVAILABLE:
                try:
                    get_debug_logger().log_annotated_image(annotated_image)
                    get_debug_logger().log_box_map(box_map)
                except Exception as e:
                    print(f"⚠️ Debug log error: {e}")
            
            return annotated_image, box_map
            
        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
    
    def map_targets_to_ids(self, annotated_image: np.ndarray, targets: list[str]) -> dict:
        """
        Use Gemini 2.0 Flash Vision Mapper to map target names to element IDs.
        
        Args:
            annotated_image: SoM-annotated image with numbered boxes
            targets: List of target names to find (e.g., ["text_tool", "width_input"])
        
        Returns:
            dict: Mapping of target names to element IDs (or None if not found)
                  e.g., {"text_tool": 45, "width_input": 88}
        
        Requirements: 4.1, 4.2
        """
        if self.vision_model is None:
            raise RuntimeError("Gemini Vision model not available. Cannot map targets.")
        
        if not targets:
            return {}
        
        # Convert image to PIL for Gemini
        image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Build prompt for Vision Mapper
        targets_str = ", ".join(f'"{t}"' for t in targets)
        prompt = f"""You are a FlexiSIGN UI element identifier. Look at this screenshot with numbered red boxes (Set-of-Mark annotations).

Your task: Find the UI elements that match these target names: {targets_str}

FlexiSIGN UI Element Guide:
- "text_tool": The "T" or text icon in the left toolbar (usually a capital T letter)
- "select_tool": The arrow/pointer icon in the left toolbar
- "width_input": Input field labeled "Width" or "W" in the right panel or dialog
- "height_input": Input field labeled "Height" or "H" in the right panel or dialog
- "canvas_center": The LARGE white/gray drawing area in the CENTER of the screen (the main workspace where designs are created). This is usually the biggest rectangular area.

For each target, identify which numbered box corresponds to that UI element.

IMPORTANT:
- Look at the red numbered boxes in the image
- Match each target name to the most appropriate numbered box
- For "canvas_center", find the LARGEST box that covers the main white drawing workspace area
- If you cannot find a matching element, use null for that target

Respond ONLY with a valid JSON object mapping target names to box numbers (integers) or null.
Example response format:
{{"text_tool": 45, "width_input": 88, "canvas_center": 12, "unknown_element": null}}

Now identify the targets in this image:"""

        try:
            # Call Gemini Vision API
            response = self.vision_model.generate_content([prompt, pil_image])
            response_text = response.text.strip()
            
            # Parse JSON response
            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                # Extract JSON from code block
                lines = response_text.split("\n")
                json_lines = []
                in_json = False
                for line in lines:
                    if line.startswith("```") and not in_json:
                        in_json = True
                        continue
                    elif line.startswith("```") and in_json:
                        break
                    elif in_json:
                        json_lines.append(line)
                response_text = "\n".join(json_lines)
            
            id_map = json.loads(response_text)
            
            # Validate and clean the response
            cleaned_map = {}
            for target in targets:
                if target in id_map:
                    value = id_map[target]
                    if value is None or isinstance(value, int):
                        cleaned_map[target] = value
                    elif isinstance(value, str) and value.isdigit():
                        cleaned_map[target] = int(value)
                    else:
                        cleaned_map[target] = None
                else:
                    cleaned_map[target] = None
            
            # Save to debug log
            if DEBUG_LOGGER_AVAILABLE:
                try:
                    get_debug_logger().log_vision_mapper_output(cleaned_map, targets)
                except Exception as e:
                    print(f"⚠️ Debug log error: {e}")
            
            return cleaned_map
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse Vision Mapper response: {e}")
            print(f"Response was: {response_text}")
            # Return all nulls on parse failure
            return {target: None for target in targets}
        except Exception as e:
            print(f"⚠️ Vision Mapper error: {e}")
            raise
