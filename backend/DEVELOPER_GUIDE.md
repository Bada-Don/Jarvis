# JARVIS FunctionGemma Integration - Developer Guide

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Design Decisions](#design-decisions)
4. [Adding New Functions](#adding-new-functions)
5. [Function Schema Format](#function-schema-format)
6. [Testing Requirements](#testing-requirements)
7. [Code Examples](#code-examples)
8. [Best Practices](#best-practices)

---

## Architecture Overview

### High-Level Architecture

The FunctionGemma integration follows a modular, layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                        User Command                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              FunctionGemma Planner Service                   │
│  - Loads local FunctionGemma-270M model                     │
│  - Processes commands without external APIs                 │
│  - Generates function calls in FunctionGemma format         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Function Call Parser                        │
│  - Extracts function calls from model output                │
│  - Validates format and casts argument types                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Function Registry                          │
│  - Centralized registry of all functions                    │
│  - Schema validation and function lookup                    │
│  - Organized by category                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Function Executor                           │
│  - Executes function calls in sequence                      │
│  - Handles errors and decides continue/abort                │
│  - Reports execution results                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 System Operations                            │
│  - File system, keyboard/mouse, window management           │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Modularity**: Functions are self-contained and independently testable
2. **Reusability**: Leverage existing code (PathResolver, WindowManager, etc.)
3. **Extensibility**: Easy to add new functions without major refactoring
4. **Testability**: Both unit tests and property-based tests
5. **Backward Compatibility**: Maintain support for legacy features

---

## Core Components

### 1. FunctionGemma Planner Service

**File**: `backend/functiongemma_service.py`

**Purpose**: Manages the local FunctionGemma model and generates function calls from natural language commands.

**Key Classes**:

```python
class FunctionGemmaPlannerService:
    """Service for planning tasks using local FunctionGemma model."""
    
    def __init__(self, model_path: str, function_registry: FunctionRegistry):
        """Initialize with model path and function registry."""
        
    def load_model(self) -> bool:
        """Load the FunctionGemma model from local storage."""
        
    def generate_function_calls(self, user_command: str) -> List[FunctionCall]:
        """Generate function calls from a user command."""
        
    def execute_multi_step_task(self, user_command: str, max_turns: int = 15) -> ExecutionResult:
        """Execute a multi-step task with conversation turns."""
```

**Design Decisions**:
- Uses `AutoProcessor` (not `AutoTokenizer`) for input processing
- Includes exact system prompt: "You are a model that can do function calling with the following functions"
- Caches model in memory after first load
- Supports multi-turn conversations for complex tasks

### 2. Function Registry

**File**: `backend/function_registry.py`

**Purpose**: Centralized registry for all available functions with schema validation.

**Key Classes**:

```python
class FunctionRegistry:
    """Registry for managing functions and their schemas."""
    
    def register_function(
        self, 
        name: str, 
        implementation: Callable,
        schema: dict,
        category: str,
        is_placeholder: bool = False
    ) -> None:
        """Register a function with its schema."""
        
    def get_function(self, name: str) -> Optional[Callable]:
        """Get a function by name."""
        
    def get_all_schemas(self) -> List[dict]:
        """Get all function schemas for the model."""
        
    def validate_parameters(self, name: str, parameters: dict) -> Tuple[bool, Optional[str]]:
        """Validate function parameters against schema."""
```

**Design Decisions**:
- Functions organized into 5 categories (folder, file, keyboard, mouse, window)
- JSON schema validation on registration
- Support for placeholder functions (not yet implemented)
- Automatic schema generation for the model

### 3. Function Call Parser

**File**: `backend/function_parser.py`

**Purpose**: Parse function calls from FunctionGemma output format.

**Key Functions**:

```python
def extract_function_calls(text: str) -> List[dict]:
    """
    Extract function calls from FunctionGemma output.
    
    Format: <start_function_call>call:function_name{arg1:<escape>value<escape>,arg2:123}<end_function_call>
    """
    
def cast_argument_value(value: str) -> Union[int, float, bool, str]:
    """Cast argument value to appropriate type (int, float, bool, str)."""
```

**Design Decisions**:
- Uses official FunctionGemma parsing regex
- Handles `<escape>` tags for string values
- Automatic type casting for numeric and boolean values
- Strips whitespace from all values

### 4. Function Executor

**File**: `backend/function_executor.py`

**Purpose**: Execute function calls with error handling and result reporting.

**Key Classes**:

```python
class FunctionExecutor:
    """Executor for function calls."""
    
    def execute_function_call(self, function_call: FunctionCall) -> ExecutionResult:
        """Execute a single function call."""
        
    def execute_sequence(self, function_calls: List[FunctionCall]) -> MultiStepExecutionResult:
        """Execute a sequence of function calls."""
```

**Design Decisions**:
- Executes functions in order specified by model
- Error severity-based continue/abort logic
- Support for parallel execution of independent operations
- Comprehensive result reporting

### 5. Function Implementations

Functions are organized into separate modules by category:

**Folder Operations** (`backend/functions/folder_operations.py`):
- `create_folder`, `delete_folder`, `open_folder`, `list_folder`
- Reuses: `PathResolver`, `PathConfig`

**File Operations** (`backend/functions/file_operations.py`):
- `delete_file`, `rename_file`, `copy_file`, `move_file`, `open_file`
- Reuses: `DirectPathExecutor`, `FilenameResolver`, `PathResolver`

**Keyboard Operations** (`backend/functions/keyboard_operations.py`):
- `type_text`, `press_key`, `press_hotkey`, `press_key_repeat`
- Reuses: Keyboard handling logic from `PlanExecutor`

**Mouse Operations** (`backend/functions/mouse_operations.py`):
- `click`, `double_click`, `right_click`, `move_mouse`, `drag`
- Reuses: Patterns from `mouse_controller.py`

**Window Management** (`backend/functions/window_management.py`):
- `activate_window`, `close_window`, `minimize_window`, `maximize_window`, `get_active_window`
- Reuses: `WindowManager` class

---

## Design Decisions

### Why FunctionGemma?

**Rationale**: FunctionGemma is specifically designed for function calling, making it ideal for converting natural language to structured function calls.

**Alternatives Considered**:
- Gemini API: Requires external API, costs money, network dependency
- GPT-4: Same issues as Gemini
- Custom model: Would require significant training data and resources

**Trade-offs**:
- Smaller model (270M) means faster inference but potentially lower accuracy
- Local operation means no API costs but requires local resources
- Specialized model means better at function calling but limited to that task

### Why Command-Line Operations?

**Rationale**: Command-line operations (os, shutil) are more reliable and faster than UI automation.

**Benefits**:
- Deterministic behavior
- No visual detection overhead
- Better error messages
- Easier to test

**When to Use UI Automation**:
- File types that can't be created via command-line (.psd, .fs, .ai)
- Complex UI interactions (FlexiSIGN operations)
- Visual targets that change dynamically

### Why Separate Function Modules?

**Rationale**: Organizing functions by category improves maintainability and testability.

**Benefits**:
- Clear separation of concerns
- Easy to find and modify functions
- Independent testing of each module
- Logical organization for users

**Structure**:
```
backend/functions/
├── __init__.py
├── folder_operations.py
├── file_operations.py
├── keyboard_operations.py
├── mouse_operations.py
└── window_management.py
```

### Why Reuse Existing Code?

**Rationale**: Existing code is tested and proven to work in production.

**Benefits**:
- Reduced development time
- Fewer bugs (code already tested)
- Consistent behavior across features
- Easier maintenance

**Reused Components**:
- `PathResolver`: Fuzzy path matching
- `FilenameResolver`: Fuzzy filename matching
- `WindowManager`: Window detection and activation
- `DirectPathExecutor`: File dialog automation
- `PlanExecutor`: Keyboard/mouse timing and logic

---

## Adding New Functions

### Step-by-Step Guide

#### Step 1: Define the Function

Create your function in the appropriate module (or create a new module for a new category).

**Example**: Adding a `search_files` function to file operations

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

#### Step 2: Create the Function Schema

Add the schema to `backend/function_schemas.py`:

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

# Add to FILE_OPERATIONS_SCHEMAS list
FILE_OPERATIONS_SCHEMAS = [
    # ... existing schemas ...
    SEARCH_FILES_SCHEMA
]
```

#### Step 3: Register the Function

Register the function in the registry initialization:

```python
# backend/function_registry.py or your initialization code

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

#### Step 4: Write Tests

Create unit tests and property tests:

```python
# backend/test_file_operations.py

def test_search_files_basic():
    """Test basic file search functionality."""
    # Create test directory with files
    import tempfile
    import os
    
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
```

#### Step 5: Update Documentation

Add your function to the user guide and update the function list:

```markdown
<!-- backend/USER_GUIDE.md -->

#### File Operations

- `search_files(directory, pattern)` - Search for files matching a pattern
```

### Quick Reference Checklist

- [ ] Function implementation with proper error handling
- [ ] Function returns dict with `success`, `message`, and relevant data
- [ ] Function schema in `function_schemas.py`
- [ ] Function registered in `FunctionRegistry`
- [ ] Unit tests for basic functionality
- [ ] Unit tests for error cases
- [ ] Property tests (if applicable)
- [ ] Documentation updated

---

## Function Schema Format

### Schema Structure

Function schemas follow the FunctionGemma format:

```python
{
    "type": "function",
    "function": {
        "name": "function_name",
        "description": "Clear description of what the function does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string|integer|boolean|number",
                    "description": "Description of parameter"
                },
                "param2": {
                    "type": "string",
                    "description": "Another parameter",
                    "enum": ["option1", "option2"]  # Optional: for enums
                }
            },
            "required": ["param1"]  # List of required parameters
        }
    }
}
```

### Supported Parameter Types

**string**: Text values
```python
"path": {
    "type": "string",
    "description": "File path"
}
```

**integer**: Whole numbers
```python
"count": {
    "type": "integer",
    "description": "Number of repetitions"
}
```

**number**: Floating-point numbers
```python
"duration": {
    "type": "number",
    "description": "Duration in seconds"
}
```

**boolean**: True/false values
```python
"confirm": {
    "type": "boolean",
    "description": "Whether to confirm action"
}
```

**enum**: Limited set of options
```python
"mode": {
    "type": "string",
    "enum": ["read", "write", "append"],
    "description": "File access mode"
}
```

### Schema Best Practices

1. **Clear Descriptions**: Be specific about what the function does and what each parameter means
2. **Required Parameters**: Mark parameters as required if they're essential
3. **Default Values**: Document default values in the description
4. **Validation**: Include constraints in the description (e.g., "must be positive")
5. **Examples**: Provide example values in the description

**Good Schema Example**:

```python
CREATE_FOLDER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "create_folder",
        "description": "Create a new folder at the specified path. Creates parent directories if they don't exist.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Full path to the folder to create (e.g., 'C:/Users/John/Documents/NewFolder')"
                }
            },
            "required": ["path"]
        }
    }
}
```

### Schema Validation

The `FunctionRegistry` validates schemas on registration:

```python
def _validate_schema(self, schema: dict) -> Tuple[bool, Optional[str]]:
    """Validate a function schema."""
    # Check required top-level fields
    if "type" not in schema or schema["type"] != "function":
        return False, "Schema must have type='function'"
    
    if "function" not in schema:
        return False, "Schema must have 'function' field"
    
    func = schema["function"]
    
    # Check required function fields
    if "name" not in func:
        return False, "Function must have 'name' field"
    
    if "description" not in func:
        return False, "Function must have 'description' field"
    
    if "parameters" not in func:
        return False, "Function must have 'parameters' field"
    
    # Validate parameters structure
    params = func["parameters"]
    if "type" not in params or params["type"] != "object":
        return False, "Parameters must have type='object'"
    
    if "properties" not in params:
        return False, "Parameters must have 'properties' field"
    
    return True, None
```

---

## Testing Requirements

### Dual Testing Approach

The system uses both unit tests and property-based tests:

**Unit Tests**: Specific examples and edge cases
**Property Tests**: Universal properties across all inputs

### Unit Testing

**Framework**: pytest

**Test Structure**:

```python
# backend/test_<module>.py

import pytest
from functions.<module> import <function>

def test_<function>_basic():
    """Test basic functionality."""
    result = <function>(valid_params)
    assert result["success"] == True

def test_<function>_error_case():
    """Test error handling."""
    result = <function>(invalid_params)
    assert result["success"] == False
    assert "error" in result["message"].lower()

def test_<function>_edge_case():
    """Test edge case."""
    result = <function>(edge_case_params)
    # Assert expected behavior
```

**Running Unit Tests**:

```bash
cd backend
pytest test_<module>.py -v
```

### Property-Based Testing

**Framework**: hypothesis

**Test Structure**:

```python
from hypothesis import given, strategies as st
import pytest

@given(
    path=st.text(min_size=1, max_size=100),
    pattern=st.text(min_size=1, max_size=50)
)
@pytest.mark.property_test
@pytest.mark.tag("Feature: functiongemma-integration, Property X: <property_name>")
def test_property_<property_name>(path, pattern):
    """
    Property X: For any <condition>, <expected_behavior>.
    """
    # Test the property
    result = search_files(path, pattern)
    
    # Assert property holds
    assert isinstance(result, dict)
    assert "success" in result
    assert "message" in result
```

**Running Property Tests**:

```bash
cd backend
pytest -m property_test -v
```

### Test Coverage Requirements

- **Line Coverage**: Minimum 80%
- **Branch Coverage**: Minimum 75%
- **All Functions**: Must have unit tests
- **All Properties**: Must have property tests

**Measuring Coverage**:

```bash
cd backend
pytest --cov=. --cov-report=html
```

### Integration Testing

Integration tests verify end-to-end workflows:

```python
def test_integration_multi_step_task():
    """Test complete multi-step task execution."""
    service = FunctionGemmaPlannerService(
        model_path="google/functiongemma-270m-it",
        function_registry=registry
    )
    
    result = service.execute_multi_step_task(
        "create a folder called test, create a file called test.txt in it"
    )
    
    assert result.overall_success == True
    assert result.successful_steps >= 2
```

---

## Code Examples

### Example 1: Simple Function

```python
# backend/functions/folder_operations.py

def list_folder(path: str) -> dict:
    """
    List contents of a folder.
    
    Args:
        path: Path to folder
        
    Returns:
        {"success": bool, "contents": List[str], "message": str}
    """
    import os
    
    try:
        if not os.path.exists(path):
            return {
                "success": False,
                "contents": [],
                "message": f"Folder not found: {path}"
            }
        
        if not os.path.isdir(path):
            return {
                "success": False,
                "contents": [],
                "message": f"Path is not a folder: {path}"
            }
        
        contents = os.listdir(path)
        
        return {
            "success": True,
            "contents": contents,
            "message": f"Found {len(contents)} items in {path}"
        }
        
    except PermissionError:
        return {
            "success": False,
            "contents": [],
            "message": f"Permission denied: {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "contents": [],
            "message": f"Error listing folder: {str(e)}"
        }
```

### Example 2: Function with Reused Code

```python
# backend/functions/file_operations.py

from local_client.path_resolver import PathResolver
from local_client.filename_resolver import FilenameResolver

def open_file(path: str) -> dict:
    """
    Open a file with its default application.
    
    Args:
        path: Fuzzy path to file
        
    Returns:
        {"success": bool, "message": str}
    """
    import os
    
    try:
        # Reuse PathResolver for fuzzy path matching
        path_resolver = PathResolver()
        resolved_path = path_resolver.resolve(path)
        
        if not resolved_path:
            # Try FilenameResolver for filename matching
            filename_resolver = FilenameResolver()
            resolved_path = filename_resolver.resolve(path)
        
        if not resolved_path:
            return {
                "success": False,
                "message": f"File not found: {path}"
            }
        
        # Open file with default application
        os.startfile(resolved_path)
        
        return {
            "success": True,
            "message": f"Opened file: {resolved_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error opening file: {str(e)}"
        }
```

### Example 3: Function with Complex Logic

```python
# backend/functions/window_management.py

from local_client.window_manager import WindowManager
import win32gui
import win32con

def activate_window(identifier: str) -> dict:
    """
    Activate a window by title or process name.
    
    Args:
        identifier: Window title or app name
        
    Returns:
        {"success": bool, "message": str}
    """
    try:
        # Reuse WindowManager for window detection
        window_manager = WindowManager()
        
        # Try to find window
        hwnd = window_manager.find_window_for_app(identifier)
        
        if not hwnd:
            return {
                "success": False,
                "message": f"Window not found: {identifier}"
            }
        
        # Check if window is minimized
        if window_manager.is_window_minimized(hwnd):
            # Restore window first
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        # Activate window
        success = window_manager.activate_window(hwnd)
        
        if success:
            return {
                "success": True,
                "message": f"Activated window: {identifier}"
            }
        else:
            return {
                "success": False,
                "message": f"Failed to activate window: {identifier}"
            }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error activating window: {str(e)}"
        }
```

### Example 4: Using the Service

```python
# Example usage of FunctionGemma service

from functiongemma_service import FunctionGemmaPlannerService
from function_registry import FunctionRegistry

# Initialize registry and service
registry = FunctionRegistry()
service = FunctionGemmaPlannerService(
    model_path="google/functiongemma-270m-it",
    function_registry=registry
)

# Execute a simple command
result = service.execute_multi_step_task("create a folder called test")
print(f"Success: {result.overall_success}")
print(f"Message: {result.step_results[0].result['message']}")

# Execute a complex command
result = service.execute_multi_step_task(
    "open notepad, type hello world, and save as test.txt"
)
print(f"Total steps: {result.total_steps}")
print(f"Successful: {result.successful_steps}")
print(f"Failed: {result.failed_steps}")
```

---

## Best Practices

### Function Implementation

1. **Return Consistent Format**: Always return dict with `success`, `message`, and relevant data
2. **Handle All Errors**: Use try-except blocks and return error messages
3. **Validate Inputs**: Check parameters before execution
4. **Use Existing Code**: Reuse tested components where possible
5. **Add Logging**: Log important operations and errors

### Schema Design

1. **Clear Names**: Use descriptive function and parameter names
2. **Good Descriptions**: Explain what the function does and what parameters mean
3. **Mark Required**: Specify which parameters are required
4. **Document Constraints**: Include validation rules in descriptions
5. **Provide Examples**: Show example values in descriptions

### Testing

1. **Test Happy Path**: Verify function works with valid inputs
2. **Test Error Cases**: Verify error handling for invalid inputs
3. **Test Edge Cases**: Test boundary conditions and special cases
4. **Test Integration**: Verify function works with other components
5. **Use Property Tests**: Test universal properties across many inputs

### Code Organization

1. **One Function Per File Section**: Keep functions focused and small
2. **Group Related Functions**: Organize by category
3. **Reuse Common Code**: Extract shared logic into utilities
4. **Document Thoroughly**: Add docstrings and comments
5. **Follow Style Guide**: Use consistent formatting (PEP 8)

### Performance

1. **Minimize I/O**: Reduce file system and network operations
2. **Cache Results**: Store frequently accessed data
3. **Use Command-Line**: Prefer command-line over UI automation
4. **Optimize Loops**: Reduce unnecessary iterations
5. **Profile Slow Code**: Identify and optimize bottlenecks

---

## Additional Resources

### Related Documentation

- **User Guide**: `USER_GUIDE.md` - How to use the system
- **Extensibility Guide**: `EXTENSIBILITY_GUIDE.md` - Adding new functions
- **Requirements**: `.kiro/specs/functiongemma-integration/requirements.md`
- **Design**: `.kiro/specs/functiongemma-integration/design.md`
- **Tasks**: `.kiro/specs/functiongemma-integration/tasks.md`

### Code References

- **Function Registry**: `backend/function_registry.py`
- **Function Schemas**: `backend/function_schemas.py`
- **Function Parser**: `backend/function_parser.py`
- **Function Executor**: `backend/function_executor.py`
- **Planner Service**: `backend/functiongemma_service.py`

### Examples

- **Demo Service**: `backend/demo_functiongemma_service.py`
- **Extensibility Example**: `backend/extensibility_example.py`
- **Test Files**: `backend/test_*.py`

### External Resources

- **FunctionGemma**: https://huggingface.co/google/functiongemma-270m-it
- **Transformers**: https://huggingface.co/docs/transformers
- **Hypothesis**: https://hypothesis.readthedocs.io/
- **pytest**: https://docs.pytest.org/

---

## Contributing

### Development Workflow

1. **Create Feature Branch**: `git checkout -b feature/new-function`
2. **Implement Function**: Write function, schema, and tests
3. **Run Tests**: `pytest test_*.py -v`
4. **Check Coverage**: `pytest --cov=. --cov-report=html`
5. **Update Documentation**: Add to user guide and developer guide
6. **Submit PR**: Create pull request with description

### Code Review Checklist

- [ ] Function implementation follows best practices
- [ ] Function returns consistent format
- [ ] Error handling is comprehensive
- [ ] Schema is valid and well-documented
- [ ] Unit tests cover basic functionality
- [ ] Unit tests cover error cases
- [ ] Property tests verify universal properties
- [ ] Documentation is updated
- [ ] Code follows style guide
- [ ] Tests pass locally

### Getting Help

- **Questions**: Open an issue or discussion
- **Bugs**: Report with reproduction steps
- **Features**: Propose with use case and rationale
- **Documentation**: Suggest improvements or clarifications

Thank you for contributing to JARVIS!
