---
name: file_navigation
description: "Use this skill whenever the user wants to open files or folders by path, save files, or perform web automation/search tasks. Triggers include: 'open file', 'open folder', 'save file', 'search the web', 'find information', 'look up', 'weather', 'browse internet', 'web search', 'google', 'what is', 'who is'. Also use when the user mentions files in 'New Briefcase' or 'stickers' folder. REQUIRED for ANY task that requires browsing or searching the internet. Do NOT use for editing file content (use file_editing skill), creating folders (use shell skill), or FlexiSIGN operations (use flexisign skill)."
---

## Web Automation Agent (RECOMMENDED FOR ALL WEB TASKS):
For searching the web, finding information, or browser-based tasks:

**REQUIRED FIELDS:**
- "type": "web_automation"
- "prompt": The user's original request or a refined version for the web agent
- "desc": Brief description

**Example - Search for something:**
{
  "order": 1,
  "type": "web_automation",
  "prompt": "What is the capital of France?",
  "desc": "Search for capital of France"
}

**Example - Find weather:**
{
  "order": 1,
  "type": "web_automation",
  "prompt": "Current weather in Mumbai",
  "desc": "Get Mumbai weather"
}

**CRITICAL: Use web_automation for ANY task that requires browsing or searching the internet.**

## File and Folder Operations (FAST & RELIABLE):
Use filesystem-based operations that bypass UI completely. These use fuzzy path matching and are MUCH faster than UI navigation.

**IMPORTANT LOCATION MAPPINGS:**
- "New Briefcase" folder → use "stickers" (located at {STICKERS_PATH})
- "Desktop" → use "desktop"
- "Documents" → use "documents"
- "Downloads" → use "downloads"

**FILE EXTENSION RULE:**
NEVER add file extensions (.pdf, .docx, .fs, .txt) to paths. The system automatically finds the correct file with any extension.

### Open File (RECOMMENDED):
Use "open_file" to open any file with fuzzy path matching. NO UI/OCR needed!
{
  "type": "open_file",
  "path": "stickers/maan 22",
  "desc": "Open maan 22 file from New Briefcase"
}
- "path": Fuzzy path WITHOUT file extension (system finds it automatically)
  - Special folders: "desktop", "documents", "downloads", "stickers"
  - For New Briefcase files: use "stickers/filename" (NOT "desktop/new briefcase")
  - Examples: "stickers/maan 22", "desktop/report", "documents/file"
- NEVER add file extensions (.pdf, .docx, .fs) - system resolves them automatically
- Opens file directly with default application
- Resolves each path component with fuzzy matching

### Open Folder (RECOMMENDED):
Use "open_folder" to open any folder in Explorer with fuzzy path matching. NO UI/OCR needed!
{
  "type": "open_folder",
  "path": "desktop/jarvis test",
  "desc": "Open JARVIS Test folder"
}
- "path": Fuzzy path to folder
- Opens folder in Windows Explorer using 'explorer' command
- Resolves path components with fuzzy matching

### Save File:
Use "save_file" to save files by typing the full path into the Save dialog.
{
  "type": "save_file",
  "path": "{DESKTOP_PATH}\\document.txt",
  "desc": "Save file to Desktop"
}
- "path": Full absolute path (use double backslashes in JSON)

## Path Resolution Examples:
The system automatically resolves fuzzy paths:
- "desktop/jarvis test" → "{DESKTOP_PATH}\\JARVIS Test"
- "stickers/maan 22" → "{STICKERS_PATH}\\maan 22.FS"
- "documents/report" → "C:\\Users\\user\\Documents\\report.docx"
- Handles typos, case differences, partial names
- Automatically finds file extensions

## Example - Open file from New Briefcase (Stickers):
{
  "sequence":[
    {"order": 1, "type": "open_file", "path": "stickers/maan 22", "desc": "Open maan 22 file"}
  ],
  "expected_final_state": "maan 22 file opened in default application"
}

## Example - Open file from Desktop:
{
  "sequence":[
    {"order": 1, "type": "open_file", "path": "desktop/report", "desc": "Open report file"}
  ],
  "expected_final_state": "Report file opened in default application"
}

## Example - Open folder:
{
  "sequence":[
    {"order": 1, "type": "open_folder", "path": "desktop/jarvis test", "desc": "Open JARVIS Test folder"}
  ],
  "expected_final_state": "JARVIS Test folder opened in File Explorer"
}

## Example - Save a file:
{
  "sequence":[
    {"order": 1, "type": "save_file", "path": "{DESKTOP_PATH}\\notes.txt", "desc": "Save notes to Desktop"}
  ],
  "expected_final_state": "File saved to Desktop as notes.txt"
}

IMPORTANT for Direct Path Operations:
- Always use full absolute paths with proper escaping (double backslashes in JSON)
- Prefer direct path operations over manual UI navigation for file operations
- Use click_text for selecting files in File Explorer after navigating to the directory
