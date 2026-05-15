# Text Processing & Similarity

> 31 nodes · cohesion 0.07

## Key Concepts

- **._generate_diff()** (8 connections) — `Jarvis-aws-migration\backend\file_editor.py`
- **.apply_v4a_diff()** (7 connections) — `backend\file_editor.py`
- **.replace_in_file()** (6 connections) — `Jarvis-aws-migration\backend\file_editor.py`
- **._perform_replacement_at_indices()** (5 connections) — `backend\file_editor.py`
- **._find_match_location()** (5 connections) — `backend\file_editor.py`
- **.modify_lines()** (4 connections) — `Jarvis-aws-migration\backend\file_editor.py`
- **.insert_at_line()** (4 connections) — `Jarvis-aws-migration\backend\file_editor.py`
- **.delete_lines()** (4 connections) — `Jarvis-aws-migration\backend\file_editor.py`
- **._is_noop_delta()** (4 connections) — `backend\file_editor.py`
- **._normalize_whitespace()** (3 connections) — `backend\file_editor.py`
- **._calculate_similarity()** (3 connections) — `backend\file_editor.py`
- **._strip_llm_garbage()** (3 connections) — `backend\file_editor.py`
- **._remove_extra_line_num_prefix()** (3 connections) — `backend\file_editor.py`
- **Performs the actual file modification by replacing content within specified indi** (1 connections) — `backend\file_editor.py`
- **Removes leading/trailing whitespace from each line and joins them.** (1 connections) — `backend\file_editor.py`
- **Calculates similarity between two strings using difflib.SequenceMatcher.** (1 connections) — `backend\file_editor.py`
- **Strips common LLM-specific garbage like triple backticks.** (1 connections) — `backend\file_editor.py`
- **Removes common LLM-hallucinated line number prefixes (e.g., '10 | ').** (1 connections) — `backend\file_editor.py`
- **Generate a unified diff between old and new content.** (1 connections) — `backend\file_editor.py`
- **Finds the start and end character indices of the 'old' content within the file,** (1 connections) — `backend\file_editor.py`
- **Replace text in a file using search/replace pattern (backward compatible).** (1 connections) — `backend\file_editor.py`
- **Public interface for applying a V4A-style diff hunk to a file.** (1 connections) — `backend\file_editor.py`
- **Modify specific lines in a file.                  Args:             path: Fil** (1 connections) — `backend\file_editor.py`
- **Insert content at a specific line number.                  Args:** (1 connections) — `backend\file_editor.py`
- **Delete specific lines from a file.                  Args:             path: F** (1 connections) — `backend\file_editor.py`
- *... and 6 more nodes in this community*

## Relationships

- [[AI Editor & LLM Engines]] (13 shared connections)

## Source Files

- `Jarvis-aws-migration\backend\file_editor.py`
- `backend\file_editor.py`

## Audit Trail

- EXTRACTED: 77 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*