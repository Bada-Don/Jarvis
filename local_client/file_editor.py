import re
from typing import List, Optional, Tuple, Dict, Any
from difflib import SequenceMatcher
import os
from pathlib import Path

# Assuming V4AHunk and FileEdit are defined in backend.session_manager
# For local_client, we might need to re-define or import them carefully
# For now, let's define them here to avoid circular dependencies or complex imports
class V4AHunk:
    pre_context: List[str]
    old: List[str]
    new: List[str]
    post_context: List[str]
    change_context: str # e.g., "@@ -1,5 +1,5 @@"

class FileEdit:
    path: str
    hunks: List[V4AHunk]

def _sanitize_llm_output(content: str) -> str:
    """
    Removes common LLM hallucinations like line number prefixes (e.g., "10| ")
    and triple backticks from code blocks.
    """
    # Remove line number prefixes like "10| "
    content = re.sub(r'^\s*\d+\|\s*', '', content, flags=re.MULTILINE)
    # Remove triple backticks if they enclose the content
    if content.startswith('```') and content.endswith('```'):
        content = content.strip('`').strip()
        # Remove language specifier if present (e.g., python, javascript)
        first_line_break = content.find('\n')
        if first_line_break != -1:
            first_line = content[:first_line_break].strip()
            if not ' ' in first_line and len(first_line) > 0: # Likely a language specifier
                content = content[first_line_break:].strip()
    return content

def _calculate_similarity(a: List[str], b: List[str]) -> float:
    """Calculates Jaro-Winkler similarity between two lists of strings."""
    return SequenceMatcher(None, "\n".join(a), "\n".join(b)).ratio()

def _find_hunk_location(file_content_lines: List[str], hunk: V4AHunk) -> Optional[Tuple[int, int]]:
    """
    Finds the location of a hunk in the file content using fuzzy matching.
    Returns (start_line_index, end_line_index) of the 'old' content in file_content_lines.
    """
    search_block = hunk.get('old', [])
    pre_context = hunk.get('pre_context', [])
    post_context = hunk.get('post_context', [])
    
    # Combine pre_context, search_block, and post_context for a more robust search
    full_hunk_lines = pre_context + search_block + post_context
    
    # Stage 1: Exact Match (full hunk)
    for i in range(len(file_content_lines) - len(full_hunk_lines) + 1):
        if file_content_lines[i:i+len(full_hunk_lines)] == full_hunk_lines:
            return (i + len(pre_context), i + len(pre_context) + len(search_block))

    # Stage 2: Indentation-Agnostic Match (full hunk)
    # Normalize whitespace for comparison
    normalized_file_lines = [re.sub(r'^\s+|\s+$', '', line) for line in file_content_lines]
    normalized_full_hunk_lines = [re.sub(r'^\s+|\s+$', '', line) for line in full_hunk_lines]

    for i in range(len(normalized_file_lines) - len(normalized_full_hunk_lines) + 1):
        if normalized_file_lines[i:i+len(normalized_full_hunk_lines)] == normalized_full_hunk_lines:
            return (i + len(pre_context), i + len(pre_context) + len(search_block))

    # Stage 3: Fuzzy Sliding Window (on 'old' content, with context as tie-breaker)
    best_match_start = -1
    best_similarity = 0.0
    
    # If search_block is empty (insertion), we need to find the best place to insert
    if not search_block:
        # For insertions, find the best match for pre_context, then check post_context
        if pre_context:
            for i in range(len(file_content_lines) - len(pre_context) + 1):
                current_pre_context = file_content_lines[i : i + len(pre_context)]
                similarity = _calculate_similarity(pre_context, current_pre_context)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_start = i + len(pre_context) # Insert after pre_context
            
            if best_similarity > 0.8: # High confidence for pre_context match
                return (best_match_start, best_match_start) # Start and end are the same for insertion point
        return None # Cannot find insertion point reliably

    # Search for the 'old' content within the file
    for i in range(len(file_content_lines) - len(search_block) + 1):
        current_block = file_content_lines[i : i + len(search_block)]
        similarity = _calculate_similarity(search_block, current_block)
        
        # If we have context, use it to boost similarity or break ties
        context_similarity = 0.0
        if pre_context and i >= len(pre_context):
            context_similarity += _calculate_similarity(pre_context, file_content_lines[i-len(pre_context):i])
        if post_context and i + len(search_block) + len(post_context) <= len(file_content_lines):
            context_similarity += _calculate_similarity(post_context, file_content_lines[i+len(search_block):i+len(search_block)+len(post_context)])
        
        # Combine similarities (e.g., weighted average)
        total_similarity = (similarity * 0.7) + (context_similarity * 0.3) # Example weighting
        
        if total_similarity > best_similarity:
            best_similarity = total_similarity
            best_match_start = i

    # Threshold for fuzzy match
    if best_similarity > 0.7: # Example threshold, can be tuned
        return (best_match_start, best_match_start + len(search_block))

    return None

def apply_v4a_diff(file_path: str, file_edit: FileEdit) -> bool:
    """
    Applies a V4A-style diff to a file with fuzzy matching.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content_lines = f.readlines()
        
        # Strip newlines for easier comparison and re-add later
        file_content_lines = [line.rstrip('\n') for line_content in file_content_lines]

        # Apply hunks in reverse order to avoid line number shifts
        # This assumes hunks are provided in a way that their relative positions
        # are stable, or that they are independent.
        # A more robust solution would re-calculate line numbers after each hunk.
        # For now, let's process them in order and assume small, independent changes.
        
        # Store changes and apply them at the end
        changes = [] # List of (start_line, end_line, new_content_lines)

        for hunk in file_edit['hunks']:
            # Sanitize LLM output within the hunk
            hunk['old'] = [_sanitize_llm_output(line) for line in hunk.get('old', [])]
            hunk['new'] = [_sanitize_llm_output(line) for line in hunk.get('new', [])]
            hunk['pre_context'] = [_sanitize_llm_output(line) for line in hunk.get('pre_context', [])]
            hunk['post_context'] = [_sanitize_llm_output(line) for line in hunk.get('post_context', [])]

            location = _find_hunk_location(file_content_lines, hunk)
            
            if location:
                start_line, end_line = location
                changes.append((start_line, end_line, hunk['new']))
            else:
                print(f"Warning: Could not find location for hunk in {file_path}. Skipping hunk.")
                # For now, if a hunk can't be found, we skip the entire edit.
                # A more advanced approach might try to re-plan or report back to the agent.
                return False # Fail entire edit if any hunk fails to match

        # Apply changes in reverse order of start_line to avoid index issues
        changes.sort(key=lambda x: x[0], reverse=True)
        
        for start_line, end_line, new_content_lines in changes:
            # Re-add newlines to new content
            new_content_with_newlines = [line + '\n' for line in new_content_lines]
            if new_content_with_newlines and not new_content_with_newlines[-1].endswith('\n'):
                new_content_with_newlines[-1] += '\n' # Ensure last line has newline if not empty

            file_content_lines[start_line:end_line] = new_content_with_newlines

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(file_content_lines)
        
        print(f"Successfully applied V4A diff to {file_path}")
        return True

    except Exception as e:
        print(f"Error applying V4A diff to {file_path}: {e}")
        return False

if __name__ == '__main__':
    # Example Usage and Testing
    test_file_path = "test_file_for_v4a.txt"
    
    # Create a dummy test file
    initial_content = [
        "Line 1: This is some initial content.",
        "Line 2: Another line here.",
        "Line 3:    Indented line.",
        "Line 4: This line will be changed.",
        "Line 5: Context after the change.",
        "Line 6: Final line."
    ]
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(initial_content))

    print(f"Initial content of {test_file_path}:\n{''.join(initial_content)}\n---")

    # Test Case 1: Simple replacement
    print("Test Case 1: Simple replacement")
    file_edit_1: FileEdit = {
        "path": test_file_path,
        "hunks": [
            {
                "pre_context": ["Line 3:    Indented line."],
                "old": ["Line 4: This line will be changed."],
                "new": ["Line 4: This line has been updated."],
                "post_context": ["Line 5: Context after the change."],
                "change_context": "@@ -3,3 +3,3 @@"
            }
        ]
    }
    success = apply_v4a_diff(test_file_path, file_edit_1)
    print(f"Test Case 1 success: {success}")
    if success:
        with open(test_file_path, 'r', encoding='utf-8') as f:
            print(f"Content after Test 1:\n{f.read()}---")
    
    # Reset file for next test
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(initial_content))

    # Test Case 2: Insertion (old is empty) - simplified handling
    print("\nTest Case 2: Insertion")
    file_edit_2: FileEdit = {
        "path": test_file_path,
        "hunks": [
            {
                "pre_context": ["Line 2: Another line here."],
                "old": [],
                "new": ["Line 2.5: Inserted new line."],
                "post_context": ["Line 3:    Indented line."],
                "change_context": "@@ -2,1 +2,2 @@"
            }
        ]
    }
    success = apply_v4a_diff(test_file_path, file_edit_2)
    print(f"Test Case 2 success: {success}")
    if success:
        with open(test_file_path, 'r', encoding='utf-8') as f:
            print(f"Content after Test 2:\n{f.read()}---")

    # Reset file for next test
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(initial_content))

    # Test Case 3: Deletion (new is empty)
    print("\nTest Case 3: Deletion")
    file_edit_3: FileEdit = {
        "path": test_file_path,
        "hunks": [
            {
                "pre_context": ["Line 2: Another line here."],
                "old": ["Line 3:    Indented line."],
                "new": [],
                "post_context": ["Line 4: This line will be changed."],
                "change_context": "@@ -2,2 +2,1 @@"
            }
        ]
    }
    success = apply_v4a_diff(test_file_path, file_edit_3)
    print(f"Test Case 3 success: {success}")
    if success:
        with open(test_file_path, 'r', encoding='utf-8') as f:
            print(f"Content after Test 3:\n{f.read()}---")

    # Reset file for next test
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(initial_content))

    # Test Case 4: Fuzzy match (old content slightly different)
    print("\nTest Case 4: Fuzzy match (old content slightly different)")
    file_edit_4: FileEdit = {
        "path": test_file_path,
        "hunks": [
            {
                "pre_context": ["Line 3:    Indented line."],
                "old": ["Line 4: This line will be changed. (typo)"], # Intentional typo
                "new": ["Line 4: This line has been fuzzily updated."],
                "post_context": ["Line 5: Context after the change."],
                "change_context": "@@ -3,3 +3,3 @@"
            }
        ]
    }
    success = apply_v4a_diff(test_file_path, file_edit_4)
    print(f"Test Case 4 success: {success}")
    if success:
        with open(test_file_path, 'r', encoding='utf-8') as f:
            print(f"Content after Test 4:\n{f.read()}---")

    # Clean up test file
    os.remove(test_file_path)
    print(f"\nCleaned up {test_file_path}")
