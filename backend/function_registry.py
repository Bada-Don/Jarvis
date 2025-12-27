"""
Function Registry for FunctionGemma Integration

This module provides the FunctionRegistry class that manages function registration,
schema validation, and function lookup for the FunctionGemma planner service.

Key Features:
- Function registration with JSON schema validation
- Category-based organization (folder, file, keyboard, mouse, window operations)
- Placeholder function support for future implementations
- Parameter type validation against schemas
- Schema generation for FunctionGemma model
"""

import logging
from typing import Callable, Optional, List, Dict, Tuple
from dataclasses import dataclass
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FunctionSchema:
    """JSON schema for a function."""
    name: str
    description: str
    parameters: dict
    category: str
    is_placeholder: bool = False
    
    def to_functiongemma_format(self) -> dict:
        """
        Convert to FunctionGemma tool schema format.
        
        Returns:
            Dict in format expected by FunctionGemma
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class FunctionRegistry:
    """
    Registry for managing functions and their schemas.
    
    The FunctionRegistry maintains a centralized registry of all available functions,
    validates their schemas, organizes them by category, and provides lookup capabilities.
    
    Attributes:
        _functions: Dict mapping function names to their implementations
        _schemas: Dict mapping function names to their FunctionSchema objects
        _categories: Set of valid function categories
    """
    
    # Valid function categories as specified in design
    VALID_CATEGORIES = {
        "folder_operations",
        "file_operations",
        "keyboard_operations",
        "mouse_operations",
        "window_management"
    }
    
    def __init__(self):
        """Initialize the function registry."""
        self._functions: Dict[str, Callable] = {}
        self._schemas: Dict[str, FunctionSchema] = {}
        logger.info("FunctionRegistry initialized")
    
    def register_function(
        self,
        name: str,
        implementation: Callable,
        schema: dict,
        category: str,
        is_placeholder: bool = False
    ) -> None:
        """
        Register a function with its schema.
        
        Validates the schema structure and registers the function for use
        by the FunctionGemma planner service.
        
        Args:
            name: Function name (must be unique)
            implementation: Callable function implementation
            schema: JSON schema for the function parameters
            category: Function category (must be in VALID_CATEGORIES)
            is_placeholder: Whether this is a placeholder for future implementation
        
        Raises:
            ValueError: If name is empty, category is invalid, or schema is invalid
            TypeError: If implementation is not callable
        """
        # Validate inputs
        if not name or not name.strip():
            raise ValueError("Function name cannot be empty")
        
        if not callable(implementation):
            raise TypeError(f"Implementation for '{name}' must be callable")
        
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. "
                f"Must be one of: {', '.join(sorted(self.VALID_CATEGORIES))}"
            )
        
        # Validate schema structure
        is_valid, error_msg = self._validate_schema(schema)
        if not is_valid:
            raise ValueError(f"Invalid schema for function '{name}': {error_msg}")
        
        # Check for duplicate registration
        if name in self._functions:
            logger.warning(f"Function '{name}' already registered. Overwriting.")
        
        # Register function
        self._functions[name] = implementation
        
        # Create and store FunctionSchema
        function_schema = FunctionSchema(
            name=name,
            description=schema.get("description", ""),
            parameters=schema.get("parameters", {}),
            category=category,
            is_placeholder=is_placeholder
        )
        self._schemas[name] = function_schema
        
        placeholder_str = " (placeholder)" if is_placeholder else ""
        logger.info(f"Registered function: {name} [{category}]{placeholder_str}")
    
    def _validate_schema(self, schema: dict) -> Tuple[bool, Optional[str]]:
        """
        Validate a function schema structure.
        
        Checks that the schema conforms to JSON Schema format and includes
        required fields for FunctionGemma compatibility.
        
        Args:
            schema: Schema dict to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(schema, dict):
            return False, "Schema must be a dictionary"
        
        # Check for required top-level fields
        if "parameters" not in schema:
            return False, "Schema must include 'parameters' field"
        
        parameters = schema["parameters"]
        if not isinstance(parameters, dict):
            return False, "'parameters' must be a dictionary"
        
        # Validate parameters structure (JSON Schema format)
        if "type" not in parameters:
            return False, "'parameters' must include 'type' field"
        
        if parameters["type"] != "object":
            return False, "'parameters.type' must be 'object'"
        
        # Validate properties if present
        if "properties" in parameters:
            properties = parameters["properties"]
            if not isinstance(properties, dict):
                return False, "'parameters.properties' must be a dictionary"
            
            # Validate each property
            for prop_name, prop_schema in properties.items():
                if not isinstance(prop_schema, dict):
                    return False, f"Property '{prop_name}' schema must be a dictionary"
                
                if "type" not in prop_schema:
                    return False, f"Property '{prop_name}' must include 'type' field"
                
                # Validate type is supported
                valid_types = {"string", "integer", "number", "boolean", "array", "object"}
                prop_type = prop_schema["type"]
                if prop_type not in valid_types:
                    return False, f"Property '{prop_name}' has unsupported type '{prop_type}'"
        
        # Validate required field if present
        if "required" in parameters:
            required = parameters["required"]
            if not isinstance(required, list):
                return False, "'parameters.required' must be a list"
            
            # Check that all required fields exist in properties
            if "properties" in parameters:
                properties = parameters["properties"]
                for req_field in required:
                    if req_field not in properties:
                        return False, f"Required field '{req_field}' not in properties"
        
        return True, None
    
    def get_function(self, name: str) -> Optional[Callable]:
        """
        Get a function by name.
        
        Args:
            name: Function name
        
        Returns:
            Function implementation or None if not found
        """
        return self._functions.get(name)
    
    def get_schema(self, name: str) -> Optional[FunctionSchema]:
        """
        Get a function schema by name.
        
        Args:
            name: Function name
        
        Returns:
            FunctionSchema object or None if not found
        """
        return self._schemas.get(name)
    
    def get_all_schemas(self) -> List[dict]:
        """
        Get all function schemas for the model.
        
        Returns schemas in FunctionGemma format for use with the model.
        
        Returns:
            List of function schemas in FunctionGemma format
        """
        schemas = []
        for schema in self._schemas.values():
            schemas.append(schema.to_functiongemma_format())
        
        logger.debug(f"Returning {len(schemas)} function schemas")
        return schemas
    
    def get_functions_by_category(self, category: str) -> List[str]:
        """
        Get all function names in a category.
        
        Args:
            category: Category name
        
        Returns:
            List of function names in the category
        """
        if category not in self.VALID_CATEGORIES:
            logger.warning(f"Invalid category '{category}'")
            return []
        
        return [
            name for name, schema in self._schemas.items()
            if schema.category == category
        ]
    
    def validate_parameters(
        self,
        name: str,
        parameters: dict
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate function parameters against schema.
        
        Checks that provided parameters match the function's schema requirements,
        including type validation and required field checking.
        
        Args:
            name: Function name
            parameters: Parameter dict to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if function exists
        schema = self._schemas.get(name)
        if schema is None:
            return False, f"Function '{name}' not found in registry"
        
        # Check if function is a placeholder
        if schema.is_placeholder:
            return False, f"Function '{name}' is a placeholder and not yet implemented"
        
        param_schema = schema.parameters
        
        # Check required parameters
        if "required" in param_schema:
            required_fields = param_schema["required"]
            for field in required_fields:
                if field not in parameters:
                    return False, f"Missing required parameter: '{field}'"
        
        # Validate parameter types
        if "properties" in param_schema:
            properties = param_schema["properties"]
            
            for param_name, param_value in parameters.items():
                # Check if parameter is defined in schema
                if param_name not in properties:
                    logger.warning(
                        f"Parameter '{param_name}' not defined in schema for '{name}'"
                    )
                    continue
                
                prop_schema = properties[param_name]
                expected_type = prop_schema.get("type")
                
                # Validate type
                is_valid, error = self._validate_parameter_type(
                    param_name,
                    param_value,
                    expected_type,
                    prop_schema
                )
                
                if not is_valid:
                    return False, error
        
        return True, None
    
    def _validate_parameter_type(
        self,
        param_name: str,
        param_value,
        expected_type: str,
        prop_schema: dict
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a parameter's type.
        
        Args:
            param_name: Parameter name
            param_value: Parameter value
            expected_type: Expected type from schema
            prop_schema: Full property schema (for enum validation)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Type mapping
        type_checks = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "array": lambda v: isinstance(v, list),
            "object": lambda v: isinstance(v, dict)
        }
        
        # Check type
        if expected_type in type_checks:
            if not type_checks[expected_type](param_value):
                return False, (
                    f"Parameter '{param_name}' has invalid type. "
                    f"Expected {expected_type}, got {type(param_value).__name__}"
                )
        
        # Check enum constraint if present
        if "enum" in prop_schema:
            allowed_values = prop_schema["enum"]
            if param_value not in allowed_values:
                return False, (
                    f"Parameter '{param_name}' has invalid value '{param_value}'. "
                    f"Must be one of: {', '.join(map(str, allowed_values))}"
                )
        
        return True, None
    
    def is_placeholder(self, name: str) -> bool:
        """
        Check if a function is a placeholder.
        
        Args:
            name: Function name
        
        Returns:
            True if function is a placeholder, False otherwise
        """
        schema = self._schemas.get(name)
        if schema is None:
            return False
        return schema.is_placeholder
    
    def list_all_functions(self) -> List[str]:
        """
        Get a list of all registered function names.
        
        Returns:
            List of function names
        """
        return list(self._functions.keys())
    
    def get_function_count(self) -> int:
        """
        Get the total number of registered functions.
        
        Returns:
            Number of registered functions
        """
        return len(self._functions)
    
    def get_category_summary(self) -> Dict[str, int]:
        """
        Get a summary of functions by category.
        
        Returns:
            Dict mapping category names to function counts
        """
        summary = {cat: 0 for cat in self.VALID_CATEGORIES}
        
        for schema in self._schemas.values():
            summary[schema.category] += 1
        
        return summary
    
    def clear(self):
        """Clear all registered functions and schemas."""
        self._functions.clear()
        self._schemas.clear()
        logger.info("Function registry cleared")
