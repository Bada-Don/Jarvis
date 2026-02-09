"""
Basic test for ApplicationLauncher and SystemTrayManager
Tests that classes can be instantiated and basic methods work.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from application_launcher import ApplicationLauncher
from system_tray_manager import SystemTrayManager


def test_application_launcher_instantiation():
    """Test that ApplicationLauncher can be instantiated."""
    print('Testing ApplicationLauncher instantiation...')
    
    try:
        launcher = ApplicationLauncher(log_level=logging.WARNING)
        print('✅ ApplicationLauncher instantiated successfully')
        
        # Test get_status method
        status = launcher.get_status()
        print(f'✅ get_status() returned: {len(status)} components')
        
        # Test that components are defined
        assert 'backend' in launcher.components
        assert 'local_client' in launcher.components
        assert 'settings_ui' in launcher.components
        print('✅ All expected components are defined')
        
        return True
    except Exception as e:
        print(f'❌ ApplicationLauncher test failed: {e}')
        return False


def test_system_tray_manager_instantiation():
    """Test that SystemTrayManager can be instantiated."""
    print('\nTesting SystemTrayManager instantiation...')
    
    try:
        # Create with dummy callbacks
        def dummy_callback():
            pass
        
        def dummy_status():
            return {}
        
        tray = SystemTrayManager(
            on_show_settings=dummy_callback,
            on_restart=dummy_callback,
            on_quit=dummy_callback,
            get_status=dummy_status
        )
        print('✅ SystemTrayManager instantiated successfully')
        
        # Test that icon was created
        assert tray.icon is not None
        print('✅ System tray icon created')
        
        return True
    except Exception as e:
        print(f'❌ SystemTrayManager test failed: {e}')
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all basic tests."""
    print('=' * 60)
    print('JARVIS Launcher Basic Tests')
    print('=' * 60)
    
    results = []
    
    # Test ApplicationLauncher
    results.append(test_application_launcher_instantiation())
    
    # Test SystemTrayManager
    results.append(test_system_tray_manager_instantiation())
    
    # Summary
    print('\n' + '=' * 60)
    print('Test Summary')
    print('=' * 60)
    passed = sum(results)
    total = len(results)
    print(f'Passed: {passed}/{total}')
    
    if passed == total:
        print('✅ All tests passed!')
        return 0
    else:
        print('❌ Some tests failed')
        return 1


if __name__ == '__main__':
    sys.exit(main())
