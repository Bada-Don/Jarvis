---
name: pdf-reading
description: "Use this skill when you need to read, inspect, or extract content from PDF files — especially when file content is NOT in your context and you need to read it from disk. Covers content inventory, text extraction, page rasterization for visual inspection, embedded image/attachment/table/form-field extraction, and choosing the right reading strategy for different document types (text-heavy, scanned, slide-decks, forms, data-heavy). Do NOT use this skill for PDF creation, form filling, merging, splitting, watermarking, or encryption — use the pdf skill instead."
license: Proprietary. LICENSE.txt has complete terms
---

# PDF Reading Guide

## Content Inventory

Run a quick diagnostic first:

```bash
# Always: page count, file size, PDF version, metadata
pdfinfo document.pdf

# Always: quick text extraction check — is this a text PDF or a scan?
pdftotext -f 1 -l 1 document.pdf - | head -20

# If figures/charts may matter:
pdfimages -list document.pdf

# If the PDF might contain embedded files (reports, portfolios):
pdfdetach -list document.pdf

# If text extraction looks garbled:
pdffonts document.pdf
```

## Text Extraction

**pypdf** for basic text:
```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

**pdftotext** preserving layout (better for multi-column docs):
```bash
# Layout mode preserves spatial positioning
pdftotext -layout document.pdf output.txt

# Specific page range
pdftotext -f 1 -l 5 document.pdf output.txt
```

**pdfplumber** for layout-aware extraction with positioning data:
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

## Visual Inspection (Rasterize Pages)

Text extraction is **blind** to charts, diagrams, figures, equations, and layout. When these matter, rasterize:

```bash
# Rasterize a single page (page 3 here) at 150 DPI
pdftoppm -jpeg -r 150 -f 3 -l 3 document.pdf /tmp/page
```

**When to rasterize vs. text-extract:**
- **Content/data questions → text extraction** (cheaper, searchable)
- **Figures, charts, visual layout → rasterize the page**
- **Tables → try text extraction first, rasterize if garbled**
- **Precision matters → do both** (extract text AND rasterize)

## Extracting Embedded Images

```bash
# List all embedded images with metadata (size, color, compression)
pdfimages -list document.pdf

# Extract all images as PNG
pdfimages -png document.pdf /tmp/img

# Extract from specific pages only (pages 3-5)
pdfimages -png -f 3 -l 5 document.pdf /tmp/img

# Extract in original format (JPEG stays JPEG, etc.)
pdfimages -all document.pdf /tmp/img
```

**Gotcha — vector graphics:** `pdfimages` extracts only raster image data. Charts and diagrams drawn as vector graphics will NOT appear — they are page content operators, not image objects. For these, rasterize the whole page with `pdftoppm` instead.

## Extracting File Attachments

PDFs can contain embedded files — spreadsheets, data files, other documents.

```bash
# List all attachments
pdfdetach -list document.pdf

# Extract all attachments to a directory
mkdir -p /tmp/attachments
pdfdetach -saveall -o /tmp/attachments/ document.pdf

# Extract a specific attachment by number (1-based index from -list output)
pdfdetach -save 1 -o /tmp/attachment.pdf document.pdf
```

In Python:
```python
import os
from pypdf import PdfReader

reader = PdfReader("document.pdf")
for name, content_list in reader.attachments.items():
    safe_name = os.path.basename(name)  # sanitize
    for content in content_list:
        with open(f"/tmp/{safe_name}", "wb") as f:
            f.write(content)
```

## Extracting Form Field Data

PDFs with interactive forms have fillable fields whose values can be read programmatically:

```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")

# Text input fields only:
fields = reader.get_form_text_fields()
for name, value in fields.items():
    print(f"{name}: {value}")

# All field types (checkboxes, radio buttons, dropdowns too):
all_fields = reader.get_fields() or {}
for name, field in all_fields.items():
    print(f"{name}: {field.get('/V', '')} (type: {field.get('/FT', '')})")
```

For comprehensive field info:
```bash
pdftk form.pdf dump_data_fields
```

## Reading Strategy by Document Type

**Text-heavy documents** (reports, articles, books):
→ Text extraction is primary. Rasterize only for specific figures or pages where layout matters.

**Scanned documents** (no extractable text):
→ Rasterize pages at 150 DPI and inspect visually. For bulk text extraction, use OCR.

**Slide-deck PDFs** (exported presentations):
→ Every page is primarily visual. Rasterize individual pages on demand.

**Form-heavy documents**:
→ Extract form field values programmatically first. Rasterize the form page for visual context if needed.

**Data-heavy documents** (tables, charts, figures):
→ Use pdfplumber for tables. Rasterize pages with charts/figures. Extract text for surrounding narrative.

## Font Diagnostics

If text extraction produces garbled output:

```bash
pdffonts document.pdf
```

Look at the "emb" column — if fonts show "no" (not embedded) with custom encodings, the PDF's character mapping may be broken for text extraction. In that case, rasterize the page and use vision instead.

## Quick Reference

| Task | Best Tool | Command |
|------|-----------|---------| 
| Inspect PDF | poppler-utils | `pdfinfo`, `pdfimages -list`, `pdfdetach -list`, `pdffonts` |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract text (CLI) | pdftotext | `pdftotext -layout input.pdf output.txt` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| See page visually | pdftoppm | `pdftoppm -jpeg -r 150 -f N -l N` |
| Extract images | pdfimages | `pdfimages -png input.pdf prefix` |
| Extract attachments | pdfdetach | `pdfdetach -saveall -o /tmp/` |
| Read form fields | pypdf | `reader.get_fields()` |
| OCR scanned PDFs | pytesseract | Convert to image first |
