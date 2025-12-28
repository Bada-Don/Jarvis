"""
Registry Initialization Module

This module populates the FunctionRegistry with all available function implementations
and their schemas. It imports all function modules and registers them with proper schemas.
"""

import logging
from function_registry import FunctionRegistry
from function_schemas import (
    FOLDER_OPERATIONS_SCHEMAS,
    FILE_OPERATIONS_SCHEMAS,
    KEYBOARD_OPERATIONS_SCHEMAS,
    MOUSE_OPERATIONS_SCHEMAS,
    WINDOW_MANAGEMENT_SCHEMAS
)

# Import function implementations
from functions import folder_operations
from functions import file_operations
from functions import keyboard_operations
from functions import mouse_operations
from functions import window_management

logger = logging.getLogger(__name__)


def initialize_function_registry() -> FunctionRegistry:
    """
    Initialize and populate the FunctionRegistry with all available functions.
    
    This function creates a new FunctionRegistry instance and registers all
    function implementations with their corresponding schemas.
    
    Returns:
        Populated FunctionRegistry instance
    """
    registry = FunctionRegistry()
    
    logger.info("Initializing function registry...")
    
    # Register folder operations
    _register_folder_operations(registry)
    
    # Register file operations
    _register_file_operations(registry)
    
    # Register keyboard operations
    _register_keyboard_operations(registry)
    
    # Register mouse operations
    _register_mouse_operations(registry)
    
    # Register window management operations
    _register_window_management(registry)
    
    # Log summary
    summary = registry.get_category_summary()
    total = registry.get_function_count()
    logger.info(f"Registry initialized with {total} functions:")
    for category, count in summary.items():
        if count > 0:
            logger.info(f"  - {category}: {count} functions")
    
    return registry


def _register_folder_operations(registry: FunctionRegistry):
    """Register folder operation functions."""
    function_map = {
        "create_folder": folder_operations.create_folder,
        "delete_folder": folder_operations.delete_folder,
        "open_folder": folder_operations.open_folder,
        "list_folder": folder_operations.list_folder
    }
    
    for schema_data in FOLDER_OPERATIONS_SCHEMAS:
        func_info = schema_data["function"]
        func_name = func_info["name"]
        
        if func_name in function_map:
            schema = {
                "description": func_info["description"],
                "parameters": func_info["parameters"]
            }
            
            registry.register_function(
                name=func_name,
                implementation=function_map[func_name],
                schema=schema,
                category="folder_operations"
            )
        else:
            logger.warning(f"No implementation found for {func_name}")


def _register_file_operations(registry: FunctionRegistry):
    """Register file operation functions."""
    function_map = {
        "delete_file": file_operations.delete_file,
        "rename_file": file_operations.rename_file,
        "copy_file": file_operations.copy_file,
        "move_file": file_operations.move_file,
        "open_file": file_operations.open_file
    }
    
    for schema_data in FILE_OPERATIONS_SCHEMAS:
        func_info = schema_data["function"]
        func_name = func_info["name"]
        
        if func_name in function_map:
            schema = {
                "description": func_info["description"],
                "parameters": func_info["parameters"]
            }
            
            registry.register_function(
                name=func_name,
                implementation=function_map[func_name],
                schema=schema,
                category="file_operations"
            )
        else:
            logger.warning(f"No implementation found for {func_name}")


def _register_keyboard_operations(registry: FunctionRegistry):
    """Register keyboard operation functions."""
    function_map = {
        "type_text": keyboard_operations.type_text,
        "press_key": keyboard_operations.press_key,
        "press_hotkey": keyboard_operations.press_hotkey,
        "press_key_repeat": keyboard_operations.press_key_repeat
    }
    
    for schema_data in KEYBOARD_OPERATIONS_SCHEMAS:
        func_info = schema_data["function"]
        func_name = func_info["name"]
        
        if func_name in function_map:
            schema = {
                "description": func_info["description"],
                "parameters": func_info["parameters"]
            }
            
            registry.register_function(
                name=func_name,
                implementation=function_map[func_name],
                schema=schema,
                category="keyboard_operations"
            )
        else:
            logger.warning(f"No implementation found for {func_name}")


def _register_mouse_operations(registry: FunctionRegistry):
    """Register mouse operation functions."""
    function_map = {
        "click": mouse_operations.click,
        "double_click": mouse_operations.double_click,
        "right_click": mouse_operations.right_click,
        "move_mouse": mouse_operations.move_mouse,
        "drag": mouse_operations.drag
    }
    
    for schema_data in MOUSE_OPERATIONS_SCHEMAS:
        func_info = schema_data["function"]
        func_name = func_info["name"]
        
        if func_name in function_map:
            schema = {
                "description": func_info["description"],
                "parameters": func_info["parameters"]
            }
            
            registry.register_function(
                name=func_name,
                implementation=function_map[func_name],
                schema=schema,
                category="mouse_operations"
            )
        else:
            logger.warning(f"No implementation found for {func_name}")


def _register_window_management(registry: FunctionRegistry):
    """Register window management functions."""
    function_map = {
        "activate_window": window_management.activate_window,
        "close_window": window_management.close_window,
        "minimize_window": window_management.minimize_window,
        "maximize_window": window_management.maximize_window,
        "get_active_window": window_management.get_active_window
    }
    
    for schema_data in WINDOW_MANAGEMENT_SCHEMAS:
        func_info = schema_data["function"]
        func_name = func_info["name"]
        
        if func_name in function_map:
            schema = {
                "description": func_info["description"],
                "parameters": func_info["parameters"]
            }
            
            registry.register_function(
                name=func_name,
                implementation=function_map[func_name],
                schema=schema,
                category="window_management"
            )
        else:
            logger.warning(f"No implementation found for {func_name}")


# Create a singleton instance for easy import
_global_registry = None


def get_global_registry() -> FunctionRegistry:
    """
    Get the global FunctionRegistry singleton instance.
    
    Creates and initializes the registry on first call, then returns
    the same instance on subsequent calls.
    
    Returns:
        Global FunctionRegistry instance
    """
    global _global_registry
    
    if _global_registry is None:
        _global_registry = initialize_function_registry()
    
    return _global_registry
