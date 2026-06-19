---
name: aiguibin-excel-hyperlink
description: Add directory hyperlinks and return links to Excel files. Use when you need to add worksheet navigation functionality to Excel files that contain a directory worksheet, supporting custom directory worksheet names, table name column positions, and return link cell positions.
---

# Excel Hyperlink Addition

## Overview

Add bidirectional navigation hyperlinks to Excel files:
- **Directory to Worksheet**: Add hyperlinks for each table name in the directory worksheet, clicking jumps to the corresponding worksheet
- **Worksheet Return to Directory**: Add "Return to Directory" hyperlink in each target worksheet, clicking jumps back to the directory worksheet

## When to Use

Use this skill when you need to add navigation functionality to Excel files of the following types:
- Excel files containing a directory worksheet
- Directory contains a list of worksheet names
- Documents requiring quick navigation between worksheets

## Quick Start

### Basic Usage

```bash
python scripts/add_hyperlinks.py <excel_file_path>
```

### Custom Parameters

```bash
python scripts/add_hyperlinks.py <excel_file_path> --catalog <directory_sheet_name> --column <table_name_column> --return-cell <return_cell>
```

**Parameter Description:**
- `file_path`: Excel file path (required)
- `--catalog`: Directory worksheet name (default: 目录)
- `--column`: Column where table names are located (default: F)
- `--return-cell`: Return link cell position (default: N2)

### Usage Examples

**Example 1: Use default settings**
```bash
python scripts/add_hyperlinks.py "database_design_report.xlsx"
```

**Example 2: Custom directory worksheet name**
```bash
python scripts/add_hyperlinks.py "database_design_report.xlsx" --catalog "index_directory"
```

**Example 3: Custom table name column and return cell**
```bash
python scripts/add_hyperlinks.py "database_design_report.xlsx" --column "E" --return-cell "M2"
```

## Key Implementation Details

### Hyperlink Fix Points

This skill fixes common issues with openpyxl hyperlinks:

**Wrong Approach** (causes navigation failure):
```python
cell.hyperlink = f"'{sheet_name}'!A1"
```

**Correct Approach** (method used by this skill):
```python
cell.hyperlink = Hyperlink(
    ref=cell_ref,
    location=f"'{sheet_name}'!A1"
)
```

**Key Points:**
- Must set both `ref` and `location` parameters
- `ref`: Cell reference where the hyperlink is located
- `location`: Target position to jump to

### Hyperlink Format

- **Font Color**: Blue (RGB: #0000FF)
- **Underline**: Single underline
- **Jump Target**: A1 cell of the worksheet

### Excluded Worksheets

By default, the following worksheets will not have return links added:
- Directory worksheet itself
- "修订记录" (Revision Record)
- "索引目录" (Index Directory)

## Workflow

1. **Load Excel File**: Load the specified file using openpyxl
2. **Verify Directory Worksheet**: Check if the specified directory worksheet exists
3. **Add Directory Hyperlinks**:
   - Iterate through the specified column of the directory worksheet
   - Create hyperlinks for each non-empty cell
   - Verify if the target worksheet exists
4. **Add Return Links**:
   - Iterate through all worksheets
   - Skip excluded worksheets
   - Add "Return to Directory" link in the specified cell
5. **Save File**: Save the modified Excel file
6. **Output Statistics**: Display the count of successful and failed hyperlinks

## Output Example

```
Hyperlink addition completed!
  Directory worksheet hyperlinks: 95 successful, 2 failed
  Return to directory hyperlinks: 93 successful, 0 failed
```

## Notes

- Files will be modified directly, it is recommended to backup first
- If the target worksheet does not exist, it will be recorded as failed but continue processing other worksheets
- Hyperlinks will overwrite existing content, ensure the target cell can be overwritten
- Worksheet names must match exactly with values in the directory (case-sensitive)

## Resources

### scripts/

**add_hyperlinks.py**: Main hyperlink addition script

**Functions:**
- Read Excel file and get all worksheet names
- Add hyperlinks for table names in the directory worksheet
- Add return directory links in target worksheets
- Count and output processing results

**Dependencies:**
- openpyxl: For Excel file operations

**Execution Method:**
```bash
python scripts/add_hyperlinks.py <file_path> [options]
```
