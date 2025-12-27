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
- Automatic schema generation from function signatures and docstrings
"""

import logging
from typing import Callable, Optional, List, Dict, Tuple, Any, get_type_hints
from dataclasses import dataclass
import json
import inspect

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
    
    def register_function_auto(
        self,
        name: str,
        implementation: Callable,
        category: str,
        description: Optional[str] = None,
        is_placeholder: bool = False
    ) -> None:
        """
        Register a function with automatic schema generation.
        
        Automatically generates a JSON schema from the function's type hints
        and docstring. This provides a convenient way to register functions
        without manually writing schemas.
        
        Args:
            name: Function name (must be unique)
            implementation: Callable function implementation
            category: Function category (must be in VALID_CATEGORIES)
            description: Optional description (extracted from docstring if not provided)
            is_placeholder: Whether this is a placeholder for future implementation
        
        Raises:
            ValueError: If name is empty, category is invalid, or schema generation fails
            TypeError: If implementation is not callable
        
        Example:
            def create_folder(path: str, confirm: bool = False) -> dict:
                '''Create a folder at the specified path.
                
                Args:
                    path: Full path to folder to create
                    confirm: Whether to confirm before creation
                
                Returns:
                    Result dictionary with success status
                '''
                # implementation
                pass
            
            registry.register_function_auto(
                name="create_folder",
                implementation=create_folder,
                category="folder_operations"
            )
        """
        # Generate schema automatically
        schema = self._generate_schema_from_function(implementation, description)
        
        # Register using the standard method
        self.register_function(
            name=name,
            implementation=implementation,
            schema=schema,
            category=category,
            is_placeholder=is_placeholder
        )
        
        logger.info(f"Auto-registered function: {name} with generated schema")
    
    def _generate_schema_from_function(
        self,
        func: Callable,
        description: Optional[str] = None
    ) -> dict:
        """
        Generate a JSON schema from a function's signature and docstring.
        
        Extracts type hints and parameter information to create a valid
        JSON schema for FunctionGemma compatibility.
        
        Args:
            func: Function to generate schema for
            description: Optional description (uses docstring if not provided)
        
        Returns:
            JSON schema dict
        
        Raises:
            ValueError: If schema generation fails
        """
        # Get function signature
        try:
            sig = inspect.signature(func)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Cannot inspect function signature: {e}")
        
        # Get type hints
        try:
            type_hints = get_type_hints(func)
        except Exception:
            type_hints = {}
        
        # Extract description from docstring if not provided
        if description is None:
            doc = inspect.getdoc(func)
            if doc:
                # Use first line of docstring as description
                description = doc.split('\n')[0].strip()
            else:
                description = f"Function {func.__name__}"
        
        # Build properties and required fields
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            # Skip self, cls, *args, **kwargs
            if param_name in ('self', 'cls') or param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD
            ):
                continue
            
            # Get type hint
            param_type = type_hints.get(param_name)
            
            # Convert Python type to JSON schema type
            json_type = self._python_type_to_json_type(param_type)
            
            # Build property schema
            prop_schema = {"type": json_type}
            
            # Extract parameter description from docstring
            param_desc = self._extract_param_description(func, param_name)
            if param_desc:
                prop_schema["description"] = param_desc
            
            properties[param_name] = prop_schema
            
            # Check if parameter is required (no default value)
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        # Build complete schema
        schema = {
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties
            }
        }
        
        if required:
            schema["parameters"]["required"] = required
        
        return schema
    
    def _python_type_to_json_type(self, python_type: Any) -> str:
        """
        Convert a Python type hint to a JSON schema type.
        
        Args:
            python_type: Python type hint
        
        Returns:
            JSON schema type string
        """
        if python_type is None or python_type == inspect.Parameter.empty:
            return "string"  # Default to string
        
        # Handle basic types
        type_mapping = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
            List: "array",
            Dict: "object"
        }
        
        # Check direct type match
        if python_type in type_mapping:
            return type_mapping[python_type]
        
        # Check if it's a typing generic
        origin = getattr(python_type, '__origin__', None)
        if origin in type_mapping:
            return type_mapping[origin]
        
        # Default to string for unknown types
        return "string"
    
    def _extract_param_description(self, func: Callable, param_name: str) -> Optional[str]:
        """
        Extract parameter description from function docstring.
        
        Looks for Google-style or NumPy-style parameter documentation.
        
        Args:
            func: Function to extract from
            param_name: Parameter name to find
        
        Returns:
            Parameter description or None
        """
        doc = inspect.getdoc(func)
        if not doc:
            return None
        
        lines = doc.split('\n')
        
        # Look for "Args:" section
        in_args_section = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Check for Args section start
            if stripped.lower() in ('args:', 'arguments:', 'parameters:'):
                in_args_section = True
                continue
            
            # Check for section end
            if in_args_section and stripped.endswith(':') and not stripped.startswith(' '):
                break
            
            # Look for parameter
            if in_args_section and stripped.startswith(f"{param_name}:"):
                # Extract description after colon
                desc = stripped[len(param_name) + 1:].strip()
                return desc
        
        return None
    
    def add_category(self, category: str) -> None:
        """
        Add a new valid category to the registry.
        
        This allows extending the registry with custom categories beyond
        the default set (folder_operations, file_operations, etc.).
        
        Args:
            category: Category name to add
        
        Raises:
            ValueError: If category is empty or already exists
        
        Example:
            registry.add_category("network_operations")
            registry.register_function(
                name="http_get",
                implementation=http_get_impl,
                schema=http_get_schema,
                category="network_operations"
            )
        """
        if not category or not category.strip():
            raise ValueError("Category name cannot be empty")
        
        if category in self.VALID_CATEGORIES:
            logger.warning(f"Category '{category}' already exists")
            return
        
        self.VALID_CATEGORIES.add(category)
        logger.info(f"Added new category: {category}")
    
    def remove_category(self, category: str) -> None:
        """
        Remove a category from the registry.
        
        Note: This will not affect already registered functions in that category,
        but will prevent new functions from being registered to it.
        
        Args:
            category: Category name to remove
        
        Raises:
            ValueError: If category doesn't exist or has registered functions
        """
        if category not in self.VALID_CATEGORIES:
            raise ValueError(f"Category '{category}' does not exist")
        
        # Check if any functions use this category
        functions_in_category = self.get_functions_by_category(category)
        if functions_in_category:
            raise ValueError(
                f"Cannot remove category '{category}': "
                f"{len(functions_in_category)} functions still registered"
            )
        
        self.VALID_CATEGORIES.remove(category)
        logger.info(f"Removed category: {category}")
    
    def unregister_function(self, name: str) -> bool:
        """
        Unregister a function from the registry.
        
        Args:
            name: Function name to unregister
        
        Returns:
            True if function was unregistered, False if not found
        """
        if name not in self._functions:
            logger.warning(f"Function '{name}' not found for unregistration")
            return False
        
        del self._functions[name]
        del self._schemas[name]
        logger.info(f"Unregistered function: {name}")
        return True
    
    def get_placeholder_functions(self) -> List[str]:
        """
        Get a list of all placeholder function names.
        
        Returns:
            List of placeholder function names
        """
        return [
            name for name, schema in self._schemas.items()
            if schema.is_placeholder
        ]
    
    def export_schemas(self, filepath: str) -> None:
        """
        Export all function schemas to a JSON file.
        
        Useful for documentation, debugging, or sharing schemas.
        
        Args:
            filepath: Path to output JSON file
        """
        schemas = self.get_all_schemas()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(schemas, f, indent=2)
        
        logger.info(f"Exported {len(schemas)} schemas to {filepath}")
    
    def import_schemas(self, filepath: str) -> int:
        """
        Import function schemas from a JSON file.
        
        Note: This only imports schemas, not implementations.
        Functions imported this way will be marked as placeholders.
        
        Args:
            filepath: Path to JSON file with schemas
        
        Returns:
            Number of schemas imported
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            schemas = json.load(f)
        
        count = 0
        for schema_data in schemas:
            if schema_data.get("type") != "function":
                continue
            
            func_data = schema_data.get("function", {})
            name = func_data.get("name")
            
            if not name:
                logger.warning("Skipping schema without name")
                continue
            
            # Create placeholder implementation
            def placeholder_impl(**kwargs):
                return {
                    "success": False,
                    "message": f"Function '{name}' is not yet implemented"
                }
            
            # Determine category (default to "other")
            category = "other"
            if "other" not in self.VALID_CATEGORIES:
                self.add_category("other")
            
            # Build schema
            schema = {
                "description": func_data.get("description", ""),
                "parameters": func_data.get("parameters", {"type": "object", "properties": {}})
            }
            
            try:
                self.register_function(
                    name=name,
                    implementation=placeholder_impl,
                    schema=schema,
                    category=category,
                    is_placeholder=True
                )
                count += 1
            except Exception as e:
                logger.error(f"Failed to import schema for '{name}': {e}")
        
        logger.info(f"Imported {count} schemas from {filepath}")
        return count
