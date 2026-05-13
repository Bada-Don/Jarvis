---
name: pptx
description: "Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions \"deck,\" \"slides,\" \"presentation,\" or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill."
license: Proprietary. LICENSE.txt has complete terms
---

# PPTX Skill

## Reading Content

```bash
# Text extraction, one `## Slide N` section per slide
extract-text presentation.pptx

# Visual overview
python scripts/thumbnail.py presentation.pptx

# Raw XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

## Creating from Scratch

Use when no template or reference presentation is available. Use **pptxgenjs** (Node.js library).

Install: `npm install -g pptxgenjs`

```javascript
const PptxGenJS = require('pptxgenjs');
const prs = new PptxGenJS();

// Add slide
let slide = prs.addSlide();
slide.background = { color: "FFFFFF" };
slide.addText("Title", { x: 1, y: 1, fontSize: 44, bold: true });
slide.addText("Subtitle", { x: 1, y: 2, fontSize: 24 });

// Save
prs.writeFile({ fileName: "presentation.pptx" });
```

### Design Principles

**Pick a bold aesthetic:**
- Dominance over equality: One color should dominate (60-70% visual weight)
- Dark/light contrast: Dark backgrounds for title + conclusion slides, light for content
- Visual motif: Pick ONE distinctive element and repeat it

**Color Palettes (choose based on topic):**

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Midnight Executive** | `1E2761` | `CADCFC` | `FFFFFF` |
| **Forest & Moss** | `2C5F2D` | `97BC62` | `F5F5F5` |
| **Coral Energy** | `F96167` | `F9E795` | `2F3C7E` |
| **Teal Trust** | `028090` | `00A896` | `02C39A` |
| **Cherry Bold** | `990011` | `FCF6F5` | `2F3C7E` |

**Typography:**
- Choose distinctive header and body font pairs
- Avoid Arial; use Georgia, Calibri, Cambria, Trebuchet MS, etc.
- Title: 36-44pt bold
- Section header: 20-24pt bold
- Body: 14-16pt
- Captions: 10-12pt

**Layout:**
- Two-column (text left, illustration right)
- Icon + text rows (icon in colored circle, header, description)
- 2x2 or 2x3 grid layouts
- Half-bleed image with content overlay
- Always include visual element — image, chart, icon, or shape

**Spacing:**
- 0.5" minimum margins
- 0.3-0.5" between content blocks
- Leave breathing room

### Avoid (Common Mistakes)

- **Don't repeat the same layout** — vary columns, cards, and callouts
- **Don't center body text** — left-align paragraphs and lists
- **Don't skimp on size contrast** — titles need 36pt+ to stand out
- **Don't default to blue** — pick colors reflecting your topic
- **Don't create text-only slides** — add images, icons, charts, or visual elements
- **Don't use low-contrast elements** — icons AND text need strong contrast
- **NEVER use accent lines under titles** — use whitespace or background color
- **Don't add decorative full-width colored bars** — header/footer bars read as AI slop
- **Don't default to cream/beige backgrounds** — use white (`FFFFFF`) or your brand palette
- **Don't ship text that overflows** — if text doesn't fit, reduce font size or split across slides

## Converting Presentations to Images

Convert slides to individual images for visual inspection:

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
rm -f slide-*.jpg
pdftoppm -jpeg -r 150 output.pdf slide
ls -1 "$PWD"/slide-*.jpg
```

After fixes, rerun all four commands — the PDF must be regenerated from the edited `.pptx`.

## Dependencies

- `npm install -g pptxgenjs` - creating from scratch
- LibreOffice (`soffice`) - PDF conversion
- Poppler (`pdftoppm`) - PDF to images
