# AI自动化编程 Skill

基于《AI编程技能规范文档V4.0_整合版》的AI自动化编程Skill，与项目解耦，开箱即用。

## 快速开始

### 1. 复制Skill到项目

```bash
# 方式1：直接复制
cp -r ai-auto-dev-skill/ /path/to/your/project/.kimi/skills/ai-auto-dev/

# 方式2：Git子模块（推荐）
git submodule add https://github.com/your-org/ai-auto-dev-skill.git .kimi/skills/ai-auto-dev
```

### 2. 配置Skill

编辑 `skill_config.yaml` 文件，配置项目信息。

### 3. 输入需求

在 `00_prompt_library/` 目录下创建需求文件 `user_requirement.md`。

### 4. 启动执行

```bash
cd .kimi/skills/ai-auto-dev/
python ai_auto_dev.py --mode daemon
```

### 5. 处理人工复核节点

当AI到达人工复核节点时，会发送通知。执行确认命令：

```bash
python ai_auto_dev.py --confirm T0050 --pass
```

## 文件夹结构

```
.
├── 00_prompt_library/         # Prompt资产库
├── 01_context_core/           # 核心上下文库
├── 02_exec_plans/             # 原子执行计划库
├── 03_delivery/               # 交付物归档
├── 04_logs/                   # 执行日志
├── 05_state_backup/           # 状态备份
├── 06_knowledge_base/         # 知识库
├── exec_index.yaml            # 执行索引文件
├── exec_index_auto_gen.py     # 索引生成脚本
├── ai_auto_dev.py             # 执行主脚本
├── skill_config.yaml          # Skill配置
└── README.md                  # 本文件
```

## 配套文档

- 《AI自动化编程全流程执行规范V3.0》 - 执行规范
- 《AI自动化编程环境准备指南》 - 环境准备
- 《AI编程技能规范文档V4.0_整合版》 - 理论基础

## 版本信息

- Skill版本：V3.0
- 适配规范：V4.0_整合版
- 最后更新：2025年2月
