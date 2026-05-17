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


def read_file(path: str, encoding: str = 'utf-8', max_bytes: int = 50 * 1024) -> Tuple[bool, str, Optional[str]]:
    """
    Read content from a file with a byte limit and binary file detection.
    
    Args:
        path: Absolute or relative file path (supports ~ for home directory)
        encoding: File encoding (default: utf-8)
        max_bytes: Maximum number of bytes to read from the file.
    
    Returns:
        Tuple[bool, str, Optional[str]]: (success, message, content)
        If success is False, content will be None.
        Message will include total line count and truncation status.
    """
    try:
        # Expand environment variables first, then user home
        expanded_path = os.path.expandvars(path)
        file_path = Path(expanded_path).expanduser()
        
        if not file_path.exists():
            return False, f"File not found: {path}", None
        
        if not file_path.is_file():
            return False, f"Path is not a file: {path}", None

        # Word documents: delegate to optional python-docx reader
        if file_path.suffix.lower() == '.docx':
            try:
                from docx_support import read_docx
            except ImportError:
                return False, (
                    "Cannot read .docx (docx_support unavailable). "
                    "Install python-docx: pip install python-docx"
                ), None
            ok, msg, content = read_docx(str(file_path))
            if not ok or content is None:
                return False, msg, None
            if len(content) > max_bytes:
                content = content[:max_bytes]
                msg = f"{msg} Content truncated to {max_bytes} characters."
            return True, msg, content

        # Binary file detection (more robust check)
        # Read a small chunk to sniff for binary content
        with open(file_path, 'rb') as f:
            initial_bytes = f.read(1024)
        
        # Heuristic: if more than 10% of the first 1KB are null bytes, it's likely binary
        if initial_bytes.count(b'\x00') > len(initial_bytes) * 0.1:
            return False, f"Binary file detected: {path}. Use specialized skills (e.g., word_docs, spreadsheets, pdf_handling) instead of read_file.", None

        # Extension check for known binary documents (as a fallback/additional check)
        ext = file_path.suffix.lower()
        if ext in ('.doc', '.xlsx', '.xls', '.pdf', '.pptx', '.zip', '.exe', '.dll', '.bin', '.jpg', '.png', '.gif', '.bmp', '.mp3', '.mp4', '.avi', '.mov'):
            return False, f"Binary file detected ({ext}). Use specialized skills (e.g., word_docs, spreadsheets, pdf_handling) instead of read_file.", None

        file_size = file_path.stat().st_size
        
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read(max_bytes)
            
            # Count lines in the read content
            lines_in_content = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
            
            truncated = f.read(1) != "" # Try reading one more char to detect truncation
            
            if truncated:
                # If truncated, we need to count the remaining lines to get the total
                remaining_lines = sum(1 for _ in f)
                total_lines = lines_in_content + remaining_lines
            else:
                total_lines = lines_in_content
            
            message = f"File read successfully: {file_path}. Total lines: {total_lines}."
            if truncated:
                message += f" Content truncated to {max_bytes} characters."
            
            return True, message, content
        
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
