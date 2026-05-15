# Smart File Editing: Fuzzy-Matching Diffs

The "excellence" of Warp's file editing lies in its ability to handle LLM hallucinations gracefully. Agents often fail to provide exact line numbers or perfectly formatted code blocks; Warp's `V4A` system is designed to bridge this gap.

## 1. The V4A Diff Format

Warp uses a structured diff format (`V4AHunk`) that provides significant context around each change. This is much more reliable than simple string replacement.

### **V4AHunk Structure**
*   **`pre_context`**: Several lines of code *before* the change.
*   **`old`**: The exact content to be removed (can be empty for additions).
*   **`new`**: The exact content to be inserted (can be empty for deletions).
*   **`post_context`**: Several lines of code *after* the change.
*   **`change_context`**: metadata like `@@` headers for location guidance.

## 2. The Fuzzy Matching Algorithm

When an agent requests an edit, Warp doesn't just look for an exact match. It uses a sophisticated matching pipeline:

### **Stage 1: Exact Match**
First, it tries to find the `pre_context + old + post_context` exactly in the file.

### **Stage 2: Indentation-Agnostic Match**
If Stage 1 fails, it trims leading/trailing whitespace and tries again. This fixes issues where the LLM gets the indentation level wrong.

### **Stage 3: Fuzzy Sliding Window**
If both fail, it uses a **Sliding Window + Jaro-Winkler Similarity** approach:
1.  It iterates through the file in windows of the expected size.
2.  It calculates a similarity score between the window and the requested `search` block.
3.  It picks the match with the highest score above a certain threshold.
4.  **Fallback Logic:** If multiple matches have similar scores, it uses the line numbers provided by the LLM (even if off-by-one) as a "tie-breaker."

## 3. Reliability Guards

*   **`remove_extra_line_num_prefix`**: Models often hallucinate line numbers *inside* the code block (e.g., `10| def main():`). Warp detects and strips these before applying the edit.
*   **`noop_deltas` detection**: If the `old` and `new` content are identical, Warp identifies this as a "no-op" and reports it back to the agent (often a sign the agent is stuck in a loop).
*   **Safety Checks**: If the match similarity is too low, Warp refuses the edit and returns an error with context, allowing the agent to "re-read" the file and try again.

## 4. Why this matters for Jarvis

Jarvis currently relies on `replace_in_file` which requires an exact string match. This is the #1 cause of "Failed to apply edit" errors.
**Implementation Plan for Jarvis:**
1.  **Introduce `V4A` style tool:** Change the tool signature to include `context_before` and `context_after`.
2.  **Add Fuzzy Matching:** Use a Python library like `difflib` or `TheFuzz` (fuzzywuzzy) to implement the sliding window match.
3.  **Sanitize Hallucinations:** Automatically strip common LLM-specific garbage (like line number prefixes or triple backticks) from the replacement string.

## 🔗 References
*   `warp-master/crates/ai/src/diff_validation/mod.rs` (The core logic)
*   `warp-master/crates/ai/src/agent/action/mod.rs` (Definition of `FileEdit`)
