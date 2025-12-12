"""
Vision Service for Two-Model Pipeline
Handles screenshot capture, SoM detection, and Vision Mapper model integration.
Supports both FlexiSIGN-specific and general computer automation.
"""

import os
import json
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
    """
    img_area = img_width * img_height
    filtered = []
    
    for box in boxes:
        x1, y1, x2, y2 = box[:4]
        w, h = x2 - x1, y2 - y1
        box_area = w * h
        
        # Skip tiny boxes (noise) - minimum 10x10 pixels for UI elements
        if w < 10 or h < 10:
            continue
        # Skip huge boxes (background windows) - max 85% of screen
        if box_area > 0.85 * img_area:
            continue
            
        filtered.append(box)
    
    return np.array(filtered) if filtered else np.array([])


def draw_annotations(image: np.ndarray, boxes: np.ndarray) -> tuple[np.ndarray, dict]:
    """
    Draw Set-of-Mark annotations: red boxes with white ID numbers.
    
    Returns:
        tuple: (annotated_image, box_map)
    """
    annotated = image.copy()
    box_map = {}
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.4
    font_thickness = 1
    box_thickness = 1
    text_padding = 2
    
    for i, box in enumerate(boxes):
        element_id = i + 1
        x1, y1, x2, y2 = map(int, box[:4])
        
        box_map[str(element_id)] = [float(box[0]), float(box[1]), float(box[2]), float(box[3])]
        
        # Draw the box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), box_thickness)
        
        # Prepare label
        label_text = str(element_id)
        (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, font_thickness)
        
        # Smart label positioning
        if y1 - text_h - text_padding * 2 > 0:
            text_bg_y1 = y1 - text_h - (text_padding * 2)
            text_bg_y2 = y1
        else:
            text_bg_y1 = y1
            text_bg_y2 = y1 + text_h + (text_padding * 2)
        
        text_bg_x1 = x1
        text_bg_x2 = x1 + text_w + (text_padding * 2)
        
        # Draw semi-transparent background
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
        
        # Draw text
        text_x = text_bg_x1 + text_padding
        text_y = text_bg_y2 - text_padding - baseline + 2
        cv2.putText(annotated, label_text, (text_x, text_y), font, font_scale, 
                   (255, 255, 255), font_thickness, cv2.LINE_AA)
    
    return annotated, box_map


# Vision Mapper prompts for different modes
GENERAL_VISION_PROMPT = """You are a computer vision assistant for GUI automation.
I am providing a screenshot with "Set-of-Mark" annotations (red boxes with ID numbers).

Your task: Find the UI elements that match the target names I provide.

## How to identify common UI elements:

### Buttons:
- Look for rectangular elements with text inside
- "button_OK", "button_Cancel" - buttons with that text
- "button_submit", "button_save" - look for Submit/Save text

### Text Fields/Inputs:
- Usually rectangular with a border, often white/light background
- May have placeholder text or be empty
- "search_box", "address_bar", "input_username"

### Icons/Toolbar Items:
- Small square or rectangular icons
- "icon_chrome" - Chrome logo (colorful circle)
- "icon_folder" - folder shape
- "close_button_x" - X symbol, usually top-right of windows

### Menu Items:
- "menu_File", "menu_Edit" - text in menu bar
- "menu_item_save" - items in dropdown menus

### Taskbar:
- Bottom of screen (usually)
- "taskbar_chrome", "taskbar_explorer" - app icons in taskbar
- "start_menu_button" - Windows logo, bottom-left

### Browser Elements:
- "chrome_address_bar" - long input field at top of browser
- "chrome_tab_new" - + symbol for new tab
- "back_button", "forward_button" - navigation arrows

For each target, identify which numbered red box corresponds to that UI element.
If you cannot find a matching element, use null.

Respond ONLY with a valid JSON object mapping target names to box numbers (integers) or null.
Example: {"button_OK": 45, "search_box": 12, "unknown_element": null}
"""

VERIFICATION_PROMPT = """You are a task verification assistant. Your job is to compare a screenshot of the current screen state against an expected outcome description.

## Your Task:
1. Analyze the provided screenshot carefully
2. Compare it against the expected final state description
3. Determine if the task was completed successfully

## Response Format:
Return ONLY a valid JSON object with these fields:
- "success": boolean - true if the expected state matches the screenshot, false otherwise
- "confidence": float (0.0 to 1.0) - how confident you are in your assessment
- "current_state": string - brief description of what you actually see on screen
- "missing_elements": array of strings - what's missing or wrong (empty if success is true)
- "corrective_actions": array of strings - suggested actions to fix the issue (empty if success is true)

## Examples:

Expected: "Notepad window open with 'Hello World!' typed in the text area"
Screenshot shows: Notepad with "Hello World!" text
Response: {"success": true, "confidence": 0.95, "current_state": "Notepad window open with 'Hello World!' text visible", "missing_elements": [], "corrective_actions": []}

Expected: "Chrome browser showing Google homepage"
Screenshot shows: Chrome with YouTube open
Response: {"success": false, "confidence": 0.9, "current_state": "Chrome browser showing YouTube homepage", "missing_elements": ["Google homepage not visible"], "corrective_actions": ["Navigate to google.com"]}

Be strict but reasonable - minor visual differences are OK, but the core task must be completed.
"""

FLEXISIGN_VISION_PROMPT = """You are a FlexiSIGN UI element identifier.
I am providing a screenshot with "Set-of-Mark" annotations (red boxes with ID numbers).

Your task: Find the UI elements that match the target names I provide.

## FlexiSIGN UI Element Guide:
- "text_tool": The "T" or text icon in the left toolbar (capital T letter)
- "select_tool": The arrow/pointer icon in the left toolbar
- "canvas_center": The LARGE white/gray drawing area in the CENTER (main workspace)
- "width_input": Input field labeled "Width" or "W" in the right panel or toolbar
- "height_input": Input field labeled "Height" or "H" in the right panel or toolbar

For each target, identify which numbered red box corresponds to that UI element.
For "canvas_center", find the LARGEST box covering the main white workspace area.
If you cannot find a matching element, use null.

Respond ONLY with a valid JSON object mapping target names to box numbers (integers) or null.
Example: {"text_tool": 45, "width_input": 88, "canvas_center": 12}
"""


class VisionService:
    """
    Vision Service for the Two-Model Pipeline.
    Handles screenshot capture, SoM detection, and Vision Mapper model.
    Supports both general and FlexiSIGN-specific modes.
    """
    
    def __init__(self, api_key: str = None, som_model_path: str = None):
        """
        Initialize VisionService with API key and FastSAM model.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not configured. Set GEMINI_API_KEY environment variable.")
        
        # Configure Gemini
        if GEMINI_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.vision_model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.vision_model = None
            print("⚠️ Warning: Gemini not available, Vision Mapper will not work")
        
        # Load FastSAM model
        if som_model_path is None:
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
        """
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        if DEBUG_LOGGER_AVAILABLE:
            try:
                get_debug_logger().log_screenshot(screenshot_bgr)
            except Exception as e:
                print(f"⚠️ Debug log error: {e}")
        
        return screenshot_bgr
    
    def run_som_detection(self, image: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Run Set-of-Mark detection on an image.
        
        Returns:
            tuple: (annotated_image, box_map)
        """
        if self.som_model is None:
            raise RuntimeError("FastSAM model not loaded. Cannot run SoM detection.")
        
        img_height, img_width = image.shape[:2]
        
        temp_path = Path(__file__).parent / "temp_screenshot.png"
        cv2.imwrite(str(temp_path), image)
        
        try:
            # Run FastSAM with optimized parameters for UI detection
            results = self.som_model(
                str(temp_path),
                conf=0.2,    # Lower confidence to catch more UI elements
                iou=0.3,     # Lower IoU to reduce duplicates
                imgsz=1024,
                retina_masks=True
            )
            
            boxes = results[0].boxes.xyxy.cpu().numpy() if results[0].boxes is not None else np.array([])
            filtered_boxes = filter_boxes(boxes, img_width, img_height)
            annotated_image, box_map = draw_annotations(image, filtered_boxes)
            
            if DEBUG_LOGGER_AVAILABLE:
                try:
                    get_debug_logger().log_annotated_image(annotated_image)
                    get_debug_logger().log_box_map(box_map)
                except Exception as e:
                    print(f"⚠️ Debug log error: {e}")
            
            return annotated_image, box_map
            
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def map_targets_to_ids(self, annotated_image: np.ndarray, targets: list[str], mode: str = "general") -> dict:
        """
        Use Gemini 2.5 Flash Vision Mapper to map target names to element IDs.
        
        Args:
            annotated_image: SoM-annotated image with numbered boxes
            targets: List of target names to find
            mode: "general" or "flexisign" - determines which prompt to use
        
        Returns:
            dict: Mapping of target names to element IDs (or None if not found)
        """
        if self.vision_model is None:
            raise RuntimeError("Gemini Vision model not available. Cannot map targets.")
        
        if not targets:
            return {}
        
        # Convert image to PIL for Gemini
        image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Select appropriate prompt based on mode
        base_prompt = FLEXISIGN_VISION_PROMPT if mode == "flexisign" else GENERAL_VISION_PROMPT
        
        # Build the full prompt
        targets_str = ", ".join(f'"{t}"' for t in targets)
        prompt = f"""{base_prompt}

Now identify these targets in the image: {targets_str}

Return ONLY a JSON object with the mappings."""

        try:
            response = self.vision_model.generate_content([prompt, pil_image])
            response_text = response.text.strip()
            
            # Handle markdown code blocks
            if response_text.startswith("```"):
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
            
            if DEBUG_LOGGER_AVAILABLE:
                try:
                    get_debug_logger().log_vision_mapper_output(cleaned_map, targets)
                except Exception as e:
                    print(f"⚠️ Debug log error: {e}")
            
            return cleaned_map
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse Vision Mapper response: {e}")
            print(f"Response was: {response_text}")
            return {target: None for target in targets}
        except Exception as e:
            print(f"⚠️ Vision Mapper error: {e}")
            raise

    def verify_task_completion(self, expected_state: str) -> dict:
        """
        Verify if the task was completed successfully by comparing
        the current screen state against the expected final state.
        
        Args:
            expected_state: Description of what the screen should look like
        
        Returns:
            dict: Verification result with keys:
                - success: bool
                - confidence: float (0.0 to 1.0)
                - current_state: str
                - missing_elements: list[str]
                - corrective_actions: list[str]
        """
        if self.vision_model is None:
            raise RuntimeError("Gemini Vision model not available. Cannot verify task.")
        
        if not expected_state:
            return {
                "success": True,
                "confidence": 0.0,
                "current_state": "No expected state provided - skipping verification",
                "missing_elements": [],
                "corrective_actions": []
            }
        
        # Capture current screen
        screenshot = self.capture_screenshot()
        
        # Convert to PIL for Gemini
        image_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Build verification prompt
        prompt = f"""{VERIFICATION_PROMPT}

Expected Final State: "{expected_state}"

Analyze the screenshot and determine if this expected state has been achieved.
Return ONLY a JSON object with your assessment."""

        try:
            response = self.vision_model.generate_content([prompt, pil_image])
            response_text = response.text.strip()
            
            # Handle markdown code blocks
            if response_text.startswith("```"):
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
            
            result = json.loads(response_text)
            
            # Ensure all required fields exist
            result.setdefault("success", False)
            result.setdefault("confidence", 0.5)
            result.setdefault("current_state", "Unknown")
            result.setdefault("missing_elements", [])
            result.setdefault("corrective_actions", [])
            
            if DEBUG_LOGGER_AVAILABLE:
                try:
                    get_debug_logger().log_verification_result(result, expected_state)
                except Exception as e:
                    print(f"⚠️ Debug log error: {e}")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse verification response: {e}")
            print(f"Response was: {response_text}")
            return {
                "success": False,
                "confidence": 0.0,
                "current_state": f"Failed to parse verification: {e}",
                "missing_elements": ["Verification parsing failed"],
                "corrective_actions": ["Retry the task"]
            }
        except Exception as e:
            print(f"⚠️ Verification error: {e}")
            return {
                "success": False,
                "confidence": 0.0,
                "current_state": f"Verification error: {e}",
                "missing_elements": ["Verification failed"],
                "corrective_actions": ["Retry the task"]
            }
