---
name: shell
description: "Use this skill whenever the user needs to run command prompt or PowerShell operations: creating folders, creating empty files, deleting files/folders, copying or moving files, running scripts, or any task best accomplished via shell commands. Triggers include: 'create folder', 'mkdir', 'delete', 'copy', 'move', 'rename', 'run script', 'command', 'terminal', 'PowerShell', 'cmd'. This is the PREFERRED method for file/folder operations — always use shell commands before UI-based approaches. Do NOT use for editing file content (use file_editing skill), opening files by path (use file_navigation skill), or FlexiSIGN operations (use flexisign skill)."
---

### File Operations (STRICT RULES):
- DO NOT assume any keyboard shortcut creates files or folders
- There is NO universal shortcut for "new text file"
- File and folder creation MUST use:
  - Command-line operations (PREFERRED - fastest and most reliable), OR
  - Direct filesystem operations, OR
  - Explicit UI menu navigation (LAST RESORT - e.g., right-click → New → Text Document)
- Ctrl+N MAY ONLY be used when the user explicitly requests "new window" or "new document" AND the application is known

**IMPORTANT Command Syntax (default shell is PowerShell — not CMD):**
- Create folder: `mkdir FolderName` / `New-Item -ItemType Directory -Path "..." -Force`
- Create empty file (PowerShell): `New-Item -ItemType File -Path "filename.txt" -Force`
  - Alternatively empty UTF-8 file: `Set-Content -Path "filename.txt" -Value ""`
  - **CMD-only idiom** `type nul > file.txt` breaks under PowerShell (`type` is `Get-Content`). Only use it wrapped as: `cmd /c "type nul > filename.txt"`
- Create multiple files: chain with `;` in PowerShell (e.g. `New-Item -ItemType File -Path "a.txt" -Force; New-Item ...`)
- Navigate to Desktop: `cd {DESKTOP_PATH}`
- Navigate to Documents: `cd {DOCUMENTS_PATH}`
- Open folder in Explorer: `explorer FolderName` or `explorer .` (current folder)
- Chain commands: Use `&&` to run multiple commands (e.g., `mkdir test && cd test`)

**IMPORTANT: When creating folders/files, ALWAYS end with opening the folder in Explorer** so the user can see the result.
Example: After creating "AI Lab" folder with files, add: `explorer "{DESKTOP_PATH}\AI Lab"`

## Shell Command Operations (HYBRID CLI APPROACH - PREFERRED):
For file/folder creation and manipulation, ALWAYS use shell commands FIRST. This is the "Killer Combo" workflow:

**CRITICAL: The Killer Combo Workflow for File Operations:**
1. **Create** the file/folder using `shell_command` FIRST with **PowerShell-safe** commands (see Command Syntax above). Avoid bare `type nul >` unless wrapped in `cmd /c`.
2. **Open** the file using `open_file` or `start filename` command
3. **Edit** via keyboard actions
4. **Save** via `Ctrl+S` (silent save because file already exists)

**Shell Command Tool:**
{
  "type": "shell_command",
  "command": "mkdir MyFolder",
  "desc": "Create MyFolder directory"
}

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
{
  "sequence":[
    {"order": 1, "type": "shell_command", "command": "type nul > \"{DESKTOP_PATH}\\notes.txt\"", "desc": "Create notes.txt on Desktop"},
    {"order": 2, "type": "shell_command", "command": "start \"\" \"{DESKTOP_PATH}\\notes.txt\"", "desc": "Open notes.txt"},
    {"order": 3, "type": "keyboard", "value": "Hello World!", "desc": "Type content"},
    {"order": 4, "type": "keyboard", "value": "enter", "desc": "New line"},
    {"order": 5, "type": "keyboard", "value": "ctrl+s", "desc": "Save file (silent)"}
  ],
  "expected_final_state": "Notepad showing notes.txt with 'Hello World!' saved"
}

**CRITICAL: For multi-line text or code, ALWAYS use write_file (Plane 2) instead of typing simulate. It is faster and safer.**

**Example - Create folder with file (spaces in names):**
{
  "sequence":[
    {"order": 1, "type": "shell_command", "command": "mkdir \"{DESKTOP_PATH}\\AI Lab\" & type nul > \"{DESKTOP_PATH}\\AI Lab\\Practical 1.txt\"", "desc": "Create AI Lab folder with Practical 1 file"},
    {"order": 2, "type": "shell_command", "command": "start \"\" \"{DESKTOP_PATH}\\AI Lab\\Practical 1.txt\"", "desc": "Open Practical 1 file"},
    {"order": 3, "type": "keyboard", "value": "AIM: To implement BFS algorithm", "desc": "Type content"},
    {"order": 4, "type": "keyboard", "value": "ctrl+s", "desc": "Save file (silent)"}
  ],
  "expected_final_state": "Notepad showing Practical 1.txt with content saved in AI Lab folder"
}

**Example - Create folder structure:**
{
  "sequence":[
    {"order": 1, "type": "shell_command", "command": "mkdir \"{DESKTOP_PATH}\\Projects\" & mkdir \"{DESKTOP_PATH}\\Projects\\Python\"", "desc": "Create nested folders"},
    {"order": 2, "type": "shell_command", "command": "explorer \"{DESKTOP_PATH}\\Projects\"", "desc": "Open Projects folder in Explorer"}
  ],
  "expected_final_state": "Explorer showing Projects folder with Python subfolder"
}

**Example - Create folder with spaces and open it:**
{
  "sequence":[
    {"order": 1, "type": "shell_command", "command": "mkdir \"{DESKTOP_PATH}\\AI Lab\"", "desc": "Create AI Lab folder"},
    {"order": 2, "type": "write_file", "path": "{DESKTOP_PATH}\\AI Lab\\notes.txt", "content": "Lab notes here", "desc": "Create notes file"},
    {"order": 3, "type": "shell_command", "command": "explorer \"{DESKTOP_PATH}\\AI Lab\"", "desc": "Open AI Lab folder in Explorer"}
  ],
  "expected_final_state": "Explorer showing AI Lab folder with notes.txt file"
}

**IMPORTANT:** This approach does NOT work with FlexiSIGN file operations. For FlexiSIGN, use the standard FlexiSIGN workflow.
