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
      "type": "keyboard|visual_click|shell_command|path_exists|directory_exists|read_file|write_file|ask_doubt|...",
      "desc": "Human readable description"
    }
  ],
  "is_complete": false,
  "expected_observation": "What you expect to see after these steps"
}

GUIDELINES:
1. If the task is finished, set "is_complete": true and "sequence": [].
2. If you need more info from the user, use type: "ask_doubt" with required "question" string (optional "options" array for suggested answers, optional "is_multiselect": false). **Do not use ask_doubt** when a recent observation already states `Files in listing: ...` with a single clear match (e.g. only `python_program.docx` when the user asked for the python program file) — proceed with `word_docs` / `read_file` on that path instead.
3. After any directory listing observation, only reference **filenames that literally appeared** in that output (look for `Files in listing:` or the Name column). If the listing shows exactly one plausible file for the user's intent, **use it** — do not ask whether the folder is empty. Use **ask_doubt** only when there are **zero** matches or **multiple** equally plausible files. Never invent paths like `program.py`.
4. Never create placeholder files, empty shells, or "sample" code to satisfy "read existing program" or "copy contents" tasks.
5. For copy / duplicate-to-new-file tasks: **write_file content must be exactly** the text from the last successful **read_file** observation in history — never substitute different code.
6. Keep batches small (1-3 steps) to allow for frequent feedback.
7. Put type-specific fields at the step top level, e.g. "command", "path", "content", "value", "target_name"; do not nest them under "parameters".
8. Make expected_observation concrete and checkable. Mention exact file/folder paths, filenames, visible window titles, or text that should exist after the batch. Avoid vague wording like "the action completed successfully".
9. Do not use read_file to verify a folder. Use directory_exists for folders and path_exists when either a file or folder is acceptable.
