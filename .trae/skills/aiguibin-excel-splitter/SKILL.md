---
name: aiguibin-excel-splitter
description: 按指定列拆分Excel文件为多个独立文件。当用户需要将一个大的Excel文件按照某一列的值拆分成多个小文件时使用此skill。触发场景包括：用户提到"按列拆分Excel"、"把Excel按某列分成多个文件"、"根据某列值拆分表格"、"Excel分组导出"等需求。即使没有明确说"拆分"，只要用户描述的需求是将Excel数据按某列分类并生成多个文件，就应使用此skill。
---

# Excel 文件拆分器

将单个Excel文件按照指定列的值拆分为多个独立的Excel文件。

## 功能特性

- 按任意列的值进行拆分
- 自动保留表头
- 支持大文件处理
- 自动生成安全的文件名
- 输出拆分统计信息

## 使用方式

### 参数说明

调用脚本时需要提供以下参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| input_file | 输入Excel文件的绝对路径 | `e:\data\sales.xlsx` |
| output_dir | 输出目录路径 | `e:\data\拆分结果` |
| split_column | 用于拆分的列名或列索引(从0开始) | `"工程名"` 或 `0` |
| sheet_name | 工作表名称(可选，默认第一个sheet) | `"Sheet1"` |

### 执行流程

1. **确认参数**: 向用户确认输入文件路径、输出目录、拆分列
2. **执行脚本**: 调用 `scripts/split.py` 执行拆分
3. **展示结果**: 显示拆分后的文件列表和统计信息

## 脚本调用

```bash
python <skill-path>/scripts/split.py --input "<input_file>" --output "<output_dir>" --column "<split_column>" [--sheet "<sheet_name>"]
```

### 参数详解

```
--input, -i    输入Excel文件的完整路径
--output, -o   输出目录路径(如不存在会自动创建)
--column, -c   拆分列名或列索引(从0开始)
--sheet, -s    工作表名称(可选，默认使用第一个sheet)
```

## 示例场景

### 场景1: 按工程名拆分

用户需求: "把这个Excel按A列的工程名拆成多个文件"

```bash
python scripts/split.py --input "e:\data\项目信息.xlsx" --output "e:\data\拆分结果" --column "工程名"
```

或使用列索引:

```bash
python scripts/split.py --input "e:\data\项目信息.xlsx" --output "e:\data\拆分结果" --column 0
```

### 场景2: 按部门拆分

用户需求: "根据部门列把员工表拆分，每个部门一个文件"

```bash
python scripts/split.py --input "e:\data\员工表.xlsx" --output "e:\data\按部门拆分" --column "部门"
```

### 场景3: 指定工作表

用户需求: "Sheet2里有销售数据，按地区列拆分"

```bash
python scripts/split.py --input "e:\data\销售数据.xlsx" --output "e:\data\按地区拆分" --column "地区" --sheet "Sheet2"
```

## 输出格式

脚本执行后会输出:

```
读取文件: <input_file>
工作表: <sheet_name>
总行数: <total_rows>
拆分列: <column_name>

拆分结果:
  - <value1>.xlsx (<count1> 行)
  - <value2>.xlsx (<count2> 行)
  ...

拆分完成! 共生成 <n> 个文件
输出目录: <output_dir>
```

## 注意事项

1. **文件名安全处理**: 列值中的特殊字符(`/ \ : * ? " < > |`)会被替换为下划线
2. **空值处理**: 空值行会被跳过，不会生成文件
3. **编码支持**: 支持中文文件名和内容
4. **大文件**: 使用pandas流式处理，支持大文件拆分

## 依赖

- Python 3.6+
- pandas
- openpyxl
