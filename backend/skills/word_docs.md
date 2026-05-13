---
name: word_docs
description: "Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx). Triggers: 'Word doc', 'word document', '.docx', 'create report', 'edit memo', 'letter template', 'tracked changes', 'insert table', 'add heading', 'replace text in Word', 'comment in document'. Do NOT use for PDFs (use pdf_handling), spreadsheets (use spreadsheets), or general text files (use file_editing)."
---

# Word Documents (DOCX) — Creation, Editing & XML Manipulation

## Overview

A `.docx` file is a ZIP archive of XML files. All editing strategies flow through three layers:

| Layer | Use When | Tool |
|-------|---------|------|
| High-level API | Creating new docs, simple edits | `python-docx` |
| XML direct edit | Complex formatting, tracked changes | Unpack → edit XML → repack |
| AI-edit bridge | Natural language instructions | `ai_edit_word` action type |

---

## Quick Reference

| Task | Approach |
|------|---------|
| Read / inspect content | `python-docx` paragraph walk |
| Create new document | `python-docx` — see Creating New Documents |
| Simple find & replace | `replace_in_docx()` helper — see Editing |
| Tables, headings, images | `python-docx` — see Formatting |
| Tracked changes / comments | Unpack → XML → repack (see XML Editing) |
| Convert `.doc` → `.docx` | `convert_doc.py` helper (Word COM) |

---

## Reading Content

```python
from docx import Document

doc = Document(r"C:\path\to\document.docx")

# All paragraphs
for para in doc.paragraphs:
    if para.text.strip():
        print(f"[{para.style.name}] {para.text}")

# Tables
for i, table in enumerate(doc.tables):
    print(f"\n=== Table {i+1} ===")
    for row in table.rows:
        print([cell.text for cell in row.cells])
```

For full text extraction (fastest):
```python
full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
```

---

## Creating New Documents

### Minimal template
```python
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Title
title = doc.add_heading("Report Title", level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Body
doc.add_paragraph("Introduction paragraph here.")

# Heading + body
doc.add_heading("Section 1", level=1)
doc.add_paragraph("Section content here.")

doc.save(r"C:\Users\harsh\Desktop\output.docx")
print("Saved successfully.")
```

### Rich formatting
```python
from docx.shared import Pt, RGBColor, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

para = doc.add_paragraph()
run = para.add_run("Bold red text")
run.bold = True
run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
run.font.size = Pt(14)
```

### Bullet lists
```python
# Use Word's built-in List Bullet style — NEVER manually insert • characters
doc.add_paragraph("First item", style="List Bullet")
doc.add_paragraph("Second item", style="List Bullet")
doc.add_paragraph("Numbered item", style="List Number")
```

### Tables
```python
from docx.shared import Pt
from docx.oxml.ns import qn

table = doc.add_table(rows=1, cols=3)
table.style = "Table Grid"

# Header row
hdr = table.rows[0].cells
hdr[0].text = "Name"
hdr[1].text = "Role"
hdr[2].text = "Status"

# Data rows
data = [("Alice", "Developer", "Active"), ("Bob", "Manager", "Active")]
for name, role, status in data:
    row = table.add_row().cells
    row[0].text = name
    row[1].text = role
    row[2].text = status
```

### Images
```python
doc.add_picture(r"C:\path\to\image.png", width=Inches(4))
```

### Headers & Footers
```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

section = doc.sections[0]

# Header
header = section.header
header.paragraphs[0].text = "Company Confidential"

# Footer with page number
footer = section.footer
footer_para = footer.paragraphs[0]
footer_para.text = "Page "
# Append page number field
run = footer_para.add_run()
fldChar = OxmlElement("w:fldChar")
fldChar.set(qn("w:fldCharType"), "begin")
run._r.append(fldChar)
instrText = OxmlElement("w:instrText")
instrText.text = "PAGE"
run._r.append(instrText)
fldChar2 = OxmlElement("w:fldChar")
fldChar2.set(qn("w:fldCharType"), "end")
run._r.append(fldChar2)
```

---

## Editing Existing Documents

### Simple find & replace
Use the `replace_in_docx` helper (backend/scripts/office/replace_in_docx.py):
```python
# Called via shell_command or directly in Python
# python backend/scripts/office/replace_in_docx.py "input.docx" "output.docx" "John Doe" "Jane Smith"
```

Or inline:
```python
from docx import Document

def replace_text(doc_path: str, out_path: str, old: str, new: str):
    doc = Document(doc_path)
    for para in doc.paragraphs:
        if old in para.text:
            for run in para.runs:
                if old in run.text:
                    run.text = run.text.replace(old, new)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        if old in run.text:
                            run.text = run.text.replace(old, new)
    doc.save(out_path)

replace_text(r"C:\path\input.docx", r"C:\path\output.docx", "old name", "new name")
```

### AI-powered editing (natural language)
```json
{
  "type": "ai_edit_word",
  "path": "desktop/report",
  "prompt": "Replace all occurrences of 'John Doe' with 'Harshit Singla' and update the date to today",
  "desc": "Update author name and date in Word document"
}
```

---

## XML-Level Editing (Advanced)

For tracked changes, comments, or complex formatting that python-docx cannot express.

### Step 1: Unpack
```python
# python backend/scripts/office/unpack.py document.docx unpacked/
```

Unpacks to `unpacked/word/document.xml` and related files.

### Step 2: Edit XML

**Smart quotes** — use XML entities for professional typography:
| Entity | Character |
|--------|-----------|
| `&#x2018;` | ' (left single) |
| `&#x2019;` | ' (right single / apostrophe) |
| `&#x201C;` | " (left double) |
| `&#x201D;` | " (right double) |

**Tracked insertion:**
```xml
<w:ins w:id="1" w:author="Jarvis" w:date="2025-01-01T00:00:00Z">
  <w:r><w:t>inserted text</w:t></w:r>
</w:ins>
```

**Tracked deletion:**
```xml
<w:del w:id="2" w:author="Jarvis" w:date="2025-01-01T00:00:00Z">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
```

**Comment markers** (add after running `comment.py`):
```xml
<w:commentRangeStart w:id="0"/>
<w:r><w:t>text being commented</w:t></w:r>
<w:commentRangeEnd w:id="0"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>
```

### Step 3: Repack
```python
# python backend/scripts/office/pack.py unpacked/ output.docx --original document.docx
```

---

## Format Conversion

### .doc → .docx (MS Word)
Use the COM helper:
```python
# python backend/scripts/office/convert_doc.py "input.doc" "output.docx"
```

### DOCX → PDF (MS Word)
```python
import win32com.client, os
word = win32com.client.DispatchEx("Word.Application")
doc = word.Documents.Open(os.path.abspath("document.docx"))
# wdFormatPDF = 17
doc.ExportAsFixedFormat(os.path.abspath("document.pdf"), 17)
doc.Close()
word.Quit()
```

---

## Critical Rules

- **Never use `\n` inside a run** — create separate `Paragraph` objects instead
- **Never manually insert bullet characters (•)** — use `style="List Bullet"`
- **Always copy `<w:rPr>` when writing tracked changes** — preserves bold, size, font
- **Use `ShadingType.CLEAR` not `SOLID`** for table cell shading (avoids black backgrounds)
- **`<w:commentRangeStart>` and `<w:commentRangeEnd>` are siblings of `<w:r>`** — never inside `<w:r>`
- **Use `Jarvis` as the tracked-change author** unless the user specifies otherwise

---

## Dependencies

| Library | Purpose | Install |
|---------|---------|---------|
| `python-docx` | All high-level DOCX operations | `pip install python-docx` |
| `pywin32` | MS Office COM Automation | `pip install pywin32` |
| `lxml` | Low-level XML editing | `pip install lxml` |
