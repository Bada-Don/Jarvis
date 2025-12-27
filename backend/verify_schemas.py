"""
Verify that function schemas match actual function implementations.
"""

import sys
import inspect
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

import function_schemas
from functions import (
    folder_operations,
    file_operations,
    keyboard_operations,
    mouse_operations,
    window_management
)

# Map categories to modules
MODULES = {
    'folder_operations': folder_operations,
    'file_operations': file_operations,
    'keyboard_operations': keyboard_operations,
    'mouse_operations': mouse_operations,
    'window_management': window_management
}


def verify_schemas():
    """Verify all schemas match their function implementations."""
    print("Verifying function signatures match schemas...\n")
    
    all_match = True
    total_functions = 0
    matched_functions = 0
    
    for category, module in MODULES.items():
        print(f"\n{category.upper().replace('_', ' ')}:")
        print("-" * 60)
        
        schemas = function_schemas.get_schemas_by_category(category)
        
        for schema in schemas:
            total_functions += 1
            fname = schema['function']['name']
            
            if not hasattr(module, fname):
                print(f"  ✗ {fname}: function not found in module")
                all_match = False
                continue
            
            func = getattr(module, fname)
            sig = inspect.signature(func)
            
            # Get schema parameters (required and optional)
            schema_params = set(schema['function']['parameters']['properties'].keys())
            
            # Get function parameters (excluding 'self')
            func_params = set([p for p in sig.parameters.keys() if p != 'self'])
            
            if schema_params == func_params:
                print(f"  ✓ {fname}: parameters match")
                matched_functions += 1
            else:
                print(f"  ✗ {fname}: MISMATCH")
                print(f"      Schema params: {sorted(schema_params)}")
                print(f"      Function params: {sorted(func_params)}")
                all_match = False
    
    print("\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"  Total functions: {total_functions}")
    print(f"  Matched: {matched_functions}")
    print(f"  Mismatched: {total_functions - matched_functions}")
    print(f"  All match: {all_match}")
    print("=" * 60)
    
    return all_match


if __name__ == "__main__":
    success = verify_schemas()
    sys.exit(0 if success else 1)
