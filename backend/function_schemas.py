"""
Function Schemas Module

Defines JSON schemas for all FunctionGemma operations organized by category.
Each schema follows the FunctionGemma format with parameter types, descriptions,
and required fields.

Requirements: 2.1, 2.5
"""

from typing import Dict, List


# ============================================================================
# FOLDER OPERATIONS SCHEMAS
# ============================================================================

FOLDER_OPERATIONS_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "create_folder",
            "description": "Create a new folder at the specified path. Supports both full paths and fuzzy path matching.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Full or fuzzy path to the folder to create (e.g., 'C:\\Users\\Documents\\NewFolder' or 'documents/newfolder')"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_folder",
            "description": "Delete a folder with safety checks. By default, requires confirmation for non-empty folders.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Full or fuzzy path to the folder to delete"
                    },
                    "confirm_non_empty": {
                        "type": "boolean",
                        "description": "Whether to require confirmation for non-empty folders (default: true)",
                        "default": True
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_folder",
            "description": "Open a folder in Windows Explorer. Supports fuzzy path matching.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Full or fuzzy path to the folder to open (e.g., 'downloads', 'documents', 'C:\\Users\\Desktop')"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_folder",
            "description": "List the contents of a folder, returning all files and subdirectories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Full or fuzzy path to the folder to list"
                    }
                },
                "required": ["path"]
            }
        }
    }
]


# ============================================================================
# FILE OPERATIONS SCHEMAS
# ============================================================================

FILE_OPERATIONS_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Delete a file with safety checks. By default, requires confirmation before deletion.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Full or fuzzy path to the file to delete"
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Whether to require confirmation for deletion (default: true)",
                        "default": True
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rename_file",
            "description": "Rename a file in its current directory. Provide only the new filename, not a full path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "old_path": {
                        "type": "string",
                        "description": "Current file path (full or fuzzy)"
                    },
                    "new_name": {
                        "type": "string",
                        "description": "New filename only (not full path), e.g., 'newfile.txt'"
                    }
                },
                "required": ["old_path", "new_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "copy_file",
            "description": "Copy a file to a new location. Destination can be a directory or a full file path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source file path (full or fuzzy)"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination path (can be directory or full file path)"
                    }
                },
                "required": ["source", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_file",
            "description": "Move a file to a new location. Destination can be a directory or a full file path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source file path (full or fuzzy)"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination path (can be directory or full file path)"
                    }
                },
                "required": ["source", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_file",
            "description": "Open a file with its default application. Supports fuzzy path matching and filename resolution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Full or fuzzy path to the file to open (e.g., 'report.pdf', 'documents/presentation.pptx')"
                    }
                },
                "required": ["path"]
            }
        }
    }
]


# ============================================================================
# KEYBOARD OPERATIONS SCHEMAS
# ============================================================================

KEYBOARD_OPERATIONS_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type a text string using keyboard automation. Includes appropriate delays for UI responsiveness.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    },
                    "interval": {
                        "type": "number",
                        "description": "Optional delay between keystrokes in seconds (default: 0.03)",
                        "default": 0.03
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": "Press a single key. Supports special keys like 'enter', 'escape', 'tab', function keys, arrow keys, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Key name (e.g., 'enter', 'escape', 'a', 'F1', 'up', 'down', 'tab')"
                    }
                },
                "required": ["key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_hotkey",
            "description": "Execute a keyboard shortcut (hotkey combination). Must include a modifier key (ctrl, alt, shift, win).",
            "parameters": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "string",
                        "description": "Hotkey combination separated by '+' (e.g., 'ctrl+c', 'alt+tab', 'ctrl+shift+s', 'win+r')"
                    }
                },
                "required": ["keys"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_key_repeat",
            "description": "Press a key multiple times. Useful for navigation or repeated actions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Key name to press repeatedly"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of times to press the key (must be positive, max 1000)"
                    }
                },
                "required": ["key", "count"]
            }
        }
    }
]


# ============================================================================
# MOUSE OPERATIONS SCHEMAS
# ============================================================================

MOUSE_OPERATIONS_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "click",
            "description": "Click at specific screen coordinates. Coordinates must be within screen bounds.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate (horizontal position, must be within screen width)"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate (vertical position, must be within screen height)"
                    }
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "double_click",
            "description": "Double-click at specific screen coordinates. Coordinates must be within screen bounds.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate (horizontal position, must be within screen width)"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate (vertical position, must be within screen height)"
                    }
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "right_click",
            "description": "Right-click at specific screen coordinates to open context menus. Coordinates must be within screen bounds.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate (horizontal position, must be within screen width)"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate (vertical position, must be within screen height)"
                    }
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_mouse",
            "description": "Move the mouse cursor to specific screen coordinates. Can be instant or animated over a duration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate (horizontal position, must be within screen width)"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate (vertical position, must be within screen height)"
                    },
                    "duration": {
                        "type": "number",
                        "description": "Movement duration in seconds (0 for instant, default: 0.0)",
                        "default": 0.0
                    }
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "drag",
            "description": "Drag from start coordinates to end coordinates. Useful for moving objects, selecting text, or drawing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_x": {
                        "type": "integer",
                        "description": "Starting X coordinate (must be within screen width)"
                    },
                    "start_y": {
                        "type": "integer",
                        "description": "Starting Y coordinate (must be within screen height)"
                    },
                    "end_x": {
                        "type": "integer",
                        "description": "Ending X coordinate (must be within screen width)"
                    },
                    "end_y": {
                        "type": "integer",
                        "description": "Ending Y coordinate (must be within screen height)"
                    },
                    "duration": {
                        "type": "number",
                        "description": "Drag duration in seconds (default: 0.5)",
                        "default": 0.5
                    }
                },
                "required": ["start_x", "start_y", "end_x", "end_y"]
            }
        }
    }
]


# ============================================================================
# WINDOW MANAGEMENT SCHEMAS
# ============================================================================

WINDOW_MANAGEMENT_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "activate_window",
            "description": "Bring a window to the foreground and give it focus. Can search by window title or application name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "Window title or application name (e.g., 'chrome', 'notepad', 'Calculator', 'Visual Studio Code')"
                    }
                },
                "required": ["identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_window",
            "description": "Close a window by sending a close message. Can search by window title or application name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "Window title or application name to close"
                    }
                },
                "required": ["identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "minimize_window",
            "description": "Minimize a window to the taskbar. Can search by window title or application name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "Window title or application name to minimize"
                    }
                },
                "required": ["identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "maximize_window",
            "description": "Maximize a window to fill the screen. Can search by window title or application name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "Window title or application name to maximize"
                    }
                },
                "required": ["identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_active_window",
            "description": "Get the title of the currently active (foreground) window.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# ============================================================================
# SCHEMA REGISTRY
# ============================================================================

# All schemas organized by category
# Requirements: 2.1, 2.3
SCHEMAS_BY_CATEGORY = {
    "folder_operations": FOLDER_OPERATIONS_SCHEMAS,
    "file_operations": FILE_OPERATIONS_SCHEMAS,
    "keyboard_operations": KEYBOARD_OPERATIONS_SCHEMAS,
    "mouse_operations": MOUSE_OPERATIONS_SCHEMAS,
    "window_management": WINDOW_MANAGEMENT_SCHEMAS
}


def get_all_schemas() -> List[Dict]:
    """
    Get all function schemas in a flat list.
    
    Returns:
        List of all function schemas in FunctionGemma format
        
    Requirements: 2.1
    """
    all_schemas = []
    for category_schemas in SCHEMAS_BY_CATEGORY.values():
        all_schemas.extend(category_schemas)
    return all_schemas


def get_schemas_by_category(category: str) -> List[Dict]:
    """
    Get function schemas for a specific category.
    
    Args:
        category: Category name (folder_operations, file_operations, etc.)
        
    Returns:
        List of function schemas for the category, or empty list if not found
        
    Requirements: 2.3
    """
    return SCHEMAS_BY_CATEGORY.get(category, [])


def get_schema_by_name(function_name: str) -> Dict:
    """
    Get a specific function schema by name.
    
    Args:
        function_name: Name of the function
        
    Returns:
        Function schema dict, or None if not found
        
    Requirements: 2.1, 2.4
    """
    for schema in get_all_schemas():
        if schema["function"]["name"] == function_name:
            return schema
    return None


def get_function_names() -> List[str]:
    """
    Get a list of all function names.
    
    Returns:
        List of function names
        
    Requirements: 2.4
    """
    return [schema["function"]["name"] for schema in get_all_schemas()]


def get_function_names_by_category() -> Dict[str, List[str]]:
    """
    Get function names organized by category.
    
    Returns:
        Dict mapping category names to lists of function names
        
    Requirements: 2.3, 2.4
    """
    return {
        category: [schema["function"]["name"] for schema in schemas]
        for category, schemas in SCHEMAS_BY_CATEGORY.items()
    }


def validate_schema_format(schema: Dict) -> tuple[bool, str]:
    """
    Validate that a schema conforms to FunctionGemma format.
    
    Args:
        schema: Schema dict to validate
        
    Returns:
        (is_valid, error_message) tuple
        
    Requirements: 2.1
    """
    # Check top-level structure
    if not isinstance(schema, dict):
        return False, "Schema must be a dictionary"
    
    if "type" not in schema:
        return False, "Schema must have 'type' field"
    
    if schema["type"] != "function":
        return False, f"Schema type must be 'function', got: {schema['type']}"
    
    if "function" not in schema:
        return False, "Schema must have 'function' field"
    
    function_def = schema["function"]
    
    # Check function definition structure
    if not isinstance(function_def, dict):
        return False, "'function' field must be a dictionary"
    
    if "name" not in function_def:
        return False, "Function definition must have 'name' field"
    
    if not isinstance(function_def["name"], str):
        return False, "Function name must be a string"
    
    if "description" not in function_def:
        return False, "Function definition must have 'description' field"
    
    if not isinstance(function_def["description"], str):
        return False, "Function description must be a string"
    
    if "parameters" not in function_def:
        return False, "Function definition must have 'parameters' field"
    
    parameters = function_def["parameters"]
    
    # Check parameters structure
    if not isinstance(parameters, dict):
        return False, "'parameters' field must be a dictionary"
    
    if "type" not in parameters:
        return False, "Parameters must have 'type' field"
    
    if parameters["type"] != "object":
        return False, f"Parameters type must be 'object', got: {parameters['type']}"
    
    if "properties" not in parameters:
        return False, "Parameters must have 'properties' field"
    
    if not isinstance(parameters["properties"], dict):
        return False, "'properties' field must be a dictionary"
    
    if "required" not in parameters:
        return False, "Parameters must have 'required' field"
    
    if not isinstance(parameters["required"], list):
        return False, "'required' field must be a list"
    
    # Validate parameter types
    valid_types = {"string", "integer", "number", "boolean", "array", "object"}
    
    for param_name, param_def in parameters["properties"].items():
        if not isinstance(param_def, dict):
            return False, f"Parameter '{param_name}' definition must be a dictionary"
        
        if "type" not in param_def:
            return False, f"Parameter '{param_name}' must have 'type' field"
        
        if param_def["type"] not in valid_types:
            return False, f"Parameter '{param_name}' has invalid type: {param_def['type']}"
        
        if "description" not in param_def:
            return False, f"Parameter '{param_name}' must have 'description' field"
    
    # Validate required parameters exist in properties
    for required_param in parameters["required"]:
        if required_param not in parameters["properties"]:
            return False, f"Required parameter '{required_param}' not found in properties"
    
    return True, ""


# Validate all schemas on module load
# Requirements: 2.1
def _validate_all_schemas():
    """
    Validate all schemas in the registry.
    
    Raises:
        ValueError: If any schema is invalid
    """
    for category, schemas in SCHEMAS_BY_CATEGORY.items():
        for schema in schemas:
            is_valid, error_msg = validate_schema_format(schema)
            if not is_valid:
                function_name = schema.get("function", {}).get("name", "unknown")
                raise ValueError(
                    f"Invalid schema for function '{function_name}' in category '{category}': {error_msg}"
                )


# Run validation on import
_validate_all_schemas()


# ============================================================================
# SUMMARY
# ============================================================================

# Total function count: 25 functions
# - Folder operations: 4 functions
# - File operations: 5 functions
# - Keyboard operations: 4 functions
# - Mouse operations: 5 functions
# - Window management: 5 functions
#
# All schemas validated against FunctionGemma format requirements
# Requirements: 2.1, 2.3, 2.5
