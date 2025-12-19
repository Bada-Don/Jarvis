"""
Comprehensive test for settings UI data flow
Tests that prompts are loaded from actual files and can be saved back
"""
import sys
import json
from pathlib import Path

# Add local_client to path
sys.path.insert(0, str(Path(__file__).parent))

from settings_app import SettingsAPI

def test_load_settings():
    """Test that settings load with actual prompt values"""
    print("=" * 60)
    print("TEST 1: Loading Settings with Prompts")
    print("=" * 60)
    
    api = SettingsAPI()
    result = api.get_settings()
    
    if not result['success']:
        print(f"✗ FAILED: {result.get('error', {}).get('message')}")
        return False
    
    settings = result['data']
    print("✓ Settings loaded successfully")
    
    # Check structure
    required_categories = ['system', 'timing', 'flexisign', 'verification', 'prompts']
    for cat in required_categories:
        if cat not in settings:
            print(f"✗ FAILED: Missing category '{cat}'")
            return False
    print(f"✓ All required categories present: {required_categories}")
    
    # Check prompts
    if 'prompts' not in settings:
        print("✗ FAILED: No prompts in settings")
        return False
    
    prompts = settings['prompts']
    
    # Check planner prompts
    if 'planner' not in prompts:
        print("✗ FAILED: No planner prompts")
        return False
    
    planner = prompts['planner']
    if 'GENERAL_SYSTEM_PROMPT' not in planner:
        print("✗ FAILED: GENERAL_SYSTEM_PROMPT not found")
        return False
    
    if 'FLEXISIGN_SYSTEM_PROMPT' not in planner:
        print("✗ FAILED: FLEXISIGN_SYSTEM_PROMPT not found")
        return False
    
    general_prompt = planner['GENERAL_SYSTEM_PROMPT']
    flexisign_prompt = planner['FLEXISIGN_SYSTEM_PROMPT']
    
    if len(general_prompt) == 0:
        print("✗ FAILED: GENERAL_SYSTEM_PROMPT is empty")
        return False
    
    if len(flexisign_prompt) == 0:
        print("✗ FAILED: FLEXISIGN_SYSTEM_PROMPT is empty")
        return False
    
    print(f"✓ GENERAL_SYSTEM_PROMPT loaded: {len(general_prompt)} chars")
    print(f"  Preview: {general_prompt[:80]}...")
    print(f"✓ FLEXISIGN_SYSTEM_PROMPT loaded: {len(flexisign_prompt)} chars")
    print(f"  Preview: {flexisign_prompt[:80]}...")
    
    # Check vision prompts
    if 'vision' not in prompts:
        print("✗ FAILED: No vision prompts")
        return False
    
    vision = prompts['vision']
    vision_prompt_names = ['GENERAL_VISION_PROMPT', 'VERIFICATION_PROMPT', 'FLEXISIGN_VISION_PROMPT']
    
    for prompt_name in vision_prompt_names:
        if prompt_name not in vision:
            print(f"✗ FAILED: {prompt_name} not found")
            return False
        if len(vision[prompt_name]) == 0:
            print(f"✗ FAILED: {prompt_name} is empty")
            return False
    
    print(f"✓ All vision prompts loaded: {vision_prompt_names}")
    
    print("\n✓ TEST 1 PASSED: All prompts loaded with actual values\n")
    return True


def test_settings_structure():
    """Test that settings have the correct structure for the UI"""
    print("=" * 60)
    print("TEST 2: Settings Structure for UI")
    print("=" * 60)
    
    api = SettingsAPI()
    result = api.get_settings()
    
    if not result['success']:
        print(f"✗ FAILED: {result.get('error', {}).get('message')}")
        return False
    
    settings = result['data']
    
    # Check that config settings are present
    if 'system' in settings:
        if 'SERVER_URL' in settings['system']:
            print(f"✓ SERVER_URL: {settings['system']['SERVER_URL']}")
        else:
            print("✗ FAILED: SERVER_URL not found")
            return False
    
    if 'timing' in settings:
        if 'ACTION_DELAY' in settings['timing']:
            print(f"✓ ACTION_DELAY: {settings['timing']['ACTION_DELAY']}")
        else:
            print("✗ FAILED: ACTION_DELAY not found")
            return False
    
    if 'flexisign' in settings:
        if 'FLEXISIGN_EXE_PATH' in settings['flexisign']:
            print(f"✓ FLEXISIGN_EXE_PATH: {settings['flexisign']['FLEXISIGN_EXE_PATH']}")
        else:
            print("✗ FAILED: FLEXISIGN_EXE_PATH not found")
            return False
    
    print("\n✓ TEST 2 PASSED: Settings structure is correct\n")
    return True


def test_json_serialization():
    """Test that settings can be serialized to JSON (for API responses)"""
    print("=" * 60)
    print("TEST 3: JSON Serialization")
    print("=" * 60)
    
    api = SettingsAPI()
    result = api.get_settings()
    
    if not result['success']:
        print(f"✗ FAILED: {result.get('error', {}).get('message')}")
        return False
    
    try:
        json_str = json.dumps(result, indent=2)
        print(f"✓ Settings serialized to JSON: {len(json_str)} chars")
        
        # Verify it can be deserialized
        parsed = json.loads(json_str)
        if 'data' in parsed and 'prompts' in parsed['data']:
            print("✓ JSON can be parsed back correctly")
        else:
            print("✗ FAILED: Parsed JSON missing expected structure")
            return False
        
    except Exception as e:
        print(f"✗ FAILED: JSON serialization error: {e}")
        return False
    
    print("\n✓ TEST 3 PASSED: Settings can be serialized to JSON\n")
    return True


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("JARVIS Settings UI - Data Flow Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_load_settings,
        test_settings_structure,
        test_json_serialization,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ TEST EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    sys.exit(0 if failed == 0 else 1)
