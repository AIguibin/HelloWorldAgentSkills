# Excel 格式配置 JSON Schema

通过 JSON 配置文件定义 Excel 的格式布局，支持灵活的格式定制。

## 顶层结构

```json
{
  "sheet_name": "Sheet1",
  "col_count": 10,
  "row_range": 100,
  "font_name": "微软雅黑",
  "border_color": "90EE90",
  "column_width": 12,
  "vertical_align": "center",
  "output_path": "output.xlsx",
  "rows": [],
  "default_rows": []
}
```

## rows 配置

`rows` 数组中的每个元素定义一行或多行的格式：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| row | int | 是 | 行号（从 1 开始） |
| start_col | int | 否 | 起始列，默认 1 |
| end_col | int | 否 | 结束列，默认等于 col_count |
| bg_color | string | 否 | 背景色，如 "7030A0"、"00B050" |
| font | object | 否 | 字体配置 |
| font.name | string | 否 | 字体名称 |
| font.size | int | 否 | 字体大小 |
| font.bold | bool | 否 | 是否加粗 |
| font.color | string | 否 | 字体颜色，如 "FFFFFF" |
| align | string | 否 | 水平对齐：left/center/right |
| merge | object | 否 | 合并单元格配置 |
| merge.start_col | int/string | 否 | 合并起始列 |
| merge.end_col | int/string | 否 | 合并结束列 |
| cells | array | 否 | 指定列的值，如 [{"col": 1, "value": "序号"}] |

## default_rows 配置

`default_rows` 数组中的元素应用批量默认格式：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start | int | 是 | 起始行号 |
| end | int | 是 | 结束行号 |
| font | object | 否 | 字体配置 |

## 完整示例

```json
{
  "sheet_name": "数据报表",
  "col_count": 10,
  "row_range": 100,
  "font_name": "微软雅黑",
  "border_color": "90EE90",
  "column_width": 12,
  "output_path": "formatted_excel.xlsx",
  "rows": [
    {
      "row": 1,
      "bg_color": "7030A0",
      "font": { "size": 16, "bold": true, "color": "FFFFFF" },
      "align": "center",
      "merge": { "start_col": "A", "end_col": "J" }
    },
    {
      "row": 2,
      "bg_color": "00B050",
      "font": { "size": 12, "bold": true, "color": "FFFFFF" },
      "cells": [
        { "col": 1, "value": "序号" },
        { "col": 10, "value": "备注" }
      ]
    }
  ],
  "default_rows": [
    {
      "start": 3,
      "end": 100,
      "font": { "size": 10 }
    }
  ]
}
```