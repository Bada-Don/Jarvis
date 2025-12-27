"""
Integration test for PlanExecutor with Function Executor.

This test verifies the complete integration between PlanExecutor and
the FunctionGemma function calling system.
"""

import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.dirname(__file__))

from plan_executor import PlanExecutor
from function_executor import FunctionExecutor
from function_registry import FunctionRegistry


def test_complete_integration():
    """Test complete integration with real Function Executor and Registry."""
    
    # Create mock vision service
    class MockVisionService:
        pass
    
    # Create function registry
    registry = FunctionRegistry()
    
    # Register a simple test function
    def test_function(message: str) -> dict:
        """Test function that returns success."""
        return {
            "success": True,
            "message": f"Test function called with: {message}"
        }
    
    # Register the function
    registry.register_function(
        name="test_function",
        implementation=test_function,
        schema={
            "description": "A test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Test message"
                    }
                },
                "required": ["message"]
            }
        },
        category="file_operations"  # Use valid category
    )
    
    # Create function executor
    executor = FunctionExecutor(registry)
    
    # Create plan executor
    plan_executor = PlanExecutor(MockVisionService())
    plan_executor.set_function_executor(executor)
    plan_executor.set_function_registry(registry)
    
    # Create a function calling plan
    plan = {
        "mode": "function_calling",
        "sequence": [
            {
                "function_name": "test_function",
                "arguments": {"message": "Hello from integration test!"}
            }
        ]
    }
    
    # Execute the plan
    result = plan_executor.execute_plan(plan, verify=False)
    
    # Verify results
    assert result["success"] == True, f"Execution should succeed, got: {result}"
    assert result["aborted"] == False, "Should not be aborted"
    
    # The result structure may vary, so let's check what we have
    print(f"Result keys: {result.keys()}")
    
    # If we have a nested result, check it
    if "result" in result:
        exec_result = result["result"]
        assert exec_result["overall_success"] == True, "Overall execution should succeed"
        assert exec_result["total_steps"] == 1, "Should have 1 step"
        assert exec_result["successful_steps"] == 1, "Should have 1 successful step"
        assert exec_result["failed_steps"] == 0, "Should have 0 failed steps"
    
    print("✓ Complete integration test passed")


def test_multiple_function_calls():
    """Test execution of multiple function calls."""
    
    class MockVisionService:
        pass
    
    registry = FunctionRegistry()
    
    # Register multiple test functions
    def func1(value: int) -> dict:
        return {"success": True, "result": value * 2}
    
    def func2(text: str) -> dict:
        return {"success": True, "result": text.upper()}
    
    registry.register_function(
        name="func1",
        implementation=func1,
        schema={
            "description": "Doubles a number",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "integer"}
                },
                "required": ["value"]
            }
        },
        category="file_operations"
    )
    
    registry.register_function(
        name="func2",
        implementation=func2,
        schema={
            "description": "Uppercases text",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        },
        category="folder_operations"
    )
    
    executor = FunctionExecutor(registry)
    plan_executor = PlanExecutor(MockVisionService())
    plan_executor.set_function_executor(executor)
    plan_executor.set_function_registry(registry)
    
    # Plan with multiple function calls
    plan = {
        "mode": "function_calling",
        "sequence": [
            {
                "function_name": "func1",
                "arguments": {"value": 5}
            },
            {
                "function_name": "func2",
                "arguments": {"text": "hello"}
            }
        ]
    }
    
    result = plan_executor.execute_plan(plan, verify=False)
    
    assert result["success"] == True, "Execution should succeed"
    
    # Check if we have detailed results
    if "result" in result:
        exec_result = result["result"]
        assert exec_result["total_steps"] == 2, "Should have 2 steps"
        assert exec_result["successful_steps"] == 2, "Both steps should succeed"
    
    print("✓ Multiple function calls test passed")


def test_error_handling():
    """Test error handling in function calling mode."""
    
    class MockVisionService:
        pass
    
    registry = FunctionRegistry()
    
    # Register a function that fails
    def failing_function() -> dict:
        return {"success": False, "message": "Intentional failure"}
    
    registry.register_function(
        name="failing_function",
        implementation=failing_function,
        schema={
            "description": "A function that fails",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        category="keyboard_operations"
    )
    
    executor = FunctionExecutor(registry)
    plan_executor = PlanExecutor(MockVisionService())
    plan_executor.set_function_executor(executor)
    plan_executor.set_function_registry(registry)
    
    plan = {
        "mode": "function_calling",
        "sequence": [
            {
                "function_name": "failing_function",
                "arguments": {}
            }
        ]
    }
    
    result = plan_executor.execute_plan(plan, verify=False)
    
    # Should complete but report failure
    assert result["success"] == False, "Should report failure"
    assert result["aborted"] == False, "Should not be aborted"
    
    # Check if we have detailed results
    if "result" in result:
        exec_result = result["result"]
        assert exec_result["failed_steps"] == 1, "Should have 1 failed step"
    
    print("✓ Error handling test passed")


if __name__ == "__main__":
    print("Running PlanExecutor integration tests...\n")
    
    try:
        test_complete_integration()
        test_multiple_function_calls()
        test_error_handling()
        
        print("\n✓ All integration tests passed!")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
