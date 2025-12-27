"""
Unit tests for FunctionRegistry

Tests the core functionality of the FunctionRegistry class including:
- Function registration and lookup
- Schema validation
- Category organization
- Parameter validation
- Placeholder function handling
"""

import pytest
from function_registry import FunctionRegistry, FunctionSchema


class TestFunctionRegistryBasics:
    """Test basic registry operations."""
    
    def test_initialization(self):
        """Test registry initializes correctly."""
        registry = FunctionRegistry()
        assert registry.get_function_count() == 0
        assert registry.list_all_functions() == []
    
    def test_register_valid_function(self):
        """Test registering a valid function."""
        registry = FunctionRegistry()
        
        def test_func(text: str) -> dict:
            return {"success": True, "text": text}
        
        schema = {
            "description": "Test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to process"}
                },
                "required": ["text"]
            }
        }
        
        registry.register_function(
            name="test_func",
            implementation=test_func,
            schema=schema,
            category="keyboard_operations"
        )
        
        assert registry.get_function_count() == 1
        assert "test_func" in registry.list_all_functions()
        assert registry.get_function("test_func") is test_func
    
    def test_register_duplicate_function(self):
        """Test that duplicate registration overwrites."""
        registry = FunctionRegistry()
        
        def func1():
            return 1
        
        def func2():
            return 2
        
        schema = {
            "description": "Test",
            "parameters": {"type": "object", "properties": {}}
        }
        
        registry.register_function("test", func1, schema, "file_operations")
        registry.register_function("test", func2, schema, "file_operations")
        
        assert registry.get_function_count() == 1
        assert registry.get_function("test") is func2


class TestSchemaValidation:
    """Test schema validation."""
    
    def test_valid_schema(self):
        """Test that valid schemas are accepted."""
        registry = FunctionRegistry()
        
        schema = {
            "description": "Valid schema",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "count": {"type": "integer"},
                    "enabled": {"type": "boolean"}
                },
                "required": ["name"]
            }
        }
        
        def dummy():
            pass
        
        # Should not raise
        registry.register_function("test", dummy, schema, "file_operations")
    
    def test_invalid_schema_missing_parameters(self):
        """Test that schema without parameters is rejected."""
        registry = FunctionRegistry()
        
        schema = {
            "description": "Invalid schema"
        }
        
        def dummy():
            pass
        
        with pytest.raises(ValueError, match="must include 'parameters'"):
            registry.register_function("test", dummy, schema, "file_operations")
    
    def test_invalid_schema_wrong_type(self):
        """Test that schema with wrong type is rejected."""
        registry = FunctionRegistry()
        
        schema = {
            "description": "Invalid schema",
            "parameters": {
                "type": "string"  # Should be "object"
            }
        }
        
        def dummy():
            pass
        
        with pytest.raises(ValueError, match="must be 'object'"):
            registry.register_function("test", dummy, schema, "file_operations")
    
    def test_invalid_schema_unsupported_property_type(self):
        """Test that unsupported property types are rejected."""
        registry = FunctionRegistry()
        
        schema = {
            "description": "Invalid schema",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {"type": "unknown_type"}
                }
            }
        }
        
        def dummy():
            pass
        
        with pytest.raises(ValueError, match="unsupported type"):
            registry.register_function("test", dummy, schema, "file_operations")


class TestCategoryOrganization:
    """Test category-based organization."""
    
    def test_valid_categories(self):
        """Test that all valid categories are accepted."""
        registry = FunctionRegistry()
        
        def dummy():
            pass
        
        schema = {
            "description": "Test",
            "parameters": {"type": "object", "properties": {}}
        }
        
        for category in FunctionRegistry.VALID_CATEGORIES:
            registry.register_function(
                f"func_{category}",
                dummy,
                schema,
                category
            )
        
        assert registry.get_function_count() == len(FunctionRegistry.VALID_CATEGORIES)
    
    def test_invalid_category(self):
        """Test that invalid categories are rejected."""
        registry = FunctionRegistry()
        
        def dummy():
            pass
        
        schema = {
            "description": "Test",
            "parameters": {"type": "object", "properties": {}}
        }
        
        with pytest.raises(ValueError, match="Invalid category"):
            registry.register_function("test", dummy, schema, "invalid_category")
    
    def test_get_functions_by_category(self):
        """Test retrieving functions by category."""
        registry = FunctionRegistry()
        
        def dummy():
            pass
        
        schema = {
            "description": "Test",
            "parameters": {"type": "object", "properties": {}}
        }
        
        # Register functions in different categories
        registry.register_function("file1", dummy, schema, "file_operations")
        registry.register_function("file2", dummy, schema, "file_operations")
        registry.register_function("key1", dummy, schema, "keyboard_operations")
        
        file_funcs = registry.get_functions_by_category("file_operations")
        assert len(file_funcs) == 2
        assert "file1" in file_funcs
        assert "file2" in file_funcs
        
        key_funcs = registry.get_functions_by_category("keyboard_operations")
        assert len(key_funcs) == 1
        assert "key1" in key_funcs


class TestParameterValidation:
    """Test parameter validation."""
    
    def test_validate_valid_parameters(self):
        """Test that valid parameters pass validation."""
        registry = FunctionRegistry()
        
        def dummy(name: str, count: int):
            pass
        
        schema = {
            "description": "Test",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "count": {"type": "integer"}
                },
                "required": ["name"]
            }
        }
        
        registry.register_function("test", dummy, schema, "file_operations")
        
        is_valid, error = registry.validate_parameters(
            "test",
            {"name": "test", "count": 5}
        )
        
        assert is_valid
        assert error is None
    
    def test_validate_missing_required_parameter(self):
        """Test that missing required parameters are caught."""
        registry = FunctionRegistry()
        
        def dummy(name: str):
            pass
        
        schema = {
            "description": "Test",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            }
        }
        
        registry.register_function("test", dummy, schema, "file_operations")
        
        is_valid, error = registry.validate_parameters("test", {})
        
        assert not is_valid
        assert "Missing required parameter" in error
        assert "name" in error
    
    def test_validate_wrong_parameter_type(self):
        """Test that wrong parameter types are caught."""
        registry = FunctionRegistry()
        
        def dummy(count: int):
            pass
        
        schema = {
            "description": "Test",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {"type": "integer"}
                },
                "required": ["count"]
            }
        }
        
        registry.register_function("test", dummy, schema, "file_operations")
        
        is_valid, error = registry.validate_parameters(
            "test",
            {"count": "not_an_int"}
        )
        
        assert not is_valid
        assert "invalid type" in error.lower()
    
    def test_validate_enum_constraint(self):
        """Test that enum constraints are enforced."""
        registry = FunctionRegistry()
        
        def dummy(location: str):
            pass
        
        schema = {
            "description": "Test",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "enum": ["desktop", "documents", "downloads"]
                    }
                },
                "required": ["location"]
            }
        }
        
        registry.register_function("test", dummy, schema, "file_operations")
        
        # Valid enum value
        is_valid, error = registry.validate_parameters(
            "test",
            {"location": "desktop"}
        )
        assert is_valid
        
        # Invalid enum value
        is_valid, error = registry.validate_parameters(
            "test",
            {"location": "invalid"}
        )
        assert not is_valid
        assert "Must be one of" in error


class TestPlaceholderFunctions:
    """Test placeholder function handling."""
    
    def test_register_placeholder(self):
        """Test registering a placeholder function."""
        registry = FunctionRegistry()
        
        def dummy():
            pass
        
        schema = {
            "description": "Placeholder",
            "parameters": {"type": "object", "properties": {}}
        }
        
        registry.register_function(
            "placeholder_func",
            dummy,
            schema,
            "file_operations",
            is_placeholder=True
        )
        
        assert registry.is_placeholder("placeholder_func")
    
    def test_validate_placeholder_parameters(self):
        """Test that placeholder functions fail validation."""
        registry = FunctionRegistry()
        
        def dummy():
            pass
        
        schema = {
            "description": "Placeholder",
            "parameters": {"type": "object", "properties": {}}
        }
        
        registry.register_function(
            "placeholder_func",
            dummy,
            schema,
            "file_operations",
            is_placeholder=True
        )
        
        is_valid, error = registry.validate_parameters("placeholder_func", {})
        
        assert not is_valid
        assert "placeholder" in error.lower()
        assert "not yet implemented" in error.lower()


class TestSchemaGeneration:
    """Test schema generation for FunctionGemma."""
    
    def test_get_all_schemas(self):
        """Test getting all schemas in FunctionGemma format."""
        registry = FunctionRegistry()
        
        def dummy():
            pass
        
        schema1 = {
            "description": "Function 1",
            "parameters": {"type": "object", "properties": {}}
        }
        
        schema2 = {
            "description": "Function 2",
            "parameters": {"type": "object", "properties": {}}
        }
        
        registry.register_function("func1", dummy, schema1, "file_operations")
        registry.register_function("func2", dummy, schema2, "keyboard_operations")
        
        schemas = registry.get_all_schemas()
        
        assert len(schemas) == 2
        assert all(s["type"] == "function" for s in schemas)
        assert all("function" in s for s in schemas)
        assert all("name" in s["function"] for s in schemas)
        assert all("description" in s["function"] for s in schemas)
        assert all("parameters" in s["function"] for s in schemas)
    
    def test_schema_format(self):
        """Test that schemas are in correct FunctionGemma format."""
        registry = FunctionRegistry()
        
        def dummy(text: str):
            pass
        
        schema = {
            "description": "Test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
        
        registry.register_function("test", dummy, schema, "file_operations")
        
        schemas = registry.get_all_schemas()
        assert len(schemas) == 1
        
        fg_schema = schemas[0]
        assert fg_schema["type"] == "function"
        assert fg_schema["function"]["name"] == "test"
        assert fg_schema["function"]["description"] == "Test function"
        assert fg_schema["function"]["parameters"]["type"] == "object"


class TestRegistryUtilities:
    """Test utility methods."""
    
    def test_get_category_summary(self):
        """Test getting category summary."""
        registry = FunctionRegistry()
        
        def dummy():
            pass
        
        schema = {
            "description": "Test",
            "parameters": {"type": "object", "properties": {}}
        }
        
        registry.register_function("file1", dummy, schema, "file_operations")
        registry.register_function("file2", dummy, schema, "file_operations")
        registry.register_function("key1", dummy, schema, "keyboard_operations")
        
        summary = registry.get_category_summary()
        
        assert summary["file_operations"] == 2
        assert summary["keyboard_operations"] == 1
        assert summary["mouse_operations"] == 0
    
    def test_clear_registry(self):
        """Test clearing the registry."""
        registry = FunctionRegistry()
        
        def dummy():
            pass
        
        schema = {
            "description": "Test",
            "parameters": {"type": "object", "properties": {}}
        }
        
        registry.register_function("test", dummy, schema, "file_operations")
        assert registry.get_function_count() == 1
        
        registry.clear()
        assert registry.get_function_count() == 0
        assert registry.list_all_functions() == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
