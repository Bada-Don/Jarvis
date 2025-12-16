"""
Manual test script for configuration profile export/import functionality.
This script tests the export_config and import_config methods.
"""

import os
import json
import tempfile
from pathlib import Path
from settings_app import SettingsAPI

def test_export_import():
    """Test export and import configuration functionality"""
    print("Testing Configuration Profile Export/Import...")
    print("=" * 60)
    
    # Initialize API
    api = SettingsAPI()
    
    # Test 1: Export configuration
    print("\n1. Testing Export Configuration...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        export_path = tmp_file.name
    
    try:
        result = api.export_config(export_path)
        
        if result["success"]:
            print(f"   ✓ Export successful: {export_path}")
            
            # Verify file exists and has content
            if os.path.exists(export_path):
                with open(export_path, 'r') as f:
                    data = json.load(f)
                
                # Check structure
                if "metadata" in data and "settings" in data and "prompts" in data:
                    print("   ✓ Export file has correct structure")
                    print(f"   - Export date: {data['metadata'].get('export_date')}")
                    print(f"   - Version: {data['metadata'].get('version')}")
                    print(f"   - Configuration name: {data['metadata'].get('configuration_name')}")
                    print(f"   - Settings categories: {list(data['settings'].keys())}")
                    print(f"   - Prompt categories: {list(data['prompts'].keys())}")
                else:
                    print("   ✗ Export file structure is invalid")
                    return False
            else:
                print("   ✗ Export file was not created")
                return False
        else:
            print(f"   ✗ Export failed: {result.get('error', {}).get('message')}")
            return False
        
        # Test 2: Import configuration
        print("\n2. Testing Import Configuration...")
        result = api.import_config(export_path)
        
        if result["success"]:
            print("   ✓ Import successful")
            
            if result.get("warnings"):
                print(f"   ⚠ Warnings: {len(result['warnings'])}")
                for warning in result["warnings"]:
                    print(f"     - {warning}")
            else:
                print("   ✓ No warnings")
        else:
            print(f"   ✗ Import failed: {result.get('error', {}).get('message')}")
            return False
        
        # Test 3: Import invalid configuration
        print("\n3. Testing Import with Invalid Configuration...")
        invalid_config = {
            "metadata": {
                "export_date": "2024-01-01",
                "version": "1.0",
                "configuration_name": "invalid_test"
            },
            "settings": {
                "system": {
                    "SERVER_URL": "not-a-valid-url",  # Invalid URL
                    "WINDOWS_USERNAME": "test_user"
                },
                "timing": {
                    "ACTION_DELAY": -1.0,  # Invalid: negative value
                }
            },
            "prompts": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            invalid_path = tmp_file.name
            json.dump(invalid_config, tmp_file)
        
        try:
            result = api.import_config(invalid_path)
            
            if result["success"]:
                if result.get("warnings"):
                    print(f"   ✓ Import handled invalid settings correctly")
                    print(f"   ⚠ Warnings: {len(result['warnings'])}")
                    for warning in result["warnings"][:3]:  # Show first 3 warnings
                        print(f"     - {warning}")
                else:
                    print("   ⚠ Import succeeded but no warnings for invalid settings")
            else:
                print(f"   ✓ Import correctly rejected invalid configuration")
        finally:
            if os.path.exists(invalid_path):
                os.unlink(invalid_path)
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        return True
        
    finally:
        # Cleanup
        if os.path.exists(export_path):
            os.unlink(export_path)

if __name__ == "__main__":
    try:
        success = test_export_import()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
