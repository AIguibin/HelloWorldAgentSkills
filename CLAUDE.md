# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Repository Overview

This is a knowledge repository for universal enterprise architecture management task lists. The repository contains documentation, templates, and tools for managing complex software projects from initiation through post-launch support.

**Key purpose**: Provide standardized, reusable architecture management checklists and planning materials for enterprise projects with 16-month lifecycles.

---

## Core Documents

### Universal Task Lists

- `universal-lifecycle-tasks.md` (v1.0) - Base version with 175 tasks across 11 categories
- `universal-lifecycle-tasks-v1.1.md` (v1.1) - Enhanced version with:
  - 7 Excel configuration templates
  - 125 deliverables organized by 11 milestones
  - Dependency relationship diagrams
  - Risk identification matrix with 29 risks

### Supporting Documentation

- `architecture-requirements.md` - Detailed requirements breakdown by category (94 tasks)
- `weekly-task-schedule.md` - Weekly schedule with daily breakdown by person
- `detailed-daily-schedule.md` - Hourly task breakdown

### Format Conventions

- **Time notation**: T = go-live date, T-N = N months before go-live
- **Priority levels**: P0 (blocking), P1 (important), P2 (optional)
- **Status tracking**: 待办, 进行中, 已完成
- **Task ID format**: CATEGORY-XXX (e.g., PM-001, DB-015)

---

## Task Management Workflow

### When Adding New Tasks

1. Use the `aiguibin-text2-todo` skill for converting task lists to Excel
2. Follow task ID format: `CATEGORY-XXX`
3. Include required fields: 时间节点, 优先级, 负责人, 依赖项, 描述
4. Update dependency relationships in v1.1 document

### When Updating Deliverables

1. Deliverables are organized by milestones M1-M11
2. Format: 交付物名称 | 文件格式 | 负责人 | 验收标准
3. Track milestone completion in the deliverable matrix

### Risk Management

1. Risk categories: 项目级 (PRJ), 技术级 (TEC), 管理级 (MGT), 外部依赖 (EXT)
2. Risk levels: 高, 中, 低
3. Update risk response timeline when risks are mitigated

---

## Skills Available

The `.trae/skills/` directory contains specialized skills:

- `aiguibin-text2-todo` - Convert markdown task lists to Excel with automatic deduplication and effort estimation
- `xlsx` - Excel manipulation capabilities
- `docx` - Document generation from templates
- `pptx` - Presentation generation
- `mcp-builder` - MCP server development

**Important**: When users request task management or Excel generation, invoke the `aiguibin-text2-todo` skill via `/text2-todo` command.

---

## Document Maintenance

### Version Control

- Document versions are tracked independently (currently v1.0 and v1.1)
- Version history is noted in document headers
- Always update version number and date when making significant changes

### Updating Task Lists

When modifying `universal-lifecycle-tasks.md`:
1. Maintain the evolution relationships section
2. Update dependencies if adding new tasks
3. Ensure T-time notation is consistent
4. Update task counts if adding/removing tasks

When modifying `universal-lifecycle-tasks-v1.1.md`:
1. Keep Excel templates synchronized with task list
2. Update deliverable counts when milestones change
3. Maintain dependency matrix accuracy
4. Refresh risk status as project progresses

---

## T-Time Notation

Standard format for expressing project timeline:
- T = go-live date
- T-16M = 16 months before go-live
- T-2W = 2 weeks before go-live
- T-3D = 3 days before go-live
- T+1M = 1 month after go-live

Use this notation consistently across all documents to maintain alignment between task lists and schedules.

---

## Milestone Structure

Project is divided into 11 milestones (M1-M11):

| Milestone | Time | Focus |
|-----------|------|-------|
| M1 | T-16M | Project startup |
| M2 | T-15M | Foundation standards |
| M3 | T-13M | Environment setup |
| M4 | T-10M | Database architecture |
| M5 | T-8M | Public components |
| M6 | T-8M | Base services |
| M7 | T-8M | Non-functional requirements |
| M8 | T-4M | Performance testing |
| M9 | T-4M | Security testing |
| M10 | T-1M | Production preparation |
| M11 | T | Go-live completion |

---

## Language and Style

- All documentation is in Simplified Chinese
- Maintain professional, enterprise terminology
- Use standard industry terms (CI/CD, DevOps, SLB, TPS, etc.)
- Keep descriptions concise but comprehensive

---

## Common Operations

### Generate Excel Task List

When user requests converting task lists to Excel:
```
/use-skill text2-todo
```

The skill will:
- Parse markdown task text
- Deduplicate similar tasks
- Estimate effort (人天)
- Calculate planned dates
- Assign responsible persons
- Generate formatted Excel

### Create New Project Schedule

1. Copy relevant tasks from universal task list
2. Convert T-time to actual dates based on project start
3. Update milestone dates
4. Generate weekly breakdown using the schedule template
5. Export to Excel for distribution

### Update Risk Status

1. Review risk matrix in v1.1 document
2. Update status column (待办/进行中/已完成)
3. Add mitigation notes if applicable
4. Update risk response timeline if dates change

---

## Document Relationships

```
prd.txt → architecture-requirements.md → universal-lifecycle-tasks.md
                                            ↓
                                    universal-lifecycle-tasks-v1.1.md
                                            ↓
                                    weekly-task-schedule.md
                                            ↓
                                    detailed-daily-schedule.md
```

Always maintain consistency across documents when updating task lists, dependencies, or timelines.

---

## Important Notes

- This is a **documentation repository**, not a code repository
- No build, test, or deployment commands are applicable
- Primary interactions involve reading, updating, and formatting documentation
- Excel skills are the main automation capability available
- Version management follows document-level versioning, not git tags

---

## Special Characters and Encoding

- All documents use UTF-8 encoding
- Markdown tables are used extensively for structured data
- Mermaid diagrams are used for dependency visualization
- Chinese characters are used throughout - ensure encoding is preserved