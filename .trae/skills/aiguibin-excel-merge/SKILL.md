---
name: aiguibin-excel-merge
description: Excel工作表合并工具，支持从指定目录下的所有Excel文件中提取并合并多个工作表内容。适用于数据库设计文档、表清单等需要汇总多个Excel文件内容的场景。
---

# Excel Sheet Merge Tool

Excel工作表合并工具，支持从指定目录下的所有Excel文件中提取并合并多个工作表内容。

## Quick Start

### 基本用法

```python
from scripts.aiguibin_excel_merge import merge_sheets_from_directory

result = merge_sheets_from_directory(
    target_directory="./draft",
    sheet_names=["修订记录", "目录", "索引目录"],
    output_file="./output/merged.xlsx"
)
```

### 命令行使用

```bash
# 合并指定目录下的修订记录、目录、索引目录工作表
python aiguibin_excel_merge.py ./draft --sheets 修订记录 目录 索引目录 --output ./output/merged.xlsx

# 仅合并目录工作表
python aiguibin_excel_merge.py ./draft --sheets 目录 --output ./output/catalog.xlsx
```

## Core Concepts

### 输入参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `target_directory` | str | 是 | - | 目标目录路径，包含要合并的Excel文件 |
| `sheet_names` | List[str] | 是 | - | 要合并的工作表名称列表 |
| `output_file` | str | 否 | 自动生成 | 输出文件路径 |
| `skip_empty` | bool | 否 | True | 是否跳过空工作表 |

### 功能特性

1. **多工作表支持**: 支持同时合并多个工作表
2. **自动检测**: 自动检测目录下所有.xlsx文件
3. **表头处理**: 从第一个文件提取表头，后续文件数据直接追加
4. **错误处理**: 跳过不存在的工作表，记录处理日志
5. **结果报告**: 返回详细的执行状态和统计信息

### 输出格式

每个工作表名称对应一个独立的工作表，包含：
- 第一行：表头（从第一个文件提取）
- 后续行：所有文件的数据合并

## Usage Scenarios

### Scenario 1: 合并数据库设计文档

```python
from scripts.aiguibin_excel_merge import merge_sheets_from_directory

result = merge_sheets_from_directory(
    target_directory="./database_docs",
    sheet_names=["修订记录", "目录", "索引目录"],
    output_file="./output/数据库设计汇总.xlsx"
)

if result["success"]:
    print(f"合并完成！")
    for sheet, count in result["sheet_counts"].items():
        print(f"  {sheet}: {count} 行")
```

### Scenario 2: 仅合并目录工作表

```python
result = merge_sheets_from_directory(
    target_directory="./draft",
    sheet_names=["目录"],
    output_file="./output/catalog_merged.xlsx"
)
```

### Scenario 3: 自定义工作表合并

```python
result = merge_sheets_from_directory(
    target_directory="./reports",
    sheet_names=["汇总表", "明细表", "统计表"],
    output_file="./output/reports_combined.xlsx"
)
```

## Input/Output Specifications

### Input Parameters

#### merge_sheets_from_directory

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target_directory` | str | Yes | - | Directory containing Excel files |
| `sheet_names` | List[str] | Yes | - | List of sheet names to merge |
| `output_file` | str | No | Auto-generated | Output file path |
| `skip_empty` | bool | No | True | Skip empty sheets |

### Output Format

#### merge_sheets_from_directory 返回值

```python
{
    "success": bool,
    "output_file": str,
    "files_processed": int,
    "sheet_counts": {
        "修订记录": int,
        "目录": int,
        "索引目录": int
    },
    "details": [
        {
            "filename": str,
            "sheets_found": List[str],
            "sheets_missing": List[str],
            "row_counts": Dict[str, int]
        }
    ],
    "errors": List[str]
}
```

## Error Handling

### Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| `E001` | 目录不存在 | 检查目录路径 |
| `E002` | 目录中无Excel文件 | 确保目录包含.xlsx文件 |
| `E003` | 工作表不存在 | 检查工作表名称，使用skip_empty=True跳过 |
| `E004` | 输出目录不可写 | 检查权限和磁盘空间 |
| `E005` | Excel格式无效 | 确保文件是有效的.xlsx/.xlsm |

### Troubleshooting

**问题**: 某些文件的工作表被跳过

**解决**: 检查返回结果中的 `details` 数组，查看 `sheets_missing` 字段

**问题**: 合并后数据行数不正确

**解决**: 确认所有文件的表头结构一致，检查是否有空行

**问题**: 输出文件无法打开

**解决**: 确保输出目录存在且有写入权限

## Best Practices

1. **统一表头格式** - 确保所有文件的相同工作表具有一致的表头结构
2. **检查数据完整性** - 合并后验证总行数是否符合预期
3. **使用绝对路径** - 推荐使用绝对路径避免路径解析问题
4. **备份原文件** - 合并操作不会修改原文件，但建议保留备份

## Integration Points

### Excel Processing

使用 `openpyxl` 库进行Excel操作：

- **读取**: `load_workbook()` 加载工作簿
- **写入**: `Workbook()` 创建新工作簿
- **合并**: 逐行复制数据到新工作表

### File System

标准Python文件I/O操作：

- **遍历**: `os.listdir()` 获取文件列表
- **验证**: `os.path.exists()` 检查路径存在
- **创建**: `os.makedirs()` 创建输出目录
