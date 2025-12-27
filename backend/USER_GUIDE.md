# JARVIS FunctionGemma Integration - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Using the Function Calling Interface](#using-the-function-calling-interface)
4. [Common Tasks](#common-tasks)
5. [Migration from Legacy Mode](#migration-from-legacy-mode)
6. [Troubleshooting](#troubleshooting)

---

## Introduction

JARVIS now uses a local FunctionGemma-270M model for task planning, enabling fully local operation without external API dependencies. The new function calling interface provides a standardized, modular way to automate computer tasks through natural language commands.

### What's New

- **Local Processing**: All task planning happens locally using FunctionGemma
- **Standardized Functions**: 25+ functions organized into logical categories
- **Improved Reliability**: Command-line operations where possible, with better error handling
- **Backward Compatible**: Existing FlexiSIGN and vision-based features still work

### Key Benefits

- No external API costs or dependencies
- Faster response times for simple commands
- More predictable and testable behavior
- Easy to extend with new functions

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Windows operating system
- At least 4GB RAM (2GB for model)
- Required Python packages (see `requirements.txt`)

### Installation

1. **Install Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

2. **Download FunctionGemma Model**

The model will be automatically downloaded on first use, or you can download it manually:

```bash
python -c "from transformers import AutoProcessor, AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('google/functiongemma-270m-it')"
```

3. **Verify Installation**

```bash
python quick_test.py
```

You should see output indicating the model loaded successfully.

### First Command

Try a simple command to verify everything works:

```python
from functiongemma_service import FunctionGemmaPlannerService
from function_registry import FunctionRegistry

# Initialize the service
registry = FunctionRegistry()
service = FunctionGemmaPlannerService(
    model_path="google/functiongemma-270m-it",
    function_registry=registry
)

# Execute a command
result = service.execute_multi_step_task("create a folder called test_folder")
print(result)
```

---

## Using the Function Calling Interface

### Basic Concepts

**Functions**: Discrete operations like creating folders, clicking, typing text
**Categories**: Functions are organized into 5 categories:
- Folder Operations
- File Operations
- Keyboard Operations
- Mouse Operations
- Window Management

**Natural Language**: You describe what you want in plain English
**Function Calls**: The model converts your command into function calls
**Execution**: Functions execute in sequence to accomplish your task

### Command Structure

Commands can be simple or complex:

**Simple Command** (single function):
```
"create a folder called Documents"
```

**Complex Command** (multiple functions):
```
"open notepad, type hello world, and save the file as test.txt"
```

### Available Functions

#### Folder Operations

- `create_folder(path)` - Create a new folder
- `delete_folder(path, confirm_non_empty)` - Delete a folder
- `open_folder(path)` - Open folder in Windows Explorer
- `list_folder(path)` - List folder contents

#### File Operations

- `delete_file(path, confirm)` - Delete a file
- `rename_file(old_path, new_name)` - Rename a file
- `copy_file(source, destination)` - Copy a file
- `move_file(source, destination)` - Move a file
- `open_file(path)` - Open file with default application

#### Keyboard Operations

- `type_text(text, interval)` - Type text
- `press_key(key)` - Press a single key
- `press_hotkey(keys)` - Press keyboard shortcut
- `press_key_repeat(key, count)` - Press key multiple times

#### Mouse Operations

- `click(x, y)` - Click at coordinates
- `double_click(x, y)` - Double-click at coordinates
- `right_click(x, y)` - Right-click at coordinates
- `move_mouse(x, y, duration)` - Move mouse to coordinates
- `drag(start_x, start_y, end_x, end_y, duration)` - Drag between coordinates

#### Window Management

- `activate_window(identifier)` - Activate a window
- `close_window(identifier)` - Close a window
- `minimize_window(identifier)` - Minimize a window
- `maximize_window(identifier)` - Maximize a window
- `get_active_window()` - Get active window title

---

## Common Tasks

### Task 1: File Management

**Create and organize folders:**
```
"create a folder called Projects in my Documents"
```

**Copy files:**
```
"copy report.pdf from Downloads to Documents"
```

**Rename files:**
```
"rename old_file.txt to new_file.txt"
```

### Task 2: Text Editing

**Open and edit a file:**
```
"open notepad, type 'Meeting Notes', press enter twice, and type 'Attendees:'"
```

**Save a file:**
```
"press ctrl+s, type meeting_notes.txt, and press enter"
```

### Task 3: Window Management

**Switch between applications:**
```
"activate the Chrome window"
```

**Organize windows:**
```
"minimize all windows except Excel"
```

### Task 4: Automation Sequences

**Create a document workflow:**
```
"create a folder called Reports, open Word, type 'Monthly Report', save as report.docx in the Reports folder"
```

**Batch file operations:**
```
"copy all files from Downloads to Archive, then delete the originals"
```

### Task 5: Keyboard Shortcuts

**Common shortcuts:**
```
"press ctrl+c to copy"
"press alt+tab to switch windows"
"press win+d to show desktop"
```

---

## Migration from Legacy Mode

### Understanding the Modes

JARVIS supports multiple execution modes:

1. **Function Calling Mode** (New): Uses FunctionGemma with standardized functions
2. **Vision Mode** (Legacy): Uses visual detection and clicking
3. **Direct Path Mode** (Legacy): Uses keyboard automation for file dialogs
4. **FlexiSIGN Mode** (Legacy): Specialized for FlexiSIGN operations

### Automatic Mode Selection

The system automatically selects the appropriate mode based on your command:

- **FlexiSIGN keywords** → FlexiSIGN mode
- **Visual targets** → Vision mode
- **Function calls** → Function calling mode
- **Fallback** → Vision mode if function mode fails

### Migrating Your Workflows

**Before (Vision Mode):**
```json
{
  "steps": [
    {"type": "visual_click", "target": "New Folder button"},
    {"type": "type_text", "text": "MyFolder"},
    {"type": "press_key", "key": "enter"}
  ]
}
```

**After (Function Calling Mode):**
```
"create a folder called MyFolder"
```

### Benefits of Migration

- **Faster**: No visual detection overhead
- **More Reliable**: Command-line operations are deterministic
- **Easier to Debug**: Clear function calls and parameters
- **Better Error Messages**: Descriptive errors with context

### Backward Compatibility

All existing features continue to work:

- FlexiSIGN operations (create_text, set_font, etc.)
- Vision-based clicking for complex UIs
- Direct path automation for file dialogs

You can mix modes in the same workflow if needed.

---

## Troubleshooting

### Common Issues

#### Issue 1: Model Loading Fails

**Symptoms:**
```
Error: Failed to load FunctionGemma model
```

**Solutions:**
1. Check model path is correct
2. Ensure you have enough RAM (4GB minimum)
3. Verify transformers library is installed: `pip install transformers torch`
4. Try downloading model manually (see Installation section)

#### Issue 2: Function Not Found

**Symptoms:**
```
Error: Function 'xyz' not found in registry
```

**Solutions:**
1. Check function name spelling
2. Verify function is registered (see available functions list)
3. Try rephrasing your command
4. Check logs for parsing errors

#### Issue 3: Invalid Parameters

**Symptoms:**
```
Error: Invalid parameter 'path': expected string, got int
```

**Solutions:**
1. Check parameter types match function schema
2. Ensure paths are properly formatted (use forward slashes or double backslashes)
3. Verify coordinates are within screen bounds
4. Check required parameters are provided

#### Issue 4: Permission Denied

**Symptoms:**
```
Error: Permission denied: cannot delete file
```

**Solutions:**
1. Run JARVIS with administrator privileges
2. Check file is not in use by another application
3. Verify you have write permissions for the directory
4. Close applications that might be locking the file

#### Issue 5: Window Not Found

**Symptoms:**
```
Error: Window not found: Chrome
```

**Solutions:**
1. Verify window is open and visible
2. Try using exact window title (check with `get_active_window()`)
3. Use process name instead of window title
4. Check window is not minimized to system tray

### Performance Issues

#### Slow Model Loading

**Problem**: Model takes 5+ seconds to load

**Solutions:**
- Model is loaded once at startup and cached
- Ensure you're not reloading the model for each command
- Check available RAM (model needs ~2GB)
- Consider using a faster storage device (SSD)

#### Slow Command Execution

**Problem**: Commands take longer than expected

**Solutions:**
- Check network connectivity (shouldn't be needed, but verify no API calls)
- Reduce unnecessary delays in keyboard/mouse operations
- Use parallel execution for independent operations
- Profile slow functions and optimize

### Getting Help

#### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed information about:
- Model loading
- Function call parsing
- Parameter validation
- Execution steps
- Error details

#### Check Logs

Logs are stored in:
- Execution logs: `debug_logs/<timestamp>/execution_log.txt`
- Session info: `debug_logs/<timestamp>/session_info.json`

#### Report Issues

When reporting issues, include:
1. Your command or code
2. Error message (full stack trace)
3. Relevant log files
4. System information (OS, RAM, Python version)
5. Steps to reproduce

### Advanced Troubleshooting

#### Verify Function Registry

```python
from function_registry import FunctionRegistry

registry = FunctionRegistry()
print("Registered functions:", registry.get_all_function_names())
print("Categories:", registry.get_categories())
```

#### Test Individual Functions

```python
from functions.folder_operations import create_folder

result = create_folder("C:/test_folder")
print(result)
```

#### Validate Function Schemas

```python
from function_registry import FunctionRegistry

registry = FunctionRegistry()
schemas = registry.get_all_schemas()

for schema in schemas:
    print(f"Function: {schema['function']['name']}")
    print(f"Parameters: {schema['function']['parameters']}")
```

#### Test Parser

```python
from function_parser import extract_function_calls

text = "<start_function_call>call:create_folder{path:<escape>C:/test<escape>}<end_function_call>"
calls = extract_function_calls(text)
print(calls)
```

---

## Best Practices

### Writing Effective Commands

1. **Be Specific**: "create a folder called Reports in Documents" vs "make a folder"
2. **Use Full Paths**: "C:/Users/John/Documents/file.txt" vs "file.txt"
3. **Break Complex Tasks**: Multiple simple commands vs one complex command
4. **Verify Results**: Check command output for success/failure

### Safety Tips

1. **Confirm Destructive Operations**: Always confirm before deleting files/folders
2. **Backup Important Data**: Before running batch operations
3. **Test on Sample Data**: Try commands on test files first
4. **Use Version Control**: For code and important documents

### Performance Tips

1. **Batch Operations**: Group related operations together
2. **Use Command-Line**: Prefer function calling over UI automation
3. **Minimize Delays**: Reduce unnecessary waits in sequences
4. **Cache Results**: Store frequently accessed data

---

## Additional Resources

- **Developer Documentation**: See `DEVELOPER_GUIDE.md` for architecture and extending functions
- **Extensibility Guide**: See `EXTENSIBILITY_GUIDE.md` for adding new functions
- **API Reference**: See function schemas in `function_schemas.py`
- **Examples**: See `demo_functiongemma_service.py` and `extensibility_example.py`

---

## Feedback and Contributions

We welcome feedback and contributions! Please:

1. Report bugs and issues
2. Suggest new functions or improvements
3. Share your workflows and use cases
4. Contribute code and documentation

Thank you for using JARVIS!
