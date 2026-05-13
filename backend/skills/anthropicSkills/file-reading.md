---
name: file-reading
description: "Use this skill when a file has been uploaded but its content is NOT in your context — only its path at /mnt/user-data/uploads/ is listed. This skill is a router: it tells you which tool to use for each file type (pdf, docx, xlsx, csv, json, images, archives, ebooks) so you read the right amount the right way instead of blindly running cat on a binary. Triggers: any mention of uploaded files or /mnt/user-data/uploads/"
---

# Reading Uploaded Files

## Protocol

1. **Look at the extension** — that is your dispatch key
2. **Stat before you read** — large files need sampling
   ```bash
   stat -c '%s bytes' file.pdf
   file file.pdf
   ```
3. **Read just enough** — if they asked "how many rows", use `wc -l`, not full load
4. **Use the right tool** — see dispatch table below

## Dispatch Table

| Extension | First Move | Next Steps |
|-----------|-----------|-----------|
| `.pdf` | `pdfinfo` + text sample | Use pdf-reading skill for content inventory |
| `.docx` | `extract-text` | Use docx skill for editing/creation |
| `.doc` | Convert to `.docx` first | Use docx skill |
| `.xlsx` | `extract-text` | Use xlsx skill for formulas/formatting |
| `.xlsm` | `extract-text --format xlsx` | Use xlsx skill |
| `.xls` | `pd.read_excel(engine="xlrd")` | Use xlsx skill |
| `.ods` | `pd.read_excel(engine="odf")` | Use xlsx skill |
| `.pptx` | `extract-text` | Use pptx skill for creation/editing |
| `.ppt` | Convert to `.pptx` first | Use pptx skill |
| `.csv`, `.tsv` | `pandas` with `nrows` | Full analysis only after you know shape |
| `.json`, `.jsonl` | `jq 'type'` then drill in | Structure first, content second |
| `.jpg`, `.png`, `.gif`, `.webp` | Already visible in your context as vision input | Use for processing only |
| `.zip`, `.tar`, `.tar.gz` | List contents with `unzip -l` or `tar -tf` | Extract only if user explicitly asks |
| `.gz` (single file) | `zcat \| head` | No manifest to list |
| `.epub`, `.odt` | `extract-text` | Pipe through `head` for long files |
| `.rtf`, `.ipynb` | `extract-text` | Use appropriate tool |
| `.txt`, `.md`, `.log` | `wc -c` then `head` or full `cat` | Large files need sampling |
| Unknown | `file` then decide | Ask user if uncertain |

## CSV / TSV

**Do not** `cat` or `head` blindly — a CSV with a 50KB quoted cell in row 1 will wreck your `head -5`:

```python
import pandas as pd
df = pd.read_csv("/path/to/file.csv", nrows=5)
print(df)
print(df.dtypes)
```

Approximate row count (over-counts if file has RFC-4180 quoted newlines):
```bash
wc -l /path/to/file.csv
```

## JSON / JSONL

Structure first, content second:
```bash
jq 'type' file.json
jq 'if type == "array" then length elif type == "object" then keys else . end' file.json
```

JSONL (one object per line) — do **not** `jq` the whole file:
```bash
head -3 /path/to/file.jsonl | jq .
wc -l /path/to/file.jsonl
```

## Images

**You can already see uploaded images** in your context as vision inputs. They are not in `/mnt/user-data/uploads/` paths unless you explicitly need to process them programmatically.

Use disk copy only for processing (PIL, pytesseract, etc.), not for viewing or description.

## Archives (ZIP / TAR / TAR.GZ)

**List first. Extract never — unless user explicitly asks.**

```bash
unzip -l bundle.zip
tar -tf bundle.tar
```

GNU tar auto-detects compression. If user wants one file from inside:
```bash
unzip -p bundle.zip path/inside/file.txt
```

## Plain Text / Code / Logs

Check size first:
```bash
wc -c app.log
```

- **Under ~20KB**: `cat` is fine
- **Over ~20KB**: `head -100` and `tail -100` to orient; `grep` for specifics

For log files, the user usually cares about the end:
```bash
tail -200 app.log
```

## Dependencies

- `extract-text` - Universal text extraction (docx, xlsx, pptx, epub, odt, rtf, ipynb)
- `pdfinfo`, `pdftotext` - PDF inspection and extraction
- `jq` - JSON parsing and inspection
- `pandas` - CSV/TSV/Excel reading and analysis
