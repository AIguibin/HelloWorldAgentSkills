---
name: aiguibin-sheet-copier
description: Copy Excel worksheet to multiple files with full formatting preservation. Use when Claude needs to copy a worksheet from one Excel file to multiple target Excel files while preserving all cell formatting, borders, fonts, fills, formulas, and merged cells. Supports specifying source file, target directory, sheet index, and insertion position.
---

# Aiguibin Sheet Copier

Copy Excel worksheets across multiple files with complete formatting preservation.

## Quick Start

Use the bundled script to copy a worksheet:

```bash
python scripts/copy_sheet.py --source <source-file> --target-dir <target-directory>
```

## Parameters

- `--source` (required): Path to source Excel file
- `--target-dir` (required): Directory containing target Excel files
- `--sheet-index` (optional): Sheet index to copy (default: 0)
- `--insert-position` (optional): Position to insert sheet in target files (default: 0)
- `--files` (optional): Specific target files to process (default: all Excel files in directory)

## Examples

### Copy first sheet to all files in directory

```bash
python scripts/copy_sheet.py \
  --source "template.xlsx" \
  --target-dir "./output"
```

### Copy specific sheet to specific files

```bash
python scripts/copy_sheet.py \
  --source "template.xlsx" \
  --target-dir "./output" \
  --sheet-index 1 \
  --files "file1.xlsx" "file2.xlsx" "file3.xlsx"
```

### Copy and insert at position 1

```bash
python scripts/copy_sheet.py \
  --source "template.xlsx" \
  --target-dir "./output" \
  --insert-position 1
```

## What Gets Preserved

- Cell values and formulas
- Font styles (bold, italic, size, color)
- Cell borders (all sides, styles, colors)
- Fill colors and patterns
- Number formats
- Text alignment
- Merged cells

## Script Functions

The script provides a Python function for programmatic use:

```python
from scripts.copy_sheet import copy_sheet_to_multiple_files

copy_sheet_to_multiple_files(
    source_file="template.xlsx",
    target_dir="./output",
    sheet_index=0,
    target_files=["file1.xlsx", "file2.xlsx"],
    insert_position=0
)
```

## Requirements

- Python 3.6+
- openpyxl: `pip install openpyxl`
