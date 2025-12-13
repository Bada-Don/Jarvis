"""
Test Integrated Window Activation

This script tests the integrated two-method activation approach
that has been added to flexisign_uia.py.

Usage:
    python test_integrated_activation.py
"""

import sys
import time

try:
    from flexisign_uia import FlexiSignUIA
    import pygetwindow as gw
    import win32gui
except ImportError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)


def get_foreground_window_title():
    """Get title of current foreground window."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd)
    except:
        return "Unknown"


def main():
    print("=" * 70)
    print("INTEGRATED ACTIVATION TEST")
    print("=" * 70)
    
    # Initialize UIA
    print("\n1. Initializing FlexiSIGN UIA...")
    uia = FlexiSignUIA()
    
    # Find window
    print("\n2. Finding FlexiSIGN window...")
    window = uia.find_flexisign_window()
    
    if window is None:
        print("❌ FlexiSIGN window not found")
        print("   Please ensure FlexiSIGN is running")
        sys.exit(1)
    
    print(f"✓ Found: {window.title}")
    
    # Check current state
    print("\n3. Checking current state...")
    current_foreground = get_foreground_window_title()
    print(f"   Current foreground: {current_foreground}")
    print(f"   FlexiSIGN active: {window.isActive}")
    
    if window.isActive:
        print("\n⚠️ FlexiSIGN is already active!")
        print("   To test activation:")
        print("   1. Switch to another window (Alt+Tab)")
        print("   2. Run this script again")
        sys.exit(0)
    
    # Test activation
    print("\n4. Testing integrated activation method...")
    print("-" * 70)
    
    success = uia.activate_window(window)
    
    # Verify
    print("\n5. Verifying activation...")
    time.sleep(0.3)
    
    is_active = window.isActive
    current_foreground = get_foreground_window_title()
    
    print(f"   FlexiSIGN active: {is_active}")
    print(f"   Current foreground: {current_foreground}")
    
    # Cleanup
    uia.cleanup()
    
    # Results
    print("\n" + "=" * 70)
    if success and is_active:
        print("✓ TEST PASSED: Activation successful")
        print("=" * 70)
        print("\nIntegrated two-method approach working:")
        print("  ✓ Primary: AttachThreadInput")
        print("  ✓ Fallback: Click Window Center")
        print("\n✓ flexisign_uia.py is ready for use")
        return 0
    elif success and not is_active:
        print("⚠️ TEST PARTIAL: Method returned success but window not active")
        print("=" * 70)
        print("\nPossible timing issue - try increasing delays")
        return 1
    else:
        print("❌ TEST FAILED: Activation failed")
        print("=" * 70)
        print("\nBoth methods failed:")
        print("  - Method 1: AttachThreadInput")
        print("  - Method 2: Click Window Center")
        print("\nNext steps:")
        print("  1. Run: python test_window_activation.py")
        print("  2. Check which methods work on your system")
        print("  3. Update flexisign_uia.py with working methods")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
