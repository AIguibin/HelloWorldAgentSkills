# 原子执行计划示例

## exec_index.yaml 格式说明

```yaml
# 执行索引文件 - 记录所有原子任务状态
meta:
  project: "{{项目名称}}"
  created_at: "{{创建时间}}"
  last_updated: "{{最后更新时间}}"
  total_tasks: 0
  completed: 0
  in_progress: 0
  pending: 0
  blocked: 0

tasks:
  - id: "S0_001"
    name: "扫描输入文档目录"
    phase: 0
    stage: "stage0"
    status: "DONE"           # PENDING/IN_PROGRESS/DONE/BLOCKED/SKIPPED
    depends_on: []
    estimated_minutes: 5
    actual_minutes: 3
    deliverable: "00_stage0_output/00.01-文档清单.md"
    completed_at: "{{时间}}"

  - id: "S0_002"
    name: "阅读需求规格说明书"
    phase: 0
    stage: "stage0"
    status: "DONE"
    depends_on: ["S0_001"]
    estimated_minutes: 15
    actual_minutes: 12
    deliverable: ""
    completed_at: "{{时间}}"

  - id: "S0_025"
    name: "生成问题清单"
    phase: 0
    stage: "stage0"
    status: "PENDING_HUMAN"  # 等待人工复核
    depends_on: ["S0_024"]
    estimated_minutes: 10
    manual_confirm: true
    confirm_command: "python ai_auto_dev.py --confirm S0_025 --pass"
    deliverable: "00_stage0_output/00.07-问题清单.md"

  - id: "T0101"
    name: "需求理解与摘要"
    phase: 1
    stage: "requirement"
    status: "PENDING"
    depends_on: ["S0_028"]
    estimated_minutes: 15
    deliverable: "02_exec_plans/01_requirement/01-需求理解摘要.md"
```

---

## 阶段0 原子执行计划列表（示例）

| 任务ID | 任务名称 | 预计耗时 | 交付物 | 依赖 |
|-------|---------|---------|-------|-----|
| S0_001 | 扫描输入文档目录 | 5min | 文档清单草稿 | — |
| S0_002 | 阅读文档1（需求规格） | 15min | 阅读笔记 | S0_001 |
| S0_003 | 阅读文档2（设计文档） | 15min | 阅读笔记 | S0_001 |
| S0_004 | 阅读文档3（数据库设计） | 10min | 阅读笔记 | S0_001 |
| S0_010 | 生成文档清单 | 5min | 00.01-文档清单.md | S0_004 |
| S0_011 | 提取项目核心信息 | 10min | 00.02-关键信息摘要.md | S0_010 |
| S0_012 | 完整性分析 | 10min | 00.03-信息缺口清单.md | S0_011 |
| S0_013 | 用户意图分析 | 10min | 00.04-用户意图分析.md | S0_012 |
| S0_014 | 技术可行性分析 | 10min | 00.05-技术可行性分析.md | S0_013 |
| S0_015 | 未知术语查询（批1） | 15min | 00.06-术语查询报告.md | S0_014 |
| S0_020 | 生成必答问题 | 10min | 问题草稿 | S0_015 |
| S0_021 | 生成选答问题 | 10min | 问题草稿 | S0_020 |
| S0_022 | 整理问题优先级 | 5min | 问题草稿 | S0_021 |
| S0_023 | 为每个问题添加AI建议 | 10min | 问题草稿 | S0_022 |
| **S0_025** | **生成问题清单（人工复核节点1）** | 10min | **00.07-问题清单.md** | S0_023 |
| S0_026 | 记录用户回答 | 5min | 00.08-问题回答记录.md | S0_025（用户回答后）|
| S0_027 | 生成意图确认书 | 15min | 00.09-意图确认书.md | S0_026 |
| **S0_028** | **提交意图确认书（人工复核节点2）** | 10min | — | S0_027 |
| S0_030 | 生成skill_config.yaml | 10min | 00.10-skill_config.yaml | S0_028（用户确认后）|
| S0_031 | 生成user_requirement.md | 10min | 00.11-user_requirement.md | S0_030 |
| S0_032 | 生成阶段0执行索引 | 5min | 00.12-stage0_exec_index.yaml | S0_031 |
| S0_033 | 阶段0完成归档 | 5min | 阶段0报告 | S0_032 |

---

## 原子执行计划详细模板

每个原子执行计划文件（存放在 `02_exec_plans/` 下）应包含：

```markdown
# 原子执行计划：{{任务名称}}

## 基本信息
- 任务ID：{{任务ID}}
- 阶段：{{阶段名称}}
- AI角色：{{角色名称}}
- 预计耗时：{{N}}分钟
- 依赖任务：{{依赖ID列表}}

## 前置条件
- [ ] {{前置条件1}}
- [ ] {{前置条件2}}

## 执行步骤
1. {{步骤1}}
2. {{步骤2}}
3. {{步骤3}}

## 验收标准
- [ ] {{验收标准1}}
- [ ] {{验收标准2}}

## 交付物
- 文件路径：{{文件路径}}
- 文件格式：{{格式}}

## 自我审查清单
- [ ] 输出是否符合预期格式
- [ ] 是否覆盖所有场景
- [ ] 内容是否准确完整

## 执行记录
- 开始时间：{{时间}}
- 完成时间：{{时间}}
- 实际耗时：{{N}}分钟
- 遇到的问题：{{问题描述}}
- 解决方案：{{解决方案}}
```
