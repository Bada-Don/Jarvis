"""
Test for PlanExecutor function calling mode integration.

This test verifies that the PlanExecutor correctly routes function calling
plans to the Function Executor while maintaining backward compatibility.
"""

import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.dirname(__file__))

from plan_executor import PlanExecutor


def test_function_calling_mode_detection():
    """Test that function calling mode is detected correctly."""
    # Create a mock vision service (not needed for function calling mode)
    class MockVisionService:
        pass
    
    # Create PlanExecutor
    executor = PlanExecutor(MockVisionService())
    
    # Test plan with function_calling mode
    plan = {
        "mode": "function_calling",
        "sequence": [
            {
                "function_name": "create_folder",
                "arguments": {"path": "/test/folder"}
            }
        ]
    }
    
    # Execute plan (should fail gracefully since function executor not set)
    result = executor.execute_plan(plan, verify=False)
    
    # Should return failure but not crash
    assert isinstance(result, dict), "Result should be a dict"
    assert "success" in result, "Result should have 'success' key"
    assert "aborted" in result, "Result should have 'aborted' key"
    
    print("✓ Function calling mode detection test passed")


def test_backward_compatibility_vision_mode():
    """Test that vision mode still works (backward compatibility)."""
    class MockVisionService:
        pass
    
    executor = PlanExecutor(MockVisionService())
    
    # Test plan with vision mode (default)
    plan = {
        "mode": "vision",
        "sequence": []  # Empty sequence
    }
    
    result = executor.execute_plan(plan, verify=False)
    
    # Should handle empty sequence gracefully
    assert isinstance(result, dict), "Result should be a dict"
    assert result["success"] == False, "Empty sequence should fail"
    
    print("✓ Backward compatibility (vision mode) test passed")


def test_backward_compatibility_direct_mode():
    """Test that direct mode still works (backward compatibility)."""
    class MockVisionService:
        pass
    
    executor = PlanExecutor(MockVisionService())
    
    # Test plan with direct mode
    plan = {
        "mode": "direct",
        "sequence": []  # Empty sequence
    }
    
    result = executor.execute_plan(plan, verify=False)
    
    # Should handle gracefully (FlexiSIGN UIA not available in test)
    assert isinstance(result, dict), "Result should be a dict"
    
    print("✓ Backward compatibility (direct mode) test passed")


def test_function_executor_setter():
    """Test that function executor can be set."""
    class MockVisionService:
        pass
    
    class MockFunctionExecutor:
        pass
    
    executor = PlanExecutor(MockVisionService())
    mock_executor = MockFunctionExecutor()
    
    # Should not raise exception
    executor.set_function_executor(mock_executor)
    
    assert executor._function_executor is mock_executor, "Function executor should be set"
    
    print("✓ Function executor setter test passed")


def test_function_registry_setter():
    """Test that function registry can be set."""
    class MockVisionService:
        pass
    
    class MockFunctionRegistry:
        pass
    
    executor = PlanExecutor(MockVisionService())
    mock_registry = MockFunctionRegistry()
    
    # Should not raise exception
    executor.set_function_registry(mock_registry)
    
    assert executor._function_registry is mock_registry, "Function registry should be set"
    
    print("✓ Function registry setter test passed")


if __name__ == "__main__":
    print("Running PlanExecutor function calling integration tests...\n")
    
    try:
        test_function_calling_mode_detection()
        test_backward_compatibility_vision_mode()
        test_backward_compatibility_direct_mode()
        test_function_executor_setter()
        test_function_registry_setter()
        
        print("\n✓ All tests passed!")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
