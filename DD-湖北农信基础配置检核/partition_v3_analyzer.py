#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
湖北农信新信贷数据库表分区精细化分析（V3）
基于 partition_v2_intermediate.json 进行精细化的逐表分区分析
"""
import json, math, re
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "partition_v2_intermediate.json"
PRIOR_FILE = BASE_DIR / "partition_analysis_data.json"
RESULT_JSON = BASE_DIR / "partition_v3_result.json"
RESULT_EXCEL = BASE_DIR / "湖北农信数据库分区表清单_精细化版.xlsx"

THRESHOLD = 10_000_000          # 1000万
MAX_PARTITION_COUNT = 50
ONE_PARTITION_SIZE = 3_000_000  # 300万

# ============================================================
# 规则4：分区键优先级
# ============================================================
PARTITION_KEY_PRIORITY = {
    # 规则4：标准业务类型
    "客户信息类":         ["CUST_NO", "CUST_INTL_SEQ_NO", "ID_CRD_NO"],
    "合同/借据类":        ["CTRT_NO", "BUS_NO", "IOU_NO"],
    "贷后检查/任务类":    ["TSK_NO", "CHK_TSK_NO", "CUST_NO"],
    "贷后检查/监控类":    ["TSK_NO", "CHK_TSK_NO", "CUST_NO"],
    "申请/审批类":        ["APLY_NO", "BUS_NO", "DOC_NO"],
    "日志/审计类":        ["CREATE_TIME", "CRT_TIME", "BIZ_DATE"],
    "营销类":             ["MKT_TSK_NO", "DOC_NO", "CUST_NO"],
    "征信查询类":         ["BUS_NO", "QUERY_NO", "APLY_NO"],
    "额度类":             ["LMT_NO", "CRLMT_NO", "CUST_NO"],
    "档案类":             ["ARS_NO", "DOC_NO", "ELC_MTRLS_NO"],
    # 估算类型映射（给未匹配表的估算类型也提供分区键优先级）
    "客户数据类":         ["CUST_NO", "CUST_INTL_SEQ_NO", "ID_CRD_NO"],
    "合同/借据/额度类":   ["CTRT_NO", "BUS_NO", "IOU_NO"],
    "文件/文档类":        ["ARS_NO", "DOC_NO", "ELC_MTRLS_NO"],
    "消息通知类":         ["CREATE_TIME", "CRT_TIME", "BIZ_DATE"],
    "流程日志类":         ["CREATE_TIME", "CRT_TIME", "BIZ_DATE"],
    "流程实例类":         ["BUS_NO", "CUST_NO", "DOC_NO"],
    "统计汇总类":         ["BUS_NO", "CUST_NO", "DOC_NO"],
    "押品管理类":         ["CLTR_NO", "BUS_NO", "CUST_NO"],
    # 默认
    "其他":               ["BUS_NO", "CUST_NO", "DOC_NO"],
    "其他/默认":          ["BUS_NO", "CUST_NO", "DOC_NO"],
}

# 日志/审计类额外时间字段（用于日志表的扩展匹配）
LOG_TIME_FIELDS = ["CREATE_TIME", "CRT_TIME", "BIZ_DATE", "OPR_TIME", "LOG_TIME",
                   "HDL_TIME", "PROC_TIME", "EXEC_TIME", "GEN_TIME", "OCCUR_TIME",
                   "CRT_DT_TM", "CRT_DT", "MSGRP_GEN_TM", "GEN_TM", "SEND_TIME",
                   "RECV_TIME", "UPDATE_TIME", "MODIFY_TIME", "UPD_TIME"]

# ============================================================
# 表类型估算规则（用于未匹配生产数据的表）
# ============================================================
def detect_business_type(table_name: str, field_count: int) -> str:
    """从表名检测更精确的业务类型"""
    tn = table_name.lower()

    # 配置/字典/参数/代码类
    config_patterns = ["config", "conf", "param", "dict", "code", "catalog",
                       "rule", "template", "seq", "sys_", "base_"]
    for p in config_patterns:
        if p in tn:
            return "配置/字典/参数/代码类"

    # 用户/权限/机构类
    user_patterns = ["user", "usr", "role", "perm", "auth", "org", "dept", "branch", "inst"]
    for p in user_patterns:
        if p in tn:
            return "用户/权限/机构类"

    # 流程日志类（必须在流程类之前判断）
    flow_log_patterns = [("flow", "log"), ("wf", "log"), ("flow", "hist"), ("wf", "hist")]
    for (a, b) in flow_log_patterns:
        if a in tn and b in tn:
            return "流程日志类"

    # 流程实例类
    flow_patterns = ["flow", "wf", "workflow"]
    for p in flow_patterns:
        if p in tn:
            return "流程实例类"

    # 产品配置类
    product_patterns = ["prdt", "product", "prod_"]
    for p in product_patterns:
        if p in tn and "aply" not in tn and "apply" not in tn:
            return "产品配置类"

    # 消息通知类
    msg_patterns = ["msg", "message", "notify", "notice"]
    for p in msg_patterns:
        if p in tn:
            return "消息通知类"

    # 档案类
    if "arch" in tn or "archive" in tn:
        return "档案类"

    # 日志/历史/审计类
    log_patterns = ["log", "hist", "history", "trace", "trail", "journal", "audit",
                    "record", "track", "snapshot", "snap"]
    for p in log_patterns:
        if p in tn:
            return "日志/审计类"

    # 文件/文档类
    doc_patterns = ["doc", "file", "attach", "img", "photo"]
    for p in doc_patterns:
        if p in tn:
            return "文件/文档类"

    # 统计汇总类
    stat_patterns = ["stat", "summ", "rpt", "report", "summary", "statis"]
    for p in stat_patterns:
        if p in tn:
            return "统计汇总类"

    # 临时表/辅助表
    tmp_patterns = ["tmp", "temp", "middle", "bak", "backup", "_mid", "_tmp"]
    for p in tmp_patterns:
        if p in tn:
            return "临时表/辅助类"

    # 客户信息类
    cust_patterns = ["cust", "customer", "ecif"]
    for p in cust_patterns:
        if p in tn:
            return "客户数据类"

    # 合同/借据/贷款
    contract_patterns = ["cont", "ctrt", "contract", "iou", "loan", "lmt", "limit", "crlmt"]
    for p in contract_patterns:
        if p in tn:
            return "合同/借据/额度类"

    # 押品管理
    clt_patterns = ["cltl", "clt", "coll", "col_", "pledge", "mortgage"]
    for p in clt_patterns:
        if p in tn:
            return "押品管理类"

    return "其他/默认"


def estimate_data_volume(table_name: str, field_count: int) -> tuple:
    """返回(文字描述, 数值估算)"""
    bt = detect_business_type(table_name, field_count)

    # 映射业务类型到数值估算
    volume_map = {
        "配置/字典/参数/代码类": 0,
        "用户/权限/机构类": 100000,
        "流程日志类": 10000000,
        "流程实例类": 3000000,
        "产品配置类": 10000,
        "消息通知类": 50000000,
        "档案类": 3000000,
        "日志/审计类": 10000000,
        "文件/文档类": 3000000,
        "统计汇总类": 3000000,
        "临时表/辅助类": 100000,
        "客户数据类": 3000000,
        "合同/借据/额度类": 3000000,
        "押品管理类": 3000000,
    }

    if bt in volume_map:
        return (bt, volume_map[bt])

    # 默认：按字段数
    if field_count < 10:
        return ("其他/默认", 100000)
    else:
        return ("其他/默认", 3000000)


# ============================================================
# 核心分析函数
# ============================================================
def select_partition_key(fields_upper: set, business_type: str, is_log_like: bool) -> tuple:
    """
    选择分区键。
    fields_upper: 表中所有字段的大写集合
    返回: (选中的分区键字段名, 优先级描述) 或 (None, 原因)
    """
    # 对于日志类使用扩展时间字段列表
    if is_log_like or "日志" in business_type or "审计" in business_type:
        # 先尝试标准优先级
        if business_type in PARTITION_KEY_PRIORITY:
            priority_list = PARTITION_KEY_PRIORITY[business_type]
        else:
            priority_list = PARTITION_KEY_PRIORITY.get("日志/审计类", LOG_TIME_FIELDS)

        # 对日志类，扩展时间字段搜索
        candidate_fields = list(priority_list) + [f for f in LOG_TIME_FIELDS if f not in priority_list]
        for idx, key in enumerate(candidate_fields):
            if key.upper() in fields_upper and key.upper() != "TENANT_ID":
                return (key, f"第{idx+1}优先级{key}")
        return (None, "未找到合适时间字段")
    else:
        # 非日志类
        if business_type in PARTITION_KEY_PRIORITY:
            priority_list = PARTITION_KEY_PRIORITY[business_type]
        else:
            priority_list = PARTITION_KEY_PRIORITY.get("其他", ["BUS_NO", "CUST_NO", "DOC_NO"])

        for idx, key in enumerate(priority_list):
            if key.upper() in fields_upper and key.upper() != "TENANT_ID":
                return (key, f"第{idx+1}优先级{key}")

        # 如果都不在，尝试通用业务字段
        extra = ["BUS_NO", "CUST_NO", "DOC_NO", "APLY_NO", "CTRT_NO", "ID"]
        for key in extra:
            if key.upper() in fields_upper and key.upper() != "TENANT_ID":
                return (key, f"通用业务字段{key}")

        return (None, "未找到合适分区键")


def analyze_table(table: dict, person_map: dict) -> dict:
    """对单张表执行精细化分区分析"""
    table_name = table["表英文名"]
    chinese_name = table["表中文名"]
    module = table["所属模块"]
    database = table["所属数据库"]
    is_matched = table.get("是否匹配", False)
    business_type = table.get("业务类型", "其他/默认")
    growth_factor = table.get("增长系数", 1.0)
    fields_list = table.get("字段列表", [])

    field_count = len(fields_list)
    fields_upper = {f["字段英文名"].upper() for f in fields_list}
    # 也保留原始大小写映射
    fields_original = {f["字段英文名"].upper(): f["字段英文名"] for f in fields_list}

    # 责任人
    person = person_map.get(table_name.lower(), "待确认")

    # ====== Step A: 确定预估3-5年数据量 ======
    if is_matched:
        current_count = table.get("当前数据量", None)
        estimated_3_5y = table.get("预估3-5年数据量", 0)
        if estimated_3_5y is None:
            estimated_3_5y = 0
        volume_desc = f"{estimated_3_5y:,}" if estimated_3_5y else "0"
        # 对匹配表但业务类型为"其他/默认"的，尝试从表名检测更精确类型
        if business_type == "其他/默认":
            detected = detect_business_type(table_name, field_count)
            if detected != "其他/默认":
                business_type = detected
    else:
        current_count = None
        data_type, estimated_3_5y = estimate_data_volume(table_name, field_count)
        volume_desc = data_type
        # 覆盖业务类型（如果估算更精确）
        if business_type == "其他/默认":
            if data_type in ["配置/字典/参数/代码类", "用户/权限/机构类", "流程日志类",
                             "流程实例类", "产品配置类", "消息通知类", "文件/文档类",
                             "统计汇总类", "临时表/辅助类", "日志/审计类"]:
                business_type = data_type

    # ====== Step B: 判断是否分区 ======
    needs_partition = estimated_3_5y > THRESHOLD

    # ====== Step C & D: 分区键与分区数 ======
    partition_key = "无需分区"
    partition_count_str = "不适用"
    partition_strategy = "不适用"
    notes_parts = []

    if needs_partition:
        # 判断是否日志类（分区键可能是时间字段）
        is_log = business_type in ["日志/审计类", "日志/审计类", "流程日志类", "消息通知类"]
        is_log = is_log or "日志" in business_type or "审计" in business_type

        pk, pk_reason = select_partition_key(fields_upper, business_type, is_log)

        if pk is not None and pk != "待确认":
            partition_key = fields_original.get(pk.upper(), pk)
            # 时间字段集合（包含所有可用于时间分区的字段名）
            TIME_FIELDS_SET = {f.upper() for f in LOG_TIME_FIELDS}
            is_time_pk = pk.upper() in TIME_FIELDS_SET

            if is_time_pk:
                partition_count_str = "0（按时间自动）"
                partition_strategy = f"按{partition_key}时间分区，3个月一个分区，保留3年数据，按时间自动创建分区"
            else:
                pcount = math.ceil(estimated_3_5y / ONE_PARTITION_SIZE)
                pcount = min(pcount, MAX_PARTITION_COUNT)
                partition_count_str = str(pcount)
                partition_strategy = f"按{partition_key} HASH分区，初始{pcount}个分区，后续按需扩容"
        else:
            partition_key = "待确认"
            partition_count_str = "待确认"
            partition_strategy = "待确认"
            pk_reason = "字段列表中未找到规则4指定的分区键候选字段"

        # 备注
        notes_parts.append(f"表类型：{business_type}")
        if is_matched and current_count is not None:
            notes_parts.append(f"当前数据量：{current_count}")
            notes_parts.append(f"预估3-5年：{estimated_3_5y}")
            notes_parts.append(f"增长系数：{growth_factor}")
        else:
            notes_parts.append(f"预估3-5年：{volume_desc}（估算值={estimated_3_5y}）")
        notes_parts.append(f"分区键来源：{pk_reason}")

        if is_matched:
            notes_parts.append(f"老系统表名：{table_name}")
        else:
            notes_parts.append("老系统表名：新系统新增")
    else:
        # 不需要分区的备注
        notes_parts.append(f"表类型：{business_type}")
        if is_matched and current_count is not None:
            notes_parts.append(f"当前数据量：{current_count}")
            notes_parts.append(f"预估3-5年：{estimated_3_5y}")
            notes_parts.append(f"增长系数：{growth_factor}")
        else:
            notes_parts.append(f"预估3-5年：{volume_desc}")
        notes_parts.append("无需分区")
        if is_matched:
            notes_parts.append(f"老系统表名：{table_name}")
        else:
            notes_parts.append("老系统表名：新系统新增")

    notes = "；".join(notes_parts)

    return {
        "所属数据库": database,
        "所属模块": module,
        "责任人": person,
        "表名（英文）": table_name,
        "表名（中文）": chinese_name,
        "是否表分区": "是" if needs_partition else "否",
        "表分区键": partition_key,
        "初始表分区数": partition_count_str,
        "表分区策略": partition_strategy,
        "备注": notes,
        "_needs_partition": needs_partition,
        "_is_matched": is_matched,
    }


def build_person_map():
    """从 partition_analysis_data.json 提取 93 条人工标注的责任人映射"""
    person_map = {}
    if PRIOR_FILE.exists():
        with open(PRIOR_FILE, "r", encoding="utf-8") as f:
            prior_data = json.load(f)
        for entry in prior_data.get("existing_partitions", []):
            name = entry.get("表名（英文）", "").strip().lower()
            person = entry.get("责任人", "待确认").strip()
            if name and person:
                person_map[name] = person
    return person_map


def main():
    # 加载数据
    print("=" * 60)
    print("  湖北农信新信贷数据库 — 精细化分区分析 V3")
    print("=" * 60)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    tables = data["tables"]
    total = len(tables)
    print(f"\n[1] 加载数据完成：共 {total} 张表")

    person_map = build_person_map()
    matched_93 = len(person_map)
    print(f"[2] 责任人映射：{matched_93} 条（来自已有93条人工标注）")

    # 逐表分析
    print(f"[3] 开始逐表精细化分析...")
    results = []
    for i, t in enumerate(tables):
        r = analyze_table(t, person_map)
        results.append(r)
        if (i + 1) % 200 == 0 or (i + 1) == total:
            print(f"    进度：{i+1}/{total}")

    # 统计
    partition_count = sum(1 for r in results if r["_needs_partition"])
    no_partition_count = total - partition_count
    matched_count = sum(1 for r in results if r["_is_matched"])
    new_count = total - matched_count

    print(f"\n[4] 分析完成：")
    print(f"    总表数：{total}")
    print(f"    需分区：{partition_count}")
    print(f"    不分区：{no_partition_count}")
    print(f"    匹配生产数据：{matched_count}")
    print(f"    新系统新增：{new_count}")

    # 排序：需分区在前，不分区在后
    results.sort(key=lambda r: (not r["_needs_partition"], r["表名（英文）"]))

    # 重新编序号
    partition_list = []
    no_partition_list = []
    for idx, r in enumerate(results, start=1):
        entry = {k: v for k, v in r.items() if not k.startswith("_")}
        entry["序号"] = idx
        if r["_needs_partition"]:
            partition_list.append(entry)
        else:
            no_partition_list.append(entry)

    # ===== 生成 JSON 文件 =====
    json_output = {
        "stats": {
            "总表数": total,
            "需分区": partition_count,
            "不分区": no_partition_count,
            "匹配生产数据": matched_count,
            "新系统新增": new_count,
        },
        "partition_tables": partition_list,
        "no_partition_tables": no_partition_list,
    }

    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)
    print(f"[5] JSON 结果已生成：{RESULT_JSON.name}")

    # ===== 生成 Excel 文件 =====
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
    all_entries = partition_list + no_partition_list
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
            # 需要分区的行高亮
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
    print(f"[6] Excel 结果已生成：{RESULT_EXCEL.name}")

    # 打印分区表摘要
    print(f"\n{'='*60}")
    print(f"  需要分区的 {partition_count} 张表明细：")
    print(f"{'='*60}")
    for p in partition_list:
        print(f"  [{p['序号']:>4}] {p['表名（英文）']:<40s} 分区键={p['表分区键']:<18s} 分区数={p['初始表分区数']:<6s}")

    print(f"\n{'='*60}")
    print(f"  分析完成！")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()