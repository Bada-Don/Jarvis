"""
Intelligent File Editor Module for Jarvis

This module provides LLM-friendly file editing capabilities similar to modern agentic IDEs.
Supports:
- Reading file content with line numbers
- In-place modifications using search/replace patterns
- Diff-based edits for large files
- Context-aware editing with minimal token usage
"""

import os
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import difflib


class FileEditor:
    """
    Intelligent file editor that works well with LLMs.
    Provides context-aware editing without sending entire file contents.
    """
    
    def __init__(self):
        self.file_cache = {}  # Cache file contents for efficiency
    
    def read_file_with_context(self, path: str, encoding: str = 'utf-8') -> Tuple[bool, str, Optional[Dict]]:
        """
        Read a file and return it with line numbers and metadata.
        
        Args:
            path: File path (supports ~ and %VAR%)
            encoding: File encoding
        
        Returns:
            Tuple[bool, str, Optional[Dict]]: (success, message, file_data)
            file_data contains:
                - 'content': raw file content
                - 'lines': list of lines
                - 'numbered_content': content with line numbers
                - 'line_count': total lines
                - 'path': resolved absolute path
        """
        try:
            expanded_path = os.path.expandvars(path)
            file_path = Path(expanded_path).expanduser()
            
            if not file_path.exists():
                return False, f"File not found: {path}", None
            
            if not file_path.is_file():
                return False, f"Path is not a file: {path}", None
            
            content = file_path.read_text(encoding=encoding)
            lines = content.splitlines(keepends=True)
            
            # Create numbered content for LLM context
            numbered_lines = []
            for i, line in enumerate(lines, 1):
                numbered_lines.append(f"{i:4d} | {line.rstrip()}")
            numbered_content = '\n'.join(numbered_lines)
            
            file_data = {
                'content': content,
                'lines': lines,
                'numbered_content': numbered_content,
                'line_count': len(lines),
                'path': str(file_path)
            }
            
            # Cache for potential edits
            self.file_cache[str(file_path)] = file_data
            
            return True, f"File read successfully: {file_path}", file_data
            
        except PermissionError:
            return False, f"Permission denied: {path}", None
        except UnicodeDecodeError:
            return False, f"Encoding error: {path}", None
        except Exception as e:
            return False, f"Error reading file: {e}", None
    
    def replace_in_file(self, path: str, old_text: str, new_text: str, 
                       encoding: str = 'utf-8', count: int = -1) -> Tuple[bool, str, Optional[str]]:
        """
        Replace text in a file using search/replace pattern.
        Similar to IDE "Find and Replace" functionality.
        
        Args:
            path: File path
            old_text: Text to search for (exact match)
            new_text: Text to replace with
            encoding: File encoding
            count: Number of replacements (-1 for all)
        
        Returns:
            Tuple[bool, str, Optional[str]]: (success, message, preview_diff)
        """
        try:
            expanded_path = os.path.expandvars(path)
            file_path = Path(expanded_path).expanduser()
            
            if not file_path.exists():
                return False, f"File not found: {path}", None
            
            # Read current content
            content = file_path.read_text(encoding=encoding)
            
            # Check if old_text exists
            if old_text not in content:
                return False, f"Text not found in file: '{old_text[:50]}...'", None
            
            # Perform replacement
            new_content = content.replace(old_text, new_text, count)
            
            # Generate diff for preview
            diff = self._generate_diff(content, new_content, str(file_path))
            
            # Write back
            file_path.write_text(new_content, encoding=encoding)
            
            replacements = content.count(old_text) if count == -1 else min(count, content.count(old_text))
            
            return True, f"Replaced {replacements} occurrence(s) in {file_path}", diff
            
        except Exception as e:
            return False, f"Error replacing in file: {e}", None
    
    def modify_lines(self, path: str, line_number: int, new_content: str,
                    num_lines: int = 1, encoding: str = 'utf-8') -> Tuple[bool, str, Optional[str]]:
        """
        Modify specific lines in a file.
        
        Args:
            path: File path
            line_number: Starting line number (1-indexed)
            new_content: New content for the line(s)
            num_lines: Number of lines to replace
            encoding: File encoding
        
        Returns:
            Tuple[bool, str, Optional[str]]: (success, message, preview_diff)
        """
        try:
            expanded_path = os.path.expandvars(path)
            file_path = Path(expanded_path).expanduser()
            
            if not file_path.exists():
                return False, f"File not found: {path}", None
            
            # Read current content
            content = file_path.read_text(encoding=encoding)
            lines = content.splitlines(keepends=True)
            
            # Validate line number
            if line_number < 1 or line_number > len(lines):
                return False, f"Invalid line number: {line_number} (file has {len(lines)} lines)", None
            
            # Prepare new content
            if not new_content.endswith('\n') and line_number < len(lines):
                new_content += '\n'
            
            # Replace lines
            old_content = content
            lines[line_number - 1:line_number - 1 + num_lines] = [new_content]
            new_content_full = ''.join(lines)
            
            # Generate diff
            diff = self._generate_diff(old_content, new_content_full, str(file_path))
            
            # Write back
            file_path.write_text(new_content_full, encoding=encoding)
            
            return True, f"Modified line(s) {line_number}-{line_number + num_lines - 1} in {file_path}", diff
            
        except Exception as e:
            return False, f"Error modifying lines: {e}", None
    
    def insert_at_line(self, path: str, line_number: int, content: str,
                      encoding: str = 'utf-8') -> Tuple[bool, str, Optional[str]]:
        """
        Insert content at a specific line number.
        
        Args:
            path: File path
            line_number: Line number to insert at (1-indexed, 0 = beginning)
            content: Content to insert
            encoding: File encoding
        
        Returns:
            Tuple[bool, str, Optional[str]]: (success, message, preview_diff)
        """
        try:
            expanded_path = os.path.expandvars(path)
            file_path = Path(expanded_path).expanduser()
            
            if not file_path.exists():
                return False, f"File not found: {path}", None
            
            # Read current content
            old_content = file_path.read_text(encoding=encoding)
            lines = old_content.splitlines(keepends=True)
            
            # Prepare content
            if not content.endswith('\n'):
                content += '\n'
            
            # Insert
            if line_number == 0:
                lines.insert(0, content)
            elif line_number <= len(lines):
                lines.insert(line_number, content)
            else:
                return False, f"Invalid line number: {line_number} (file has {len(lines)} lines)", None
            
            new_content = ''.join(lines)
            
            # Generate diff
            diff = self._generate_diff(old_content, new_content, str(file_path))
            
            # Write back
            file_path.write_text(new_content, encoding=encoding)
            
            return True, f"Inserted content at line {line_number} in {file_path}", diff
            
        except Exception as e:
            return False, f"Error inserting at line: {e}", None
    
    def delete_lines(self, path: str, start_line: int, end_line: int = None,
                    encoding: str = 'utf-8') -> Tuple[bool, str, Optional[str]]:
        """
        Delete specific lines from a file.
        
        Args:
            path: File path
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (inclusive, None = delete only start_line)
            encoding: File encoding
        
        Returns:
            Tuple[bool, str, Optional[str]]: (success, message, preview_diff)
        """
        try:
            expanded_path = os.path.expandvars(path)
            file_path = Path(expanded_path).expanduser()
            
            if not file_path.exists():
                return False, f"File not found: {path}", None
            
            # Read current content
            old_content = file_path.read_text(encoding=encoding)
            lines = old_content.splitlines(keepends=True)
            
            if end_line is None:
                end_line = start_line
            
            # Validate line numbers
            if start_line < 1 or start_line > len(lines):
                return False, f"Invalid start line: {start_line}", None
            if end_line < start_line or end_line > len(lines):
                return False, f"Invalid end line: {end_line}", None
            
            # Delete lines
            del lines[start_line - 1:end_line]
            new_content = ''.join(lines)
            
            # Generate diff
            diff = self._generate_diff(old_content, new_content, str(file_path))
            
            # Write back
            file_path.write_text(new_content, encoding=encoding)
            
            return True, f"Deleted lines {start_line}-{end_line} from {file_path}", diff
            
        except Exception as e:
            return False, f"Error deleting lines: {e}", None
    
    def _generate_diff(self, old_content: str, new_content: str, filename: str) -> str:
        """Generate a unified diff between old and new content."""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{filename} (before)",
            tofile=f"{filename} (after)",
            lineterm=''
        )
        
        return ''.join(diff)


# Example usage
if __name__ == "__main__":
    editor = FileEditor()
    
    # Test read with context
    success, msg, data = editor.read_file_with_context("test.txt")
    if success:
        print("File content with line numbers:")
        print(data['numbered_content'])
    
    # Test replace
    success, msg, diff = editor.replace_in_file(
        "test.txt",
        "old text",
        "new text"
    )
    if success:
        print(f"\n{msg}")
        print(f"Diff:\n{diff}")
