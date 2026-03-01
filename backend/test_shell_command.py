"""
Test script for the new shell_command tool in JARVIS.

This demonstrates the "Killer Combo" workflow for file operations:
1. Create file/folder using shell command
2. Open file using start command
3. Edit via keyboard
4. Save via Ctrl+S (silent because file exists)
"""

import json
from newPlanner_service import PlannerService

def test_killer_combo_workflow():
    """Test the Killer Combo workflow for creating and editing a file."""
    
    # Initialize planner service
    planner = PlannerService()
    
    # Test command: Create a text file on desktop and edit it
    user_command = "Create a file called test_notes.txt on my desktop and write 'Hello from JARVIS!' in it"
    
    print("=" * 60)
    print("Testing Killer Combo Workflow")
    print("=" * 60)
    print(f"User Command: {user_command}")
    print()
    
    # Generate plan
    plan = planner.generate_plan(user_command, mode="general")
    
    print("Generated Plan:")
    print(json.dumps(plan, indent=2))
    print()
    
    # Verify the plan uses shell_command
    has_shell_command = any(step.get('type') == 'shell_command' for step in plan.get('sequence', []))
    
    if has_shell_command:
        print("✓ Plan correctly uses shell_command tool")
    else:
        print("✗ Plan does not use shell_command tool")
    
    print()
    print("Expected workflow:")
    print("1. shell_command: cd %USERPROFILE%\\Desktop & type nul > test_notes.txt")
    print("2. shell_command: start test_notes.txt")
    print("3. keyboard: Hello from JARVIS!")
    print("4. keyboard: ctrl+s")
    print()

def test_folder_creation():
    """Test folder creation using shell commands."""
    
    planner = PlannerService()
    
    user_command = "Create a folder called JARVIS_Test on my desktop with subfolders Python and JavaScript"
    
    print("=" * 60)
    print("Testing Folder Creation")
    print("=" * 60)
    print(f"User Command: {user_command}")
    print()
    
    plan = planner.generate_plan(user_command, mode="general")
    
    print("Generated Plan:")
    print(json.dumps(plan, indent=2))
    print()

def test_validation():
    """Test that shell_command validation works correctly."""
    
    planner = PlannerService()
    
    # Test plan with missing command parameter
    invalid_plan = {
        "mode": "general",
        "sequence": [
            {
                "order": 1,
                "type": "shell_command",
                "desc": "Missing command parameter"
            }
        ]
    }
    
    print("=" * 60)
    print("Testing Validation")
    print("=" * 60)
    
    try:
        planner._validate_plan(invalid_plan)
        print("✗ Validation should have failed for missing 'command' parameter")
    except ValueError as e:
        print(f"✓ Validation correctly caught error: {e}")
    
    # Test valid plan
    valid_plan = {
        "mode": "general",
        "sequence": [
            {
                "order": 1,
                "type": "shell_command",
                "command": "mkdir test",
                "desc": "Create test folder"
            }
        ]
    }
    
    try:
        planner._validate_plan(valid_plan)
        print("✓ Validation passed for valid shell_command")
    except ValueError as e:
        print(f"✗ Validation failed unexpectedly: {e}")
    
    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("JARVIS Shell Command Tool - Test Suite")
    print("=" * 60 + "\n")
    
    try:
        test_validation()
        test_killer_combo_workflow()
        test_folder_creation()
        
        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
