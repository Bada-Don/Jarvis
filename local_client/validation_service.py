"""
Validation Service for JARVIS Settings Interface

This module provides the ValidationService class for validating user input
and settings according to defined rules and constraints.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse


class ValidationService:
    """
    Service for validating settings and user input.
    Provides methods for path, number, string, and complete settings validation.
    """
    
    @staticmethod
    def validate_path(
        path: str,
        must_exist: bool = True,
        is_directory: bool = False,
        is_executable: bool = False
    ) -> Tuple[bool, str]:
        """
        Validate file/directory path
        
        Args:
            path: Path string to validate
            must_exist: Whether the path must exist on the filesystem
            is_directory: Whether the path should be a directory
            is_executable: Whether the path should be an executable file
            
        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        # Empty path validation
        if not path or not path.strip():
            return False, "Path cannot be empty"
        
        path = path.strip()
        
        # Convert to Path object for easier manipulation
        try:
            path_obj = Path(path)
        except Exception as e:
            return False, f"Invalid path format: {str(e)}"
        
        # Check if path must exist
        if must_exist:
            if not path_obj.exists():
                return False, f"Path does not exist: {path}"
            
            # Check if it should be a directory
            if is_directory:
                if not path_obj.is_dir():
                    return False, f"Path is not a directory: {path}"
            else:
                # If not explicitly a directory, check if it's a file when needed
                if is_executable and not path_obj.is_file():
                    return False, f"Path is not a file: {path}"
        
        # Check executable requirements
        if is_executable:
            # Check file extension
            executable_extensions = ['.exe', '.bat', '.cmd', '.com', '.ps1']
            if path_obj.suffix.lower() not in executable_extensions:
                return False, f"File does not have an executable extension: {path}"
            
            # If must_exist is True, we already checked it exists above
            # If must_exist is False, we just check the extension
            if must_exist and not path_obj.is_file():
                return False, f"Executable file does not exist: {path}"
        
        return True, ""
    
    @staticmethod
    def validate_number(
        value: Any,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        allow_int_only: bool = False
    ) -> Tuple[bool, str]:
        """
        Validate numeric value
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)
            allow_int_only: If True, only integers are allowed
            
        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        # Check if value is numeric
        try:
            if isinstance(value, str):
                # Try to parse string to number
                if allow_int_only or '.' not in value:
                    num_value = int(value)
                else:
                    num_value = float(value)
            elif isinstance(value, (int, float)):
                num_value = value
            else:
                return False, f"Value must be a number, got {type(value).__name__}"
        except (ValueError, TypeError) as e:
            return False, f"Invalid numeric value: {str(e)}"
        
        # Check integer requirement
        if allow_int_only and not isinstance(num_value, int):
            if isinstance(num_value, float) and not num_value.is_integer():
                return False, "Value must be an integer"
        
        # Check minimum value
        if min_val is not None and num_value < min_val:
            return False, f"Value must be at least {min_val}, got {num_value}"
        
        # Check maximum value
        if max_val is not None and num_value > max_val:
            return False, f"Value must be at most {max_val}, got {num_value}"
        
        return True, ""
    
    @staticmethod
    def validate_string(
        value: str,
        pattern: Optional[str] = None,
        min_length: int = 0,
        max_length: Optional[int] = None,
        allowed_values: Optional[List[str]] = None
    ) -> Tuple[bool, str]:
        """
        Validate string value
        
        Args:
            value: String value to validate
            pattern: Regex pattern the string must match
            min_length: Minimum string length
            max_length: Maximum string length
            allowed_values: List of allowed values (if specified, value must be in list)
            
        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        # Check if value is a string
        if not isinstance(value, str):
            return False, f"Value must be a string, got {type(value).__name__}"
        
        # Check minimum length
        if len(value) < min_length:
            return False, f"String must be at least {min_length} characters long"
        
        # Check maximum length
        if max_length is not None and len(value) > max_length:
            return False, f"String must be at most {max_length} characters long"
        
        # Check allowed values
        if allowed_values is not None and value not in allowed_values:
            return False, f"Value must be one of: {', '.join(allowed_values)}"
        
        # Check pattern
        if pattern is not None:
            try:
                if not re.match(pattern, value):
                    return False, f"String does not match required pattern"
            except re.error as e:
                return False, f"Invalid regex pattern: {str(e)}"
        
        return True, ""
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """
        Validate URL format
        
        Args:
            url: URL string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url or not url.strip():
            return False, "URL cannot be empty"
        
        try:
            result = urlparse(url)
            # Check if scheme and netloc are present
            if not all([result.scheme, result.netloc]):
                return False, "Invalid URL format (missing scheme or domain)"
            
            # Check if scheme is http or https
            if result.scheme not in ['http', 'https']:
                return False, "URL must use http or https protocol"
            
            return True, ""
        except Exception as e:
            return False, f"Invalid URL: {str(e)}"
    
    @staticmethod
    def validate_settings_dict(settings: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate entire settings dictionary against schema
        
        Args:
            settings: Dictionary of settings to validate
            schema: Schema dictionary defining validation rules
            
        Returns:
            Dictionary with validation results:
            {
                "valid": bool,
                "errors": {
                    "category.key": "error message",
                    ...
                },
                "warnings": {
                    "category.key": "warning message",
                    ...
                }
            }
        """
        result = {
            "valid": True,
            "errors": {},
            "warnings": {}
        }
        
        # Validate each category and setting
        for category, category_settings in settings.items():
            if category not in schema:
                result["warnings"][category] = f"Unknown category: {category}"
                continue
            
            category_schema = schema[category]
            
            for key, value in category_settings.items():
                if key not in category_schema:
                    result["warnings"][f"{category}.{key}"] = f"Unknown setting: {key}"
                    continue
                
                setting_schema = category_schema[key]
                full_key = f"{category}.{key}"
                
                # Validate based on type
                setting_type = setting_schema.get("type", "string")
                
                if setting_type == "string":
                    # Check for URL validation
                    if setting_schema.get("validation") == "url":
                        is_valid, error = ValidationService.validate_url(value)
                        if not is_valid:
                            result["valid"] = False
                            result["errors"][full_key] = error
                    else:
                        # Regular string validation
                        min_length = 1 if setting_schema.get("required", False) else 0
                        is_valid, error = ValidationService.validate_string(value, min_length=min_length)
                        if not is_valid:
                            result["valid"] = False
                            result["errors"][full_key] = error
                
                elif setting_type == "int":
                    min_val = setting_schema.get("min")
                    max_val = setting_schema.get("max")
                    is_valid, error = ValidationService.validate_number(
                        value, min_val=min_val, max_val=max_val, allow_int_only=True
                    )
                    if not is_valid:
                        result["valid"] = False
                        result["errors"][full_key] = error
                
                elif setting_type == "float":
                    min_val = setting_schema.get("min")
                    max_val = setting_schema.get("max")
                    is_valid, error = ValidationService.validate_number(
                        value, min_val=min_val, max_val=max_val, allow_int_only=False
                    )
                    if not is_valid:
                        result["valid"] = False
                        result["errors"][full_key] = error
                    
                    # Add warning if below recommended minimum
                    if min_val is not None and value < min_val:
                        result["warnings"][full_key] = f"Value is below recommended minimum of {min_val}"
                
                elif setting_type == "bool":
                    if not isinstance(value, bool):
                        result["valid"] = False
                        result["errors"][full_key] = f"Value must be boolean, got {type(value).__name__}"
                
                elif setting_type == "path":
                    # Path validation
                    file_type = setting_schema.get("file_type")
                    is_executable = file_type == "executable"
                    
                    # Allow empty paths if not required
                    if not value and not setting_schema.get("required", False):
                        continue
                    
                    is_valid, error = ValidationService.validate_path(
                        value,
                        must_exist=True,
                        is_directory=False,
                        is_executable=is_executable
                    )
                    if not is_valid:
                        result["valid"] = False
                        result["errors"][full_key] = error
        
        return result
