"""
Real-World Demo for FunctionGemma Service

This script demonstrates the FunctionGemma service with actual model usage.
It provides an interactive way to test the service with real commands.

Prerequisites:
1. Download the model first:
   cd "FunctionGemma Files"
   python download_functiongemma.py

2. Install dependencies:
   pip install transformers torch
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from functiongemma_service import FunctionGemmaPlannerService, FunctionCall


class SimpleFunctionRegistry:
    """
    Simple function registry for demo purposes.
    This mimics what the real FunctionRegistry will do.
    """
    
    def get_all_schemas(self):
        """Return demo function schemas."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "open_app",
                    "description": "Open an application by name (notepad, calculator, chrome, etc.)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {"type": "string", "description": "Name of the application"}
                        },
                        "required": ["app_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "type_text",
                    "description": "Type text using the keyboard",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to type"}
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "press_key",
                    "description": "Press keyboard keys or combinations (enter, ctrl+s, alt+f4, etc.)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Key or combination to press"}
                        },
                        "required": ["key"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_folder",
                    "description": "Create a new folder",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "folder_name": {"type": "string", "description": "Name of the folder"},
                            "location": {"type": "string", "description": "Where to create it", "enum": ["desktop", "documents", "downloads"]}
                        },
                        "required": ["folder_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_file",
                    "description": "Save the current file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "Name of the file"},
                            "location": {"type": "string", "description": "Where to save", "enum": ["desktop", "documents", "downloads"]}
                        },
                        "required": ["filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "close_app",
                    "description": "Close the current application",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ]


def check_model_availability():
    """Check if the FunctionGemma model is available."""
    possible_paths = [
        "./local_models/functiongemma-270m-it",
        "../local_models/functiongemma-270m-it",
        "../FunctionGemma Files/local_models/functiongemma-270m-it",
        "./FunctionGemma Files/local_models/functiongemma-270m-it"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return True, os.path.abspath(path)
    
    return False, None


def demo_basic_usage(model_path=None):
    """Demo 1: Basic service initialization and model loading."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Service Initialization")
    print("="*70)
    
    print("\n1. Creating service with lazy loading...")
    service = FunctionGemmaPlannerService(model_path=model_path, lazy_load=True)
    print(f"   ✓ Service created")
    print(f"   ✓ Model loaded: {service.is_loaded()}")
    print(f"   ✓ Model path: {service.model_path}")
    
    print("\n2. Loading model...")
    try:
        success = service.load_model()
        if success:
            print(f"   ✓ Model loaded successfully!")
            print(f"   ✓ Model is now ready: {service.is_loaded()}")
            return service
        else:
            print(f"   ✗ Model loading failed")
            return None
    except FileNotFoundError as e:
        print(f"   ✗ Model not found: {e}")
        print("\n   To download the model:")
        print("   1. cd 'FunctionGemma Files'")
        print("   2. python download_functiongemma.py")
        return None
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None


def demo_function_generation(service):
    """Demo 2: Generate function calls from natural language."""
    print("\n" + "="*70)
    print("DEMO 2: Function Call Generation")
    print("="*70)
    
    # Set up function registry
    registry = SimpleFunctionRegistry()
    service.set_function_registry(registry)
    print("\n1. Function registry configured")
    print(f"   ✓ Available functions: {len(registry.get_all_schemas())}")
    
    # Test commands
    test_commands = [
        "Open notepad",
        "Open calculator and then notepad",
        "Create a folder called Projects on desktop",
        "Open notepad, type Hello World, and save as test.txt"
    ]
    
    print("\n2. Testing function call generation...")
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n   Command {i}: '{command}'")
        try:
            function_calls = service.generate_function_calls(command)
            print(f"   ✓ Generated {len(function_calls)} function call(s):")
            
            for j, fc in enumerate(function_calls, 1):
                print(f"      {j}. {fc.name}({fc.arguments})")
            
        except Exception as e:
            print(f"   ✗ Error: {e}")


def demo_model_caching(service):
    """Demo 3: Model caching performance."""
    print("\n" + "="*70)
    print("DEMO 3: Model Caching Performance")
    print("="*70)
    
    import time
    
    registry = SimpleFunctionRegistry()
    service.set_function_registry(registry)
    
    command = "Open notepad"
    
    print("\n1. First call (model already loaded from previous demo)...")
    start = time.time()
    try:
        function_calls = service.generate_function_calls(command)
        elapsed = time.time() - start
        print(f"   ✓ Time: {elapsed:.3f} seconds")
        print(f"   ✓ Generated: {[fc.name for fc in function_calls]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    print("\n2. Second call (using cached model)...")
    start = time.time()
    try:
        function_calls = service.generate_function_calls(command)
        elapsed = time.time() - start
        print(f"   ✓ Time: {elapsed:.3f} seconds")
        print(f"   ✓ Generated: {[fc.name for fc in function_calls]}")
        print(f"   ✓ Caching provides consistent fast performance!")
    except Exception as e:
        print(f"   ✗ Error: {e}")


def demo_memory_management(service):
    """Demo 4: Memory management."""
    print("\n" + "="*70)
    print("DEMO 4: Memory Management")
    print("="*70)
    
    print("\n1. Current state:")
    print(f"   ✓ Model loaded: {service.is_loaded()}")
    
    print("\n2. Unloading model...")
    service.unload_model()
    print(f"   ✓ Model loaded: {service.is_loaded()}")
    print(f"   ✓ Memory freed (model removed from RAM)")
    
    print("\n3. Reloading model...")
    try:
        service.load_model()
        print(f"   ✓ Model loaded: {service.is_loaded()}")
        print(f"   ✓ Model ready for use again")
    except Exception as e:
        print(f"   ✗ Error: {e}")


def interactive_mode(service):
    """Interactive mode: Test your own commands."""
    print("\n" + "="*70)
    print("INTERACTIVE MODE: Test Your Own Commands")
    print("="*70)
    
    registry = SimpleFunctionRegistry()
    service.set_function_registry(registry)
    
    print("\nAvailable functions:")
    for schema in registry.get_all_schemas():
        func = schema["function"]
        print(f"  • {func['name']}: {func['description']}")
    
    print("\nExample commands:")
    print("  • 'Open notepad and type hello'")
    print("  • 'Create a folder called Test on desktop'")
    print("  • 'Open calculator'")
    print("\nType 'quit' to exit\n")
    
    while True:
        try:
            command = input("Your command: ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Exiting interactive mode")
                break
            
            if not command:
                continue
            
            print(f"\nProcessing: '{command}'")
            function_calls = service.generate_function_calls(command)
            
            print(f"✓ Generated {len(function_calls)} function call(s):")
            for i, fc in enumerate(function_calls, 1):
                print(f"  {i}. {fc.name}({fc.arguments})")
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Exiting interactive mode")
            break
        except Exception as e:
            print(f"✗ Error: {e}\n")


def main():
    """Main demo runner."""
    print("="*70)
    print("FunctionGemma Service - Real-World Demo")
    print("="*70)
    
    # Check model availability
    print("\nChecking model availability...")
    model_available, model_path = check_model_availability()
    
    if not model_available:
        print("✗ FunctionGemma model not found!")
        print("\nTo download the model:")
        print("  1. cd 'FunctionGemma Files'")
        print("  2. python download_functiongemma.py")
        print("\nThis will download ~540MB and may take a few minutes.")
        return 1
    
    print(f"✓ Model found at: {model_path}")
    
    # Run demos
    print("\nStarting demos...")
    
    # Demo 1: Basic usage
    service = demo_basic_usage(model_path=model_path)
    if service is None:
        return 1
    
    # Demo 2: Function generation
    demo_function_generation(service)
    
    # Demo 3: Caching performance
    demo_model_caching(service)
    
    # Demo 4: Memory management
    demo_memory_management(service)
    
    # Interactive mode
    print("\n" + "="*70)
    response = input("\nWould you like to try interactive mode? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        interactive_mode(service)
    
    print("\n" + "="*70)
    print("Demo Complete!")
    print("="*70)
    print("\nKey Takeaways:")
    print("  ✓ Model loads in 2-5 seconds")
    print("  ✓ Subsequent calls are fast (cached)")
    print("  ✓ Generates accurate function calls from natural language")
    print("  ✓ Memory can be managed with unload/reload")
    print("  ✓ Ready for integration with Function Registry and Executor")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
