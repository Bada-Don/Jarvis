"""
Test Filename Resolver

Quick test script to verify filename resolution works correctly.
"""

import sys
from filename_resolver import resolve_filename

def test_resolve(directory: str, query: str):
    """Test filename resolution."""
    print(f"\n{'='*60}")
    print(f"Directory: {directory}")
    print(f"Query: '{query}'")
    print(f"{'='*60}")
    
    result = resolve_filename(directory, query)
    
    if result.success:
        print(f"✓ SUCCESS")
        print(f"  Resolved Name: {result.resolved_name}")
        print(f"  Full Path: {result.full_path}")
        print(f"  Confidence: {result.confidence:.1f}%")
        
        if result.candidates:
            print(f"\n  Top Candidates:")
            for i, (name, score) in enumerate(result.candidates, 1):
                marker = "→" if i == 1 else " "
                print(f"    {marker} {name} (score: {score:.2f})")
    else:
        print(f"✗ FAILED")
        print(f"  Error: {result.error_message}")
        
        if result.candidates:
            print(f"\n  Available files:")
            for name, score in result.candidates:
                print(f"    - {name} (score: {score:.2f})")
    
    print(f"{'='*60}\n")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python test_filename_resolver.py <directory> <query>")
        print("\nExample:")
        print('  python test_filename_resolver.py "C:\\Users\\harsh\\Desktop" "jarvis test"')
        sys.exit(1)
    
    directory = sys.argv[1]
    query = sys.argv[2]
    
    test_resolve(directory, query)
