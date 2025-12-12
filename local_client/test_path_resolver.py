"""
Test Path Resolver

Quick test script to verify path resolution works correctly.
"""

import sys
from path_resolver import resolve_path

def test_resolve(path_query: str):
    """Test path resolution."""
    print(f"\n{'='*60}")
    print(f"Path Query: '{path_query}'")
    print(f"{'='*60}")
    
    result = resolve_path(path_query)
    
    if result.success:
        print(f"✓ SUCCESS")
        print(f"  Resolved Path: {result.resolved_path}")
        
        if result.resolution_steps:
            print(f"\n  Resolution Steps:")
            for step in result.resolution_steps:
                print(f"    {step}")
    else:
        print(f"✗ FAILED")
        print(f"  Error: {result.error_message}")
        
        if result.resolution_steps:
            print(f"\n  Partial Resolution:")
            for step in result.resolution_steps:
                print(f"    {step}")
    
    print(f"{'='*60}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_path_resolver.py <path_query>")
        print("\nExamples:")
        print('  python test_path_resolver.py "desktop/jarvis test"')
        print('  python test_path_resolver.py "documents/report.pdf"')
        print('  python test_path_resolver.py "desktop/new brif case/maan 22.pdf"')
        sys.exit(1)
    
    path_query = sys.argv[1]
    test_resolve(path_query)
