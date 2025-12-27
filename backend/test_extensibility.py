"""
Tests for FunctionRegistry extensibility features.

Tests the automatic schema generation, category management,
and other extensibility features added to the FunctionRegistry.
"""

import pytest
import tempfile
import json
import os
from function_registry import FunctionRegistry


class TestAutomaticSchemaGeneration:
    """Test automatic schema generation from function signatures."""
    
    def test_register_function_auto_with_type_hints(self):
        """Test automatic registration with type hints."""
        registry = FunctionRegistry()
        
        def sample_function(path: str, count: int, enabled: bool = False) -> dict:
            """Sample function for testing.
            
            Args:
                path: File path
                count: Number of items
                enabled: Whether feature is enabled
            
            Returns:
                Result dictionary
            """
            return {"success": True}
        
        registry.register_function_auto(
            name="sample_function",
            implementation=sample_function,
            category="file_operations"
        )
        
        # Verify function is registered
        assert registry.get_function("sample_function") is not None
        
        # Verify schema was generated
        schema = registry.get_schema("sample_function")
        assert schema is not None
        assert schema.name == "sample_function"
        assert "Sample function for testing" in schema.description
        
        # Verify parameters
        params = schema.parameters
        assert "properties" in params
        assert "path" in params["properties"]
        assert "count" in params["properties"]
        assert "enabled" in params["properties"]
        
        # Verify types
        assert params["properties"]["path"]["type"] == "string"
        assert params["properties"]["count"]["type"] == "integer"
        assert params["properties"]["enabled"]["type"] == "boolean"
        
        # Verify required fields (only those without defaults)
        assert "required" in params
        assert "path" in params["required"]
        assert "count" in params["required"]
        assert "enabled" not in params["required"]
    
    def test_register_function_auto_without_type_hints(self):
        """Test automatic registration without type hints defaults to string."""
        registry = FunctionRegistry()
        
        def no_hints_function(param1, param2):
            """Function without type hints."""
            return {"success": True}
        
        registry.register_function_auto(
            name="no_hints_function",
            implementation=no_hints_function,
            category="file_operations"
        )
        
        schema = registry.get_schema("no_hints_function")
        assert schema is not None
        
        # Should default to string type
        params = schema.parameters
        assert params["properties"]["param1"]["type"] == "string"
        assert params["properties"]["param2"]["type"] == "string"
    
    def test_register_function_auto_with_custom_description(self):
        """Test automatic registration with custom description."""
        registry = FunctionRegistry()
        
        def func(x: int) -> dict:
            """Original description."""
            return {"success": True}
        
        custom_desc = "Custom description for function"
        registry.register_function_auto(
            name="func",
            implementation=func,
            category="file_operations",
            description=custom_desc
        )
        
        schema = registry.get_schema("func")
        assert schema.description == custom_desc
    
    def test_register_function_auto_extracts_param_descriptions(self):
        """Test that parameter descriptions are extracted from docstring."""
        registry = FunctionRegistry()
        
        def documented_function(path: str, count: int) -> dict:
            """Function with documented parameters.
            
            Args:
                path: The file path to process
                count: Number of iterations
            
            Returns:
                Result dictionary
            """
            return {"success": True}
        
        registry.register_function_auto(
            name="documented_function",
            implementation=documented_function,
            category="file_operations"
        )
        
        schema = registry.get_schema("documented_function")
        params = schema.parameters["properties"]
        
        assert "description" in params["path"]
        assert "file path" in params["path"]["description"].lower()
        assert "description" in params["count"]
        assert "iterations" in params["count"]["description"].lower()
    
    def test_register_function_auto_as_placeholder(self):
        """Test registering a placeholder function with auto schema."""
        registry = FunctionRegistry()
        
        def future_function(x: str) -> dict:
            """Function to be implemented later."""
            return {"success": False, "message": "Not implemented"}
        
        registry.register_function_auto(
            name="future_function",
            implementation=future_function,
            category="file_operations",
            is_placeholder=True
        )
        
        assert registry.is_placeholder("future_function")
        
        # Validation should fail for placeholder
        is_valid, error = registry.validate_parameters("future_function", {"x": "test"})
        assert not is_valid
        assert "placeholder" in error.lower()


class TestCategoryManagement:
    """Test category management features."""
    
    def test_add_new_category(self):
        """Test adding a new category."""
        registry = FunctionRegistry()
        
        initial_count = len(registry.VALID_CATEGORIES)
        registry.add_category("network_operations")
        
        assert "network_operations" in registry.VALID_CATEGORIES
        assert len(registry.VALID_CATEGORIES) == initial_count + 1
    
    def test_add_duplicate_category_warns(self):
        """Test adding duplicate category logs warning but doesn't fail."""
        registry = FunctionRegistry()
        
        registry.add_category("custom_category")
        # Should not raise, just warn
        registry.add_category("custom_category")
        
        assert "custom_category" in registry.VALID_CATEGORIES
    
    def test_add_empty_category_raises(self):
        """Test adding empty category raises error."""
        registry = FunctionRegistry()
        
        with pytest.raises(ValueError, match="cannot be empty"):
            registry.add_category("")
    
    def test_remove_category(self):
        """Test removing a category."""
        registry = FunctionRegistry()
        
        registry.add_category("temp_category")
        assert "temp_category" in registry.VALID_CATEGORIES
        
        registry.remove_category("temp_category")
        assert "temp_category" not in registry.VALID_CATEGORIES
    
    def test_remove_category_with_functions_raises(self):
        """Test removing category with registered functions raises error."""
        registry = FunctionRegistry()
        
        def dummy_func() -> dict:
            return {"success": True}
        
        registry.register_function_auto(
            name="test_func",
            implementation=dummy_func,
            category="file_operations"
        )
        
        with pytest.raises(ValueError, match="functions still registered"):
            registry.remove_category("file_operations")
    
    def test_remove_nonexistent_category_raises(self):
        """Test removing non-existent category raises error."""
        registry = FunctionRegistry()
        
        with pytest.raises(ValueError, match="does not exist"):
            registry.remove_category("nonexistent_category")
    
    def test_register_function_with_custom_category(self):
        """Test registering function with custom category."""
        registry = FunctionRegistry()
        
        registry.add_category("custom_ops")
        
        def custom_func(x: str) -> dict:
            """Custom function."""
            return {"success": True}
        
        registry.register_function_auto(
            name="custom_func",
            implementation=custom_func,
            category="custom_ops"
        )
        
        functions = registry.get_functions_by_category("custom_ops")
        assert "custom_func" in functions


class TestFunctionUnregistration:
    """Test function unregistration."""
    
    def test_unregister_function(self):
        """Test unregistering a function."""
        registry = FunctionRegistry()
        
        def temp_func(x: str) -> dict:
            """Temporary function."""
            return {"success": True}
        
        registry.register_function_auto(
            name="temp_func",
            implementation=temp_func,
            category="file_operations"
        )
        
        assert registry.get_function("temp_func") is not None
        
        result = registry.unregister_function("temp_func")
        assert result is True
        assert registry.get_function("temp_func") is None
        assert registry.get_schema("temp_func") is None
    
    def test_unregister_nonexistent_function(self):
        """Test unregistering non-existent function returns False."""
        registry = FunctionRegistry()
        
        result = registry.unregister_function("nonexistent")
        assert result is False


class TestPlaceholderFunctions:
    """Test placeholder function features."""
    
    def test_get_placeholder_functions(self):
        """Test getting list of placeholder functions."""
        registry = FunctionRegistry()
        
        def impl_func(x: str) -> dict:
            return {"success": True}
        
        def placeholder_func(x: str) -> dict:
            return {"success": False}
        
        registry.register_function_auto(
            name="implemented",
            implementation=impl_func,
            category="file_operations",
            is_placeholder=False
        )
        
        registry.register_function_auto(
            name="placeholder1",
            implementation=placeholder_func,
            category="file_operations",
            is_placeholder=True
        )
        
        registry.register_function_auto(
            name="placeholder2",
            implementation=placeholder_func,
            category="file_operations",
            is_placeholder=True
        )
        
        placeholders = registry.get_placeholder_functions()
        assert len(placeholders) == 2
        assert "placeholder1" in placeholders
        assert "placeholder2" in placeholders
        assert "implemented" not in placeholders


class TestSchemaImportExport:
    """Test schema import/export features."""
    
    def test_export_schemas(self):
        """Test exporting schemas to JSON file."""
        registry = FunctionRegistry()
        
        def func1(x: str) -> dict:
            """Function 1."""
            return {"success": True}
        
        def func2(y: int) -> dict:
            """Function 2."""
            return {"success": True}
        
        registry.register_function_auto("func1", func1, "file_operations")
        registry.register_function_auto("func2", func2, "file_operations")
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            registry.export_schemas(temp_path)
            
            # Verify file was created and contains schemas
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r') as f:
                data = json.load(f)
            
            assert len(data) == 2
            assert any(s["function"]["name"] == "func1" for s in data)
            assert any(s["function"]["name"] == "func2" for s in data)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_import_schemas(self):
        """Test importing schemas from JSON file."""
        registry = FunctionRegistry()
        
        # Create test schema file
        schemas = [
            {
                "type": "function",
                "function": {
                    "name": "imported_func1",
                    "description": "Imported function 1",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "string"}
                        },
                        "required": ["x"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "imported_func2",
                    "description": "Imported function 2",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "y": {"type": "integer"}
                        }
                    }
                }
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(schemas, f)
            temp_path = f.name
        
        try:
            count = registry.import_schemas(temp_path)
            
            assert count == 2
            assert registry.get_function("imported_func1") is not None
            assert registry.get_function("imported_func2") is not None
            
            # Imported functions should be placeholders
            assert registry.is_placeholder("imported_func1")
            assert registry.is_placeholder("imported_func2")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestComplexTypeHints:
    """Test handling of complex type hints."""
    
    def test_list_type_hint(self):
        """Test List type hint converts to array."""
        registry = FunctionRegistry()
        
        from typing import List
        
        def func_with_list(items: List[str]) -> dict:
            """Function with list parameter."""
            return {"success": True}
        
        registry.register_function_auto(
            name="func_with_list",
            implementation=func_with_list,
            category="file_operations"
        )
        
        schema = registry.get_schema("func_with_list")
        assert schema.parameters["properties"]["items"]["type"] == "array"
    
    def test_dict_type_hint(self):
        """Test Dict type hint converts to object."""
        registry = FunctionRegistry()
        
        from typing import Dict
        
        def func_with_dict(config: Dict[str, str]) -> dict:
            """Function with dict parameter."""
            return {"success": True}
        
        registry.register_function_auto(
            name="func_with_dict",
            implementation=func_with_dict,
            category="file_operations"
        )
        
        schema = registry.get_schema("func_with_dict")
        assert schema.parameters["properties"]["config"]["type"] == "object"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
