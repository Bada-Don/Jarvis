"""
Basic tests for FunctionGemma Service

This script tests the basic functionality of the FunctionGemmaPlannerService
without requiring the actual model to be downloaded.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from functiongemma_service import FunctionGemmaPlannerService, FunctionCall, ExecutionResult


def test_initialization():
    """Test service initialization with lazy loading."""
    print("Test 1: Initialization with lazy loading...")
    
    try:
        service = FunctionGemmaPlannerService(
            model_path="./test_model_path",
            lazy_load=True
        )
        
        assert service.model_path == "./test_model_path"
        assert service._model_loaded == False
        assert service.processor is None
        assert service.model is None
        
        print("  ✓ Service initialized successfully with lazy loading")
        print(f"  ✓ Model path: {service.model_path}")
        print(f"  ✓ Model loaded: {service._model_loaded}")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def test_function_call_dataclass():
    """Test FunctionCall dataclass."""
    print("\nTest 2: FunctionCall dataclass...")
    
    try:
        # Create a function call
        fc = FunctionCall(
            name="test_function",
            arguments={"arg1": "value1", "arg2": 42}
        )
        
        assert fc.name == "test_function"
        assert fc.arguments["arg1"] == "value1"
        assert fc.arguments["arg2"] == 42
        
        # Test to_dict
        fc_dict = fc.to_dict()
        assert fc_dict["name"] == "test_function"
        assert fc_dict["arguments"]["arg1"] == "value1"
        
        # Test from_dict
        fc2 = FunctionCall.from_dict(fc_dict)
        assert fc2.name == fc.name
        assert fc2.arguments == fc.arguments
        
        print("  ✓ FunctionCall dataclass works correctly")
        print(f"  ✓ Created: {fc.name}({fc.arguments})")
        print(f"  ✓ Round-trip conversion successful")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def test_execution_result_dataclass():
    """Test ExecutionResult dataclass."""
    print("\nTest 3: ExecutionResult dataclass...")
    
    try:
        # Create an execution result
        result = ExecutionResult(
            success=True,
            function_name="test_function",
            result={"status": "ok", "data": "test"},
            error_message=None
        )
        
        assert result.success == True
        assert result.function_name == "test_function"
        assert result.result["status"] == "ok"
        assert result.error_message is None
        
        # Test to_dict
        result_dict = result.to_dict()
        assert result_dict["success"] == True
        assert result_dict["function_name"] == "test_function"
        
        print("  ✓ ExecutionResult dataclass works correctly")
        print(f"  ✓ Success: {result.success}")
        print(f"  ✓ Function: {result.function_name}")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def test_model_loading_without_model():
    """Test that model loading fails gracefully when model is not present."""
    print("\nTest 4: Model loading error handling...")
    
    try:
        service = FunctionGemmaPlannerService(
            model_path="./nonexistent_model_path",
            lazy_load=True
        )
        
        # Try to load model (should fail)
        try:
            service.load_model()
            print("  ✗ Expected FileNotFoundError but model loaded")
            return False
        except FileNotFoundError as e:
            print("  ✓ Correctly raised FileNotFoundError for missing model")
            print(f"  ✓ Error message: {str(e)[:80]}...")
            return True
        except Exception as e:
            print(f"  ✗ Unexpected error type: {type(e).__name__}")
            return False
            
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def test_is_loaded():
    """Test is_loaded method."""
    print("\nTest 5: is_loaded() method...")
    
    try:
        service = FunctionGemmaPlannerService(
            model_path="./test_model_path",
            lazy_load=True
        )
        
        assert service.is_loaded() == False
        print("  ✓ is_loaded() returns False before loading")
        
        # Simulate loading
        service._model_loaded = True
        assert service.is_loaded() == True
        print("  ✓ is_loaded() returns True after loading")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def test_unload_model():
    """Test model unloading."""
    print("\nTest 6: Model unloading...")
    
    try:
        service = FunctionGemmaPlannerService(
            model_path="./test_model_path",
            lazy_load=True
        )
        
        # Simulate loaded state
        service._model_loaded = True
        service.model = "fake_model"
        service.processor = "fake_processor"
        
        assert service.is_loaded() == True
        
        # Unload
        service.unload_model()
        
        assert service.is_loaded() == False
        assert service.model is None
        assert service.processor is None
        
        print("  ✓ Model unloaded successfully")
        print("  ✓ Memory cleared")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def test_set_function_registry():
    """Test setting function registry."""
    print("\nTest 7: Setting function registry...")
    
    try:
        service = FunctionGemmaPlannerService(
            model_path="./test_model_path",
            lazy_load=True
        )
        
        assert service.function_registry is None
        
        # Create a mock registry
        mock_registry = {"test": "registry"}
        service.set_function_registry(mock_registry)
        
        assert service.function_registry == mock_registry
        
        print("  ✓ Function registry set successfully")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("FunctionGemma Service Basic Tests")
    print("="*60)
    
    tests = [
        test_initialization,
        test_function_call_dataclass,
        test_execution_result_dataclass,
        test_model_loading_without_model,
        test_is_loaded,
        test_unload_model,
        test_set_function_registry
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("="*60)
    
    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
