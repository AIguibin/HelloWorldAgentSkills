---
name: aiguibin-insert-columns
description: Excel通用插入列工具，支持在指定工作表的特定列后插入新列，自动继承相邻列格式。适用于需要批量添加新字段的数据库设计文档、表清单等Excel文件。
---

# Excel Insert Columns Tool

Excel通用插入列工具，支持在指定工作表的特定列后插入新列，并自动继承相邻列格式。

## Quick Start

### 基本用法

```python
from scripts.aiguibin_insert_columns import insert_columns_after

result = insert_columns_after(
    file_path="database_design.xlsx",
    sheet_name="目录",
    after_column="H",
    headers=["初始分片数", "分片策略"]
)
```

### 批量处理多个文件

```python
from scripts.aiguibin_insert_columns import batch_insert_columns
import os

files = [f for f in os.listdir("./draft") if f.endswith('.xlsx')]

result = batch_insert_columns(
    file_paths=[os.path.join("./draft", f) for f in files],
    sheet_name="目录",
    after_column="H",
    headers=["初始分片数", "分片策略"]
)
```

## Core Concepts

### 输入参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `file_path` | str | 是 | - | Excel文件路径 |
| `sheet_name` | str | 是 | - | 目标工作表名称 |
| `after_column` | str | 是 | - | 基准列位置（在该列后插入） |
| `headers` | List[str] | 是 | - | 新列的表头文本列表 |
| `copy_format_from` | str | 否 | "left" | 格式来源列（"left"或"right"） |

### 功能特性

1. **智能格式继承**: 自动检测并复制相邻列的格式
2. **批量插入**: 支持一次插入多列
3. **批量处理**: 支持处理多个文件
4. **错误处理**: 完善的参数验证和错误提示

### 格式继承规则

新插入的列会自动继承以下格式属性：

- 字体样式（字体名称、大小、颜色、粗体、斜体）
- 单元格背景色
- 对齐方式（水平、垂直）
- 边框样式
- 数字格式

## Usage Scenarios

### Scenario 1: 单文件单列插入

```python
from scripts.aiguibin_insert_columns import insert_columns_after

result = insert_columns_after(
    file_path="report.xlsx",
    sheet_name="目录",
    after_column="H",
    headers=["备注"]
)

if result["success"]:
    print(f"成功插入 {result['columns_inserted']} 列")
else:
    print(f"失败: {result['errors']}")
```

### Scenario 2: 单文件多列插入

```python
from scripts.aiguibin_insert_columns import insert_columns_after

result = insert_columns_after(
    file_path="database_design.xlsx",
    sheet_name="目录",
    after_column="H",
    headers=["初始分片数", "分片策略(迁移数据量，8-10年增长量)"]
)
```

### Scenario 3: 批量处理目录下所有文件

```python
from scripts.aiguibin_insert_columns import batch_insert_columns
import os

draft_dir = "./draft"
files = [os.path.join(draft_dir, f) for f in os.listdir(draft_dir) if f.endswith('.xlsx')]

result = batch_insert_columns(
    file_paths=files,
    sheet_name="目录",
    after_column="H",
    headers=["初始分片数", "分片策略"]
)

print(f"处理文件: {result['total_files']}")
print(f"成功: {result['successful']}")
print(f"失败: {result['failed']}")
```

### Scenario 4: 从右侧列复制格式

```python
result = insert_columns_after(
    file_path="report.xlsx",
    sheet_name="目录",
    after_column="H",
    headers=["新字段"],
    copy_format_from="right"  # 从右侧列复制格式
)
```

## Input/Output Specifications

### Input Parameters

#### insert_columns_after

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | str | Yes | - | Path to Excel file |
| `sheet_name` | str | Yes | - | Target sheet name |
| `after_column` | str | Yes | - | Column letter to insert after (e.g., "H") |
| `headers` | List[str] | Yes | - | List of header texts for new columns |
| `copy_format_from` | str | No | "left" | Format source: "left" or "right" |

#### batch_insert_columns

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_paths` | List[str] | Yes | - | List of Excel file paths |
| `sheet_name` | str | Yes | - | Target sheet name |
| `after_column` | str | Yes | - | Column letter to insert after |
| `headers` | List[str] | Yes | - | List of header texts |
| `copy_format_from` | str | No | "left" | Format source |

### Output Format

#### insert_columns_after 返回值

```python
{
    "success": bool,
    "file_path": str,
    "sheet_name": str,
    "after_column": str,
    "columns_inserted": int,
    "headers": List[str],
    "new_column_letters": List[str],  # e.g., ["I", "J"]
    "errors": List[str]
}
```

#### batch_insert_columns 返回值

```python
{
    "success": bool,
    "total_files": int,
    "successful": int,
    "failed": int,
    "results": [
        {
            "file_path": str,
            "success": bool,
            "columns_inserted": int,
            "errors": List[str]
        }
    ],
    "errors": List[str]
}
```

## Error Handling

### Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| `E001` | 文件不存在 | 检查文件路径 |
| `E002` | 工作表不存在 | 检查工作表名称 |
| `E003` | 列位置无效 | 使用有效的列字母（如A-Z, AA-AZ等） |
| `E004` | 表头文本为空 | 提供非空表头文本列表 |
| `E005` | Excel格式无效 | 确保文件是有效的.xlsx/.xlsm |
| `E006` | 格式复制失败 | 检查相邻列是否有有效格式 |

### Troubleshooting

**问题**: 列位置无效

**解决**: 使用大写字母表示列位置，如 "A", "B", "H", "AA" 等

**问题**: 格式不一致

**解决**: 检查 `copy_format_from` 参数，确保从正确的列复制格式

**问题**: 部分文件处理失败

**解决**: 查看 `results` 数组中每个文件的错误信息

## Best Practices

1. **备份原文件** - 操作前建议备份
2. **验证参数** - 确保工作表名称和列位置正确
3. **批量处理** - 使用 `batch_insert_columns` 处理多个文件
4. **格式检查** - 操作后验证格式是否正确应用

## Integration Points

### Excel Processing

使用 `openpyxl` 库进行Excel操作：

- **读取**: `load_workbook()` 加载工作簿
- **插入**: `ws.insert_cols()` 插入列
- **格式复制**: 完整复制单元格样式

### File System

标准Python文件I/O操作：

- **验证**: `os.path.exists()` 检查文件存在
- **批量处理**: 遍历目录处理多个文件
