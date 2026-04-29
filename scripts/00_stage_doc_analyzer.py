#!/usr/bin/env python3
"""
stage0_doc_analyzer.py - 阶段0：文档理解与意图分析
基于《AI自动化编程全流程执行规范V4.0》

用法：
    python stage0_doc_analyzer.py --mode analyze     # 启动文档分析
    python stage0_doc_analyzer.py --mode answer      # 提交问题回答
    python stage0_doc_analyzer.py --mode confirm --pass    # 确认意图确认书
    python stage0_doc_analyzer.py --mode confirm --reject  # 驳回意图确认书
    python stage0_doc_analyzer.py --mode status      # 查看阶段0进度
    python stage0_doc_analyzer.py --mode generate-config   # 重新生成配置文件
"""

import os
import sys
import json
import yaml
import argparse
import datetime
from pathlib import Path


# ============================================================
# 路径配置
# ============================================================
SKILL_DIR = Path(__file__).parent.parent  # ai-auto-dev/ 根目录
INPUT_DIR = SKILL_DIR / "00_input_documents"
OUTPUT_DIR = SKILL_DIR / "00_stage0_output"
EXEC_PLANS_DIR = SKILL_DIR / "02_exec_plans" / "00_stage0"
LOG_DIR = SKILL_DIR / "04_logs"
STATE_DIR = SKILL_DIR / "05_state_backup"

# 阶段0输出文件
FILES = {
    "document_list":     OUTPUT_DIR / "00.01-文档清单.md",
    "key_info":          OUTPUT_DIR / "00.02-关键信息摘要.md",
    "gap_list":          OUTPUT_DIR / "00.03-信息缺口清单.md",
    "intent_analysis":   OUTPUT_DIR / "00.04-用户意图分析.md",
    "tech_feasibility":  OUTPUT_DIR / "00.05-技术可行性分析.md",
    "term_query":        OUTPUT_DIR / "00.06-术语查询报告.md",
    "question_list":     OUTPUT_DIR / "00.07-问题清单.md",
    "answer_record":     OUTPUT_DIR / "00.08-问题回答记录.md",
    "intent_confirm":    OUTPUT_DIR / "00.09-意图确认书.md",
    "skill_config":      OUTPUT_DIR / "00.10-skill_config.yaml",
    "user_requirement":  OUTPUT_DIR / "00.11-user_requirement.md",
    "stage0_index":      OUTPUT_DIR / "00.12-stage0_exec_index.yaml",
    "state":             STATE_DIR / "stage0_state.json",
    "exec_log":          LOG_DIR / "stage0_exec.log",
}

# 阶段0任务列表
STAGE0_TASKS = [
    {"id": "S0_001", "name": "创建目录结构",            "output": None},
    {"id": "S0_002", "name": "扫描输入文档目录",         "output": "00.01-文档清单.md"},
    {"id": "S0_010", "name": "逐篇阅读文档（循环）",     "output": "00.02-关键信息摘要.md"},
    {"id": "S0_020", "name": "文档完整性分析",           "output": "00.03-信息缺口清单.md"},
    {"id": "S0_021", "name": "用户意图分析",             "output": "00.04-用户意图分析.md"},
    {"id": "S0_022", "name": "技术可行性分析",           "output": "00.05-技术可行性分析.md"},
    {"id": "S0_023", "name": "未知概念查询",             "output": "00.06-术语查询报告.md"},
    {"id": "S0_024", "name": "生成问题清单",             "output": "00.07-问题清单.md"},
    {"id": "S0_025", "name": "人工复核节点1：问题回答",  "output": None,                   "manual": True},
    {"id": "S0_026", "name": "记录用户回答",             "output": "00.08-问题回答记录.md"},
    {"id": "S0_027", "name": "生成意图确认书",           "output": "00.09-意图确认书.md"},
    {"id": "S0_028", "name": "人工复核节点2：意图确认",  "output": None,                   "manual": True},
    {"id": "S0_030", "name": "生成skill_config.yaml",    "output": "00.10-skill_config.yaml"},
    {"id": "S0_031", "name": "生成user_requirement.md",  "output": "00.11-user_requirement.md"},
    {"id": "S0_032", "name": "生成阶段0执行索引",        "output": "00.12-stage0_exec_index.yaml"},
    {"id": "S0_033", "name": "阶段0完成归档",            "output": None},
]


# ============================================================
# 工具函数
# ============================================================

def ensure_dirs():
    """确保所有必要目录存在"""
    for d in [INPUT_DIR, OUTPUT_DIR, EXEC_PLANS_DIR, LOG_DIR, STATE_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg: str, level: str = "INFO"):
    timestamp = now()
    line = f"[{timestamp}] [{level}] {msg}"
    print(line)
    try:
        with open(FILES["exec_log"], "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def load_state() -> dict:
    """加载阶段0执行状态"""
    if FILES["state"].exists():
        with open(FILES["state"], encoding="utf-8") as f:
            return json.load(f)
    return {
        "phase": "stage0",
        "current_step": "S0_001",
        "completed_tasks": [],
        "pending_human": None,
        "iteration_count": 0,
        "started_at": now(),
        "last_updated": now(),
    }

def save_state(state: dict):
    """保存阶段0执行状态"""
    state["last_updated"] = now()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(FILES["state"], "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def mark_task_done(state: dict, task_id: str):
    """标记任务完成"""
    if task_id not in state["completed_tasks"]:
        state["completed_tasks"].append(task_id)
    state["current_step"] = task_id
    save_state(state)
    log(f"✅ 任务完成：{task_id}")

def scan_input_documents() -> list:
    """扫描输入文档目录"""
    if not INPUT_DIR.exists():
        return []
    docs = []
    for f in sorted(INPUT_DIR.rglob("*")):
        if f.is_file() and not f.name.startswith("."):
            docs.append({
                "name": f.name,
                "path": str(f.relative_to(SKILL_DIR)),
                "size_kb": round(f.stat().st_size / 1024, 1),
                "type": classify_doc(f.name),
            })
    return docs

def classify_doc(filename: str) -> str:
    """按文件名判断文档类型"""
    name_lower = filename.lower()
    if any(k in name_lower for k in ["需求", "requirement", "req"]):
        return "需求文档"
    if any(k in name_lower for k in ["架构", "architecture", "arch"]):
        return "架构设计"
    if any(k in name_lower for k in ["数据库", "database", "db", "sql"]):
        return "数据库设计"
    if any(k in name_lower for k in ["详细", "detail", "设计"]):
        return "详细设计"
    if any(k in name_lower for k in ["接口", "api", "interface"]):
        return "接口文档"
    if f.suffix in [".java", ".py", ".ts", ".js", ".vue"] if (f := Path(filename)) else False:
        return "示例代码"
    return "其他文档"

def write_file(path: Path, content: str):
    """写入文件并打印日志"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    log(f"📄 已生成：{path.relative_to(SKILL_DIR)}")


# ============================================================
# 模式：analyze - 启动文档分析
# ============================================================

def mode_analyze():
    """阶段0主流程：扫描文档、生成分析报告、生成问题清单"""
    ensure_dirs()
    state = load_state()

    print("\n" + "="*60)
    print("  阶段0：文档理解与意图分析")
    print("  基于《AI自动化编程全流程执行规范V4.0》")
    print("="*60 + "\n")

    # S0_001: 创建目录
    log("S0_001 创建目录结构...")
    mark_task_done(state, "S0_001")

    # S0_002: 扫描文档
    log("S0_002 扫描输入文档目录...")
    docs = scan_input_documents()

    if not docs:
        print("\n⚠️  警告：00_input_documents/ 目录为空！")
        print("请将初步文档（需求、设计、数据库设计等）放入该目录后重新运行。\n")
        print("示例目录结构：")
        print("  00_input_documents/")
        print("  ├── 01-需求规格说明书-v1.md")
        print("  ├── 02-架构设计-v1.md")
        print("  └── 03-数据库设计-v1.md\n")
        sys.exit(1)

    # 生成文档清单
    doc_list_content = _gen_document_list(docs)
    write_file(FILES["document_list"], doc_list_content)
    mark_task_done(state, "S0_002")

    print(f"\n✅ 发现 {len(docs)} 个输入文档：")
    for d in docs:
        print(f"   📄 {d['name']} ({d['type']}, {d['size_kb']} KB)")

    # S0_010~S0_027: AI分析阶段
    # 这些步骤需要 AI 实际阅读文档内容并分析
    # 脚本生成结构化的分析框架，AI 负责填充实际内容
    print("\n" + "-"*60)
    print("📋 AI分析任务已就绪，请按以下提示词让AI执行分析：")
    print("-"*60)

    _print_ai_analysis_prompt(docs)

    # 生成问题清单模板（AI填充后保存）
    question_template = _gen_question_template()
    write_file(FILES["question_list"], question_template)

    state["pending_human"] = "S0_025"
    save_state(state)

    print("\n" + "="*60)
    print("  ⏸️  人工复核节点1 (S0_025)")
    print("  AI已生成问题清单模板：")
    print(f"  📄 {FILES['question_list'].relative_to(SKILL_DIR)}")
    print("\n  请步骤：")
    print("  1. AI阅读所有输入文档，填充问题清单中的实际问题")
    print("  2. 用户回答问题清单中的问题")
    print("  3. 将回答写入 00.07-问题清单.md（用户回答栏）")
    print("  4. 执行：python scripts/stage0_doc_analyzer.py --mode answer")
    print("="*60 + "\n")


def _gen_document_list(docs: list) -> str:
    table_rows = "\n".join(
        f"| {i+1} | {d['name']} | {d['type']} | {d['size_kb']} KB | 待分析 |"
        for i, d in enumerate(docs)
    )
    return f"""# 输入文档清单
生成时间：{now()}
文档总数：{len(docs)}

## 文档列表

| 序号 | 文档名称 | 文档类型 | 文件大小 | 完整度 |
|-----|---------|---------|---------|------|
{table_rows}

## AI分析说明
以上文档已扫描完成，AI将逐篇阅读并分析，提取关键信息，识别信息缺口，生成问题清单。
"""

def _gen_question_template() -> str:
    return f"""# 问题清单
生成时间：{now()}
状态：待AI填充（AI请根据文档分析结果填充实际问题）

> 📌 AI：请根据 00.02~00.06 的分析结果，填充以下问题模板。
> 用户：填写"您的回答"栏后，执行 `python scripts/stage0_doc_analyzer.py --mode answer`

---

## 🔴 必答问题（AI填充）

### Q1: 项目目标确认
- **问题**：{{AI根据文档分析填充}}
- **选项**：
  - A. 基于现有文档，补充完善并生成完整可运行代码
  - B. 仅生成核心模块，其他后续扩展
  - C. 其他（请说明）
- **AI建议**：{{AI分析建议}}
- **您的回答**：___

### Q2: 执行范围确认
- **问题**：{{AI根据文档中的模块列表填充}}
- **选项**（可多选）：
  - [ ] {{AI填充模块1}}
  - [ ] {{AI填充模块2}}
  - [ ] 全部模块
- **您的回答**：___

### Q3: 数据库连接配置
- **问题**：请提供开发环境数据库连接信息（不提供则使用模拟配置）
- **默认值**：使用模拟配置（AI自动生成占位符）
- **您的回答**：___

---

## 🟡 选答问题（有默认值，AI填充）

### Q10: 编码规范
- **问题**：使用哪种编码规范？
- **默认值**：阿里巴巴Java开发规范
- **您的回答**：___

### Q11: 测试覆盖率
- **问题**：最低测试覆盖率要求？
- **默认值**：行覆盖率80%，分支覆盖率70%，方法覆盖率100%
- **您的回答**：___

### Q12: 人工复核间隔
- **问题**：每完成多少个任务进行一次人工复核？
- **默认值**：50个任务
- **您的回答**：___
"""

def _print_ai_analysis_prompt(docs: list):
    doc_names = "\n".join(f"  - {d['name']} ({d['type']})" for d in docs)
    print(f"""
请让AI（在AI对话界面）执行以下分析任务：

【任务】
你是文档理解专家。请阅读以下文档并完成分析：
{doc_names}

【执行步骤】
1. 逐篇阅读每个文档，提取关键信息（项目目标/功能范围/技术栈/数据实体）
2. 评估每份文档完整度（百分比）
3. 识别信息缺口（缺失的关键信息）
4. 对未知术语进行说明
5. 将分析结果填充到以下文件：
   - {FILES['key_info'].relative_to(SKILL_DIR)}
   - {FILES['gap_list'].relative_to(SKILL_DIR)}
   - {FILES['intent_analysis'].relative_to(SKILL_DIR)}
   - {FILES['tech_feasibility'].relative_to(SKILL_DIR)}
   - {FILES['term_query'].relative_to(SKILL_DIR)}
6. 根据信息缺口，在 {FILES['question_list'].relative_to(SKILL_DIR)} 中填充实际问题

模板格式参考：references/stage0_guide.md
""")


# ============================================================
# 模式：answer - 处理用户回答
# ============================================================

def mode_answer():
    """处理用户对问题清单的回答"""
    state = load_state()
    print("\n" + "="*60)
    print("  处理用户回答 (S0_026)")
    print("="*60 + "\n")

    if not FILES["question_list"].exists():
        print("❌ 错误：问题清单文件不存在！请先运行 --mode analyze")
        sys.exit(1)

    # 读取问题清单，检查是否有回答
    with open(FILES["question_list"], encoding="utf-8") as f:
        content = f.read()

    # 检查是否有"___"未填写的回答
    unfilled = content.count("**您的回答**：___")
    if unfilled > 0:
        # 计算必答问题未填写数量（简单判断：必答区域的___数量）
        required_section = content.split("## 🟡")[0] if "## 🟡" in content else content
        required_unfilled = required_section.count("**您的回答**：___")
        if required_unfilled > 0:
            print(f"⚠️  还有 {required_unfilled} 个必答问题未填写！")
            print("请先填写所有必答问题（🔴标记的），再运行此命令。\n")
            print(f"问题清单文件：{FILES['question_list']}\n")
            sys.exit(1)

    # 将问题清单中的回答复制到回答记录
    answer_record = f"""# 问题回答记录
记录时间：{now()}

## 说明
本文件记录用户对问题清单的回答，由 stage0_doc_analyzer.py 自动生成。

## 回答内容

{content}
"""
    write_file(FILES["answer_record"], answer_record)
    mark_task_done(state, "S0_026")

    print("✅ 用户回答已记录")
    print("\n📋 AI请执行以下操作：")
    print("  1. 读取 00.08-问题回答记录.md 中的用户回答")
    print("  2. 分析回答，判断是否有新的信息缺口")
    print("  3. 如有新缺口（最多迭代3轮），生成补充问题，用户再次回答")
    print("  4. 否则，生成意图确认书：00.09-意图确认书.md")
    print("     格式参考：references/stage0_guide.md 中的模板3")
    print("  5. AI完成意图确认书后，执行：")
    print("     python scripts/stage0_doc_analyzer.py --mode confirm --pass")
    print()

    state["iteration_count"] = state.get("iteration_count", 0) + 1
    state["pending_human"] = "S0_028"
    save_state(state)


# ============================================================
# 模式：confirm - 处理意图确认
# ============================================================

def mode_confirm(passed: bool, reason: str = ""):
    """处理用户对意图确认书的确认"""
    state = load_state()
    print("\n" + "="*60)
    print("  意图确认书处理 (S0_028)")
    print("="*60 + "\n")

    if not passed:
        print(f"❌ 用户驳回意图确认书")
        print(f"   原因：{reason or '未说明'}")
        print("\n📋 AI请根据用户反馈修改意图确认书，然后重新提交确认")
        state["pending_human"] = "S0_028"
        save_state(state)
        return

    # 确认通过，生成配置文件
    print("✅ 意图确认书已通过！")
    mark_task_done(state, "S0_028")

    print("\n📋 AI请执行以下操作：")
    print("  1. 读取 00.09-意图确认书.md 中已确认的信息")
    print("  2. 生成 00.10-skill_config.yaml（格式参考 assets/skill_config.template.yaml）")
    print("  3. 生成 00.11-user_requirement.md（标准化需求文档）")
    print("  4. 完成后执行：python scripts/stage0_doc_analyzer.py --mode generate-config")
    print()


# ============================================================
# 模式：generate-config - 生成配置文件完成
# ============================================================

def mode_generate_config():
    """验证配置文件已生成，完成阶段0"""
    state = load_state()
    print("\n" + "="*60)
    print("  完成配置生成 (S0_030~S0_033)")
    print("="*60 + "\n")

    # 检查关键文件是否存在
    required_files = [
        (FILES["skill_config"], "skill_config.yaml"),
        (FILES["user_requirement"], "user_requirement.md"),
        (FILES["intent_confirm"], "意图确认书"),
    ]
    missing = []
    for fpath, fname in required_files:
        if fpath.exists():
            print(f"  ✅ {fname} 已生成")
        else:
            print(f"  ❌ {fname} 缺失！")
            missing.append(fname)

    if missing:
        print(f"\n⚠️  以下文件缺失，请AI先生成：{', '.join(missing)}")
        sys.exit(1)

    # 生成阶段0执行索引
    stage0_index = _gen_stage0_index(state)
    write_file(FILES["stage0_index"], stage0_index)
    mark_task_done(state, "S0_030")
    mark_task_done(state, "S0_031")
    mark_task_done(state, "S0_032")
    mark_task_done(state, "S0_033")

    state["pending_human"] = None
    state["stage0_completed"] = True
    state["completed_at"] = now()
    save_state(state)

    # 将配置文件复制到根目录
    root_config = SKILL_DIR / "skill_config.yaml"
    if not root_config.exists() and FILES["skill_config"].exists():
        import shutil
        shutil.copy(FILES["skill_config"], root_config)
        log("已将 skill_config.yaml 复制到 Skill 根目录")

    print("\n" + "="*60)
    print("  🎉 阶段0：文档理解与意图分析 完成！")
    print("="*60)
    print(f"\n📁 输出文件位于：{OUTPUT_DIR.relative_to(SKILL_DIR)}/")
    print("\n🚀 下一步：开始阶段1（需求分析）")
    print("   执行：python scripts/ai_auto_dev.py --phase requirement")
    print()


def _gen_stage0_index(state: dict) -> str:
    completed = state.get("completed_tasks", [])
    tasks_yaml = "\n".join(
        f"  - id: {t['id']}\n    name: {t['name']}\n    status: {'DONE' if t['id'] in completed else 'PENDING'}"
        for t in STAGE0_TASKS
    )
    return f"""# 阶段0执行索引
生成时间：{now()}

stage0:
  started_at: {state.get('started_at', now())}
  completed_at: {now()}
  iteration_count: {state.get('iteration_count', 1)}
  tasks:
{tasks_yaml}

outputs:
  document_list: 00_stage0_output/00.01-文档清单.md
  key_info: 00_stage0_output/00.02-关键信息摘要.md
  gap_list: 00_stage0_output/00.03-信息缺口清单.md
  intent_analysis: 00_stage0_output/00.04-用户意图分析.md
  question_list: 00_stage0_output/00.07-问题清单.md
  answer_record: 00_stage0_output/00.08-问题回答记录.md
  intent_confirm: 00_stage0_output/00.09-意图确认书.md
  skill_config: 00_stage0_output/00.10-skill_config.yaml
  user_requirement: 00_stage0_output/00.11-user_requirement.md
"""


# ============================================================
# 模式：status - 查看阶段0进度
# ============================================================

def mode_status():
    """查看阶段0执行进度"""
    state = load_state()
    completed = state.get("completed_tasks", [])
    total = len(STAGE0_TASKS)
    done_count = sum(1 for t in STAGE0_TASKS if t["id"] in completed)

    print("\n" + "="*60)
    print(f"  阶段0 执行进度：{done_count}/{total}")
    print("="*60 + "\n")

    for t in STAGE0_TASKS:
        status = "✅ DONE" if t["id"] in completed else ("⏸️  等待" if t.get("manual") else "⏳ PENDING")
        print(f"  {t['id']}  {status}  {t['name']}")

    pending_human = state.get("pending_human")
    if pending_human:
        print(f"\n⚠️  当前阻塞在人工复核节点：{pending_human}")

    if state.get("stage0_completed"):
        print("\n🎉 阶段0 已完成！")
    print()


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="阶段0：文档理解与意图分析脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--mode", choices=["analyze", "answer", "confirm", "generate-config", "status"],
                        default="status", help="执行模式")
    parser.add_argument("--pass", dest="passed", action="store_true", help="确认通过（--mode confirm使用）")
    parser.add_argument("--reject", dest="reject", action="store_true", help="驳回（--mode confirm使用）")
    parser.add_argument("--reason", default="", help="驳回原因（--reject使用）")

    args = parser.parse_args()

    if args.mode == "analyze":
        mode_analyze()
    elif args.mode == "answer":
        mode_answer()
    elif args.mode == "confirm":
        if args.passed:
            mode_confirm(passed=True)
        elif args.reject:
            mode_confirm(passed=False, reason=args.reason)
        else:
            print("❌ 请指定 --pass 或 --reject")
            sys.exit(1)
    elif args.mode == "generate-config":
        mode_generate_config()
    elif args.mode == "status":
        mode_status()


if __name__ == "__main__":
    main()
