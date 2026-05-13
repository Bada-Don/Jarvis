---
name: file_reading
description: "Use this skill whenever a file path is mentioned but its content is NOT yet in context — the user wants you to read, inspect, or analyze a file. This skill is a ROUTER: it tells you which tool or approach to use for every file extension so you never blindly cat a binary. Triggers: any mention of 'read file', 'open file', 'check file', 'what's in this file', a bare file path, or any extension like .pdf .docx .xlsx .csv .json .zip .png .log."
---

# File Reading — Dispatch Router

## Protocol (always follow in order)

1. **Check extension** — that is your dispatch key (see table below).
2. **Stat before reading** — know the file size before loading it entirely.
   ```python
   import os
   size = os.path.getsize(r"C:\path\to\file.ext")
   print(f"{size:,} bytes")
   ```
3. **Read just enough** — if the user asks "how many rows", use line count, not a full load.
4. **Use the right tool** — see the dispatch table.

---

## Dispatch Table

| Extension | First Move | Delegate To |
|-----------|-----------|-------------|
| `.pdf` | `pdfinfo` via subprocess + text sample | → `pdf_handling` skill |
| `.docx` | `python-docx` paragraph peek | → `word_docs` skill |
| `.doc` | Convert to `.docx` first via Word COM | → `word_docs` skill |
| `.xlsx`, `.xlsm` | `openpyxl` sheet names + first 5 rows | → `spreadsheets` skill |
| `.xls` | `pd.read_excel(engine="xlrd")` shape | → `spreadsheets` skill |
| `.ods` | `pd.read_excel(engine="odf")` shape | → `spreadsheets` skill |
| `.csv`, `.tsv` | `pd.read_csv(nrows=5)` | → `spreadsheets` skill |
| `.json` | `json.load` type check → drill in | Read inline |
| `.jsonl` | `head` 3 lines + `wc -l` equivalent | Read inline |
| `.jpg`, `.png`, `.gif`, `.webp` | Vision input — already visible | No extra step needed |
| `.zip` | `zipfile.namelist()` — list only | Extract only if asked |
| `.tar`, `.tar.gz`, `.tgz` | `tarfile.getmembers()` — list only | Extract only if asked |
| `.gz` (single file) | `gzip.open` + `head` 20 lines | Read inline |
| `.txt`, `.md`, `.log` | `os.path.getsize` then read or sample | Read inline |
| `.py`, `.js`, `.ts`, code | `wc -l` equivalent + read | Use file_editing skill |
| Unknown | `python-magic` MIME detect | Ask user if uncertain |

---

## CSV / TSV

**Never** open a raw CSV with `cat` — a 50 KB quoted cell in row 1 will corrupt the preview.

```python
import pandas as pd

# Step 1: shape without loading
with open(r"C:\path\to\file.csv", "r", encoding="utf-8-sig") as f:
    row_count = sum(1 for _ in f) - 1  # subtract header

# Step 2: safe preview
df = pd.read_csv(r"C:\path\to\file.csv", nrows=5)
print(f"Shape estimate: {row_count} rows × {len(df.columns)} cols")
print(df)
print(df.dtypes)
```

---

## JSON / JSONL

Structure first, content second:

```python
import json, pathlib

raw = pathlib.Path(r"C:\path\to\file.json").read_text(encoding="utf-8")
data = json.loads(raw)

if isinstance(data, list):
    print(f"Array with {len(data)} items")
    print("First item:", data[0])
elif isinstance(data, dict):
    print("Object keys:", list(data.keys()))
```

JSONL (one object per line) — never load the whole file:

```python
with open(r"C:\path\to\file.jsonl", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= 3: break
        print(json.loads(line))
```

---

## Archives (ZIP / TAR)

**List first. Extract never — unless the user explicitly asks.**

```python
import zipfile, tarfile

# ZIP
with zipfile.ZipFile(r"C:\path\to\bundle.zip") as z:
    print(z.namelist())

# TAR / TAR.GZ (auto-detects compression)
with tarfile.open(r"C:\path\to\bundle.tar.gz") as t:
    t.list()
```

To extract a single file from a ZIP:
```python
with zipfile.ZipFile(r"C:\path\to\bundle.zip") as z:
    content = z.read("path/inside/file.txt")
    print(content.decode("utf-8"))
```

---

## Plain Text / Code / Logs

```python
import os

path = r"C:\path\to\app.log"
size = os.path.getsize(path)

if size < 20_000:  # Under ~20 KB: read fully
    print(open(path, encoding="utf-8", errors="replace").read())
else:  # Over 20 KB: head + tail
    lines = open(path, encoding="utf-8", errors="replace").readlines()
    print("=== FIRST 100 LINES ===")
    print("".join(lines[:100]))
    print(f"\n... ({len(lines)} total lines) ...\n")
    print("=== LAST 100 LINES ===")
    print("".join(lines[-100:]))
```

For log files, the user usually cares about the end:
```python
print("".join(open(path, encoding="utf-8", errors="replace").readlines()[-200:]))
```

---

## Images

Uploaded images appear as vision inputs in context — you can already describe them. Use the file path only for programmatic processing (PIL, pytesseract, etc.).

---

## Unknown File Types

```python
import subprocess
result = subprocess.run(["file", r"C:\path\to\unknown"], capture_output=True, text=True)
print(result.stdout)
```

On Windows (no `file` command), use `python-magic`:
```python
import magic
print(magic.from_file(r"C:\path\to\unknown", mime=True))
```

---

## Dependencies

| Library | Purpose | Install |
|---------|---------|---------|
| `pandas` | CSV / TSV / Excel shape | `pip install pandas` |
| `openpyxl` | XLSX peek | `pip install openpyxl` |
| `pypdf` | PDF metadata | `pip install pypdf` |
| `pdfplumber` | PDF text + tables | `pip install pdfplumber` |
| `python-docx` | DOCX paragraph peek | `pip install python-docx` |
| `python-magic` | Unknown MIME detection | `pip install python-magic-bin` |
| `chardet` | Encoding detection | `pip install chardet` |
