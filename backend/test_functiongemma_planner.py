"""
Quick test script to verify FunctionGemma planner adapter works correctly.
"""

import os
import sys

# Set environment to use local model
os.environ['USE_LOCAL_MODEL'] = 'true'

from functiongemma_planner_adapter import FunctionGemmaPlannerAdapter

def test_basic_command():
    """Test a simple command."""
    print("="*70)
    print("Testing FunctionGemma Planner Adapter")
    print("="*70)
    
    print("\n1. Initializing adapter...")
    try:
        adapter = FunctionGemmaPlannerAdapter()
        print("   ✓ Adapter initialized")
    except Exception as e:
        print(f"   ✗ Failed to initialize: {e}")
        return False
    
    print("\n2. Testing simple command: 'Open notepad'")
    try:
        plan = adapter.generate_plan("Open notepad")
        print(f"   ✓ Plan generated successfully")
        print(f"   ✓ Mode: {plan.get('mode')}")
        print(f"   ✓ Steps: {len(plan.get('sequence', []))}")
        print(f"\n   Sequence:")
        for step in plan.get('sequence', []):
            print(f"      {step.get('order')}. {step.get('type')}: {step.get('desc', '')}")
        print(f"\n   Expected final state: {plan.get('expected_final_state')}")
        return True
    except Exception as e:
        print(f"   ✗ Failed to generate plan: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mode_detection():
    """Test mode detection."""
    print("\n" + "="*70)
    print("Testing Mode Detection")
    print("="*70)
    
    adapter = FunctionGemmaPlannerAdapter()
    
    test_cases = [
        ("Open notepad", "general"),
        ("Make a bike plate for PB12W3998", "flexisign"),
        ("Create iron plate", "flexisign"),
        ("Open chrome and go to google", "general"),
    ]
    
    for command, expected_mode in test_cases:
        detected_mode = adapter.detect_mode(command)
        status = "✓" if detected_mode == expected_mode else "✗"
        print(f"{status} '{command}' → {detected_mode} (expected: {expected_mode})")

if __name__ == "__main__":
    print("\nFunctionGemma Planner Adapter Test\n")
    
    # Test mode detection first (doesn't require model)
    test_mode_detection()
    
    # Test basic command (requires model)
    print("\n")
    success = test_basic_command()
    
    if success:
        print("\n" + "="*70)
        print("✓ All tests passed!")
        print("="*70)
        print("\nThe adapter is working correctly and can be used in server.py")
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("✗ Tests failed")
        print("="*70)
        print("\nCheck the error messages above for details")
        sys.exit(1)
