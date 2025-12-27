# JARVIS FunctionGemma - Extensibility Guide

## Quick Start: Adding a New Function

This guide shows you how to add new functions to JARVIS in 5 simple steps.

---

## Step 1: Implement the Function

Create your function in the appropriate module under `backend/functions/`:

```python
# backend/functions/file_operations.py

def search_files(directory: str, pattern: str) -> dict:
    """
    Search for files matching a pattern in a directory.
    
    Args:
        directory: Directory to search in
        pattern: File pattern to match (e.g., "*.txt")
        
    Returns:
        {"success": bool, "files": List[str], "message": str}
    """
    import glob
    import os
    
    try:
        # Validate directory exists
        if not os.path.exists(directory):
            return {
                "success": False,
                "files": [],
                "message": f"Directory not found: {directory}"
            }
        
        # Search for files
        search_path = os.path.join(directory, pattern)
        files = glob.glob(search_path)
        
        return {
            "success": True,
            "files": files,
            "message": f"Found {len(files)} files matching '{pattern}'"
        }
        
    except Exception as e:
        return {
            "success": False,
            "files": [],
            "message": f"Error searching files: {str(e)}"
        }
```

**Key Requirements**:
- Return a dict with `success` (bool) and `message` (str)
- Include any additional data in the dict (e.g., `files`)
- Handle all errors with try-except
- Provide clear error messages

---

## Step 2: Define the Schema

Add the function schema to `backend/function_schemas.py`:

```python
# backend/function_schemas.py

SEARCH_FILES_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_files",
        "description": "Search for files matching a pattern in a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory to search in (full path)"
                },
                "pattern": {
                    "type": "string",
                    "description": "File pattern to match (e.g., '*.txt', 'report*.pdf')"
                }
            },
            "required": ["directory", "pattern"]
        }
    }
}

# Add to the appropriate category list
FILE_OPERATIONS_SCHEMAS = [
    # ... existing schemas ...
    SEARCH_FILES_SCHEMA
]
```

**Schema Guidelines**:
- Use clear, descriptive names
- Provide detailed descriptions
- Mark required parameters
- Include example values in descriptions
- Supported types: string, integer, number, boolean

---

## Step 3: Register the Function

Register your function with the registry:

```python
# In your initialization code or backend/function_registry.py

from functions.file_operations import search_files
from function_schemas import SEARCH_FILES_SCHEMA

registry = FunctionRegistry()
registry.register_function(
    name="search_files",
    implementation=search_files,
    schema=SEARCH_FILES_SCHEMA,
    category="file_operations"
)
```

**Categories**:
- `folder_operations`: Folder management
- `file_operations`: File management
- `keyboard_operations`: Keyboard input
- `mouse_operations`: Mouse control
- `window_management`: Window control

---

## Step 4: Write Tests

Create tests in `backend/test_<module>.py`:

```python
# backend/test_file_operations.py

import pytest
import tempfile
import os

def test_search_files_basic():
    """Test basic file search functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_files = ["test1.txt", "test2.txt", "other.pdf"]
        for filename in test_files:
            open(os.path.join(tmpdir, filename), 'w').close()
        
        # Search for .txt files
        result = search_files(tmpdir, "*.txt")
        
        assert result["success"] == True
        assert len(result["files"]) == 2
        assert all(f.endswith(".txt") for f in result["files"])

def test_search_files_nonexistent_directory():
    """Test search in non-existent directory."""
    result = search_files("/nonexistent/path", "*.txt")
    
    assert result["success"] == False
    assert "not found" in result["message"].lower()

def test_search_files_no_matches():
    """Test search with no matching files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = search_files(tmpdir, "*.nonexistent")
        
        assert result["success"] == True
        assert len(result["files"]) == 0
```

**Test Requirements**:
- Test basic functionality (happy path)
- Test error cases (invalid inputs)
- Test edge cases (empty results, boundary conditions)
- Use pytest framework

---

## Step 5: Update Documentation

Add your function to `backend/USER_GUIDE.md`:

```markdown
#### File Operations

- `search_files(directory, pattern)` - Search for files matching a pattern
```

---

## Complete Example

Here's a complete example of adding a `get_file_size` function:

### 1. Implementation

```python
# backend/functions/file_operations.py

def get_file_size(path: str) -> dict:
    """
    Get the size of a file in bytes.
    
    Args:
        path: Path to file
        
    Returns:
        {"success": bool, "size": int, "size_mb": float, "message": str}
    """
    import os
    
    try:
        if not os.path.exists(path):
            return {
                "success": False,
                "size": 0,
                "size_mb": 0.0,
                "message": f"File not found: {path}"
            }
        
        if not os.path.isfile(path):
            return {
                "success": False,
                "size": 0,
                "size_mb": 0.0,
                "message": f"Path is not a file: {path}"
            }
        
        size_bytes = os.path.getsize(path)
        size_mb = size_bytes / (1024 * 1024)
        
        return {
            "success": True,
            "size": size_bytes,
            "size_mb": round(size_mb, 2),
            "message": f"File size: {size_bytes} bytes ({size_mb:.2f} MB)"
        }
        
    except Exception as e:
        return {
            "success": False,
            "size": 0,
            "size_mb": 0.0,
            "message": f"Error getting file size: {str(e)}"
        }
```

### 2. Schema

```python
# backend/function_schemas.py

GET_FILE_SIZE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_file_size",
        "description": "Get the size of a file in bytes and megabytes",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Full path to the file (e.g., 'C:/Users/John/Documents/report.pdf')"
                }
            },
            "required": ["path"]
        }
    }
}

FILE_OPERATIONS_SCHEMAS = [
    # ... existing schemas ...
    GET_FILE_SIZE_SCHEMA
]
```

### 3. Registration

```python
# In initialization code

from functions.file_operations import get_file_size
from function_schemas import GET_FILE_SIZE_SCHEMA

registry.register_function(
    name="get_file_size",
    implementation=get_file_size,
    schema=GET_FILE_SIZE_SCHEMA,
    category="file_operations"
)
```

### 4. Tests

```python
# backend/test_file_operations.py

def test_get_file_size_basic():
    """Test getting file size."""
    import tempfile
    
    with tempfile.NamedTemporaryFile(delete=False) as f:
        # Write 1KB of data
        f.write(b'x' * 1024)
        f.flush()
        
        result = get_file_size(f.name)
        
        assert result["success"] == True
        assert result["size"] == 1024
        assert result["size_mb"] > 0
        
        os.unlink(f.name)

def test_get_file_size_nonexistent():
    """Test getting size of non-existent file."""
    result = get_file_size("/nonexistent/file.txt")
    
    assert result["success"] == False
    assert "not found" in result["message"].lower()
```

### 5. Documentation

```markdown
<!-- backend/USER_GUIDE.md -->

#### File Operations

- `get_file_size(path)` - Get the size of a file in bytes and megabytes
```

---

## Advanced Topics

### Reusing Existing Code

Leverage existing components for common tasks:

```python
# Reuse PathResolver for fuzzy path matching
from local_client.path_resolver import PathResolver

def my_function(path: str) -> dict:
    path_resolver = PathResolver()
    resolved_path = path_resolver.resolve(path)
    
    if not resolved_path:
        return {"success": False, "message": f"Path not found: {path}"}
    
    # Use resolved_path...
```

**Available Components**:
- `PathResolver`: Fuzzy path matching
- `FilenameResolver`: Fuzzy filename matching
- `WindowManager`: Window detection and activation
- `DirectPathExecutor`: File dialog automation
- `PlanExecutor`: Keyboard/mouse timing and logic

### Adding a New Category

To add a new category of functions:

1. Create a new module: `backend/functions/new_category.py`
2. Create a schema list: `NEW_CATEGORY_SCHEMAS` in `function_schemas.py`
3. Register functions with `category="new_category"`
4. Update documentation with new category

Example:

```python
# backend/functions/network_operations.py

def download_file(url: str, destination: str) -> dict:
    """Download a file from a URL."""
    import requests
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(destination, 'wb') as f:
            f.write(response.content)
        
        return {
            "success": True,
            "message": f"Downloaded {url} to {destination}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error downloading file: {str(e)}"
        }
```

### Placeholder Functions

Mark functions as placeholders if not yet implemented:

```python
registry.register_function(
    name="future_function",
    implementation=lambda **kwargs: {
        "success": False,
        "message": "This function is not yet implemented"
    },
    schema=FUTURE_FUNCTION_SCHEMA,
    category="file_operations",
    is_placeholder=True
)
```

### Property-Based Testing

For complex functions, add property tests:

```python
from hypothesis import given, strategies as st

@given(
    directory=st.text(min_size=1),
    pattern=st.text(min_size=1)
)
@pytest.mark.property_test
def test_property_search_files_returns_dict(directory, pattern):
    """Property: search_files always returns a dict with required keys."""
    result = search_files(directory, pattern)
    
    assert isinstance(result, dict)
    assert "success" in result
    assert "message" in result
    assert "files" in result
```

---

## Checklist

Use this checklist when adding a new function:

- [ ] Function implemented with proper error handling
- [ ] Function returns dict with `success` and `message`
- [ ] Function schema created in `function_schemas.py`
- [ ] Function registered in `FunctionRegistry`
- [ ] Unit tests for basic functionality
- [ ] Unit tests for error cases
- [ ] Unit tests for edge cases
- [ ] Property tests (if applicable)
- [ ] Documentation updated in `USER_GUIDE.md`
- [ ] All tests pass: `pytest test_*.py -v`

---

## Common Patterns

### Pattern 1: File/Folder Validation

```python
import os

def my_function(path: str) -> dict:
    if not os.path.exists(path):
        return {"success": False, "message": f"Path not found: {path}"}
    
    if not os.path.isfile(path):  # or os.path.isdir(path)
        return {"success": False, "message": f"Path is not a file: {path}"}
    
    # Continue with operation...
```

### Pattern 2: Try-Except with Specific Errors

```python
def my_function(path: str) -> dict:
    try:
        # Operation
        return {"success": True, "message": "Success"}
    except PermissionError:
        return {"success": False, "message": f"Permission denied: {path}"}
    except FileNotFoundError:
        return {"success": False, "message": f"File not found: {path}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
```

### Pattern 3: Coordinate Validation

```python
import pyautogui

def my_mouse_function(x: int, y: int) -> dict:
    screen_width, screen_height = pyautogui.size()
    
    if not (0 <= x < screen_width and 0 <= y < screen_height):
        return {
            "success": False,
            "message": f"Coordinates out of bounds: ({x}, {y})"
        }
    
    # Continue with operation...
```

### Pattern 4: Window Validation

```python
from local_client.window_manager import WindowManager

def my_window_function(identifier: str) -> dict:
    window_manager = WindowManager()
    hwnd = window_manager.find_window_for_app(identifier)
    
    if not hwnd:
        return {"success": False, "message": f"Window not found: {identifier}"}
    
    # Continue with operation...
```

---

## Troubleshooting

### Function Not Being Called

**Problem**: Model doesn't generate calls to your function

**Solutions**:
1. Check function is registered: `registry.get_all_function_names()`
2. Verify schema is valid: `registry.validate_schema(schema)`
3. Improve function description (be more specific)
4. Add example values in parameter descriptions
5. Test with explicit command mentioning function name

### Schema Validation Fails

**Problem**: Schema rejected during registration

**Solutions**:
1. Check required fields: `type`, `function`, `name`, `description`, `parameters`
2. Verify parameters have `type: "object"` and `properties`
3. Ensure parameter types are valid: string, integer, number, boolean
4. Check for typos in field names

### Tests Failing

**Problem**: Tests don't pass

**Solutions**:
1. Check function returns correct format
2. Verify error handling covers all cases
3. Use temporary directories for file operations
4. Clean up resources after tests
5. Run tests individually to isolate issues: `pytest test_file.py::test_name -v`

---

## Examples from Codebase

See these files for complete examples:

- **Folder Operations**: `backend/functions/folder_operations.py`
- **File Operations**: `backend/functions/file_operations.py`
- **Keyboard Operations**: `backend/functions/keyboard_operations.py`
- **Mouse Operations**: `backend/functions/mouse_operations.py`
- **Window Management**: `backend/functions/window_management.py`

- **Schemas**: `backend/function_schemas.py`
- **Tests**: `backend/test_*.py`
- **Demo**: `backend/extensibility_example.py`

---

## Getting Help

- **Questions**: Check `DEVELOPER_GUIDE.md` for detailed information
- **Issues**: Report bugs with reproduction steps
- **Suggestions**: Propose new functions with use cases

Happy extending!
