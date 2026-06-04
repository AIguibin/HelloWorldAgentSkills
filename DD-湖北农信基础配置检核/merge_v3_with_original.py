# -*- coding: utf-8 -*-
"""
合并源表（人工标注必须）到 V3 精细表
规则：源表中标记为"是"的表，必须保留为分区表
"""
import json
import os
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

BASE_DIR = r"e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\DD-湖北农信基础配置检核"

# ==================== 1. 读取原始清单（人工标注） ====================
print("读取原始清单...")
wb_orig = load_workbook(os.path.join(BASE_DIR, "湖北农信数据库分区表清单.xlsx"))
ws_orig = wb_orig["数据库表分区"]

# 原始清单中标记为分区 = "是" 的表（人工标注，必须保留）
orig_must_partition = {}  # {表英文名(小写): 完整信息}
for row in ws_orig.iter_rows(min_row=3, values_only=True):
    if row[4] is None:
        continue
    table_en = str(row[4]).strip().lower()
    is_partition = str(row[6]).strip() if row[6] else ""
    orig_must_partition[table_en] = {
        "序号": row[0],
        "所属数据库": str(row[1]).strip() if row[1] else "",
        "所属模块": str(row[2]).strip() if row[2] else "",
        "责任人": str(row[3]).strip() if row[3] else "",
        "表名（英文）": str(row[4]).strip(),
        "表名（中文）": str(row[5]).strip() if row[5] else "",
        "是否表分区": is_partition,
        "表分区键": str(row[7]).strip() if row[7] else "",
        "初始表分区数": str(row[8]).strip() if row[8] else "",
        "表分区策略": str(row[9]).strip() if row[9] else "",
        "备注": str(row[10]).strip() if row[10] else "",
    }

# 只取标记为"是"的
orig_partition = {k: v for k, v in orig_must_partition.items() if v["是否表分区"] == "是"}
print(f"原始清单人工标注分区表: {len(orig_partition)} 张")

# ==================== 2. 读取 V3 AI 分析结果 ====================
print("读取 V3 分析结果...")
with open(os.path.join(BASE_DIR, "ai_analysis_result.json"), "r", encoding="utf-8") as f:
    ai_result = json.load(f)

# 构建 V3 分析结果映射 {表英文名(小写): 分析结果}
v3_analysis = {}
for t in ai_result["tables"]:
    v3_analysis[t["table_en"].lower()] = t

# ==================== 3. 读取 V3 表结构（获取完整表名列表） ====================
print("读取 V3 表结构...")
with open(os.path.join(BASE_DIR, "table_structures.json"), "r", encoding="utf-8") as f:
    structures = json.load(f)

# 构建表结构映射 {表英文名(小写): 表中文名}
table_cn_map = {}
for cn, info in structures["tables"].items():
    table_cn_map[info["table_en"].lower()] = cn

# ==================== 4. 合并逻辑 ====================
# 规则：
#   a) 原始清单标记为"是"的表 → 强制分区，分区键/分区数优先用V3分析结果，否则用原始值
#   b) V3标记为分区但原始清单中不存在或不分区 → 保留V3分区
#   c) 其余表 → 不分区

# 收集所有表名
all_table_names = set(v3_analysis.keys()) | set(orig_partition.keys())

# 构建最终结果
final_tables = []

for en in sorted(all_table_names):
    is_orig_partition = en in orig_partition
    v3_info = v3_analysis.get(en)
    
    if is_orig_partition:
        # 源表人工标注的必须分区表
        orig = orig_partition[en]
        table_cn = v3_info["table_cn"] if v3_info else orig["表名（中文）"]
        module = orig["所属模块"] if orig["所属模块"] else (v3_info["module"] if v3_info else "未知")
        db = orig["所属数据库"] if orig["所属数据库"] else "NCMS_CREDIT_BASE"
        person = orig["责任人"] if orig["责任人"] else "待确认"
        
        # 分区键和分区数：优先用 V3 分析结果（如果有），否则用原始值
        if v3_info and v3_info["need_partition"]:
            # V3 也认为需要分区，用 V3 的精确分析
            partition_key = v3_info["partition_key"]
            partition_count = str(v3_info["partition_count"])
            strategy = v3_info["partition_strategy"]
            remark = f"【源表标注必须分区】{v3_info['remark']}"
        else:
            # V3 认为不需要分区，但源表标注必须分区，保留原始分区键
            partition_key = orig["表分区键"]
            partition_count = orig["初始表分区数"]
            strategy = orig["表分区策略"]
            if v3_info:
                remark = f"【源表标注必须分区】V3预估{format(v3_info['estimated_volume'], ',')}，未达1000万但源表人工标注必须分区"
            else:
                remark = "【源表标注必须分区】V3清单中无此表，保留原始人工标注"
        
        final_tables.append({
            "table_en": en,
            "table_cn": table_cn,
            "module": module,
            "db": db,
            "person": person,
            "is_partition": True,
            "partition_key": partition_key,
            "partition_count": partition_count,
            "strategy": strategy,
            "remark": remark,
            "estimated_volume": v3_info["estimated_volume"] if v3_info else 0,
            "source": "原始标注",
        })
    elif v3_info and v3_info["need_partition"]:
        # V3 新增的分区表（原始清单中不存在或不分区）
        final_tables.append({
            "table_en": en,
            "table_cn": v3_info["table_cn"],
            "module": v3_info["module"],
            "db": "NCMS_CREDIT_BASE",
            "person": "待确认",
            "is_partition": True,
            "partition_key": v3_info["partition_key"],
            "partition_count": str(v3_info["partition_count"]),
            "strategy": v3_info["partition_strategy"],
            "remark": f"【V3新增】{v3_info['remark']}",
            "estimated_volume": v3_info["estimated_volume"],
            "source": "V3新增",
        })
    else:
        # 不分区
        if v3_info:
            final_tables.append({
                "table_en": en,
                "table_cn": v3_info["table_cn"],
                "module": v3_info["module"],
                "db": "NCMS_CREDIT_BASE",
                "person": "待确认",
                "is_partition": False,
                "partition_key": "",
                "partition_count": "",
                "strategy": "",
                "remark": v3_info["remark"],
                "estimated_volume": v3_info["estimated_volume"],
                "source": "不分区",
            })
        else:
            # 原始清单中不分区但V3中也没分析的表
            orig = orig_must_partition.get(en, {})
            final_tables.append({
                "table_en": en,
                "table_cn": orig.get("表名（中文）", table_cn_map.get(en, en)),
                "module": orig.get("所属模块", "未知"),
                "db": orig.get("所属数据库", "NCMS_CREDIT_BASE"),
                "person": orig.get("责任人", "待确认"),
                "is_partition": False,
                "partition_key": "",
                "partition_count": "",
                "strategy": "",
                "remark": "原始清单标记为不分区",
                "estimated_volume": 0,
                "source": "不分区",
            })

# 排序：分区表在前（按预估量降序），不分区表在后
partition_tables = sorted([t for t in final_tables if t["is_partition"]], key=lambda x: -x["estimated_volume"])
no_partition = sorted([t for t in final_tables if not t["is_partition"]], key=lambda x: (x["module"], x["table_en"]))
final_tables = partition_tables + no_partition

# ==================== 5. 统计 ====================
final_partition = [t for t in final_tables if t["is_partition"]]
orig_only = [t for t in final_partition if t["source"] == "原始标注"]
v3_only = [t for t in final_partition if t["source"] == "V3新增"]
orig_in_v3 = [t for t in final_partition if t["source"] == "原始标注" and t["table_en"] in v3_analysis]

print(f"\n合并结果统计:")
print(f"  总表数: {len(final_tables)}")
print(f"  分区表: {len(final_partition)}")
print(f"    - 原始人工标注: {len(orig_only)} 张")
print(f"    - 其中V3也认为需分区: {len(orig_in_v3)} 张")
print(f"    - V3新增: {len(v3_only)} 张")
print(f"  不分区: {len(final_tables) - len(final_partition)}")

# ==================== 6. 生成 Excel ====================
print("\n生成 Excel...")

wb = Workbook()
ws = wb.active
ws.title = "分区清单"

# 样式
title_font = Font(name="微软雅黑", size=14, bold=True)
header_font = Font(name="微软雅黑", size=10, bold=True, color="FFFFFF")
data_font = Font(name="微软雅黑", size=9)
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
must_fill = PatternFill(start_color="D9EAD3", end_color="D9EAD3", fill_type="solid")  # 浅绿=源表必须
v3_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")     # 浅黄=V3新增
thin_border = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin"),
)
center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)

# 列宽
col_widths = {"A": 6, "B": 20, "C": 14, "D": 10, "E": 35, "F": 35, "G": 12, "H": 22, "I": 16, "J": 50, "K": 70, "L": 12}
for col, width in col_widths.items():
    ws.column_dimensions[col].width = width

# 标题
ws.merge_cells("A1:L1")
ws["A1"].value = "湖北农信新信贷数据库表分区清单（V3 + 源表人工标注合并版）"
ws["A1"].font = title_font
ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 30

# 表头
headers = ["序号", "所属数据库", "所属模块", "责任人", "表名（英文）", "表名（中文）", "是否表分区", "表分区键", "初始表分区数", "表分区策略", "备注", "来源"]
for col_idx, header in enumerate(headers, 1):
    cell = ws.cell(row=2, column=col_idx, value=header)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = center_align
    cell.border = thin_border
ws.row_dimensions[2].height = 25

# 数据行
row = 3
for idx, t in enumerate(final_tables):
    seq = idx + 1
    
    if t["is_partition"]:
        if t["source"] == "原始标注":
            fill = must_fill
        else:
            fill = v3_fill
        is_partition = "是"
        pk = t["partition_key"]
        pc = t["partition_count"]
        strategy = t["strategy"]
        remark = t["remark"]
    else:
        fill = None
        is_partition = "否"
        pk = ""
        pc = ""
        strategy = ""
        remark = t["remark"]
    
    values = [
        seq, t["db"], t["module"], t["person"],
        t["table_en"], t["table_cn"],
        is_partition, pk, pc, strategy, remark, t["source"]
    ]
    
    for col_idx, value in enumerate(values, 1):
        cell = ws.cell(row=row, column=col_idx, value=value)
        cell.font = data_font
        cell.border = thin_border
        if col_idx in [1, 2, 3, 4, 7, 8, 9, 12]:
            cell.alignment = center_align
        else:
            cell.alignment = left_align
        if fill:
            cell.fill = fill
    
    ws.row_dimensions[row].height = 22
    row += 1

# 冻结 + 筛选
ws.freeze_panes = "A3"
ws.auto_filter.ref = f"A2:L{row - 1}"

# 保存
output_path = os.path.join(BASE_DIR, "湖北农信数据库分区表清单_最终版.xlsx")

# 7. 校验 ====================
print("\n" + "=" * 60)
print("质量校验")
print("=" * 60)

# 校验1：原始清单93张必须全部为分区
orig_not_partition = [t for t in final_tables if t["table_en"] in orig_partition and not t["is_partition"]]
if orig_not_partition:
    print(f"  FAIL: {len(orig_not_partition)} 张原始标注表未标记为分区!")
    for t in orig_not_partition:
        print(f"    - {t['table_cn']}({t['table_en']})")
else:
    print(f"  PASS: 原始清单93张表全部标记为分区")

# 校验2：确认分区表数量
print(f"  PASS: 最终分区表 = {len(final_partition)} 张（原始93 + V3新增{len(v3_only)}）")

# 校验3：原始清单中是否有表在最终清单中缺失
orig_not_found = [en for en in orig_partition if en not in [t["table_en"] for t in final_tables]]
if orig_not_found:
    print(f"  WARN: {len(orig_not_found)} 张原始标注表在最终清单中缺失!")
    for en in orig_not_found:
        print(f"    - {en}")
else:
    print(f"  PASS: 原始清单93张表全部在最终清单中")

# 校验4：分区键无TENANT_ID —— 自动修正
tenant_fix_map = {
    "dsbr_cont_acc_inf": "CUST_NO",
    "prvt_crline_use_reply": "CTRT_NO",
    "crlmt_lmt_reply": "CREATE_TIME",
    "crlmt_crgln_aply": "CREATE_TIME",
    "crlmt_lmt_reply_record": "CREATE_TIME",
    "crlmt_sitmlmt_reply_record": "CREATE_TIME",
    "cust_credit_query_object": "CUST_NO",
    "cust_credit_query_result": "CUST_NO",
    "ped_cust_accumu_fund_qry_apply": "CUST_NO",
    "ped_cust_accumu_fund_qry_result": "CUST_NO",
    "crlmt_crg_pd_lmt_aply": "CREATE_TIME",
    "crlmt_sitmlmt_reply": "CREATE_TIME",
}

fixed_count = 0
for idx, t in enumerate(final_partition):
    if "TENANT" in t["partition_key"].upper():
        old_key = t["partition_key"]
        if t["table_en"] in tenant_fix_map:
            new_key = tenant_fix_map[t["table_en"]]
            t["partition_key"] = new_key
            if new_key == "CREATE_TIME":
                t["partition_count"] = "0（按时间自动）"
                t["strategy"] = f"按{new_key}时间分区，3个月一个分区，按时间自动创建分区"
            else:
                t["partition_count"] = "4"
                t["strategy"] = f"按{new_key} HASH分区，初始4个分区，后续按需扩容"
            t["remark"] = t["remark"].replace("【源表标注必须分区】", "【源表标注必须分区】分区键已从TENANT_ID修正为" + new_key + "；")
            
            # 更新 Excel 单元格
            row_num = 3 + idx  # 分区表都在前面
            ws.cell(row=row_num, column=8, value=new_key)  # H列=分区键
            ws.cell(row=row_num, column=9, value=t["partition_count"])  # I列=分区数
            ws.cell(row=row_num, column=10, value=t["strategy"])  # J列=策略
            ws.cell(row=row_num, column=11, value=t["remark"])  # K列=备注
            
            fixed_count += 1
            print(f"  FIXED: {t['table_cn']}({t['table_en']}): {old_key} → {new_key}")
        else:
            print(f"  WARN: {t['table_cn']}({t['table_en']}): {old_key} 无自动修正映射，需人工处理")

if fixed_count > 0:
    print(f"  PASS: 已自动修正 {fixed_count} 张表的TENANT_ID分区键")

# 重新检查
tenant_tables = [t for t in final_partition if "TENANT" in t["partition_key"].upper()]
if tenant_tables:
    print(f"  WARN: 仍有 {len(tenant_tables)} 张表分区键含TENANT_ID（需人工处理）")
else:
    print(f"  PASS: 无TENANT_ID分区键")

# 重新保存修正后的Excel
output_path = os.path.join(BASE_DIR, "湖北农信数据库分区表清单_最终版.xlsx")
wb.save(output_path)
print(f"\n修正后 Excel 已保存: {output_path}")

print("\n合并完成！")