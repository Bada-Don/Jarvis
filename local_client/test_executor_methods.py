"""
Quick test to check if PlanExecutor has the new file editing methods.
"""

import sys
from pathlib import Path
import inspect

# Add backend to path for file_editor import
backend_path = Path(__file__).parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Import the module, not the class
import plan_executor

# Get the PlanExecutor class
PlanExecutor = plan_executor.PlanExecutor

# Check for the new methods
methods_to_check = [
    '_execute_replace_in_file_step',
    '_execute_modify_lines_step',
    '_execute_insert_at_line_step',
    '_execute_delete_lines_step'
]

print("Checking PlanExecutor for new file editing methods:\n")
print("=" * 60)

all_found = True
for method_name in methods_to_check:
    # Check if method exists in the class
    has_method = hasattr(PlanExecutor, method_name)
    status = "✓ FOUND" if has_method else "✗ MISSING"
    print(f"{status}: {method_name}")
    if not has_method:
        all_found = False

print("=" * 60)

if all_found:
    print("\n✓ All methods found! The executor is ready.")
else:
    print("\n✗ Some methods are missing. Check if:")
    print("  1. The file was saved correctly")
    print("  2. Python cache was cleared")
    print("  3. The process was restarted")

# Check all methods in PlanExecutor
print("\n\nAll methods in PlanExecutor that contain 'replace' or 'modify':")
print("=" * 60)
for name in dir(PlanExecutor):
    if 'replace' in name.lower() or 'modify' in name.lower() or 'insert' in name.lower() or 'delete' in name.lower():
        if not name.startswith('__'):
            print(f"  - {name}")
