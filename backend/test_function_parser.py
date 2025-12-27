"""
Unit tests for Function Parser

Tests the parsing functionality for FunctionGemma output including:
- Function call extraction
- Argument parsing
- Type casting
- Edge cases and error handling
"""

import pytest
from function_parser import extract_function_calls, cast_argument_value, extract_tool_calls


class TestArgumentCasting:
    """Test argument value type casting."""
    
    def test_cast_integer(self):
        """Test casting string to integer."""
        assert cast_argument_value("123") == 123
        assert cast_argument_value("0") == 0
        assert cast_argument_value("-456") == -456
    
    def test_cast_float(self):
        """Test casting string to float."""
        assert cast_argument_value("45.67") == 45.67
        assert cast_argument_value("0.0") == 0.0
        assert cast_argument_value("-12.34") == -12.34
        assert cast_argument_value("3.14159") == 3.14159
    
    def test_cast_boolean(self):
        """Test casting string to boolean."""
        assert cast_argument_value("true") is True
        assert cast_argument_value("True") is True
        assert cast_argument_value("TRUE") is True
        assert cast_argument_value("false") is False
        assert cast_argument_value("False") is False
        assert cast_argument_value("FALSE") is False
    
    def test_cast_string(self):
        """Test that strings remain strings."""
        assert cast_argument_value("hello") == "hello"
        assert cast_argument_value("world") == "world"
        assert cast_argument_value("test123") == "test123"
    
    def test_cast_string_with_quotes(self):
        """Test stripping quotes from strings."""
        assert cast_argument_value("'quoted'") == "quoted"
        assert cast_argument_value('"double quoted"') == "double quoted"
        assert cast_argument_value("'single'") == "single"
    
    def test_cast_empty_string(self):
        """Test casting empty string."""
        assert cast_argument_value("") == ""
        assert cast_argument_value("''") == ""
        assert cast_argument_value('""') == ""
    
    def test_cast_whitespace(self):
        """Test casting strings with whitespace."""
        # Note: Whitespace is preserved in strings, only stripped during argument extraction
        assert cast_argument_value("  hello  ") == "  hello  "
        # Numbers with whitespace get stripped during extraction, so they cast correctly
        assert cast_argument_value("123") == 123


class TestFunctionCallExtraction:
    """Test extracting function calls from model output."""
    
    def test_extract_single_function_call(self):
        """Test extracting a single function call."""
        text = "<start_function_call>call:open_app{app_name:<escape>notepad<escape>}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["name"] == "open_app"
        assert calls[0]["arguments"] == {"app_name": "notepad"}
    
    def test_extract_multiple_function_calls(self):
        """Test extracting multiple function calls."""
        text = """
        <start_function_call>call:open_app{app_name:<escape>notepad<escape>}<end_function_call>
        <start_function_call>call:type_text{text:<escape>Hello World<escape>}<end_function_call>
        """
        calls = extract_function_calls(text)
        
        assert len(calls) == 2
        assert calls[0]["name"] == "open_app"
        assert calls[0]["arguments"] == {"app_name": "notepad"}
        assert calls[1]["name"] == "type_text"
        assert calls[1]["arguments"] == {"text": "Hello World"}
    
    def test_extract_function_with_multiple_arguments(self):
        """Test extracting function with multiple arguments."""
        text = "<start_function_call>call:click{x:100,y:200}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["name"] == "click"
        assert calls[0]["arguments"] == {"x": 100, "y": 200}
    
    def test_extract_function_with_mixed_types(self):
        """Test extracting function with mixed argument types."""
        text = "<start_function_call>call:test_func{name:<escape>test<escape>,count:5,enabled:true}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["name"] == "test_func"
        assert calls[0]["arguments"] == {
            "name": "test",
            "count": 5,
            "enabled": True
        }
    
    def test_extract_function_with_no_arguments(self):
        """Test extracting function with no arguments."""
        text = "<start_function_call>call:task_complete{}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["name"] == "task_complete"
        assert calls[0]["arguments"] == {}
    
    def test_extract_with_surrounding_text(self):
        """Test extracting function calls with surrounding text."""
        text = """
        I will help you with that.
        <start_function_call>call:open_app{app_name:<escape>notepad<escape>}<end_function_call>
        The application should now be open.
        """
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["name"] == "open_app"
    
    def test_extract_no_function_calls(self):
        """Test extracting from text with no function calls."""
        text = "This is just regular text without any function calls."
        calls = extract_function_calls(text)
        
        assert len(calls) == 0
    
    def test_extract_escaped_strings(self):
        """Test extracting function calls with escaped string values."""
        text = "<start_function_call>call:type_text{text:<escape>Hello, World!<escape>}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["arguments"]["text"] == "Hello, World!"
    
    def test_extract_multiline_arguments(self):
        """Test extracting function calls with multiline arguments."""
        text = """<start_function_call>call:type_text{text:<escape>Line 1
Line 2
Line 3<escape>}<end_function_call>"""
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert "Line 1" in calls[0]["arguments"]["text"]
        assert "Line 2" in calls[0]["arguments"]["text"]
        assert "Line 3" in calls[0]["arguments"]["text"]


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_malformed_function_call_missing_start(self):
        """Test handling malformed function call without start tag."""
        text = "call:open_app{app_name:<escape>notepad<escape>}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 0
    
    def test_malformed_function_call_missing_end(self):
        """Test handling malformed function call without end tag."""
        text = "<start_function_call>call:open_app{app_name:<escape>notepad<escape>}"
        calls = extract_function_calls(text)
        
        assert len(calls) == 0
    
    def test_malformed_function_call_missing_braces(self):
        """Test handling malformed function call without braces."""
        text = "<start_function_call>call:open_app<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 0
    
    def test_empty_string(self):
        """Test extracting from empty string."""
        calls = extract_function_calls("")
        assert len(calls) == 0
    
    def test_special_characters_in_arguments(self):
        """Test handling special characters in arguments."""
        text = "<start_function_call>call:type_text{text:<escape>Hello @#$%^&*()<escape>}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["arguments"]["text"] == "Hello @#$%^&*()"
    
    def test_nested_braces_in_escaped_string(self):
        """Test handling nested braces in escaped strings."""
        text = "<start_function_call>call:type_text{text:<escape>{nested: value}<escape>}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["arguments"]["text"] == "{nested: value}"
    
    def test_commas_in_escaped_string(self):
        """Test handling commas in escaped strings."""
        text = "<start_function_call>call:type_text{text:<escape>Hello, World, Test<escape>}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["arguments"]["text"] == "Hello, World, Test"
    
    def test_whitespace_in_arguments(self):
        """Test handling whitespace in arguments."""
        text = "<start_function_call>call:click{x: 100 , y: 200 }<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["arguments"]["x"] == 100
        assert calls[0]["arguments"]["y"] == 200
    
    def test_float_arguments(self):
        """Test handling float arguments."""
        text = "<start_function_call>call:move_mouse{x:100.5,y:200.75,duration:0.5}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["arguments"]["x"] == 100.5
        assert calls[0]["arguments"]["y"] == 200.75
        assert calls[0]["arguments"]["duration"] == 0.5
    
    def test_negative_numbers(self):
        """Test handling negative numbers."""
        text = "<start_function_call>call:test{value:-123,ratio:-45.67}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["arguments"]["value"] == -123
        assert calls[0]["arguments"]["ratio"] == -45.67


class TestBackwardCompatibility:
    """Test backward compatibility features."""
    
    def test_extract_tool_calls_alias(self):
        """Test that extract_tool_calls is an alias for extract_function_calls."""
        text = "<start_function_call>call:open_app{app_name:<escape>notepad<escape>}<end_function_call>"
        
        calls1 = extract_function_calls(text)
        calls2 = extract_tool_calls(text)
        
        assert calls1 == calls2


class TestRealWorldExamples:
    """Test with real-world examples from FunctionGemma."""
    
    def test_open_notepad_example(self):
        """Test parsing 'open notepad' command."""
        text = "<start_function_call>call:open_app{app_name:<escape>notepad<escape>}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["name"] == "open_app"
        assert calls[0]["arguments"]["app_name"] == "notepad"
    
    def test_create_folder_example(self):
        """Test parsing 'create folder' command."""
        text = "<start_function_call>call:create_folder{folder_name:<escape>Projects<escape>,location:<escape>desktop<escape>}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["name"] == "create_folder"
        assert calls[0]["arguments"]["folder_name"] == "Projects"
        assert calls[0]["arguments"]["location"] == "desktop"
    
    def test_save_file_example(self):
        """Test parsing 'save file' command."""
        text = "<start_function_call>call:save_file{filename:<escape>test.txt<escape>,location:<escape>desktop<escape>}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["name"] == "save_file"
        assert calls[0]["arguments"]["filename"] == "test.txt"
        assert calls[0]["arguments"]["location"] == "desktop"
    
    def test_multi_step_task_example(self):
        """Test parsing multi-step task."""
        text = """
        I'll help you with that task.
        <start_function_call>call:open_app{app_name:<escape>notepad<escape>}<end_function_call>
        Now I'll type the text.
        <start_function_call>call:type_text{text:<escape>Hello World<escape>}<end_function_call>
        Finally, I'll save the file.
        <start_function_call>call:save_file{filename:<escape>hello.txt<escape>}<end_function_call>
        <start_function_call>call:task_complete{}<end_function_call>
        """
        calls = extract_function_calls(text)
        
        assert len(calls) == 4
        assert calls[0]["name"] == "open_app"
        assert calls[1]["name"] == "type_text"
        assert calls[2]["name"] == "save_file"
        assert calls[3]["name"] == "task_complete"
    
    def test_keyboard_shortcut_example(self):
        """Test parsing keyboard shortcut command."""
        text = "<start_function_call>call:press_key{key:<escape>ctrl+s<escape>}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["name"] == "press_key"
        assert calls[0]["arguments"]["key"] == "ctrl+s"
    
    def test_mouse_click_example(self):
        """Test parsing mouse click command."""
        text = "<start_function_call>call:click{x:500,y:300}<end_function_call>"
        calls = extract_function_calls(text)
        
        assert len(calls) == 1
        assert calls[0]["name"] == "click"
        assert calls[0]["arguments"]["x"] == 500
        assert calls[0]["arguments"]["y"] == 300


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
