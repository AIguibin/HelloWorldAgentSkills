#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 partition_v3_result.json 中的三个问题：
1. 日志/审计类表（LOG、ACT_HI_、ACT_RU_、MSG_/MESSAGE）的估算修正
2. 备注中"预估3-5年"字段显示实际数值而非业务类型标签
3. 重新生成 JSON 和 Excel 输出
"""
import json, re, math
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

BASE_DIR = Path(__file__).parent
RESULT_JSON = BASE_DIR / "partition_v3_result.json"
RESULT_EXCEL = BASE_DIR / "湖北农信数据库分区表清单_精细化版.xlsx"

# ============================================================
# 修复1: 日志/审计类表强制估算规则
# ============================================================
# 对于未匹配生产数据的表（备注含"新系统新增"），按表名强制估算
def get_forced_estimate(table_name: str) -> tuple:
    """
    返回 (预估3-5年数值, 业务类型, 是否强制分区键为CREATE_TIME)
    返回 (None, None, False) 表示不需要强制修正
    """
    tn = table_name.lower()

    # 表名含 LOG → 5000万
    if 'log' in tn:
        return (50_000_000, "日志/审计类", True)

    # 表名含 ACT_HI_ → 3000万（Activiti历史表）
    if tn.startswith('act_hi_'):
        return (30_000_000, "日志/审计类", True)

    # 表名含 ACT_RU_ → 500万（Activiti运行时表，数据量较小）
    if tn.startswith('act_ru_'):
        return (5_000_000, "日志/审计类", True)

    # 表名含 MSG_ 或 MESSAGE → 2000万
    if 'msg_' in tn or 'message' in tn:
        return (20_000_000, "消息通知类", True)

    return (None, None, False)


# ============================================================
# 修复2: 备注格式修正
# ============================================================
def fix_remarks_format(notes: str, estimated_value: int, is_matched: bool) -> str:
    """
    修复备注中的"预估3-5年"字段，确保显示实际数值而非业务类型标签。
    同时修复其他可能的问题。
    """
    # 替换"预估3-5年：XXX（估算值=NNN）" → "预估3-5年：NNN"
    notes = re.sub(
        r'预估3-5年：[^；]+（估算值=(\d+)）',
        r'预估3-5年：\1',
        notes
    )

    # 替换"预估3-5年：XXX"（非数字）→ "预估3-5年：estimated_value"
    # 匹配"预估3-5年："后面跟的不是数字的情况
    def replace_estimate(m):
        prefix = m.group(1)
        value = m.group(2)
        if not value.isdigit():
            # 非数字，替换为实际数值
            return f"{prefix}{estimated_value}"
        return m.group(0)

    notes = re.sub(r'(预估3-5年：)([^；]+)', replace_estimate, notes)

    return notes


def fix_table_entry(entry: dict) -> dict:
    """对单个表条目进行修复，返回修改后的条目和是否被修改"""
    table_name = entry.get("表名（英文）", "")
    notes = entry.get("备注", "")
    is_partition = entry.get("是否表分区", "否") == "是"
    is_unmatched = "新系统新增" in notes
    is_matched = not is_unmatched

    modified = False

    # ===== 修复1: 对未匹配的表应用强制估算规则 =====
    if is_unmatched:
        forced_est, forced_type, use_time_key = get_forced_estimate(table_name)
        if forced_est is not None:
            needs_partition = forced_est > 10_000_000  # 1000万阈值

            if needs_partition and not is_partition:
                # 当前标记为"不分区"但应该为"是"
                entry["是否表分区"] = "是"

                if use_time_key:
                    entry["表分区键"] = "CREATE_TIME"
                    entry["初始表分区数"] = "0（按时间自动）"
                    entry["表分区策略"] = "按CREATE_TIME时间分区，3个月一个分区，保留3年数据，按时间自动创建分区"
                else:
                    pcount = math.ceil(forced_est / 3_000_000)
                    pcount = min(pcount, 50)
                    entry["表分区键"] = "CREATE_TIME"
                    entry["初始表分区数"] = str(pcount)
                    entry["表分区策略"] = f"按CREATE_TIME HASH分区，初始{pcount}个分区，后续按需扩容"

                # 重建备注
                notes_parts = [
                    f"表类型：{forced_type}",
                    f"预估3-5年：{forced_est}",
                    f"分区键来源：强制规则（{table_name}为日志/审计类表，数据持续增长，按表名强制估算）",
                    "老系统表名：新系统新增",
                ]
                entry["备注"] = "；".join(notes_parts)
                modified = True

            elif not needs_partition:
                # ACT_RU_ 等：5M < 10M，仍为"不分区"，但修正备注中的数值
                if is_partition:
                    # 不应该出现，但以防万一
                    pass
                else:
                    # 修正备注中的预估数值
                    notes = re.sub(
                        r'预估3-5年：[^；]+',
                        f'预估3-5年：{forced_est}',
                        notes
                    )
                    entry["备注"] = notes
                    modified = True

    # ===== 修复2: 对已分区的表修正备注格式 =====
    if is_partition:
        old_notes = entry.get("备注", "")
        # 提取估算值
        m = re.search(r'估算值=(\d+)', old_notes)
        if m:
            estimated_value = int(m.group(1))
        else:
            # 尝试从备注中提取数字
            m2 = re.search(r'预估3-5年：(\d+)', old_notes)
            if m2:
                estimated_value = int(m2.group(1))
            else:
                estimated_value = 0

        # 修正备注
        new_notes = fix_remarks_format(old_notes, estimated_value, is_matched)
        if new_notes != old_notes:
            entry["备注"] = new_notes
            modified = True

    # ===== 修复2: 对不分区的表也修正备注格式 =====
    if not is_partition:
        old_notes = entry.get("备注", "")
        # 提取估算值
        m = re.search(r'当前数据量：(\d+)', old_notes)
        m2 = re.search(r'预估3-5年：(\d+)', old_notes)
        if m2:
            estimated_value = int(m2.group(1))
        elif m:
            # 有当前数据量，尝试估算
            estimated_value = int(m.group(1))
        else:
            # 尝试从"预估3-5年：XXX"中提取
            m3 = re.search(r'预估3-5年：([^；]+)', old_notes)
            if m3:
                val_str = m3.group(1)
                if val_str.isdigit():
                    estimated_value = int(val_str)
                else:
                    estimated_value = 0
            else:
                estimated_value = 0

        new_notes = fix_remarks_format(old_notes, estimated_value, is_matched)
        if new_notes != old_notes:
            entry["备注"] = new_notes
            modified = True

    return (entry, modified)


# ============================================================
# Excel 生成（复用V3格式）
# ============================================================
def generate_excel(all_entries: list, stats: dict):
    wb = Workbook()
    ws = wb.active
    ws.title = "分区清单"

    # 公共样式
    header_font = Font(name="微软雅黑", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell_font = Font(name="微软雅黑", size=10)
    cell_align = Alignment(vertical="center", wrap_text=True)
    cell_align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )
    yes_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")

    # 第1行：标题
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=11)
    title_cell = ws.cell(row=1, column=1, value="湖北农信新信贷数据库表分区清单")
    title_cell.font = Font(name="微软雅黑", size=16, bold=True, color="1F4E79")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    # 第2行：表头
    headers = ["序号", "所属数据库", "所属模块", "责任人", "表名（英文）",
               "表名（中文）", "是否表分区", "表分区键", "初始表分区数",
               "表分区策略(迁移数据量，8-10年增长量)", "备注"]

    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=2, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border
    ws.row_dimensions[2].height = 32

    # 第3行起：数据
    for row_idx, entry in enumerate(all_entries, start=3):
        row_data = [
            entry["序号"],
            entry["所属数据库"],
            entry["所属模块"],
            entry["责任人"],
            entry["表名（英文）"],
            entry["表名（中文）"],
            entry["是否表分区"],
            entry["表分区键"],
            entry["初始表分区数"],
            entry["表分区策略"],
            entry["备注"],
        ]

        is_yes = entry["是否表分区"] == "是"

        for col, val in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col, value=val if val is not None else "")
            cell.font = cell_font
            cell.border = thin_border
            if col in (1, 7):
                cell.alignment = cell_align_center
            else:
                cell.alignment = cell_align
            if is_yes:
                cell.fill = yes_fill

        ws.row_dimensions[row_idx].height = 22 if not is_yes else 28

    # 列宽
    col_widths = [6, 22, 14, 8, 34, 28, 10, 18, 12, 42, 60]
    for col, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(col)].width = w

    # 冻结窗格
    ws.freeze_panes = "A3"

    # 自动筛选
    ws.auto_filter.ref = f"A2:K{2 + len(all_entries)}"

    wb.save(RESULT_EXCEL)
    print(f"Excel 结果已生成：{RESULT_EXCEL.name}")


# ============================================================
# 主处理
# ============================================================
def main():
    print("=" * 60)
    print("  修复 partition_v3_result.json")
    print("=" * 60)

    # 1. 加载数据
    with open(RESULT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    old_stats = data["stats"]
    old_partition_count = old_stats["需分区"]
    old_total = old_stats["总表数"]

    print(f"\n[原统计] 总表数：{old_total}，需分区：{old_partition_count}，不分区：{old_stats['不分区']}")

    # 2. 处理所有表
    all_tables = data["partition_tables"] + data["no_partition_tables"]
    print(f"\n[处理] 共 {len(all_tables)} 张表，逐表检查修复...")

    modified_count = 0
    promoted_from_no = []  # 从不分区提升为分区
    notes_fixed_count = 0  # 仅修正备注格式

    for entry in all_tables:
        original_partition = entry.get("是否表分区", "否")
        entry, mod = fix_table_entry(entry)
        if mod:
            modified_count += 1
            new_partition = entry.get("是否表分区", "否")
            if original_partition == "否" and new_partition == "是":
                promoted_from_no.append(entry["表名（英文）"])
            elif original_partition == "是" and new_partition == "是":
                notes_fixed_count += 1
            elif original_partition == "否" and new_partition == "否":
                notes_fixed_count += 1

    print(f"  修改了 {modified_count} 张表")
    print(f"  其中从不分区提升为分区：{len(promoted_from_no)} 张")
    print(f"  仅修正备注格式：{notes_fixed_count} 张")

    if promoted_from_no:
        print(f"\n  提升为分区的表：")
        for name in promoted_from_no:
            print(f"    - {name}")

    # 3. 重新排序和编号
    # 分区表在前，不分区表在后
    partition_tables = [e for e in all_tables if e["是否表分区"] == "是"]
    no_partition_tables = [e for e in all_tables if e["是否表分区"] == "否"]

    # 分区表保持原有相对顺序（已匹配的在前，新增的在后的逻辑隐含在原始顺序中）
    all_entries = partition_tables + no_partition_tables

    # 重新编号
    for idx, entry in enumerate(all_entries, start=1):
        entry["序号"] = idx

    new_partition_count = len(partition_tables)
    new_no_partition_count = len(no_partition_tables)

    # 4. 生成新的 JSON
    new_stats = {
        "总表数": len(all_entries),
        "需分区": new_partition_count,
        "不分区": new_no_partition_count,
        "匹配生产数据": old_stats.get("匹配生产数据", 0),
        "新系统新增": old_stats.get("新系统新增", 0),
    }
    # 修正统计：提升的表从"新系统新增"中移出（它们仍属于新系统新增，但统计不变）
    new_stats["匹配生产数据"] = new_stats["匹配生产数据"]
    new_stats["新系统新增"] = new_stats["新系统新增"]

    json_output = {
        "stats": new_stats,
        "partition_tables": partition_tables,
        "no_partition_tables": no_partition_tables,
    }

    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)
    print(f"\nJSON 结果已更新：{RESULT_JSON.name}")

    # 5. 生成 Excel
    generate_excel(all_entries, new_stats)

    # 6. 统计输出
    print(f"\n{'='*60}")
    print(f"  修复前后对比：")
    print(f"{'='*60}")
    print(f"  总表数：          {old_total} → {len(all_entries)}（不变）")
    print(f"  需分区表数：      {old_partition_count} → {new_partition_count}（+{new_partition_count - old_partition_count}）")
    print(f"  不分区表数：      {old_stats['不分区']} → {new_no_partition_count}（-{old_stats['不分区'] - new_no_partition_count}）")
    print(f"  修改表数：        {modified_count}")
    print(f"  其中提升为分区：  {len(promoted_from_no)}")

    # 7. 打印分区表清单
    print(f"\n{'='*60}")
    print(f"  需要分区的 {new_partition_count} 张表明细：")
    print(f"{'='*60}")
    for p in partition_tables:
        print(f"  [{p['序号']:>4}] {p['表名（英文）']:<40s} 分区键={p['表分区键']:<18s} 分区数={p['初始表分区数']}")

    print(f"\n{'='*60}")
    print(f"  修复完成！")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()