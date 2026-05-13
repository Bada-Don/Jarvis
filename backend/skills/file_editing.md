---
name: file_editing
description: "Use this skill whenever the user wants to create, edit, modify, or write the content of files — code files, plain text, structured data, or any document. This is the PRIMARY entry point for all file operations. It handles code/text files directly and DELEGATES to specialized skills for heavy document types. Triggers: 'edit', 'modify', 'write', 'create file', 'update', 'fix code', 'debug', 'replace text in file', 'append', 'write program', 'read file'. DELEGATES to: word_docs (.docx), spreadsheets (.xlsx/.csv), pdf_handling (.pdf), file_reading (read-only inspection). Do NOT use for opening files by path (file_navigation), sending emails (email), or FlexiSIGN (flexisign)."
---

# File Editing — Entry Point & Delegation Hub

## Step 0: Choose the Right Skill

Check the file extension BEFORE proceeding:

| File type | Correct skill |
|-----------|-------------|
| `.docx`, `.doc` | → **word_docs** skill |
| `.xlsx`, `.xlsm`, `.xls`, `.csv`, `.tsv` | → **spreadsheets** skill |
| `.pdf` | → **pdf_handling** skill |
| Read-only inspection of any file | → **file_reading** skill |
| `.py`, `.js`, `.ts`, `.txt`, `.md`, `.json`, code | ✅ Continue here |

---

## Workflow for Code & Text Files

**CRITICAL: Always follow Read → Analyze → Edit. Never skip the read step on existing files.**

### Step 1: Read first
```json
{
  "type": "read_file",
  "path": "{DESKTOP_PATH}\\script.py",
  "desc": "Read current content before making any changes"
}
```

### Step 2: Edit with the right operation

**Targeted find-and-replace (PREFERRED):**
```json
{
  "type": "replace_in_file",
  "path": "{DESKTOP_PATH}\\script.py",
  "old_text": "def old_function():\n    return False",
  "new_text": "def old_function():\n    return True",
  "desc": "Fix return value"
}
```

⚠️ `old_text` must be the **COMPLETE** text to replace — not a partial key:

❌ **WRONG** (appends instead of replacing):
```json
{ "old_text": "name:", "new_text": "name: Harshit" }
```
✅ **CORRECT:**
```json
{ "old_text": "name: John Doe", "new_text": "name: Harshit Singla" }
```

**Line-specific edit:**
```json
{
  "type": "modify_lines",
  "path": "{DESKTOP_PATH}\\form.txt",
  "line_number": 5,
  "new_content": "Name: Harshit Singla",
  "num_lines": 1,
  "desc": "Update line 5"
}
```

**Complete file rewrite** (only when necessary):
```json
{
  "type": "write_file",
  "path": "{DESKTOP_PATH}\\LabCode\\script.py",
  "content": "# full content here...",
  "desc": "Rewrite entire file"
}
```

**Append to file:**
```json
{
  "type": "append_file",
  "path": "{DESKTOP_PATH}\\log.txt",
  "content": "New log entry\n",
  "desc": "Append to log"
}
```

### Step 3: Verify (optional)
```json
{
  "type": "shell_command",
  "command": "python \"{DESKTOP_PATH}\\LabCode\\script.py\"",
  "desc": "Run to verify changes"
}
```

---

## AI-Powered Document Editing

For `.docx`, `.xlsx`, `.txt` files with natural language instructions:

### Edit Word document
```json
{
  "type": "ai_edit_word",
  "path": "desktop/report",
  "prompt": "Replace 'John Doe' with 'Ayushi Singla' and update the date to today",
  "desc": "Update name and date"
}
```

### Edit Excel spreadsheet
```json
{
  "type": "ai_edit_excel",
  "path": "desktop/sales_data",
  "prompt": "Add a Commission column that calculates 5% of the Sales column",
  "desc": "Add commission formula column"
}
```

### Edit text file
```json
{
  "type": "ai_edit_text",
  "path": "desktop/notes",
  "prompt": "Organize the content into sections: Attendees, Discussion, Action Items",
  "desc": "Restructure meeting notes"
}
```

**REQUIRED:** Both `path` and `prompt` are mandatory — never omit either.

---

## Creating New Code Files

```json
{
  "sequence": [
    {
      "order": 1,
      "type": "shell_command",
      "command": "mkdir \"{DESKTOP_PATH}\\LabCode\"",
      "desc": "Create folder"
    },
    {
      "order": 2,
      "type": "write_file",
      "path": "{DESKTOP_PATH}\\LabCode\\bubble_sort.py",
      "content": "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n\ndata = [64, 34, 25, 12, 22]\nbubble_sort(data)\nprint(data)",
      "desc": "Write bubble sort program"
    },
    {
      "order": 3,
      "type": "shell_command",
      "command": "code \"{DESKTOP_PATH}\\LabCode\"",
      "desc": "Open in VS Code"
    }
  ]
}
```

### Create directory
```json
{
  "type": "create_directory",
  "path": "{DESKTOP_PATH}\\Projects\\Python",
  "desc": "Create Python projects folder"
}
```

---

## Debug Workflow (READ → ANALYZE → FIX)

```json
{
  "sequence": [
    {
      "order": 1,
      "type": "read_file",
      "path": "{DESKTOP_PATH}\\LabCode\\script.py",
      "desc": "Read file to identify the bug"
    },
    {
      "order": 2,
      "type": "replace_in_file",
      "path": "{DESKTOP_PATH}\\LabCode\\script.py",
      "old_text": "if x = 5:",
      "new_text": "if x == 5:",
      "desc": "Fix assignment operator used as comparison"
    },
    {
      "order": 3,
      "type": "shell_command",
      "command": "python \"{DESKTOP_PATH}\\LabCode\\script.py\"",
      "desc": "Run to verify fix"
    }
  ]
}
```

---

## Critical Rules

1. **ALWAYS `read_file` first** before modifying existing files
2. **NEVER use placeholder text** like `{UPDATED_CONTENT}` — always write actual content
3. **`replace_in_file`:** `old_text` must be the full, complete text being replaced
4. Small changes → `replace_in_file` (fastest, most reliable)
5. Line-specific → `modify_lines`
6. Full rewrites → `write_file` (only when necessary)
7. **Document types** → delegate to the correct specialized skill (see Step 0)

---

## Operation Reference

| Operation | Use for | Key fields |
|-----------|---------|-----------|
| `read_file` | Read any file before editing | `path` |
| `write_file` | Create or overwrite entire file | `path`, `content` |
| `replace_in_file` | Targeted find-and-replace | `path`, `old_text`, `new_text` |
| `modify_lines` | Edit specific line numbers | `path`, `line_number`, `new_content`, `num_lines` |
| `append_file` | Add content to end of file | `path`, `content` |
| `create_directory` | Create a folder | `path` |
| `ai_edit_word` | NL editing of `.docx` | `path`, `prompt` |
| `ai_edit_excel` | NL editing of `.xlsx` | `path`, `prompt` |
| `ai_edit_text` | NL editing of `.txt` | `path`, `prompt` |
