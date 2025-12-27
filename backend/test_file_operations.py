"""
Unit tests for file operations module.

Tests the file operation functions including delete, rename, copy, move, and open.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the functions directory to the path
sys.path.insert(0, str(Path(__file__).parent / "functions"))

from file_operations import delete_file, rename_file, copy_file, move_file, open_file


def test_delete_file():
    """Test file deletion."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file
        test_file = os.path.join(temp_dir, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        result = delete_file(test_file, confirm=False)
        assert result["success"] is True, f"Failed to delete file: {result['message']}"
        assert not os.path.exists(test_file), "File still exists after deletion"
        
        print("✓ test_delete_file passed")


def test_delete_file_not_exists():
    """Test deleting a file that doesn't exist."""
    result = delete_file("/nonexistent/path/to/file.txt")
    assert result["success"] is False, "Should fail for non-existent file"
    assert "not exist" in result["message"].lower() or "resolve" in result["message"].lower()
    
    print("✓ test_delete_file_not_exists passed")


def test_delete_file_empty_path():
    """Test deleting with empty path."""
    result = delete_file("")
    assert result["success"] is False, "Should fail with empty path"
    assert "empty" in result["message"].lower(), "Error message should mention empty path"
    
    print("✓ test_delete_file_empty_path passed")


def test_rename_file():
    """Test file renaming."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file
        old_file = os.path.join(temp_dir, "old_name.txt")
        with open(old_file, 'w') as f:
            f.write("test content")
        
        result = rename_file(old_file, "new_name.txt")
        assert result["success"] is True, f"Failed to rename file: {result['message']}"
        assert not os.path.exists(old_file), "Old file still exists"
        
        new_file = os.path.join(temp_dir, "new_name.txt")
        assert os.path.exists(new_file), "New file doesn't exist"
        
        # Verify content is preserved
        with open(new_file, 'r') as f:
            content = f.read()
        assert content == "test content", "File content was not preserved"
        
        print("✓ test_rename_file passed")


def test_rename_file_already_exists():
    """Test renaming to a name that already exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create two test files
        old_file = os.path.join(temp_dir, "old_name.txt")
        with open(old_file, 'w') as f:
            f.write("old content")
        
        existing_file = os.path.join(temp_dir, "existing.txt")
        with open(existing_file, 'w') as f:
            f.write("existing content")
        
        result = rename_file(old_file, "existing.txt")
        assert result["success"] is False, "Should fail when new name already exists"
        assert "already exists" in result["message"].lower()
        
        print("✓ test_rename_file_already_exists passed")


def test_rename_file_empty_name():
    """Test renaming with empty new name."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        result = rename_file(test_file, "")
        assert result["success"] is False, "Should fail with empty new name"
        assert "empty" in result["message"].lower()
        
        print("✓ test_rename_file_empty_name passed")


def test_copy_file():
    """Test file copying."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create source file
        source_file = os.path.join(temp_dir, "source.txt")
        with open(source_file, 'w') as f:
            f.write("test content")
        
        # Copy to new location
        dest_file = os.path.join(temp_dir, "destination.txt")
        result = copy_file(source_file, dest_file)
        
        assert result["success"] is True, f"Failed to copy file: {result['message']}"
        assert os.path.exists(source_file), "Source file was removed"
        assert os.path.exists(dest_file), "Destination file doesn't exist"
        
        # Verify content
        with open(dest_file, 'r') as f:
            content = f.read()
        assert content == "test content", "File content was not copied correctly"
        
        print("✓ test_copy_file passed")


def test_copy_file_to_directory():
    """Test copying file to a directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create source file
        source_file = os.path.join(temp_dir, "source.txt")
        with open(source_file, 'w') as f:
            f.write("test content")
        
        # Create destination directory
        dest_dir = os.path.join(temp_dir, "dest_folder")
        os.makedirs(dest_dir)
        
        # Copy to directory
        result = copy_file(source_file, dest_dir)
        
        assert result["success"] is True, f"Failed to copy file: {result['message']}"
        
        # Check file exists in destination directory with same name
        dest_file = os.path.join(dest_dir, "source.txt")
        assert os.path.exists(dest_file), "File not copied to directory"
        
        print("✓ test_copy_file_to_directory passed")


def test_copy_file_already_exists():
    """Test copying to a destination that already exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        source_file = os.path.join(temp_dir, "source.txt")
        with open(source_file, 'w') as f:
            f.write("source content")
        
        dest_file = os.path.join(temp_dir, "dest.txt")
        with open(dest_file, 'w') as f:
            f.write("dest content")
        
        result = copy_file(source_file, dest_file)
        assert result["success"] is False, "Should fail when destination exists"
        assert "already exists" in result["message"].lower()
        
        print("✓ test_copy_file_already_exists passed")


def test_move_file():
    """Test file moving."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create source file
        source_file = os.path.join(temp_dir, "source.txt")
        with open(source_file, 'w') as f:
            f.write("test content")
        
        # Move to new location
        dest_file = os.path.join(temp_dir, "destination.txt")
        result = move_file(source_file, dest_file)
        
        assert result["success"] is True, f"Failed to move file: {result['message']}"
        assert not os.path.exists(source_file), "Source file still exists"
        assert os.path.exists(dest_file), "Destination file doesn't exist"
        
        # Verify content
        with open(dest_file, 'r') as f:
            content = f.read()
        assert content == "test content", "File content was not moved correctly"
        
        print("✓ test_move_file passed")


def test_move_file_to_directory():
    """Test moving file to a directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create source file
        source_file = os.path.join(temp_dir, "source.txt")
        with open(source_file, 'w') as f:
            f.write("test content")
        
        # Create destination directory
        dest_dir = os.path.join(temp_dir, "dest_folder")
        os.makedirs(dest_dir)
        
        # Move to directory
        result = move_file(source_file, dest_dir)
        
        assert result["success"] is True, f"Failed to move file: {result['message']}"
        assert not os.path.exists(source_file), "Source file still exists"
        
        # Check file exists in destination directory with same name
        dest_file = os.path.join(dest_dir, "source.txt")
        assert os.path.exists(dest_file), "File not moved to directory"
        
        print("✓ test_move_file_to_directory passed")


def test_move_file_already_exists():
    """Test moving to a destination that already exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        source_file = os.path.join(temp_dir, "source.txt")
        with open(source_file, 'w') as f:
            f.write("source content")
        
        dest_file = os.path.join(temp_dir, "dest.txt")
        with open(dest_file, 'w') as f:
            f.write("dest content")
        
        result = move_file(source_file, dest_file)
        assert result["success"] is False, "Should fail when destination exists"
        assert "already exists" in result["message"].lower()
        assert os.path.exists(source_file), "Source file was removed despite failure"
        
        print("✓ test_move_file_already_exists passed")


def test_open_file_not_exists():
    """Test opening a file that doesn't exist."""
    result = open_file("/nonexistent/path/to/file.txt")
    assert result["success"] is False, "Should fail for non-existent file"
    assert "not exist" in result["message"].lower() or "resolve" in result["message"].lower()
    
    print("✓ test_open_file_not_exists passed")


def test_open_file_empty_path():
    """Test opening with empty path."""
    result = open_file("")
    assert result["success"] is False, "Should fail with empty path"
    assert "empty" in result["message"].lower()
    
    print("✓ test_open_file_empty_path passed")


if __name__ == "__main__":
    print("Running file operations tests...\n")
    
    try:
        test_delete_file()
        test_delete_file_not_exists()
        test_delete_file_empty_path()
        test_rename_file()
        test_rename_file_already_exists()
        test_rename_file_empty_name()
        test_copy_file()
        test_copy_file_to_directory()
        test_copy_file_already_exists()
        test_move_file()
        test_move_file_to_directory()
        test_move_file_already_exists()
        test_open_file_not_exists()
        test_open_file_empty_path()
        
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
