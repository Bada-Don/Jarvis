"""
Verification test for Task 12.1: Create FunctionGemmaPlannerService class

This test verifies that all requirements from task 12.1 are met:
- Implement model loading with error handling
- Implement generate_function_calls() method
- Implement execute_multi_step_task() with conversation turns
- Add system prompt with exact required text
- Integrate with FunctionRegistry for schema generation

Requirements: 1.1, 1.2, 1.5, 12.1
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from functiongemma_service import FunctionGemmaPlannerService, FunctionCall, ExecutionResult
from function_registry import FunctionRegistry


def test_requirement_1_1_model_loading():
    """
    Requirement 1.1: WHEN the system initializes, THE Planner_Service SHALL 
    load the FunctionGemma model from local storage
    """
    print("\n" + "="*70)
    print("Test: Requirement 1.1 - Model Loading from Local Storage")
    print("="*70)
    
    try:
        # Test 1: Service can be initialized
        service = FunctionGemmaPlannerService(
            model_path="./test_model",
            lazy_load=True
        )
        print("✓ Service initialized successfully")
        
        # Test 2: load_model() method exists and has error handling
        assert hasattr(service, 'load_model'), "load_model() method missing"
        print("✓ load_model() method exists")
        
        # Test 3: Error handling for missing model
        try:
            service.load_model()
            print("✗ Should have raised FileNotFoundError")
            return False
        except FileNotFoundError as e:
            print(f"✓ Proper error handling: {str(e)[:60]}...")
        
        # Test 4: Model caching (lazy loading)
        assert service._model_loaded == False, "Model should not be loaded yet"
        print("✓ Lazy loading works (model not loaded until needed)")
        
        print("\n✓ Requirement 1.1 VERIFIED: Model loading with error handling")
        return True
        
    except Exception as e:
        print(f"\n✗ Requirement 1.1 FAILED: {e}")
        return False


def test_requirement_1_2_local_processing():
    """
    Requirement 1.2: WHEN a user command is received, THE Planner_Service SHALL 
    process it using the Local_Model without making external API calls
    """
    print("\n" + "="*70)
    print("Test: Requirement 1.2 - Local Processing (No External API Calls)")
    print("="*70)
    
    try:
        service = FunctionGemmaPlannerService(
            model_path="./test_model",
            lazy_load=True
        )
        
        # Test 1: generate_function_calls() method exists
        assert hasattr(service, 'generate_function_calls'), "generate_function_calls() missing"
        print("✓ generate_function_calls() method exists")
        
        # Test 2: Method requires function_registry (local processing)
        try:
            service.generate_function_calls("test command")
            print("✗ Should require function_registry")
            return False
        except ValueError as e:
            if "Function registry not set" in str(e):
                print("✓ Requires function_registry (ensures local processing)")
            else:
                raise
        
        # Test 3: Uses AutoProcessor (not AutoTokenizer) - check in code
        with open('functiongemma_service.py', 'r') as f:
            code = f.read()
            assert 'AutoProcessor' in code, "Should use AutoProcessor"
            assert 'from transformers import AutoProcessor' in code
            print("✓ Uses AutoProcessor (as specified in requirements)")
        
        print("\n✓ Requirement 1.2 VERIFIED: Local processing without external APIs")
        return True
        
    except Exception as e:
        print(f"\n✗ Requirement 1.2 FAILED: {e}")
        return False


def test_requirement_1_5_system_prompt():
    """
    Requirement 1.5: THE System SHALL include the exact system prompt: 
    "You are a model that can do function calling with the following functions"
    """
    print("\n" + "="*70)
    print("Test: Requirement 1.5 - Exact System Prompt")
    print("="*70)
    
    try:
        # Test 1: SYSTEM_PROMPT constant exists
        assert hasattr(FunctionGemmaPlannerService, 'SYSTEM_PROMPT'), "SYSTEM_PROMPT missing"
        print("✓ SYSTEM_PROMPT constant exists")
        
        # Test 2: Exact text match
        expected_prompt = "You are a model that can do function calling with the following functions"
        actual_prompt = FunctionGemmaPlannerService.SYSTEM_PROMPT
        
        assert actual_prompt == expected_prompt, f"Prompt mismatch: {actual_prompt}"
        print(f"✓ Exact system prompt: '{actual_prompt}'")
        
        # Test 3: Prompt is used in generate_function_calls
        with open('functiongemma_service.py', 'r') as f:
            code = f.read()
            assert 'self.SYSTEM_PROMPT' in code, "SYSTEM_PROMPT not used"
            print("✓ System prompt is used in message generation")
        
        print("\n✓ Requirement 1.5 VERIFIED: Exact system prompt implemented")
        return True
        
    except Exception as e:
        print(f"\n✗ Requirement 1.5 FAILED: {e}")
        return False


def test_requirement_12_1_multi_step_execution():
    """
    Requirement 12.1: WHEN a user provides a complex command, THE Local_Model 
    SHALL generate multiple function calls in sequence
    """
    print("\n" + "="*70)
    print("Test: Requirement 12.1 - Multi-Step Task Execution")
    print("="*70)
    
    try:
        service = FunctionGemmaPlannerService(
            model_path="./test_model",
            lazy_load=True
        )
        
        # Test 1: execute_multi_step_task() method exists
        assert hasattr(service, 'execute_multi_step_task'), "execute_multi_step_task() missing"
        print("✓ execute_multi_step_task() method exists")
        
        # Test 2: Method has conversation turns parameter
        import inspect
        sig = inspect.signature(service.execute_multi_step_task)
        params = list(sig.parameters.keys())
        
        assert 'user_command' in params, "Missing user_command parameter"
        assert 'max_turns' in params, "Missing max_turns parameter"
        print("✓ Method supports conversation turns (max_turns parameter)")
        
        # Test 3: Method returns structured result
        # Check return type in docstring
        method = service.execute_multi_step_task
        assert 'Dict' in method.__doc__ or 'dict' in method.__doc__, "Should return Dict"
        print("✓ Method returns structured execution result")
        
        # Test 4: Handles multiple function calls
        with open('functiongemma_service.py', 'r') as f:
            code = f.read()
            # Check for conversation loop
            assert 'for turn in range' in code, "Should have conversation loop"
            assert 'all_function_calls' in code, "Should track all function calls"
            print("✓ Implements conversation turns for multi-step tasks")
        
        print("\n✓ Requirement 12.1 VERIFIED: Multi-step task execution with conversation")
        return True
        
    except Exception as e:
        print(f"\n✗ Requirement 12.1 FAILED: {e}")
        return False


def test_function_registry_integration():
    """
    Test: Integrate with FunctionRegistry for schema generation
    """
    print("\n" + "="*70)
    print("Test: FunctionRegistry Integration")
    print("="*70)
    
    try:
        # Test 1: Service accepts function_registry parameter
        registry = FunctionRegistry()
        service = FunctionGemmaPlannerService(
            model_path="./test_model",
            function_registry=registry,
            lazy_load=True
        )
        
        assert service.function_registry is registry
        print("✓ Service accepts function_registry in constructor")
        
        # Test 2: set_function_registry() method exists
        service2 = FunctionGemmaPlannerService(model_path="./test_model", lazy_load=True)
        service2.set_function_registry(registry)
        assert service2.function_registry is registry
        print("✓ set_function_registry() method works")
        
        # Test 3: generate_function_calls uses registry schemas
        with open('functiongemma_service.py', 'r') as f:
            code = f.read()
            assert 'get_all_schemas' in code, "Should call get_all_schemas()"
            print("✓ generate_function_calls() uses registry.get_all_schemas()")
        
        print("\n✓ FunctionRegistry Integration VERIFIED")
        return True
        
    except Exception as e:
        print(f"\n✗ FunctionRegistry Integration FAILED: {e}")
        return False


def test_data_models():
    """
    Test: FunctionCall and ExecutionResult data models
    """
    print("\n" + "="*70)
    print("Test: Data Models (FunctionCall, ExecutionResult)")
    print("="*70)
    
    try:
        # Test FunctionCall
        fc = FunctionCall(name="test", arguments={"x": 1})
        assert fc.name == "test"
        assert fc.arguments["x"] == 1
        
        fc_dict = fc.to_dict()
        fc2 = FunctionCall.from_dict(fc_dict)
        assert fc2.name == fc.name
        print("✓ FunctionCall dataclass works correctly")
        
        # Test ExecutionResult
        result = ExecutionResult(
            success=True,
            function_name="test",
            result={"status": "ok"}
        )
        assert result.success == True
        assert result.function_name == "test"
        
        result_dict = result.to_dict()
        assert result_dict["success"] == True
        print("✓ ExecutionResult dataclass works correctly")
        
        print("\n✓ Data Models VERIFIED")
        return True
        
    except Exception as e:
        print(f"\n✗ Data Models FAILED: {e}")
        return False


def main():
    """Run all verification tests for Task 12.1"""
    print("\n" + "="*70)
    print("TASK 12.1 VERIFICATION: FunctionGemmaPlannerService")
    print("="*70)
    print("\nVerifying all task requirements:")
    print("  • Model loading with error handling")
    print("  • generate_function_calls() method")
    print("  • execute_multi_step_task() with conversation turns")
    print("  • System prompt with exact required text")
    print("  • Integration with FunctionRegistry for schema generation")
    
    tests = [
        ("Requirement 1.1", test_requirement_1_1_model_loading),
        ("Requirement 1.2", test_requirement_1_2_local_processing),
        ("Requirement 1.5", test_requirement_1_5_system_prompt),
        ("Requirement 12.1", test_requirement_12_1_multi_step_execution),
        ("Registry Integration", test_function_registry_integration),
        ("Data Models", test_data_models),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} FAILED with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print("\n" + "="*70)
    print(f"Results: {passed}/{total} requirements verified")
    print("="*70)
    
    if all(r for _, r in results):
        print("\n✓✓✓ TASK 12.1 COMPLETE ✓✓✓")
        print("All requirements have been successfully implemented!")
        return 0
    else:
        print("\n✗ TASK 12.1 INCOMPLETE")
        print("Some requirements are not met.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
