# -*- coding: utf-8 -*-
"""
Task 6: 质量校验
"""
import json
import math
import os

BASE_DIR = r"e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\DD-湖北农信基础配置检核"

with open(os.path.join(BASE_DIR, "ai_analysis_result.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

tables = data["tables"]
partition_tables = [t for t in tables if t["need_partition"]]
no_partition_tables = [t for t in tables if not t["need_partition"]]

errors = []
warnings = []

print("=" * 60)
print("质量校验报告")
print("=" * 60)

# 1. 校验：G列="是" 的表，预估数据量 > 1000万
print("\n[校验1] 分区表数据量 > 1000万")
for t in partition_tables:
    if t["estimated_volume"] <= 10_000_000:
        errors.append(f"{t['table_cn']}({t['table_en']}): 标记为分区但预估量={t['estimated_volume']:,} <= 1000万")
print(f"  通过: {len(partition_tables)}张分区表全部 > 1000万" if not any(t['estimated_volume'] <= 10_000_000 for t in partition_tables) else f"  失败: {len([t for t in partition_tables if t['estimated_volume'] <= 10_000_000])}张表不满足")

# 2. 校验：G列="否" 的表，预估数据量 ≤ 1000万
print("\n[校验2] 非分区表数据量 ≤ 1000万")
over_threshold = [t for t in no_partition_tables if t["estimated_volume"] > 10_000_000]
if over_threshold:
    for t in over_threshold:
        errors.append(f"{t['table_cn']}({t['table_en']}): 标记为不分区但预估量={t['estimated_volume']:,} > 1000万")
    print(f"  失败: {len(over_threshold)}张表数据量超过1000万但未分区")
else:
    print(f"  通过: 所有{len(no_partition_tables)}张非分区表 ≤ 1000万")

# 3. 校验：分区键无 TENANT_ID
print("\n[校验3] 分区键无 TENANT_ID")
tenant_id_tables = [t for t in partition_tables if "TENANT" in t.get("partition_key", "").upper()]
if tenant_id_tables:
    for t in tenant_id_tables:
        errors.append(f"{t['table_cn']}({t['table_en']}): 分区键={t['partition_key']}包含TENANT_ID")
    print(f"  失败: {len(tenant_id_tables)}张表使用TENANT_ID")
else:
    print(f"  通过: 无TENANT_ID分区键")

# 4. 校验：分区数 = CEILING(预估量/300万)，≤ 50
print("\n[校验4] 分区数计算正确 (CEILING(预估量/300万), ≤ 50)")
for t in partition_tables:
    pk = t["partition_key"]
    pc = t["partition_count"]
    ev = t["estimated_volume"]
    bt = t["business_type"]
    
    # 日志类时间分区表，分区数应为0
    if ("日志" in bt or "审计" in bt) and pk in ["CREATE_TIME", "CRT_TIME", "CRT_DT", "CREATE_DATE"]:
        if str(pc) != "0（按时间自动）" and pc != 0:
            errors.append(f"{t['table_cn']}({t['table_en']}): 日志类时间分区表，分区数应为0，实际={pc}")
    else:
        expected = math.ceil(ev / 3_000_000)
        expected = min(expected, 50)
        try:
            actual = int(pc)
        except (ValueError, TypeError):
            actual = 0
        if actual != expected:
            errors.append(f"{t['table_cn']}({t['table_en']}): 分区数={actual}，期望={expected} (CEILING({ev:,}/3,000,000))")
print(f"  通过: 所有分区表分区数计算正确" if not any(t for t in partition_tables if "分区数=" in str(errors)) else "  有错误")

# 5. 校验：单分区 ≤ 300万
print("\n[校验5] 单分区数据量 ≤ 300万")
for t in partition_tables:
    ev = t["estimated_volume"]
    pc = t["partition_count"]
    if pc == 0 or str(pc) == "0（按时间自动）":
        continue  # 时间分区表跳过
    try:
        actual_pc = int(pc)
    except (ValueError, TypeError):
        continue
    if actual_pc > 0:
        per_partition = ev / actual_pc
        if per_partition > 3_000_000:
            errors.append(f"{t['table_cn']}({t['table_en']}): 单分区={per_partition:,.0f}行 > 300万")
print(f"  通过: 所有分区表单分区 ≤ 300万" if not any("单分区" in str(e) for e in errors) else "  有错误")

# 6. 抽查10张表
print("\n[校验6] 抽查10张表验证AI分析逻辑")
spot_checks = [
    # 大表（应该分区）
    ("ecif_p_addr_info", "客户信息类", True),
    ("prvt_ctr_inf", "合同类", True),
    ("iou_inf", "合同类", True),
    ("arch_info", "档案类", True),
    ("loan_rt_labour_gen_chk", "任务类", True),
    # 小表（不应该分区）
    ("base_ddct", "字典类", False),
    ("sys_audit_log", "日志/审计类", False),  # 新系统预估2M，不分区
    ("act_hi_actinst", "工作流历史类", False),  # 新系统预估3M，不分区
    ("bat_core_msg_inf", "消息通知类", False),  # 新系统预估5M，不分区
    ("prod_elmt_dtl", "产品配置类", False),
]

for en, expected_type, expected_partition in spot_checks:
    found = [t for t in tables if t["table_en"].lower() == en.lower()]
    if found:
        t = found[0]
        type_ok = expected_type in t["business_type"]
        part_ok = t["need_partition"] == expected_partition
        status = "✓" if (type_ok and part_ok) else "✗"
        issues = []
        if not type_ok:
            issues.append(f"类型不匹配: 期望={expected_type}, 实际={t['business_type']}")
        if not part_ok:
            issues.append(f"分区判断不匹配: 期望={'是' if expected_partition else '否'}, 实际={'是' if t['need_partition'] else '否'}")
        print(f"  {status} {t['table_cn']}({en}): 类型={t['business_type']}, 分区={'是' if t['need_partition'] else '否'}, 预估={t['estimated_volume']:,}行")
        if issues:
            for issue in issues:
                warnings.append(f"{en}: {issue}")
    else:
        warnings.append(f"未找到表: {en}")

# 7. 汇总统计
print("\n" + "=" * 60)
print("汇总统计")
print("=" * 60)
print(f"总表数: {len(tables)}")
print(f"分区表: {len(partition_tables)} ({len(partition_tables)/len(tables)*100:.1f}%)")
print(f"不分区: {len(no_partition_tables)} ({len(no_partition_tables)/len(tables)*100:.1f}%)")
print(f"错误数: {len(errors)}")
print(f"警告数: {len(warnings)}")

if errors:
    print("\n错误详情:")
    for e in errors:
        print(f"  - {e}")

if warnings:
    print("\n警告详情:")
    for w in warnings:
        print(f"  - {w}")

print("\n" + "=" * 60)
if errors:
    print("校验未通过！请修复上述错误。")
else:
    print("所有校验通过！")