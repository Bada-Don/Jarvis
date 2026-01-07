"""
Gemini Planner Service for Two-Model Pipeline

This module provides the GeminiPlannerService class that uses Gemini Flash Lite
to convert natural language commands into structured execution plans.
Supports both FlexiSIGN-specific tasks and general computer automation.
"""

import os
import json
from google import genai
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


GENERAL_SYSTEM_PROMPT = r"""You are JARVIS, an AI assistant that automates computer tasks. Your job is to convert user commands into structured execution plans.

## System Information:
- Windows Username: {WINDOWS_USERNAME}
- User Home Directory: C:\Users\{WINDOWS_USERNAME}
- Desktop Path: {DESKTOP_PATH}
- Documents Path: {DOCUMENTS_PATH}
- Downloads Path: {DOWNLOADS_PATH}
- **Stickers/New Briefcase Path: {{STICKERS_PATH}}** (IMPORTANT: When user mentions "New Briefcase", "stickers", or files from there, use "stickers" or "{{STICKERS_PATH}}")

CRITICAL PATH RULES:
1. When user mentions "New Briefcase" → use "stickers" or "D:\Stickers\New Briefcase"
2. When user mentions "Desktop" → use "desktop" or the full Desktop path
3. NEVER add file extensions unless the user explicitly mentions them
4. Use fuzzy paths without extensions - the system will find the correct file automatically

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
- To navigate to a URL: Ctrl+L (focus address bar), type URL with a SPACE at the end, press Enter
- IMPORTANT: Always add a trailing space after URLs (e.g., "youtube.com ") to prevent browser autocomplete
- To search on a website: Use the website's search shortcut (e.g., "/" on YouTube) or visual_click on search box
- YouTube shortcuts: "/" focuses the search bar, then type query and press Enter
- Google shortcuts: Just type in the search box (auto-focused on google.com)
- DO NOT use the browser address bar to search within a website - use the website's own search feature

### File Operations:
- Ctrl+O (Open), Ctrl+S (Save), Ctrl+N (New), Ctrl+L (Focus Address Bar)
- Navigate file dialogs by clicking folders

### Text Editing:
- Click to position cursor
- Type text
- Use Ctrl+A (select all), Ctrl+C (copy), Ctrl+V (paste)

## Example - Open Notepad and type:
{{
  "sequence": [
    {{"order": 1, "type": "keyboard", "value": "win", "desc": "Open Start menu"}},
    {{"order": 2, "type": "keyboard", "value": "notepad", "desc": "Type notepad"}},
    {{"order": 3, "type": "keyboard", "value": "enter", "desc": "Launch Notepad"}},
    {{"order": 4, "type": "keyboard", "value": "Hello World!", "desc": "Type the message"}}
  ],
  "expected_final_state": "Notepad window open with 'Hello World!' typed in the text area"
}}

## Example - Open Chrome and go to Google:
{{
  "sequence": [
    {{"order": 1, "type": "keyboard", "value": "win", "desc": "Open Start menu"}},
    {{"order": 2, "type": "keyboard", "value": "chrome", "desc": "Search for Chrome"}},
    {{"order": 3, "type": "keyboard", "value": "enter", "desc": "Launch Chrome"}},
    {{"order": 4, "type": "keyboard", "value": "ctrl+l", "desc": "Focus address bar"}},
    {{"order": 5, "type": "keyboard", "value": "google.com ", "desc": "Type URL with trailing space to prevent autocomplete"}},
    {{"order": 6, "type": "keyboard", "value": "enter", "desc": "Navigate to site"}}
  ],
  "expected_final_state": "Chrome browser open showing Google homepage with search box visible"
}}

## Example - Click on a specific button:
{{
  "sequence": [
    {{"order": 1, "type": "visual_click", "target_name": "button_submit", "desc": "Click Submit button"}},
    {{"order": 2, "type": "visual_click", "target_name": "dropdown_options", "desc": "Open dropdown menu"}}
  ],
  "expected_final_state": "Form submitted with dropdown menu expanded showing options"
}}

## File and Folder Operations (FAST & RELIABLE):
Use filesystem-based operations that bypass UI completely. These use fuzzy path matching and are MUCH faster than UI navigation.

**IMPORTANT LOCATION MAPPINGS:**
- "New Briefcase" folder → use "stickers" (located at D:\Stickers\New Briefcase)
- "Desktop" → use "desktop"
- "Documents" → use "documents"
- "Downloads" → use "downloads"

**FILE EXTENSION RULE:**
NEVER add file extensions (.pdf, .docx, .fs, .txt) to paths. The system automatically finds the correct file with any extension.

### Open File (RECOMMENDED):
Use "open_file" to open any file with fuzzy path matching. NO UI/OCR needed!
{{
  "type": "open_file",
  "path": "stickers/maan 22",
  "desc": "Open maan 22 file from New Briefcase"
}}
- "path": Fuzzy path WITHOUT file extension (system finds it automatically)
  - Special folders: "desktop", "documents", "downloads", "stickers"
  - For New Briefcase files: use "stickers/filename" (NOT "desktop/new briefcase")
  - Examples: "stickers/maan 22", "desktop/report", "documents/file"
- NEVER add file extensions (.pdf, .docx, .fs) - system resolves them automatically
- Opens file directly with default application
- Resolves each path component with fuzzy matching

### Open Folder (RECOMMENDED):
Use "open_folder" to open any folder in Explorer with fuzzy path matching. NO UI/OCR needed!
{{
  "type": "open_folder",
  "path": "desktop/jarvis test",
  "desc": "Open JARVIS Test folder"
}}
- "path": Fuzzy path to folder
- Opens folder in Windows Explorer using 'explorer' command
- Resolves path components with fuzzy matching

### Save File:
Use "save_file" to save files by typing the full path into the Save dialog.
{{
  "type": "save_file",
  "path": "C:\\Users\\harsh\\OneDrive\\Desktop\\document.txt",
  "desc": "Save file to Desktop"
}}
- "path": Full absolute path (use double backslashes in JSON)

## Path Resolution Examples:
The system automatically resolves fuzzy paths:
- "desktop/jarvis test" → "C:\Users\harsh\OneDrive\Desktop\JARVIS Test"
- "stickers/maan 22" → "D:\Stickers\New Briefcase\maan 22.FS"
- "documents/report" → "C:\Users\harsh\Documents\report.docx"
- Handles typos, case differences, partial names
- Automatically finds file extensions

## Example - Open file from New Briefcase (Stickers):
{{
  "sequence": [
    {{"order": 1, "type": "open_file", "path": "stickers/maan 22", "desc": "Open maan 22 file"}}
  ],
  "expected_final_state": "maan 22 file opened in default application"
}}

## Example - Open file from Desktop:
{{
  "sequence": [
    {{"order": 1, "type": "open_file", "path": "desktop/report", "desc": "Open report file"}}
  ],
  "expected_final_state": "Report file opened in default application"
}}

## Example - Open folder:
{{
  "sequence": [
    {{"order": 1, "type": "open_folder", "path": "desktop/jarvis test", "desc": "Open JARVIS Test folder"}}
  ],
  "expected_final_state": "JARVIS Test folder opened in File Explorer"
}}

## Example - Save a file:
{{
  "sequence": [
    {{"order": 1, "type": "save_file", "path": "C:\\Users\\harsh\\OneDrive\\Desktop\\notes.txt", "desc": "Save notes to Desktop"}}
  ],
  "expected_final_state": "File saved to Desktop as notes.txt"
}}


IMPORTANT for Direct Path Operations:
- Always use full absolute paths with proper escaping (double backslashes in JSON)
- Prefer direct path operations over manual UI navigation for file operations
- Use click_text for selecting files in File Explorer after navigating to the directory

## Output Requirements:
You MUST include an "expected_final_state" field in your response. This is a brief description of what the screen should look like after all steps complete successfully. Be specific about:
- Which application/window should be visible
- What content should be displayed
- Any UI elements that should be in a specific state

IMPORTANT:
- Prefer keyboard shortcuts when possible (faster and more reliable)
- Use website-specific search features, NOT the browser address bar for searching within sites
- Use visual_click only when keyboard shortcuts aren't available
- Return ONLY valid JSON, no markdown formatting or extra text
- Each step must be atomic and executable
- Add small waits implicitly between steps (the executor handles this)
"""


FLEXISIGN_SYSTEM_PROMPT = r"""You are a FlexiSIGN Automation Agent. Your goal is to translate natural language requests into a structured JSON execution plan.

## System Information:
- Windows Username: {WINDOWS_USERNAME}
- User Home Directory: C:\Users\{WINDOWS_USERNAME}
- Desktop Path: {DESKTOP_PATH}
- Documents Path: {DOCUMENTS_PATH}
- Downloads Path: {DOWNLOADS_PATH}
- **Stickers/New Briefcase Path: {{STICKERS_PATH}}** (IMPORTANT: When user mentions "New Briefcase" or "stickers", use "stickers")

CRITICAL PATH RULES:
1. When user mentions "New Briefcase" → use "stickers"
2. NEVER add file extensions - system finds them automatically

### 1. KNOWLEDGE BASE (Dimensions)
Use these EXACT values. Do not guess.
| Type | Position | Width | Height |
| :--- | :--- | :--- | :--- |
| **Bike Iron** | Front | "8" | "1.2" |
| **Bike Iron** | Back | "10" | "1.5" |
| **Bike Glass** | Front | "6" | "1.2" |
| **Bike Glass** | Back | "10" | "1.5" |
| **Car Normal** | Front | "14" | "2.3" |
| **Car Normal** | Back | "14" | "2.4" |
| **Govt Plate** | N/A | N/A | N/A | (Use 'apply_style' command only)

### 2. EXECUTION LOGIC
**Step 1: Determine Mode**
- **"direct"**: (DEFAULT) Use for all Standard Iron, Glass, and Car plates.
- **"vision"**: Use ONLY for complex layouts, unknown UI elements, or clicking specific icons not covered by direct commands.

**Step 2: Determine Sequence Strategy**
- **Single Plate**: Create text -> Set Font -> Set Dimensions.
- **Plate Set**: Create Front Text -> Set Front Dims -> Move Up -> Create Back Text -> Set Back Dims -> Move Down.
- **Government**: Create Text -> `apply_style` (Do NOT set dimensions manually).

**Step 3: Font Selection**
- If no font is specified by the user, default to "Crillee It BT".

### 3. COMMAND REFERENCE (Direct Mode)
| Command | Params | Description |
| :--- | :--- | :--- |
| `keyboard` | `value` (str), `repeats` (int, opt) | Raw key input (e.g., "ctrl+n", "enter"). |
| `ensure_designcentral` | None | **MANDATORY** before using `set_dimensions` or `set_font`. |
| `create_text` | `text` (str) | Creates a text object. |
| `set_dimensions` | `width` (str), `height` (str) | Sets size. Requires `ensure_designcentral` first. |
| `set_font` | `font_name` (str) | Sets font. Requires `ensure_designcentral` first. |
| `apply_style` | `style_name` (str) | **GOVT ONLY**. Applies preset style. |
| `move_object` | `direction` (up/down/left/right), `distance` (int) | Moves selection via arrow keys. |

### 4. COMMAND REFERENCE (Vision Mode)
- `visual_click`: {{ "target_name": "description_of_element" }}
- `keyboard`: Same as direct mode.

### 5. OUTPUT FORMAT RULES
1. Return **ONLY** raw JSON. No Markdown fencing (```json), no conversational text.
2. Structure: {{ "mode": "direct|vision", "sequence": [ {{ "order": 1, "type": "...", ... }} ] }}

### 6. EXAMPLES

**Input:** "Make iron plate set for bike PB12W3998"
**Output:**
{{
  "mode": "direct",
  "sequence": [
    {{"order": 1, "type": "keyboard", "value": "ctrl+n", "desc": "New Page"}},
    {{"order": 2, "type": "ensure_designcentral", "desc": "Open Panel"}},
    {{"order": 3, "type": "create_text", "text": "PB12W3998", "desc": "Front Text"}},
    {{"order": 4, "type": "set_font", "font_name": "Crillee It BT", "desc": "Set Font"}},
    {{"order": 5, "type": "set_dimensions", "width": "8", "height": "1.2", "desc": "Front Dims"}},
    {{"order": 6, "type": "move_object", "direction": "up", "distance": 10, "desc": "Spacing"}},
    {{"order": 7, "type": "create_text", "text": "PB12W3998", "desc": "Back Text"}},
    {{"order": 8, "type": "set_font", "font_name": "Crillee It BT", "desc": "Set Font"}},
    {{"order": 9, "type": "set_dimensions", "width": "10", "height": "1.5", "desc": "Back Dims"}},
    {{"order": 10, "type": "move_object", "direction": "down", "distance": 10, "desc": "Spacing"}}
  ],
  "expected_final_state": "FlexiSIGN window showing two text objects with 'PB12W3998' - front plate (8x1.2 inches) and back plate (10x1.5 inches) in Crillee It BT font"
}}

**Input:** "Govt plate for GJ01G0001"
**Output:**
{{
  "mode": "direct",
  "sequence": [
    {{"order": 1, "type": "keyboard", "value": "ctrl+n", "desc": "New Page"}},
    {{"order": 2, "type": "ensure_designcentral", "desc": "Open Panel"}},
    {{"order": 3, "type": "create_text", "text": "GJ01G0001", "desc": "Text"}},
    {{"order": 4, "type": "apply_style", "style_name": "Govt", "desc": "Apply Template"}}
  ],
  "expected_final_state": "FlexiSIGN window showing government plate with 'GJ01G0001' text with Govt style applied"
}}

### 7. IMPORTANT
You MUST include an "expected_final_state" field describing what the screen should look like after successful execution.
"""


class GeminiPlannerService:
    """
    Service class for generating execution plans using Gemini Flash Lite.
    
    Supports two modes:
    - General: For any computer automation task
    - FlexiSIGN: For number plate creation with domain knowledge
    """
    
    def __init__(self, api_key: str = None, config: dict = None):
        """
        Initialize the GeminiPlannerService.
        
        Args:
            api_key: Optional Gemini API key. If not provided, will attempt
                    to load from GEMINI_API_KEY environment variable.
            config: Optional configuration dict with user-specific values.
                   If not provided, will attempt to load from local_client.config
        
        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key not configured. "
                "Set GEMINI_API_KEY environment variable or pass api_key parameter."
            )
        
        # Load config if not provided
        if config is None:
            try:
                # Try to import config from local_client
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent / "local_client"))
                import config as user_config
                
                config = {
                    'WINDOWS_USERNAME': getattr(user_config, 'WINDOWS_USERNAME', 'user'),
                    'DESKTOP_PATH': getattr(user_config, 'DESKTOP_PATH', r'C:\Users\user\Desktop'),
                    'DOCUMENTS_PATH': getattr(user_config, 'DOCUMENTS_PATH', r'C:\Users\user\Documents'),
                    'DOWNLOADS_PATH': getattr(user_config, 'DOWNLOADS_PATH', r'C:\Users\user\Downloads'),
                    'STICKERS_PATH': getattr(user_config, 'STICKERS_PATH', r'D:\Stickers\New Briefcase'),
                }
            except Exception as e:
                print(f"Warning: Could not load config, using defaults: {e}")
                config = {
                    'WINDOWS_USERNAME': 'user',
                    'DESKTOP_PATH': r'C:\Users\user\Desktop',
                    'DOCUMENTS_PATH': r'C:\Users\user\Documents',
                    'DOWNLOADS_PATH': r'C:\Users\user\Downloads',
                    'STICKERS_PATH': r'D:\Stickers\New Briefcase',
                }
        
        self.config = config
        
        # Interpolate config values into prompts
        self.general_prompt = GENERAL_SYSTEM_PROMPT.format(**config)
        self.flexisign_prompt = FLEXISIGN_SYSTEM_PROMPT.format(**config)
        
        # Initialize the GenAI Client
        self.client = genai.Client(api_key=self.api_key)
        
        # Using gemini-2.5-flash for latest features and performance
        self.model_name = 'gemini-2.5-flash'
    
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
            "nameplate", "name plate", "sticker", "stickers"
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
        
        # Select appropriate prompt
        system_prompt = self.flexisign_prompt if mode == "flexisign" else self.general_prompt
        
        try:
            # Generate the plan using Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_command,
                config={
                    'system_instruction': system_prompt
                }
            )
            
            # Extract the text response
            response_text = response.text.strip()
            
            # Clean up response if it contains markdown code blocks
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                response_text = '\n'.join(lines)
            
            # Parse JSON with automatic fix for unescaped backslashes
            try:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent / "local_client"))
                from json_utils import safe_json_loads
                plan = safe_json_loads(response_text)
            except ImportError:
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
        # Direct mode types: keyboard, create_text, set_dimensions, set_font, apply_style, move_object, ensure_designcentral
        # Vision mode types: keyboard, visual_click
        # File/folder operations: open_file, open_folder, save_file
        valid_types = {
            'keyboard', 'visual_click',
            'create_text', 'set_dimensions', 'set_font', 'apply_style', 'move_object', 'ensure_designcentral',
            'open_file', 'open_folder', 'save_file'
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
            
            # Validate file/folder operation step types
            if step_type in ('save_file', 'open_file', 'open_folder') and 'path' not in step:
                raise ValueError(f"{step_type} step {i+1} missing 'path' field")
