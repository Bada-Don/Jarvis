"""
Gemini Planner Service for Two-Model Pipeline

This module provides the GeminiPlannerService class that uses Gemini Flash Lite
to convert natural language commands into structured execution plans for
FlexiSIGN automation.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


# Hardcoded plate dimensions knowledge base
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


SYSTEM_PROMPT = """You are a FlexiSIGN automation planner. Your job is to convert user commands into structured execution plans.

## Plate Dimensions Knowledge Base (ALWAYS use these exact values):
- Bike Iron Plate: Front (8 x 1.2 inches), Back (10 x 1.5 inches)
- Bike Glass Plate: Front (6 x 1.2 inches), Back (10 x 1.5 inches)  
- Car Normal Plate: Front (14 x 2.3 inches), Back (14 x 2.4 inches)

## Output Format:
You MUST return a valid JSON object with a "sequence" array containing ordered steps.

Each step must have:
- "order": integer (1, 2, 3, ...)
- "type": either "keyboard" or "visual_click"
- "desc": brief description of the action

For keyboard steps, include:
- "value": the key or text to type (e.g., "ctrl+n", "PB12W3998", "8")
- "repeats": (optional) number of times to repeat the action

For visual_click steps, include:
- "target_name": the UI element to click (e.g., "text_tool", "width_input", "canvas_center")

## Common UI Elements in FlexiSIGN:
- "text_tool": The text tool in the toolbar
- "select_tool": The selection tool
- "canvas_center": Center of the canvas area
- "width_input": Width input field in properties
- "height_input": Height input field in properties
- "ok_button": OK/Apply button in dialogs
- "new_page_dialog": New page dialog elements

## Example Output:
{
  "sequence": [
    {"order": 1, "type": "keyboard", "value": "ctrl+n", "desc": "Open new page dialog"},
    {"order": 2, "type": "visual_click", "target_name": "width_input", "desc": "Click width input"},
    {"order": 3, "type": "keyboard", "value": "8", "desc": "Enter width"},
    {"order": 4, "type": "visual_click", "target_name": "height_input", "desc": "Click height input"},
    {"order": 5, "type": "keyboard", "value": "1.2", "desc": "Enter height"},
    {"order": 6, "type": "visual_click", "target_name": "ok_button", "desc": "Confirm new page"},
    {"order": 7, "type": "visual_click", "target_name": "text_tool", "desc": "Select text tool"},
    {"order": 8, "type": "visual_click", "target_name": "canvas_center", "desc": "Click canvas to place text"},
    {"order": 9, "type": "keyboard", "value": "PB12W3998", "desc": "Type plate number"}
  ]
}

IMPORTANT:
- Always use the exact plate dimensions from the knowledge base
- Return ONLY valid JSON, no markdown formatting or extra text
- Each step must be atomic and executable
"""


class GeminiPlannerService:
    """
    Service class for generating execution plans using Gemini Flash Lite.
    
    This service converts natural language commands into structured JSON
    execution plans that can be executed by the local client.
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
        
        # Initialize the model (using gemini-flash-lite-latest for the planner)
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-lite',
            system_instruction=SYSTEM_PROMPT
        )
    
    def generate_plan(self, user_command: str) -> dict:
        """
        Generate an execution plan from a user command.
        
        Args:
            user_command: Natural language command from the user
                         (e.g., "Make iron number plate set for bike, PB12W3998")
        
        Returns:
            dict: Parsed execution plan with "sequence" array containing
                  ordered steps with type, value/target_name, and description.
        
        Raises:
            ValueError: If the model returns invalid JSON.
            Exception: If the API call fails.
        """
        if not user_command or not user_command.strip():
            raise ValueError("User command cannot be empty")
        
        try:
            # Generate the plan using Gemini
            response = self.model.generate_content(user_command)
            
            # Extract the text response
            response_text = response.text.strip()
            
            # Clean up response if it contains markdown code blocks
            if response_text.startswith('```'):
                # Remove markdown code block formatting
                lines = response_text.split('\n')
                # Remove first line (```json or ```)
                lines = lines[1:]
                # Remove last line if it's ```
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                response_text = '\n'.join(lines)
            
            # Parse the JSON response
            plan = json.loads(response_text)
            
            # Validate the plan structure
            self._validate_plan(plan)
            
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
        
        for i, step in enumerate(plan['sequence']):
            if not isinstance(step, dict):
                raise ValueError(f"Step {i+1} must be a dictionary")
            
            if 'order' not in step:
                raise ValueError(f"Step {i+1} missing 'order' field")
            
            if 'type' not in step:
                raise ValueError(f"Step {i+1} missing 'type' field")
            
            step_type = step['type']
            if step_type not in ('keyboard', 'visual_click'):
                raise ValueError(
                    f"Step {i+1} has invalid type '{step_type}'. "
                    "Must be 'keyboard' or 'visual_click'"
                )
            
            if step_type == 'keyboard' and 'value' not in step:
                raise ValueError(f"Keyboard step {i+1} missing 'value' field")
            
            if step_type == 'visual_click' and 'target_name' not in step:
                raise ValueError(f"Visual click step {i+1} missing 'target_name' field")
