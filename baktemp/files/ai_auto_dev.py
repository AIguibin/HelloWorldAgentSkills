#!/usr/bin/env python3
"""
ai_auto_dev.py - AI自动化编程主控脚本
基于《AI自动化编程全流程执行规范V4.0》

用法：
    python ai_auto_dev.py                          # 查看当前状态
    python ai_auto_dev.py --status                 # 查看详细状态
    python ai_auto_dev.py --start                  # 从头开始（阶段0）
    python ai_auto_dev.py --resume                 # 从断点恢复
    python ai_auto_dev.py --phase requirement      # 开始指定阶段
    python ai_auto_dev.py --from-task T0305        # 从指定任务开始
    python ai_auto_dev.py --confirm T0050 --pass   # 人工复核节点确认通过
    python ai_auto_dev.py --confirm T0050 --reject # 人工复核节点驳回
    python ai_auto_dev.py --rerun T0305            # 重新执行指定任务
    python ai_auto_dev.py --checklist              # 显示当前阶段检查清单
"""

import os
import sys
import yaml
import json
import argparse
import datetime
import subprocess
from pathlib import Path


SKILL_DIR = Path(__file__).parent.parent
INDEX_FILE = SKILL_DIR / "exec_index.yaml"
CONFIG_FILE = SKILL_DIR / "skill_config.yaml"
CONTEXT_DIR = SKILL_DIR / "01_context_core"
LOG_DIR = SKILL_DIR / "04_logs"
STATE_DIR = SKILL_DIR / "05_state_backup"
DELIVERY_DIR = SKILL_DIR / "03_delivery"

MAIN_LOG = LOG_DIR / "main_exec.log"
STATE_FILE = STATE_DIR / "main_state.json"

PHASES = ["stage0", "requirement", "architecture", "task_split", "coding", "testing", "archive"]

PHASE_INFO = {
    "stage0":       {"name": "阶段0：文档理解与意图分析", "ai_role": "文档理解专家"},
    "requirement":  {"name": "阶段1：需求分析",          "ai_role": "需求分析专家"},
    "architecture": {"name": "阶段2：设计",              "ai_role": "架构设计专家"},
    "task_split":   {"name": "阶段3：任务拆分",          "ai_role": "开发专家"},
    "coding":       {"name": "阶段4：编码实现",          "ai_role": "高级开发工程师"},
    "testing":      {"name": "阶段5：测试",              "ai_role": "测试工程师"},
    "archive":      {"name": "阶段6：文档归档",          "ai_role": "文档管理员"},
}

MANUAL_REVIEW_INTERVAL = 50  # 每N个任务触发一次人工复核


# ============================================================
# 工具函数
# ============================================================

def now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg: str, level: str = "INFO"):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{now()}] [{level}] {msg}"
    print(line)
    with open(MAIN_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {
        "current_phase": None,
        "current_task": None,
        "completed_count": 0,
        "since_last_review": 0,
        "started_at": now(),
        "last_updated": now(),
        "phase_history": [],
    }

def save_state(state: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = now()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

def load_index() -> dict:
    if INDEX_FILE.exists():
        with open(INDEX_FILE, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

def save_index(index: dict):
    if "meta" in index:
        index["meta"]["last_updated"] = now()
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        yaml.dump(index, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def separator(title: str = "", width: int = 70):
    if title:
        pad = (width - len(title) - 2) // 2
        print("=" * pad + f" {title} " + "=" * pad)
    else:
        print("=" * width)


# ============================================================
# 状态显示
# ============================================================

def cmd_status():
    """显示完整的执行状态"""
    state = load_state()
    config = load_config()
    index = load_index()

    separator("AI自动化编程 执行状态")
    print(f"\n  项目：{config.get('project', {}).get('name', '未配置')}")
    print(f"  技术栈：{config.get('tech_stack', {}).get('backend', '未配置')}")
    print(f"  启动时间：{state.get('started_at', '未知')}")
    print(f"  最后更新：{state.get('last_updated', '未知')}")

    current_phase = state.get("current_phase")
    current_task = state.get("current_task")

    if current_phase:
        phase_info = PHASE_INFO.get(current_phase, {})
        print(f"\n  当前阶段：{phase_info.get('name', current_phase)}")
        print(f"  AI角色：{phase_info.get('ai_role', '未知')}")
        if current_task:
            print(f"  当前任务：{current_task}")

    completed = state.get("completed_count", 0)
    since_review = state.get("since_last_review", 0)
    next_review = MANUAL_REVIEW_INTERVAL - since_review

    print(f"\n  累计完成任务：{completed} 个")
    print(f"  距下次人工复核：{next_review} 个任务")

    # 阶段进度
    if index.get("tasks"):
        tasks = index["tasks"]
        total = len(tasks)
        done = sum(1 for t in tasks if t.get("status") == "DONE")
        blocked = sum(1 for t in tasks if t.get("status") == "BLOCKED")

        print(f"\n  总任务进度：{done}/{total}")
        if blocked > 0:
            print(f"  🚫 阻塞任务：{blocked} 个（需立即处理！）")

    # 快速操作提示
    print("\n  快速操作：")
    if not current_phase:
        print("    python ai_auto_dev.py --start         # 开始执行")
    else:
        print("    python ai_auto_dev.py --resume        # 继续执行")
        print("    python ai_auto_dev.py --status        # 刷新状态")

    separator()
    print()


# ============================================================
# 阶段启动
# ============================================================

def cmd_start():
    """从头开始执行（阶段0）"""
    state = load_state()
    config = load_config()

    separator("启动 AI自动化编程")

    if config:
        print(f"\n  ✅ 已找到配置文件：skill_config.yaml")
        print(f"  项目：{config.get('project', {}).get('name', '未知')}")
        print(f"\n  询问：是否跳过阶段0（文档理解），直接从阶段1（需求分析）开始？")
        print("  如需跳过阶段0，请运行：python ai_auto_dev.py --phase requirement")
        print("  如需从阶段0开始，请运行：python scripts/stage0_doc_analyzer.py --mode analyze")
    else:
        print("\n  未找到 skill_config.yaml，将从阶段0开始。")
        print("\n  步骤1：将初步文档放入 00_input_documents/ 目录")
        print("  步骤2：执行：python scripts/stage0_doc_analyzer.py --mode analyze")

    separator()


def cmd_start_phase(phase: str):
    """开始指定阶段"""
    if phase not in PHASES:
        print(f"❌ 无效的阶段：{phase}")
        print(f"   可用阶段：{', '.join(PHASES)}")
        sys.exit(1)

    state = load_state()
    phase_info = PHASE_INFO[phase]

    separator(phase_info["name"])

    state["current_phase"] = phase
    state["last_phase_started"] = now()
    save_state(state)

    log(f"开始阶段：{phase} - {phase_info['name']}")

    print(f"\n  [切换角色 → {phase_info['ai_role']}]")
    print(f"\n  📋 AI请执行以下操作：")

    # 各阶段的AI提示
    phase_prompts = {
        "requirement": _requirement_phase_prompt,
        "architecture": _architecture_phase_prompt,
        "task_split": _task_split_phase_prompt,
        "coding": _coding_phase_prompt,
        "testing": _testing_phase_prompt,
        "archive": _archive_phase_prompt,
    }

    if phase in phase_prompts:
        phase_prompts[phase]()
    elif phase == "stage0":
        print("  请运行：python scripts/stage0_doc_analyzer.py --mode analyze")

    print()


def _requirement_phase_prompt():
    print("""
  1. 读取 00_stage0_output/00.11-user_requirement.md（或用户描述的需求）
  2. 读取 references/prompt_library.md 中的"阶段1：需求分析Prompt"
  3. 按需求分析SOP执行（6个步骤）：
     - 需求理解 → 需求拆分（MECE原则）→ 场景穷举 → 数据字典 → 编写需求规格说明书 → 自我审查
  4. 对照 references/review_checklists.md 的"需求分析审查清单"进行自我审查
  5. 交付物：02_exec_plans/01_requirement/需求规格说明书.md
  6. 完成后执行：python ai_auto_dev.py --phase architecture
""")

def _architecture_phase_prompt():
    print("""
  1. 读取 02_exec_plans/01_requirement/需求规格说明书.md
  2. 读取 references/prompt_library.md 中的"阶段2：设计Prompt"
  3. 按概要设计SOP执行：
     - 系统架构（分层、模块划分）→ 数据库设计（含建表SQL）→ 接口设计（RESTful）
  4. 按详细设计SOP执行：
     - 每个核心方法的伪代码 → 异常处理方案
  5. 对照 references/review_checklists.md 的"设计审查清单"进行自我审查
  6. 交付物：02_exec_plans/02_architecture/ 下的概要设计.md、详细设计.md、建表SQL.sql
  7. 完成后执行：python ai_auto_dev.py --phase task_split
""")

def _task_split_phase_prompt():
    print("""
  1. 读取详细设计文档
  2. 将设计分解为原子执行计划（每个10-20分钟，单个类/方法/组件粒度）
  3. 按格式生成 exec_index.yaml（格式参考 assets/exec_index.template.yaml）
  4. 每个任务包含：ID、名称、阶段、依赖关系、前置条件、验收标准、交付物路径
  5. 任务ID命名：T{阶段号}{3位序号}，如 T4001
  6. 在索引中设置人工复核节点（每50个任务一个）：status: PENDING_HUMAN
  7. 完成后执行：python ai_auto_dev.py --phase coding
""")

def _coding_phase_prompt():
    print("""
  1. 读取 exec_index.yaml，找到第一个 status=PENDING 的编码任务
  2. 读取 references/coding_sop.md 的"PDCA执行循环"
  3. 对每个任务：
     a. Plan：读取任务描述+验收标准+设计文档，找参考样例
     b. Do：编码实现（注释+方法签名+实现）+ 单元测试
     c. Check：切换为代码审查员，对照 references/review_checklists.md 审查
     d. Act：修正问题，标记完成：
        python scripts/exec_index_manager.py --done T4001 --deliverable 路径
  4. 每完成50个任务，生成人工复核报告（格式见 assets/human_review_report.template.md）
""")

def _testing_phase_prompt():
    print("""
  1. 读取接口设计文档
  2. 读取 references/coding_sop.md 的"接口测试SOP"
  3. 为每个接口端点生成 curl 测试脚本（正常场景+异常场景+边界场景）
  4. 执行测试脚本，记录结果
  5. 生成测试报告：03_delivery/test_report.md
  6. 完成后执行：python ai_auto_dev.py --phase archive
""")

def _archive_phase_prompt():
    print("""
  1. 将所有交付物归档到 03_delivery/，按模块和版本组织
  2. 为每份文档添加定版标记：[已定版 v{{版本号}}] {{日期}}
  3. 生成最终交付清单（包含所有文件路径、版本号、覆盖率）
  4. 更新 exec_index.yaml 整体状态为 COMPLETED
  5. 生成项目完成报告
""")


# ============================================================
# 断点恢复
# ============================================================

def cmd_resume():
    """从断点恢复执行"""
    state = load_state()
    index = load_index()

    separator("断点恢复")

    current_phase = state.get("current_phase")
    if not current_phase:
        print("\n  没有找到执行记录，请先运行 --start")
        return

    phase_info = PHASE_INFO.get(current_phase, {})
    print(f"\n  恢复阶段：{phase_info.get('name', current_phase)}")
    print(f"  [切换角色 → {phase_info.get('ai_role', '未知')}]")

    # 找到第一个未完成的任务
    if index.get("tasks"):
        completed_ids = {t["id"] for t in index["tasks"] if t.get("status") == "DONE"}
        next_task = None
        for t in index["tasks"]:
            if t.get("status") in ("PENDING", None, "IN_PROGRESS"):
                deps = t.get("depends_on", [])
                if all(d in completed_ids for d in deps):
                    next_task = t
                    break

        if next_task:
            print(f"\n  恢复任务：{next_task['id']} - {next_task.get('name', '')}")
            print(f"  预计耗时：{next_task.get('estimated_minutes', '-')} 分钟")
            print(f"\n  AI请继续执行此任务，然后标记完成：")
            print(f"  python scripts/exec_index_manager.py --done {next_task['id']}")
        else:
            pending_human = next(
                (t for t in index["tasks"] if t.get("status") == "PENDING_HUMAN"), None
            )
            if pending_human:
                print(f"\n  ⏸️  等待人工确认：{pending_human['id']} - {pending_human.get('name', '')}")
                print(f"  确认通过：python ai_auto_dev.py --confirm {pending_human['id']} --pass")
            else:
                print("\n  当前阶段所有任务已完成！")
                next_phase_idx = PHASES.index(current_phase) + 1
                if next_phase_idx < len(PHASES):
                    next_phase = PHASES[next_phase_idx]
                    print(f"  请继续执行下一阶段：python ai_auto_dev.py --phase {next_phase}")

    separator()
    print()


# ============================================================
# 人工复核节点确认
# ============================================================

def cmd_confirm(task_id: str, passed: bool, reason: str = ""):
    """处理人工复核节点"""
    index = load_index()
    state = load_state()

    # 找到任务
    task = None
    for t in index.get("tasks", []):
        if t.get("id") == task_id:
            task = t
            break

    if not task:
        print(f"❌ 任务不存在：{task_id}")
        sys.exit(1)

    separator(f"人工复核节点 {task_id}")
    print(f"  任务：{task.get('name', '')}")

    if passed:
        task["status"] = "DONE"
        task["confirmed_at"] = now()
        task["confirmed_by"] = "human"
        save_index(index)

        state["since_last_review"] = 0  # 重置计数器
        save_state(state)

        log(f"人工复核通过：{task_id}")
        print(f"\n  ✅ 复核通过！")
        print(f"\n  继续执行：python ai_auto_dev.py --resume")
    else:
        print(f"\n  ❌ 复核驳回：{reason or '未说明原因'}")
        print(f"\n  AI请根据反馈修正，修正后重新提交：")
        print(f"  python ai_auto_dev.py --confirm {task_id} --pass")

    separator()
    print()


# ============================================================
# 重跑指定任务
# ============================================================

def cmd_rerun(task_id: str):
    """重新执行指定任务（清除DONE状态）"""
    index = load_index()
    task = None
    for t in index.get("tasks", []):
        if t.get("id") == task_id:
            task = t
            break

    if not task:
        print(f"❌ 任务不存在：{task_id}")
        sys.exit(1)

    old_status = task.get("status")
    task["status"] = "PENDING"
    task.pop("completed_at", None)
    task.pop("deliverable", None)
    task["rerun_at"] = now()
    task["rerun_reason"] = "手动重跑"
    save_index(index)

    log(f"任务重跑：{task_id}（原状态：{old_status}）")
    print(f"✅ 任务已重置为 PENDING：{task_id} - {task.get('name', '')}")
    print(f"   继续执行：python ai_auto_dev.py --resume")
    print()


# ============================================================
# 检查清单显示
# ============================================================

def cmd_checklist(phase: str = None):
    """显示当前阶段的检查清单"""
    state = load_state()
    current_phase = phase or state.get("current_phase", "coding")

    checklist_file = SKILL_DIR / "references" / "review_checklists.md"
    if not checklist_file.exists():
        print(f"❌ 检查清单文件不存在：{checklist_file}")
        return

    with open(checklist_file, encoding="utf-8") as f:
        content = f.read()

    # 按阶段筛选
    phase_sections = {
        "requirement": "需求分析审查清单",
        "architecture": "概要设计审查清单",
        "coding": "代码审查清单",
        "testing": "单元测试审查清单",
    }

    section_name = phase_sections.get(current_phase)
    if section_name and section_name in content:
        start = content.find(f"## {section_name}")
        end = content.find("\n## ", start + 1)
        section = content[start:end] if end > 0 else content[start:]
        print(f"\n{section}\n")
    else:
        print(content)


# ============================================================
# 人工复核报告生成
# ============================================================

def generate_review_report(state: dict, index: dict, trigger_task_id: str):
    """生成人工复核报告"""
    config = load_config()
    tasks = index.get("tasks", [])
    completed_count = state.get("completed_count", 0)
    current_phase = state.get("current_phase", "unknown")

    # 最近完成的50个任务
    done_tasks = [t for t in tasks if t.get("status") == "DONE"]
    recent_tasks = done_tasks[-50:] if len(done_tasks) > 50 else done_tasks

    # 统计交付物
    deliverables = [t.get("deliverable") for t in recent_tasks if t.get("deliverable")]

    report_template = SKILL_DIR / "assets" / "human_review_report.template.md"
    if report_template.exists():
        with open(report_template, encoding="utf-8") as f:
            template = f.read()
    else:
        template = _default_review_template()

    report_content = template.format(
        task_id=trigger_task_id,
        phase=PHASE_INFO.get(current_phase, {}).get("name", current_phase),
        completed_count=completed_count,
        recent_count=len(recent_tasks),
        deliverables="\n".join(f"- {d}" for d in deliverables[:20]),
        timestamp=now(),
        confirm_cmd=f"python ai_auto_dev.py --confirm {trigger_task_id} --pass",
        reject_cmd=f"python ai_auto_dev.py --confirm {trigger_task_id} --reject --reason '原因'",
    )

    report_path = LOG_DIR / f"review_report_{trigger_task_id}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_path


def _default_review_template() -> str:
    return """# 人工复核报告

**任务节点**：{task_id}
**当前阶段**：{phase}
**生成时间**：{timestamp}

---

## 执行概况

- 本轮完成任务：{recent_count} 个
- 累计完成任务：{completed_count} 个

## 本轮交付物清单

{deliverables}

## 质量评估

（AI自动填充：覆盖率统计、审查问题数、已修复数、P0问题情况）

## 待您确认的事项

（AI自动填充：需要人工决策的事项）

---

## 复核操作

**确认通过**：
```bash
{confirm_cmd}
```

**驳回修改**：
```bash
{reject_cmd}
```
"""


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="AI自动化编程主控脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--status", action="store_true", help="查看详细状态")
    parser.add_argument("--start", action="store_true", help="从头开始执行")
    parser.add_argument("--resume", action="store_true", help="从断点恢复执行")
    parser.add_argument("--phase", metavar="PHASE", help="开始指定阶段")
    parser.add_argument("--from-task", metavar="TASK_ID", help="从指定任务开始")
    parser.add_argument("--confirm", metavar="TASK_ID", help="人工复核节点操作")
    parser.add_argument("--rerun", metavar="TASK_ID", help="重新执行指定任务")
    parser.add_argument("--checklist", action="store_true", help="显示当前阶段检查清单")
    # --confirm 附加参数
    parser.add_argument("--pass", dest="passed", action="store_true", help="确认通过")
    parser.add_argument("--reject", action="store_true", help="驳回")
    parser.add_argument("--reason", default="", help="驳回原因")

    args = parser.parse_args()

    if args.status or len(sys.argv) == 1:
        cmd_status()
    elif args.start:
        cmd_start()
    elif args.resume:
        cmd_resume()
    elif args.phase:
        cmd_start_phase(args.phase)
    elif args.from_task:
        # 将 exec_index 中该任务之前的所有任务标记为DONE，然后恢复
        print(f"从任务 {args.from_task} 开始执行...")
        index = load_index()
        tasks = index.get("tasks", [])
        target_idx = next((i for i, t in enumerate(tasks) if t["id"] == args.from_task), -1)
        if target_idx < 0:
            print(f"❌ 任务不存在：{args.from_task}")
            sys.exit(1)
        # 将之前的任务标记为DONE（仅未完成的）
        for t in tasks[:target_idx]:
            if t.get("status") == "PENDING":
                t["status"] = "SKIPPED"
        save_index(index)
        cmd_resume()
    elif args.confirm:
        if args.passed:
            cmd_confirm(args.confirm, passed=True)
        elif args.reject:
            cmd_confirm(args.confirm, passed=False, reason=args.reason)
        else:
            print("❌ 请指定 --pass 或 --reject")
            sys.exit(1)
    elif args.rerun:
        cmd_rerun(args.rerun)
    elif args.checklist:
        cmd_checklist()


if __name__ == "__main__":
    main()
