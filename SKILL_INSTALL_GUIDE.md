# Skill安装和使用指南

## 📦 Skill文件信息

- **Skill名称**: aiguibin-excel-merge-optimizer
- **文件名**: aiguibin-excel-merge-optimizer.skill
- **文件大小**: 9.4 KB
- **创建时间**: 2024-04-22

## 🚀 安装方法

### 方法1：直接安装（推荐）

将 `.skill` 文件复制到Claude Code的skills目录：

```bash
# Windows
copy aiguibin-excel-merge-optimizer.skill %USERPROFILE%\.claude\skills\

# Linux/Mac
cp aiguibin-excel-merge-optimizer.skill ~/.claude/skills/
```

### 方法2：解压安装

如果需要查看或修改skill内容，可以解压 `.skill` 文件：

```bash
# .skill文件实际上是zip格式的压缩包
unzip aiguibin-excel-merge-optimizer.skill -d aiguibin-excel-merge-optimizer

# 然后复制到skills目录
cp -r aiguibin-excel-merge-optimizer ~/.claude/skills/
```

## 📖 使用方法

安装完成后，在Claude Code中直接描述你的需求，skill会自动触发：

### 示例1：基本用法

```
请将'e:\WorkSpace\数据库设计文档'文件夹下的所有Excel文件的'目录'工作表合并成一个文件
```

### 示例2：指定参数

```
合并'/data/departments'文件夹下的所有Excel文件，每个文件都有'数据汇总'工作表，
合并后删除空白行和重复标题，输出文件命名为'全公司数据汇总.xlsx'
```

### 示例3：批量处理

```
我有一个文件夹包含多个部门的Excel数据表，每个文件都有'数据汇总'工作表。
请将这些工作表合并成一个文件，并清理格式问题。
```

## ✨ 功能特性

- ✅ 自动合并多个Excel文件的指定工作表
- ✅ 完整保留原数据格式（字体、颜色、边框、对齐方式等）
- ✅ 自动删除空白行
- ✅ 自动删除重复标题行
- ✅ 支持自然排序
- ✅ 生成详细的处理报告

## 🔧 核心脚本

Skill包含两个核心Python脚本：

1. **merge_excel.py**: 合并多个Excel文件
2. **optimize_excel.py**: 优化Excel格式

这两个脚本也可以独立使用：

```bash
# 合并Excel文件
python scripts/merge_excel.py --folder "源文件夹" --sheet "工作表名" --output "输出文件"

# 优化Excel格式
python scripts/optimize_excel.py --file "Excel文件"
```

## 📋 依赖要求

- Python 3.6+
- openpyxl库

安装依赖：

```bash
pip install openpyxl
```

## 🎯 触发关键词

Skill会在以下情况下自动触发：

- 用户提到"合并Excel文件"
- 用户提到"合并多个Excel"
- 用户提到"Excel工作表合并"
- 用户提到"批量合并Excel"
- 用户提到"Excel文件整合"
- 用户描述需要将多个Excel文件的数据整合到一个文件中

## 📊 输出报告

处理完成后会生成详细报告，包括：

- 处理的文件列表
- 每个文件的数据行数
- 删除的空白行数量
- 删除的重复标题行数量
- 最终文件的总行数
- 数据预览（前5行和最后5行）

## ⚠️ 注意事项

1. **备份原文件**：处理前建议备份原始Excel文件
2. **文件权限**：确保有读写权限
3. **内存占用**：大文件处理可能占用较多内存
4. **处理时间**：大量文件合并可能需要较长时间
5. **格式兼容性**：确保所有源文件使用相同的Excel版本格式

## 🐛 常见问题

### Q1: Skill没有自动触发？

确保：
- Skill文件已正确安装到 `~/.claude/skills/` 目录
- 描述中包含触发关键词
- 重启Claude Code

### Q2: 格式丢失了？

确保：
- 使用openpyxl库而不是pandas
- 源文件格式正确
- 没有使用特殊格式（如条件格式）

### Q3: 处理速度慢？

可以尝试：
- 分批处理文件
- 减少文件数量
- 使用更快的存储设备

## 📝 版本信息

- **版本**: v1.0.0
- **作者**: aiguibin
- **许可**: MIT License

## 🤝 反馈与支持

如有问题或建议，请：
1. 查看README.md文档
2. 检查evals/evals.json中的测试用例
3. 提交Issue或Pull Request

---

**享受使用Excel文件合并与格式优化工具！** 🎉
