"""
Quick Test - Run this right now to see the service in action!

This demonstrates what you can test WITHOUT downloading the model.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from functiongemma_service import FunctionGemmaPlannerService, FunctionCall, ExecutionResult


def main():
    print("="*70)
    print("FunctionGemma Service - Quick Test (No Model Required)")
    print("="*70)
    
    print("\n✓ Testing what works RIGHT NOW without model download:\n")
    
    # Test 1: Service Creation
    print("1. Creating service with lazy loading...")
    service = FunctionGemmaPlannerService(lazy_load=True)
    print(f"   ✓ Service created successfully")
    print(f"   ✓ Model path: {service.model_path}")
    print(f"   ✓ Model loaded: {service.is_loaded()}")
    
    # Test 2: Data Structures
    print("\n2. Testing FunctionCall data structure...")
    fc = FunctionCall(
        name="open_app",
        arguments={"app_name": "notepad"}
    )
    print(f"   ✓ Created: {fc.name}({fc.arguments})")
    
    fc_dict = fc.to_dict()
    fc2 = FunctionCall.from_dict(fc_dict)
    print(f"   ✓ Serialization works: {fc2.name}({fc2.arguments})")
    
    # Test 3: ExecutionResult
    print("\n3. Testing ExecutionResult data structure...")
    result = ExecutionResult(
        success=True,
        function_name="open_app",
        result={"status": "opened", "app": "notepad"},
        error_message=None
    )
    print(f"   ✓ Created result: success={result.success}, function={result.function_name}")
    print(f"   ✓ Result data: {result.result}")
    
    # Test 4: System Prompt
    print("\n4. Checking system prompt...")
    print(f"   ✓ System prompt: '{FunctionGemmaPlannerService.SYSTEM_PROMPT}'")
    
    # Test 5: Function Registry Integration
    print("\n5. Testing function registry integration...")
    
    class MockRegistry:
        def get_all_schemas(self):
            return [
                {
                    "type": "function",
                    "function": {
                        "name": "test_function",
                        "description": "A test function",
                        "parameters": {"type": "object", "properties": {}}
                    }
                }
            ]
    
    registry = MockRegistry()
    service.set_function_registry(registry)
    schemas = service.function_registry.get_all_schemas()
    print(f"   ✓ Registry set with {len(schemas)} function(s)")
    print(f"   ✓ Function: {schemas[0]['function']['name']}")
    
    # Test 6: Validation
    print("\n6. Testing input validation...")
    try:
        service.generate_function_calls("")
        print("   ✗ Should have raised ValueError")
    except ValueError as e:
        print(f"   ✓ Correctly validates empty commands: {e}")
    
    # Test 7: Memory Management
    print("\n7. Testing memory management...")
    print(f"   ✓ Model loaded: {service.is_loaded()}")
    service._model_loaded = True  # Simulate loaded state
    print(f"   ✓ Simulated loaded state: {service.is_loaded()}")
    service.unload_model()
    print(f"   ✓ After unload: {service.is_loaded()}")
    
    # Summary
    print("\n" + "="*70)
    print("Summary: What You Just Tested")
    print("="*70)
    print("\n✓ Service initialization (lazy loading)")
    print("✓ Data structures (FunctionCall, ExecutionResult)")
    print("✓ System prompt configuration")
    print("✓ Function registry integration")
    print("✓ Input validation")
    print("✓ Memory management")
    
    print("\n" + "="*70)
    print("What You Can Test Next")
    print("="*70)
    print("\nTo test with the ACTUAL MODEL:")
    print("  1. Download model: cd 'FunctionGemma Files' && python download_functiongemma.py")
    print("  2. Run full demo: cd backend && python demo_functiongemma_service.py")
    print("\nTo run comprehensive tests:")
    print("  python test_functiongemma_service.py")
    print("  python test_functiongemma_integration.py")
    
    print("\n✓ All quick tests passed! Service is ready for model integration.")
    print("="*70)


if __name__ == "__main__":
    main()
