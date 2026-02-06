# JARVIS - Complete Feature List

## Overview
JARVIS is a multi-plane AI automation system that combines command-line operations, direct file manipulation, and GUI automation to control Windows computers through natural language.

---

## 🎯 Core Capabilities

### 1. **Intelligent Planning System**
- **Auto-mode Detection**: Automatically detects whether command is for general automation or FlexiSIGN
- **Two-Model Pipeline**: Separates planning (Gemini Flash Lite) from execution (Vision Mapper)
- **Expected State Verification**: Validates task completion using vision AI
- **Retry Logic**: Automatically retries failed operations with verification
- **Debug Logging**: Comprehensive session logs with screenshots, plans, and execution traces

### 2. **Multi-Plane Execution Architecture**

#### **Plane 1: Command-Line Operations (Priority #1)**
- Execute Windows shell commands directly
- Create folders and files via CMD
- Launch applications with `start` command
- Chain multiple commands with `&` operator
- Environment variable expansion (%USERPROFILE%, etc.)
- Silent background execution

#### **Plane 2: Code Workspace Control (Priority #2)**
- Direct file I/O without UI interaction
- Intelligent file editing (IDE-like capabilities)
- Read-modify-write workflows
- Code generation and manipulation

#### **Plane 3: UI Automation (Priority #3 - Fallback)**
- Vision-based element detection (FastSAM + Gemini Vision)
- OCR-based text clicking
- Keyboard shortcuts and typing
- Window management and activation

---

## 📋 Supported Step Types

### **Keyboard & Input Operations**

#### `keyboard`
**Description**: Type text or press keys/shortcuts
**Parameters**:
- `value` (string): Text to type or key to press
  - Text: `"Hello World"`
  - Special keys: `"enter"`, `"tab"`, `"escape"`, `"backspace"`, `"delete"`, `"up"`, `"down"`, `"left"`, `"right"`, `"f1"`-`"f12"`
  - Shortcuts: `"ctrl+c"`, `"alt+tab"`, `"win+r"`, `"ctrl+shift+esc"`
- `repeats` (int, optional): Number of times to repeat

**Features**:
- Smart window activation before input
- App launch detection and window waiting
- Hotkey combination support
- Configurable delays for different key types

**Examples**:
```json
{"type": "keyboard", "value": "win", "desc": "Open Start menu"}
{"type": "keyboard", "value": "notepad", "desc": "Type app name"}
{"type": "keyboard", "value": "ctrl+s", "desc": "Save file"}
{"type": "keyboard", "value": "Hello World!", "desc": "Type text"}
```

---

### **UI Interaction Operations**

#### `visual_click`
**Description**: Click UI elements using vision AI (SLOW - last resort)
**Parameters**:
- `target_name` (string): Descriptive name of element
  - Examples: `"button_OK"`, `"chrome_address_bar"`, `"menu_File"`, `"icon_chrome"`

**Features**:
- FastSAM segmentation for UI element detection
- Gemini Vision for element identification
- Set-of-Mark (SoM) annotation system
- Automatic coordinate calculation
- Fallback to screen center for canvas elements

**Examples**:
```json
{"type": "visual_click", "target_name": "button_Compose", "desc": "Click Gmail compose"}
{"type": "visual_click", "target_name": "chrome_address_bar", "desc": "Focus address bar"}
```

#### `click_text_fast`
**Description**: Click UI elements by visible text using OCR (FAST - preferred)
**Parameters**:
- `window_title` (string): Partial or full window title
- `text` (string): Exact text to find and click

**Features**:
- Fast OCR-based text detection
- Fuzzy matching (partial word matching)
- Window-specific scanning
- Works for buttons, menus, contacts, file names

**Examples**:
```json
{"type": "click_text_fast", "window_title": "WhatsApp", "text": "Harshit", "desc": "Click contact"}
{"type": "click_text_fast", "window_title": "Inbox", "text": "Send", "desc": "Click Send button"}
```

#### `click_text`
**Description**: Click text using OCR (slower, more thorough)
**Parameters**:
- `text` (string): Text to find and click

**Features**:
- Full-screen OCR scanning
- More thorough than click_text_fast
- Used when window title unknown

---

### **File & Folder Operations**

#### `open_file`
**Description**: Open any file with fuzzy path matching (NO UI needed)
**Parameters**:
- `path` (string): Fuzzy path WITHOUT file extension
  - Special folders: `"desktop"`, `"documents"`, `"downloads"`, `"stickers"`
  - Examples: `"stickers/maan 22"`, `"desktop/report"`, `"documents/file"`

**Features**:
- Fuzzy path resolution (handles typos, case differences)
- Automatic file extension detection
- Opens with default application
- Resolves each path component with fuzzy matching

**Examples**:
```json
{"type": "open_file", "path": "stickers/maan 22", "desc": "Open file from New Briefcase"}
{"type": "open_file", "path": "desktop/report", "desc": "Open report file"}
```

#### `open_folder`
**Description**: Open folder in Windows Explorer with fuzzy matching
**Parameters**:
- `path` (string): Fuzzy path to folder

**Features**:
- Fuzzy path resolution
- Opens in Windows Explorer
- Handles special folders

**Examples**:
```json
{"type": "open_folder", "path": "desktop/jarvis test", "desc": "Open JARVIS Test folder"}
```

#### `save_file`
**Description**: Save file by typing path into Save dialog
**Parameters**:
- `path` (string): Full absolute path

**Features**:
- Triggers Ctrl+S automatically
- Waits for Save dialog
- Types path into dialog
- Handles overwrite confirmations
- Error dialog detection via OCR

**Examples**:
```json
{"type": "save_file", "path": "C:\\Users\\harsh\\Desktop\\document.txt", "desc": "Save to Desktop"}
```

#### `navigate_explorer`
**Description**: Navigate to directory in File Explorer using address bar
**Parameters**:
- `directory` (string): Directory path

**Features**:
- Uses Explorer address bar (fast and reliable)
- Waits for navigation to complete
- Extra delay for UI to settle

#### `resolve_filename`
**Description**: Resolve fuzzy filename to exact match in directory
**Parameters**:
- `directory` (string): Directory to search
- `query` (string): Fuzzy filename query

**Features**:
- Filesystem-based fuzzy matching
- Returns exact filename
- Used internally by other operations

---

### **Shell Command Operations**

#### `shell_command`
**Description**: Execute Windows shell commands directly (FASTEST method)
**Parameters**:
- `command` (string): Shell command to execute

**Supported Commands**:
- Create folder: `mkdir "Folder Name"`
- Create file: `type nul > "filename.txt"`
- Create multiple files: `type nul > file1.txt & type nul > file2.txt`
- Open file: `start "" "full\path\to\file.txt"`
- Open folder: `explorer "%USERPROFILE%\Desktop\FolderName"`
- Delete file: `del "filename.txt"`
- Delete folder: `rmdir /s /q "FolderName"`
- Copy file: `copy "source.txt" "dest.txt"`
- Move file: `move "source.txt" "dest.txt"`
- Chain commands: Use `&` to run multiple

**Features**:
- Direct command execution (no UI)
- Environment variable expansion
- Automatic waiting for window creation (with `start` command)
- Command chaining support
- Fastest method for file/folder operations

**Examples**:
```json
{"type": "shell_command", "command": "mkdir \"%USERPROFILE%\\Desktop\\AI Lab\"", "desc": "Create folder"}
{"type": "shell_command", "command": "type nul > \"%USERPROFILE%\\Desktop\\notes.txt\"", "desc": "Create file"}
{"type": "shell_command", "command": "start \"\" \"%USERPROFILE%\\Desktop\\notes.txt\"", "desc": "Open file"}
{"type": "shell_command", "command": "explorer \"%USERPROFILE%\\Desktop\\AI Lab\"", "desc": "Open folder"}
```

---

### **Code Workspace Control (Plane 2)**

#### `write_file`
**Description**: Create or overwrite file with content (NO UI interaction)
**Parameters**:
- `path` (string): Full absolute path
- `content` (string): Complete file content (use `\n` for newlines)

**Features**:
- Direct file I/O (no editor needed)
- Creates parent directories automatically
- Handles long code perfectly
- Preserves exact formatting
- Supports environment variables

**Examples**:
```json
{
  "type": "write_file",
  "path": "%USERPROFILE%\\Desktop\\LabCode\\bubble_sort.py",
  "content": "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr",
  "desc": "Write bubble sort program"
}
```

#### `read_file`
**Description**: Read content from a file
**Parameters**:
- `path` (string): Full absolute path

**Features**:
- Direct file reading
- Caches content for read-modify-write workflows
- Supports environment variables
- Returns content to planner for analysis

**Examples**:
```json
{"type": "read_file", "path": "%USERPROFILE%\\Desktop\\script.py", "desc": "Read script"}
```

#### `append_file`
**Description**: Append content to existing file
**Parameters**:
- `path` (string): Full absolute path
- `content` (string): Content to append

**Features**:
- Adds content to end of file
- Automatic newline handling
- Preserves existing content

**Examples**:
```json
{"type": "append_file", "path": "%USERPROFILE%\\Desktop\\log.txt", "content": "New log entry\n", "desc": "Append to log"}
```

#### `create_directory`
**Description**: Create directory (and parent directories if needed)
**Parameters**:
- `path` (string): Full absolute path

**Features**:
- Creates nested directories
- No error if already exists
- Supports environment variables

**Examples**:
```json
{"type": "create_directory", "path": "%USERPROFILE%\\Desktop\\Projects\\Python", "desc": "Create nested folders"}
```

---

### **Intelligent File Editing (IDE-like)**

#### `replace_in_file`
**Description**: Search and replace text in file (like IDE Find & Replace)
**Parameters**:
- `path` (string): Full absolute path
- `old_text` (string): COMPLETE text to replace (e.g., "Name: John Doe")
- `new_text` (string): COMPLETE replacement text (e.g., "Name: Harshit Singla")
- `count` (int, optional): Number of replacements (-1 for all)

**Features**:
- Fast targeted changes
- Shows diff preview
- Multiple replacement support
- Preserves file structure

**CRITICAL**: `old_text` must be the COMPLETE text to replace, not just a prefix!

**Examples**:
```json
{
  "type": "replace_in_file",
  "path": "%USERPROFILE%\\Desktop\\form.txt",
  "old_text": "Name: John Doe",
  "new_text": "Name: Harshit Singla",
  "desc": "Update name field"
}
```

#### `modify_lines`
**Description**: Modify specific lines in a file
**Parameters**:
- `path` (string): Full absolute path
- `line_number` (int): Line number to modify (1-indexed)
- `new_content` (string): New content for the line(s)
- `num_lines` (int, optional): Number of lines to replace (default 1)

**Features**:
- Line-specific editing
- Shows diff preview
- Multi-line replacement support

**Examples**:
```json
{
  "type": "modify_lines",
  "path": "%USERPROFILE%\\Desktop\\form.txt",
  "line_number": 5,
  "new_content": "Name: Harshit Singla",
  "num_lines": 1,
  "desc": "Update line 5"
}
```

#### `insert_at_line`
**Description**: Insert content at specific line
**Parameters**:
- `path` (string): Full absolute path
- `line_number` (int): Line number to insert at
- `content` (string): Content to insert

**Features**:
- Inserts before specified line
- Shows diff preview
- Preserves existing content

**Examples**:
```json
{
  "type": "insert_at_line",
  "path": "%USERPROFILE%\\Desktop\\code.py",
  "line_number": 10,
  "content": "    # New comment\n    new_code_line()",
  "desc": "Insert code at line 10"
}
```

#### `delete_lines`
**Description**: Delete specific lines from file
**Parameters**:
- `path` (string): Full absolute path
- `start_line` (int): First line to delete
- `end_line` (int, optional): Last line to delete (if omitted, deletes only start_line)

**Features**:
- Single or range deletion
- Shows diff preview
- Preserves rest of file

**Examples**:
```json
{
  "type": "delete_lines",
  "path": "%USERPROFILE%\\Desktop\\code.py",
  "start_line": 15,
  "end_line": 20,
  "desc": "Delete lines 15-20"
}
```

---

### **Critical Operations (Require Permission)**

#### `delete_file`
**Description**: Delete a file from filesystem
**Parameters**:
- `path` (string): Full absolute path

**Features**:
- Permission request before execution
- Confirmation dialog
- Safe deletion

#### `delete_folder`
**Description**: Delete folder and all contents
**Parameters**:
- `path` (string): Full absolute path

**Features**:
- Permission request before execution
- Recursive deletion
- Confirmation dialog

---

### **FlexiSIGN-Specific Operations (Direct Mode)**

#### `ensure_designcentral`
**Description**: Ensure DesignCentral panel is open
**Features**:
- Required before `set_dimensions` or `set_font`
- Uses Windows UI Automation (UIA)

#### `create_text`
**Description**: Create text object in FlexiSIGN
**Parameters**:
- `text` (string): Text content

**Features**:
- Direct UIA automation
- No vision needed

#### `set_dimensions`
**Description**: Set object dimensions
**Parameters**:
- `width` (string): Width value
- `height` (string): Height value

**Features**:
- Requires `ensure_designcentral` first
- Direct UIA automation

#### `set_font`
**Description**: Set font for text object
**Parameters**:
- `font_name` (string): Font name

**Features**:
- Requires `ensure_designcentral` first
- Direct UIA automation

#### `apply_style`
**Description**: Apply preset style (Government plates)
**Parameters**:
- `style_name` (string, optional): Style name

**Features**:
- Direct UIA automation
- Used for government plates

#### `move_object`
**Description**: Move selected object
**Parameters**:
- `direction` (string): `"up"`, `"down"`, `"left"`, `"right"`
- `distance` (int): Number of arrow key presses

**Features**:
- Direct UIA automation
- Precise positioning

---

## 🔧 Advanced Features

### **Window Management**
- Automatic window activation before input
- Window title detection and tracking
- Foreground window management
- App launch detection and waiting
- Multi-window support

### **Readiness Detection**
- Browser readiness detection (page load complete)
- Desktop app readiness (control count stable)
- Filesystem readiness (folder creation verification)
- CPU usage monitoring
- Configurable timeouts and thresholds

### **Adaptive Re-scanning**
- Detects UI changes during execution
- Automatically re-scans when needed
- Optimizes vision passes
- Reduces unnecessary screenshots

### **Permission System**
- Critical operation detection
- User confirmation dialogs
- Abort task functionality
- Permission request/response flow

### **Debug & Logging**
- Session-based debug folders
- Screenshot capture
- Annotated image logging
- Box map and ID map logging
- Vision mapper output logging
- Execution log with timestamps
- Verification result logging

### **Error Handling**
- Automatic retry with verification
- Configurable retry count and delay
- Error dialog detection (OCR-based)
- Graceful degradation
- Comprehensive error messages

### **Path Resolution**
- Fuzzy path matching
- Environment variable expansion
- Special folder support (desktop, documents, downloads, stickers)
- Automatic file extension detection
- Typo tolerance

### **Audio Feedback**
- Start sound on execution begin
- Complete sound on execution finish
- Optional (requires pygame)

---

## 🎨 Execution Modes

### **General Mode** (Default)
- For any computer automation task
- Prioritizes command-line and file operations
- Uses UI automation as fallback
- Supports all step types

### **FlexiSIGN Mode** (Auto-detected)
- For number plate creation
- Uses direct UIA automation
- Domain-specific knowledge (plate dimensions)
- Specialized commands

### **Vision Mode** (Fallback)
- When direct methods unavailable
- Uses FastSAM + Gemini Vision
- Slower but works with any UI
- Last resort option

---

## 📊 Performance Characteristics

### **Speed Comparison**
- **Shell command**: ~0.1 seconds
- **File operation**: ~0.1 seconds
- **Keyboard action**: ~0.3-0.5 seconds
- **OCR click (fast)**: ~1-2 seconds
- **Vision click (slow)**: ~3-5 seconds

### **Typical Task Times**
- Create folder + file: ~0.5 seconds (shell)
- Write Python file: ~0.2 seconds (write_file)
- Open file: ~0.5 seconds (open_file)
- Launch app: ~3-5 seconds (with window wait)
- Vision-based task: ~10-15 seconds (with screenshot)

---

## 🔐 Security Features

- Permission system for critical operations
- User confirmation before deletion
- Abort task functionality
- Safe path handling
- No arbitrary code execution (unlike Open Interpreter)
- Sandboxed file operations

---

## 🌐 Integration Features

### **Mobile App Control**
- React Native mobile interface
- WebSocket communication
- Real-time status updates
- Progress tracking
- Permission request/response
- Task abort capability

### **Backend Server**
- Flask + SocketIO
- Plan generation API
- Status broadcasting
- Multi-client support
- Session management

### **Local Client**
- WebSocket connection
- Plan execution engine
- Vision service integration
- Debug logging
- Permission handling

---

## 📝 Configuration

### **Configurable Settings**
- LLM provider (Gemini or OpenAI)
- API keys
- User paths (Desktop, Documents, Downloads, Stickers)
- Verification settings (enabled, delay, confidence threshold)
- Retry settings (max retries, delay)
- Readiness detection timeouts
- Window activation timeouts
- Overwrite policies

### **Path Configuration**
- Custom path mappings
- Fuzzy matching thresholds
- Special folder aliases
- Environment variable support

---

## 🎯 Use Cases

### **Developer Productivity**
- Create project folders and files
- Write complete code files
- Read and modify existing code
- Debug and fix code
- Run programs and see output
- Automate repetitive coding tasks

### **System Automation**
- Launch applications
- Navigate file system
- Create/delete files and folders
- Execute shell commands
- Manage windows

### **GUI Automation**
- Click buttons in applications
- Fill forms
- Navigate menus
- Interact with legacy apps
- Control apps without APIs

### **File Management**
- Organize files and folders
- Batch file operations
- Search and replace in files
- Intelligent file editing
- Fuzzy file finding

### **FlexiSIGN Automation**
- Create number plates
- Set dimensions and fonts
- Apply styles
- Position objects
- Batch plate creation

---

## 🚀 Unique Advantages

1. **Multi-Plane Architecture**: Combines command-line, file ops, and GUI in one system
2. **Intelligent Prioritization**: Always uses fastest method available
3. **Fuzzy Path Matching**: Handles typos and partial names
4. **Hybrid Workflows**: Seamlessly mix different execution planes
5. **Verification System**: Validates task completion with vision AI
6. **Adaptive Re-scanning**: Optimizes vision passes based on UI changes
7. **Developer-Focused**: Direct code manipulation without UI
8. **Windows Integration**: Deep system integration with native APIs

---

## 📚 Documentation

- Comprehensive system prompts with examples
- Inline code documentation
- Debug logging for troubleshooting
- Error messages with context
- Diff previews for file edits
- Progress tracking and status updates

---

## 🔮 Future Capabilities (Roadmap)

- Voice activation ("Hey JARVIS")
- Camera/OCR input
- Multi-monitor support
- Task scheduling
- Conversation memory
- Query optimization
- Mac/Linux support
- Offline mode (local models)
