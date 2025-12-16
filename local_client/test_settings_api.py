"""
Basic tests for SettingsAPI to verify implementation

This is a simple test to ensure the API methods work correctly
without requiring the full PyWebView environment.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from settings_app import SettingsAPI


def test_api_initialization():
    """Test that the API can be initialized."""
    print("Testing API initialization...")
    try:
        api = SettingsAPI()
        print("  ✓ API initialized successfully")
        return True
    except Exception as e:
        print(f"  ✗ Failed to initialize API: {e}")
        return False


def test_get_settings():
    """Test getting settings."""
    print("\nTesting get_settings()...")
    try:
        api = SettingsAPI()
        result = api.get_settings()
        
        if result["success"]:
            print(f"  ✓ Successfully retrieved settings")
            print(f"    Categories: {list(result['data'].keys())}")
            return True
        else:
            print(f"  ✗ Failed to get settings: {result.get('error', {}).get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False


def test_validate_setting():
    """Test validating a setting."""
    print("\nTesting validate_setting()...")
    try:
        api = SettingsAPI()
        
        # Test valid string
        result = api.validate_setting("SERVER_URL", "http://localhost:5000")
        if result["success"] and result["valid"]:
            print("  ✓ Valid URL accepted")
        else:
            print(f"  ✗ Valid URL rejected: {result.get('error', 'Unknown error')}")
            return False
        
        # Test invalid URL
        result = api.validate_setting("SERVER_URL", "not-a-url")
        if result["success"] and not result["valid"]:
            print("  ✓ Invalid URL rejected")
        else:
            print(f"  ✗ Invalid URL accepted")
            return False
        
        # Test valid number
        result = api.validate_setting("ACTION_DELAY", 0.5)
        if result["success"] and result["valid"]:
            print("  ✓ Valid number accepted")
        else:
            print(f"  ✗ Valid number rejected: {result.get('error', 'Unknown error')}")
            return False
        
        # Test invalid number (out of range)
        result = api.validate_setting("ACTION_DELAY", -1.0)
        if result["success"] and not result["valid"]:
            print("  ✓ Out-of-range number rejected")
        else:
            print(f"  ✗ Out-of-range number accepted")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False


def test_get_prompts():
    """Test getting prompts."""
    print("\nTesting get_prompts()...")
    try:
        api = SettingsAPI()
        result = api.get_prompts()
        
        if result["success"]:
            print(f"  ✓ Successfully retrieved prompts")
            print(f"    Categories: {list(result['data'].keys())}")
            return True
        else:
            print(f"  ✗ Failed to get prompts: {result.get('error', {}).get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False


def test_reset_setting():
    """Test resetting a setting to default."""
    print("\nTesting reset_setting()...")
    try:
        api = SettingsAPI()
        
        # Test resetting a known setting
        result = api.reset_setting("ACTION_DELAY")
        if result["success"]:
            print(f"  ✓ Successfully reset ACTION_DELAY to {result['data']['value']}")
            return True
        else:
            print(f"  ✗ Failed to reset setting: {result.get('error', {}).get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False


def test_configuration_test():
    """Test the configuration testing functionality."""
    print("\nTesting test_configuration()...")
    try:
        api = SettingsAPI()
        result = api.test_configuration()
        
        if result["success"]:
            data = result["data"]
            summary = data.get("summary", {})
            print(f"  ✓ Configuration test completed")
            print(f"    Total tests: {summary.get('total_tests', 0)}")
            print(f"    Passed: {summary.get('passed_count', 0)}")
            print(f"    Failed: {summary.get('failed_count', 0)}")
            print(f"    Warnings: {summary.get('warning_count', 0)}")
            return True
        else:
            print(f"  ✗ Failed to test configuration: {result.get('error', {}).get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("JARVIS Settings API - Basic Tests")
    print("=" * 60)
    
    tests = [
        test_api_initialization,
        test_get_settings,
        test_validate_setting,
        test_get_prompts,
        test_reset_setting,
        test_configuration_test,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\nUnexpected error in {test.__name__}: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
