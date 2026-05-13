---
name: file_editing
description: "Use this skill whenever the user wants to create, edit, modify, or manipulate the content of files — especially Word (.docx), Excel (.xlsx), or Text (.txt) files using AI-powered editing, or when writing/reading/replacing content in code files. Triggers include: 'edit document', 'modify file', 'create Word', 'update Excel', 'write code', 'replace text in file', 'fix code', 'debug', 'write file', 'read file', 'append', 'create directory'. REQUIRED when user asks to edit, modify, or change content in any document or code file. Do NOT use for opening files by path (use file_navigation skill), sending emails (use email skill), or FlexiSIGN operations (use flexisign skill)."
---

## AI-POWERED FILE EDITING (RECOMMENDED FOR WORD/EXCEL/TEXT FILES):

For editing Word (.docx), Excel (.xlsx), or Text (.txt) files with natural language instructions:

**REQUIRED FIELDS:**
- "type": Must be "ai_edit_word" (for .docx), "ai_edit_excel" (for .xlsx), or "ai_edit_text" (for .txt)
- "path": Fuzzy path to the file (e.g., "desktop/report" or "desktop/input")
- "prompt": Natural language instructions describing what to change (e.g., "Replace Harshit with Ayushi")
- "desc": Brief description of the action

**CRITICAL: Both "path" and "prompt" are REQUIRED. DO NOT omit either field.**

**Example - Edit Word document:**
{
  "order": 1,
  "type": "ai_edit_word",
  "path": "desktop/input",
  "prompt": "Replace the name Harshit Singla with Ayushi and replace the phone number with 9872113958",
  "desc": "Update name and phone in Word document"
}

**Example - Edit Excel spreadsheet:**
{
  "order": 1,
  "type": "ai_edit_excel",
  "path": "desktop/sales_data",
  "prompt": "Add a Commission column that calculates 5% of Sales",
  "desc": "Add commission calculations"
}

**Example - Edit text file:**
{
  "order": 1,
  "type": "ai_edit_text",
  "path": "desktop/notes",
  "prompt": "Organize into sections: Attendees, Discussion, Action Items",
  "desc": "Restructure meeting notes"
}

## PLANE 2: CODE WORKSPACE CONTROL (RECOMMENDED FOR CODE FILES):
For creating/editing code files and structured content, use these direct file operations. They are MUCH faster and more reliable than UI-based editing.

**CRITICAL: The Modern Workflow for Code Files:**
1. **Create folder** using `shell_command` (e.g., `mkdir "{DESKTOP_PATH}\LabCode"`)
2. **Write file content** using `write_file` with full code (NO UI interaction needed!)
3. **Open in editor** using `shell_command` (e.g., `code "path\to\file.py"` for VS Code)
4. **Run program** using keyboard shortcuts (Ctrl+` for terminal, then type command)

**INTELLIGENT FILE MODIFICATION WORKFLOW (CRITICAL FOR EDITING EXISTING FILES):**
When user asks to modify, edit, update, change, or fix an existing file:

**STEP 1: READ THE FILE FIRST**
{
  "type": "read_file",
  "path": "{DESKTOP_PATH}\\form.txt",
  "desc": "Read current file content to understand what needs to be changed"
}

**STEP 2: MODIFY USING SEARCH/REPLACE**
Use `replace_in_file` for targeted changes (PREFERRED - works like IDE Find & Replace):
{
  "type": "replace_in_file",
  "path": "{DESKTOP_PATH}\\form.txt",
  "old_text": "Name: John Doe",
  "new_text": "Name: Harshit Singla",
  "desc": "Replace the name field with new value"
}

**CRITICAL: For replace_in_file:**
- `old_text` must be the COMPLETE text you want to replace (e.g., "Name: John Doe", not just "Name:")
- `new_text` is the COMPLETE replacement text (e.g., "Name: Harshit Singla")
- The operation finds `old_text` and replaces it entirely with `new_text`
- Think of it like: Find "Name: John Doe" → Replace with "Name: Harshit Singla"

**WRONG (will result in "Name: Harshit Singla John Doe"):**
{
  "old_text": "Name:",
  "new_text": "Name: Harshit Singla"
}

**CORRECT (will result in "Name: Harshit Singla"):**
{
  "old_text": "Name: John Doe",
  "new_text": "Name: Harshit Singla"
}

OR use `modify_lines` for line-specific changes:
{
  "type": "modify_lines",
  "path": "{DESKTOP_PATH}\\form.txt",
  "line_number": 5,
  "new_content": "Name: Harshit Singla",
  "num_lines": 1,
  "desc": "Update line 5 with new name"
}

OR use `write_file` ONLY if you need to rewrite the entire file:
{
  "type": "write_file",
  "path": "{DESKTOP_PATH}\\form.txt",
  "content": "Full updated content here...",
  "desc": "Rewrite entire file with modifications"
}

**STEP 3: VERIFY (OPTIONAL)**
{
  "type": "shell_command",
  "command": "start \"\" \"{DESKTOP_PATH}\\form.txt\"",
  "desc": "Open file to verify changes"
}

**CRITICAL RULES FOR FILE MODIFICATIONS:**
1. ALWAYS use `read_file` FIRST when modifying existing files
2. NEVER use placeholder text like {UPDATED_CONTENT} - always provide actual content
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
{
  "type": "write_file",
  "path": "{DESKTOP_PATH}\\LabCode\\bubble_sort.py",
  "content": "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n\ndata =[64, 34, 25, 12, 22, 11, 90]\nbubble_sort(data)\nprint(data)",
  "desc": "Write bubble sort program"
}
- "path": Full absolute path to file (use {DESKTOP_PATH} or {DOCUMENTS_PATH} for user directories)
- "content": Complete file content (use \n for newlines, escape quotes)
- Creates parent directories automatically if they don't exist
- Overwrites file if it already exists

### Read File:
Use "read_file" to read file contents.
{
  "type": "read_file",
  "path": "{DESKTOP_PATH}\\script.py",
  "desc": "Read script contents"
}

### Append File:
Use "append_file" to add content to existing file.
{
  "type": "append_file",
  "path": "{DESKTOP_PATH}\\log.txt",
  "content": "New log entry\n",
  "desc": "Append to log file"
}

### Create Directory:
Use "create_directory" to create folders.
{
  "type": "create_directory",
  "path": "{DESKTOP_PATH}\\Projects\\Python",
  "desc": "Create Python projects folder"
}

**Example - Create Python program and run in VS Code (MODERN APPROACH):**
{
  "sequence":[
    {"order": 1, "type": "shell_command", "command": "mkdir \"{DESKTOP_PATH}\\LabCode\"", "desc": "Create LabCode folder"},
    {"order": 2, "type": "write_file", "path": "{DESKTOP_PATH}\\LabCode\\bubble_sort.py", "content": "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        swapped = False\n        for j in range(0, n - i - 1):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n                swapped = True\n        if not swapped:\n            break\n    return arr\n\nif __name__ == \"__main__\":\n    data = input(\"Enter numbers separated by spaces: \").strip()\n    if not data:\n        print(\"No input provided.\")\n    else:\n        arr = list(map(int, data.split()))\n        bubble_sort(arr)\n        print(\"Sorted array:\", *arr)", "desc": "Write bubble sort program"},
    {"order": 3, "type": "shell_command", "command": "code \"{DESKTOP_PATH}\\LabCode\"", "desc": "Open folder in VS Code"},
    {"order": 4, "type": "keyboard", "value": "ctrl+`", "desc": "Open integrated terminal"},
    {"order": 5, "type": "keyboard", "value": "python bubble_sort.py", "desc": "Type run command"},
    {"order": 6, "type": "keyboard", "value": "enter", "desc": "Execute program"}
  ],
  "expected_final_state": "VS Code showing bubble_sort.py with terminal ready to run the program"
}

**Example - Debug existing code (READ → ANALYZE → FIX → WRITE):**
{
  "sequence":[
    {"order": 1, "type": "read_file", "path": "{DESKTOP_PATH}\\LabCode\\bubble_sort.py", "desc": "Read existing code to analyze"},
    {"order": 2, "type": "write_file", "path": "{DESKTOP_PATH}\\LabCode\\bubble_sort.py", "content": "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        swapped = False\n        for j in range(0, n - i - 1):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n                swapped = True\n        if not swapped:\n            break\n    return arr\n\nif __name__ == \"__main__\":\n    data =[64, 34, 25, 12, 22, 11, 90]\n    result = bubble_sort(data)\n    print(\"Sorted array:\", result)", "desc": "Write corrected code with bug fixes"},
    {"order": 3, "type": "shell_command", "command": "code \"{DESKTOP_PATH}\\LabCode\\bubble_sort.py\"", "desc": "Open fixed file in VS Code"},
    {"order": 4, "type": "keyboard", "value": "ctrl+`", "desc": "Open integrated terminal"},
    {"order": 5, "type": "keyboard", "value": "python bubble_sort.py", "desc": "Type run command"},
    {"order": 6, "type": "keyboard", "value": "enter", "desc": "Execute program"}
  ],
  "expected_final_state": "VS Code showing debugged bubble_sort.py with terminal displaying sorted output"
}

**Example - Copy code from document to new file:**
{
  "sequence":[
    {"order": 1, "type": "read_file", "path": "{DESKTOP_PATH}\\AI Lab\\Practical 1.txt", "desc": "Read code from document"},
    {"order": 2, "type": "write_file", "path": "{DESKTOP_PATH}\\LabCode\\dfs.py", "content": "# DFS Algorithm Implementation\ndef dfs(graph, start, visited=None):\n    if visited is None:\n        visited = set()\n    visited.add(start)\n    print(start, end=' ')\n    for neighbor in graph[start]:\n        if neighbor not in visited:\n            dfs(graph, neighbor, visited)\n    return visited\n\nif __name__ == \"__main__\":\n    graph = {\n        'A': ['B', 'C'],\n        'B':['D', 'E'],\n        'C': ['F'],\n        'D':[],\n        'E': ['F'],\n        'F':[]\n    }\n    print(\"DFS Traversal:\")\n    dfs(graph, 'A')", "desc": "Write extracted code to new Python file"},
    {"order": 3, "type": "shell_command", "command": "code \"{DESKTOP_PATH}\\LabCode\\dfs.py\"", "desc": "Open new file in VS Code"},
    {"order": 4, "type": "keyboard", "value": "ctrl+`", "desc": "Open integrated terminal"},
    {"order": 5, "type": "keyboard", "value": "python dfs.py", "desc": "Type run command"},
    {"order": 6, "type": "keyboard", "value": "enter", "desc": "Execute program"}
  ],
  "expected_final_state": "VS Code showing dfs.py with terminal displaying DFS traversal output"
}

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
