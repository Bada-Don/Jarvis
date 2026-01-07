"""
Test script for PackagingService

This script tests the basic functionality of the PackagingService
without actually running PyInstaller.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from packaging_service import PackagingService


def test_packaging_service():
    """Test PackagingService initialization and spec generation."""
    print("Testing PackagingService...")
    print("-" * 60)
    
    # Test 1: Initialize service
    print("\n1. Testing initialization...")
    project_root = Path(__file__).parent.parent
    service = PackagingService(str(project_root))
    print(f"   - Service initialized with project root: {service.project_root_str}")
    print(f"   - Build directory: {service.build_dir_str}")
    
    # Test 2: Generate spec file
    print("\n2. Testing spec file generation...")
    options = {
        'output_name': 'TestApp',
        'include_console': True,
        'one_file': True,
        'icon': ''
    }
    
    spec_content = service.get_build_spec(options)
    print(f"   - Spec file generated ({len(spec_content)} characters)")
    
    # Verify spec content contains expected elements
    expected_elements = [
        'TestApp',
        'Analysis',
        'PYZ',
        'EXE',
        'google.genai',
        'pyautogui',
        'backend',
        'local_client'
    ]
    
    missing = []
    for element in expected_elements:
        if element not in spec_content:
            missing.append(element)
    
    if missing:
        print(f"   x Missing elements in spec: {missing}")
        return False
    else:
        print(f"   - All expected elements present in spec")
    
    # Test 3: Test spec with different options
    print("\n3. Testing spec with different options...")
    options_no_console = {
        'output_name': 'TestApp',
        'include_console': False,
        'one_file': False,
        'icon': 'icon.ico'
    }
    
    spec_content_2 = service.get_build_spec(options_no_console)
    
    if 'console=False' in spec_content_2:
        print("   - Console mode correctly set to False")
    else:
        print("   x Console mode not correctly set")
        return False
    
    if 'COLLECT' in spec_content_2:
        print("   - Directory-based build (COLLECT) present")
    else:
        print("   x Directory-based build not correctly configured")
        return False
    
    # Test 4: Test build status
    print("\n4. Testing build status...")
    status = service.get_build_status()
    
    if not status['is_building']:
        print("   - Initial build status is not building")
    else:
        print("   x Initial build status incorrect")
        return False
    
    if status['progress'] == 0:
        print("   - Initial progress is 0")
    else:
        print("   x Initial progress incorrect")
        return False
    
    print("\n" + "=" * 60)
    print("All tests passed! -")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = test_packaging_service()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n- Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
