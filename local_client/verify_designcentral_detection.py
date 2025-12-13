"""
Verify DesignCentral Detection Fix

This script verifies that we correctly distinguish between:
1. DesignCentral window (Class="#32770", Type=Window) - only when open
2. DesignCentral checkbox (Class="", Type=CheckBox) - always present

Run this with DesignCentral both open and closed to verify detection.
"""

import sys
import time

try:
    from flexisign_uia import FlexiSignUIA
    from comtypes.gen.UIAutomationClient import (
        UIA_NamePropertyId,
        UIA_ClassNamePropertyId,
        UIA_ControlTypePropertyId,
        TreeScope_Subtree
    )
except ImportError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)


def find_all_designcentral_elements(uia):
    """Find ALL elements with name 'DesignCentral' to show the difference."""
    if uia._root is None:
        print("❌ Root element not available")
        return []
    
    # Create condition for name only
    name_condition = uia._uia.CreatePropertyCondition(UIA_NamePropertyId, "DesignCentral")
    
    # Find all matching elements
    elements = uia._root.FindAll(TreeScope_Subtree, name_condition)
    
    results = []
    if elements:
        for i in range(elements.Length):
            elem = elements.GetElement(i)
            try:
                name = elem.GetCurrentPropertyValue(UIA_NamePropertyId)
                class_name = elem.GetCurrentPropertyValue(UIA_ClassNamePropertyId)
                control_type = elem.GetCurrentPropertyValue(UIA_ControlTypePropertyId)
                
                results.append({
                    'name': name,
                    'class': class_name if class_name else "(empty)",
                    'type': control_type,
                    'element': elem
                })
            except:
                pass
    
    return results


def main():
    print("=" * 70)
    print("DESIGNCENTRAL DETECTION VERIFICATION")
    print("=" * 70)
    
    # Initialize
    print("\n1. Initializing FlexiSIGN UIA...")
    uia = FlexiSignUIA()
    
    # Activate window
    print("2. Activating FlexiSIGN window...")
    if not uia.find_and_activate_window():
        print("❌ Failed to activate FlexiSIGN")
        sys.exit(1)
    print("✓ Window activated")
    
    # Find all elements named "DesignCentral"
    print("\n3. Finding ALL elements with name 'DesignCentral'...")
    print("-" * 70)
    
    elements = find_all_designcentral_elements(uia)
    
    if not elements:
        print("⚠️ No elements found with name 'DesignCentral'")
    else:
        print(f"Found {len(elements)} element(s) with name 'DesignCentral':\n")
        
        for i, elem_info in enumerate(elements, 1):
            print(f"Element {i}:")
            print(f"  Name: {elem_info['name']}")
            print(f"  Class: {elem_info['class']}")
            print(f"  Type: {elem_info['type']}", end="")
            
            # Identify type
            if elem_info['type'] == 50032:
                print(" (Window) ← THIS IS THE PANEL")
            elif elem_info['type'] == 50002:
                print(" (CheckBox) ← THIS IS THE MENU ITEM")
            else:
                print(f" (Unknown)")
            
            print()
    
    # Test our detection method
    print("-" * 70)
    print("\n4. Testing _get_designcentral() method...")
    
    dc = uia._get_designcentral()
    
    if dc is not None:
        print("✓ _get_designcentral() found the DesignCentral WINDOW")
        
        try:
            actual_class = dc.GetCurrentPropertyValue(UIA_ClassNamePropertyId)
            actual_type = dc.GetCurrentPropertyValue(UIA_ControlTypePropertyId)
            print(f"  Verified Class: '{actual_class}'")
            print(f"  Verified Type: {actual_type} (50032=Window)")
        except:
            pass
    else:
        print("✓ _get_designcentral() correctly returned None (window not open)")
    
    # Cleanup
    uia.cleanup()
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    window_found = any(e['type'] == 50032 for e in elements)
    checkbox_found = any(e['type'] == 50002 for e in elements)
    
    print(f"DesignCentral Window (Class=#32770): {'FOUND' if window_found else 'NOT FOUND'}")
    print(f"DesignCentral CheckBox (Class=''): {'FOUND' if checkbox_found else 'NOT FOUND'}")
    print(f"Detection Method Result: {'OPEN' if dc is not None else 'CLOSED'}")
    
    if window_found and dc is not None:
        print("\n✓ CORRECT: Window is open and detected")
    elif not window_found and dc is None:
        print("\n✓ CORRECT: Window is closed and not detected")
    elif window_found and dc is None:
        print("\n❌ ERROR: Window exists but not detected (false negative)")
    elif not window_found and dc is not None:
        print("\n❌ ERROR: Window doesn't exist but detected (false positive)")
    
    print("\nTo test both states:")
    print("1. Run with DesignCentral OPEN (press Ctrl+I if needed)")
    print("2. Run with DesignCentral CLOSED (press Ctrl+I to close)")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
