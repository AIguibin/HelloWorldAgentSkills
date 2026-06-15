# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是一个AI全流程自动化编程框架，可实现从文档理解到代码交付的端到端软件开发自动化。框架采用7阶段工作流，AI代理会自动切换角色（需求专家、架构师、开发工程师、测试工程师、文档管理员）。

**核心命令：**
- `python scripts/aiguibin_automated_main.py --status` - 查看执行状态
- `python scripts/aiguibin_automated_main.py --resume` - 从断点恢复执行
- `python scripts/aiguibin_automated_main.py --phase <阶段>` - 开始指定阶段

**任务管理：**
- `python scripts/exec_index_manager.py --report` - 生成进度报告
- `python scripts/exec_index_manager.py --done <任务ID>` - 标记任务完成
- `python scripts/exec_index_manager.py --task <任务ID>` - 查看任务详情
- `python scripts/exec_index_manager.py --next` - 显示下一个待执行任务

**阶段0专用：**
- `python scripts/00_stage_doc_analyzer.py --mode analyze` - 启动文档分析
- `python scripts/00_stage_doc_analyzer.py --mode status` - 查看阶段0进度

## 架构设计

### 执行阶段（7阶段）
1. **阶段0** (`stage0`) - 文档理解与意图分析。需将输入文档放入 `00_input_documents/`，自动生成配置文件。
2. **阶段1** (`requirement`) - 需求分析，遵循MECE原则，编写用户故事（Given-When-Then），穷举场景。
3. **阶段2** (`architecture`) - 设计，包括系统架构、数据库设计、接口设计、详细伪代码。
4. **阶段3** (`task_split`) - 任务拆分，将设计分解为原子任务（每个10-20分钟），生成依赖图。
5. **阶段4** (`coding`) - 编码实现，使用PDCA循环（计划-执行-检查-处理），自我审查，满足测试覆盖率要求。
6. **阶段5** (`testing`) - 测试，包括单元测试（JUnit5+Mockito）和接口测试（curl脚本）。
7. **阶段6** (`archive`) - 文档归档，整理交付物并生成最终报告。

### 关键状态文件
- `exec_index.yaml` - 主任务索引，包含所有原子任务及其依赖关系、状态、交付物。这是执行进度的唯一真实来源。
- `skill_config.yaml` - 项目配置，包括技术栈、编码规范、测试覆盖率要求、路径配置等。阶段0自动生成。
- `05_state_backup/main_state.json` - 运行时状态，用于跨会话恢复。

### 目录结构
- `00_input_documents/` - 阶段0分析的输入文档
- `00_stage0_output/` - 阶段0输出（意图确认书、配置等）
- `01_context_core/` - 持久化上下文文件，用于会话恢复
- `02_exec_plans/01_requirement/` - 需求规格说明书
- `02_exec_plans/02_architecture/` - 设计文档和SQL脚本
- `03_delivery/` - 最终交付物，按模块和版本组织
- `04_logs/` - 执行日志和技术债务记录
- `05_state_backup/` - 断点续跑的检查点备份

### 任务状态流转
任务状态流转：`PENDING` → `IN_PROGRESS` → `DONE`（或 `BLOCKED`、`PENDING_HUMAN`、`SKIPPED`）
- `PENDING_HUMAN` - 人工复核节点（默认每50个任务一个）
- `BLOCKED` - P0阻塞问题，必须解决后才能继续

## 开发流程

### 角色切换
框架要求显式声明角色切换：`[切换角色 → {角色名}]`
角色包括：文档理解专家、需求分析专家、架构设计专家、详细设计专家、高级开发工程师、测试工程师、代码审查员、文档管理员

### 自我审查闭环
每个阶段完成后需切换为"代码审查员"角色，对照 `references/review_checklists.md` 逐项检查，全部通过后才能进入下一阶段。

### 版本锚定机制
进入"已定版"状态的文档必须在 `01_context_core/current_context.md` 中记录锚定版本。修改已锚定文档需要创建新版本并通知用户。

## 质量管控

### P0阻塞问题（必须立即修复）
- SQL注入风险
- 未处理的空指针异常
- 敏感信息泄露
- 多步操作的事务不完整
- 测试覆盖率低于配置阈值
- 需求冲突

### 测试覆盖率要求
在 `skill_config.yaml` 中配置（默认：行覆盖率≥80%、分支覆盖率≥70%、方法覆盖率=100%）。外部依赖（Mapper、Redis、外部服务）必须Mock。

## 编码规范

默认使用"阿里巴巴Java开发规范"：
- 命名：类名用 `UpperCamelCase`，方法/变量用 `lowerCamelCase`，常量用 `UPPER_CASE_WITH_UNDERSCORES`
- 分层：Controller（仅参数校验）→ Service（业务逻辑、事务控制）→ Mapper（数据库操作）
- 日志：使用 `@Slf4j`，禁止使用 `System.out.println`
- 异常处理：禁止空catch块
- 事务：写操作使用 `@Transactional`，只读操作使用 `@Transactional(readOnly=true)`

## 会话恢复

新会话中恢复执行时：
1. 加载 `exec_index.yaml`，找到第一个状态为 `IN_PROGRESS` 或 `PENDING` 的任务
2. 加载 `01_context_core/current_context.md` 恢复执行上下文
3. 验证依赖任务已完成
4. 声明恢复：`[恢复执行] 当前任务：{{任务ID}} - {{任务名称}}，继续执行...`

每完成10个任务自动进行偏差校验，确保与锚定文档保持一致。