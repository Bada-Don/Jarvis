"""
Unit tests for function_schemas module.

Tests schema format validation, schema retrieval, and FunctionGemma format compliance.

Requirements: 2.1, 2.5
"""

import pytest
import function_schemas


class TestSchemaRetrieval:
    """Test schema retrieval functions."""
    
    def test_get_all_schemas_returns_list(self):
        """Test that get_all_schemas returns a list."""
        schemas = function_schemas.get_all_schemas()
        assert isinstance(schemas, list)
        assert len(schemas) > 0
    
    def test_get_all_schemas_count(self):
        """Test that we have the expected number of schemas."""
        schemas = function_schemas.get_all_schemas()
        # We have 23 functions implemented
        assert len(schemas) == 23
    
    def test_get_schemas_by_category_folder_operations(self):
        """Test retrieving folder operations schemas."""
        schemas = function_schemas.get_schemas_by_category("folder_operations")
        assert isinstance(schemas, list)
        assert len(schemas) == 4
        
        names = [s["function"]["name"] for s in schemas]
        assert "create_folder" in names
        assert "delete_folder" in names
        assert "open_folder" in names
        assert "list_folder" in names
    
    def test_get_schemas_by_category_file_operations(self):
        """Test retrieving file operations schemas."""
        schemas = function_schemas.get_schemas_by_category("file_operations")
        assert isinstance(schemas, list)
        assert len(schemas) == 5
        
        names = [s["function"]["name"] for s in schemas]
        assert "delete_file" in names
        assert "rename_file" in names
        assert "copy_file" in names
        assert "move_file" in names
        assert "open_file" in names
    
    def test_get_schemas_by_category_keyboard_operations(self):
        """Test retrieving keyboard operations schemas."""
        schemas = function_schemas.get_schemas_by_category("keyboard_operations")
        assert isinstance(schemas, list)
        assert len(schemas) == 4
        
        names = [s["function"]["name"] for s in schemas]
        assert "type_text" in names
        assert "press_key" in names
        assert "press_hotkey" in names
        assert "press_key_repeat" in names
    
    def test_get_schemas_by_category_mouse_operations(self):
        """Test retrieving mouse operations schemas."""
        schemas = function_schemas.get_schemas_by_category("mouse_operations")
        assert isinstance(schemas, list)
        assert len(schemas) == 5
        
        names = [s["function"]["name"] for s in schemas]
        assert "click" in names
        assert "double_click" in names
        assert "right_click" in names
        assert "move_mouse" in names
        assert "drag" in names
    
    def test_get_schemas_by_category_window_management(self):
        """Test retrieving window management schemas."""
        schemas = function_schemas.get_schemas_by_category("window_management")
        assert isinstance(schemas, list)
        assert len(schemas) == 5
        
        names = [s["function"]["name"] for s in schemas]
        assert "activate_window" in names
        assert "close_window" in names
        assert "minimize_window" in names
        assert "maximize_window" in names
        assert "get_active_window" in names
    
    def test_get_schemas_by_category_invalid(self):
        """Test retrieving schemas for invalid category."""
        schemas = function_schemas.get_schemas_by_category("invalid_category")
        assert isinstance(schemas, list)
        assert len(schemas) == 0
    
    def test_get_schema_by_name_valid(self):
        """Test retrieving a schema by name."""
        schema = function_schemas.get_schema_by_name("create_folder")
        assert schema is not None
        assert schema["function"]["name"] == "create_folder"
        assert "description" in schema["function"]
        assert "parameters" in schema["function"]
    
    def test_get_schema_by_name_invalid(self):
        """Test retrieving a schema with invalid name."""
        schema = function_schemas.get_schema_by_name("nonexistent_function")
        assert schema is None
    
    def test_get_function_names(self):
        """Test getting all function names."""
        names = function_schemas.get_function_names()
        assert isinstance(names, list)
        assert len(names) == 23
        assert "create_folder" in names
        assert "type_text" in names
        assert "click" in names
    
    def test_get_function_names_by_category(self):
        """Test getting function names organized by category."""
        names_by_cat = function_schemas.get_function_names_by_category()
        assert isinstance(names_by_cat, dict)
        assert len(names_by_cat) == 5
        
        assert "folder_operations" in names_by_cat
        assert "file_operations" in names_by_cat
        assert "keyboard_operations" in names_by_cat
        assert "mouse_operations" in names_by_cat
        assert "window_management" in names_by_cat


class TestSchemaFormatValidation:
    """Test schema format validation."""
    
    def test_validate_valid_schema(self):
        """Test validation of a valid schema."""
        schema = {
            "type": "function",
            "function": {
                "name": "test_function",
                "description": "A test function",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "First parameter"
                        }
                    },
                    "required": ["param1"]
                }
            }
        }
        
        is_valid, error_msg = function_schemas.validate_schema_format(schema)
        assert is_valid
        assert error_msg == ""
    
    def test_validate_missing_type(self):
        """Test validation fails when 'type' is missing."""
        schema = {
            "function": {
                "name": "test_function",
                "description": "A test function",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
        
        is_valid, error_msg = function_schemas.validate_schema_format(schema)
        assert not is_valid
        assert "type" in error_msg.lower()
    
    def test_validate_wrong_type(self):
        """Test validation fails when type is not 'function'."""
        schema = {
            "type": "invalid",
            "function": {
                "name": "test_function",
                "description": "A test function",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
        
        is_valid, error_msg = function_schemas.validate_schema_format(schema)
        assert not is_valid
        assert "function" in error_msg.lower()
    
    def test_validate_missing_function_field(self):
        """Test validation fails when 'function' field is missing."""
        schema = {
            "type": "function"
        }
        
        is_valid, error_msg = function_schemas.validate_schema_format(schema)
        assert not is_valid
        assert "function" in error_msg.lower()
    
    def test_validate_missing_name(self):
        """Test validation fails when function name is missing."""
        schema = {
            "type": "function",
            "function": {
                "description": "A test function",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
        
        is_valid, error_msg = function_schemas.validate_schema_format(schema)
        assert not is_valid
        assert "name" in error_msg.lower()
    
    def test_validate_missing_description(self):
        """Test validation fails when description is missing."""
        schema = {
            "type": "function",
            "function": {
                "name": "test_function",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
        
        is_valid, error_msg = function_schemas.validate_schema_format(schema)
        assert not is_valid
        assert "description" in error_msg.lower()
    
    def test_validate_missing_parameters(self):
        """Test validation fails when parameters are missing."""
        schema = {
            "type": "function",
            "function": {
                "name": "test_function",
                "description": "A test function"
            }
        }
        
        is_valid, error_msg = function_schemas.validate_schema_format(schema)
        assert not is_valid
        assert "parameters" in error_msg.lower()
    
    def test_validate_invalid_parameter_type(self):
        """Test validation fails for invalid parameter type."""
        schema = {
            "type": "function",
            "function": {
                "name": "test_function",
                "description": "A test function",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "invalid_type",
                            "description": "First parameter"
                        }
                    },
                    "required": ["param1"]
                }
            }
        }
        
        is_valid, error_msg = function_schemas.validate_schema_format(schema)
        assert not is_valid
        assert "invalid type" in error_msg.lower()
    
    def test_validate_missing_parameter_description(self):
        """Test validation fails when parameter description is missing."""
        schema = {
            "type": "function",
            "function": {
                "name": "test_function",
                "description": "A test function",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string"
                        }
                    },
                    "required": ["param1"]
                }
            }
        }
        
        is_valid, error_msg = function_schemas.validate_schema_format(schema)
        assert not is_valid
        assert "description" in error_msg.lower()
    
    def test_validate_required_param_not_in_properties(self):
        """Test validation fails when required param not in properties."""
        schema = {
            "type": "function",
            "function": {
                "name": "test_function",
                "description": "A test function",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "First parameter"
                        }
                    },
                    "required": ["param1", "param2"]
                }
            }
        }
        
        is_valid, error_msg = function_schemas.validate_schema_format(schema)
        assert not is_valid
        assert "param2" in error_msg


class TestAllSchemasValid:
    """Test that all registered schemas are valid."""
    
    def test_all_schemas_pass_validation(self):
        """Test that all schemas in the registry are valid."""
        schemas = function_schemas.get_all_schemas()
        
        for schema in schemas:
            is_valid, error_msg = function_schemas.validate_schema_format(schema)
            assert is_valid, f"Schema for {schema['function']['name']} is invalid: {error_msg}"
    
    def test_all_schemas_have_required_fields(self):
        """Test that all schemas have required fields."""
        schemas = function_schemas.get_all_schemas()
        
        for schema in schemas:
            assert "type" in schema
            assert schema["type"] == "function"
            
            assert "function" in schema
            func_def = schema["function"]
            
            assert "name" in func_def
            assert isinstance(func_def["name"], str)
            assert len(func_def["name"]) > 0
            
            assert "description" in func_def
            assert isinstance(func_def["description"], str)
            assert len(func_def["description"]) > 0
            
            assert "parameters" in func_def
            params = func_def["parameters"]
            
            assert "type" in params
            assert params["type"] == "object"
            
            assert "properties" in params
            assert isinstance(params["properties"], dict)
            
            assert "required" in params
            assert isinstance(params["required"], list)
    
    def test_all_parameters_have_types_and_descriptions(self):
        """Test that all parameters have type and description."""
        schemas = function_schemas.get_all_schemas()
        
        for schema in schemas:
            func_name = schema["function"]["name"]
            properties = schema["function"]["parameters"]["properties"]
            
            for param_name, param_def in properties.items():
                assert "type" in param_def, f"{func_name}.{param_name} missing type"
                assert "description" in param_def, f"{func_name}.{param_name} missing description"
                
                # Check type is valid
                valid_types = {"string", "integer", "number", "boolean", "array", "object"}
                assert param_def["type"] in valid_types, f"{func_name}.{param_name} has invalid type: {param_def['type']}"


class TestFunctionGemmaFormatCompliance:
    """Test compliance with FunctionGemma format requirements."""
    
    def test_schemas_use_function_type(self):
        """Test that all schemas use 'function' type."""
        schemas = function_schemas.get_all_schemas()
        
        for schema in schemas:
            assert schema["type"] == "function"
    
    def test_parameters_use_object_type(self):
        """Test that all parameters use 'object' type."""
        schemas = function_schemas.get_all_schemas()
        
        for schema in schemas:
            params = schema["function"]["parameters"]
            assert params["type"] == "object"
    
    def test_required_fields_are_lists(self):
        """Test that required fields are lists."""
        schemas = function_schemas.get_all_schemas()
        
        for schema in schemas:
            required = schema["function"]["parameters"]["required"]
            assert isinstance(required, list)
    
    def test_properties_are_dicts(self):
        """Test that properties are dictionaries."""
        schemas = function_schemas.get_all_schemas()
        
        for schema in schemas:
            properties = schema["function"]["parameters"]["properties"]
            assert isinstance(properties, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
