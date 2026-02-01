"""
Planner Service for Two-Model Pipeline

This module provides the PlannerService class that uses an LLM (Gemini or OpenAI)
to convert natural language commands into structured execution plans.
Supports both FlexiSIGN-specific tasks and general computer automation.
"""

import os
import json
from dotenv import load_dotenv
from llm_provider import GeminiProvider, OpenAIProvider

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


GENERAL_SYSTEM_PROMPT = r"""You are JARVIS, an AI that automates Windows computer tasks by converting commands into structured execution plans.

## System Info
- Username: {WINDOWS_USERNAME}
- Paths: Desktop={DESKTOP_PATH}, Documents={DOCUMENTS_PATH}, Downloads={DOWNLOADS_PATH}
- Stickers: {STICKERS_PATH} (when user says "New Briefcase" or "stickers")
- ALWAYS use {DESKTOP_PATH} for Desktop (OneDrive sync may redirect %USERPROFILE%\Desktop)

## Execution Priority (STRICT)
1. **Shell commands** - mkdir, type nul, start (fastest, most reliable)
2. **Direct filesystem** - open_file, open_folder, write_file, save_file
3. **Keyboard shortcuts** - When deterministic
4. **UI navigation** - LAST RESORT (visual_click, right-click menus)

FORBIDDEN: Creating folders/files via right-click when commands work.

## Path Rules
- "New Briefcase" → "stickers" or "{STICKERS_PATH}"
- NEVER add file extensions - system auto-resolves them
- Use fuzzy paths: "stickers/maan 22" finds "maan 22.FS"

## Output Format
Return JSON with "sequence" array + "expected_final_state" string.

### Step Types

**keyboard**: Keys/text input
```json
{{"order":1,"type":"keyboard","value":"ctrl+s","desc":"Save file"}}
{{"order":2,"type":"keyboard","value":"notepad","desc":"Type app name"}}
```
- Shortcuts: "ctrl+c", "alt+tab", "win+r"
- Special keys: "enter", "tab", "escape", "f1"-"f12", arrows
- Text: plain strings
- Optional: "repeats": N

**click_text_fast** (PREFERRED - 10x faster than visual_click): OCR-based text clicking
```json
{{"order":1,"type":"click_text_fast","window_title":"WhatsApp","text":"Harshit","desc":"Click contact"}}
```
- Fuzzy matches partial text
- Use for: buttons, menus, contacts, filenames

**visual_click** (SLOW - icons/images only):
```json
{{"order":1,"type":"visual_click","target_name":"icon_chrome","desc":"Click Chrome icon"}}
```
- Only when no readable text exists

**shell_command**: Windows commands
```json
{{"order":1,"type":"shell_command","command":"mkdir \"%USERPROFILE%\\Desktop\\Project\"","desc":"Create folder"}}
```

| Command | Syntax |
|---------|--------|
| Create folder | `mkdir "Folder Name"` |
| Create file | `type nul > "file.txt"` |
| Open file | `start "" "full\path\file.txt"` |
| Open folder | `explorer "%USERPROFILE%\Desktop\Folder"` |
| Chain | `cmd1 & cmd2` |

Rules: Always quote paths with spaces. Use full paths with `start`. System waits 3-5s after `start`.

**File Operations** (No UI needed):

| Type | Required Fields | Notes |
|------|----------------|-------|
| open_file | path | Fuzzy, no extension: `"stickers/maan 22"` |
| open_folder | path | Opens in Explorer |
| save_file | path | Full absolute path |
| write_file | path, content | Creates/overwrites, auto-creates dirs |
| read_file | path | Stores content for later use |
| append_file | path, content | Adds to existing file |
| create_directory | path | Creates folder hierarchy |
| replace_in_file | path, old_text, new_text | Find & replace |
| modify_lines | path, line_number, new_content | Edit specific line |

## Key Patterns

### Open App
```json
{{"order":1,"type":"keyboard","value":"win","desc":"Open Start"}},
{{"order":2,"type":"keyboard","value":"chrome","desc":"Search"}},
{{"order":3,"type":"keyboard","value":"enter","desc":"Launch"}}
```

### Navigate URL (add trailing space to prevent autocomplete)
```json
{{"order":1,"type":"keyboard","value":"ctrl+l","desc":"Focus address bar"}},
{{"order":2,"type":"keyboard","value":"youtube.com ","desc":"URL with space"}},
{{"order":3,"type":"keyboard","value":"enter","desc":"Go"}}
```

### Search on Website (use site's search, NOT address bar)
- YouTube: "/" focuses search
- Then type query + Enter

### Killer Combo (File Creation → Edit → Save)
```json
{{"order":1,"type":"shell_command","command":"type nul > \"%USERPROFILE%\\Desktop\\notes.txt\"","desc":"Create file"}},
{{"order":2,"type":"shell_command","command":"start \"\" \"%USERPROFILE%\\Desktop\\notes.txt\"","desc":"Open"}},
{{"order":3,"type":"keyboard","value":"Hello World!","desc":"Type"}},
{{"order":4,"type":"keyboard","value":"ctrl+s","desc":"Save"}}
```

### Create Folder + Open
```json
{{"order":1,"type":"shell_command","command":"mkdir \"%USERPROFILE%\\Desktop\\AI Lab\"","desc":"Create folder"}},
{{"order":2,"type":"shell_command","command":"explorer \"%USERPROFILE%\\Desktop\\AI Lab\"","desc":"Open in Explorer"}}
```

### Write Code File (RECOMMENDED for code)
```json
{{"order":1,"type":"write_file","path":"%USERPROFILE%\\Desktop\\sort.py","content":"def sort(arr):\\n    return sorted(arr)\\n\\nprint(sort([3,1,2]))","desc":"Write Python file"}},
{{"order":2,"type":"shell_command","command":"code \"%USERPROFILE%\\Desktop\\sort.py\"","desc":"Open in VS Code"}}
```
Advantages: No UI, handles long code, preserves formatting, instant.

### Modify Existing File (READ → MODIFY)
```json
{{"order":1,"type":"read_file","path":"%USERPROFILE%\\Desktop\\form.txt","desc":"Read current content"}},
{{"order":2,"type":"replace_in_file","path":"%USERPROFILE%\\Desktop\\form.txt","old_text":"Name: John Doe","new_text":"Name: Harshit Singla","desc":"Update name"}}
```
CRITICAL: `old_text` must be COMPLETE text to replace (not just "Name:").

### Open File (Fuzzy Path)
```json
{{"order":1,"type":"open_file","path":"stickers/maan 22","desc":"Open from New Briefcase"}}
```

### WhatsApp Message
```json
{{"order":1,"type":"keyboard","value":"win","desc":"Start"}},
{{"order":2,"type":"keyboard","value":"whatsapp","desc":"Search"}},
{{"order":3,"type":"keyboard","value":"enter","desc":"Launch"}},
{{"order":4,"type":"click_text_fast","window_title":"WhatsApp","text":"Harshit","desc":"Select contact"}},
{{"order":5,"type":"keyboard","value":"Hello!","desc":"Type message"}},
{{"order":6,"type":"keyboard","value":"enter","desc":"Send"}}
```

### VS Code Workflow
```json
{{"order":1,"type":"shell_command","command":"code \"%USERPROFILE%\\Desktop\\Project\"","desc":"Open in VS Code"}},
{{"order":2,"type":"keyboard","value":"ctrl+`","desc":"Open terminal"}},
{{"order":3,"type":"keyboard","value":"python main.py","desc":"Run command"}},
{{"order":4,"type":"keyboard","value":"enter","desc":"Execute"}}
```

## Rules Summary
1. Prefer shell_command > write_file > keyboard > click_text_fast > visual_click
2. NEVER add file extensions to paths
3. Quote all paths with spaces
4. Use full absolute paths with `start` command
5. Always end folder creation by opening in Explorer
6. For file edits: read_file FIRST, then replace_in_file
7. For code: use write_file (not keyboard typing)
8. Ctrl+N only when user explicitly says "new window/document"
9. Return ONLY valid JSON

## expected_final_state
REQUIRED field describing the screen after completion:
- Which window/app is visible
- What content is displayed
- Specific UI state
```

---

## Optimization Summary

| Section | Original | Optimized | Savings |
|---------|----------|-----------|---------|
| System Info | ~200 tokens | ~100 tokens | 50% |
| Rules/Priorities | ~400 tokens | ~150 tokens | 62% |
| Step Types | ~1200 tokens | ~400 tokens | 67% |
| Shell Commands | ~1500 tokens | ~300 tokens | 80% |
| File Operations | ~1800 tokens | ~400 tokens | 78% |
| Examples | ~2000 tokens | ~700 tokens | 65% |
| Patterns | ~400 tokens | ~200 tokens | 50% |
| **Total** | **~7500 tokens** | **~4000 tokens** | **~47%** |

### Key Changes Made:
1. **Merged redundant sections** - Shell commands + file ops consolidated
2. **Used tables** - Command syntax, step types
3. **Removed duplicate examples** - Kept one representative per pattern
4. **Condensed JSON** - Removed extra whitespace, combined lines
5. **Eliminated repetitive warnings** - Single mention of critical rules
6. **Shortened descriptions** - Same meaning, fewer words
7. **Removed obvious explanations** - LLMs understand context
8. **Combined similar patterns** - Killer Combo covers multiple use cases
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


class PlannerService:
    """
    Service class for generating execution plans using an LLM.
    
    Supports two modes:
    - General: For any computer automation task
    - FlexiSIGN: For number plate creation with domain knowledge
    """
    
    def __init__(self, api_key: str = None, config: dict = None):
        """
        Initialize the PlannerService.
        
        Args:
            api_key: Optional API key override. 
            config: Optional configuration dict with user-specific values.
        """
        # Load config if not provided
        if config is None:
            try:
                # Try to import config from local_client
                import sys
                from pathlib import Path
                local_client_path = Path(__file__).parent.parent / "local_client"
                if str(local_client_path) not in sys.path:
                    sys.path.insert(0, str(local_client_path))
                import config as user_config
                
                config = {
                    'WINDOWS_USERNAME': getattr(user_config, 'WINDOWS_USERNAME', 'user'),
                    'DESKTOP_PATH': getattr(user_config, 'DESKTOP_PATH', r'C:\Users\user\Desktop'),
                    'DOCUMENTS_PATH': getattr(user_config, 'DOCUMENTS_PATH', r'C:\Users\user\Documents'),
                    'DOWNLOADS_PATH': getattr(user_config, 'DOWNLOADS_PATH', r'C:\Users\user\Downloads'),
                    'STICKERS_PATH': getattr(user_config, 'STICKERS_PATH', r'D:\Stickers\New Briefcase'),
                }
                self.llm_provider = getattr(user_config, 'LLM_PROVIDER', 'gemini')
                self.openai_key = getattr(user_config, 'OPENAI_API_KEY', '')
            except Exception as e:
                print(f"Warning: Could not load config, using defaults: {e}")
                config = {
                    'WINDOWS_USERNAME': 'user',
                    'DESKTOP_PATH': r'C:\Users\user\Desktop',
                    'DOCUMENTS_PATH': r'C:\Users\user\Documents',
                    'DOWNLOADS_PATH': r'C:\Users\user\Downloads',
                    'STICKERS_PATH': r'D:\Stickers\New Briefcase',
                }
                self.llm_provider = 'gemini'
                self.openai_key = ''
        
        # Ensure LLM provider settings are available
        self.llm_provider = config.get('LLM_PROVIDER', getattr(self, 'llm_provider', 'gemini'))
        self.openai_key = config.get('OPENAI_API_KEY', getattr(self, 'openai_key', ''))

        self.config = config
        
        # Interpolate config values into prompts
        self.general_prompt = GENERAL_SYSTEM_PROMPT.format(**config)
        self.flexisign_prompt = FLEXISIGN_SYSTEM_PROMPT.format(**config)
        
        # Initialize the Provider
        self.init_provider(api_key)
        
    def init_provider(self, str_api_key_override=None):
        """Initialize the LLM provider based on configuration."""
        if self.llm_provider == 'openai':
             api_key = str_api_key_override or self.openai_key or os.getenv('OPENAI_API_KEY')
             if not api_key:
                 raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY in config or env.")
             self.provider = OpenAIProvider(api_key=api_key)
        else:
             # Default to Gemini
             api_key = str_api_key_override or os.getenv('GEMINI_API_KEY')
             if not api_key:
                 raise ValueError("Gemini API key not configured. Set GEMINI_API_KEY environment variable.")
             self.provider = GeminiProvider(api_key=api_key)
        
        print(f"Initialized Planner with {self.llm_provider} provider")
    
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
        """
        if not user_command or not user_command.strip():
            raise ValueError("User command cannot be empty")
        
        # Auto-detect mode if not specified
        if mode is None:
            mode = self.detect_mode(user_command)
        
        # Select appropriate prompt
        system_prompt = self.flexisign_prompt if mode == "flexisign" else self.general_prompt
        
        try:
            # Generate the content using the abstract provider
            response_text = self.provider.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_command
            )
            
            response_text = response_text.strip()
            
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
                # Add local_client to sys.path to import json_utils
                local_client_path = Path(__file__).parent.parent / "local_client"
                if str(local_client_path) not in sys.path:
                    sys.path.insert(0, str(local_client_path))
                from json_utils import safe_json_loads
                plan = safe_json_loads(response_text)
            except ImportError:
                plan = json.loads(response_text)
            
            # Validate the plan structure
            self._validate_plan(plan)
            
            # Post-process content fields to handle escaped newlines and code fences
            if 'sequence' in plan:
                for step in plan['sequence']:
                    if step.get('type') == 'write_file' and 'content' in step:
                        content = step['content']
                        # Remove markdown code fences if present
                        if content.startswith('```'):
                            lines = content.split('\n')
                            # Remove first line (```python or ```)
                            lines = lines[1:]
                            # Remove last line if it's ```
                            if lines and lines[-1].strip() == '```':
                                lines = lines[:-1]
                            content = '\n'.join(lines)
                        # Update the step with cleaned content
                        step['content'] = content
            
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
        # Vision mode types: keyboard, visual_click, click_text_fast
        # File/folder operations: open_file, open_folder, save_file
        # Shell operations: shell_command
        # Plane 2 workspace control: write_file, read_file, append_file, create_directory
        # Intelligent file editing: replace_in_file, modify_lines, insert_at_line, delete_lines
        valid_types = {
            'keyboard', 'visual_click', 'click_text_fast',
            'create_text', 'set_dimensions', 'set_font', 'apply_style', 'move_object', 'ensure_designcentral',
            'open_file', 'open_folder', 'save_file', 'shell_command',
            'write_file', 'read_file', 'append_file', 'create_directory',
            'replace_in_file', 'modify_lines', 'insert_at_line', 'delete_lines'
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
            
            if step_type == 'click_text_fast':
                if 'window_title' not in step:
                    raise ValueError(f"click_text_fast step {i+1} missing 'window_title' field")
                if 'text' not in step:
                    raise ValueError(f"click_text_fast step {i+1} missing 'text' field")
            
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
            
            # Validate shell_command step type
            if step_type == 'shell_command' and 'command' not in step:
                raise ValueError(f"shell_command step {i+1} missing 'command' field")
            
            # Validate Plane 2 workspace control step types
            if step_type == 'write_file':
                if 'path' not in step:
                    raise ValueError(f"write_file step {i+1} missing 'path' field")
                if 'content' not in step:
                    raise ValueError(f"write_file step {i+1} missing 'content' field")
            
            if step_type in ('read_file', 'create_directory') and 'path' not in step:
                raise ValueError(f"{step_type} step {i+1} missing 'path' field")
            
            if step_type == 'append_file':
                if 'path' not in step:
                    raise ValueError(f"append_file step {i+1} missing 'path' field")
                if 'content' not in step:
                    raise ValueError(f"append_file step {i+1} missing 'content' field")
            
            # Validate intelligent file editing operations
            if step_type == 'replace_in_file':
                if 'path' not in step:
                    raise ValueError(f"replace_in_file step {i+1} missing 'path' field")
                if 'old_text' not in step:
                    raise ValueError(f"replace_in_file step {i+1} missing 'old_text' field")
                if 'new_text' not in step:
                    raise ValueError(f"replace_in_file step {i+1} missing 'new_text' field")
            
            if step_type == 'modify_lines':
                if 'path' not in step:
                    raise ValueError(f"modify_lines step {i+1} missing 'path' field")
                if 'line_number' not in step:
                    raise ValueError(f"modify_lines step {i+1} missing 'line_number' field")
                if 'new_content' not in step:
                    raise ValueError(f"modify_lines step {i+1} missing 'new_content' field")
            
            if step_type == 'insert_at_line':
                if 'path' not in step:
                    raise ValueError(f"insert_at_line step {i+1} missing 'path' field")
                if 'line_number' not in step:
                    raise ValueError(f"insert_at_line step {i+1} missing 'line_number' field")
                if 'content' not in step:
                    raise ValueError(f"insert_at_line step {i+1} missing 'content' field")
            
            if step_type == 'delete_lines':
                if 'path' not in step:
                    raise ValueError(f"delete_lines step {i+1} missing 'path' field")
                if 'start_line' not in step:
                    raise ValueError(f"delete_lines step {i+1} missing 'start_line' field")
