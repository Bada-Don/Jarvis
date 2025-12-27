"""
Keyboard Operations Module

Provides functions for keyboard automation including typing text, pressing keys,
executing hotkeys, and repeating key presses. Reuses timing constants and key
mapping logic from PlanExecutor.

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 8.3
"""

import time
from typing import Dict

import pyautogui


# Timing configuration (reused from PlanExecutor)
# Requirements: 5.5, 8.3
DELAY_BEFORE_TYPING = 0.2       # Small delay before typing text
DELAY_AFTER_HOTKEY = 0.5        # Delay after hotkey combinations
DELAY_AFTER_KEY = 0.05          # Minimal delay after single key press
TYPING_INTERVAL = 0.03          # Interval between characters when typing


# Special key names (reused from PlanExecutor)
# Requirements: 5.2, 8.3
SPECIAL_KEYS = {
    'enter', 'return', 'tab', 'space', 'backspace', 'delete', 'del',
    'escape', 'esc', 'up', 'down', 'left', 'right',
    'home', 'end', 'pageup', 'pagedown', 'pgup', 'pgdn',
    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
    'insert', 'pause', 'capslock', 'numlock', 'scrolllock',
    'printscreen', 'prtsc', 'prtscr', 'win', 'windows', 'command', 'cmd'
}


# Key mapping for hotkeys (reused from PlanExecutor)
# Requirements: 5.3, 8.3
KEY_MAP = {
    'win': 'win',
    'windows': 'win',
    'super': 'win',
    'cmd': 'command',
    'ctrl': 'ctrl',
    'control': 'ctrl',
    'alt': 'alt',
    'shift': 'shift',
}


# Modifier keys for hotkey detection (reused from PlanExecutor)
# Requirements: 5.3, 8.3
MODIFIER_KEYS = {'ctrl', 'alt', 'shift', 'win', 'cmd', 'command', 'meta', 'super', 'windows'}


def _is_special_key(key: str) -> bool:
    """
    Check if a key is a special key name.
    
    Reused from PlanExecutor._is_special_key()
    
    Args:
        key: Key name to check
        
    Returns:
        True if key is a special key
        
    Requirements: 8.3
    """
    return key.lower() in SPECIAL_KEYS


def _is_hotkey(value: str) -> bool:
    """
    Check if value is a hotkey combination vs regular text with '+'.
    
    Reused from PlanExecutor._is_hotkey()
    
    Args:
        value: String to check
        
    Returns:
        True if value is a hotkey combination
        
    Requirements: 8.3
    """
    parts = value.lower().split('+')
    return any(part.strip() in MODIFIER_KEYS for part in parts)


def type_text(text: str, interval: float = None) -> Dict[str, any]:
    """
    Type a text string using keyboard automation.
    
    Uses: pyautogui.typewrite()
    Reuses: Timing logic from PlanExecutor (DELAY_BEFORE_TYPING, TYPING_INTERVAL)
    
    Args:
        text: Text to type
        interval: Optional delay between keystrokes (defaults to TYPING_INTERVAL)
        
    Returns:
        {"success": bool, "message": str, "text": str, "length": int}
        
    Requirements: 5.1, 5.5, 8.3
    """
    try:
        if text is None:
            return {
                "success": False,
                "message": "Text cannot be None",
                "text": None,
                "length": 0
            }
        
        # Allow empty strings (user might want to clear a field)
        text_str = str(text)
        
        # Use default interval if not specified
        if interval is None:
            interval = TYPING_INTERVAL
        
        # Validate interval
        if interval < 0:
            return {
                "success": False,
                "message": f"Interval must be non-negative, got: {interval}",
                "text": text_str,
                "length": len(text_str)
            }
        
        # Small delay before typing (reused from PlanExecutor)
        time.sleep(DELAY_BEFORE_TYPING)
        
        # Type the text using pyautogui
        pyautogui.typewrite(text_str, interval=interval)
        
        return {
            "success": True,
            "message": f"Typed {len(text_str)} characters successfully",
            "text": text_str,
            "length": len(text_str)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to type text: {str(e)}",
            "text": text_str if 'text_str' in locals() else None,
            "length": 0
        }


def press_key(key: str) -> Dict[str, any]:
    """
    Press a single key.
    
    Uses: pyautogui.press()
    Reuses: Key mapping from PlanExecutor (SPECIAL_KEYS)
    
    Args:
        key: Key name (e.g., 'enter', 'escape', 'a', 'F1')
        
    Returns:
        {"success": bool, "message": str, "key": str, "is_special": bool}
        
    Requirements: 5.2, 5.5, 8.3
    """
    try:
        if not key or not key.strip():
            return {
                "success": False,
                "message": "Key cannot be empty",
                "key": None,
                "is_special": False
            }
        
        key_lower = key.strip().lower()
        is_special = _is_special_key(key_lower)
        
        # Press the key using pyautogui
        pyautogui.press(key_lower)
        
        # Small delay after key press
        time.sleep(DELAY_AFTER_KEY)
        
        return {
            "success": True,
            "message": f"Pressed key '{key}' successfully",
            "key": key,
            "is_special": is_special
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to press key: {str(e)}",
            "key": key if 'key' in locals() else None,
            "is_special": False
        }


def press_hotkey(keys: str) -> Dict[str, any]:
    """
    Execute a keyboard shortcut (hotkey combination).
    
    Uses: pyautogui.hotkey()
    Reuses: Hotkey parsing from PlanExecutor (KEY_MAP, MODIFIER_KEYS)
    
    Args:
        keys: Hotkey combination (e.g., 'ctrl+c', 'alt+tab', 'ctrl+shift+s')
        
    Returns:
        {"success": bool, "message": str, "hotkey": str, "keys": list}
        
    Requirements: 5.3, 5.5, 8.3
    """
    try:
        if not keys or not keys.strip():
            return {
                "success": False,
                "message": "Hotkey cannot be empty",
                "hotkey": None,
                "keys": []
            }
        
        # Check if this is actually a hotkey combination
        if not _is_hotkey(keys):
            return {
                "success": False,
                "message": f"'{keys}' is not a valid hotkey combination (must contain a modifier key)",
                "hotkey": keys,
                "keys": []
            }
        
        # Parse and map keys (reused from PlanExecutor._execute_hotkey)
        key_parts = [k.strip().lower() for k in keys.split('+')]
        mapped_keys = [KEY_MAP.get(k, k) for k in key_parts]
        
        # Execute the hotkey using pyautogui
        pyautogui.hotkey(*mapped_keys)
        
        # Delay after hotkey (reused from PlanExecutor)
        time.sleep(DELAY_AFTER_HOTKEY)
        
        return {
            "success": True,
            "message": f"Executed hotkey '{keys}' successfully",
            "hotkey": keys,
            "keys": mapped_keys
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to execute hotkey: {str(e)}",
            "hotkey": keys if 'keys' in locals() else None,
            "keys": []
        }


def press_key_repeat(key: str, count: int) -> Dict[str, any]:
    """
    Press a key multiple times.
    
    Uses: pyautogui.press() in a loop
    Reuses: Key mapping from PlanExecutor
    
    Args:
        key: Key name to press
        count: Number of times to press the key (must be positive)
        
    Returns:
        {"success": bool, "message": str, "key": str, "count": int, "actual_count": int}
        
    Requirements: 5.4, 5.5, 8.3
    """
    try:
        if not key or not key.strip():
            return {
                "success": False,
                "message": "Key cannot be empty",
                "key": None,
                "count": count,
                "actual_count": 0
            }
        
        # Validate count parameter
        if not isinstance(count, int):
            return {
                "success": False,
                "message": f"Count must be an integer, got: {type(count).__name__}",
                "key": key,
                "count": count,
                "actual_count": 0
            }
        
        if count <= 0:
            return {
                "success": False,
                "message": f"Count must be positive, got: {count}",
                "key": key,
                "count": count,
                "actual_count": 0
            }
        
        # Limit count to prevent accidental infinite loops
        MAX_REPEAT_COUNT = 1000
        if count > MAX_REPEAT_COUNT:
            return {
                "success": False,
                "message": f"Count exceeds maximum allowed ({MAX_REPEAT_COUNT}), got: {count}",
                "key": key,
                "count": count,
                "actual_count": 0
            }
        
        key_lower = key.strip().lower()
        is_special = _is_special_key(key_lower)
        
        # Press the key multiple times
        for i in range(count):
            pyautogui.press(key_lower)
            
            # Small delay between presses (except for the last one)
            if i < count - 1:
                time.sleep(0.1)
        
        # Final delay after all presses
        time.sleep(DELAY_AFTER_KEY)
        
        return {
            "success": True,
            "message": f"Pressed key '{key}' {count} times successfully",
            "key": key,
            "count": count,
            "actual_count": count,
            "is_special": is_special
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to repeat key press: {str(e)}",
            "key": key if 'key' in locals() else None,
            "count": count if 'count' in locals() else 0,
            "actual_count": 0
        }
