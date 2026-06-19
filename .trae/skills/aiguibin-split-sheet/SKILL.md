---
name: aiguibin-split-sheet
description: Excel模块化管理工具，支持按模块删除工作表、提取单个模块、拆分多模块文件。适用于数据库设计文档、表清单等包含目录工作表的Excel文件，可按"所属模块"列自动识别并处理相关工作表。
---

# Excel Module-Based Sheet Management

Excel模块化管理工具，支持删除、提取、拆分三种操作模式。

## Quick Start

### 1. 删除指定模块（保留其他模块）

```python
from scripts.aiguibin_split_sheet import delete_sheets_by_module

result = delete_sheets_by_module(
    input_file="database_design.xlsx",
    output_file="cleaned.xlsx",
    keep_modules=["贷后管理", "风险分类"]
)
```

### 2. 提取单个模块到新文件

```python
from scripts.aiguibin_split_sheet import extract_module

result = extract_module(
    input_file="database_design.xlsx",
    module="押品管理",
    output_dir="./output"
)
# 输出: ./output/押品管理.xlsx
```

### 3. 按模块拆分为多个文件

```python
from scripts.aiguibin_split_sheet import split_excel_by_modules

result = split_excel_by_modules(
    input_file="database_design.xlsx",
    output_dir="./output"
)
# 输出多个文件:
#   ./output/贷后管理.xlsx
#   ./output/押品管理.xlsx
#   ./output/风险分类.xlsx
#   ...
```

### 4. 验证拆分结果

```python
from scripts.aiguibin_split_sheet import verify_split_result

result = verify_split_result(
    original_file="database_design.xlsx",
    output_dir="./output"
)

if result["success"]:
    print(f"验证通过！目录行数匹配: {result['catalog_match']}")
else:
    print(f"验证失败！")
    for err in result["errors"]:
        print(f"  错误: {err}")
```

## Core Concepts

### 目录工作表结构

本技能针对包含目录工作表的Excel文件设计：

| 列 | 字段 | 说明 |
|----|------|------|
| A | 序号 | 自动编号 |
| C | 所属模块 | 模块分类标识 |
| E | 表名（英文） | 英文表名，对应工作表名 |
| F | 表名（中文） | 中文表名，对应工作表名 |

### 结构性工作表

以下工作表在拆分/提取时自动保留：

- **修订记录**: 版本变更历史
- **目录**: 表清单目录
- **索引目录**: 索引信息目录

### 四种操作模式

| 模式 | 函数 | 说明 | 原文件 |
|------|------|------|--------|
| 删除 | `delete_sheets_by_module` | 保留指定模块，删除其他 | 不变 |
| 提取 | `extract_module` | 提取单个模块到新文件 | 不变 |
| 拆分 | `split_excel_by_modules` | 按模块拆分为多个文件 | 不变 |
| 验证 | `verify_split_result` | 验证拆分结果完整性 | - |

## Usage Scenarios

### Scenario 1: 清理文件，删除已迁移模块

**场景**: 押品管理模块已独立成文件，需从原文件中删除

```python
from scripts.aiguibin_split_sheet import get_all_modules, delete_sheets_by_module

all_modules = get_all_modules("database_design.xlsx")
keep_modules = [m for m in all_modules if m != "押品管理"]

result = delete_sheets_by_module(
    input_file="database_design.xlsx",
    output_file="database_design_v1.0.1.xlsx",
    keep_modules=keep_modules
)
```

### Scenario 2: 提取单个模块独立文档

**场景**: 将押品管理模块提取为独立的设计文档

```python
from scripts.aiguibin_split_sheet import extract_module

result = extract_module(
    input_file="新信贷_数据库设计报告_贷后管理v1.0.0.xlsx",
    module="押品管理",
    output_dir="./output",
    output_filename="押品管理设计文档.xlsx"
)
```

### Scenario 3: 按模块拆分完整文档

**场景**: 将综合设计文档按业务模块拆分为多个独立文件

```python
from scripts.aiguibin_split_sheet import split_excel_by_modules

result = split_excel_by_modules(
    input_file="综合数据库设计.xlsx",
    output_dir="./modules",
    preserve_original=True,
    renumber_catalog=True
)

print(f"拆分完成，共生成 {result['total_files']} 个文件:")
for file_info in result['files']:
    print(f"  - {file_info['filename']}: {file_info['sheet_count']} 个工作表")
```

### Scenario 4: 预览模式（Dry Run）

**场景**: 在实际操作前预览将要进行的变更

```python
result = split_excel_by_modules(
    input_file="database_design.xlsx",
    output_dir="./output",
    dry_run=True
)

print("预览拆分结果:")
for file_info in result['files']:
    print(f"  {file_info['module']}: {file_info['sheets']}")
```

## Input/Output Specifications

### Input Parameters

#### delete_sheets_by_module

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_file` | str | Yes | - | 输入文件路径 |
| `output_file` | str | Yes | - | 输出文件路径 |
| `keep_modules` | List[str] | Yes | - | 保留的模块列表 |
| `catalog_sheet` | str | No | "目录" | 目录工作表名称 |
| `preserve_sheets` | List[str] | No | ["修订记录", "索引目录"] | 始终保留的工作表 |
| `dry_run` | bool | No | False | 预览模式 |

#### extract_module

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_file` | str | Yes | - | 输入文件路径 |
| `module` | str | Yes | - | 要提取的模块名 |
| `output_dir` | str | No | 同输入目录 | 输出目录 |
| `output_filename` | str | No | `{module}.xlsx` | 输出文件名 |
| `renumber_catalog` | bool | No | True | 是否重新编排目录序号 |

#### split_excel_by_modules

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_file` | str | Yes | - | 输入文件路径 |
| `output_dir` | str | No | 同输入目录 | 输出目录 |
| `modules` | List[str] | No | None (全部模块) | 指定拆分的模块 |
| `preserve_original` | bool | No | True | 保留原文件 |
| `renumber_catalog` | bool | No | True | 重新编排目录序号 |
| `dry_run` | bool | No | False | 预览模式 |

### Output Format

#### delete_sheets_by_module 返回值

```python
{
    "success": bool,
    "input_file": str,
    "output_file": str,
    "total_sheets": int,
    "kept_sheets": int,
    "deleted_sheets": int,
    "kept_rows": int,
    "deleted_rows": int,
    "kept_modules": List[str],
    "deleted_modules": List[str],
    "details": {
        "sheets_deleted": List[str],
        "sheets_not_found": List[str],
        "errors": List[str]
    }
}
```

#### split_excel_by_modules 返回值

```python
{
    "success": bool,
    "input_file": str,
    "output_dir": str,
    "total_files": int,
    "total_sheets_processed": int,
    "preserve_original": bool,
    "files": [
        {
            "module": str,
            "filename": str,
            "filepath": str,
            "sheet_count": int,
            "catalog_rows": int,
            "index_rows": int,
            "data_sheets": List[str]
        }
    ],
    "errors": List[str]
}
```

## Error Handling

### Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| `E001` | 输入文件不存在 | 检查文件路径和扩展名 |
| `E002` | 目录工作表不存在 | 检查工作表名称参数 |
| `E003` | 未找到匹配的模块 | 验证模块名称和列映射 |
| `E004` | 输出目录不可写 | 检查权限和磁盘空间 |
| `E005` | Excel格式无效 | 确保文件是有效的.xlsx/.xlsm |
| `E006` | 模块无对应工作表 | 检查目录表中的表名映射 |

### Troubleshooting

**问题**: 拆分后目录序号不连续

**解决**: 设置 `renumber_catalog=True`（默认开启）

**问题**: 部分模块没有生成文件

**解决**: 使用 `get_all_modules()` 检查模块名称，确认大小写匹配

**问题**: 索引目录未正确过滤

**解决**: 确保索引目录的A列包含英文表名，与目录表E列对应

## Advanced Features

### 自定义列映射

```python
result = extract_module(
    input_file="custom_format.xlsx",
    module="业务模块",
    module_column=4,        # D列为模块
    sheet_name_column=7     # G列为表名
)
```

### 批量处理多个文件

```python
from pathlib import Path
from scripts.aiguibin_split_sheet import split_excel_by_modules

for file in Path("./input").glob("*.xlsx"):
    result = split_excel_by_modules(
        input_file=str(file),
        output_dir=f"./output/{file.stem}"
    )
```

### 过滤特定模块拆分

```python
result = split_excel_by_modules(
    input_file="database_design.xlsx",
    output_dir="./output",
    modules=["贷后管理", "押品管理"]  # 仅拆分这两个模块
)
```

## Best Practices

1. **始终备份原文件** - 所有操作都不会修改原文件，但建议保留备份
2. **使用预览模式** - 首次操作时使用 `dry_run=True` 预览结果
3. **验证输出完整性** - 检查目录行数和工作表数量是否匹配
4. **保留结构性工作表** - 修订记录、目录、索引目录应始终保留
5. **注意模块名称大小写** - 模块名称默认区分大小写
6. **检查空单元格** - 确保目录表的模块列有有效值

## Integration Points

### Excel Processing

使用 `openpyxl` 库进行Excel操作：

- **读取**: `load_workbook()` 加载工作簿
- **复制**: 完整复制单元格样式、列宽、行高
- **写入**: `wb.save()` 保存文件

### File System

标准Python文件I/O操作：

- **验证**: `os.path.exists()`, `os.access()`
- **目录创建**: `os.makedirs()` with `exist_ok=True`
- **路径处理**: 使用 `pathlib.Path` 实现跨平台兼容
