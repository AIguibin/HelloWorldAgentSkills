---
name: aiguibin-create-excel
description: >
  通过 openpyxl 创建带格式的 Excel (.xlsx) 文件。支持合并单元格、自定义背景色、
  字体样式（大小/加粗/颜色）、边框线、批量行格式等。Use when users need to create
  formatted Excel files with specific styling requirements including merged cells,
  colored backgrounds, custom fonts, borders, and batch row formatting.
  Trigger phrases: "创建Excel", "生成Excel", "create excel", "格式化Excel",
  "生成带格式的表格", "创建.xlsx文件", "create formatted spreadsheet".
---

# Excel 格式化创建

基于 openpyxl 库，通过 JSON 配置文件驱动，生成带格式的 Excel 文件。

## 工作流程

1. 根据用户的格式需求，生成 JSON 配置文件
2. 执行 `scripts/create_excel.py` 脚本生成 Excel 文件
3. 向用户确认输出文件路径和内容

## JSON 配置文件结构

配置文件是描述 Excel 格式的核心。详见 [config_schema.md](references/config_schema.md)。

### 快速模板

创建一个带标题行和表头的标准表格：

```json
{
  "sheet_name": "Sheet1",
  "col_count": 10,
  "row_range": 100,
  "font_name": "微软雅黑",
  "border_color": "90EE90",
  "column_width": 12,
  "output_path": "output.xlsx",
  "rows": [],
  "default_rows": []
}
```

### rows 配置详解

`rows` 数组中每个元素定义**一行**的格式，支持的配置项：

| 字段 | 说明 |
|------|------|
| row | 行号（必填） |
| bg_color | 背景色，如 "7030A0"（紫色）、"00B050"（绿色） |
| font.size | 字体大小 |
| font.bold | 是否加粗 |
| font.color | 字体颜色，如 "FFFFFF"（白色） |
| align | 水平对齐：center/left/right |
| merge | 合并单元格：{"start_col": "A", "end_col": "J"} |
| cells | 单元格值：[{"col": 1, "value": "序号"}] |

### default_rows 配置详解

`default_rows` 对连续行区域批量设置格式：

```json
{
  "default_rows": [
    { "start": 3, "end": 100, "font": { "size": 10 } }
  ]
}
```

## 执行脚本

生成 JSON 配置文件后，执行：

```bash
python scripts/create_excel.py <config.json> [output_path]
```

- 输出路径可选，未指定时使用配置文件中的 `output_path` 字段

## 预设字体回退

默认字体为"微软雅黑"。若系统不可用，按优先级回退：

1. 微软雅黑
2. 思源黑体
3. WPS灵秀黑
4. 新宋体

## 格式规范

### 颜色值

颜色使用 6 位十六进制字符串（不带 `#`）：

| 颜色 | 色值 |
|------|------|
| 紫色 | 7030A0 |
| 纯绿 | 00B050 |
| 浅绿 | 90EE90 |
| 白色 | FFFFFF |
| 黑色 | 000000 |
| 红色 | FF0000 |
| 蓝色 | 0000FF |
| 黄色 | FFFF00 |

### 边框

默认使用浅绿色(`90EE90`)细线边框，可通过 `border_color` 自定义。

## 错误处理

- 配置文件不存在时，脚本返回错误码 1 并输出错误信息
- JSON 格式错误时，由 Python json 模块抛出异常并显示错误位置
- 输出目录不存在时自动创建
- 字体不可用时，openpyxl 保留字体名称，由 Excel 应用程序自行回退