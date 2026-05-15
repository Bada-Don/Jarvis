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
import re


class FileEditor:
    """
    Intelligent file editor that works well with LLMs.
    Provides context-aware editing without sending entire file contents.
    """
    
    def __init__(self):
        self.file_cache = {}  # Cache file contents for efficiency
    
    def read_file_with_context(self, path: str, encoding: str = 'utf-8', max_bytes: int = 50000) -> Tuple[bool, str, Optional[Dict]]:
        """
        Read a file and return it with line numbers and metadata, with a byte limit.
        
        Args:
            path: File path (supports ~ and %VAR%)
            encoding: File encoding
            max_bytes: Maximum number of bytes to read from the file.
        
        Returns:
            Tuple[bool, str, Optional[Dict]]: (success, message, file_data)
            file_data contains:
                - 'content': raw file content (potentially truncated)
                - 'lines': list of lines (potentially truncated)
                - 'numbered_content': content with line numbers (potentially truncated)
                - 'line_count': total lines in the *original* file
                - 'truncated': boolean indicating if content was truncated
                - 'path': resolved absolute path
        """
        try:
            expanded_path = os.path.expandvars(path)
            file_path = Path(expanded_path).expanduser()
            
            if not file_path.exists():
                return False, f"File not found: {path}", None
            
            if not file_path.is_file():
                return False, f"Path is not a file: {path}", None
            
            # Read content with byte limit
            with open(file_path, 'rb') as f:
                raw_content = f.read(max_bytes + 1) # Read one extra byte to detect truncation
            
            truncated = len(raw_content) > max_bytes
            content_to_decode = raw_content[:max_bytes]
            
            # Check if the file is likely binary
            if b'\0' in content_to_decode:
                return False, f"File appears to be a binary file and cannot be read as text: {path}", None
            
            try:
                content = content_to_decode.decode(encoding)
            except UnicodeDecodeError:
                return False, f"File is not a readable text file or uses an unsupported encoding: {path}", None
            
            # Get total line count of the original file
            total_line_count = 0
            with open(file_path, 'r', encoding=encoding) as f:
                for line in f:
                    total_line_count += 1
            
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
                'line_count': total_line_count, # Total lines in original file
                'truncated': truncated,
                'path': str(file_path)
            }
            
            # Cache for potential edits
            self.file_cache[str(file_path)] = file_data
            
            return True, f"File read successfully: {file_path}", file_data
            
        except PermissionError:
            return False, f"Permission denied: {path}", None
        except Exception as e:
            return False, f"Error reading file: {e}", None
    
    def _perform_replacement_at_indices(self, path: str, start_index: int, end_index: int, new_content_segment: str,
                                       encoding: str = 'utf-8') -> Tuple[bool, str, Optional[str]]:
        """
        Performs the actual file modification by replacing content within specified indices.
        This is a low-level internal function.
        
        Args:
            path: File path
            start_index: The starting character index of the content to be replaced.
            end_index: The ending character index of the content to be replaced.
            new_content_segment: The new content to insert at the specified indices.
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
            
            # Perform replacement using indices
            new_content = content[:start_index] + new_content_segment + content[end_index:]
            
            # Generate diff for preview
            diff = self._generate_diff(content, new_content, str(file_path))
            
            # Write back
            file_path.write_text(new_content, encoding=encoding)
            
            return True, f"Content replaced in {file_path} from index {start_index} to {end_index}", diff
            
        except Exception as e:
            return False, f"Error performing replacement at indices: {e}", None

    def _normalize_whitespace(self, text: str) -> str:
        """Removes leading/trailing whitespace from each line and joins them."""
        return "\n".join([line.strip() for line in text.splitlines()])



    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculates similarity between two strings using difflib.SequenceMatcher."""
        return difflib.SequenceMatcher(None, text1, text2).ratio()

    def _strip_llm_garbage(self, text: str) -> str:
        """Strips common LLM-specific garbage like triple backticks."""
        text = text.strip()
        # Remove triple backticks at start/end
        text = re.sub(r'^```[a-zA-Z]*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
        return text.strip()

    def _remove_extra_line_num_prefix(self, text: str) -> str:
        """Removes common LLM-hallucinated line number prefixes (e.g., '10 | ')."""
        lines = text.splitlines(keepends=True)
        cleaned_lines = []
        for line in lines:
            # Match patterns like "  10 | ", "10: ", "10| "
            cleaned = re.sub(r'^\s*\d+\s*[:|]\s*', '', line)
            cleaned_lines.append(cleaned)
        return "".join(cleaned_lines)

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

    def _find_match_location(self, content: str, pre_context: str, old: str, post_context: str) -> Optional[Tuple[int, int]]:
        """
        Finds the start and end character indices of the 'old' content within the file,
        considering pre_context and post_context for precise matching.
        
        Args:
            content: The full content of the file.
            pre_context: Lines before the change.
            old: The exact content to be removed.
            post_context: Lines after the change.
            
        Returns:
            Optional[Tuple[int, int]]: A tuple (start_index, end_index) if a match is found, else None.
        """
        search_pattern = pre_context + old + post_context
        
        # Stage 1: Exact Match
        match_start = content.find(search_pattern)
        if match_start != -1:
            # Calculate the start and end indices of the 'old' content within the match
            old_start_index = match_start + len(pre_context)
            old_end_index = old_start_index + len(old)
            return old_start_index, old_end_index
            
        # Stage 2: Indentation-Agnostic Match
        content_lines = content.splitlines(keepends=True)
        normalized_content_lines = [line.strip() for line in content_lines]
        
        pre_context_lines = pre_context.splitlines()
        old_lines = old.splitlines()
        post_context_lines = post_context.splitlines()
        
        normalized_search_lines = [line.strip() for line in pre_context_lines + old_lines + post_context_lines]
        
        for i in range(len(normalized_content_lines) - len(normalized_search_lines) + 1):
            if normalized_content_lines[i : i + len(normalized_search_lines)] == normalized_search_lines:
                start_char_of_pre_context = sum(len(line) for line in content_lines[:i])
                start_char_of_old = start_char_of_pre_context + sum(len(line) for line in content_lines[i : i + len(pre_context_lines)])
                end_char_of_old = start_char_of_old + sum(len(line) for line in content_lines[i + len(pre_context_lines) : i + len(pre_context_lines) + len(old_lines)])
                return start_char_of_old, end_char_of_old
        
        # Stage 3: Fuzzy Sliding Window (Line-based for efficiency)
        # Combine pre_context, old, and post_context to form the target block for fuzzy matching
        target_block = pre_context + old + post_context
        target_lines = target_block.splitlines()
        target_len = len(target_lines)
        
        content_lines = content.splitlines(keepends=True)
        
        best_match_score = 0.0
        best_match_indices: Optional[Tuple[int, int]] = None
        
        # Iterate through the content lines with a sliding window
        # This is much faster than character-by-character for large files
        for i in range(len(content_lines) - target_len + 1):
            window_lines = content_lines[i : i + target_len]
            window_text = "".join(window_lines)
            
            # Use SequenceMatcher on the window
            similarity = self._calculate_similarity(target_block, window_text)
            
            if similarity > best_match_score:
                best_match_score = similarity
                # Calculate character offsets
                start_char_of_window = sum(len(line) for line in content_lines[:i])
                
                # Within the window, the 'old' part starts after pre_context_lines
                pre_context_lines_count = len(pre_context.splitlines())
                old_lines_count = len(old.splitlines())
                
                old_start_index = start_char_of_window + sum(len(line) for line in content_lines[i : i + pre_context_lines_count])
                old_end_index = old_start_index + sum(len(line) for line in content_lines[i + pre_context_lines_count : i + pre_context_lines_count + old_lines_count])
                
                best_match_indices = (old_start_index, old_end_index)
        
        # Define a threshold for fuzzy matching (e.g., 80%)
        FUZZY_MATCH_THRESHOLD = 0.8
        if best_match_score >= FUZZY_MATCH_THRESHOLD and best_match_indices:
            return best_match_indices
            
        return None

    def replace_in_file(self, path: str, old_text: str, new_text: str, 
                       encoding: str = 'utf-8', count: int = -1) -> Tuple[bool, str, Optional[str]]:
        """
        Replace text in a file using search/replace pattern (backward compatible).
        This function will internally call _apply_v4a_diff.
        
        Args:
            path: File path
            old_text: Text to search for (exact match)
            new_text: Text to replace with
            encoding: File encoding
            count: Number of replacements (-1 for all) - currently ignored for V4A diff
        
        Returns:
            Tuple[bool, str, Optional[str]]: (success, message, preview_diff)
        """
        # For backward compatibility, we'll treat old_text as 'old' and new_text as 'new'
        # with empty pre_context and post_context.
        # The 'count' parameter will be ignored for now, as V4A diffs are typically single-hunk.
        
        # Read current content
        try:
            expanded_path = os.path.expandvars(path)
            file_path = Path(expanded_path).expanduser()
            content = file_path.read_text(encoding=encoding)
        except Exception as e:
            return False, f"Error reading file for replace_in_file: {e}", None

        match_location = self._find_match_location(content, "", old_text, "")
        if match_location:
            start_index, end_index = match_location
            # The new content segment for _perform_replacement_at_indices is just new_text
            return self._perform_replacement_at_indices(path, start_index, end_index, new_text, encoding)
        else:
            return False, f"Text not found in file: '{old_text[:50]}...'", None

    def apply_v4a_diff(self, path: str, pre_context: str, old: str, new: str, post_context: str,
                       encoding: str = 'utf-8') -> Tuple[bool, str, Optional[str]]:
        """
        Public interface for applying a V4A-style diff hunk to a file.
        
        Args:
            path: File path
            pre_context: Lines before the change
            old: The exact content to be removed
            new: The exact content to be inserted
            post_context: Lines after the change
            encoding: File encoding
        
        Returns:
            Tuple[bool, str, Optional[str]]: (success, message, preview_diff)
        """
        try:
            expanded_path = os.path.expandvars(path)
            file_path = Path(expanded_path).expanduser()
            content = file_path.read_text(encoding=encoding)
        except Exception as e:
            return False, f"Error reading file for apply_v4a_diff: {e}", None

        # Apply sanitization to old and new content before processing
        old = self._strip_llm_garbage(self._remove_extra_line_num_prefix(old))
        new = self._strip_llm_garbage(self._remove_extra_line_num_prefix(new))

        if self._is_noop_delta(old, new):
            return True, "No-op detected: old and new content are effectively the same.", None

        match_location = self._find_match_location(content, pre_context, old, post_context)
        if match_location:
            start_index, end_index = match_location
            # The new content segment for _perform_replacement_at_indices is pre_context + new + post_context
            return self._perform_replacement_at_indices(path, start_index, end_index, pre_context + new + post_context, encoding)
        else:
            return False, f"V4A diff pattern not found in file: '{pre_context[:50]}...{old[:50]}...{post_context[:50]}...'", None
    
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
    
    def _is_noop_delta(self, old: str, new: str) -> bool:
        """Checks if the old and new content are effectively the same after normalization."""
        return self._normalize_whitespace(old) == self._normalize_whitespace(new)


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
