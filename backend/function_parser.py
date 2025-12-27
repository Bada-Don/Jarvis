"""
Function Call Parser for FunctionGemma Integration

This module provides parsing functionality for FunctionGemma model output.
It extracts function calls from the model's output format and casts arguments
to appropriate types.

Official FunctionGemma format:
<start_function_call>call:function_name{arg1:<escape>value<escape>,arg2:123}<end_function_call>
"""

import re
import logging
from typing import List, Dict, Union, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_function_calls(text: str) -> List[Dict[str, Any]]:
    """
    Extract function calls from FunctionGemma output.
    
    Uses the official FunctionGemma parsing pattern to extract function calls
    from model output. The pattern matches:
    <start_function_call>call:function_name{arg1:<escape>value<escape>,arg2:123}<end_function_call>
    
    Args:
        text: Model output text containing function calls
        
    Returns:
        List of dicts with 'name' and 'arguments' keys
        Example: [{"name": "open_app", "arguments": {"app_name": "notepad"}}]
        
    Raises:
        ValueError: If text is None or empty
        
    Examples:
        >>> text = "<start_function_call>call:open_app{app_name:<escape>notepad<escape>}<end_function_call>"
        >>> extract_function_calls(text)
        [{'name': 'open_app', 'arguments': {'app_name': 'notepad'}}]
        
        >>> text = "<start_function_call>call:click{x:100,y:200}<end_function_call>"
        >>> extract_function_calls(text)
        [{'name': 'click', 'arguments': {'x': 100, 'y': 200}}]
        
    Validates: Requirements 10.3 (Parsing error reporting for invalid function calls)
    """
    # Requirement 10.3: Validate input
    if text is None:
        error_msg = "Cannot parse function calls from None text"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if not text.strip():
        logger.warning("Empty text provided for function call extraction")
        return []
    
    # Log parsing attempt
    logger.debug(f"Parsing function calls from text (length: {len(text)})")
    
    # Extract function calls using official FunctionGemma regex pattern
    # Pattern: <start_function_call>call:function_name{arguments}<end_function_call>
    try:
        function_matches = re.findall(
            r"<start_function_call>call:(\w+)\{(.*?)\}<end_function_call>",
            text,
            re.DOTALL
        )
    except re.error as e:
        # Requirement 10.3: Report parsing errors with context
        error_msg = f"Regex parsing error: {str(e)}"
        logger.error(f"{error_msg} | Text: {text[:100]}...")
        raise ValueError(error_msg) from e
    
    if not function_matches:
        # Requirement 10.3: Report when no valid function calls found
        logger.warning(
            f"No valid function calls found in text. "
            f"Expected format: <start_function_call>call:function_name{{args}}<end_function_call>"
        )
        
        # Check for malformed function calls and provide helpful error messages
        if "<start_function_call>" in text:
            if "<end_function_call>" not in text:
                logger.error("Found <start_function_call> but missing <end_function_call>")
            elif "call:" not in text:
                logger.error("Found function call tags but missing 'call:' prefix")
            else:
                logger.error("Found function call tags but format is invalid")
        
        return []
    
    result = []
    
    for i, (function_name, args_string) in enumerate(function_matches, 1):
        logger.debug(f"Parsing function call {i}/{len(function_matches)}: {function_name}")
        
        try:
            # Parse arguments from the args_string
            # Pattern: key:value or key:<escape>value<escape>
            # Arguments are comma-separated
            arguments = {}
            
            # Extract all key-value pairs
            # Matches: key:<escape>value<escape> or key:value
            arg_matches = re.findall(
                r"(\w+):(?:<escape>(.*?)<escape>|([^,}]*))",
                args_string
            )
            
            if not arg_matches and args_string.strip():
                # Requirement 10.3: Report malformed arguments
                logger.warning(
                    f"Function '{function_name}' has malformed arguments: '{args_string}'. "
                    f"Expected format: key:value or key:<escape>value<escape>"
                )
            
            for key, escaped_value, unescaped_value in arg_matches:
                # Use escaped value if present, otherwise use unescaped value
                raw_value = (escaped_value or unescaped_value).strip()
                
                try:
                    # Cast the value to appropriate type
                    casted_value = cast_argument_value(raw_value)
                    arguments[key] = casted_value
                    logger.debug(f"  {key}: {raw_value} -> {casted_value} ({type(casted_value).__name__})")
                except Exception as e:
                    # Requirement 10.3: Report type casting errors with context
                    logger.error(
                        f"Failed to cast argument '{key}' with value '{raw_value}' "
                        f"for function '{function_name}': {str(e)}"
                    )
                    # Include the raw value as string fallback
                    arguments[key] = raw_value
            
            result.append({
                "name": function_name,
                "arguments": arguments
            })
            
            logger.info(f"✓ Parsed function call: {function_name} with {len(arguments)} argument(s)")
            
        except Exception as e:
            # Requirement 10.2: Log errors with context
            # Requirement 10.3: Report parsing errors
            logger.error(
                f"Error parsing function call {i} ('{function_name}'): {str(e)} | "
                f"Args string: '{args_string}'"
            )
            # Continue parsing other function calls
            continue
    
    logger.info(f"Successfully parsed {len(result)}/{len(function_matches)} function call(s)")
    return result


def cast_argument_value(value: str) -> Union[int, float, bool, str]:
    """
    Cast argument value to appropriate type.
    
    Attempts to cast string values to int, float, or bool. If all casting
    fails, returns the original string with quotes stripped.
    
    Args:
        value: String value to cast
        
    Returns:
        Casted value (int, float, bool, or str)
        
    Examples:
        >>> cast_argument_value("123")
        123
        
        >>> cast_argument_value("45.67")
        45.67
        
        >>> cast_argument_value("true")
        True
        
        >>> cast_argument_value("false")
        False
        
        >>> cast_argument_value("hello")
        'hello'
        
        >>> cast_argument_value("'quoted'")
        'quoted'
        
        >>> cast_argument_value('"double quoted"')
        'double quoted'
    """
    # Try to cast to int
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try to cast to float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Try to cast to boolean
    lower_value = value.lower()
    if lower_value == 'true':
        return True
    elif lower_value == 'false':
        return False
    
    # Return as string, stripping quotes if present
    return value.strip("'\"")


# Convenience function for backward compatibility
def extract_tool_calls(text: str) -> List[Dict[str, Any]]:
    """
    Alias for extract_function_calls for backward compatibility.
    
    Args:
        text: Model output text containing function calls
        
    Returns:
        List of dicts with 'name' and 'arguments' keys
    """
    return extract_function_calls(text)
