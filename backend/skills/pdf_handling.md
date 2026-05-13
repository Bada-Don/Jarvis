---
name: pdf_handling
description: "Use this skill whenever a PDF file is involved — reading, extracting text or tables, inspecting metadata, OCR on scanned pages, merging, splitting, rotating, watermarking, or creating new PDFs. Triggers: any mention of '.pdf', 'extract from PDF', 'read PDF', 'how many pages', 'PDF table', 'scan to text', 'merge PDFs', 'split PDF', 'add watermark', 'PDF form'. Delegates from file_reading when extension is .pdf. Also handles form field extraction and embedded attachment detection."
---

# PDF Handling — Read, Extract, Create & Manipulate

## Content Inventory (always run first)

```python
import subprocess, sys

def pdf_info(path: str):
    """Run pdfinfo and return parsed metadata dict."""
    result = subprocess.run(
        ["pdfinfo", path], capture_output=True, text=True, check=True
    )
    info = {}
    for line in result.stdout.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            info[k.strip()] = v.strip()
    return info

meta = pdf_info(r"C:\path\to\document.pdf")
print(meta)
# {'Pages': '12', 'File size': '1.2 MB', 'Title': '...', ...}
```

Quick text sample to distinguish text PDF from scan:
```python
result = subprocess.run(
    ["pdftotext", "-f", "1", "-l", "1", r"C:\path\to\document.pdf", "-"],
    capture_output=True, text=True
)
if len(result.stdout.strip()) < 50:
    print("⚠️  Likely a scanned PDF — use OCR path")
else:
    print("✅ Text-based PDF — use extraction path")
```

---

## Text Extraction

### Basic (pypdf)
```python
from pypdf import PdfReader

reader = PdfReader(r"C:\path\to\document.pdf")
print(f"Pages: {len(reader.pages)}")

text = ""
for page in reader.pages:
    text += page.extract_text() or ""
print(text[:2000])
```

### Layout-aware (pdfplumber — preferred for complex docs)
```python
import pdfplumber

with pdfplumber.open(r"C:\path\to\document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"\n=== Page {i+1} ===")
        print(page.extract_text())
```

### Multi-column layout (CLI)
```python
subprocess.run(
    ["pdftotext", "-layout", r"C:\path\to\document.pdf", r"C:\path\to\output.txt"],
    check=True
)
```

---

## Table Extraction

```python
import pdfplumber, pandas as pd

all_tables = []

with pdfplumber.open(r"C:\path\to\document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            if not table:
                continue
            # First row as header
            df = pd.DataFrame(table[1:], columns=table[0])
            df["_source_page"] = i + 1
            df["_table_idx"] = j + 1
            all_tables.append(df)
            print(f"Page {i+1}, Table {j+1}: {df.shape}")

# Save all tables to Excel
if all_tables:
    combined = pd.concat(all_tables, ignore_index=True)
    combined.to_excel(r"C:\path\to\tables.xlsx", index=False)
    print(f"Extracted {len(all_tables)} tables → tables.xlsx")
```

---

## Visual Inspection (Rasterize Pages)

Text extraction is **blind** to charts, diagrams, equations, and scanned content. Rasterize when layout matters:

```python
# Rasterize page 3 at 150 DPI → JPEG
subprocess.run(
    ["pdftoppm", "-jpeg", "-r", "150", "-f", "3", "-l", "3",
     r"C:\path\to\document.pdf", r"C:\temp\page"],
    check=True
)
# Creates C:\temp\page-3.jpg
```

**Decision guide:**
| Content type | Strategy |
|-------------|---------|
| Text / narrative | Text extraction (cheaper, searchable) |
| Charts, diagrams | Rasterize the page |
| Tables | Try text extraction first; rasterize if garbled |
| Mixed / precision | Do both |

---

## OCR for Scanned PDFs

```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path(r"C:\path\to\scanned.pdf", dpi=200)
text = ""
for i, img in enumerate(images):
    page_text = pytesseract.image_to_string(img, lang="eng")
    text += f"\n=== Page {i+1} ===\n{page_text}"

print(text)
```

---

## Metadata & Diagnostics

```python
from pypdf import PdfReader

reader = PdfReader(r"C:\path\to\document.pdf")
meta = reader.metadata
print(f"Title:   {meta.title}")
print(f"Author:  {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
print(f"Pages:   {len(reader.pages)}")

# Font check (garbled text diagnosis)
subprocess.run(["pdffonts", r"C:\path\to\document.pdf"])
# If 'emb' column shows 'no' → rasterize instead of text-extract
```

---

## Form Field Extraction

```python
from pypdf import PdfReader

reader = PdfReader(r"C:\path\to\form.pdf")

# Text fields only
text_fields = reader.get_form_text_fields()
for name, value in text_fields.items():
    print(f"  {name}: {value}")

# All field types (checkboxes, radio, dropdowns)
all_fields = reader.get_fields() or {}
for name, field in all_fields.items():
    print(f"  {name}: {field.get('/V', '')} [{field.get('/FT', '')}]")
```

---

## Embedded Attachments

```python
from pypdf import PdfReader
import os

reader = PdfReader(r"C:\path\to\document.pdf")
out_dir = r"C:\path\to\attachments"
os.makedirs(out_dir, exist_ok=True)

for name, content_list in reader.attachments.items():
    safe_name = os.path.basename(name)
    for content in content_list:
        with open(os.path.join(out_dir, safe_name), "wb") as f:
            f.write(content)
        print(f"Extracted: {safe_name}")
```

---

## Merge, Split, Rotate

### Merge multiple PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_path in [r"C:\doc1.pdf", r"C:\doc2.pdf", r"C:\doc3.pdf"]:
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        writer.add_page(page)

with open(r"C:\merged.pdf", "wb") as f:
    writer.write(f)
```

### Split into individual pages
```python
reader = PdfReader(r"C:\path\to\input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(rf"C:\path\to\page_{i+1}.pdf", "wb") as f:
        writer.write(f)
```

### Rotate pages
```python
reader = PdfReader(r"C:\path\to\input.pdf")
writer = PdfWriter()
for page in reader.pages:
    page.rotate(90)       # 90, 180, or 270 degrees clockwise
    writer.add_page(page)
with open(r"C:\path\to\rotated.pdf", "wb") as f:
    writer.write(f)
```

---

## Add Watermark

```python
from pypdf import PdfReader, PdfWriter

watermark_page = PdfReader(r"C:\path\to\watermark.pdf").pages[0]
reader = PdfReader(r"C:\path\to\document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark_page)
    writer.add_page(page)

with open(r"C:\path\to\watermarked.pdf", "wb") as f:
    writer.write(f)
```

---

## Create New PDFs (reportlab)

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate(r"C:\path\to\report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph("Report Title", styles["Title"]))
story.append(Spacer(1, 12))
story.append(Paragraph("Body paragraph here.", styles["Normal"]))
story.append(PageBreak())
story.append(Paragraph("Page 2 content", styles["Heading1"]))

doc.build(story)
```

⚠️ **IMPORTANT:** Never use Unicode subscript/superscript characters (₀ ₁ ⁰ ¹) in ReportLab — they render as solid black boxes. Use `<sub>` and `<super>` XML tags in `Paragraph` instead:
```python
Paragraph("H<sub>2</sub>O and x<super>2</super>", styles["Normal"])
```

---

## Reading Strategy by Document Type

| Document type | Strategy |
|--------------|---------|
| Text-heavy (reports, books) | `pdfplumber` text extraction; rasterize only for figures |
| Scanned (no text layer) | Rasterize at 200 DPI → `pytesseract` OCR |
| Slide-deck PDF | Every page is visual — rasterize individual pages |
| Form-heavy | `pypdf.get_fields()` first; rasterize for visual context |
| Data-heavy (tables/charts) | `pdfplumber.extract_tables()` + rasterize chart pages |

---

## Quick Reference

| Task | Best Tool | Method |
|------|---------|--------|
| Inspect PDF | `pdfinfo` (CLI) | subprocess call |
| Extract text | `pdfplumber` | `page.extract_text()` |
| Extract tables | `pdfplumber` | `page.extract_tables()` |
| Rasterize page | `pdftoppm` (CLI) | `-jpeg -r 150 -f N -l N` |
| OCR scan | `pytesseract` | Convert to image first |
| Extract images | `pdfimages` (CLI) | `-png input.pdf prefix` |
| Extract attachments | `pypdf` | `reader.attachments` |
| Read form fields | `pypdf` | `reader.get_fields()` |
| Merge | `pypdf` | `PdfWriter.add_page()` |
| Split | `pypdf` | One page per writer |
| Rotate | `pypdf` | `page.rotate(90)` |
| Create new | `reportlab` | `SimpleDocTemplate` |

---

## Dependencies

| Library | Purpose | Install |
|---------|---------|---------|
| `pypdf` | Read, merge, split, metadata | `pip install pypdf` |
| `pdfplumber` | Text + table extraction | `pip install pdfplumber` |
| `reportlab` | Create new PDFs | `pip install reportlab` |
| `pytesseract` | OCR for scanned PDFs | `pip install pytesseract` |
| `pdf2image` | PDF → PIL images for OCR | `pip install pdf2image` |
| `poppler-utils` | `pdfinfo`, `pdftotext`, `pdftoppm`, `pdfimages` | System package |
