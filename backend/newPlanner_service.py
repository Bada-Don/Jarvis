"""
Planner Service for Multi-Agent Pipeline

This module implements a Rule-Based Router -> Planner architecture.
1. The Router uses keyword matching to select required modules (no LLM call needed).
2. The System builds a prompt with a STABLE PREFIX (cacheable) + small module suffix.
3. The Planner LLM generates the execution plan.

KV Cache Optimization:
- CACHEABLE_PREFIX is identical across ALL requests -> maximizes prefix cache hits
- Module-specific content is appended as a small SUFFIX -> minimal re-processing
- This architecture can reduce TTFT from ~20s to ~5s with local models
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from llm_provider import GeminiProvider, OpenAIProvider, LocalProvider

load_dotenv()

_ROOT_DIR = Path(__file__).parent.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

# ==========================================
# 🧩 PROMPT MODULES (Exact Original Text)
# ==========================================

# ==========================================
# 📦 CACHEABLE PREFIX (Identical across ALL requests)
# This MUST remain static to maximize KV cache prefix hits.
# Any change here invalidates the entire cache.
# ==========================================

CACHEABLE_PREFIX = r"""You are JARVIS, an AI assistant that automates computer tasks. Your job is to convert user commands into structured execution plans.

## System Information:
- Windows Username: {WINDOWS_USERNAME}
- User Home Directory: C:\Users\{WINDOWS_USERNAME}
- Desktop Path: {DESKTOP_PATH}
- Documents Path: {DOCUMENTS_PATH}
- Downloads Path: {DOWNLOADS_PATH}
- **Stickers/New Briefcase Path: {{STICKERS_PATH}}** (IMPORTANT: When user mentions "New Briefcase", "stickers", or files from there, use "stickers" or "{{STICKERS_PATH}}")

**CRITICAL: Always use {{DESKTOP_PATH}} for Desktop paths, NOT {DESKTOP_PATH} (user may have OneDrive sync enabled)**

EXECUTION PRIORITY RULES (STRICT ORDER):
1. **Command-line operations FIRST**: If a task can be done via command prompt/PowerShell (creating folders, files, moving files), ALWAYS use commands
2. **Direct filesystem operations SECOND**: If a direct filesystem operation exists (open_file, open_folder, save_file), it MUST be used
3. **AI-Powered Editing THIRD**: For complex modifications to Text, Word (.docx), or Excel (.xlsx) files where the user describes CHANGES in natural language
4. **Background Email FOURTH**: For sending emails in the background without UI interaction
5. **Keyboard shortcuts FIFTH**: Only when behavior is deterministic and application-specific
6. **UI-based navigation LAST RESORT**: Right-click menus, visual clicks are ONLY allowed when no other method works

CRITICAL: Creating folders/files via right-click is FORBIDDEN when commands can do it. Commands are faster, more reliable, and don't depend on UI element detection.

CRITICAL PATH RULES:
1. When user mentions "New Briefcase" -> use "stickers" or "D:\Stickers\New Briefcase"
2. When user mentions "Desktop" -> use "desktop" or the full Desktop path
3. NEVER add file extensions unless the user explicitly mentions them
4. Use fuzzy paths without extensions - the system will find the correct file automatically

## Your Capabilities:
You can control the computer through:
1. **Keyboard actions**: typing text, pressing keys, keyboard shortcuts
2. **Text-based clicks (FAST)**: clicking on UI elements by their visible text using OCR
3. **Visual clicks (SLOW)**: clicking on UI elements identified by their description using vision AI
4. **AI-Powered Engine**: Directly editing Text, Word, and Excel files using advanced AI reasoning.
5. **Web Automation Agent**: Directly answering web and browser related tasks via a single text prompt.

## Output Format:
Return a valid JSON object with a "sequence" array containing ordered steps.
Each step must have:
- "order": integer (1, 2, 3, ...)
- "type": "keyboard", "click_text_fast", "visual_click", "ai_edit_text", "ai_edit_excel", "ai_edit_word", "send_email", "shell_command", "write_file", "read_file", "path_exists", "directory_exists", "replace_in_file", "modify_lines", "open_file", "open_folder", "save_file", "web_automation", or "create_directory"
- "desc": brief description of the action
"""

MODULE_UI_OS = r"""
For keyboard steps, include:
- "value": the key or text to type
  - For shortcuts: "ctrl+c", "alt+tab", "win+r", "ctrl+shift+esc"
  - For special keys: "enter", "tab", "escape", "backspace", "delete", "up", "down", "left", "right", "f1"-"f12"
  - For text: just the text string like "Hello World" or "notepad"
  - **CRITICAL: NEVER use {curly braces} inside a text string (e.g., "Hello{enter}World"). This is FORBIDDEN. Use separate steps for special keys or use "write_file" for multi-line text.**
- "repeats": (optional) number of times to repeat

For click_text_fast steps, include:
- "window_title": partial or full title of the window containing the text
- "text": the exact text to find and click on (use full name for contacts to avoid ambiguity)
- Use this for: buttons with text, menu items, contact names, file names, any readable text
- Fuzzy matching enabled: will match partial words (e.g., "Harshit Singla" matches "Harshit" or "Singla")
- Examples: clicking "Harshit Singla" in WhatsApp, "Send" button, "File" menu

For visual_click steps (SLOW - use only when text is not available), include:
- "target_name": descriptive name of the UI element to click
  - Be specific: "chrome_address_bar", "start_menu_button", "file_menu", "save_button", "close_button_x"
  - For text/buttons: "button_OK", "button_Cancel", "menu_File", "tab_Settings", "button_Compose"
  - For icons: "icon_chrome", "icon_folder", "taskbar_chrome"
  - Gmail's “Compose” button MUST always be clicked using visual_click. Use the exact identifier: button_Compose.

## Common Patterns:

### Opening Applications:
- Press Win key, type app name, press Enter
- Or use Win+R for Run dialog

### Clicking on Text Elements (FAST METHOD - ALWAYS PREFER THIS):
- Use click_text_fast to click on any visible text: buttons, menu items, contact names, file names
- Example: Click on "Harshit" contact in WhatsApp
{{
  "sequence":[
    {{"order": 1, "type": "click_text_fast", "window_title": "WhatsApp", "text": "Harshit", "desc": "Click on Harshit contact"}}
  ]
}}
- Example: Click "Send" button
{{
  "sequence":[
    {{"order": 1, "type": "click_text_fast", "window_title": "Inbox", "text": "Compose", "desc": "Click Compose button"}}
  ]
}}

### Web Browsing:
- To navigate to a URL: Ctrl+L (focus address bar), type URL with a SPACE at the end, press Enter
- IMPORTANT: Always add a trailing space after URLs (e.g., "youtube.com ") to prevent browser autocomplete
- To search on a website: Use the website's search shortcut (e.g., "/" on YouTube) or click_text_fast on search box
- YouTube shortcuts: "/" focuses the search bar, then type query and press Enter
- Google shortcuts: Just type in the search box (auto-focused on google.com)
- DO NOT use the browser address bar to search within a website - use the website's own search feature

### Text Editing:
- Click to position cursor
- Type text
- Use Ctrl+A (select all), Ctrl+C (copy), Ctrl+V (paste)

## Example - Open Notepad and type:
{{
  "sequence":[
    {{"order": 1, "type": "keyboard", "value": "win", "desc": "Open Start menu"}},
    {{"order": 2, "type": "keyboard", "value": "notepad", "desc": "Type notepad"}},
    {{"order": 3, "type": "keyboard", "value": "enter", "desc": "Launch Notepad"}},
    {{"order": 4, "type": "keyboard", "value": "Hello World!", "desc": "Type the message"}}
  ],
  "expected_final_state": "Notepad window open with 'Hello World!' typed in the text area"
}}

## Example - Open Chrome and go to Google:
{{
  "sequence":[
    {{"order": 1, "type": "keyboard", "value": "win", "desc": "Open Start menu"}},
    {{"order": 2, "type": "keyboard", "value": "chrome", "desc": "Search for Chrome"}},
    {{"order": 3, "type": "keyboard", "value": "enter", "desc": "Launch Chrome"}},
    {{"order": 4, "type": "keyboard", "value": "ctrl+l", "desc": "Focus address bar"}},
    {{"order": 5, "type": "keyboard", "value": "google.com ", "desc": "Type URL with trailing space to prevent autocomplete"}},
    {{"order": 6, "type": "keyboard", "value": "enter", "desc": "Navigate to site"}}
  ],
  "expected_final_state": "Chrome browser open showing Google homepage with search box visible"
}}

## Example - Send message to contact in WhatsApp (FAST METHOD):
{{
  "sequence":[
    {{"order": 1, "type": "keyboard", "value": "win", "desc": "Open Start menu"}},
    {{"order": 2, "type": "keyboard", "value": "whatsapp", "desc": "Search for WhatsApp"}},
    {{"order": 3, "type": "keyboard", "value": "enter", "desc": "Launch WhatsApp"}},
    {{"order": 4, "type": "click_text_fast", "window_title": "WhatsApp", "text": "Harshit", "desc": "Click on Harshit contact"}},
    {{"order": 5, "type": "keyboard", "value": "Hello!", "desc": "Type message"}},
    {{"order": 6, "type": "keyboard", "value": "enter", "desc": "Send message"}}
  ],
  "expected_final_state": "WhatsApp showing chat with Harshit with 'Hello!' message sent"
}}

## Example - Click on icon without text (SLOW - only when necessary):
{{
  "sequence":[
    {{"order": 1, "type": "visual_click", "target_name": "button_submit", "desc": "Click Submit button"}},
    {{"order": 2, "type": "visual_click", "target_name": "dropdown_options", "desc": "Open dropdown menu"}}
  ],
  "expected_final_state": "Form submitted with dropdown menu expanded showing options"
}}
"""

MODULE_EMAIL = r"""
For send_email steps (BACKGROUND - no UI), include:
- "recipient_email": email address of the recipient
- "subject": subject line of the email
- "body": body text of the email (supports UTF-8)
- "attachment_filepaths": (optional) list of absolute paths to local files (e.g. ["C:\\Users\\user\\Desktop\\report.pdf"])
- Use this for: "Send an email to...", "Email the report to...", "Forward this file to..."

## Example - Send a background email with attachment:
{{
  "sequence":[
    {{
      "order": 1, 
      "type": "send_email", 
      "recipient_email": "example@gmail.com", 
      "subject": "Monthly Report", 
      "body": "Hi, please find the attached report.",
      "attachment_filepaths": ["{DESKTOP_PATH}\\report.pdf"],
      "desc": "Send report via background email"
    }}
  ],
  "expected_final_state": "Email sent in background to example@gmail.com with report.pdf attachment"
}}
"""

MODULE_SHELL = r"""
### File Operations (STRICT RULES):
- DO NOT assume any keyboard shortcut creates files or folders
- There is NO universal shortcut for "new text file"
- File and folder creation MUST use:
  - Command-line operations (PREFERRED - fastest and most reliable), OR
  - Direct filesystem operations, OR
  - Explicit UI menu navigation (LAST RESORT - e.g., right-click -> New -> Text Document)
- Ctrl+N MAY ONLY be used when the user explicitly requests "new window" or "new document" AND the application is known

**IMPORTANT Command Syntax:**
- Create folder: `mkdir FolderName`
- Create empty file: `type nul > filename.txt`
- Create multiple files: `type nul > file1.txt && type nul > file2.txt`
- Navigate to Desktop: `cd {DESKTOP_PATH}`
- Navigate to Documents: `cd {DOCUMENTS_PATH}`
- Open folder in Explorer: `explorer FolderName` or `explorer .` (current folder)
- Chain commands: Use `&&` to run multiple commands (e.g., `mkdir test && cd test`)

**IMPORTANT: When creating folders/files, ALWAYS end with opening the folder in Explorer** so the user can see the result.
Example: After creating "AI Lab" folder with files, add: `explorer "{DESKTOP_PATH}\AI Lab"`

## Shell Command Operations (HYBRID CLI APPROACH - PREFERRED):
For file/folder creation and manipulation, ALWAYS use shell commands FIRST. This is the "Killer Combo" workflow:

**CRITICAL: The Killer Combo Workflow for File Operations:**
1. **Create** the file/folder using `shell_command` FIRST (e.g., `mkdir FolderName`, `type nul > file.txt`)
2. **Open** the file using `open_file` or `start filename` command
3. **Edit** via keyboard actions
4. **Save** via `Ctrl+S` (silent save because file already exists)

**Shell Command Tool:**
{{
  "type": "shell_command",
  "command": "mkdir MyFolder",
  "desc": "Create MyFolder directory"
}}

**Available Commands:**
- Create folder: `mkdir "Folder Name"` (use quotes for spaces)
- Create empty file: `type nul > "filename.txt"` (use quotes for spaces)
- Create multiple files: `type nul > file1.txt & type nul > file2.txt`
- Open file: `start "" "full\path\to\file.txt"` (ALWAYS use full path with start, quotes for spaces)
- Open folder in Explorer: `explorer "{DESKTOP_PATH}\FolderName"` (environment variables work correctly)
- Open current folder: `explorer .`
- Chain commands: Use `&` to run multiple commands (e.g., `mkdir test & cd test`)
- Delete file: `del "filename.txt"`
- Delete folder: `rmdir /s /q "FolderName"`
- Copy file: `copy "source.txt" "dest.txt"`
- Move file: `move "source.txt" "dest.txt"`

**CRITICAL RULES FOR SHELL COMMANDS:**
1. **ALWAYS use quotes** around paths/filenames with spaces: `mkdir "AI Lab"` not `mkdir AI Lab`
2. **For start command**: Use format `start "" "full\path\to\file.txt"` - the empty quotes are required
3. **For explorer command**: Use `explorer "{DESKTOP_PATH}\Folder Name"` - environment variables are automatically expanded
4. **Path Variables**: Use {DESKTOP_PATH}, {DOCUMENTS_PATH}, etc. - they will be expanded automatically with the correct user paths (including OneDrive if enabled).
5. **Use full absolute paths** with start command, not relative paths or cd
6. **Combine folder creation and file creation** in ONE command when possible
7. **Don't chain cd commands** - use full paths instead

**IMPORTANT:** When using `start` command to open applications, the system automatically waits 3-5 seconds for the window to appear.

**Example - Create and edit a file (Killer Combo):**
{{
  "sequence":[
    {{"order": 1, "type": "shell_command", "command": "type nul > \"{DESKTOP_PATH}\\notes.txt\"", "desc": "Create notes.txt on Desktop"}},
    {{"order": 2, "type": "shell_command", "command": "start \"\" \"{DESKTOP_PATH}\\notes.txt\"", "desc": "Open notes.txt"}},
    {{"order": 3, "type": "keyboard", "value": "Hello World!", "desc": "Type content"}},
    {{"order": 4, "type": "keyboard", "value": "enter", "desc": "New line"}},
    {{"order": 5, "type": "keyboard", "value": "ctrl+s", "desc": "Save file (silent)"}}
  ],
  "expected_final_state": "Notepad showing notes.txt with 'Hello World!' saved"
}}

**CRITICAL: For multi-line text or code, ALWAYS use write_file (Plane 2) instead of typing simulate. It is faster and safer.**

**Example - Create folder with file (spaces in names):**
{{
  "sequence":[
    {{"order": 1, "type": "shell_command", "command": "mkdir \"{DESKTOP_PATH}\\AI Lab\" & type nul > \"{DESKTOP_PATH}\\AI Lab\\Practical 1.txt\"", "desc": "Create AI Lab folder with Practical 1 file"}},
    {{"order": 2, "type": "shell_command", "command": "start \"\" \"{DESKTOP_PATH}\\AI Lab\\Practical 1.txt\"", "desc": "Open Practical 1 file"}},
    {{"order": 3, "type": "keyboard", "value": "AIM: To implement BFS algorithm", "desc": "Type content"}},
    {{"order": 4, "type": "keyboard", "value": "ctrl+s", "desc": "Save file (silent)"}}
  ],
  "expected_final_state": "Notepad showing Practical 1.txt with content saved in AI Lab folder"
}}

**Example - Create folder structure:**
{{
  "sequence":[
    {{"order": 1, "type": "shell_command", "command": "mkdir \"{DESKTOP_PATH}\\Projects\" & mkdir \"{DESKTOP_PATH}\\Projects\\Python\"", "desc": "Create nested folders"}},
    {{"order": 2, "type": "shell_command", "command": "explorer \"{DESKTOP_PATH}\\Projects\"", "desc": "Open Projects folder in Explorer"}}
  ],
  "expected_final_state": "Explorer showing Projects folder with Python subfolder"
}}

**Example - Create folder with spaces and open it:**
{{
  "sequence":[
    {{"order": 1, "type": "shell_command", "command": "mkdir \"{DESKTOP_PATH}\\AI Lab\"", "desc": "Create AI Lab folder"}},
    {{"order": 2, "type": "write_file", "path": "{DESKTOP_PATH}\\AI Lab\\notes.txt", "content": "Lab notes here", "desc": "Create notes file"}},
    {{"order": 3, "type": "shell_command", "command": "explorer \"{DESKTOP_PATH}\\AI Lab\"", "desc": "Open AI Lab folder in Explorer"}}
  ],
  "expected_final_state": "Explorer showing AI Lab folder with notes.txt file"
}}

**IMPORTANT:** This approach does NOT work with FlexiSIGN file operations. For FlexiSIGN, use the standard FlexiSIGN workflow.
"""

MODULE_FILE_EDITING = r"""
## AI-POWERED FILE EDITING & CREATION (RECOMMENDED FOR WORD/EXCEL/TEXT FILES):

For editing OR CREATING Word (.docx), Excel (.xlsx), or Text (.txt) files with natural language instructions:

**CRITICAL: Creating Word/Excel files via `start` or `keyboard` is FORBIDDEN.**
- Use `ai_edit_word` to create/edit .docx files.
- Use `ai_edit_excel` to create/edit .xlsx files.
- The system automatically creates the file if it doesn't exist.

**REQUIRED FIELDS:**
- "type": Must be "ai_edit_word" (for .docx), "ai_edit_excel" (for .xlsx), or "ai_edit_text" (for .txt)
- "path": Fuzzy path to the file (e.g., "desktop/report" or "desktop/input")
- "prompt": Natural language instructions describing what to change or what to create (e.g., "Create a report about AI trends")
- "desc": Brief description of the action

**CRITICAL: Both "path" and "prompt" are REQUIRED. DO NOT omit either field.**

**Example - Create a new Word document:**
{{
  "order": 1,
  "type": "ai_edit_word",
  "path": "desktop/LabCode/python_intro",
  "prompt": "Create a new document with a basic python program that prints 'Hello World'",
  "desc": "Create python intro Word document"
}}

**Example - Edit existing Word document:**
{{
  "order": 1,
  "type": "ai_edit_word",
  "path": "desktop/input",
  "prompt": "Replace the name Harshit Singla with Ayushi and replace the phone number with 9872113958",
  "desc": "Update name and phone in Word document"
}}
"""

MODULE_WORKSPACE_CONTROL = r"""
For creating/editing code files and structured content, use these direct file operations. They are MUCH faster and more reliable than UI-based editing.

**CRITICAL: The Modern Workflow for Code Files:**
1. **Create folder** using `shell_command` (e.g., `mkdir "{DESKTOP_PATH}\LabCode"`)
2. **Write file content** using `write_file` with full code (NO UI interaction needed!)
3. **Open in editor** using `shell_command` (e.g., `code "path\to\file.py"` for VS Code)
4. **Run program** using keyboard shortcuts (Ctrl+` for terminal, then type command)

**INTELLIGENT FILE MODIFICATION WORKFLOW (CRITICAL FOR EDITING EXISTING FILES):**
When user asks to modify, edit, update, change, or fix an existing file:

**STEP 1: READ THE FILE FIRST**
{{
  "type": "read_file",
  "path": "{DESKTOP_PATH}\\form.txt",
  "desc": "Read current file content to understand what needs to be changed"
}}

**STEP 2: MODIFY USING SEARCH/REPLACE**
Use `replace_in_file` for targeted changes (PREFERRED - works like IDE Find & Replace):
{{
  "type": "replace_in_file",
  "path": "{DESKTOP_PATH}\\form.txt",
  "old_text": "Name: John Doe",
  "new_text": "Name: Harshit Singla",
  "desc": "Replace the name field with new value"
}}

**CRITICAL: For replace_in_file:**
- `old_text` must be the COMPLETE text you want to replace (e.g., "Name: John Doe", not just "Name:")
- `new_text` is the COMPLETE replacement text (e.g., "Name: Harshit Singla")
- The operation finds `old_text` and replaces it entirely with `new_text`
- Think of it like: Find "Name: John Doe" -> Replace with "Name: Harshit Singla"

**WRONG (will result in "Name: Harshit Singla John Doe"):**
{{
  "old_text": "Name:",
  "new_text": "Name: Harshit Singla"
}}

**CORRECT (will result in "Name: Harshit Singla"):**
{{
  "old_text": "Name: John Doe",
  "new_text": "Name: Harshit Singla"
}}

OR use `modify_lines` for line-specific changes:
{{
  "type": "modify_lines",
  "path": "{DESKTOP_PATH}\\form.txt",
  "line_number": 5,
  "new_content": "Name: Harshit Singla",
  "num_lines": 1,
  "desc": "Update line 5 with new name"
}}

OR use `write_file` ONLY if you need to rewrite the entire file:
{{
  "type": "write_file",
  "path": "{DESKTOP_PATH}\\form.txt",
  "content": "Full updated content here...",
  "desc": "Rewrite entire file with modifications"
}}

**STEP 3: VERIFY (OPTIONAL)**
{{
  "type": "shell_command",
  "command": "start \"\" \"{DESKTOP_PATH}\\form.txt\"",
  "desc": "Open file to verify changes"
}}

**CRITICAL RULES FOR FILE MODIFICATIONS:**
1. ALWAYS use `read_file` FIRST when modifying existing files
2. NEVER use placeholder text like {{UPDATED_CONTENT}} - always provide actual content
3. For `replace_in_file`: `old_text` must be the COMPLETE text to replace (e.g., "Name: John Doe", not just "Name:")
4. For small changes, use `replace_in_file` (fastest and most reliable)
5. For line-specific edits, use `modify_lines`
6. Only use `write_file` when rewriting the entire file is necessary
7. The system will automatically handle the actual text replacement

**IMPORTANT:** When user asks to "debug", "fix", "modify", or "copy code from" a file:
- ALWAYS use `read_file` FIRST to get the actual file content
- Analyze what needs to be changed
- Use `replace_in_file` or `modify_lines` for targeted edits
- Use `write_file` only for complete rewrites
- Then open in editor and run

### Write File (RECOMMENDED FOR CODE):
Use "write_file" to create or overwrite a file with content directly. NO UI needed!
{{
  "type": "write_file",
  "path": "{DESKTOP_PATH}\\LabCode\\bubble_sort.py",
  "content": "def bubble_sort(arr):\\n    n = len(arr)\\n    for i in range(n):\\n        for j in range(0, n-i-1):\\n            if arr[j] > arr[j+1]:\\n                arr[j], arr[j+1] = arr[j+1], arr[j]\\n\\ndata =[64, 34, 25, 12, 22, 11, 90]\\nbubble_sort(data)\\nprint(data)",
  "desc": "Write bubble sort program"
}}
- "path": Full absolute path to file (use {DESKTOP_PATH} or {DOCUMENTS_PATH} for user directories)
- "content": Complete file content (use \n for newlines, escape quotes)
- Creates parent directories automatically if they don't exist
- Overwrites file if it already exists

### Read File:
Use "read_file" to read file contents.
{{
  "type": "read_file",
  "path": "{DESKTOP_PATH}\\script.py",
  "desc": "Read script contents"
}}

### Append File:
Use "append_file" to add content to existing file.
{{
  "type": "append_file",
  "path": "{DESKTOP_PATH}\\log.txt",
  "content": "New log entry\\n",
  "desc": "Append to log file"
}}

### Create Directory:
Use "create_directory" to create folders.
{{
  "type": "create_directory",
  "path": "{DESKTOP_PATH}\\Projects\\Python",
  "desc": "Create Python projects folder"
}}

**Example - Create Python program and run in VS Code (MODERN APPROACH):**
{{
  "sequence":[
    {{"order": 1, "type": "shell_command", "command": "mkdir \"{DESKTOP_PATH}\\LabCode\"", "desc": "Create LabCode folder"}},
    {{"order": 2, "type": "write_file", "path": "{DESKTOP_PATH}\\LabCode\\bubble_sort.py", "content": "def bubble_sort(arr):\\n    n = len(arr)\\n    for i in range(n):\\n        swapped = False\\n        for j in range(0, n - i - 1):\\n            if arr[j] > arr[j + 1]:\\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\\n                swapped = True\\n        if not swapped:\\n            break\\n    return arr\\n\\nif __name__ == \\"__main__\\":\\n    data = input(\\"Enter numbers separated by spaces: \\").strip()\\n    if not data:\\n        print(\\"No input provided.\\")\\n    else:\\n        arr = list(map(int, data.split()))\\n        bubble_sort(arr)\\n        print(\\"Sorted array:\\", *arr)", "desc": "Write bubble sort program"}},
    {{"order": 3, "type": "shell_command", "command": "code \"{DESKTOP_PATH}\\LabCode\"", "desc": "Open folder in VS Code"}},
    {{"order": 4, "type": "keyboard", "value": "ctrl+`", "desc": "Open integrated terminal"}},
    {{"order": 5, "type": "keyboard", "value": "python bubble_sort.py", "desc": "Type run command"}},
    {{"order": 6, "type": "keyboard", "value": "enter", "desc": "Execute program"}}
  ],
  "expected_final_state": "VS Code showing bubble_sort.py with terminal ready to run the program"
}}

**Example - Debug existing code (READ -> ANALYZE -> FIX -> WRITE):**
{{
  "sequence":[
    {{"order": 1, "type": "read_file", "path": "{DESKTOP_PATH}\\LabCode\\bubble_sort.py", "desc": "Read existing code to analyze"}},
    {{"order": 2, "type": "write_file", "path": "{DESKTOP_PATH}\\LabCode\\bubble_sort.py", "content": "def bubble_sort(arr):\\n    n = len(arr)\\n    for i in range(n):\\n        swapped = False\\n        for j in range(0, n - i - 1):\\n            if arr[j] > arr[j + 1]:\\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\\n                swapped = True\\n        if not swapped:\\n            break\\n    return arr\\n\\nif __name__ == \\"__main__\\":\\n    data =[64, 34, 25, 12, 22, 11, 90]\\n    result = bubble_sort(data)\\n    print(\\"Sorted array:\\", result)", "desc": "Write corrected code with bug fixes"}},
    {{"order": 3, "type": "shell_command", "command": "code \"{DESKTOP_PATH}\\LabCode\\bubble_sort.py\"", "desc": "Open fixed file in VS Code"}},
    {{"order": 4, "type": "keyboard", "value": "ctrl+`", "desc": "Open integrated terminal"}},
    {{"order": 5, "type": "keyboard", "value": "python bubble_sort.py", "desc": "Type run command"}},
    {{"order": 6, "type": "keyboard", "value": "enter", "desc": "Execute program"}}
  ],
  "expected_final_state": "VS Code showing debugged bubble_sort.py with terminal displaying sorted output"
}}

**Example - Copy code from document to new file:**
{{
  "sequence":[
    {{"order": 1, "type": "read_file", "path": "{DESKTOP_PATH}\\AI Lab\\Practical 1.txt", "desc": "Read code from document"}},
    {{"order": 2, "type": "write_file", "path": "{DESKTOP_PATH}\\LabCode\\dfs.py", "content": "# DFS Algorithm Implementation\\ndef dfs(graph, start, visited=None):\\n    if visited is None:\\n        visited = set()\\n    visited.add(start)\\n    print(start, end=' ')\\n    for neighbor in graph[start]:\\n        if neighbor not in visited:\\n            dfs(graph, neighbor, visited)\\n    return visited\\n\\nif __name__ == \\"__main__\\":\\n    graph = {{\\n        'A': ['B', 'C'],\\n        'B':['D', 'E'],\\n        'C': ['F'],\\n        'D':[],\\n        'E': ['F'],\\n        'F':[]\\n    }}\\n    print(\\"DFS Traversal:\\")\\n    dfs(graph, 'A')", "desc": "Write extracted code to new Python file"}},
    {{"order": 3, "type": "shell_command", "command": "code \"{DESKTOP_PATH}\\LabCode\\dfs.py\"", "desc": "Open new file in VS Code"}},
    {{"order": 4, "type": "keyboard", "value": "ctrl+`", "desc": "Open integrated terminal"}},
    {{"order": 5, "type": "keyboard", "value": "python dfs.py", "desc": "Type run command"}},
    {{"order": 6, "type": "keyboard", "value": "enter", "desc": "Execute program"}}
  ],
  "expected_final_state": "VS Code showing dfs.py with terminal displaying DFS traversal output"
}}

**ADVANTAGES OF write_file:**
- ✓ No UI interaction needed (no Ctrl+A, no typing, no Save dialog)
- ✓ Handles long code perfectly (no character limits, no timing issues)
- ✓ Preserves exact formatting (indentation, newlines, special characters)
- ✓ Much faster (instant file creation vs slow typing simulation)
- ✓ More reliable (no permission dialogs, no UI detection failures)
- ✓ Works even if editor is not open

**WHEN TO USE write_file vs shell_command + keyboard:**
- Use `write_file` for: Code files, structured content, long text, precise formatting
- Use `shell_command + keyboard` for: Simple text files, user-visible editing process
"""

MODULE_FILE_NAV = r"""
## Web Automation Agent (RECOMMENDED FOR ALL WEB TASKS):
For searching the web, finding information, or browser-based tasks:

**REQUIRED FIELDS:**
- "type": "web_automation"
- "prompt": The user's original request or a refined version for the web agent
- "desc": Brief description

**Example - Search for something:**
{{
  "order": 1,
  "type": "web_automation",
  "prompt": "What is the capital of France?",
  "desc": "Search for capital of France"
}}

**Example - Find weather:**
{{
  "order": 1,
  "type": "web_automation",
  "prompt": "Current weather in Mumbai",
  "desc": "Get Mumbai weather"
}}

**CRITICAL: Use web_automation for ANY task that requires browsing or searching the internet.**

## File and Folder Operations (FAST & RELIABLE):
Use filesystem-based operations that bypass UI completely. These use fuzzy path matching and are MUCH faster than UI navigation.

**IMPORTANT LOCATION MAPPINGS:**
- "New Briefcase" folder -> use "stickers" (located at {{STICKERS_PATH}})
- "Desktop" -> use "desktop"
- "Documents" -> use "documents"
- "Downloads" -> use "downloads"

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
  "path": "{{DESKTOP_PATH}}\\document.txt",
  "desc": "Save file to Desktop"
}}
- "path": Full absolute path (use double backslashes in JSON)

## Path Resolution Examples:
The system automatically resolves fuzzy paths:
- "desktop/jarvis test" -> "{{DESKTOP_PATH}}\\JARVIS Test"
- "stickers/maan 22" -> "{{STICKERS_PATH}}\\maan 22.FS"
- "documents/report" -> "C:\\Users\\user\\Documents\\report.docx"
- Handles typos, case differences, partial names
- Automatically finds file extensions

## Example - Open file from New Briefcase (Stickers):
{{
  "sequence":[
    {{"order": 1, "type": "open_file", "path": "stickers/maan 22", "desc": "Open maan 22 file"}}
  ],
  "expected_final_state": "maan 22 file opened in default application"
}}

## Example - Open file from Desktop:
{{
  "sequence":[
    {{"order": 1, "type": "open_file", "path": "desktop/report", "desc": "Open report file"}}
  ],
  "expected_final_state": "Report file opened in default application"
}}

## Example - Open folder:
{{
  "sequence":[
    {{"order": 1, "type": "open_folder", "path": "desktop/jarvis test", "desc": "Open JARVIS Test folder"}}
  ],
  "expected_final_state": "JARVIS Test folder opened in File Explorer"
}}

## Example - Save a file:
{{
  "sequence":[
    {{"order": 1, "type": "save_file", "path": "{{DESKTOP_PATH}}\\notes.txt", "desc": "Save notes to Desktop"}}
  ],
  "expected_final_state": "File saved to Desktop as notes.txt"
}}

IMPORTANT for Direct Path Operations:
- Always use full absolute paths with proper escaping (double backslashes in JSON)
- Prefer direct path operations over manual UI navigation for file operations
- Use click_text for selecting files in File Explorer after navigating to the directory
"""

MODULE_OUT_REQ = r"""
## Output Requirements:
You MUST include an "expected_final_state" field in your response. This is a brief description of what the screen should look like after all steps complete successfully. Be specific about:
- Which application/window should be visible
- What content should be displayed
- Any UI elements that should be in a specific state

IMPORTANT:
- Prefer keyboard shortcuts when possible (fastest and most reliable)
- Use click_text_fast for any UI element with visible text (10x faster than visual_click)
- Use website-specific search features, NOT the browser address bar for searching within sites
- Use visual_click ONLY when the element has no readable text (icons, images, complex UI)
- Return ONLY valid JSON, no markdown formatting or extra text
- Each step must be atomic and executable
- Add small waits implicitly between steps (the executor handles this)

ACT AS A PURE JSON API. DO NOT provide explanations. DO NOT provide conversational text. Output ONLY the raw JSON object. If you include any text outside the JSON, the system will fail. No markdown fences, no thinking, no extra output.
"""

MODULE_FLEXISIGN = r"""You are a FlexiSIGN Automation Agent. Your goal is to translate natural language requests into a structured JSON execution plan.

## System Information:
- Windows Username: {WINDOWS_USERNAME}
- User Home Directory: C:\Users\{WINDOWS_USERNAME}
- Desktop Path: {DESKTOP_PATH}
- Documents Path: {DOCUMENTS_PATH}
- Downloads Path: {DOWNLOADS_PATH}
- **Stickers/New Briefcase Path: {STICKERS_PATH}** (IMPORTANT: When user mentions "New Briefcase" or "stickers", use "stickers")

CRITICAL PATH RULES:
1. When user mentions "New Briefcase" -> use "stickers"
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
2. Structure: {{ "mode": "direct|vision", "sequence":[ {{ "order": 1, "type": "...", ... }} ] }}

### 6. EXAMPLES

**Input:** "Make iron plate set for bike PB12W3998"
**Output:**
{{
  "mode": "direct",
  "sequence":[
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
  "sequence":[
    {{"order": 1, "type": "keyboard", "value": "ctrl+n", "desc": "New Page"}},
    {{"order": 2, "type": "ensure_designcentral", "desc": "Open Panel"}},
    {{"order": 3, "type": "create_text", "text": "GJ01G0001", "desc": "Text"}},
    {{"order": 4, "type": "apply_style", "style_name": "Govt", "desc": "Apply Template"}}
  ],
  "expected_final_state": "FlexiSIGN window showing government plate with 'GJ01G0001' text with Govt style applied"
}}

### 7. IMPORTANT
You MUST include an "expected_final_state" field describing what the screen should look like after successful execution.

ACT AS A PURE JSON API. DO NOT provide explanations. DO NOT provide conversational text. Output ONLY the raw JSON object. If you include any text outside the JSON, the system will fail. No markdown fences, no thinking, no extra output.
"""

MODULE_REACT = r"""
MODULE: REACT (Iterative Execution)
CONTEXT: You are in an iterative Thought-Action-Observation loop.
GOAL: Generate 1-3 atomic steps to progress toward the user's goal.

RESPONSE SCHEMA:
{
  "thought": "Brief reasoning about current state and next steps",
  "sequence": [
    {
      "order": 1,
      "type": "keyboard|visual_click|shell_command|path_exists|directory_exists|read_file|write_file|...",
      "desc": "Human readable description"
    }
  ],
  "is_complete": false,
  "expected_observation": "What you expect to see after these steps"
}

GUIDELINES:
1. If the task is finished, set "is_complete": true and "sequence": [].
2. If you need more info from the user, use type: "ask_doubt" with "question" parameter.
3. Keep batches small (1-3 steps) to allow for frequent feedback.
4. Put type-specific fields at the step top level, e.g. "command", "path", "content", "value", "target_name"; do not nest them under "parameters".
5. Make expected_observation concrete and checkable. Mention exact file/folder paths, filenames, visible window titles, or text that should exist after the batch. Avoid vague wording like "the action completed successfully".
6. Do not use read_file to verify a folder. Use directory_exists for folders and path_exists when either a file or folder is acceptable.
"""



# ==========================================
# 🚀 PLANNER SERVICE CLASS
# ==========================================

class PlannerService:
    def __init__(self, api_key: str = None, config: dict = None):
        if config is None:
            config = {
                'WINDOWS_USERNAME': os.getenv('WINDOWS_USERNAME', 'user'),
                'DESKTOP_PATH': os.getenv('DESKTOP_PATH', r'C:\Users\user\Desktop'),
                'DOCUMENTS_PATH': os.getenv('DOCUMENTS_PATH', r'C:\Users\user\Documents'),
                'DOWNLOADS_PATH': os.getenv('DOWNLOADS_PATH', r'C:\Users\user\Downloads'),
                'STICKERS_PATH': os.getenv('STICKERS_PATH', r'D:\Stickers\New Briefcase'),
                'LLM_PROVIDER': os.getenv('LLM_PROVIDER', 'gemini'),
                'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
                'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
                'LOCAL_MODEL_NAME': os.getenv('LOCAL_MODEL_NAME', 'google/gemma-4-e2b'),
                'LOCAL_BASE_URL': os.getenv('LOCAL_BASE_URL', 'http://127.0.0.1:1234/v1')
            }
        
        self.llm_provider = config.get('LLM_PROVIDER', 'gemini')
        self.gemini_key = config.get('GEMINI_API_KEY', '')
        self.openai_key = config.get('OPENAI_API_KEY', '')
        self.config = config
        self._cached_content_name = None
        self._cached_content_text = ""
        
        # Initialize modules dictionary for easy access
        self.MODULES = {
            'general': MODULE_UI_OS + MODULE_SHELL + MODULE_OUT_REQ,
            'flexisign': MODULE_FLEXISIGN,
            'react': MODULE_REACT,
            'email': MODULE_EMAIL,
            'file_editing': MODULE_FILE_EDITING + "\n" + MODULE_WORKSPACE_CONTROL,
            'file_navigation': MODULE_FILE_NAV
        }
        
        self.init_provider(api_key)

    def init_provider(self, str_api_key_override=None):
        if self.llm_provider == 'openai':
            api_key = str_api_key_override or self.openai_key or os.getenv('OPENAI_API_KEY')
            if not api_key: raise ValueError("OpenAI API key not configured.")
            self.provider = OpenAIProvider(api_key=api_key)
        elif self.llm_provider == 'local':
            model_name = self.config.get('LOCAL_MODEL_NAME', os.getenv('LOCAL_MODEL_NAME', 'gemma:2b'))
            base_url = self.config.get('LOCAL_BASE_URL', os.getenv('LOCAL_BASE_URL', 'http://localhost:11434/v1'))
            self.provider = LocalProvider(model_name=model_name, base_url=base_url)
        else:
            api_key = str_api_key_override or self.gemini_key or os.getenv('GEMINI_API_KEY')
            if not api_key: raise ValueError("Gemini API key not configured.")
            self.provider = GeminiProvider(api_key=api_key)
             
        self.provider_name = self.llm_provider
        self.llm = self.provider
             
        print(f"Initialized Planner with {self.llm_provider} provider")

        # Initialize Gemini Context Cache if using Google provider
        if self.llm_provider == 'gemini':
            self.init_context_cache()

        # Pre-warm KV cache for local providers (populates cache with static prompts)
        if self.llm_provider == 'local' and isinstance(self.provider, LocalProvider):
            safe_config = {k: f"{{{k}}}" for k in self.config.keys()}
            # Warm up the planner prefix cache
            warmup_prompt = CACHEABLE_PREFIX.format(**safe_config)
            self.provider.warmup_cache(warmup_prompt)
            # Warm up the router prompt cache (static, reused on every routing call)
            self.provider.warmup_cache(self.ROUTER_PROMPT)

    # Static router prompt — identical across all requests -> KV cache reuses it
    ROUTER_PROMPT = """You are a routing agent for a Computer Automation AI. 
Analyze the user command and determine which tool modules are required.
Available Modules:
- "ui_os": Opening apps, typing, web browsing, clicking buttons (keyboard, click_text_fast, visual_click).
- "email": Sending background emails (send_email).
- "shell": Command prompt operations, creating folders, basic file creation (shell_command).
- "file_editing": AI-powered editing of Word (.docx), Excel (.xlsx), or Text (.txt) files, AND direct code/text file operations (ai_edit_word, ai_edit_excel, ai_edit_text, write_file, replace_in_file, modify_lines). REQUIRED when user asks to edit, modify, or change content in documents.
- "file_navigation": Opening files/folders directly by path or saving files (open_file, open_folder, save_file).
- "flexisign": ONLY if command involves number plates, flexisign, govt plates, or bike/car plates.
- "web_auto": MUST include for ANY web searching, browsing, or online information retrieval. REQUIRED for "search for", "find on google", "weather", etc.

CRITICAL: If user asks to edit/modify/change content in a Word, Excel, or Text file, you MUST include "file_editing" module.
CRITICAL: Only include modules that are ACTUALLY needed. Do NOT include modules "just in case". Minimal modules = faster response.

ACT AS A PURE JSON API. DO NOT provide explanations. DO NOT provide conversational text. Output ONLY the raw JSON object. If you include any text outside the JSON, the system will fail. No markdown fences, no thinking, no extra output.

Return ONLY a JSON object exactly like this (no markdown):
{
    "mode": "general",  // or "flexisign"
    "modules": ["ui_os", "shell"] // Array of module names from above
}"""

    def route_command(self, user_command: str) -> dict:
        """
        LLM Router: Uses the LLM to intelligently select required modules.
        The ROUTER_PROMPT is static and small — KV cache reuses it after the first call,
        making subsequent routing calls much faster.
        """
        try:
            response_text = self.provider.generate_content(
                system_prompt=self.ROUTER_PROMPT,
                user_prompt=user_command
            )
            
            if response_text.startswith('```'):
                lines = response_text.split('\n')[1:]
                if lines and lines[-1].strip() == '```': lines = lines[:-1]
                response_text = '\n'.join(lines)
                
            return json.loads(response_text)
        except Exception as e:
            print(f"Router failed, falling back to minimal modules: {e}")
            return {"mode": "general", "modules": ["ui_os", "shell"]}

    def build_prompt(self, route_data: dict) -> str:
        """Assembles the final system prompt with a STABLE PREFIX for KV cache reuse.
        
        Architecture:
        [CACHEABLE_PREFIX] (identical across all requests -> cached by KV cache)
        [MODULE_SUFFIX]    (small, varies per request -> minimal re-processing)
        
        The CACHEABLE_PREFIX is always sent first and never changes,
        so the local LLM server can reuse its KV cache for that portion.
        """
        mode = route_data.get("mode", "general")
        modules = route_data.get("modules", [])
        
        # Create a "Safe" config that keeps the placeholder names literal for the LLM
        # This prevents leaking real paths/usernames to the LLM.
        safe_config = {k: f"{{{k}}}" for k in self.config.keys()}
        
        # If FlexiSIGN is detected, use the exact original Flexisign prompt ONLY.
        # FlexiSIGN has its own complete prompt — no prefix sharing possible.
        if mode == "flexisign" or "flexisign" in modules:
            return MODULE_FLEXISIGN.format(**safe_config)
        
        # === KV CACHE-OPTIMIZED PROMPT ASSEMBLY ===
        # The CACHEABLE_PREFIX is always identical -> KV cache reuses it 100%
        final_prompt = CACHEABLE_PREFIX.format(**safe_config)
        
        # Append module-specific content as SUFFIX (small, varies per request)
        if "ui_os" in modules: final_prompt += "\n" + MODULE_UI_OS
        if "email" in modules: final_prompt += "\n" + MODULE_EMAIL
        if "shell" in modules: final_prompt += "\n" + MODULE_SHELL
        if "file_editing" in modules: final_prompt += "\n" + MODULE_FILE_EDITING + "\n" + MODULE_WORKSPACE_CONTROL
        if "file_navigation" in modules or "web_auto" in modules: final_prompt += "\n" + MODULE_FILE_NAV
        
        # Always add the mandatory output requirements at the end
        final_prompt += "\n" + MODULE_OUT_REQ
        
        return final_prompt

    def detect_mode(self, user_command: str) -> str:
        # Kept for backward compatibility, though router handles this now
        flexisign_keywords =["plate", "number plate", "numberplate", "bike", "car", "iron", "glass", "flexisign", "flexi sign", "flexi-sign", "nameplate", "name plate", "sticker", "stickers"]
        command_lower = user_command.lower()
        for keyword in flexisign_keywords:
            if keyword in command_lower: return "flexisign"
        return "general"

    def generate_plan(self, user_command: str, mode: str = None) -> dict:
        if not user_command or not user_command.strip():
            raise ValueError("User command cannot be empty")
        
        # 1. Route the command (Dynamic Module Selection)
        route_data = self.route_command(user_command)
        
        # Manual override fallback
        if mode is None:
            mode = self.detect_mode(user_command)
        if mode:
            route_data["mode"] = mode
            
        # 2. Build the optimized prompt
        system_prompt = self.build_prompt(route_data)
        
        try:
            # 3. Generate Execution Plan
            response_text = self.provider.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_command
            )
            print(f"DEBUG: RAW AI RESPONSE:\n{response_text}\n--- END RAW ---")
            
            # Privacy Audit: Log the safe prompt and raw response
            self._log_privacy_audit(system_prompt, response_text)
            
            response_text = response_text.strip()
            
            if response_text.startswith('```'):
                lines = response_text.split('\n')[1:]
                if lines and lines[-1].strip() == '```': lines = lines[:-1]
                response_text = '\n'.join(lines)
            
            try:
                from local_client.json_utils import safe_json_loads
                plan = safe_json_loads(response_text)
            except ImportError:
                plan = json.loads(response_text)

            # 4. Resolve placeholders in the generated plan LOCALLY (for privacy)
            plan = self._resolve_placeholders(plan)
            
            self._validate_plan(plan)
            
            if 'sequence' in plan:
                for step in plan['sequence']:
                    if step.get('type') == 'write_file' and 'content' in step:
                        content = step['content']
                        if content.startswith('```'):
                            lines = content.split('\n')[1:]
                            if lines and lines[-1].strip() == '```': lines = lines[:-1]
                            content = '\n'.join(lines)
                        step['content'] = content
            
            plan['mode'] = route_data["mode"]
            return plan
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Planner Model: {e}")
        except Exception as e:
            raise Exception(f"Failed to generate plan: {e}")
    
    def _resolve_placeholders(self, data):
        """Recursively resolve placeholders in strings within a dictionary or list."""
        if isinstance(data, str):
            # Resolve placeholders using self.config
            try:
                # Use a dict that only contains what we want to resolve
                return data.format(**self.config)
            except (KeyError, ValueError, IndexError):
                # If formatting fails (e.g. unknown key or malformed braces), return original
                return data
        elif isinstance(data, list):
            return [self._resolve_placeholders(item) for item in data]
        elif isinstance(data, dict):
            return {key: self._resolve_placeholders(value) for key, value in data.items()}
        return data

    def _log_privacy_audit(self, system_prompt: str, raw_response: str):
        """Logs the safe system prompt and raw LLM response for privacy auditing."""
        try:
            # Determine log directory (relative to current file's parent's parent -> root/local_client/debug_logs)
            log_base = Path(__file__).parent.parent / "local_client" / "debug_logs"
            log_dir = log_base / "privacy_audit"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"audit_{timestamp}.txt"
            
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("="*80 + "\n")
                f.write(f"PRIVACY AUDIT LOG - {datetime.now().isoformat()}\n")
                f.write("="*80 + "\n\n")
                f.write("--- [SAFE SYSTEM PROMPT SENT TO LLM] ---\n")
                f.write("(Contains abstract placeholders, no real paths/usernames)\n\n")
                f.write(system_prompt)
                f.write("\n\n" + "-"*40 + "\n\n")
                f.write("--- [RAW RESPONSE RECEIVED FROM LLM] ---\n")
                f.write("(Contains abstract placeholders to be resolved locally)\n\n")
                f.write(raw_response)
                f.write("\n\n" + "="*80 + "\n")
                
            print(f"Privacy audit log saved to: {log_file}")
        except Exception as e:
            print(f"Failed to save privacy audit log: {e}")

    def _validate_plan(self, plan: dict) -> None:
        """Validation logic kept identical"""
        if not isinstance(plan, dict): raise ValueError("Plan must be a dictionary")
        if 'sequence' not in plan: raise ValueError("Plan must contain a 'sequence' array")
        if not isinstance(plan['sequence'], list): raise ValueError("'sequence' must be an array")
        
        valid_types = {
            'keyboard', 'visual_click', 'click_text_fast',
            'create_text', 'set_dimensions', 'set_font', 'apply_style', 'move_object', 'ensure_designcentral',
            'open_file', 'open_folder', 'save_file', 'shell_command',
            'write_file', 'read_file', 'path_exists', 'directory_exists', 'append_file', 'create_directory',
            'replace_in_file', 'modify_lines', 'insert_at_line', 'delete_lines',
            'ai_edit_text', 'ai_edit_excel', 'ai_edit_word', 'send_email', 'web_automation'
        }
        
        for i, step in enumerate(plan['sequence']):
            if not isinstance(step, dict): raise ValueError(f"Step {i+1} must be a dictionary")
            if 'order' not in step: raise ValueError(f"Step {i+1} missing 'order' field")
            if 'type' not in step: raise ValueError(f"Step {i+1} missing 'type' field")
            
            step_type = step['type']
            if step_type not in valid_types:
                raise ValueError(f"Step {i+1} has invalid type '{step_type}'.")
                # Validate required fields for each step type
            if step_type == 'keyboard' and 'value' not in step:
                raise ValueError(f"Keyboard step {i+1} missing 'value' field")
            
            if step_type == 'web_automation' and 'prompt' not in step:
                raise ValueError(f"Web automation step {i+1} missing 'prompt' field")
            
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

            # Validate AI editing step types
            if step_type in ('ai_edit_text', 'ai_edit_excel', 'ai_edit_word'):
                if 'path' not in step:
                    raise ValueError(f"{step_type} step {i+1} missing 'path' field")
                if 'prompt' not in step:
                    raise ValueError(f"{step_type} step {i+1} missing 'prompt' field")
            
            # Validate Plane 2 workspace control step types
            if step_type == 'write_file':
                if 'path' not in step:
                    raise ValueError(f"write_file step {i+1} missing 'path' field")
                if 'content' not in step:
                    raise ValueError(f"write_file step {i+1} missing 'content' field")
            
            if step_type in ('read_file', 'path_exists', 'directory_exists', 'create_directory') and 'path' not in step:
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

            # Validate send_email step type
            if step_type == 'send_email':
                if 'recipient_email' not in step:
                    raise ValueError(f"send_email step {i+1} missing 'recipient_email' field")
                if 'subject' not in step:
                    raise ValueError(f"send_email step {i+1} missing 'subject' field")
                if 'body' not in step:
                    raise ValueError(f"send_email step {i+1} missing 'body' field")

    def generate_next_steps(self, session) -> dict:
        """
        ReAct Loop: Generate the next batch of steps based on session history.
        Uses the full system prompt plus ReAct instructions for iterative reasoning.
        """
        route_data = session.route_data
        if not route_data:
            route_data = self.route_command(session.user_command)
            session.route_data = route_data

        # Build the full system prompt (same as generate_plan uses)
        system_prompt = self.build_prompt(route_data)
        system_prompt += "\n" + MODULE_REACT  # Append ReAct instructions
        
        # Format conversation history
        history_context = session.get_history_for_planner()
        
        user_prompt = f"""USER COMMAND: {session.user_command}
CURRENT MODE: {session.mode}

EXECUTION HISTORY:
{history_context}

Generate the next 1-3 steps. If the task is complete, set is_complete to true with an empty sequence."""
        
        try:
            # Use cached generation for Gemini to save tokens/latency
            if self.provider_name == 'gemini':
                response_text = self._generate_with_cache(system_prompt, user_prompt)
            else:
                response_text = self.llm.generate_content(system_prompt=system_prompt, user_prompt=user_prompt)
                
            plan = self._parse_json_response(response_text)
            plan = self._resolve_placeholders(plan)
            plan = self._validate_react_plan(plan)
            plan['mode'] = route_data.get("mode", "general")
            return plan
            
        except Exception as e:
            print(f"✗ ReAct planning failed: {e}")
            raise

    def _validate_react_plan(self, plan: dict) -> dict:
        """Ensure ReAct plan follows the required schema."""
        if not isinstance(plan, dict):
            raise ValueError("ReAct plan must be a dictionary")
        if 'sequence' not in plan:
            plan['sequence'] = []
        if plan['sequence'] is None:
            plan['sequence'] = []
        if not isinstance(plan['sequence'], list):
            raise ValueError("ReAct plan 'sequence' must be a list")
        if 'is_complete' not in plan:
            plan['is_complete'] = False
        if 'thought' not in plan:
            plan['thought'] = "Continuing execution..."
            
        # Ensure steps have correct format
        for i, step in enumerate(plan['sequence']):
            if not isinstance(step, dict):
                raise ValueError(f"ReAct step {i+1} must be a dictionary")
            parameters = step.pop('parameters', None)
            if isinstance(parameters, dict):
                for key, value in parameters.items():
                    step.setdefault(key, value)
            if 'order' not in step:
                step['order'] = i + 1
            if 'desc' not in step:
                step['desc'] = f"Executing {step.get('type', 'step')}"
                
        return plan

    def _parse_json_response(self, response_text: str) -> dict:
        """Parse JSON from LLM response, handling markdown fences."""
        response_text = response_text.strip()
        if response_text.startswith('```'):
            lines = response_text.split('\n')[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            response_text = '\n'.join(lines)
        
        try:
            import sys
            from pathlib import Path
            local_client_path = Path(__file__).parent.parent / "local_client"
            if str(local_client_path) not in sys.path:
                sys.path.insert(0, str(local_client_path))
            from json_utils import safe_json_loads
            return safe_json_loads(response_text)
        except ImportError:
            return json.loads(response_text)

    def _generate_with_cache(self, system_prompt: str, user_prompt: str) -> str:
        """Generate content using Gemini Context Cache if available, else standard call."""
        if hasattr(self, '_cached_content_name') and self._cached_content_name:
            try:
                from google.genai import types

                cached_text = getattr(self, '_cached_content_text', '')
                contents = user_prompt
                if cached_text and system_prompt.startswith(cached_text):
                    dynamic_system = system_prompt[len(cached_text):].strip()
                    if dynamic_system:
                        contents = f"{dynamic_system}\n\n{user_prompt}"
                else:
                    contents = f"{system_prompt}\n\n{user_prompt}"

                response = self.provider.client.models.generate_content(
                    model=self.provider.model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        cached_content=self._cached_content_name,
                        temperature=0.1
                    )
                )
                return response.text
            except Exception as e:
                print(f"⚠️ Gemini Context Cache failed, falling back: {e}")
        
        # Standard generation fallback
        return self.llm.generate_content(system_prompt=system_prompt, user_prompt=user_prompt)

    def init_context_cache(self):
        """Initialize the Gemini Context Cache with the static prefix prompt."""
        if self.llm_provider != 'gemini':
            print("Context caching only available for Gemini provider")
            return

        try:
            from google.genai import types

            safe_config = {k: f"{{{k}}}" for k in self.config.keys()}
            cache_content = CACHEABLE_PREFIX.format(**safe_config)
            cache_api = getattr(self.provider.client, 'caches', None) or getattr(self.provider.client, 'caching', None)
            if cache_api is None:
                raise AttributeError("Gemini client does not expose a cache API")

            create_config = getattr(types, 'CreateCachedContentConfig', None)
            if create_config:
                cached = cache_api.create(
                    model=self.provider.model_name,
                    config=create_config(
                        contents=[cache_content],
                        ttl="3600s"
                    )
                )
            else:
                cached = cache_api.create(
                    model=self.provider.model_name,
                    contents=[cache_content],
                    ttl="3600s"
                )

            self._cached_content_name = cached.name
            self._cached_content_text = cache_content
            print(f"Gemini Context Cache created: {cached.name}")
        except Exception as e:
            print(f"⚠️ Failed to create Gemini Context Cache: {e}")
            self._cached_content_name = None
            self._cached_content_text = ""
