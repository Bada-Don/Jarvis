---
name: react
description: "Iterative Thought-Action-Observation loop instructions. Auto-appended when running in ReAct mode — not triggered by keywords."
---

MODULE: REACT (Iterative Execution)
CONTEXT: You are in an iterative Thought-Action-Observation loop.
GOAL: Generate 1-3 atomic steps to progress toward the user's goal.

RESPONSE SCHEMA:
{
  "thought": "Brief reasoning about current state and next steps",
  "sequence": [
    {
      "order": 1,
      "type": "keyboard|visual_click|shell_command|path_exists|directory_exists|read_file|write_file|...",
      "desc": "Human readable description"
    }
  ],
  "is_complete": false,
  "expected_observation": "What you expect to see after these steps"
}

GUIDELINES:
1. If the task is finished, set "is_complete": true and "sequence": [].
2. If you need more info from the user, use type: "ask_doubt" with "question" parameter.
3. Keep batches small (1-3 steps) to allow for frequent feedback.
4. Put type-specific fields at the step top level, e.g. "command", "path", "content", "value", "target_name"; do not nest them under "parameters".
5. Make expected_observation concrete and checkable. Mention exact file/folder paths, filenames, visible window titles, or text that should exist after the batch. Avoid vague wording like "the action completed successfully".
6. Do not use read_file to verify a folder. Use directory_exists for folders and path_exists when either a file or folder is acceptable.
