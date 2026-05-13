---
name: spreadsheets
description: "Use this skill whenever the primary input or output is a spreadsheet file. Triggers: any mention of .xlsx, .xlsm, .xls, .ods, .csv, .tsv; requests to 'create spreadsheet', 'update Excel', 'add column', 'calculate formula', 'format cells', 'pivot table', 'data analysis', 'financial model'. Delegates from file_reading when the file extension is a spreadsheet type. Do NOT use for Word docs (word_docs), PDFs (pdf_handling), or plain code files (file_editing)."
---

# Spreadsheets — XLSX / CSV / ODS Creation & Editing

## Core Principle: Formula-First

**Always use Excel formulas instead of hardcoded calculated values.** This keeps sheets dynamic and auditable.

❌ **WRONG** — hardcoding a result:
```python
total = df["Sales"].sum()
sheet["B10"] = total           # locked-in value, breaks if data changes
```

✅ **CORRECT** — letting Excel compute:
```python
sheet["B10"] = "=SUM(B2:B9)"  # dynamic, recalculates automatically
```

---

## Reading Spreadsheets

### Quick shape check (always run first)
```python
import pandas as pd

df = pd.read_excel(r"C:\path\to\file.xlsx", nrows=5)
print(f"Columns: {list(df.columns)}")
print(f"Dtypes:\n{df.dtypes}")
print(df)
```

### Full shape without loading all data
```python
from openpyxl import load_workbook

wb = load_workbook(r"C:\path\to\file.xlsx", read_only=True, data_only=True)
for name in wb.sheetnames:
    ws = wb[name]
    print(f"{name}: {ws.max_row} rows × {ws.max_column} cols")
wb.close()
```

### All sheets
```python
all_sheets = pd.read_excel(r"C:\path\to\file.xlsx", sheet_name=None)
for name, df in all_sheets.items():
    print(f"{name}: {df.shape}")
```

### CSV / TSV
```python
# Encoding-safe CSV read
df = pd.read_csv(r"C:\path\to\file.csv", encoding="utf-8-sig", nrows=5)
# Row count without loading
with open(r"C:\path\to\file.csv", encoding="utf-8-sig") as f:
    row_count = sum(1 for _ in f) - 1  # subtract header row
print(f"~{row_count} rows")
```

---

## Creating New Excel Files

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "Data"

# Headers
headers = ["Month", "Revenue", "Expenses", "Net Profit"]
for col, header in enumerate(headers, start=1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="1F4E79")
    cell.alignment = Alignment(horizontal="center")

# Data rows
rows = [
    ("Jan", 50000, 30000),
    ("Feb", 60000, 32000),
    ("Mar", 55000, 28000),
]
for r, (month, rev, exp) in enumerate(rows, start=2):
    ws.cell(row=r, column=1, value=month)
    ws.cell(row=r, column=2, value=rev)
    ws.cell(row=r, column=3, value=exp)
    # FORMULA — not hardcoded
    ws.cell(row=r, column=4, value=f"=B{r}-C{r}")

# Summary row
last = len(rows) + 1
ws.cell(row=last + 1, column=1, value="TOTAL")
ws.cell(row=last + 1, column=2, value=f"=SUM(B2:B{last})")
ws.cell(row=last + 1, column=3, value=f"=SUM(C2:C{last})")
ws.cell(row=last + 1, column=4, value=f"=SUM(D2:D{last})")

# Column widths
for col in range(1, 5):
    ws.column_dimensions[get_column_letter(col)].width = 16

wb.save(r"C:\Users\harsh\Desktop\report.xlsx")
print("Saved.")
```

---

## Editing Existing Files

```python
from openpyxl import load_workbook

# IMPORTANT: data_only=False preserves formulas
wb = load_workbook(r"C:\path\to\existing.xlsx")
ws = wb.active        # or wb["SheetName"]

# Modify a cell
ws["B5"] = "=B4*1.1"  # formula, not a hardcoded value

# Insert row at position 3
ws.insert_rows(3)

# Delete column 4
ws.delete_cols(4)

# Add a new sheet
new_ws = wb.create_sheet("Summary")
new_ws["A1"] = "Auto-generated summary"

wb.save(r"C:\path\to\existing.xlsx")
```

⚠️ **WARNING:** Opening with `data_only=True` then saving **permanently replaces formulas with their last calculated values**. Never do this unless intentional.

---

## Recalculating Formulas

`openpyxl` writes formula strings but does NOT evaluate them. Use the recalc helper (which uses MS Excel COM) after saving:

```python
# python backend/scripts/office/recalc_xlsx.py "C:\path\to\output.xlsx"
import subprocess
subprocess.run(
    ["python", r"backend\scripts\office\recalc_xlsx.py", r"C:\path\to\output.xlsx"],
    check=True
)
```

The helper script uses LibreOffice headless to force-recalculate all sheets and scan for `#REF!`, `#DIV/0!`, `#VALUE!` errors.

---

## Data Analysis with pandas

```python
import pandas as pd

df = pd.read_excel(r"C:\path\to\file.xlsx")

# Basic stats
print(df.describe())

# Filter
high_rev = df[df["Revenue"] > 50_000]

# Group & aggregate
monthly = df.groupby("Month")["Revenue"].sum().reset_index()

# Export back to Excel (preserves index=False)
monthly.to_excel(r"C:\path\to\summary.xlsx", index=False)
```

---

## Financial Model Standards

### Color Coding (industry standard)
| Color | Meaning |
|-------|---------|
| **Blue text** | Hardcoded inputs / changeable assumptions |
| **Black text** | All formula outputs and calculations |
| **Green text** | Links pulling from other worksheets |
| **Red text** | External links to other files |
| **Yellow background** | Key assumptions needing review |

```python
from openpyxl.styles import Font, PatternFill

# Hardcoded input → blue
cell.font = Font(color="0070C0")

# Formula output → black (default, but set explicitly)
cell.font = Font(color="000000")

# Key assumption → yellow background
cell.fill = PatternFill("solid", fgColor="FFFF00")
```

### Number Formatting
```python
from openpyxl.styles import numbers

cell.number_format = "$#,##0"          # Currency
cell.number_format = "0.0%"            # Percentage
cell.number_format = "0.0x"            # Multiples (EV/EBITDA)
cell.number_format = "$#,##0;($#,##0);-"  # With negatives in parentheses
cell.number_format = "@"               # Text (for year labels)
```

### Formula Construction Rules
- All assumptions in dedicated assumption cells — **never hardcode inside formulas**
- Use named ranges for cross-sheet references: `=Assumptions!B3` not `=Sheet2!B3`
- Verify all cell references are correct before saving
- Check for off-by-one errors in SUM ranges
- Use consistent formulas across all projection periods (copy-paste one correct column)

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `NaN` in numeric columns | `df.fillna(0)` or `pd.notna()` guard |
| FY data in far-right columns (col 50+) | Use `usecols` or `openpyxl` column iteration |
| `#DIV/0!` errors | `=IFERROR(A1/B1, 0)` or check denominator |
| `#REF!` after row/col delete | Use `scripts/office/recalc_xlsx.py` to scan |
| Encoding issues in CSV | Open with `encoding="utf-8-sig"` |
| Formula strings not calculating | Run `recalc_xlsx.py` via LibreOffice |

---

## Data Validation (dropdowns, constraints)

```python
from openpyxl.worksheet.datavalidation import DataValidation

dv = DataValidation(
    type="list",
    formula1='"Active,Inactive,Pending"',
    allow_blank=True,
    showDropDown=False   # False = show dropdown arrow
)
ws.add_data_validation(dv)
dv.add("C2:C100")       # Apply to range
```

---

## Library Selection Guide

| Need | Library |
|------|---------|
| Bulk data load, analysis, joins | `pandas` |
| Formulas, formatting, charts | `openpyxl` |
| Legacy `.xls` (Excel 97-2003) | `xlrd` engine via pandas |
| ODS (LibreOffice Calc) | `odf` engine via pandas |
| High-perf read-only (large files) | `openpyxl(read_only=True)` |

---

## Dependencies

| Library | Purpose | Install |
|---------|---------|---------|
| `openpyxl` | XLSX read/write/format | `pip install openpyxl` |
| `pandas` | Data analysis, CSV, bulk ops | `pip install pandas` |
| `xlrd` | Legacy `.xls` reading | `pip install xlrd` |
| `odfpy` | ODS reading | `pip install odfpy` |
| LibreOffice | Formula recalculation | System package |
