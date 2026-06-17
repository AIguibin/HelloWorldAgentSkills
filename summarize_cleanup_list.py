"""生成清理归档表清单的完整统计摘要，用于文档生成"""
import json
import sys
import io
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r"e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\cleanup_archive_list.json", 'r', encoding='utf-8') as f:
    rows = json.load(f)

print(f"清单总表数: {len(rows)}")
print("=" * 80)

# 按数据库统计
db_counter = Counter(r["所属数据库"] for r in rows)
print("\n【按数据库统计】")
for db, count in db_counter.most_common():
    print(f"  {db}: {count}张")

# 按模块统计
module_counter = Counter(r["所属模块"] for r in rows)
print("\n【按模块统计】")
for module, count in module_counter.most_common():
    print(f"  {module}: {count}张")

# 按责任人统计
owner_counter = Counter(r["责任人"] for r in rows)
print("\n【按责任人统计】")
for owner, count in owner_counter.most_common():
    print(f"  {owner}: {count}张")

# 按是否数据清理统计
clean_counter = Counter(r["是否数据清理"] for r in rows)
print("\n【按是否数据清理统计】")
for k, v in clean_counter.most_common():
    print(f"  {k}: {v}张")

# 按归档策略统计
print("\n【按归档策略统计】")
archive_groups = defaultdict(list)
for r in rows:
    strategy = r["归档策略"] if r["归档策略"] else "(空/未定义)"
    archive_groups[strategy].append(r["表名_英文"])
for strategy, tables in archive_groups.items():
    print(f"  {strategy}: {len(tables)}张")

# 清理策略模式分析
print("\n【清理策略模式分析】")
patterns = {
    "按年创建历史表": 0,
    "失效超过1年": 0,
    "保留N月/N年数据": 0,
    "其他": 0
}
for r in rows:
    cs = r["清理策略"] or ""
    if "按年创建历史表" in cs or "历史表" in cs and "YYYY" in cs:
        patterns["按年创建历史表"] += 1
    elif "失效超过1年" in cs:
        patterns["失效超过1年"] += 1
    elif "保留" in cs and ("月" in cs or "年" in cs):
        patterns["保留N月/N年数据"] += 1
    elif cs:
        patterns["其他"] += 1
for p, c in patterns.items():
    print(f"  {p}: {c}张")

# 按模块+数据库分组输出完整清单
print("\n" + "=" * 80)
print("【完整清单 - 按数据库+模块分组】")
print("=" * 80)

groups = defaultdict(list)
for r in rows:
    key = f"{r['所属数据库']} - {r['所属模块']}"
    groups[key].append(r)

for group_key in sorted(groups.keys()):
    group_rows = groups[group_key]
    print(f"\n■ {group_key} ({len(group_rows)}张)")
    for r in group_rows:
        cs = (r["清理策略"] or "(空)").replace("\n", " | ")[:80]
        ar = r["归档策略"] or "(空)"
        print(f"  - {r['表名_英文']} | {r['表名_中文']} | 清理:{cs[:60]}... | 归档:{ar}")

# 保存为结构化JSON供文档生成使用
summary = {
    "total_tables": len(rows),
    "by_database": dict(db_counter),
    "by_module": dict(module_counter),
    "by_owner": dict(owner_counter),
    "by_clean_flag": dict(clean_counter),
    "by_archive_strategy": {k: len(v) for k, v in archive_groups.items()},
    "clean_patterns": patterns,
    "groups": {k: [{"表名": r["表名_英文"], "中文名": r["表名_中文"], "清理策略": r["清理策略"], "归档策略": r["归档策略"], "责任人": r["责任人"], "序号": r["序号"]} for r in v] for k, v in groups.items()}
}

output_path = r"e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\cleanup_archive_summary.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"\n\n统计摘要已保存到: {output_path}")
