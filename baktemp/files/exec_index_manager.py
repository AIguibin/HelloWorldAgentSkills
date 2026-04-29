#!/usr/bin/env python3
"""
exec_index_manager.py - 执行索引管理工具
用于读取/更新 exec_index.yaml，管理所有原子任务状态

用法：
    python exec_index_manager.py --report                     # 生成进度报告
    python exec_index_manager.py --task T0301                 # 查看任务详情
    python exec_index_manager.py --done T0301                 # 标记任务完成
    python exec_index_manager.py --done T0301 --deliverable src/main/.../Foo.java
    python exec_index_manager.py --blocked T0301 --reason "依赖未完成"
    python exec_index_manager.py --next                       # 查看下一个待执行任务
    python exec_index_manager.py --phase requirement          # 查看指定阶段任务
    python exec_index_manager.py --pending                    # 列出所有待执行任务
    python exec_index_manager.py --debt                       # 查看技术债务
"""

import os
import sys
import yaml
import json
import argparse
import datetime
from pathlib import Path
from collections import defaultdict
from typing import Optional, List


SKILL_DIR = Path(__file__).parent.parent
INDEX_FILE = SKILL_DIR / "exec_index.yaml"
DEBT_FILE = SKILL_DIR / "04_logs" / "tech_debt.md"
LOG_FILE = SKILL_DIR / "04_logs" / "exec_manager.log"
STATE_BACKUP = SKILL_DIR / "05_state_backup"

STATUS_EMOJI = {
    "DONE": "✅",
    "IN_PROGRESS": "🔄",
    "PENDING": "⏳",
    "BLOCKED": "🚫",
    "PENDING_HUMAN": "⏸️",
    "SKIPPED": "⏭️",
}

PHASE_NAMES = {
    "stage0":        "阶段0：文档理解",
    "requirement":   "阶段1：需求分析",
    "architecture":  "阶段2：概要设计",
    "detail_design": "阶段3：详细设计",
    "task_split":    "阶段4：任务拆分",
    "coding":        "阶段5：编码实现",
    "testing":       "阶段6：测试",
    "archive":       "阶段7：文档归档",
}


# ============================================================
# 工具函数
# ============================================================

def now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now()}] {msg}\n")

def load_index() -> dict:
    """加载执行索引文件"""
    if not INDEX_FILE.exists():
        print(f"❌ exec_index.yaml 不存在：{INDEX_FILE}")
        print("   请先运行阶段3（任务拆分）生成执行索引，或从模板创建：")
        print(f"   cp assets/exec_index.template.yaml exec_index.yaml")
        sys.exit(1)
    with open(INDEX_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def save_index(index: dict):
    """保存执行索引文件（同时备份）"""
    # 备份
    STATE_BACKUP.mkdir(parents=True, exist_ok=True)
    backup_file = STATE_BACKUP / f"exec_index_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
    with open(backup_file, "w", encoding="utf-8") as f:
        yaml.dump(index, f, allow_unicode=True, default_flow_style=False)

    # 更新 last_updated
    if "meta" in index:
        index["meta"]["last_updated"] = now()

    # 写入
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        yaml.dump(index, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def get_all_tasks(index: dict) -> list:
    """获取所有任务列表"""
    return index.get("tasks", [])

def find_task(index: dict, task_id: str) -> Optional[dict]:
    """根据ID查找任务"""
    for t in get_all_tasks(index):
        if t.get("id") == task_id:
            return t
    return None


# ============================================================
# 功能函数
# ============================================================

def cmd_report(index: dict):
    """生成进度报告"""
    tasks = get_all_tasks(index)
    meta = index.get("meta", {})

    # 统计
    by_status = defaultdict(list)
    by_phase = defaultdict(lambda: defaultdict(int))
    for t in tasks:
        status = t.get("status", "PENDING")
        phase = t.get("stage", "unknown")
        by_status[status].append(t)
        by_phase[phase][status] += 1

    total = len(tasks)
    done = len(by_status.get("DONE", []))
    in_progress = len(by_status.get("IN_PROGRESS", []))
    blocked = len(by_status.get("BLOCKED", []))
    pending = len(by_status.get("PENDING", [])) + len(by_status.get("PENDING_HUMAN", []))
    progress_pct = round(done / total * 100, 1) if total > 0 else 0

    print("\n" + "="*70)
    print(f"  📊 执行进度报告")
    print(f"  项目：{meta.get('project', '未知')}")
    print(f"  生成时间：{now()}")
    print("="*70)

    print(f"\n  总任务数：{total}")
    print(f"  ✅ 已完成：{done} ({progress_pct}%)")
    print(f"  🔄 进行中：{in_progress}")
    print(f"  🚫 已阻塞：{blocked}")
    print(f"  ⏳ 待执行：{pending}")

    # 进度条
    bar_len = 40
    filled = int(bar_len * done / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"\n  进度: [{bar}] {progress_pct}%\n")

    # 按阶段统计
    print("  按阶段统计：")
    for phase, stats in by_phase.items():
        phase_name = PHASE_NAMES.get(phase, phase)
        phase_total = sum(stats.values())
        phase_done = stats.get("DONE", 0)
        print(f"  {'─'*50}")
        print(f"  {phase_name}")
        status_line = "  " + "  ".join(
            f"{STATUS_EMOJI.get(s, s)} {s}: {n}"
            for s, n in sorted(stats.items())
        )
        print(status_line)

    # 阻塞任务
    if by_status.get("BLOCKED"):
        print(f"\n  🚫 阻塞任务（需立即处理）：")
        for t in by_status["BLOCKED"]:
            print(f"    {t['id']} - {t.get('name', '')} | 原因：{t.get('block_reason', '未说明')}")

    # 人工复核节点
    if by_status.get("PENDING_HUMAN"):
        print(f"\n  ⏸️  等待人工确认：")
        for t in by_status["PENDING_HUMAN"]:
            print(f"    {t['id']} - {t.get('name', '')}")
            print(f"    确认命令：python scripts/ai_auto_dev.py --confirm {t['id']} --pass")

    print()


def cmd_task_detail(index: dict, task_id: str):
    """查看任务详情"""
    task = find_task(index, task_id)
    if not task:
        print(f"❌ 任务不存在：{task_id}")
        sys.exit(1)

    status = task.get("status", "PENDING")
    print(f"\n{'='*60}")
    print(f"  任务详情：{task_id}")
    print(f"{'='*60}")
    print(f"  名称：{task.get('name', '')}")
    print(f"  阶段：{PHASE_NAMES.get(task.get('stage', ''), task.get('stage', ''))}")
    print(f"  状态：{STATUS_EMOJI.get(status, status)} {status}")
    print(f"  预计耗时：{task.get('estimated_minutes', '-')} 分钟")

    if task.get("depends_on"):
        print(f"  依赖任务：{', '.join(task['depends_on'])}")

    if task.get("deliverable"):
        print(f"  交付物：{task['deliverable']}")

    if task.get("test_file"):
        print(f"  测试文件：{task['test_file']}")

    if task.get("coverage"):
        print(f"  覆盖率：{task['coverage']}")

    print(f"\n  验收标准：")
    for criterion in task.get("acceptance_criteria", ["（未定义）"]):
        print(f"    - {criterion}")

    if task.get("completed_at"):
        print(f"\n  完成时间：{task['completed_at']}")
        print(f"  实际耗时：{task.get('actual_minutes', '-')} 分钟")

    if task.get("issues"):
        print(f"\n  发现问题（已修复）：")
        for issue in task["issues"]:
            print(f"    - {issue}")

    if task.get("block_reason"):
        print(f"\n  阻塞原因：{task['block_reason']}")

    print()


MANUAL_REVIEW_INTERVAL = 50  # 每N个普通任务触发一次人工复核

def cmd_mark_done(index: dict, task_id: str, deliverable: str = "", coverage: str = "", issues: list = None):
    """标记任务完成，并在每50个任务时自动触发人工复核提醒"""
    task = find_task(index, task_id)
    if not task:
        print(f"❌ 任务不存在：{task_id}")
        sys.exit(1)

    old_status = task.get("status", "PENDING")
    task["status"] = "DONE"
    task["completed_at"] = now()
    if deliverable:
        task["deliverable"] = deliverable
    if coverage:
        task["coverage"] = coverage
    if issues:
        task["issues"] = issues

    # 更新meta统计
    done_count = sum(1 for t in get_all_tasks(index) if t.get("status") == "DONE")
    in_progress_count = sum(1 for t in get_all_tasks(index) if t.get("status") == "IN_PROGRESS")
    pending_count = sum(1 for t in get_all_tasks(index) if t.get("status") in ("PENDING", "PENDING_HUMAN"))
    blocked_count = sum(1 for t in get_all_tasks(index) if t.get("status") == "BLOCKED")

    if "meta" in index:
        index["meta"]["completed"] = done_count
        index["meta"]["in_progress"] = in_progress_count
        index["meta"]["pending"] = pending_count
        index["meta"]["blocked"] = blocked_count

    save_index(index)
    log(f"DONE: {task_id} | {task.get('name', '')} | 累计完成: {done_count}")

    print(f"✅ 任务已标记完成：{task_id} - {task.get('name', '')}")
    if deliverable:
        print(f"   交付物：{deliverable}")
    if coverage:
        print(f"   覆盖率：{coverage}")

    # ── 自动检测是否需要触发人工复核 ──
    # 只统计非人工复核节点的普通任务
    normal_done = sum(
        1 for t in get_all_tasks(index)
        if t.get("status") == "DONE" and not t.get("manual")
    )

    if normal_done > 0 and normal_done % MANUAL_REVIEW_INTERVAL == 0:
        _trigger_human_review(index, task_id, done_count)
        return  # 人工复核节点处理后不再显示下一个任务

    # 查找下一个可执行任务
    next_task = _find_next_task(index, task_id)
    if next_task:
        if next_task.get("manual") or next_task.get("status") == "PENDING_HUMAN":
            print(f"\n⏸️  下一个是人工复核节点：{next_task['id']} - {next_task.get('name', '')}")
            print(f"   确认后继续：python scripts/ai_auto_dev.py --confirm {next_task['id']} --pass")
        else:
            print(f"\n▶️  下一个任务：{next_task['id']} - {next_task.get('name', '')}")
    else:
        print(f"\n🎉 当前阶段任务已全部完成！")
    print()


def _trigger_human_review(index: dict, trigger_task_id: str, done_count: int):
    """触发人工复核流程"""
    tasks = get_all_tasks(index)

    # 收集本轮（最近50个任务）的交付物
    done_tasks = [t for t in tasks if t.get("status") == "DONE" and not t.get("manual")]
    recent_batch = done_tasks[-MANUAL_REVIEW_INTERVAL:]

    deliverables = [t.get("deliverable") for t in recent_batch if t.get("deliverable")]
    coverages = [f"{t['id']}: {t.get('coverage', 'N/A')}" for t in recent_batch if t.get("coverage")]
    issues_found = [i for t in recent_batch for i in t.get("issues", [])]

    # 生成复核报告
    review_id = f"REVIEW_{done_count:04d}"
    report_content = f"""# 人工复核报告

**复核节点ID**：{review_id}
**触发任务**：{trigger_task_id}
**生成时间**：{now()}
**累计完成任务**：{done_count} 个
**本轮任务数**：{len(recent_batch)} 个

---

## 本轮交付物清单（最近{MANUAL_REVIEW_INTERVAL}个任务）

{chr(10).join(f'- {d}' for d in deliverables[:20]) or '（无文件交付物）'}

## 测试覆盖率汇总

{chr(10).join(f'- {c}' for c in coverages[:10]) or '（本轮无需覆盖率）'}

## 发现的问题（已修复）

{chr(10).join(f'- {i}' for i in issues_found[:10]) or '（本轮无问题）'}

---

## 请确认

- [ ] 交付物符合预期
- [ ] 覆盖率达标
- [ ] 无未处理的P0问题

**确认通过并继续**：
```bash
python scripts/ai_auto_dev.py --confirm {review_id} --pass
```

**驳回需修改**：
```bash
python scripts/ai_auto_dev.py --confirm {review_id} --reject --reason '原因'
```
"""
    # 写入复核报告
    report_path = Path(__file__).parent.parent / "04_logs" / f"review_report_{review_id}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    # 在 exec_index.yaml 中插入复核节点
    review_task = {
        "id": review_id,
        "name": f"人工复核节点（第{done_count}个任务完成）",
        "stage": tasks[-1].get("stage", "coding") if tasks else "coding",
        "phase": tasks[-1].get("phase", 5) if tasks else 5,
        "status": "PENDING_HUMAN",
        "manual": True,
        "depends_on": [trigger_task_id],
        "estimated_minutes": 30,
        "acceptance_criteria": ["用户确认本批次交付物质量"],
        "deliverable": str(report_path.relative_to(report_path.parent.parent)),
        "confirm_command": f"python scripts/ai_auto_dev.py --confirm {review_id} --pass",
        "triggered_at": now(),
    }
    index["tasks"].append(review_task)
    save_index(index)
    log(f"触发人工复核节点: {review_id}")

    print(f"\n{'='*60}")
    print(f"  ⏸️  人工复核节点触发！（已完成 {done_count} 个任务）")
    print(f"  复核报告：04_logs/review_report_{review_id}.md")
    print(f"\n  请查看报告后执行：")
    print(f"  python scripts/ai_auto_dev.py --confirm {review_id} --pass")
    print(f"{'='*60}\n")


def cmd_mark_blocked(index: dict, task_id: str, reason: str):
    """标记任务阻塞"""
    task = find_task(index, task_id)
    if not task:
        print(f"❌ 任务不存在：{task_id}")
        sys.exit(1)

    task["status"] = "BLOCKED"
    task["block_reason"] = reason
    task["blocked_at"] = now()
    save_index(index)
    log(f"BLOCKED: {task_id} | {reason}")

    print(f"🚫 任务已标记阻塞：{task_id}")
    print(f"   原因：{reason}")
    print(f"\n⚠️  这是一个P0阻塞问题，必须解决后才能继续执行！")
    print(f"   解决后执行：python scripts/exec_index_manager.py --done {task_id}")
    print()


def cmd_next(index: dict):
    """查看下一个待执行任务"""
    tasks = get_all_tasks(index)
    completed_ids = {t["id"] for t in tasks if t.get("status") == "DONE"}

    for t in tasks:
        if t.get("status") not in ("PENDING", None):
            continue
        # 检查依赖是否满足
        depends = t.get("depends_on", [])
        if all(d in completed_ids for d in depends):
            print(f"\n▶️  下一个任务：{t['id']} - {t.get('name', '')}")
            print(f"   阶段：{PHASE_NAMES.get(t.get('stage', ''), t.get('stage', ''))}")
            print(f"   预计耗时：{t.get('estimated_minutes', '-')} 分钟")
            if t.get("acceptance_criteria"):
                print(f"   验收标准：")
                for c in t["acceptance_criteria"][:3]:
                    print(f"     - {c}")
            print()
            return

    # 检查是否有待等待人工的
    for t in tasks:
        if t.get("status") == "PENDING_HUMAN":
            print(f"\n⏸️  等待人工确认：{t['id']} - {t.get('name', '')}")
            print(f"   执行确认命令：python scripts/ai_auto_dev.py --confirm {t['id']} --pass")
            return

    print("\n🎉 所有任务已完成！\n")


def cmd_phase_tasks(index: dict, phase: str):
    """列出指定阶段的所有任务"""
    tasks = [t for t in get_all_tasks(index) if t.get("stage") == phase]
    if not tasks:
        print(f"❌ 阶段不存在或无任务：{phase}")
        print(f"   可用阶段：{', '.join(PHASE_NAMES.keys())}")
        sys.exit(1)

    phase_name = PHASE_NAMES.get(phase, phase)
    total = len(tasks)
    done = sum(1 for t in tasks if t.get("status") == "DONE")

    print(f"\n{phase_name}  ({done}/{total})")
    print("="*60)
    for t in tasks:
        status = t.get("status", "PENDING")
        emoji = STATUS_EMOJI.get(status, "?")
        deliverable = t.get("deliverable", "")
        print(f"  {emoji} {t['id']}  {t.get('name', '')}")
        if deliverable:
            print(f"       └─ {deliverable}")
    print()


def cmd_list_pending(index: dict):
    """列出所有待执行任务"""
    tasks = get_all_tasks(index)
    completed_ids = {t["id"] for t in tasks if t.get("status") == "DONE"}
    pending = [t for t in tasks if t.get("status") in ("PENDING", None, "IN_PROGRESS")]

    if not pending:
        print("\n🎉 没有待执行任务！\n")
        return

    print(f"\n⏳ 待执行任务（共 {len(pending)} 个）：")
    print("="*60)
    for t in pending:
        depends = t.get("depends_on", [])
        deps_met = all(d in completed_ids for d in depends)
        can_run = "可立即执行" if deps_met else f"等待：{', '.join(d for d in depends if d not in completed_ids)}"
        status_emoji = STATUS_EMOJI.get(t.get("status", "PENDING"), "⏳")
        print(f"  {status_emoji} {t['id']}  {t.get('name', '')}")
        print(f"       └─ {can_run}")
    print()


def cmd_add_debt(description: str, severity: str = "中", location: str = ""):
    """记录技术债务"""
    DEBT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 生成债务ID
    existing_count = 0
    if DEBT_FILE.exists():
        with open(DEBT_FILE, encoding="utf-8") as f:
            existing_count = f.read().count("| TD")

    debt_id = f"TD{existing_count + 1:03d}"

    row = f"| {debt_id} | {severity} | {description} | {location} | {now()} | 待处理 |\n"

    if not DEBT_FILE.exists():
        header = """# 技术债务记录

| 债务ID | 严重程度 | 描述 | 所在位置 | 发现时间 | 状态 |
|-------|---------|------|---------|---------|------|
"""
        with open(DEBT_FILE, "w", encoding="utf-8") as f:
            f.write(header)

    with open(DEBT_FILE, "a", encoding="utf-8") as f:
        f.write(row)

    print(f"📝 技术债务已记录：{debt_id} - {description}")


def _find_next_task(index: dict, completed_task_id: str) -> Optional[dict]:
    """找到下一个可执行的任务"""
    tasks = get_all_tasks(index)
    completed_ids = {t["id"] for t in tasks if t.get("status") == "DONE"}

    for t in tasks:
        if t.get("status") not in ("PENDING", None):
            continue
        depends = t.get("depends_on", [])
        if all(d in completed_ids for d in depends):
            return t
    return None


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="执行索引管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--report", action="store_true", help="生成进度报告")
    parser.add_argument("--task", metavar="TASK_ID", help="查看任务详情")
    parser.add_argument("--done", metavar="TASK_ID", help="标记任务完成")
    parser.add_argument("--blocked", metavar="TASK_ID", help="标记任务阻塞")
    parser.add_argument("--next", action="store_true", help="查看下一个待执行任务")
    parser.add_argument("--phase", metavar="PHASE", help="查看指定阶段任务")
    parser.add_argument("--pending", action="store_true", help="列出所有待执行任务")
    parser.add_argument("--debt", action="store_true", help="查看技术债务")
    parser.add_argument("--add-debt", metavar="DESCRIPTION", help="记录新的技术债务")
    # --done 附加参数
    parser.add_argument("--deliverable", default="", help="交付物路径（配合--done使用）")
    parser.add_argument("--coverage", default="", help="测试覆盖率（配合--done使用）")
    # --blocked 附加参数
    parser.add_argument("--reason", default="", help="阻塞原因（配合--blocked使用）")
    # --add-debt 附加参数
    parser.add_argument("--severity", default="中", choices=["高", "中", "低"], help="债务严重程度")
    parser.add_argument("--location", default="", help="债务所在位置（文件路径）")

    args = parser.parse_args()

    if args.add_debt:
        cmd_add_debt(args.add_debt, args.severity, args.location)
        return

    if args.debt:
        if DEBT_FILE.exists():
            with open(DEBT_FILE, encoding="utf-8") as f:
                print(f.read())
        else:
            print("✅ 暂无技术债务记录")
        return

    # 需要加载索引的命令
    index = load_index()

    if args.report:
        cmd_report(index)
    elif args.task:
        cmd_task_detail(index, args.task)
    elif args.done:
        cmd_mark_done(index, args.done, args.deliverable, args.coverage)
    elif args.blocked:
        if not args.reason:
            print("❌ 标记阻塞需要指定原因：--reason '原因说明'")
            sys.exit(1)
        cmd_mark_blocked(index, args.blocked, args.reason)
    elif args.next:
        cmd_next(index)
    elif args.phase:
        cmd_phase_tasks(index, args.phase)
    elif args.pending:
        cmd_list_pending(index)
    else:
        # 默认显示报告
        cmd_report(index)


if __name__ == "__main__":
    main()
