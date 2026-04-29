# AI自动化编程 Skill - aiguibin-platform-auto

基于《AI编程技能规范文档V4.0_整合版》的AI自动化编程Skill，与项目解耦，开箱即用。

## 快速开始

### 1. 复制Skill到项目

```bash
# 方式1：直接复制
cp -r aiguibin-platform-auto/ /path/to/your/project/.trae/skills/aiguibin-platform-auto/

# 方式2：Git子模块（推荐）
git submodule add https://github.com/your-org/aiguibin-platform-auto.git .trae/skills/aiguibin-platform-auto
```

### 2. 配置Skill

编辑 `skill_config.yaml` 文件，配置项目信息：

```yaml
project:
  name: "你的项目名称"
  description: "项目描述"
  version: "1.0.0"

tech_stack:
  backend: "Spring Boot 3.2.5 + MyBatis-Plus + MySQL 8.0 + Java 17"
  frontend: "Vue3 + Element Plus"
  build_tool: "Maven"
```

### 3. 输入需求

在 `00_input_documents/` 目录下创建需求文件：

```
00_input_documents/
├── 01-需求规格说明书/
├── 02-架构设计文档/
├── 04-详细设计文档/
├── 05-数据库设计文档/
└── 06-示例代码文件/
```

### 4. 启动执行

```bash
cd .trae/skills/aiguibin-platform-auto/
python ai_auto_dev.py --stage 0
```

### 5. 处理人工复核节点

当AI到达人工复核节点时，会发送通知。执行确认命令：

```bash
python ai_auto_dev.py --confirm T0050 --pass
```

## 文件夹结构

```
aiguibin-platform-auto/
├── 00_input_documents/          # 输入文档目录
├── 00_stage0_output/            # 阶段0输出
├── 01_requirement_output/       # 需求分析与定版输出
├── 02_design_output/            # 架构设计输出
├── 03_exec_plans/               # 执行计划
├── 04_code_output/              # 代码输出
├── 05_test_reports/             # 测试报告
├── 06_delivery/                 # 交付物
├── 07_logs/                     # 执行日志
├── 08_state_backup/             # 状态备份
├── 09_knowledge_base/           # 知识库
├── examples/                    # 示例代码
│   ├── pom.xml                  # Maven配置示例
│   ├── PlatformApplication.java # 启动类示例
│   ├── application.yml          # 主配置示例
│   └── application-dev.yml      # 开发环境配置示例
├── templates/                   # 模板文件
│   ├── all_stages_exec_plan.md  # 完整执行计划
│   ├── prompt_library.md        # Prompt模板库
│   ├── skill_config_template.yaml # 配置模板
│   └── stage0_exec_plan_template.md # 阶段0执行计划
├── exec_index.yaml              # 执行索引文件
├── skill_config.yaml            # Skill配置
├── SKILL.md                     # Skill主文档
└── README.md                    # 本文件
```

## 执行流程

```
阶段0: 文档理解与意图分析 → 阶段1: 需求输入 → 阶段2: 需求分析与定版
→ 阶段3: 架构设计与定版 → 阶段4: 原子执行计划拆分 → 阶段5: 索引文件生成
→ 阶段6: AI自动化执行 → 阶段7: 全流程交付物终审 → 阶段8: 文档归档与沉淀
```

## 配套文档

- [SKILL.md](SKILL.md) - Skill主文档，包含完整8个阶段的详细说明
- [templates/all_stages_exec_plan.md](templates/all_stages_exec_plan.md) - 完整执行计划
- [templates/prompt_library.md](templates/prompt_library.md) - Prompt模板库
- 《AI自动化编程全流程执行规范V4.0》 - 执行规范
- 《AI自动化编程环境准备指南》 - 环境准备
- 《AI编程技能规范文档V4.0_整合版》 - 理论基础

## 技术栈

- **后端**: Spring Boot 3.2.5 + MyBatis-Plus 3.5.6 + MySQL 8.0 + Java 17
- **前端**: Vue3 + Element Plus
- **构建工具**: Maven
- **数据库连接池**: Druid
- **API文档**: Knife4j
- **工具库**: Hutool

## 版本信息

- Skill版本：V1.0.0
- 适配规范：V4.0_整合版
- 最后更新：2025年2月
