# Excel文件合并与格式优化工具

## 简介

这是一个用于合并多个Excel文件指定工作表并优化格式的Claude Code skill。

## 功能特性

- ✅ 合并多个Excel文件的指定工作表
- ✅ 完整保留原数据格式（字体、颜色、边框、对齐方式等）
- ✅ 自动删除空白行
- ✅ 自动删除重复标题行
- ✅ 支持自然排序
- ✅ 详细的处理报告

## 安装方法

### 方法1：使用.skill文件安装

```bash
# 将.skill文件放置到Claude Code的skills目录
cp aiguibin-excel-merge-optimizer.skill ~/.claude/skills/
```

### 方法2：从源码安装

```bash
# 克隆或下载skill目录
git clone <repository-url>
cd aiguibin-excel-merge-optimizer

# 复制到Claude Code的skills目录
cp -r . ~/.claude/skills/aiguibin-excel-merge-optimizer
```

## 使用方法

### 基本用法

在Claude Code中，直接描述你的需求，skill会自动触发：

```
请将'e:\WorkSpace\数据库设计文档'文件夹下的所有Excel文件的'目录'工作表合并成一个文件
```

### 高级用法

你也可以明确指定参数：

```
合并'/data/departments'文件夹下的所有Excel文件，每个文件都有'数据汇总'工作表，
合并后删除空白行和重复标题，输出文件命名为'全公司数据汇总.xlsx'
```

## 核心脚本

### merge_excel.py

合并多个Excel文件的指定工作表：

```bash
python scripts/merge_excel.py \
  --folder "源文件夹路径" \
  --sheet "工作表名称" \
  --output "输出文件路径"
```

### optimize_excel.py

优化Excel文件格式：

```bash
python scripts/optimize_excel.py --file "Excel文件路径"
```

## 依赖要求

- Python 3.6+
- openpyxl库

安装依赖：

```bash
pip install openpyxl
```

## 示例

### 示例1：合并数据库设计文档

```bash
# 合并所有数据库设计文档的目录表
python scripts/merge_excel.py \
  --folder "e:\WorkSpace\数据库设计文档" \
  --sheet "目录" \
  --output "e:\WorkSpace\数据库设计文档\全量数据库设计v1.0.0.xlsx"

# 优化合并后的文件
python scripts/optimize_excel.py \
  --file "e:\WorkSpace\数据库设计文档\全量数据库设计v1.0.0.xlsx"
```

### 示例2：合并多个部门的数据表

```bash
# 合并多个部门的数据表
python scripts/merge_excel.py \
  --folder "/data/departments" \
  --sheet "数据汇总" \
  --output "/data/merged/全公司数据汇总.xlsx"

# 优化格式
python scripts/optimize_excel.py \
  --file "/data/merged/全公司数据汇总.xlsx"
```

## 输出报告

处理完成后会生成详细报告，包括：

- 处理的文件列表
- 每个文件的数据行数
- 删除的空白行数量
- 删除的重复标题行数量
- 最终文件的总行数
- 数据预览（前5行和最后5行）

## 注意事项

1. **备份原文件**：处理前建议备份原始Excel文件
2. **文件权限**：确保有读写权限
3. **内存占用**：大文件处理可能占用较多内存
4. **处理时间**：大量文件合并可能需要较长时间
5. **格式兼容性**：确保所有源文件使用相同的Excel版本格式

## 常见问题

### Q1: 为什么有些格式丢失了？
A: 确保使用openpyxl库而不是pandas，pandas会丢失大部分格式信息。

### Q2: 如何处理不同列数的Excel文件？
A: 脚本会自动适应不同的列数，但建议源文件保持相同的列结构。

### Q3: 合并后的文件太大怎么办？
A: 可以考虑：
- 分批处理文件
- 删除不必要的工作表
- 使用Excel的压缩功能

## 版本历史

- v1.0.0 (2024-01-XX)
  - 初始版本
  - 支持Excel文件合并
  - 支持格式优化
  - 支持空白行和重复标题删除

## 许可证

MIT License

## 作者

aiguibin

## 贡献

欢迎提交Issue和Pull Request！
