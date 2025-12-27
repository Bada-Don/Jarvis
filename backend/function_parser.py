"""
Function Call Parser for FunctionGemma

This module provides functions to parse FunctionGemma model output and extract
function calls with their arguments. Uses the official FunctionGemma parsing pattern.
"""

import re
from typing import List, Dict, Union


def cast_argument_value(value: str) -> Union[int, float, bool, str]:
    """
    Cast argument value to appropriate type.
    
    Attempts to cast string values to int, float, or bool.
    Returns the original string if casting fails.
    
    Args:
        value: String value to cast
        
    Returns:
        Casted value (int, float, bool, or str)
    
    Examples:
        >>> cast_argument_value("123")
        123
        >>> cast_argument_value("3.14")
        3.14
        >>> cast_argument_value("true")
        True
        >>> cast_argument_value("hello")
        'hello'
    """
    # Try integer
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Try boolean
    lower_value = value.lower()
    if lower_value == 'true':
        return True
    elif lower_value == 'false':
        return False
    
    # Return as string, stripping quotes if present
    return value.strip("'\"")


def extract_function_calls(text: str) -> List[Dict]:
    """
    Extract function calls from FunctionGemma output.
    
    Uses the official FunctionGemma parsing pattern:
    <start_function_call>call:function_name{arg1:<escape>value<escape>,arg2:123}<end_function_call>
    
    Args:
        text: Model output text containing function calls
        
    Returns:
        List of dicts with 'name' and 'arguments' keys
        
    Examples:
        >>> text = '<start_function_call>call:open_app{app_name:<escape>notepad<escape>}<end_function_call>'
        >>> extract_function_calls(text)
        [{'name': 'open_app', 'arguments': {'app_name': 'notepad'}}]
    """
    # Find all function calls using regex
    # Pattern: <start_function_call>call:function_name{arguments}<end_function_call>
    function_calls = []
    
    pattern = r"<start_function_call>call:(\w+)\{(.*?)\}<end_function_call>"
    matches = re.findall(pattern, text, re.DOTALL)
    
    for function_name, args_str in matches:
        # Parse arguments
        arguments = {}
        
        if args_str.strip():
            # Pattern for arguments: key:<escape>value<escape> or key:value
            arg_pattern = r"(\w+):(?:<escape>(.*?)<escape>|([^,}]*))"
            arg_matches = re.findall(arg_pattern, args_str)
            
            for key, escaped_value, unescaped_value in arg_matches:
                # Use escaped value if present, otherwise unescaped
                value = escaped_value if escaped_value else unescaped_value
                value = value.strip()
                
                # Cast to appropriate type
                arguments[key] = cast_argument_value(value)
        
        function_calls.append({
            "name": function_name,
            "arguments": arguments
        })
    
    return function_calls
