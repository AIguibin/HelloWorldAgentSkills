---
name: "aiguibin-skill-naming"
description: "指导所有新创建的skills都必须以aiguibin开头命名，确保skill命名规范统一。"
---

# Skill命名规范技能

## 功能介绍

该技能定义了skill命名的统一规范，确保所有新创建的skills都以`aiguibin`开头命名，从而保持skill命名的一致性和可识别性。

## 使用场景

当你需要创建新的skill时，该技能可以帮助你：

- 遵循统一的skill命名规范
- 确保所有skill都以`aiguibin`开头
- 保持skill命名的一致性
- 便于管理和识别自定义技能

## 命名规范

### 强制规则

1. **所有新创建的skills必须以`aiguibin`开头命名**
2. **skill名称使用小写字母**
3. **单词之间使用连字符(`-`)分隔**
4. **名称应简洁明了，反映skill的功能**
5. **名称必须包含3个单词，不能多也不能少**

### 示例

✅ **正确的命名**：
- `aiguibin-db-query`
- `aiguibin-frontend-mock`
- `aiguibin-code-review`
- `aiguibin-api-test`

❌ **错误的命名**：
- `db-query` (缺少`aiguibin`前缀)
- `Aiguibin-DB-Query` (使用大写字母)
- `aiguibin_db_query` (使用下划线分隔)
- `aiguibinlongnamethatdoesnotmakeanysense` (名称过长且不清晰)

## 如何创建符合规范的Skill

### 1. 创建Skill目录

```bash
mkdir -p .trae/skills/aiguibin-<skill-name>
```

例如：
```bash
mkdir -p .trae/skills/aiguibin-data-validation
```

### 2. 创建SKILL.md文件

```bash
touch .trae/skills/aiguibin-<skill-name>/SKILL.md
```

### 3. 编写SKILL.md内容

确保文件中的`name`字段也以`aiguibin`开头：

```markdown
---
name: "aiguibin-<skill-name>"
description: "<skill-description>"
---

# <Skill Title>

<Skill Content>
```

## 检查现有Skill命名

### 检查所有Skill命名

```bash
ls -la .trae/skills/ | grep -v "^d"
```

### 筛选不符合规范的Skill

```bash
ls -la .trae/skills/ | grep -v "^d" | grep -v "aiguibin-"
```

## 重命名不符合规范的Skill

### 1. 重命名目录

```bash
mv .trae/skills/<old-skill-name> .trae/skills/aiguibin-<old-skill-name>
```

### 2. 更新SKILL.md中的name字段

```bash
# 使用sed命令更新name字段
sed -i 's/name: "<old-skill-name>"/name: "aiguibin-<old-skill-name>"/' .trae/skills/aiguibin-<old-skill-name>/SKILL.md
```

## 最佳实践

1. **提前规划名称**：在创建skill前，先确定一个简洁明了的名称
2. **遵循命名规范**：始终以`aiguibin`开头，使用小写字母和连字符
3. **反映功能**：名称应清晰反映skill的主要功能
4. **定期检查**：定期检查现有skill的命名，确保符合规范
5. **文档化**：在skill文档中明确说明命名规范

## 工具推荐

- **命名检查工具**：可以使用脚本自动检查skill命名
- **代码审查**：在团队开发中，将skill命名规范纳入代码审查
- **模板化创建**：创建skill模板，确保新skill自动遵循命名规范

## 常见问题

### Q: 为什么要使用统一的命名规范？
A: 统一的命名规范有助于：
   - 提高skill的可识别性
   - 便于管理和组织大量skill
   - 保持项目的一致性
   - 减少命名冲突
   - 便于自动化工具处理

### Q: 现有不符合规范的skill需要修改吗？
A: 建议修改现有不符合规范的skill，以保持命名的一致性。可以逐步进行修改，避免影响现有功能。

### Q: 可以使用其他前缀吗？
A: 不建议使用其他前缀。统一使用`aiguibin`前缀可以确保所有自定义skill都有明确的标识，便于区分和管理。

### Q: 如何处理长名称？
A: 长名称应尽量简洁，只包含必要的关键字。如果名称过长，可以考虑使用缩写或重新组织名称结构。

## 版本历史

- v1.0.0: 初始版本，定义了skill命名规范，要求所有skill以`aiguibin`开头命名
- v1.1.0: 添加了检查和重命名不符合规范skill的方法
- v1.2.0: 完善了最佳实践和常见问题解答