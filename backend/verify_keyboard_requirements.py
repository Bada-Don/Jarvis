"""
Verification script to check that keyboard_operations module meets all requirements.

Requirements being verified:
- 5.1: type_text() function
- 5.2: press_key() function  
- 5.3: press_hotkey() function
- 5.4: press_key_repeat() with count validation
- 5.5: Appropriate delays for UI responsiveness
- 8.3: Reuse logic from PlanExecutor
"""

import sys
from pathlib import Path
import inspect

sys.path.insert(0, str(Path(__file__).parent / "functions"))

from keyboard_operations import (
    type_text,
    press_key,
    press_hotkey,
    press_key_repeat,
    DELAY_BEFORE_TYPING,
    DELAY_AFTER_HOTKEY,
    DELAY_AFTER_KEY,
    TYPING_INTERVAL,
    SPECIAL_KEYS,
    KEY_MAP,
    MODIFIER_KEYS
)


def verify_requirement_5_1():
    """Verify Requirement 5.1: type_text() function exists and uses pyautogui.typewrite()."""
    print("Requirement 5.1: THE System SHALL provide a function to type text strings")
    
    # Check function exists
    assert callable(type_text), "type_text function should exist"
    
    # Check function signature
    sig = inspect.signature(type_text)
    params = list(sig.parameters.keys())
    assert 'text' in params, "type_text should have 'text' parameter"
    assert 'interval' in params, "type_text should have 'interval' parameter"
    
    # Check source code mentions pyautogui.typewrite
    source = inspect.getsource(type_text)
    assert 'pyautogui.typewrite' in source, "type_text should use pyautogui.typewrite()"
    
    print("  ✓ type_text() function exists and uses pyautogui.typewrite()")
    return True


def verify_requirement_5_2():
    """Verify Requirement 5.2: press_key() function exists and uses pyautogui.press()."""
    print("Requirement 5.2: THE System SHALL provide a function to press individual keys")
    
    # Check function exists
    assert callable(press_key), "press_key function should exist"
    
    # Check function signature
    sig = inspect.signature(press_key)
    params = list(sig.parameters.keys())
    assert 'key' in params, "press_key should have 'key' parameter"
    
    # Check source code mentions pyautogui.press
    source = inspect.getsource(press_key)
    assert 'pyautogui.press' in source, "press_key should use pyautogui.press()"
    
    print("  ✓ press_key() function exists and uses pyautogui.press()")
    return True


def verify_requirement_5_3():
    """Verify Requirement 5.3: press_hotkey() function exists and uses pyautogui.hotkey()."""
    print("Requirement 5.3: THE System SHALL provide a function to execute keyboard shortcuts")
    
    # Check function exists
    assert callable(press_hotkey), "press_hotkey function should exist"
    
    # Check function signature
    sig = inspect.signature(press_hotkey)
    params = list(sig.parameters.keys())
    assert 'keys' in params, "press_hotkey should have 'keys' parameter"
    
    # Check source code mentions pyautogui.hotkey
    source = inspect.getsource(press_hotkey)
    assert 'pyautogui.hotkey' in source, "press_hotkey should use pyautogui.hotkey()"
    
    print("  ✓ press_hotkey() function exists and uses pyautogui.hotkey()")
    return True


def verify_requirement_5_4():
    """Verify Requirement 5.4: press_key_repeat() with count validation."""
    print("Requirement 5.4: THE System SHALL provide a function to press keys multiple times with a repeat parameter")
    
    # Check function exists
    assert callable(press_key_repeat), "press_key_repeat function should exist"
    
    # Check function signature
    sig = inspect.signature(press_key_repeat)
    params = list(sig.parameters.keys())
    assert 'key' in params, "press_key_repeat should have 'key' parameter"
    assert 'count' in params, "press_key_repeat should have 'count' parameter"
    
    # Check source code has validation
    source = inspect.getsource(press_key_repeat)
    assert 'isinstance(count, int)' in source, "Should validate count is integer"
    assert 'count <= 0' in source or 'count < 1' in source, "Should validate count is positive"
    
    print("  ✓ press_key_repeat() function exists with count validation")
    return True


def verify_requirement_5_5():
    """Verify Requirement 5.5: Appropriate delays for UI responsiveness."""
    print("Requirement 5.5: WHEN keyboard operations execute, THE System SHALL include appropriate delays for UI responsiveness")
    
    # Check timing constants exist
    assert DELAY_BEFORE_TYPING is not None, "DELAY_BEFORE_TYPING should be defined"
    assert DELAY_AFTER_HOTKEY is not None, "DELAY_AFTER_HOTKEY should be defined"
    assert DELAY_AFTER_KEY is not None, "DELAY_AFTER_KEY should be defined"
    assert TYPING_INTERVAL is not None, "TYPING_INTERVAL should be defined"
    
    # Check timing constants are reasonable
    assert 0 < DELAY_BEFORE_TYPING < 1, "DELAY_BEFORE_TYPING should be reasonable"
    assert 0 < DELAY_AFTER_HOTKEY < 2, "DELAY_AFTER_HOTKEY should be reasonable"
    assert 0 < DELAY_AFTER_KEY < 1, "DELAY_AFTER_KEY should be reasonable"
    assert 0 < TYPING_INTERVAL < 1, "TYPING_INTERVAL should be reasonable"
    
    # Check functions use delays
    type_text_source = inspect.getsource(type_text)
    assert 'time.sleep' in type_text_source, "type_text should include delays"
    assert 'DELAY_BEFORE_TYPING' in type_text_source, "type_text should use DELAY_BEFORE_TYPING"
    
    press_hotkey_source = inspect.getsource(press_hotkey)
    assert 'time.sleep' in press_hotkey_source, "press_hotkey should include delays"
    assert 'DELAY_AFTER_HOTKEY' in press_hotkey_source, "press_hotkey should use DELAY_AFTER_HOTKEY"
    
    print("  ✓ Appropriate delays are defined and used")
    return True


def verify_requirement_8_3():
    """Verify Requirement 8.3: Reuse logic from PlanExecutor."""
    print("Requirement 8.3: WHEN implementing keyboard operations, THE System SHALL reuse logic from the current PlanExecutor keyboard handling")
    
    # Check timing constants match PlanExecutor values
    assert DELAY_BEFORE_TYPING == 0.2, "DELAY_BEFORE_TYPING should match PlanExecutor (0.2)"
    assert DELAY_AFTER_HOTKEY == 0.5, "DELAY_AFTER_HOTKEY should match PlanExecutor (0.5)"
    
    # Check SPECIAL_KEYS is defined (reused from PlanExecutor)
    assert len(SPECIAL_KEYS) > 0, "SPECIAL_KEYS should be defined"
    assert 'enter' in SPECIAL_KEYS, "SPECIAL_KEYS should include 'enter'"
    assert 'escape' in SPECIAL_KEYS, "SPECIAL_KEYS should include 'escape'"
    assert 'tab' in SPECIAL_KEYS, "SPECIAL_KEYS should include 'tab'"
    
    # Check KEY_MAP is defined (reused from PlanExecutor)
    assert len(KEY_MAP) > 0, "KEY_MAP should be defined"
    assert 'ctrl' in KEY_MAP, "KEY_MAP should include 'ctrl'"
    assert 'win' in KEY_MAP, "KEY_MAP should include 'win'"
    assert 'alt' in KEY_MAP, "KEY_MAP should include 'alt'"
    
    # Check MODIFIER_KEYS is defined (reused from PlanExecutor)
    assert len(MODIFIER_KEYS) > 0, "MODIFIER_KEYS should be defined"
    assert 'ctrl' in MODIFIER_KEYS, "MODIFIER_KEYS should include 'ctrl'"
    assert 'alt' in MODIFIER_KEYS, "MODIFIER_KEYS should include 'alt'"
    
    print("  ✓ Logic reused from PlanExecutor (timing constants, key mappings)")
    return True


def main():
    print("=" * 70)
    print("Keyboard Operations Module - Requirements Verification")
    print("=" * 70)
    print()
    
    results = []
    
    try:
        results.append(("5.1", verify_requirement_5_1()))
        print()
        results.append(("5.2", verify_requirement_5_2()))
        print()
        results.append(("5.3", verify_requirement_5_3()))
        print()
        results.append(("5.4", verify_requirement_5_4()))
        print()
        results.append(("5.5", verify_requirement_5_5()))
        print()
        results.append(("8.3", verify_requirement_8_3()))
        print()
        
        print("=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)
        
        all_passed = all(result[1] for result in results)
        
        for req_id, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"Requirement {req_id}: {status}")
        
        print()
        if all_passed:
            print("✅ ALL REQUIREMENTS VERIFIED")
            return 0
        else:
            print("❌ SOME REQUIREMENTS FAILED")
            return 1
            
    except AssertionError as e:
        print(f"\n❌ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
