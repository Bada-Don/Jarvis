"""
Integration test for FunctionRegistry with FunctionGemmaPlannerService

This test verifies that the FunctionRegistry integrates correctly with
the FunctionGemmaPlannerService.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from function_registry import FunctionRegistry


def test_registry_with_service_interface():
    """Test that FunctionRegistry provides the interface expected by the service."""
    registry = FunctionRegistry()
    
    # Define some test functions
    def open_app(app_name: str) -> dict:
        return {"success": True, "message": f"Opened {app_name}"}
    
    def type_text(text: str) -> dict:
        return {"success": True, "message": f"Typed: {text}"}
    
    def create_folder(folder_name: str, location: str = "desktop") -> dict:
        return {"success": True, "message": f"Created {folder_name} in {location}"}
    
    # Register functions with schemas
    registry.register_function(
        name="open_app",
        implementation=open_app,
        schema={
            "description": "Open an application by name",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application"}
                },
                "required": ["app_name"]
            }
        },
        category="window_management"
    )
    
    registry.register_function(
        name="type_text",
        implementation=type_text,
        schema={
            "description": "Type text using the keyboard",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type"}
                },
                "required": ["text"]
            }
        },
        category="keyboard_operations"
    )
    
    registry.register_function(
        name="create_folder",
        implementation=create_folder,
        schema={
            "description": "Create a new folder",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder_name": {"type": "string", "description": "Name of the folder"},
                    "location": {
                        "type": "string",
                        "description": "Where to create it",
                        "enum": ["desktop", "documents", "downloads"]
                    }
                },
                "required": ["folder_name"]
            }
        },
        category="folder_operations"
    )
    
    # Test get_all_schemas() - this is what the service calls
    schemas = registry.get_all_schemas()
    
    print(f"\n✓ Registry has {len(schemas)} functions")
    assert len(schemas) == 3
    
    # Verify schema format matches what FunctionGemma expects
    for schema in schemas:
        assert schema["type"] == "function"
        assert "function" in schema
        assert "name" in schema["function"]
        assert "description" in schema["function"]
        assert "parameters" in schema["function"]
        print(f"  • {schema['function']['name']}: {schema['function']['description']}")
    
    # Test function lookup
    open_app_func = registry.get_function("open_app")
    assert open_app_func is not None
    assert callable(open_app_func)
    
    # Test function execution
    result = open_app_func(app_name="notepad")
    assert result["success"]
    print(f"\n✓ Function execution works: {result['message']}")
    
    # Test parameter validation
    is_valid, error = registry.validate_parameters("open_app", {"app_name": "notepad"})
    assert is_valid
    print(f"✓ Parameter validation works")
    
    # Test invalid parameters
    is_valid, error = registry.validate_parameters("open_app", {})
    assert not is_valid
    assert "Missing required parameter" in error
    print(f"✓ Invalid parameter detection works: {error}")
    
    # Test category organization
    keyboard_funcs = registry.get_functions_by_category("keyboard_operations")
    assert "type_text" in keyboard_funcs
    print(f"\n✓ Category organization works")
    
    # Test category summary
    summary = registry.get_category_summary()
    assert summary["keyboard_operations"] == 1
    assert summary["window_management"] == 1
    assert summary["folder_operations"] == 1
    print(f"✓ Category summary: {summary}")
    
    print("\n" + "="*70)
    print("✓ All integration tests passed!")
    print("✓ FunctionRegistry is ready for use with FunctionGemmaPlannerService")
    print("="*70)


if __name__ == "__main__":
    test_registry_with_service_interface()
