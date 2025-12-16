"""
Test script for the configuration testing API
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from settings_app import SettingsAPI

def test_configuration_api():
    """Test the test_configuration API method"""
    print("Testing Configuration API...")
    print("=" * 60)
    
    # Create API instance
    api = SettingsAPI()
    
    # Run configuration tests
    result = api.test_configuration()
    
    # Display results
    if result["success"]:
        data = result["data"]
        summary = data["summary"]
        
        print(f"\nTest Summary:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Passed: {summary['passed_count']}")
        print(f"  Failed: {summary['failed_count']}")
        print(f"  Warnings: {summary['warning_count']}")
        
        # Show passed tests
        if data["passed"]:
            print(f"\n✓ Passed Tests ({len(data['passed'])}):")
            for test in data["passed"]:
                print(f"  - {test['test']}: {test['message']}")
        
        # Show failed tests
        if data["failed"]:
            print(f"\n✗ Failed Tests ({len(data['failed'])}):")
            for test in data["failed"]:
                print(f"  - {test['test']}: {test['message']}")
                if test.get('guidance'):
                    print(f"    → {test['guidance']}")
        
        # Show warnings
        if data["warnings"]:
            print(f"\n⚠ Warnings ({len(data['warnings'])}):")
            for test in data["warnings"]:
                print(f"  - {test['test']}: {test['message']}")
        
        print("\n" + "=" * 60)
        if summary['failed_count'] == 0:
            print("✓ Configuration is valid!")
        else:
            print("✗ Configuration has issues that need to be fixed")
        
    else:
        print(f"Error: {result['error']['message']}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = test_configuration_api()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
