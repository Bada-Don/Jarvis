"""
Unit tests for keyboard operations module.

Tests the keyboard operation functions including type_text, press_key,
press_hotkey, and press_key_repeat.

Note: These tests validate parameter checking and function logic without
actually executing keyboard automation to avoid interfering with the system.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the functions directory to the path
sys.path.insert(0, str(Path(__file__).parent / "functions"))

from keyboard_operations import (
    type_text,
    press_key,
    press_hotkey,
    press_key_repeat,
    _is_special_key,
    _is_hotkey,
    DELAY_BEFORE_TYPING,
    DELAY_AFTER_HOTKEY,
    SPECIAL_KEYS,
    KEY_MAP
)


def test_type_text_success():
    """Test typing text successfully."""
    with patch('keyboard_operations.pyautogui.typewrite') as mock_typewrite:
        with patch('keyboard_operations.time.sleep'):
            result = type_text("Hello World")
            
            assert result["success"] is True, f"Failed to type text: {result['message']}"
            assert result["text"] == "Hello World"
            assert result["length"] == 11
            assert "11 characters" in result["message"]
            
            # Verify pyautogui.typewrite was called
            mock_typewrite.assert_called_once()
            
    print("✓ test_type_text_success passed")


def test_type_text_empty_string():
    """Test typing empty string (should succeed)."""
    with patch('keyboard_operations.pyautogui.typewrite') as mock_typewrite:
        with patch('keyboard_operations.time.sleep'):
            result = type_text("")
            
            assert result["success"] is True, "Should succeed with empty string"
            assert result["text"] == ""
            assert result["length"] == 0
            
            mock_typewrite.assert_called_once()
            
    print("✓ test_type_text_empty_string passed")


def test_type_text_none():
    """Test typing None text."""
    result = type_text(None)
    assert result["success"] is False, "Should fail with None text"
    assert "cannot be None" in result["message"]
    assert result["text"] is None
    
    print("✓ test_type_text_none passed")


def test_type_text_custom_interval():
    """Test typing with custom interval."""
    with patch('keyboard_operations.pyautogui.typewrite') as mock_typewrite:
        with patch('keyboard_operations.time.sleep'):
            result = type_text("test", interval=0.1)
            
            assert result["success"] is True
            
            # Verify interval was passed to typewrite
            call_args = mock_typewrite.call_args
            assert call_args[1]['interval'] == 0.1
            
    print("✓ test_type_text_custom_interval passed")


def test_type_text_negative_interval():
    """Test typing with negative interval."""
    result = type_text("test", interval=-1)
    assert result["success"] is False, "Should fail with negative interval"
    assert "non-negative" in result["message"]
    
    print("✓ test_type_text_negative_interval passed")


def test_press_key_success():
    """Test pressing a key successfully."""
    with patch('keyboard_operations.pyautogui.press') as mock_press:
        with patch('keyboard_operations.time.sleep'):
            result = press_key("enter")
            
            assert result["success"] is True, f"Failed to press key: {result['message']}"
            assert result["key"] == "enter"
            assert result["is_special"] is True
            
            # Verify pyautogui.press was called with lowercase key
            mock_press.assert_called_once_with("enter")
            
    print("✓ test_press_key_success passed")


def test_press_key_regular_key():
    """Test pressing a regular key."""
    with patch('keyboard_operations.pyautogui.press') as mock_press:
        with patch('keyboard_operations.time.sleep'):
            result = press_key("a")
            
            assert result["success"] is True
            assert result["key"] == "a"
            assert result["is_special"] is False
            
            mock_press.assert_called_once_with("a")
            
    print("✓ test_press_key_regular_key passed")


def test_press_key_empty():
    """Test pressing empty key."""
    result = press_key("")
    assert result["success"] is False, "Should fail with empty key"
    assert "cannot be empty" in result["message"]
    
    print("✓ test_press_key_empty passed")


def test_press_key_whitespace():
    """Test pressing whitespace key."""
    result = press_key("   ")
    assert result["success"] is False, "Should fail with whitespace key"
    assert "cannot be empty" in result["message"]
    
    print("✓ test_press_key_whitespace passed")


def test_press_hotkey_success():
    """Test pressing a hotkey successfully."""
    with patch('keyboard_operations.pyautogui.hotkey') as mock_hotkey:
        with patch('keyboard_operations.time.sleep'):
            result = press_hotkey("ctrl+c")
            
            assert result["success"] is True, f"Failed to press hotkey: {result['message']}"
            assert result["hotkey"] == "ctrl+c"
            assert result["keys"] == ["ctrl", "c"]
            
            # Verify pyautogui.hotkey was called with correct keys
            mock_hotkey.assert_called_once_with("ctrl", "c")
            
    print("✓ test_press_hotkey_success passed")


def test_press_hotkey_multiple_modifiers():
    """Test pressing hotkey with multiple modifiers."""
    with patch('keyboard_operations.pyautogui.hotkey') as mock_hotkey:
        with patch('keyboard_operations.time.sleep'):
            result = press_hotkey("ctrl+shift+s")
            
            assert result["success"] is True
            assert result["keys"] == ["ctrl", "shift", "s"]
            
            mock_hotkey.assert_called_once_with("ctrl", "shift", "s")
            
    print("✓ test_press_hotkey_multiple_modifiers passed")


def test_press_hotkey_key_mapping():
    """Test hotkey with key mapping (win -> win, ctrl -> ctrl)."""
    with patch('keyboard_operations.pyautogui.hotkey') as mock_hotkey:
        with patch('keyboard_operations.time.sleep'):
            result = press_hotkey("win+r")
            
            assert result["success"] is True
            assert result["keys"] == ["win", "r"]
            
            mock_hotkey.assert_called_once_with("win", "r")
            
    print("✓ test_press_hotkey_key_mapping passed")


def test_press_hotkey_empty():
    """Test pressing empty hotkey."""
    result = press_hotkey("")
    assert result["success"] is False, "Should fail with empty hotkey"
    assert "cannot be empty" in result["message"]
    
    print("✓ test_press_hotkey_empty passed")


def test_press_hotkey_no_modifier():
    """Test pressing hotkey without modifier key."""
    result = press_hotkey("a+b")
    assert result["success"] is False, "Should fail without modifier key"
    assert "not a valid hotkey" in result["message"]
    assert "modifier key" in result["message"]
    
    print("✓ test_press_hotkey_no_modifier passed")


def test_press_key_repeat_success():
    """Test repeating key press successfully."""
    with patch('keyboard_operations.pyautogui.press') as mock_press:
        with patch('keyboard_operations.time.sleep'):
            result = press_key_repeat("down", 5)
            
            assert result["success"] is True, f"Failed to repeat key: {result['message']}"
            assert result["key"] == "down"
            assert result["count"] == 5
            assert result["actual_count"] == 5
            assert result["is_special"] is True
            
            # Verify pyautogui.press was called 5 times
            assert mock_press.call_count == 5
            
    print("✓ test_press_key_repeat_success passed")


def test_press_key_repeat_single():
    """Test repeating key press once."""
    with patch('keyboard_operations.pyautogui.press') as mock_press:
        with patch('keyboard_operations.time.sleep'):
            result = press_key_repeat("a", 1)
            
            assert result["success"] is True
            assert result["count"] == 1
            assert result["actual_count"] == 1
            
            mock_press.assert_called_once()
            
    print("✓ test_press_key_repeat_single passed")


def test_press_key_repeat_empty_key():
    """Test repeating with empty key."""
    result = press_key_repeat("", 5)
    assert result["success"] is False, "Should fail with empty key"
    assert "cannot be empty" in result["message"]
    
    print("✓ test_press_key_repeat_empty_key passed")


def test_press_key_repeat_zero_count():
    """Test repeating with zero count."""
    result = press_key_repeat("a", 0)
    assert result["success"] is False, "Should fail with zero count"
    assert "must be positive" in result["message"]
    
    print("✓ test_press_key_repeat_zero_count passed")


def test_press_key_repeat_negative_count():
    """Test repeating with negative count."""
    result = press_key_repeat("a", -5)
    assert result["success"] is False, "Should fail with negative count"
    assert "must be positive" in result["message"]
    
    print("✓ test_press_key_repeat_negative_count passed")


def test_press_key_repeat_non_integer_count():
    """Test repeating with non-integer count."""
    result = press_key_repeat("a", "5")
    assert result["success"] is False, "Should fail with non-integer count"
    assert "must be an integer" in result["message"]
    
    print("✓ test_press_key_repeat_non_integer_count passed")


def test_press_key_repeat_excessive_count():
    """Test repeating with excessive count."""
    result = press_key_repeat("a", 10000)
    assert result["success"] is False, "Should fail with excessive count"
    assert "exceeds maximum" in result["message"]
    
    print("✓ test_press_key_repeat_excessive_count passed")


def test_is_special_key():
    """Test _is_special_key helper function."""
    assert _is_special_key("enter") is True
    assert _is_special_key("ENTER") is True
    assert _is_special_key("escape") is True
    assert _is_special_key("f1") is True
    assert _is_special_key("a") is False
    assert _is_special_key("ctrl") is False
    
    print("✓ test_is_special_key passed")


def test_is_hotkey():
    """Test _is_hotkey helper function."""
    assert _is_hotkey("ctrl+c") is True
    assert _is_hotkey("alt+tab") is True
    assert _is_hotkey("ctrl+shift+s") is True
    assert _is_hotkey("win+r") is True
    assert _is_hotkey("a+b") is False
    assert _is_hotkey("enter") is False
    
    print("✓ test_is_hotkey passed")


def test_constants():
    """Test that constants are properly defined."""
    assert DELAY_BEFORE_TYPING == 0.2
    assert DELAY_AFTER_HOTKEY == 0.5
    assert len(SPECIAL_KEYS) > 0
    assert len(KEY_MAP) > 0
    assert 'enter' in SPECIAL_KEYS
    assert 'ctrl' in KEY_MAP
    
    print("✓ test_constants passed")


def test_timing_reuse():
    """Test that timing constants match PlanExecutor values."""
    # These values should match PlanExecutor timing constants
    assert DELAY_BEFORE_TYPING == 0.2, "DELAY_BEFORE_TYPING should match PlanExecutor"
    assert DELAY_AFTER_HOTKEY == 0.5, "DELAY_AFTER_HOTKEY should match PlanExecutor"
    
    print("✓ test_timing_reuse passed")


def test_key_mapping_reuse():
    """Test that key mapping matches PlanExecutor."""
    # These mappings should match PlanExecutor
    assert KEY_MAP['ctrl'] == 'ctrl'
    assert KEY_MAP['win'] == 'win'
    assert KEY_MAP['alt'] == 'alt'
    assert KEY_MAP['shift'] == 'shift'
    
    print("✓ test_key_mapping_reuse passed")


if __name__ == "__main__":
    print("Running keyboard operations tests...\n")
    
    try:
        test_type_text_success()
        test_type_text_empty_string()
        test_type_text_none()
        test_type_text_custom_interval()
        test_type_text_negative_interval()
        test_press_key_success()
        test_press_key_regular_key()
        test_press_key_empty()
        test_press_key_whitespace()
        test_press_hotkey_success()
        test_press_hotkey_multiple_modifiers()
        test_press_hotkey_key_mapping()
        test_press_hotkey_empty()
        test_press_hotkey_no_modifier()
        test_press_key_repeat_success()
        test_press_key_repeat_single()
        test_press_key_repeat_empty_key()
        test_press_key_repeat_zero_count()
        test_press_key_repeat_negative_count()
        test_press_key_repeat_non_integer_count()
        test_press_key_repeat_excessive_count()
        test_is_special_key()
        test_is_hotkey()
        test_constants()
        test_timing_reuse()
        test_key_mapping_reuse()
        
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
