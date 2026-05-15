# V4A Hunk & Diff Applicator

> 11 nodes · cohesion 0.24

## Key Concepts

- **file_editor.py** (6 connections) — `local_client\file_editor.py`
- **_find_hunk_location()** (4 connections) — `local_client\file_editor.py`
- **apply_v4a_diff()** (4 connections) — `local_client\file_editor.py`
- **_sanitize_llm_output()** (3 connections) — `local_client\file_editor.py`
- **_calculate_similarity()** (3 connections) — `local_client\file_editor.py`
- **V4AHunk** (1 connections) — `local_client\file_editor.py`
- **FileEdit** (1 connections) — `local_client\file_editor.py`
- **Removes common LLM hallucinations like line number prefixes (e.g., "10| ")     a** (1 connections) — `local_client\file_editor.py`
- **Calculates Jaro-Winkler similarity between two lists of strings.** (1 connections) — `local_client\file_editor.py`
- **Finds the location of a hunk in the file content using fuzzy matching.     Retur** (1 connections) — `local_client\file_editor.py`
- **Applies a V4A-style diff to a file with fuzzy matching.** (1 connections) — `local_client\file_editor.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `local_client\file_editor.py`

## Audit Trail

- EXTRACTED: 26 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*