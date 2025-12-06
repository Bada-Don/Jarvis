"""
Gemini Planner Service for Two-Model Pipeline

This module provides the GeminiPlannerService class that uses Gemini Flash Lite
to convert natural language commands into structured execution plans.
Supports both FlexiSIGN-specific tasks and general computer automation.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


# Hardcoded plate dimensions knowledge base (FlexiSIGN specific)
PLATE_DIMENSIONS = {
    "bike_iron": {
        "front": {"width": 8, "height": 1.2},
        "back": {"width": 10, "height": 1.5}
    },
    "bike_glass": {
        "front": {"width": 6, "height": 1.2},
        "back": {"width": 10, "height": 1.5}
    },
    "car_normal": {
        "front": {"width": 14, "height": 2.3},
        "back": {"width": 14, "height": 2.4}
    }
}


GENERAL_SYSTEM_PROMPT = """You are JARVIS, an AI assistant that automates computer tasks. Your job is to convert user commands into structured execution plans.

## Your Capabilities:
You can control the computer through:
1. **Keyboard actions**: typing text, pressing keys, keyboard shortcuts
2. **Visual clicks**: clicking on UI elements identified by their description

## Output Format:
Return a valid JSON object with a "sequence" array containing ordered steps.

Each step must have:
- "order": integer (1, 2, 3, ...)
- "type": either "keyboard" or "visual_click"
- "desc": brief description of the action

For keyboard steps, include:
- "value": the key or text to type
  - For shortcuts: "ctrl+c", "alt+tab", "win+r", "ctrl+shift+esc"
  - For special keys: "enter", "tab", "escape", "backspace", "delete", "up", "down", "left", "right", "f1"-"f12"
  - For text: just the text string like "Hello World" or "notepad"
- "repeats": (optional) number of times to repeat

For visual_click steps, include:
- "target_name": descriptive name of the UI element to click
  - Be specific: "chrome_address_bar", "start_menu_button", "file_menu", "save_button", "close_button_x"
  - For text/buttons: "button_OK", "button_Cancel", "menu_File", "tab_Settings"
  - For icons: "icon_chrome", "icon_folder", "taskbar_chrome"

## Common Patterns:

### Opening Applications:
- Press Win key, type app name, press Enter
- Or use Win+R for Run dialog

### Web Browsing:
- Click address bar (or Ctrl+L), type URL with a SPACE at the end, press Enter
- IMPORTANT: Always add a trailing space after URLs (e.g., "google.com ") to prevent browser autocomplete from changing the URL
- Click on links, buttons, form fields

### File Operations:
- Ctrl+O (Open), Ctrl+S (Save), Ctrl+N (New)
- Navigate file dialogs by clicking folders

### Text Editing:
- Click to position cursor
- Type text
- Use Ctrl+A (select all), Ctrl+C (copy), Ctrl+V (paste)

## Example - Open Notepad and type:
{
  "sequence": [
    {"order": 1, "type": "keyboard", "value": "win", "desc": "Open Start menu"},
    {"order": 2, "type": "keyboard", "value": "notepad", "desc": "Type notepad"},
    {"order": 3, "type": "keyboard", "value": "enter", "desc": "Launch Notepad"},
    {"order": 4, "type": "keyboard", "value": "Hello World!", "desc": "Type the message"}
  ]
}

## Example - Open Chrome and go to Google:
{
  "sequence": [
    {"order": 1, "type": "keyboard", "value": "win", "desc": "Open Start menu"},
    {"order": 2, "type": "keyboard", "value": "chrome", "desc": "Search for Chrome"},
    {"order": 3, "type": "keyboard", "value": "enter", "desc": "Launch Chrome"},
    {"order": 4, "type": "keyboard", "value": "ctrl+l", "desc": "Focus address bar"},
    {"order": 5, "type": "keyboard", "value": "google.com ", "desc": "Type URL with trailing space to prevent autocomplete"},
    {"order": 6, "type": "keyboard", "value": "enter", "desc": "Navigate to site"}
  ]
}

## Example - Click on a specific button:
{
  "sequence": [
    {"order": 1, "type": "visual_click", "target_name": "button_submit", "desc": "Click Submit button"},
    {"order": 2, "type": "visual_click", "target_name": "dropdown_options", "desc": "Open dropdown menu"}
  ]
}

IMPORTANT:
- Prefer keyboard shortcuts when possible (faster and more reliable)
- Use visual_click only when keyboard shortcuts aren't available
- Return ONLY valid JSON, no markdown formatting or extra text
- Each step must be atomic and executable
- Add small waits implicitly between steps (the executor handles this)
"""


FLEXISIGN_SYSTEM_PROMPT = """You are a FlexiSIGN automation planner. Your job is to convert user commands into structured execution plans.

## Plate Dimensions Knowledge Base (ALWAYS use these exact values):
- Bike Iron Plate: Front (8 x 1.2 inches), Back (10 x 1.5 inches)
- Bike Glass Plate: Front (6 x 1.2 inches), Back (10 x 1.5 inches)  
- Car Normal Plate: Front (14 x 2.3 inches), Back (14 x 2.4 inches)

## EXECUTION MODES:
You must choose the appropriate execution mode for each task:

1. **direct**: Use for standard number plate tasks. Commands execute via UI Automation (faster, more reliable).
   - Use when: Creating standard number plates, setting dimensions, changing fonts, applying styles
   - Benefits: No screenshots needed, faster execution, more reliable

2. **vision**: Use for complex or non-standard tasks requiring visual element detection.
   - Use when: Custom layouts, unusual UI interactions, tasks requiring visual verification
   - Benefits: Can handle any UI element visible on screen

## MODE SELECTION GUIDANCE:
- Standard number plate requests (e.g., "Make iron plate set for bike PB12W3998") → Use "direct" mode
- Simple dimension/font/style changes → Use "direct" mode
- Complex layouts, custom designs, or unfamiliar UI elements → Use "vision" mode
- When in doubt about UI element locations → Use "vision" mode

## Output Format:
You MUST return a valid JSON object with:
- "mode": either "direct" or "vision"
- "sequence": array containing ordered steps

Each step must have:
- "order": integer (1, 2, 3, ...)
- "type": the command type (see below)
- "desc": brief description of the action

## DIRECT MODE COMMAND TYPES:

### keyboard
Raw keyboard input for hotkeys and typing.
- "value": the key or text to type (e.g., "ctrl+n", "enter", "PB12W3998")
- "repeats": (optional) number of times to repeat

### create_text
Create a text object with specified content.
- "text": the text content to create (e.g., "PB12W3998")

### set_dimensions
Set width and height of the selected object.
- "width": width value as string (e.g., "8")
- "height": height value as string (e.g., "1.2")

### set_font
Change the font of selected text.
- "font_name": name of the font to apply (e.g., "Blackberry")

### apply_style
Apply a predefined style (opens Apply Styles window with Shift+S).
- "style_name": (optional) name of style to search and apply

### move_object
Move the selected object using arrow keys with Shift modifier.
- "direction": one of "up", "down", "left", "right"
- "distance": number of key presses (integer)

## VISION MODE COMMAND TYPES:

### keyboard
Same as direct mode.

### visual_click
Click on a UI element identified visually.
- "target_name": descriptive name of the UI element to click

## Common UI Elements (for vision mode):
- "text_tool": The text tool in the toolbar
- "select_tool": The selection tool
- "canvas_center": Center of the canvas area
- "width_input": Width input field in properties
- "height_input": Height input field in properties

## EXAMPLE - Direct Mode (Standard Number Plate):
{
  "mode": "direct",
  "sequence": [
    {"order": 1, "type": "keyboard", "value": "ctrl+n", "desc": "Open new page"},
    {"order": 2, "type": "create_text", "text": "PB12W3998", "desc": "Create plate text"},
    {"order": 3, "type": "set_font", "font_name": "Blackberry", "desc": "Set plate font"},
    {"order": 4, "type": "set_dimensions", "width": "8", "height": "1.2", "desc": "Set front plate size"},
    {"order": 5, "type": "apply_style", "style_name": "Iron Plate", "desc": "Apply iron plate style"},
    {"order": 6, "type": "move_object", "direction": "up", "distance": 10, "desc": "Move plate up"}
  ]
}

## EXAMPLE - Vision Mode (Complex Task):
{
  "mode": "vision",
  "sequence": [
    {"order": 1, "type": "keyboard", "value": "ctrl+n", "desc": "Open new page"},
    {"order": 2, "type": "visual_click", "target_name": "text_tool", "desc": "Select text tool"},
    {"order": 3, "type": "visual_click", "target_name": "canvas_center", "desc": "Click canvas to place text"},
    {"order": 4, "type": "keyboard", "value": "PB12W3998", "desc": "Enter number"},
    {"order": 5, "type": "visual_click", "target_name": "select_tool", "desc": "Select selection tool"},
    {"order": 6, "type": "visual_click", "target_name": "height_input", "desc": "Click height input"},
    {"order": 7, "type": "keyboard", "value": "1.2", "desc": "Enter height"},
    {"order": 8, "type": "visual_click", "target_name": "width_input", "desc": "Click width input"},
    {"order": 9, "type": "keyboard", "value": "8", "desc": "Enter width"}
  ]
}

IMPORTANT:
- Always use the exact plate dimensions from the knowledge base
- Choose "direct" mode for standard tasks (faster and more reliable)
- Choose "vision" mode only when direct automation cannot handle the task
- Return ONLY valid JSON, no markdown formatting or extra text
- Each step must be atomic and executable
"""


class GeminiPlannerService:
    """
    Service class for generating execution plans using Gemini Flash Lite.
    
    Supports two modes:
    - General: For any computer automation task
    - FlexiSIGN: For number plate creation with domain knowledge
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the GeminiPlannerService.
        
        Args:
            api_key: Optional Gemini API key. If not provided, will attempt
                    to load from GEMINI_API_KEY environment variable.
        
        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key not configured. "
                "Set GEMINI_API_KEY environment variable or pass api_key parameter."
            )
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize models for different modes
        self.general_model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-lite',
            system_instruction=GENERAL_SYSTEM_PROMPT
        )
        
        self.flexisign_model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-lite',
            system_instruction=FLEXISIGN_SYSTEM_PROMPT
        )
    
    def detect_mode(self, user_command: str) -> str:
        """
        Detect whether the command is for FlexiSIGN or general use.
        
        Args:
            user_command: The user's natural language command
            
        Returns:
            str: "flexisign" or "general"
        """
        command_lower = user_command.lower()
        
        # FlexiSIGN keywords
        flexisign_keywords = [
            "plate", "number plate", "numberplate", 
            "bike", "car", "iron", "glass",
            "flexisign", "flexi sign", "flexi-sign",
            "nameplate", "name plate"
        ]
        
        for keyword in flexisign_keywords:
            if keyword in command_lower:
                return "flexisign"
        
        return "general"
    
    def generate_plan(self, user_command: str, mode: str = None) -> dict:
        """
        Generate an execution plan from a user command.
        
        Args:
            user_command: Natural language command from the user
            mode: Optional mode override ("general" or "flexisign")
                  If not provided, auto-detects based on command content.
        
        Returns:
            dict: Parsed execution plan with "sequence" array and "mode" field.
        
        Raises:
            ValueError: If the model returns invalid JSON.
            Exception: If the API call fails.
        """
        if not user_command or not user_command.strip():
            raise ValueError("User command cannot be empty")
        
        # Auto-detect mode if not specified
        if mode is None:
            mode = self.detect_mode(user_command)
        
        # Select appropriate model
        model = self.flexisign_model if mode == "flexisign" else self.general_model
        
        try:
            # Generate the plan using Gemini
            response = model.generate_content(user_command)
            
            # Extract the text response
            response_text = response.text.strip()
            
            # Clean up response if it contains markdown code blocks
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                response_text = '\n'.join(lines)
            
            # Parse the JSON response
            plan = json.loads(response_text)
            
            # Validate the plan structure
            self._validate_plan(plan)
            
            # Add mode to the plan for downstream processing
            plan['mode'] = mode
            
            return plan
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Planner Model: {e}")
        except Exception as e:
            raise Exception(f"Failed to generate plan: {e}")
    
    def _validate_plan(self, plan: dict) -> None:
        """
        Validate the structure of an execution plan.
        
        Args:
            plan: The execution plan to validate.
        
        Raises:
            ValueError: If the plan structure is invalid.
        """
        if not isinstance(plan, dict):
            raise ValueError("Plan must be a dictionary")
        
        if 'sequence' not in plan:
            raise ValueError("Plan must contain a 'sequence' array")
        
        if not isinstance(plan['sequence'], list):
            raise ValueError("'sequence' must be an array")
        
        # Valid step types for each mode
        # Direct mode types: keyboard, create_text, set_dimensions, set_font, apply_style, move_object
        # Vision mode types: keyboard, visual_click
        valid_types = {
            'keyboard', 'visual_click',
            'create_text', 'set_dimensions', 'set_font', 'apply_style', 'move_object'
        }
        
        for i, step in enumerate(plan['sequence']):
            if not isinstance(step, dict):
                raise ValueError(f"Step {i+1} must be a dictionary")
            
            if 'order' not in step:
                raise ValueError(f"Step {i+1} missing 'order' field")
            
            if 'type' not in step:
                raise ValueError(f"Step {i+1} missing 'type' field")
            
            step_type = step['type']
            if step_type not in valid_types:
                raise ValueError(
                    f"Step {i+1} has invalid type '{step_type}'. "
                    f"Must be one of: {', '.join(sorted(valid_types))}"
                )
            
            # Validate required fields for each step type
            if step_type == 'keyboard' and 'value' not in step:
                raise ValueError(f"Keyboard step {i+1} missing 'value' field")
            
            if step_type == 'visual_click' and 'target_name' not in step:
                raise ValueError(f"Visual click step {i+1} missing 'target_name' field")
            
            if step_type == 'create_text' and 'text' not in step:
                raise ValueError(f"Create text step {i+1} missing 'text' field")
            
            if step_type == 'set_dimensions':
                if 'width' not in step:
                    raise ValueError(f"Set dimensions step {i+1} missing 'width' field")
                if 'height' not in step:
                    raise ValueError(f"Set dimensions step {i+1} missing 'height' field")
            
            if step_type == 'set_font' and 'font_name' not in step:
                raise ValueError(f"Set font step {i+1} missing 'font_name' field")
            
            if step_type == 'move_object':
                if 'direction' not in step:
                    raise ValueError(f"Move object step {i+1} missing 'direction' field")
                if 'distance' not in step:
                    raise ValueError(f"Move object step {i+1} missing 'distance' field")
                if step['direction'] not in ('up', 'down', 'left', 'right'):
                    raise ValueError(
                        f"Move object step {i+1} has invalid direction '{step['direction']}'. "
                        "Must be 'up', 'down', 'left', or 'right'"
                    )
