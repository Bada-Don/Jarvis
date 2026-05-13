"""
File Operations Module for Plane 2: Code Workspace Control

This module provides reliable file system operations that bypass UI interactions.
These operations are deterministic, fast, and don't depend on OCR or vision.

Operations:
- write_file: Create or overwrite a file with content
- read_file: Read file contents
- append_file: Append content to existing file
- delete_file: Delete a file
- create_directory: Create a directory
"""

import os
from pathlib import Path
from typing import Optional, Tuple


class FileOperationError(Exception):
    """Raised when a file operation fails."""
    pass


def write_file(path: str, content: str, encoding: str = 'utf-8') -> Tuple[bool, str]:
    """
    Write content to a file, creating it if it doesn't exist or overwriting if it does.
    
    This is the core of Plane 2 workspace control - reliable file creation/editing
    without UI interaction.
    
    Args:
        path: Absolute or relative file path (supports ~ for home directory and %VAR% for environment variables)
        content: Text content to write to the file
        encoding: File encoding (default: utf-8)
    
    Returns:
        Tuple[bool, str]: (success, message)
        
    Examples:
        >>> write_file("~/Desktop/test.py", "print('Hello')")
        (True, "File written successfully: C:\\Users\\user\\Desktop\\test.py")
        
        >>> write_file("%USERPROFILE%\\Desktop\\test.py", "print('Hello')")
        (True, "File written successfully: C:\\Users\\user\\Desktop\\test.py")
        
        >>> write_file("C:\\temp\\script.py", "def bubble_sort(arr):\\n    pass")
        (True, "File written successfully: C:\\temp\\script.py")
    """
    try:
        # Expand user home directory if present (~ style) FIRST
        file_path = Path(path).expanduser()
        
        # Then expand environment variables (Windows %VAR% style)
        file_path = Path(os.path.expandvars(str(file_path)))
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        file_path.write_text(content, encoding=encoding)
        
        return True, f"File written successfully: {file_path}"
        
    except PermissionError:
        return False, f"Permission denied: {path}"
    except OSError as e:
        return False, f"OS error writing file: {e}"
    except Exception as e:
        return False, f"Error writing file: {e}"


def read_file(path: str, encoding: str = 'utf-8') -> Tuple[bool, str, Optional[str]]:
    """
    Read content from a file.
    
    Args:
        path: Absolute or relative file path (supports ~ for home directory)
        encoding: File encoding (default: utf-8)
    
    Returns:
        Tuple[bool, str, Optional[str]]: (success, message, content)
        If success is False, content will be None
    """
    try:
        # Expand environment variables first, then user home
        expanded_path = os.path.expandvars(path)
        file_path = Path(expanded_path).expanduser()
        
        # Extension check for binary documents
        ext = file_path.suffix.lower()
        if ext in ('.docx', '.doc', '.xlsx', '.xls', '.pdf', '.pptx', '.zip', '.exe', '.dll', '.bin'):
            return False, f"Binary file detected ({ext}). Use specialized skills (word_docs, spreadsheets, pdf_handling) instead of read_file.", None

        if not file_path.exists():
            return False, f"File not found: {path}", None
        
        if not file_path.is_file():
            return False, f"Path is not a file: {path}", None
        
        content = file_path.read_text(encoding=encoding)
        return True, f"File read successfully: {file_path}", content
        
    except PermissionError:
        return False, f"Permission denied: {path}", None
    except UnicodeDecodeError:
        return False, f"Encoding error (binary file or wrong encoding): {path}", None
    except Exception as e:
        return False, f"Error reading file: {e}", None


def append_file(path: str, content: str, encoding: str = 'utf-8') -> Tuple[bool, str]:
    """
    Append content to an existing file.
    
    Args:
        path: Absolute or relative file path (supports ~ for home directory)
        content: Text content to append
        encoding: File encoding (default: utf-8)
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        expanded_path = os.path.expandvars(path)
        file_path = Path(expanded_path).expanduser()
        
        if not file_path.exists():
            return False, f"File not found: {path}"
        
        # Append to file
        with open(file_path, 'a', encoding=encoding) as f:
            f.write(content)
        
        return True, f"Content appended successfully: {file_path}"
        
    except PermissionError:
        return False, f"Permission denied: {path}"
    except Exception as e:
        return False, f"Error appending to file: {e}"


def create_directory(path: str) -> Tuple[bool, str]:
    """
    Create a directory (and parent directories if needed).
    
    Args:
        path: Absolute or relative directory path (supports ~ for home directory)
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        expanded_path = os.path.expandvars(path)
        dir_path = Path(expanded_path).expanduser()
        dir_path.mkdir(parents=True, exist_ok=True)
        return True, f"Directory created: {dir_path}"
        
    except PermissionError:
        return False, f"Permission denied: {path}"
    except Exception as e:
        return False, f"Error creating directory: {e}"


def file_exists(path: str) -> bool:
    """
    Check if a file exists.
    
    Args:
        path: Absolute or relative file path (supports ~ for home directory)
    
    Returns:
        bool: True if file exists
    """
    try:
        return Path(path).expanduser().is_file()
    except:
        return False


def directory_exists(path: str) -> bool:
    """
    Check if a directory exists.
    
    Args:
        path: Absolute or relative directory path (supports ~ for home directory)
    
    Returns:
        bool: True if directory exists
    """
    try:
        return Path(path).expanduser().is_dir()
    except:
        return False


# Example usage and tests
if __name__ == "__main__":
    # Test write_file
    test_path = "test_output.txt"
    success, msg = write_file(test_path, "Hello, World!\n")
    print(f"Write: {msg}")
    
    # Test read_file
    success, msg, content = read_file(test_path)
    print(f"Read: {msg}")
    if success:
        print(f"Content: {content}")
    
    # Test append_file
    success, msg = append_file(test_path, "Appended line\n")
    print(f"Append: {msg}")
    
    # Clean up
    if file_exists(test_path):
        os.remove(test_path)
        print("Test file cleaned up")
