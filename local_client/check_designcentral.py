"""
DesignCentral Diagnostic Script

This script checks whether the DesignCentral panel is open in FlexiSIGN
and provides detailed diagnostic information about the FlexiSIGN window state.

Usage:
    python check_designcentral.py
"""

import sys
import time

try:
    from flexisign_uia import FlexiSignUIA, FlexiSignUIAError
except ImportError as e:
    print(f"❌ Error: Could not import FlexiSignUIA: {e}")
    print("Make sure you're running from the local_client directory")
    sys.exit(1)


def print_separator():
    """Print a visual separator."""
    print("=" * 70)


def check_flexisign_window():
    """Check if FlexiSIGN window is available."""
    print("\n🔍 Step 1: Checking for FlexiSIGN window...")
    print_separator()
    
    uia = FlexiSignUIA()
    
    # Find window
    window = uia.find_flexisign_window()
    if window is None:
        print("❌ FlexiSIGN window NOT FOUND")
        print("   Please ensure FlexiSIGN is running")
        return None
    
    print(f"✓ FlexiSIGN window found: {window.title}")
    
    # Get PID
    pid = uia.get_pid_from_window(window)
    if pid:
        print(f"✓ Process ID: {pid}")
    else:
        print("⚠️ Could not get process ID")
    
    return uia


def check_window_activation(uia):
    """Check if window can be activated."""
    print("\n🔍 Step 2: Activating FlexiSIGN window...")
    print_separator()
    
    success = uia.find_and_activate_window()
    
    if success:
        print("✓ FlexiSIGN window activated successfully")
        print(f"✓ Root element: {'Found' if uia._root else 'NOT FOUND'}")
        return True
    else:
        print("❌ Failed to activate FlexiSIGN window")
        print("   This may cause automation to fail")
        return False


def check_designcentral(uia):
    """Check if DesignCentral panel is open."""
    print("\n🔍 Step 3: Checking DesignCentral panel...")
    print_separator()
    
    # Check if DesignCentral is currently visible
    dc = uia._get_designcentral()
    
    if dc is not None:
        print("✓ DesignCentral panel is OPEN")
        
        # Try to get bounding rect
        rect = uia.get_bounding_rect(dc)
        if rect:
            print(f"  Position: ({rect[0]:.0f}, {rect[1]:.0f})")
            print(f"  Size: {rect[2]-rect[0]:.0f} x {rect[3]-rect[1]:.0f}")
        
        return True
    else:
        print("❌ DesignCentral panel is CLOSED")
        return False


def test_open_designcentral(uia):
    """Test opening DesignCentral if it's closed."""
    print("\n🔍 Step 4: Testing DesignCentral open function...")
    print_separator()
    
    print("Attempting to open DesignCentral with Ctrl+I...")
    
    success = uia.ensure_designcentral_open()
    
    if success:
        print("✓ DesignCentral opened successfully")
        
        # Verify it's actually open
        dc = uia._get_designcentral()
        if dc is not None:
            print("✓ DesignCentral verified as open")
            return True
        else:
            print("⚠️ ensure_designcentral_open returned True but panel not found")
            return False
    else:
        print("❌ Failed to open DesignCentral")
        print("   Possible causes:")
        print("   - FlexiSIGN window not in foreground")
        print("   - Ctrl+I hotkey not working")
        print("   - DesignCentral already docked/hidden")
        return False


def check_designcentral_elements(uia):
    """Check if DesignCentral elements are accessible."""
    print("\n🔍 Step 5: Checking DesignCentral elements...")
    print_separator()
    
    # Check tab control
    tabcontrol = uia._get_designcentral_tabcontrol()
    if tabcontrol:
        print("✓ Tab control found (AutomationId: 12320)")
    else:
        print("❌ Tab control NOT FOUND")
        return False
    
    # Check Scale tab
    try:
        scale_tab = uia.get_scale_tab_item()
        if scale_tab:
            print("✓ Scale tab found (index 0)")
    except FlexiSignUIAError as e:
        print(f"❌ Scale tab error: {e}")
        return False
    
    # Check Character tab
    try:
        char_tab = uia.get_character_tab_item()
        if char_tab:
            print("✓ Character tab found (index 2)")
    except FlexiSignUIAError as e:
        print(f"❌ Character tab error: {e}")
        return False
    
    # Check width input (requires Scale tab to be active)
    try:
        width_input = uia.get_scale_width_input(ensure_tab_active=True)
        if width_input:
            print("✓ Width input found (AutomationId: 10609)")
    except FlexiSignUIAError as e:
        print(f"❌ Width input error: {e}")
        return False
    
    # Check height input
    try:
        height_input = uia.get_scale_height_input(ensure_tab_active=False)
        if height_input:
            print("✓ Height input found (AutomationId: 10610)")
    except FlexiSignUIAError as e:
        print(f"❌ Height input error: {e}")
        return False
    
    # Check font combobox (requires Character tab to be active)
    try:
        font_combo = uia.get_font_family_combobox(ensure_tab_active=True)
        if font_combo:
            print("✓ Font combobox found (AutomationId: 10825)")
    except FlexiSignUIAError as e:
        print(f"❌ Font combobox error: {e}")
        return False
    
    return True


def main():
    """Main diagnostic routine."""
    print("\n" + "=" * 70)
    print("DESIGNCENTRAL DIAGNOSTIC TOOL")
    print("=" * 70)
    
    # Step 1: Check FlexiSIGN window
    uia = check_flexisign_window()
    if uia is None:
        print("\n❌ DIAGNOSTIC FAILED: FlexiSIGN not running")
        sys.exit(1)
    
    # Step 2: Activate window
    if not check_window_activation(uia):
        print("\n⚠️ WARNING: Window activation failed, continuing anyway...")
    
    # Step 3: Check if DesignCentral is open
    is_open = check_designcentral(uia)
    
    # Step 4: If closed, try to open it
    if not is_open:
        if not test_open_designcentral(uia):
            print("\n❌ DIAGNOSTIC FAILED: Cannot open DesignCentral")
            print("\nTroubleshooting tips:")
            print("1. Make sure FlexiSIGN window is in foreground")
            print("2. Try manually pressing Ctrl+I to toggle DesignCentral")
            print("3. Check if DesignCentral is docked or hidden")
            print("4. Restart FlexiSIGN and try again")
            sys.exit(1)
    
    # Step 5: Check DesignCentral elements
    if not check_designcentral_elements(uia):
        print("\n❌ DIAGNOSTIC FAILED: DesignCentral elements not accessible")
        sys.exit(1)
    
    # Cleanup
    uia.cleanup()
    
    # Final summary
    print("\n" + "=" * 70)
    print("✓ DIAGNOSTIC PASSED: All checks successful")
    print("=" * 70)
    print("\nDesignCentral Status:")
    print("  - Window: Found and activated")
    print("  - Panel: Open and accessible")
    print("  - Elements: All key elements found")
    print("\n✓ FlexiSIGN automation should work correctly")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Diagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
