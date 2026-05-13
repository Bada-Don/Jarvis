---
name: xlsx
description: "Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: open, read, edit, or fix an existing .xlsx, .xlsm, .csv, or .tsv file; create a new spreadsheet from scratch or from other data sources; or convert between tabular file formats. Trigger especially when the user references a spreadsheet file by name or path. The deliverable must be a spreadsheet file."
license: Proprietary. LICENSE.txt has complete terms
---

# XLSX Skill

## Key Principle

**Always use Excel formulas instead of hardcoded values.** This keeps spreadsheets dynamic and updateable.

❌ WRONG - Hardcoding calculated values:
```python
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes 5000
```

✅ CORRECT - Using Excel formulas:
```python
sheet['B10'] = '=SUM(B2:B9)'
```

## Reading Spreadsheets

### Quick text dump
```bash
extract-text file.xlsx | head -100
```

### Data analysis with pandas
```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict

df.head()      # Preview
df.info()      # Column info
df.describe()  # Statistics
```

## Creating New Excel Files

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active

# Add data
sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet.append(['Row', 'of', 'data'])

# Add formula
sheet['B2'] = '=SUM(A1:A10)'

# Formatting
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')

# Column width
sheet.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

## Editing Existing Spreadsheets

```python
from openpyxl import load_workbook

# Load existing file
wb = load_workbook('existing.xlsx')
sheet = wb.active  # or wb['SheetName'] for specific sheet

# Working with multiple sheets
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    print(f"Sheet: {sheet_name}")

# Modify cells
sheet['A1'] = 'New Value'
sheet.insert_rows(2)  # Insert row at position 2
sheet.delete_cols(3)  # Delete column 3

# Add new sheet
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'

wb.save('modified.xlsx')
```

## Recalculating Formulas

Excel files created with openpyxl contain formulas as strings but not calculated values. Use LibreOffice to recalculate:

```bash
python scripts/recalc.py output.xlsx 30
```

The script:
- Automatically sets up LibreOffice macro on first run
- Recalculates all formulas in all sheets
- Scans ALL cells for Excel errors (#REF!, #DIV/0!, etc.)
- Returns JSON with detailed error locations and counts

## Common Pitfalls

- **NaN handling**: Check for null values with `pd.notna()`
- **Far-right columns**: FY data often in columns 50+
- **Division by zero**: Check denominators before using `/` (#DIV/0!)
- **Wrong references**: Verify all cell references point to intended cells (#REF!)
- **Cross-sheet references**: Use correct format (Sheet1!A1) for linking sheets

## Financial Model Standards

### Color Coding
- **Blue text**: Hardcoded inputs and changeable numbers
- **Black text**: ALL formulas and calculations
- **Green text**: Links pulling from other worksheets
- **Red text**: External links to other files
- **Yellow background**: Key assumptions needing attention

### Number Formatting
- **Years**: Format as text strings (e.g., "2024" not "2,024")
- **Currency**: Use $#,##0 format; specify units in headers ("Revenue ($mm)")
- **Zeros**: Format all zeros as "-" (e.g., "$#,##0;($#,##0);-")
- **Percentages**: Default to 0.0% format
- **Multiples**: Format as 0.0x for valuation multiples (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses (123) not minus -123

### Formula Construction Rules
- Place ALL assumptions in separate assumption cells
- Use cell references instead of hardcoded values
- Verify all cell references are correct
- Check for off-by-one errors in ranges
- Ensure consistent formulas across all projection periods

## Library Selection

- **pandas**: Best for data analysis, bulk operations, and simple data export
- **openpyxl**: Best for complex formatting, formulas, and Excel-specific features

## Best Practices

### For openpyxl
- Cell indices are 1-based (row=1, column=1 refers to cell A1)
- **Warning**: If opened with `data_only=True` and saved, formulas are permanently replaced with values
- For large files: Use `read_only=True` for reading or `write_only=True` for writing
- Formulas are preserved but not evaluated — use scripts/recalc.py to update values

### For pandas
- Specify data types to avoid inference issues: `pd.read_excel('file.xlsx', dtype={'id': str})`
- For large files, read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates properly: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Dependencies

- `openpyxl`: `pip install openpyxl`
- `pandas`: `pip install pandas`
- LibreOffice: System package (auto-configured for formula recalculation)
