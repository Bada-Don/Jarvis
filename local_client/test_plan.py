"""
Test Plan Executor - Execute plans from JSON files without Gemini API

This script allows you to test execution plans directly from JSON files,
bypassing the need for Gemini API calls. Useful for debugging and testing.

Usage:
    python test_plan.py <plan_file.json>
    
Example:
    python test_plan.py test_plans/open_folder.json
"""

import sys
import json
import time
from pathlib import Path

# Import required components
try:
    from vision_service import VisionService
    from plan_executor import PlanExecutor
    from debug_logger import create_new_session, get_debug_logger
    
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Error: Required components not available: {e}")
    print("Make sure you're running from the local_client directory")
    sys.exit(1)

try:
    from flexisign_manager import FlexiSignManager
    FLEXISIGN_MANAGER_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: flexisign_manager not available")
    FLEXISIGN_MANAGER_AVAILABLE = False


def load_plan_from_file(filepath: str) -> dict:
    """Load execution plan from JSON file."""
    try:
        from json_utils import safe_json_loads
    except ImportError:
        safe_json_loads = json.loads  # Fallback
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return safe_json_loads(f.read())
    except FileNotFoundError:
        print(f"❌ Error: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in file: {e}")
        sys.exit(1)


def validate_plan(plan: dict) -> bool:
    """Validate that the plan has required fields."""
    if not isinstance(plan, dict):
        print("❌ Error: Plan must be a JSON object")
        return False
    
    if 'sequence' not in plan:
        print("❌ Error: Plan must have 'sequence' field")
        return False
    
    if not isinstance(plan['sequence'], list):
        print("❌ Error: 'sequence' must be a list")
        return False
    
    # Validate each step
    for i, step in enumerate(plan['sequence'], 1):
        if 'type' not in step:
            print(f"❌ Error: Step {i} missing 'type' field")
            return False
    
    return True


def print_plan_summary(plan: dict):
    """Print a summary of the plan."""
    print("\n" + "="*60)
    print("PLAN SUMMARY")
    print("="*60)
    
    mode = plan.get('mode', 'vision')
    print(f"Mode: {mode}")
    
    # Show if FlexiSIGN initialization will be performed
    if mode in ('direct', 'flexisign'):
        print(f"FlexiSIGN Init: {'Yes' if FLEXISIGN_MANAGER_AVAILABLE else 'No (manager not available)'}")
    
    if 'expected_final_state' in plan:
        print(f"Expected Final State: {plan['expected_final_state']}")
    
    print(f"\nSteps ({len(plan['sequence'])}):")
    for step in plan['sequence']:
        order = step.get('order', '?')
        step_type = step.get('type', 'unknown')
        desc = step.get('desc', 'No description')
        print(f"  [{order}] {step_type}: {desc}")
    
    print("="*60 + "\n")


def execute_plan_from_file(filepath: str):
    """Execute a plan loaded from a JSON file."""
    print(f"Loading plan from: {filepath}")
    
    # Load and validate plan
    plan = load_plan_from_file(filepath)
    
    if not validate_plan(plan):
        sys.exit(1)
    
    # Print plan summary
    print_plan_summary(plan)
    
    # Ask for confirmation
    response = input("Execute this plan? (y/n): ").strip().lower()
    if response != 'y':
        print("Execution cancelled.")
        return
    
    # Create debug session
    session_id = create_new_session()
    logger = get_debug_logger()
    
    print(f"\n📝 Debug logs: debug_logs/{session_id}/")
    
    # Log the plan
    logger.log_planner_output(plan)
    
    # Initialize services
    print("\n🔧 Initializing services...")
    
    def status_callback(status_data, status_type=None):
        """Print status updates."""
        # Handle both dict and string formats
        if isinstance(status_data, dict):
            message = status_data.get('message', '')
            progress = status_data.get('progress', 0)
            print(f"  [{progress}%] {message}")
        else:
            # String format
            print(f"  {status_data}")
    
    # Check if this is a FlexiSIGN plan (mode: direct or flexisign)
    mode = plan.get('mode', 'vision')
    
    # For FlexiSIGN mode, ensure the app is ready
    if mode in ('direct', 'flexisign') and FLEXISIGN_MANAGER_AVAILABLE:
        print("\n🎨 Preparing FlexiSIGN...")
        manager = FlexiSignManager(status_callback=status_callback)
        if not manager.ensure_proper_state():
            print("❌ Failed to start FlexiSIGN Pro")
            print("   Please ensure FlexiSIGN is installed and accessible")
            sys.exit(1)
        print("✓ FlexiSIGN ready")
    
    vision_service = VisionService()
    executor = PlanExecutor(vision_service, status_callback)
    
    # Give user time to prepare
    print("\n⏱️  Starting execution in 3 seconds...")
    print("   (Move your mouse to a corner to abort if needed)")
    time.sleep(3)
    
    # Load verification settings from config
    try:
        from config import VERIFICATION_ENABLED, MAX_RETRIES
        verify_enabled = VERIFICATION_ENABLED
        print(f"📋 Verification: {'Enabled' if verify_enabled else 'Disabled'}")
        if verify_enabled:
            print(f"📋 Max retries: {MAX_RETRIES}")
    except ImportError:
        verify_enabled = True  # Default
        print("⚠️ Could not load verification config, using defaults")
    
    # Execute the plan
    print("\n🚀 Executing plan...\n")
    
    try:
        result = executor.execute_plan(plan, verify=verify_enabled)
        
        # Print results
        print("\n" + "="*60)
        print("EXECUTION RESULTS")
        print("="*60)
        print(f"Success: {result.get('success', False)}")
        
        if 'message' in result:
            print(f"Message: {result['message']}")
        
        if 'steps_executed' in result:
            print(f"Steps Executed: {result['steps_executed']}")
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        
        if 'verification' in result:
            verification = result['verification']
            print(f"Verification: {verification.get('status', 'unknown')}")
            if 'confidence' in verification:
                print(f"Confidence: {verification['confidence']}%")
        
        print("="*60)
        
        # Log results (if method exists)
        if hasattr(logger, 'log_execution_result'):
            logger.log_execution_result(result)
        
        print(f"\n📝 Full logs saved to: debug_logs/{session_id}/")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Execution failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python test_plan.py <plan_file.json>")
        print("\nExample:")
        print("  python test_plan.py test_plans/open_folder.json")
        sys.exit(1)
    
    filepath = sys.argv[1]
    execute_plan_from_file(filepath)


if __name__ == '__main__':
    main()
