"""
Function Call Parser for FunctionGemma Integration

This module provides parsing functionality for FunctionGemma model output.
It extracts function calls from the model's output format and casts arguments
to appropriate types.

Official FunctionGemma format:
<start_function_call>call:function_name{arg1:<escape>value<escape>,arg2:123}<end_function_call>
"""

import re
from typing import List, Dict, Union, Any


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
        
    Examples:
        >>> text = "<start_function_call>call:open_app{app_name:<escape>notepad<escape>}<end_function_call>"
        >>> extract_function_calls(text)
        [{'name': 'open_app', 'arguments': {'app_name': 'notepad'}}]
        
        >>> text = "<start_function_call>call:click{x:100,y:200}<end_function_call>"
        >>> extract_function_calls(text)
        [{'name': 'click', 'arguments': {'x': 100, 'y': 200}}]
    """
    # Extract function calls using official FunctionGemma regex pattern
    # Pattern: <start_function_call>call:function_name{arguments}<end_function_call>
    function_matches = re.findall(
        r"<start_function_call>call:(\w+)\{(.*?)\}<end_function_call>",
        text,
        re.DOTALL
    )
    
    result = []
    
    for function_name, args_string in function_matches:
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
        
        for key, escaped_value, unescaped_value in arg_matches:
            # Use escaped value if present, otherwise use unescaped value
            raw_value = (escaped_value or unescaped_value).strip()
            
            # Cast the value to appropriate type
            casted_value = cast_argument_value(raw_value)
            arguments[key] = casted_value
        
        result.append({
            "name": function_name,
            "arguments": arguments
        })
    
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
