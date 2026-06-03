---
name: aiguibin-excel-header-replacer
description: 批量修改Excel文件指定工作表的表头内容，支持将表头中的指定文本替换为新文本。不局限于特定Sheet，支持任意匹配规则的批量替换。触发场景包括：用户提到"批量修改Excel表头"、"替换表头文字"、"修改列名"、"Excel表头批量替换"、"把表头的XX改成YY"等需求。即使没有明确说"表头"，只要用户描述的需求是修改多个Excel文件中某个Sheet的列标题文字，就应使用此skill。
---

# Excel 表头批量替换工具

将多个Excel文件中指定工作表的表头内容按规则批量替换。

## 功能特性

- 批量处理文件夹中所有 `.xlsx` 文件
- 支持任意Sheet名称（不局限于"目录"）
- 支持多组查找替换规则
- 默认修改第1行（可配置目标行）
- 自动跳过临时文件（`~$` 开头）
- 锁定文件自动跳过并提示
- 修改后提供验证抽查

## 使用方式

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| 文件夹路径 | 包含目标Excel文件的目录 | `e:\data\设计文档` |
| Sheet名称 | 要修改的工作表名称 | `"目录"` |
| 替换规则 | 旧文本→新文本的映射 | `{"是否分片":"是否分区", "分片键":"分区键"}` |
| 目标行 | 表头所在行（默认第1行） | `1` |

### 执行流程

1. **确认参数**: 向用户确认文件夹路径、Sheet名称、替换规则
2. **抽查预览**: 先读取一个文件确认表头结构
3. **批量执行**: 使用 Python + openpyxl 逐文件处理，保留原有格式
4. **验证结果**: 随机抽查 3-4 个文件验证修改是否正确

## 核心脚本

### 批量替换脚本

使用以下 Python 代码模式执行批量替换，直接在终端中通过 `python -c` 运行：

```python
import glob, os
from openpyxl import load_workbook

base_dir = r'<文件夹路径>'
xlsx_files = glob.glob(os.path.join(base_dir, '*.xlsx'))
xlsx_files = [f for f in xlsx_files if not os.path.basename(f).startswith('~$')]

old_headers = ['<旧文本1>', '<旧文本2>', ...]
new_headers = ['<新文本1>', '<新文本2>', ...]
sheet_name = '<工作表名称>'
target_row = <目标行号>

for f in xlsx_files:
    wb = load_workbook(f)
    if sheet_name not in wb.sheetnames:
        print(f'  SKIP: {os.path.basename(f)}')
        wb.close()
        continue
    ws = wb[sheet_name]
    changed = False
    for col in range(1, ws.max_column + 1):
        cell = ws.cell(row=target_row, column=col)
        if cell.value in old_headers:
            idx = old_headers.index(cell.value)
            cell.value = new_headers[idx]
            changed = True
            print(f'  {os.path.basename(f)}: col {col} -> "{new_headers[idx]}"')
    if changed:
        try:
            wb.save(f)
            print(f'  SAVED: {os.path.basename(f)}')
        except PermissionError:
            print(f'  LOCKED: {os.path.basename(f)} - 文件被占用，请关闭后重试')
    else:
        print(f'  NO CHANGE: {os.path.basename(f)}')
    wb.close()
```

### 验证脚本

修改后使用 MCP Excel 工具抽查 3-4 个随机文件：

```
excel_read_sheet: fileAbsolutePath=<文件路径>, sheetName=<Sheet名称>, range=A1:<最后一列>1
```

## 示例场景

### 场景1: 术语统一替换

用户需求: "把数据库设计文档目录中的'分片'改为'分区'"

替换规则:
```
是否分片 → 是否分区
分片键 → 分区键
初始分片数 → 初始分区数
分片策略(迁移数据量，8-10年增长量) → 分区策略(迁移数据量，8-10年增长量)
```

### 场景2: 字段名规范

用户需求: "把Sheet1表头中的'用户ID'改为'用户编号'，'手机'改为'手机号'"

替换规则:
```
用户ID → 用户编号
手机 → 手机号
```

### 场景3: 中英文统一

用户需求: "把数据表的表头从英文改成中文"

替换规则:
```
ID → 编号
Name → 名称
Status → 状态
CreateTime → 创建时间
```

### 场景4: 第N行表头

用户需求: "第3行是实际表头，把'项目名'改为'工程名称'"

参数配置:
```
target_row = 3
old_headers = ['项目名']
new_headers = ['工程名称']
```

## 注意事项

1. **备份提醒**: 执行前提醒用户备份原始文件
2. **文件占用**: 如果Excel正在被打开，保存会失败，需先关闭文件
3. **精确匹配**: 使用完全匹配模式，不会部分替换（如需模糊匹配，需调整脚本）
4. **临时文件**: 自动跳过 `~$` 开头的Excel临时文件
5. **格式保留**: 使用 openpyxl 确保修改后原有格式完整保留
6. **大小写**: 查找替换区分大小写
7. **不存在Sheet**: 没有指定Sheet的文件自动跳过，不报错

## 依赖

- Python 3.6+
- openpyxl