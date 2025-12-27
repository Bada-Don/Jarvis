"""
Unit tests for folder operations module.

Tests the folder operation functions including create, delete, open, and list.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the functions directory to the path
sys.path.insert(0, str(Path(__file__).parent / "functions"))

from folder_operations import create_folder, delete_folder, open_folder, list_folder


def test_create_folder():
    """Test folder creation."""
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test creating a folder with absolute path
        test_folder = os.path.join(temp_dir, "test_folder")
        result = create_folder(test_folder)
        
        assert result["success"] is True, f"Failed to create folder: {result['message']}"
        assert os.path.exists(test_folder), "Folder was not created"
        assert os.path.isdir(test_folder), "Created path is not a directory"
        
        print("✓ test_create_folder passed")


def test_create_folder_already_exists():
    """Test creating a folder that already exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_folder = os.path.join(temp_dir, "existing_folder")
        os.makedirs(test_folder)
        
        # Should succeed with exist_ok=True
        result = create_folder(test_folder)
        assert result["success"] is True, f"Failed on existing folder: {result['message']}"
        
        print("✓ test_create_folder_already_exists passed")


def test_create_folder_empty_path():
    """Test creating a folder with empty path."""
    result = create_folder("")
    assert result["success"] is False, "Should fail with empty path"
    assert "empty" in result["message"].lower(), "Error message should mention empty path"
    
    print("✓ test_create_folder_empty_path passed")


def test_delete_folder_empty():
    """Test deleting an empty folder."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_folder = os.path.join(temp_dir, "to_delete")
        os.makedirs(test_folder)
        
        result = delete_folder(test_folder)
        assert result["success"] is True, f"Failed to delete folder: {result['message']}"
        assert not os.path.exists(test_folder), "Folder still exists after deletion"
        assert result["was_empty"] is True, "Should report folder was empty"
        
        print("✓ test_delete_folder_empty passed")


def test_delete_folder_non_empty_with_confirmation():
    """Test deleting a non-empty folder with confirmation required."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_folder = os.path.join(temp_dir, "non_empty")
        os.makedirs(test_folder)
        
        # Create a file inside
        test_file = os.path.join(test_folder, "file.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        # Should fail with confirm_non_empty=True (default)
        result = delete_folder(test_folder, confirm_non_empty=True)
        assert result["success"] is False, "Should fail to delete non-empty folder with confirmation"
        assert os.path.exists(test_folder), "Folder should still exist"
        assert result["was_empty"] is False, "Should report folder was not empty"
        
        print("✓ test_delete_folder_non_empty_with_confirmation passed")


def test_delete_folder_non_empty_without_confirmation():
    """Test deleting a non-empty folder without confirmation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_folder = os.path.join(temp_dir, "non_empty")
        os.makedirs(test_folder)
        
        # Create a file inside
        test_file = os.path.join(test_folder, "file.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        # Should succeed with confirm_non_empty=False
        result = delete_folder(test_folder, confirm_non_empty=False)
        assert result["success"] is True, f"Failed to delete folder: {result['message']}"
        assert not os.path.exists(test_folder), "Folder still exists after deletion"
        assert result["was_empty"] is False, "Should report folder was not empty"
        
        print("✓ test_delete_folder_non_empty_without_confirmation passed")


def test_delete_folder_not_exists():
    """Test deleting a folder that doesn't exist."""
    result = delete_folder("/nonexistent/path/to/folder")
    assert result["success"] is False, "Should fail for non-existent folder"
    assert "not exist" in result["message"].lower() or "resolve" in result["message"].lower()
    
    print("✓ test_delete_folder_not_exists passed")


def test_list_folder():
    """Test listing folder contents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some files and folders
        os.makedirs(os.path.join(temp_dir, "subfolder1"))
        os.makedirs(os.path.join(temp_dir, "subfolder2"))
        
        with open(os.path.join(temp_dir, "file1.txt"), 'w') as f:
            f.write("test")
        with open(os.path.join(temp_dir, "file2.txt"), 'w') as f:
            f.write("test")
        
        result = list_folder(temp_dir)
        assert result["success"] is True, f"Failed to list folder: {result['message']}"
        assert len(result["contents"]) == 4, f"Expected 4 items, got {len(result['contents'])}"
        assert "subfolder1" in result["contents"], "subfolder1 not in contents"
        assert "subfolder2" in result["contents"], "subfolder2 not in contents"
        assert "file1.txt" in result["contents"], "file1.txt not in contents"
        assert "file2.txt" in result["contents"], "file2.txt not in contents"
        
        print("✓ test_list_folder passed")


def test_list_folder_empty():
    """Test listing an empty folder."""
    with tempfile.TemporaryDirectory() as temp_dir:
        result = list_folder(temp_dir)
        assert result["success"] is True, f"Failed to list folder: {result['message']}"
        assert len(result["contents"]) == 0, "Empty folder should have no contents"
        
        print("✓ test_list_folder_empty passed")


def test_list_folder_not_exists():
    """Test listing a folder that doesn't exist."""
    result = list_folder("/nonexistent/path/to/folder")
    assert result["success"] is False, "Should fail for non-existent folder"
    assert "not exist" in result["message"].lower() or "resolve" in result["message"].lower()
    
    print("✓ test_list_folder_not_exists passed")


def test_list_folder_empty_path():
    """Test listing with empty path."""
    result = list_folder("")
    assert result["success"] is False, "Should fail with empty path"
    assert "empty" in result["message"].lower(), "Error message should mention empty path"
    
    print("✓ test_list_folder_empty_path passed")


if __name__ == "__main__":
    print("Running folder operations tests...\n")
    
    try:
        test_create_folder()
        test_create_folder_already_exists()
        test_create_folder_empty_path()
        test_delete_folder_empty()
        test_delete_folder_non_empty_with_confirmation()
        test_delete_folder_non_empty_without_confirmation()
        test_delete_folder_not_exists()
        test_list_folder()
        test_list_folder_empty()
        test_list_folder_not_exists()
        test_list_folder_empty_path()
        
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
