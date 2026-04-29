# 上下文管理与断点续跑机制

## 一、为什么需要上下文管理

AI在长任务执行中面临以下挑战：
- **上下文窗口有限**：长任务无法在单次对话中完成
- **会话重置**：新会话开始时，AI不记得之前做了什么
- **执行偏差**：长时间执行后，AI可能偏离原始意图

本机制通过**状态持久化 + 版本锚定 + 偏差校验**解决上述问题。

---

## 二、必须持久化的核心信息

在 `01_context_core/` 目录中维护以下文件，每次新会话开始时优先读取：

```
01_context_core/
├── project_info.md          # 项目基本信息（技术栈、路径、规范）
├── current_context.md       # 当前执行上下文（锚定版本、当前阶段、关键决策）
├── data_dictionary.md       # 数据字典（所有实体定义，跨会话共享）
├── api_contracts.md         # 接口契约（路径、请求/响应格式，已定版）
└── business_rules.md        # 业务规则（校验规则、状态流转，已确认）
```

### current_context.md 格式

```markdown
# 当前执行上下文
最后更新：{{YYYY-MM-DD HH:mm}}

## 锚定版本（绝对不能更改，改变前必须重新定版）
- 需求规格说明书：v{{版本号}}（路径：02_exec_plans/01_requirement/...）
- 概要设计文档：v{{版本号}}（路径：02_exec_plans/02_architecture/...）
- 详细设计文档：v{{版本号}}（路径：02_exec_plans/02_architecture/...）

## 当前执行状态
- 当前阶段：阶段{{N}}（{{阶段名称}}）
- 当前任务：{{任务ID}} - {{任务名称}}
- 已完成任务数：{{N}}
- 待完成任务数：{{M}}

## 关键决策记录（不可随意更改）
- 技术栈：{{已确认的技术栈}}
- 统一响应格式：{{格式}}
- 错误码体系：{{错误码范围和规则}}
- 编码规范：{{规范名称}}

## 下一步执行计划
继续执行任务：{{下一个任务ID}} - {{任务描述}}
```

---

## 三、会话恢复流程

当新会话开始时（或用户说"继续执行"时），按以下步骤恢复：

```
Step 1: 读取 exec_index.yaml，找到第一个 status=IN_PROGRESS 或 PENDING 的任务
Step 2: 读取 01_context_core/current_context.md，恢复执行上下文
Step 3: 读取对应任务的依赖任务，确认前置条件已满足
Step 4: 宣告：[恢复执行] 当前任务：{{任务ID}} - {{任务名称}}，继续执行...
Step 5: 继续执行，无需重新解释已完成的内容
```

---

## 四、版本锚定机制

**原则**：所有AI生成必须基于定版的前置文档。定版后的文档不能在未通知用户的情况下修改。

```
文档定版时机：每个阶段完成且自我审查通过后，文档进入"已定版"状态

定版操作：
1. 在文档头部添加：[已定版 v{{版本号}}] {{YYYY-MM-DD}}
2. 在 current_context.md 中记录锚定版本
3. 更新 exec_index.yaml 中该阶段的 document_version 字段

版本变更处理：
- 如需修改已定版文档，必须：
  1. 创建新版本文件（v1.0.0 → v1.1.0）
  2. 在 current_context.md 中更新锚定版本
  3. 评估影响范围，决定是否需要重做后续工作
```

---

## 五、偏差校验机制

**校验时机**：
1. 每完成10个任务，自动进行一次轻量偏差校验
2. 跨越阶段时，进行全面偏差校验
3. 人工复核时，检查是否偏离用户意图

**偏差校验步骤**：

```
1. 读取 01_context_core/current_context.md 中的锚定版本
2. 对比当前正在执行的内容与锚定文档
3. 检查以下项目：
   - 技术选型是否与锚定版本一致
   - 数据字典字段是否与锚定版本一致  
   - 接口路径/响应格式是否与锚定版本一致
   - 业务规则是否与锚定版本一致
4. 如发现偏差：
   - 记录偏差内容（what changed, when, why）
   - 评估影响（哪些已完成任务需要回溯）
   - 上报给用户，等待决策
```

---

## 六、动态上下文压缩

当上下文窗口接近限制时，执行以下压缩策略：

```
压缩策略（保留关键，丢弃冗余）：

必须保留（不可压缩）：
- 当前任务的完整描述和验收标准
- 依赖任务的关键输出（接口签名、数据结构）
- 数据字典（实体定义）
- 关键业务规则

可以压缩：
- 历史执行记录 → 压缩为一行摘要："已完成 T0101~T0150，共50个任务，阶段4编码已完成60%"
- 已通过的审查记录 → 只保留"审查通过"结论
- 中间计算过程 → 只保留最终结果

压缩后写入：01_context_core/current_context.md
```

---

## 七、状态持久化规范

**持久化时机**：
- 每完成一个原子任务（status: DONE）
- 每次人工复核节点
- 每10个任务完成时（检查点备份）

**状态写入操作**：

```python
# 完成任务后，立即更新 exec_index.yaml
task:
  id: "T0301"
  status: "DONE"           # PENDING → IN_PROGRESS → DONE
  completed_at: "2025-02-01 14:30"
  actual_minutes: 18
  deliverable: "src/main/java/.../DictTypeServiceImpl.java"
  test_file: "src/test/java/.../DictTypeServiceImplTest.java"
  coverage: "行: 85%, 分支: 75%, 方法: 100%"
  issues: []               # 发现的问题（已修复）
```

---

## 八、断点续跑命令

```bash
# 查看当前执行状态
python scripts/ai_auto_dev.py --status

# 从断点恢复执行
python scripts/ai_auto_dev.py --resume

# 从指定任务开始执行
python scripts/ai_auto_dev.py --from-task T0305

# 强制重跑指定任务（忽略已DONE状态）
python scripts/ai_auto_dev.py --rerun T0305

# 查看某个任务的详细信息
python scripts/exec_index_manager.py --task T0305

# 生成执行进度报告
python scripts/exec_index_manager.py --report
```
