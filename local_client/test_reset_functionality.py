"""
Test script to verify reset functionality for settings interface.
Tests the reset_setting API method.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from settings_app import SettingsAPI


def test_reset_setting():
    """Test resetting a setting to its default value."""
    print("Testing reset_setting functionality...")
    print("=" * 60)
    
    # Initialize API
    api = SettingsAPI()
    
    # Test cases
    test_cases = [
        ("SERVER_URL", "http://localhost:5000"),
        ("ACTION_DELAY", 0.3),
        ("VERIFICATION_ENABLED", False),
        ("FLEXISIGN_PROCESS_NAME", "Production Suite Scanner 10.5.1 Build 1806 Protected"),
        ("WINDOW_ACTIVATION_ATTEMPTS", 3),
    ]
    
    print("\nTest Cases:")
    print("-" * 60)
    
    for key, expected_default in test_cases:
        print(f"\nTesting: {key}")
        print(f"Expected default: {expected_default}")
        
        # Call reset_setting
        result = api.reset_setting(key)
        
        if result["success"]:
            actual_value = result["data"]["value"]
            print(f"Actual default: {actual_value}")
            
            if actual_value == expected_default:
                print(f"✓ PASS: Default value matches")
            else:
                print(f"✗ FAIL: Default value mismatch")
                print(f"  Expected: {expected_default}")
                print(f"  Got: {actual_value}")
        else:
            print(f"✗ FAIL: API call failed")
            print(f"  Error: {result.get('error', {}).get('message', 'Unknown error')}")
    
    # Test invalid setting
    print("\n" + "-" * 60)
    print("\nTesting invalid setting:")
    result = api.reset_setting("INVALID_SETTING_NAME")
    
    if not result["success"]:
        print("✓ PASS: Invalid setting correctly rejected")
        print(f"  Error message: {result.get('error', {}).get('message', 'Unknown')}")
    else:
        print("✗ FAIL: Invalid setting should have been rejected")
    
    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == "__main__":
    try:
        test_reset_setting()
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
