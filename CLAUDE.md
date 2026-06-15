# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered automated programming framework that enables end-to-end software development automation from document understanding to code delivery. It implements a 7-stage workflow with AI agents that automatically switch roles (requirements expert, architect, developer, tester, documentation manager).

**Primary Commands:**
- `python scripts/aiguibin_automated_main.py --status` - Show execution status
- `python scripts/aiguibin_automated_main.py --resume` - Resume from breakpoint
- `python scripts/aiguibin_automated_main.py --phase <phase>` - Start specific phase

**Task Management:**
- `python scripts/exec_index_manager.py --report` - Generate progress report
- `python scripts/exec_index_manager.py --done <task_id>` - Mark task complete
- `python scripts/exec_index_manager.py --task <task_id>` - View task details
- `python scripts/exec_index_manager.py --next` - Show next pending task

**Stage 0:**
- `python scripts/00_stage_doc_analyzer.py --mode analyze` - Start document analysis
- `python scripts/00_stage_doc_analyzer.py --mode status` - View Stage 0 progress

## Architecture

### Execution Phases (7 stages)
1. **Stage 0** (`stage0`) - Document understanding and intent analysis. Requires user input in `00_input_documents/` and generates configuration.
2. **Stage 1** (`requirement`) - Requirements analysis with MECE principle, user stories with Given-When-Then, scenario enumeration.
3. **Stage 2** (`architecture`) - Design including system architecture, database schema, API contracts, detailed pseudocode.
4. **Stage 3** (`task_split`) - Task decomposition into atomic units (10-20 min each) with dependency graph.
5. **Stage 4** (`coding`) - Implementation with PDCA cycle (Plan-Do-Check-Act), self-review, test coverage requirements.
6. **Stage 5** (`testing`) - Unit tests (JUnit5+Mockito) and API tests (curl scripts).
7. **Stage 6** (`archive`) - Deliverable archiving and final report generation.

### Key State Files
- `exec_index.yaml` - Master task index with all atomic tasks, their dependencies, status, and deliverables. This is the source of truth for execution progress.
- `skill_config.yaml` - Project configuration including tech stack, coding standards, test coverage requirements, and paths. Auto-generated in Stage 0.
- `05_state_backup/main_state.json` - Runtime state for resumption across sessions.

### Directory Structure
- `00_input_documents/` - Input documents for Stage 0 analysis
- `00_stage0_output/` - Stage 0 outputs (intent confirmation, config, etc.)
- `01_context_core/` - Persistent context files for session recovery
- `02_exec_plans/01_requirement/` - Requirements specifications
- `02_exec_plans/02_architecture/` - Design documents and SQL
- `03_delivery/` - Final deliverables organized by module and version
- `04_logs/` - Execution logs and tech debt tracking
- `05_state_backup/` - Checkpoint backups for resume functionality

### Task State Machine
Task statuses flow: `PENDING` → `IN_PROGRESS` → `DONE` (or `BLOCKED`, `PENDING_HUMAN`, `SKIPPED`)
- `PENDING_HUMAN` - Manual review checkpoint (every 50 tasks by default)
- `BLOCKED` - P0 blocker that requires resolution before continuation

## Development Workflow

### Role Switching
The framework requires explicit role switching with declaration: `[切换角色 → {角色名}]`
Roles include: 文档理解专家, 需求分析专家, 架构设计专家, 详细设计专家, 高级开发工程师, 测试工程师, 代码审查员, 文档管理员

### Self-Review Closed Loop
Every phase completion requires switching to "代码审查员" role and running against `references/review_checklists.md` before proceeding.

### Version Anchoring
Documents entering "已定版" status must be anchored in `01_context_core/current_context.md`. Changes to anchored documents require version bump and user notification.

## Quality Gates

### P0 Blockers (must resolve immediately)
- SQL injection risk
- Unhandled NullPointerException
- Sensitive information leakage
- Incomplete transactions for multi-step operations
- Test coverage below configured threshold
- Requirements conflicts

### Test Coverage Requirements
Configurable in `skill_config.yaml` (default: line≥80%, branch≥70%, method=100%). External dependencies (Mapper, Redis, external services) must be Mocked.

## Coding Standards

Default is "阿里巴巴Java开发规范" (Alibaba Java Coding Standard):
- Naming: `UpperCamelCase` for classes, `lowerCamelCase` for methods/variables, `UPPER_CASE_WITH_UNDERSCORES` for constants
- Layering: Controller (validation only) → Service (business logic, transactions) → Mapper (database ops)
- Logging: Use `@Slf4j`, never `System.out.println`
- Exception handling: No empty catch blocks
- Transactions: `@Transactional` for write operations, `@Transactional(readOnly=true)` for reads

## Session Recovery

When resuming execution in a new session:
1. Load `exec_index.yaml` to find first `IN_PROGRESS` or `PENDING` task
2. Load `01_context_core/current_context.md` to restore execution context
3. Verify dependencies are satisfied
4. Declare recovery: `[恢复执行] 当前任务：{{任务ID}} - {{任务名称}}，继续执行...`

Use deviation checking every 10 tasks to validate alignment with anchored documents.