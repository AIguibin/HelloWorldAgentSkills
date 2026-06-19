---
name: aiguibin-excel-lookup
description: Batch Excel data synchronization tool for matching and updating source table data to target Excel files. Supports custom field mapping, batch processing, exception handling and detailed logging. Suitable for database design documents, table lists and other Excel file automation scenarios.
---

# Excel Batch Data Synchronization

## Quick Start

Execute batch data synchronization:

```bash
python scripts/sync_excel_data.py
```

## Core Features

- **Data Matching**: Case-insensitive matching based on table name (English)
- **Field Mapping**: Support custom source column to target column mapping
- **Batch Processing**: Automatically process all Excel files in specified directory
- **Smart Update**: Only update empty target cells, preserve existing data
- **Exception Handling**: Comprehensive error handling with openpyxl and pandas dual engine
- **Logging**: Detailed processing logs to file and terminal

## Configuration Parameters

Modify the following configuration at the beginning of the script:

```python
SOURCE_FILE = r'source_file_path.xlsx'        # Source data file path
SOURCE_SHEET = 'TableInfoV1.0'            # Source data sheet name
TARGET_DIR = r'target_file_directory'          # Target file directory
TARGET_SHEET = 'Directory'                     # Target sheet name

COLUMN_MAPPING = {                                # Field mapping relationship
    'target_C': 'source_C',                      # Target column C <- Source column C
    'target_M': 'source_F',                      # Target column M <- Source column F
    'target_I': 'source_G',                      # Target column I <- Source column G
    'target_L': 'source_H',                      # Target column L <- Source column H
    'target_K': 'source_I'                       # Target column K <- Source column I
}
```

## Data Matching Rules

Matching key: Target column E (Table Name English) uppercase == Source column D (Table Name English) uppercase

Update strategy: Only update when target column is empty, preserve existing data

## Processing Workflow

1. Load source data file, read "TableInfoV1.0" sheet
2. Build table name -> data mapping dictionary (1149 records)
3. Iterate through all .xlsx files in target directory
4. For each target file:
   - Check if "Directory" sheet exists
   - Read data row by row, extract column E table name
   - Find match in source dictionary after uppercase conversion
   - If matched, update corresponding columns (C, M, I, L, K)
5. Save updated file
6. Output processing statistics and logs

## Field Mapping Details

| Target Column | Source Column | Field Name | Description |
|--------------|--------------|-------------|-------------|
| C | C | Module | Functional module the table belongs to |
| M | F | Standard Compliant | Whether it meets standards |
| I | G | Online Initialization | Whether initialization is needed |
| L | H | Sync Query Library | Whether to sync to query library |
| K | I | Migration | Whether migration is needed |

## Exception Handling

The script includes multi-level exception handling:

1. **File-level exceptions**
   - File not found -> Skip processing, log warning
   - Sheet not found -> Skip processing, log warning
   - openpyxl read failure -> Automatically switch to pandas engine

2. **Row-level exceptions**
   - Index out of range -> Log warning, continue processing next row
   - Data type error -> Log warning, continue processing next row

3. **Save exceptions**
   - Save failure -> Log error, do not interrupt overall process

## Log Output

Logs include the following information:

- Processing start/end timestamps
- Progress of each file
- Match count and update count statistics
- Error and warning details
- Final summary statistics

Log file: `excel_sync.log`

## Usage Scenarios

### Scenario 1: Database Design Document Synchronization

Synchronize module, standard compliance status and other information from the full table list to the Directory sheet of each database design document.

### Scenario 2: Table List Batch Update

Extract field information from the standard table list and batch update to multiple design documents.

### Scenario 3: Data Consistency Maintenance

Regularly execute synchronization to ensure table information in each document remains consistent with the latest standards.

## Important Notes

1. The script directly modifies target files, it is recommended to backup first
2. Only update empty cells, existing data will not be overwritten
3. Matching is based on English table name, ensure table name spelling is correct
4. Processing large files may take a long time, please wait patiently
5. The log file records all processing details for troubleshooting

## Advanced Features

### Custom Field Mapping

If you need to modify field mapping relationships, edit the `COLUMN_MAPPING` dictionary:

```python
COLUMN_MAPPING = {
    'target_C': 'source_C',      # Target column: Source column
    'target_M': 'source_F',
    # Add more mappings...
}
```

### Processing Specific Files

If you need to process specific files instead of the entire directory, modify the file acquisition logic in the `main()` function.

## Troubleshooting

### Issue: File Read Failure

**Solution**: Check if file path is correct, confirm file is not occupied by other programs

### Issue: Match Count is 0

**Solution**: Check if table names in source and target files are consistent (case, spelling)

### Issue: openpyxl Index Error

**Solution**: The script will automatically switch to pandas engine, if there are still issues check file format

### Issue: Data Not Saved After Update

**Solution**: Check file permissions, confirm sufficient disk space

### Issue: Unified Authentication Library File Processing

**Note**: The file `新信贷_数据库设计报告_统一认证库v1.0.0.xlsx` has a special format that may cause openpyxl index errors.

**Solution**: The script automatically switches to pandas engine when openpyxl fails. For this specific file, use the dedicated fix script:

```bash
python scripts/fix_unified_auth.py
```

This script manually updates the unified authentication library file with the correct data:
- Column C (Module): Set to "统一认证中心"
- Column M (Standard Compliant): Set to "Y"
- Column L (Sync Query Library): Clear (empty)
- Column K (Migration): Clear (empty)
