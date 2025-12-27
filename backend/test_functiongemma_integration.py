"""
Integration tests for FunctionGemma Service

These tests verify the service integrates correctly with the expected
model interface, even without the actual model downloaded.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from functiongemma_service import FunctionGemmaPlannerService, FunctionCall


class MockFunctionRegistry:
    """Mock function registry for testing."""
    
    def get_all_schemas(self):
        """Return mock function schemas."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "open_app",
                    "description": "Open an application",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {"type": "string"}
                        },
                        "required": ["app_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "type_text",
                    "description": "Type text",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"}
                        },
                        "required": ["text"]
                    }
                }
            }
        ]


def test_service_with_registry():
    """Test service initialization with function registry."""
    print("Test 1: Service with function registry...")
    
    try:
        registry = MockFunctionRegistry()
        service = FunctionGemmaPlannerService(
            model_path="./test_model",
            function_registry=registry,
            lazy_load=True
        )
        
        assert service.function_registry is not None
        schemas = service.function_registry.get_all_schemas()
        assert len(schemas) == 2
        assert schemas[0]["function"]["name"] == "open_app"
        
        print("  ✓ Service initialized with function registry")
        print(f"  ✓ Registry has {len(schemas)} functions")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def test_generate_function_calls_validation():
    """Test validation in generate_function_calls."""
    print("\nTest 2: generate_function_calls validation...")
    
    try:
        service = FunctionGemmaPlannerService(
            model_path="./test_model",
            lazy_load=True
        )
        
        # Test empty command
        try:
            service.generate_function_calls("")
            print("  ✗ Should have raised ValueError for empty command")
            return False
        except ValueError as e:
            print("  ✓ Correctly raised ValueError for empty command")
        
        # Test without registry
        try:
            service.generate_function_calls("test command")
            print("  ✗ Should have raised ValueError for missing registry")
            return False
        except ValueError as e:
            print("  ✓ Correctly raised ValueError for missing registry")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def test_execute_multi_step_validation():
    """Test validation in execute_multi_step_task."""
    print("\nTest 3: execute_multi_step_task validation...")
    
    try:
        service = FunctionGemmaPlannerService(
            model_path="./test_model",
            lazy_load=True
        )
        
        # Test empty command
        try:
            service.execute_multi_step_task("")
            print("  ✗ Should have raised ValueError for empty command")
            return False
        except ValueError as e:
            print("  ✓ Correctly raised ValueError for empty command")
        
        # Test without registry
        try:
            service.execute_multi_step_task("test command")
            print("  ✗ Should have raised ValueError for missing registry")
            return False
        except ValueError as e:
            print("  ✓ Correctly raised ValueError for missing registry")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def test_system_prompt():
    """Test that system prompt is correctly set."""
    print("\nTest 4: System prompt...")
    
    try:
        expected_prompt = "You are a model that can do function calling with the following functions"
        
        assert FunctionGemmaPlannerService.SYSTEM_PROMPT == expected_prompt
        
        print("  ✓ System prompt is correctly set")
        print(f"  ✓ Prompt: {FunctionGemmaPlannerService.SYSTEM_PROMPT}")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def test_model_path_detection():
    """Test automatic model path detection."""
    print("\nTest 5: Model path detection...")
    
    try:
        # Test with no path provided
        service = FunctionGemmaPlannerService(lazy_load=True)
        
        # Should have set a default path
        assert service.model_path is not None
        assert isinstance(service.model_path, str)
        
        print("  ✓ Default model path set")
        print(f"  ✓ Path: {service.model_path}")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def test_lazy_vs_eager_loading():
    """Test lazy vs eager loading behavior."""
    print("\nTest 6: Lazy vs eager loading...")
    
    try:
        # Test lazy loading
        service_lazy = FunctionGemmaPlannerService(
            model_path="./test_model",
            lazy_load=True
        )
        assert service_lazy.is_loaded() == False
        print("  ✓ Lazy loading: model not loaded on init")
        
        # Test eager loading (will fail without model, but that's expected)
        try:
            service_eager = FunctionGemmaPlannerService(
                model_path="./nonexistent_model",
                lazy_load=False
            )
            print("  ✗ Eager loading should have failed without model")
            return False
        except (FileNotFoundError, Exception):
            print("  ✓ Eager loading: attempted to load model on init")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def test_function_call_structure():
    """Test FunctionCall structure matches expected format."""
    print("\nTest 7: FunctionCall structure...")
    
    try:
        fc = FunctionCall(
            name="open_app",
            arguments={"app_name": "notepad"}
        )
        
        # Test dict format
        fc_dict = fc.to_dict()
        assert "name" in fc_dict
        assert "arguments" in fc_dict
        assert fc_dict["name"] == "open_app"
        assert fc_dict["arguments"]["app_name"] == "notepad"
        
        # Test round-trip
        fc2 = FunctionCall.from_dict(fc_dict)
        assert fc2.name == fc.name
        assert fc2.arguments == fc.arguments
        
        print("  ✓ FunctionCall structure is correct")
        print(f"  ✓ Format: {fc_dict}")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def main():
    """Run all integration tests."""
    print("="*60)
    print("FunctionGemma Service Integration Tests")
    print("="*60)
    
    tests = [
        test_service_with_registry,
        test_generate_function_calls_validation,
        test_execute_multi_step_validation,
        test_system_prompt,
        test_model_path_detection,
        test_lazy_vs_eager_loading,
        test_function_call_structure
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("="*60)
    
    if all(results):
        print("✓ All integration tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
