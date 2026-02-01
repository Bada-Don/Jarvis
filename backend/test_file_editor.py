"""
Test script for the intelligent file editor module.
"""

import os
import tempfile
from pathlib import Path
from file_editor import FileEditor


def test_file_editor():
    """Test all file editor operations."""
    
    editor = FileEditor()
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        f.write("Line 1: Name: John Doe\n")
        f.write("Line 2: Age: 30\n")
        f.write("Line 3: City: New York\n")
        f.write("Line 4: Country: USA\n")
    
    print(f"Created test file: {test_file}\n")
    
    try:
        # Test 1: Read file with context
        print("=" * 60)
        print("TEST 1: Read file with context")
        print("=" * 60)
        success, msg, data = editor.read_file_with_context(test_file)
        if success:
            print(f"✓ {msg}")
            print("\nFile content with line numbers:")
            print(data['numbered_content'])
            print(f"\nTotal lines: {data['line_count']}")
        else:
            print(f"✗ {msg}")
        
        # Test 2: Replace in file
        print("\n" + "=" * 60)
        print("TEST 2: Replace text in file")
        print("=" * 60)
        success, msg, diff = editor.replace_in_file(
            test_file,
            "John Doe",
            "Harshit Singla"
        )
        if success:
            print(f"✓ {msg}")
            print("\nDiff:")
            print(diff)
        else:
            print(f"✗ {msg}")
        
        # Test 3: Modify lines
        print("\n" + "=" * 60)
        print("TEST 3: Modify specific line")
        print("=" * 60)
        success, msg, diff = editor.modify_lines(
            test_file,
            line_number=2,
            new_content="Line 2: Age: 25\n"
        )
        if success:
            print(f"✓ {msg}")
            print("\nDiff:")
            print(diff)
        else:
            print(f"✗ {msg}")
        
        # Test 4: Insert at line
        print("\n" + "=" * 60)
        print("TEST 4: Insert new line")
        print("=" * 60)
        success, msg, diff = editor.insert_at_line(
            test_file,
            line_number=3,
            content="Line 2.5: Email: harshit@example.com\n"
        )
        if success:
            print(f"✓ {msg}")
            print("\nDiff:")
            print(diff)
        else:
            print(f"✗ {msg}")
        
        # Test 5: Delete lines
        print("\n" + "=" * 60)
        print("TEST 5: Delete lines")
        print("=" * 60)
        success, msg, diff = editor.delete_lines(
            test_file,
            start_line=4,
            end_line=4
        )
        if success:
            print(f"✓ {msg}")
            print("\nDiff:")
            print(diff)
        else:
            print(f"✗ {msg}")
        
        # Final: Read and display final content
        print("\n" + "=" * 60)
        print("FINAL: File content after all operations")
        print("=" * 60)
        success, msg, data = editor.read_file_with_context(test_file)
        if success:
            print(data['numbered_content'])
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\nCleaned up test file: {test_file}")


if __name__ == "__main__":
    test_file_editor()
