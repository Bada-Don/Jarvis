"""
Quick test to verify DesignCentral detection and opening works correctly.

This script tests the ensure_designcentral_open() function in isolation.
"""

import sys
import time

try:
    from flexisign_uia import FlexiSignUIA, FlexiSignUIAError
except ImportError as e:
    print(f"❌ Error: Could not import FlexiSignUIA: {e}")
    sys.exit(1)


def main():
    print("=" * 60)
    print("DESIGNCENTRAL FIX TEST")
    print("=" * 60)
    
    # Initialize UIA
    print("\n1. Initializing FlexiSIGN UIA...")
    uia = FlexiSignUIA()
    
    # Find and activate window
    print("2. Finding and activating FlexiSIGN window...")
    if not uia.find_and_activate_window():
        print("❌ Failed to find/activate FlexiSIGN window")
        print("   Please ensure FlexiSIGN is running")
        sys.exit(1)
    print("✓ Window activated")
    
    # Check initial state
    print("\n3. Checking initial DesignCentral state...")
    dc = uia._designcentral.get_designcentral()
    if dc is not None:
        print("✓ DesignCentral is already OPEN")
        initial_state = "open"
    else:
        print("✓ DesignCentral is currently CLOSED")
        initial_state = "closed"
    
    # Test ensure_designcentral_open
    print("\n4. Testing ensure_designcentral_open()...")
    success = uia.ensure_designcentral_open()
    
    if success:
        print("✓ ensure_designcentral_open() returned True")
    else:
        print("❌ ensure_designcentral_open() returned False")
    
    # Verify final state
    print("\n5. Verifying final state...")
    dc = uia._designcentral.get_designcentral()
    if dc is not None:
        print("✓ DesignCentral is now OPEN")
        final_state = "open"
    else:
        print("❌ DesignCentral is still CLOSED")
        final_state = "closed"
    
    # Cleanup
    uia.cleanup()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Initial State: {initial_state}")
    print(f"Function Result: {'Success' if success else 'Failed'}")
    print(f"Final State: {final_state}")
    
    if final_state == "open":
        print("\n✓ TEST PASSED: DesignCentral is accessible")
        return 0
    else:
        print("\n❌ TEST FAILED: DesignCentral could not be opened")
        print("\nTroubleshooting:")
        print("1. Try manually pressing Ctrl+I in FlexiSIGN")
        print("2. Check if DesignCentral is docked/hidden")
        print("3. Restart FlexiSIGN and try again")
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
