# JARVIS FunctionGemma - Troubleshooting Guide

## Quick Diagnostics

Run these commands to diagnose common issues:

```bash
# Check Python version (need 3.8+)
python --version

# Check installed packages
pip list | grep -E "transformers|torch|hypothesis|pytest"

# Verify model can be loaded
python -c "from transformers import AutoProcessor, AutoModelForCausalLM; print('OK')"

# Run quick test
cd backend
python quick_test.py
```

---

## Common Issues

### 1. Model Loading Fails

#### Symptoms
```
Error: Failed to load FunctionGemma model
ModuleNotFoundError: No module named 'transformers'
RuntimeError: Insufficient memory
```

#### Solutions

**Missing Dependencies**:
```bash
pip install transformers torch
```

**Insufficient Memory**:
- Close other applications
- Ensure at least 4GB RAM available
- Check Task Manager for memory usage
- Consider upgrading RAM

**Model Not Downloaded**:
```bash
python -c "from transformers import AutoProcessor, AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('google/functiongemma-270m-it')"
```

**Corrupted Model**:
```bash
# Remove cached model
rm -rf ~/.cache/huggingface/hub/models--google--functiongemma-270m-it

# Re-download
python -c "from transformers import AutoProcessor, AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('google/functiongemma-270m-it')"
```

---

### 2. Function Not Found

#### Symptoms
```
Error: Function 'create_folder' not found in registry
KeyError: 'create_folder'
```

#### Solutions

**Verify Function Registration**:
```python
from function_registry import FunctionRegistry

registry = FunctionRegistry()
print("Registered functions:", registry.get_all_function_names())
```

**Check Function Name**:
- Verify spelling (case-sensitive)
- Check for typos
- Use exact name from schema

**Re-register Function**:
```python
from functions.folder_operations import create_folder
from function_schemas import CREATE_FOLDER_SCHEMA

registry.register_function(
    name="create_folder",
    implementation=create_folder,
    schema=CREATE_FOLDER_SCHEMA,
    category="folder_operations"
)
```

---

### 3. Invalid Parameters

#### Symptoms
```
Error: Invalid parameter 'path': expected string, got int
TypeError: argument must be str, not int
ValidationError: Parameter validation failed
```

#### Solutions

**Check Parameter Types**:
```python
# Wrong
result = create_folder(123)

# Correct
result = create_folder("C:/test_folder")
```

**Verify Required Parameters**:
```python
# Check schema for required parameters
from function_schemas import CREATE_FOLDER_SCHEMA
print(CREATE_FOLDER_SCHEMA["function"]["parameters"]["required"])
```

**Path Formatting**:
```python
# Use forward slashes or double backslashes
path = "C:/Users/John/Documents"  # Good
path = "C:\\Users\\John\\Documents"  # Good
path = "C:\Users\John\Documents"  # Bad (escape sequences)
```

---

### 4. Permission Denied

#### Symptoms
```
Error: Permission denied: cannot delete file
PermissionError: [WinError 5] Access is denied
```

#### Solutions

**Run as Administrator**:
- Right-click Python script
- Select "Run as administrator"

**Check File Locks**:
- Close applications using the file
- Check Task Manager for processes
- Use `handle.exe` to find locks (Sysinternals)

**Verify Permissions**:
- Right-click file/folder → Properties → Security
- Ensure your user has write permissions
- Check if file is read-only

**Alternative Approach**:
```python
import os
import stat

# Remove read-only attribute
os.chmod(path, stat.S_IWRITE)

# Then delete
os.remove(path)
```

---

### 5. Window Not Found

#### Symptoms
```
Error: Window not found: Chrome
Error: Window not found: notepad
```

#### Solutions

**Verify Window is Open**:
- Check window is visible (not minimized to tray)
- Ensure window is not on another virtual desktop

**Get Exact Window Title**:
```python
from functions.window_management import get_active_window

# Click on the window you want
import time
time.sleep(3)  # Time to click the window

result = get_active_window()
print(f"Window title: {result['title']}")
```

**Try Process Name**:
```python
# Instead of window title
activate_window("chrome.exe")  # Process name
activate_window("Google Chrome")  # Window title
```

**Check Window Manager**:
```python
from local_client.window_manager import WindowManager

wm = WindowManager()
windows = wm.get_all_windows()
for hwnd, title in windows:
    print(f"HWND: {hwnd}, Title: {title}")
```

---

### 6. Parsing Errors

#### Symptoms
```
Error: Failed to parse function call
Error: Invalid function call format
```

#### Solutions

**Check Model Output**:
```python
from functiongemma_service import FunctionGemmaPlannerService

service = FunctionGemmaPlannerService(
    model_path="google/functiongemma-270m-it",
    function_registry=registry
)

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

result = service.generate_function_calls("create a folder")
```

**Verify Parser**:
```python
from function_parser import extract_function_calls

# Test with known good format
text = "<start_function_call>call:create_folder{path:<escape>C:/test<escape>}<end_function_call>"
calls = extract_function_calls(text)
print(calls)
```

**Check for Escape Tags**:
- String values should be wrapped in `<escape>` tags
- Model should generate: `{path:<escape>value<escape>}`
- Not: `{path:value}`

---

### 7. Slow Performance

#### Symptoms
- Model takes 10+ seconds to load
- Commands take 5+ seconds to execute
- System becomes unresponsive

#### Solutions

**Model Loading**:
```python
# Load model once at startup, not per command
service = FunctionGemmaPlannerService(
    model_path="google/functiongemma-270m-it",
    function_registry=registry
)

# Reuse service for all commands
result1 = service.execute_multi_step_task("command 1")
result2 = service.execute_multi_step_task("command 2")
```

**Reduce Delays**:
```python
# Keyboard operations
type_text("hello", interval=0.01)  # Faster typing

# Mouse operations
move_mouse(100, 100, duration=0.1)  # Faster movement
```

**Check System Resources**:
- Close unnecessary applications
- Check CPU usage (Task Manager)
- Check RAM usage (should have 2GB+ free)
- Check disk I/O (SSD recommended)

**Profile Slow Functions**:
```python
import time

start = time.time()
result = my_function()
end = time.time()

print(f"Execution time: {end - start:.2f}s")
```

---

### 8. Import Errors

#### Symptoms
```
ModuleNotFoundError: No module named 'functions'
ImportError: cannot import name 'create_folder'
```

#### Solutions

**Check Working Directory**:
```bash
cd backend
python your_script.py
```

**Verify Module Structure**:
```bash
backend/
├── functions/
│   ├── __init__.py  # Must exist!
│   ├── folder_operations.py
│   └── ...
```

**Add to Python Path**:
```python
import sys
sys.path.append('path/to/backend')

from functions.folder_operations import create_folder
```

**Use Absolute Imports**:
```python
# Instead of relative imports
from functions.folder_operations import create_folder

# Not
from .functions.folder_operations import create_folder
```

---

### 9. Test Failures

#### Symptoms
```
FAILED test_create_folder_basic
AssertionError: assert False == True
```

#### Solutions

**Run Single Test**:
```bash
pytest backend/test_folder_operations.py::test_create_folder_basic -v
```

**Enable Debug Output**:
```bash
pytest backend/test_folder_operations.py -v -s
```

**Check Test Isolation**:
```python
# Clean up after tests
import tempfile
import shutil

def test_my_function():
    tmpdir = tempfile.mkdtemp()
    try:
        # Test code
        result = my_function(tmpdir)
        assert result["success"] == True
    finally:
        # Always clean up
        shutil.rmtree(tmpdir, ignore_errors=True)
```

**Verify Test Data**:
```python
# Print intermediate values
def test_my_function():
    result = my_function("test")
    print(f"Result: {result}")  # Debug output
    assert result["success"] == True
```

---

### 10. Coordinate Out of Bounds

#### Symptoms
```
Error: Coordinates out of bounds: (2000, 1500)
Error: Mouse position outside screen
```

#### Solutions

**Check Screen Size**:
```python
import pyautogui

width, height = pyautogui.size()
print(f"Screen size: {width}x{height}")
```

**Validate Coordinates**:
```python
def click(x: int, y: int) -> dict:
    screen_width, screen_height = pyautogui.size()
    
    if not (0 <= x < screen_width and 0 <= y < screen_height):
        return {
            "success": False,
            "message": f"Coordinates out of bounds: ({x}, {y}). Screen size: {screen_width}x{screen_height}"
        }
    
    pyautogui.click(x, y)
    return {"success": True, "message": f"Clicked at ({x}, {y})"}
```

**Use Relative Coordinates**:
```python
# Center of screen
screen_width, screen_height = pyautogui.size()
center_x = screen_width // 2
center_y = screen_height // 2

click(center_x, center_y)
```

---

## Advanced Troubleshooting

### Enable Debug Logging

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# Now run your code
service = FunctionGemmaPlannerService(...)
result = service.execute_multi_step_task("command")
```

### Check Execution Logs

```bash
# View recent execution logs
ls -lt debug_logs/

# View specific log
cat debug_logs/2025-12-27_20-20-56/execution_log.txt
```

### Verify Function Registry State

```python
from function_registry import FunctionRegistry

registry = FunctionRegistry()

# List all functions
print("Functions:", registry.get_all_function_names())

# List by category
print("Categories:", registry.get_categories())

# Get specific function
func = registry.get_function("create_folder")
print("Function:", func)

# Get all schemas
schemas = registry.get_all_schemas()
print(f"Total schemas: {len(schemas)}")
```

### Test Individual Components

**Test Parser**:
```python
from function_parser import extract_function_calls, cast_argument_value

# Test parsing
text = "<start_function_call>call:test{arg1:<escape>value<escape>,arg2:123}<end_function_call>"
calls = extract_function_calls(text)
print("Parsed calls:", calls)

# Test type casting
print(cast_argument_value("123"))  # int
print(cast_argument_value("123.45"))  # float
print(cast_argument_value("true"))  # bool
print(cast_argument_value("hello"))  # str
```

**Test Executor**:
```python
from function_executor import FunctionExecutor
from function_registry import FunctionRegistry

registry = FunctionRegistry()
executor = FunctionExecutor(registry)

# Test single function
from dataclasses import dataclass

@dataclass
class FunctionCall:
    name: str
    arguments: dict

call = FunctionCall(name="create_folder", arguments={"path": "C:/test"})
result = executor.execute_function_call(call)
print("Result:", result)
```

### Memory Profiling

```python
import tracemalloc

# Start tracing
tracemalloc.start()

# Your code
service = FunctionGemmaPlannerService(...)
result = service.execute_multi_step_task("command")

# Get memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024 / 1024:.2f} MB")
print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")

tracemalloc.stop()
```

### Network Monitoring

Verify no external API calls are made:

```python
import socket

# Block all network access (for testing)
def guard(*args, **kwargs):
    raise Exception("Network access blocked!")

socket.socket = guard

# Now run your code - should work without network
service = FunctionGemmaPlannerService(...)
result = service.execute_multi_step_task("command")
```

---

## Error Messages Reference

### Model Loading Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: transformers` | Missing package | `pip install transformers` |
| `RuntimeError: Insufficient memory` | Not enough RAM | Close apps, upgrade RAM |
| `FileNotFoundError: model.safetensors` | Model not downloaded | Download model manually |
| `OSError: Can't load tokenizer` | Corrupted cache | Clear cache, re-download |

### Function Execution Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `KeyError: 'function_name'` | Function not registered | Register function |
| `TypeError: expected str, got int` | Wrong parameter type | Check parameter types |
| `PermissionError: Access denied` | Insufficient permissions | Run as admin |
| `FileNotFoundError: path` | File doesn't exist | Check path exists |

### Parsing Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ValueError: Invalid function call` | Malformed output | Check model output |
| `KeyError: 'name'` | Missing function name | Verify parsing regex |
| `TypeError: unhashable type` | Invalid argument type | Check type casting |

---

## Getting Help

### Before Asking for Help

1. Check this troubleshooting guide
2. Review error message carefully
3. Enable debug logging
4. Try to reproduce with minimal example
5. Check if issue is already reported

### When Reporting Issues

Include:
1. **Error message** (full stack trace)
2. **Code** (minimal reproducible example)
3. **Environment**:
   - OS and version
   - Python version
   - Package versions (`pip list`)
   - RAM available
4. **Steps to reproduce**
5. **Expected vs actual behavior**
6. **Logs** (if available)

### Where to Get Help

- **Documentation**: Check `USER_GUIDE.md` and `DEVELOPER_GUIDE.md`
- **Examples**: See `demo_functiongemma_service.py` and `extensibility_example.py`
- **Tests**: Look at `test_*.py` files for usage examples
- **Issues**: Report bugs with reproduction steps

---

## Prevention Tips

### Best Practices

1. **Always validate inputs** before operations
2. **Use try-except** for all external operations
3. **Provide clear error messages** with context
4. **Log important operations** for debugging
5. **Test thoroughly** before deploying

### Code Review Checklist

- [ ] Error handling for all operations
- [ ] Input validation before execution
- [ ] Clear error messages with context
- [ ] Logging for debugging
- [ ] Tests for happy path and error cases
- [ ] Documentation updated

### Testing Checklist

- [ ] Unit tests pass
- [ ] Property tests pass (if applicable)
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Edge cases covered
- [ ] Error cases covered

---

## Quick Reference

### Useful Commands

```bash
# Run all tests
pytest backend/test_*.py -v

# Run specific test file
pytest backend/test_folder_operations.py -v

# Run with coverage
pytest backend/test_*.py --cov=backend --cov-report=html

# Run with debug output
pytest backend/test_*.py -v -s

# Check Python packages
pip list | grep -E "transformers|torch|hypothesis|pytest"

# Check model cache
ls ~/.cache/huggingface/hub/
```

### Useful Code Snippets

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check function registry
from function_registry import FunctionRegistry
registry = FunctionRegistry()
print(registry.get_all_function_names())

# Test parser
from function_parser import extract_function_calls
calls = extract_function_calls(text)

# Get screen size
import pyautogui
print(pyautogui.size())

# Get active window
from functions.window_management import get_active_window
print(get_active_window())
```

---

## Still Having Issues?

If you've tried everything in this guide and still have issues:

1. Create a minimal reproducible example
2. Gather all relevant information (error, logs, environment)
3. Report the issue with details
4. Be patient and provide additional information if requested

We're here to help!
