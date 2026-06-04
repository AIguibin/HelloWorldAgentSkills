#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
湖北农信新信贷数据库表分区分析工具
读取 partition_analysis_data.json，逐表分析分区需求，生成完整Excel输出。
"""

import json
import re
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

# ============================================================
# 配置
# ============================================================
BASE_DIR = Path(__file__).parent
JSON_FILE = BASE_DIR / "partition_analysis_data.json"
OUTPUT_FILE = BASE_DIR / "湖北农信数据库分区表清单_完整版.xlsx"

# ============================================================
# 分区判断规则定义（关键词均为小写，用于大小写不敏感的匹配）
# ============================================================

# 必须分区的表名关键词
MUST_PARTITION_KEYWORDS = {
    # 规则1: 日志/历史类
    "LOG": "日志/历史类表，数据持续增长",
    "HIST": "历史类表，数据量大且持续增长",
    "HISTORY": "历史类表，数据量大且持续增长",
    "TRACE": "追踪/跟踪类表，数据持续增长",
    "TRAIL": "审计追踪类表，数据持续增长",
    "RECORD": "记录类表，数据量大",
    "JOURNAL": "日志/流水类表，数据持续增长",

    # 规则2: 归档/档案类
    "ARCH": "归档/档案类表",
    "ARCHIVE": "归档/档案类表，数据量大",

    # 规则3: 检查/监控/预警类
    "CHK": "检查/监控类表",
    "CHECK": "检查/监控类表，数据持续增长",
    "MONITOR": "监控类表，数据持续增长",
    "WARN": "预警类表，数据持续增长",
    "ALERT": "预警类表，数据持续增长",
    "INSPECT": "检查/稽核类表",

    # 规则4: 任务类
    "TASK": "任务类表，数据持续增长",
    "TSK": "任务类表，数据持续增长",

    # 规则5: 消息/通知类
    "MSG": "消息类表，数据量大",
    "MESSAGE": "消息类表，数据量大",
    "NOTIFY": "通知类表，数据量大",
    "NOTICE": "通知类表，数据量大",

    # 规则6: 征信查询类
    "CREDIT_QUERY": "征信查询类表，数据量大",
    "CREDIT_REPORT": "征信报告类表，数据量大",

    # 规则7: 合同/借据/贷款核心表
    "IOU": "借据核心表，数据量大",
    "CTR_": "合同相关表，数据量大",
    "CONT": "合同相关表，数据量大",
    "CTRT": "合同核心表，数据量大",
    "CONTRACT": "合同核心表，数据量大",
    "LOAN": "贷款核心表，数据量大",
    "LN_": "贷款/借据类表",

    # 规则8: 申请/审批/批复类
    "APLY": "申请类表，数据持续增长",
    "APPLY": "申请类表，数据持续增长",
    "REPLY": "批复/回复类表",
    "APPROVAL": "审批类表，数据持续增长",
    "AUDIT": "审计/审批类表",

    # 规则9: 客户信息类
    "CUST": "客户信息类表，数据量大",
    "ECIF": "ECIF客户信息类表，数据量大",
    "CUSTOMER": "客户信息类表，数据量大",

    # 规则10: 额度/授信类
    "LMT": "额度/授信类表",
    "LIMIT": "额度/授信类表",
    "CREDIT_LINE": "授信/额度类表",

    # 规则11: 评级/评分类
    "RATING": "评级/评分表，数据持续增长",
    "RTG": "评级类表",
    "SCORE": "评分/评级表",

    # 规则12: 催收/逾期类
    "COLLECTION": "催收类表，数据持续增长",
    "COLL": "催收类表",
    "OVERDUE": "逾期类表，数据持续增长",

    # 规则13: 营销活动类
    "MARKET": "营销类表",
    "MKT": "营销活动类表",
    "CMPN": "营销活动类表",
    "CAMPAIGN": "营销活动类表",

    # 规则14: 流程/工作流类
    "FLOW": "流程类表，数据持续增长",
    "PROCESS": "流程/处理类表",
    "WF": "工作流类表",
    "WORKFLOW": "工作流类表",

    # 规则15: 明细/清单类（大表）
    "DTL": "明细类表，数据量大",
    "DETAIL": "明细类表，数据量大",
    "ITEM": "清单/项目明细表",
    "LIST": "清单/列表类表",

    # 规则16: 结果类表
    "RESULT": "结果类表，数据量持续增长",
    "RSLT": "结果类表",

    # 规则17: 报表类
    "REPORT": "报表类表，数据量大",
    "RPT": "报表类表",

    # 规则18: 批处理/作业类
    "BATCH": "批处理/作业类表",
    "JOB": "作业类表",

    # 规则19: 签署/电子类
    "SIGN": "签署类表，数据持续增长",
    "SIGNATURE": "签署类表",
    "ELEC": "电子档案/签名类表",

    # 规则20: 放还款/支付类
    "PAY": "支付/还款类表，数据量大",
    "REPAY": "还款类表，数据量大",
    "DSBR": "放款类表，数据量大",
    "DISBURSE": "放款类表，数据量大",
}

# 可不分区的表名关键词
NO_PARTITION_KEYWORDS = {
    # 规则1: 配置/参数类
    "CONFIG": "配置表，数据量小且稳定",
    "CONF": "配置表",
    "CFG": "配置表",
    "PARAM": "参数表，数据量小且稳定",
    "PARA": "参数表",
    "SETTING": "设置表，数据量小且稳定",

    # 规则2: 字典/代码/目录类
    "DICT": "字典表，数据量小且稳定",
    "DIC": "字典表",
    "CODE": "代码/编码表",
    "CD": "代码字典表",
    "CATALOG": "目录表",
    "CATLG": "目录表",

    # 规则3: 规则/策略类
    "RULE_": "规则表，数据量小且稳定",
    "RULE": "规则/策略表",
    "POLICY": "策略表",

    # 规则4: 模板类
    "TEMPLATE": "模板表，数据量小且稳定",
    "TMPL": "模板表",
    "TMP": "模板/临时表",

    # 规则5: 序列号类
    "SEQ": "序列号表，数据量小",
    "SEQUENCE": "序列号表",
    "SERIAL": "序列号表",

    # 规则6: 机构/部门类
    "ORG": "机构表，数据量小且稳定",
    "DEPT": "部门表，数据量小且稳定",
    "BRANCH": "机构/网点表",
    "INSTITUTION": "机构表",

    # 规则7: 用户/权限/认证类
    "USER": "用户表，数据量通常较小",
    "USR": "用户表",
    "ROLE": "角色表，数据量小",
    "PERMISSION": "权限表",
    "AUTH": "认证/授权表",

    # 规则8: 产品定义类
    "PRODUCT": "产品定义表，数据量小且稳定",
    "PRDT": "产品定义表",
    "PROD": "产品定义表",

    # 规则9: 关联关系类
    "RELATION": "关联关系表，数据量通常不大",
    "REL": "关联关系表",

    # 规则10: 映射关系类
    "MAP": "映射关系表",
    "MAPPING": "映射关系表",

    # 规则11: 版本信息类
    "VERSION": "版本信息表",
    "VER": "版本信息表",
}

# SYS_开头的系统管理表（不分区的），但排除日志类
SYS_EXCLUDE_PARTITION = {"SYS_LOG", "SYS_LOGIN_LOG"}

# ============================================================
# 分区键优先级选择规则
# ============================================================

# 分区键优先级：按表类型分组，每组内按优先级排列
PARTITION_KEY_PRIORITY = [
    # 时间类键（日志/历史/记录）
    ["CREATE_TIME", "BIZ_DATE", "OPER_DATE", "CRT_TIME", "CREATE_DATE",
     "DEAL_DATE", "TRANS_DATE", "ACCT_DATE", "BUSI_DATE", "DATA_DATE",
     "EXEC_DATE", "TXN_DATE", "OPR_DATE", "GEN_DATE", "SEND_DATE",
     "RECV_DATE", "START_DATE", "END_DATE", "EFFECT_DATE", "EXPIRE_DATE"],

    # 合同/借据类
    ["CTRT_NO", "BUS_NO", "LOAN_NO", "IOU_NO", "CONT_NO", "CONTRACT_NO",
     "PRVT_CTR_NO", "PUB_CTR_NO", "LON_BUS_NO"],

    # 客户类
    ["CUST_NO", "CUST_INTL_SEQ_NO", "GTCR_CUST_NO", "CUST_ID",
     "ECIF_CUST_NO", "CUSTOMER_NO"],

    # 额度/授信类
    ["LMT_NO", "CRLMT_NO", "CREDIT_LMT_NO", "CREDIT_LINE_NO",
     "LMT_APLY_NO", "BUS_NO"],

    # 申请/审批类
    ["APLY_NO", "APPLY_NO", "BUS_NO", "APPROVAL_NO", "BIZ_APLY_NO",
     "APPR_NO"],

    # 任务/流程类
    ["TSK_NO", "TASK_NO", "PROCESS_ID", "PROCESS_INST_ID",
     "WF_INST_ID", "FLOW_NO", "TASK_ID", "JOB_NO"],

    # 营销类
    ["MKT_TSK_NO", "MKT_TASK_NO", "CUST_NO", "DOC_NO", "MKT_NO"],

    # 档案/签署类
    ["ARS_NO", "ELC_MTRLS_NO", "BIZ_APLY_NO", "SIGN_NO", "DOC_NO",
     "ARCH_NO"],

    # 通用/多租户
    ["TENANT_ID", "BIZ_NO", "SERIAL_NO", "DOC_NO", "REF_NO"],
]

# 按表类型重新组织分区键优先级（类型相关键优先，再通用键）
# 对于日志/历史/记录类，时间键应该最先
# 对于其他类型，业务键应该先于时间键
PARTITION_KEY_TYPED_PRIORITY = {
    "日志/历史": [
        ["CREATE_TIME", "BIZ_DATE", "OPER_DATE", "CRT_TIME", "CREATE_DATE",
         "DEAL_DATE", "TRANS_DATE", "ACCT_DATE", "BUSI_DATE", "DATA_DATE",
         "EXEC_DATE", "TXN_DATE", "OPR_DATE", "GEN_DATE", "SEND_DATE",
         "RECV_DATE", "START_DATE", "END_DATE", "EFFECT_DATE", "EXPIRE_DATE"],
    ],
    "记录": [
        ["CREATE_TIME", "BIZ_DATE", "OPER_DATE", "CRT_TIME", "CREATE_DATE",
         "DEAL_DATE", "TRANS_DATE", "ACCT_DATE", "BUSI_DATE", "DATA_DATE",
         "EXEC_DATE", "TXN_DATE", "OPR_DATE", "GEN_DATE", "SEND_DATE",
         "RECV_DATE"],
    ],
    "合同/借据/贷款": [
        ["CTRT_NO", "BUS_NO", "LOAN_NO", "IOU_NO", "CONT_NO", "CONTRACT_NO",
         "PRVT_CTR_NO", "PUB_CTR_NO", "LON_BUS_NO"],
    ],
    "客户信息": [
        ["CUST_NO", "CUST_INTL_SEQ_NO", "GTCR_CUST_NO", "CUST_ID",
         "ECIF_CUST_NO", "CUSTOMER_NO"],
    ],
    "额度/授信": [
        ["LMT_NO", "CRLMT_NO", "CREDIT_LMT_NO", "CREDIT_LINE_NO", "LMT_APLY_NO"],
    ],
    "申请/审批": [
        ["APLY_NO", "APPLY_NO", "BUS_NO", "APPROVAL_NO", "BIZ_APLY_NO", "APPR_NO"],
    ],
    "任务": [
        ["TSK_NO", "TASK_NO", "TASK_ID", "JOB_NO"],
    ],
    "流程/工作流": [
        ["PROCESS_INST_ID", "WF_INST_ID", "FLOW_NO", "PROCESS_ID", "TSK_NO"],
    ],
    "营销活动": [
        ["MKT_TSK_NO", "MKT_TASK_NO", "CUST_NO", "DOC_NO", "MKT_NO"],
    ],
    "档案": [
        ["ARS_NO", "ELC_MTRLS_NO", "BIZ_APLY_NO", "ARCH_NO", "DOC_NO"],
    ],
    "签署/电子": [
        ["SIGN_NO", "ELC_MTRLS_NO", "BIZ_APLY_NO", "DOC_NO"],
    ],
    "放还款/支付": [
        ["BUS_NO", "LOAN_NO", "CTRT_NO", "PAY_NO"],
    ],
    "检查/监控": [
        ["TSK_NO", "TASK_NO", "CUST_NO", "BUS_NO"],
    ],
    "批处理/作业": [
        ["JOB_NO", "BATCH_NO", "TASK_NO"],
    ],
    "消息/通知": [
        ["BUS_NO", "CUST_NO"],
    ],
    "催收/逾期": [
        ["CUST_NO", "BUS_NO", "LOAN_NO"],
    ],
    "评级/评分": [
        ["CUST_NO", "BUS_NO"],
    ],
    "报表": [
        ["BUS_NO", "CUST_NO"],
    ],
    "结果": [
        ["BUS_NO", "TSK_NO", "CUST_NO"],
    ],
    "征信查询": [
        ["CUST_NO", "BUS_NO"],
    ],
    "明细/清单": [
        ["BUS_NO", "CTRT_NO", "CUST_NO", "TSK_NO"],
    ],
}

# 通用后备键（用于没有类型特定键匹配时，或者用于所有类型键之后的兜底）
FALLBACK_KEYS = [
    ["TENANT_ID"],
    ["CREATE_TIME", "BIZ_DATE", "OPER_DATE", "CRT_TIME", "CREATE_DATE",
     "DEAL_DATE", "TRANS_DATE", "ACCT_DATE", "BUSI_DATE", "DATA_DATE",
     "EXEC_DATE", "TXN_DATE", "OPR_DATE", "GEN_DATE", "SEND_DATE",
     "RECV_DATE"],
    ["CTRT_NO", "BUS_NO", "LOAN_NO", "IOU_NO", "CONT_NO", "CONTRACT_NO",
     "PRVT_CTR_NO", "PUB_CTR_NO", "LON_BUS_NO"],
    ["CUST_NO", "CUST_INTL_SEQ_NO", "GTCR_CUST_NO", "CUST_ID",
     "ECIF_CUST_NO", "CUSTOMER_NO"],
    ["LMT_NO", "CRLMT_NO", "CREDIT_LMT_NO", "CREDIT_LINE_NO", "LMT_APLY_NO"],
    ["APLY_NO", "APPLY_NO", "BUS_NO", "APPROVAL_NO", "BIZ_APLY_NO", "APPR_NO"],
    ["TSK_NO", "TASK_NO", "PROCESS_ID", "PROCESS_INST_ID",
     "WF_INST_ID", "FLOW_NO", "TASK_ID", "JOB_NO"],
    ["MKT_TSK_NO", "MKT_TASK_NO", "CUST_NO", "DOC_NO", "MKT_NO"],
    ["ARS_NO", "ELC_MTRLS_NO", "BIZ_APLY_NO", "SIGN_NO", "DOC_NO", "ARCH_NO"],
]

# 时间类关键词（用于识别日志/时间类表）
TIME_KEY_FIELD_PATTERNS = [
    "TIME", "DATE", "DT", "TIMESTAMP",
]

# 文件类关键词
FILE_KEY_FIELD_PATTERNS = [
    "FILE_NO", "DOC_NO", "FILE_ID", "DOC_ID",
]


def normalize_table_name(name: str) -> str:
    """归一化表名：去除前后空格，保留原样用于匹配"""
    return name.strip()


def table_name_lower(name: str) -> str:
    """获取小写表名用于关键词匹配"""
    return normalize_table_name(name).lower()


def check_must_partition(table_name: str) -> tuple:
    """
    检查表名是否命中"必须分区"规则。
    返回 (是否命中, 命中关键词, 命中原因)
    """
    tn_lower = table_name_lower(table_name)

    # 特殊处理：SYS_开头的系统表，非日志类不分区（规则12）
    if tn_lower.startswith("sys_"):
        if tn_lower not in SYS_EXCLUDE_PARTITION:
            return (False, "", "")

    matched_keywords = []
    for keyword, reason in MUST_PARTITION_KEYWORDS.items():
        kw_lower = keyword.lower()
        if kw_lower in tn_lower:
            matched_keywords.append((keyword, reason))

    if matched_keywords:
        # 返回第一个匹配的（优先级最高）
        return (True, matched_keywords[0][0], matched_keywords[0][1])

    return (False, "", "")


def check_no_partition(table_name: str) -> tuple:
    """
    检查表名是否命中"可不分区"规则。
    返回 (是否命中, 命中关键词, 命中原因)
    """
    tn_lower = table_name_lower(table_name)

    matched_keywords = []
    for keyword, reason in NO_PARTITION_KEYWORDS.items():
        kw_lower = keyword.lower()
        if kw_lower in tn_lower:
            matched_keywords.append((keyword, reason))

    if matched_keywords:
        return (True, matched_keywords[0][0], matched_keywords[0][1])

    return (False, "", "")


def should_partition(table_name: str) -> tuple:
    """
    综合判断表是否需要分区。
    优先级：必须分区 > 可不分区
    返回 (是否分区, 原因描述, 表分类)
    """
    must_hit, must_keyword, must_reason = check_must_partition(table_name)
    no_hit, no_keyword, no_reason = check_no_partition(table_name)

    tn_lower = table_name_lower(table_name)

    if must_hit:
        return ("是", must_reason, must_keyword)
    elif no_hit:
        return ("否", no_reason, no_keyword)
    else:
        # 没有命中任何规则，保守处理
        # 进一步启发式判断
        if any(k in tn_lower for k in ["_his", "_hist", "_log", "_rec", "_trc", "_trail"]):
            return ("是", "表名含历史/日志/记录类后缀，保守标记为需分区", "启发式")
        if any(k in tn_lower for k in ["_ext", "_snap", "_backup"]):
            return ("是", "表名含扩展/快照/备份类后缀，可能数据量较大", "启发式")
        if "_inf" in tn_lower and not any(k in tn_lower for k in ["_cfg", "_conf", "_para", "_dict"]):
            return ("是", "信息类主表（_INF），可能数据量较大", "启发式")

        return ("否", "未命中任何分区规则，数据量预估不大", "默认")


def classify_table_type(table_name: str) -> str:
    """
    根据表名分类，用于分区键选择和分区策略描述。
    """
    tn_lower = table_name_lower(table_name)

    # 按优先级判断表类型
    if any(k.lower() in tn_lower for k in ["LOG", "HIST", "HISTORY", "TRACE", "TRAIL", "JOURNAL"]):
        return "日志/历史"
    if any(k.lower() in tn_lower for k in ["ARCH", "ARCHIVE"]):
        return "档案"
    if any(k.lower() in tn_lower for k in ["CHK", "CHECK", "MONITOR", "WARN", "ALERT", "INSPECT"]):
        return "检查/监控"
    if any(k.lower() in tn_lower for k in ["TASK", "TSK"]):
        return "任务"
    if any(k.lower() in tn_lower for k in ["MSG", "MESSAGE", "NOTIFY", "NOTICE"]):
        return "消息/通知"
    if any(k.lower() in tn_lower for k in ["CREDIT_QUERY", "CREDIT_REPORT"]):
        return "征信查询"
    if any(k.lower() in tn_lower for k in ["IOU", "CTR_", "CTRT", "CONTRACT", "LOAN", "LN_", "CONT"]):
        return "合同/借据/贷款"
    if any(k.lower() in tn_lower for k in ["APLY", "APPLY", "REPLY", "APPROVAL", "AUDIT"]):
        return "申请/审批"
    if any(k.lower() in tn_lower for k in ["ECIF", "CUST", "CUSTOMER"]):
        return "客户信息"
    if any(k.lower() in tn_lower for k in ["LMT", "LIMIT", "CREDIT_LINE"]):
        return "额度/授信"
    if any(k.lower() in tn_lower for k in ["RATING", "RTG", "SCORE"]):
        return "评级/评分"
    if any(k.lower() in tn_lower for k in ["COLLECTION", "COLL", "OVERDUE"]):
        return "催收/逾期"
    if any(k.lower() in tn_lower for k in ["MARKET", "MKT", "CMPN", "CAMPAIGN"]):
        return "营销活动"
    if any(k.lower() in tn_lower for k in ["FLOW", "PROCESS", "WF", "WORKFLOW"]):
        return "流程/工作流"
    if any(k.lower() in tn_lower for k in ["DTL", "DETAIL", "ITEM", "LIST"]):
        return "明细/清单"
    if any(k.lower() in tn_lower for k in ["RESULT", "RSLT"]):
        return "结果"
    if any(k.lower() in tn_lower for k in ["REPORT", "RPT"]):
        return "报表"
    if any(k.lower() in tn_lower for k in ["BATCH", "JOB"]):
        return "批处理/作业"
    if any(k.lower() in tn_lower for k in ["SIGN", "SIGNATURE", "ELEC"]):
        return "签署/电子"
    if any(k.lower() in tn_lower for k in ["PAY", "REPAY", "DSBR", "DISBURSE"]):
        return "放还款/支付"
    if any(k.lower() in tn_lower for k in ["RECORD"]):
        return "记录"

    return "通用"


def select_partition_key(table_type: str, fields: list) -> str:
    """
    根据表类型和字段列表，选择最合适的分区键。
    优先使用类型特定的分区键，再使用通用后备键。
    """
    # 收集所有字段名（大写）
    field_names = set()
    for f in fields:
        fname = f.get("字段英文名", "").strip().upper()
        if fname:
            field_names.add(fname)

    if not field_names:
        return "待确认"

    # 1. 先按表类型特定的优先级查找
    typed_groups = PARTITION_KEY_TYPED_PRIORITY.get(table_type, [])
    for group in typed_groups:
        for key_candidate in group:
            if key_candidate.upper() in field_names:
                return key_candidate

    # 2. 再按通用后备键查找（TENANT_ID优先，然后是各类业务键）
    for group in FALLBACK_KEYS:
        for key_candidate in group:
            if key_candidate.upper() in field_names:
                return key_candidate

    # 3. 如果都没找到，检查是否有 TENANT_ID
    if "TENANT_ID" in field_names:
        return "TENANT_ID"

    # 4. 查找任何包含 "NO" 或 "ID" 的字段（业务编号）作为兜底
    for fname in field_names:
        if fname.endswith("_NO") or fname.endswith("_ID"):
            return fname

    # 5. 查找任何包含 "KEY" 的字段
    for fname in field_names:
        if "KEY" in fname:
            return fname

    return "待确认"


def estimate_partition_count(table_type: str, partition_key: str, is_time_based: bool) -> str:
    """
    估算初始分区数。
    - 日志/时间类表：0（按时间自动创建）
    - 客户类大表：50
    - 合同/贷款核心：2-20
    - 其他：根据表类型估算
    """
    if is_time_based:
        return "0"

    if table_type == "客户信息":
        return "50"
    elif table_type in ("合同/借据/贷款", "征信查询"):
        return "20"
    elif table_type in ("明细/清单", "报表", "记录", "结果"):
        return "20"
    elif table_type in ("放还款/支付", "申请/审批", "流程/工作流"):
        return "10"
    elif table_type in ("任务", "消息/通知", "检查/监控"):
        return "10"
    elif table_type in ("催收/逾期", "评级/评分", "额度/授信"):
        return "10"
    elif table_type in ("档案", "签署/电子", "营销活动"):
        return "5"
    elif table_type in ("批处理/作业",):
        return "5"

    # 默认
    return "5"


def generate_partition_strategy(table_type: str, partition_key: str,
                                 is_time_based: bool, partition_count: str) -> str:
    """
    生成分区策略描述（J列）。
    """
    if is_time_based:
        if partition_key in ("待确认", ""):
            return "按时间分区，3个月一个分区，自动创建分区"
        return f"按{partition_key}时间分区，3个月一个分区，保留3年数据，按时间自动创建分区"

    if partition_key == "TENANT_ID":
        return f"按租户ID({partition_key}) HASH分区，初始{partition_count}个分区，后续按需扩容"

    if partition_count == "0":
        return f"按{partition_key}时间分区，3个月一个分区，自动创建分区"

    if table_type == "客户信息":
        return f"按{partition_key} HASH分区，初始{partition_count}个分区，后续按需扩容（客户数据持续增长）"
    elif table_type == "合同/借据/贷款":
        return f"按{partition_key} HASH分区，初始{partition_count}个分区，后续按需扩容（合同/贷款数据持续增长）"
    elif table_type in ("日志/历史",):
        return f"按{partition_key}时间分区，3个月一个分区，自动创建分区"
    elif partition_key == "待确认":
        return f"待确认分区键后确定分区策略，预估初始{partition_count}个分区"

    return f"按{partition_key} HASH分区，初始{partition_count}个分区，后续按需扩容"


def generate_remarks(should_part: str, table_type: str, partition_key: str,
                     is_time_based: bool, matched_rule: str, existing_matched: bool = False) -> str:
    """
    生成备注（K列）。
    """
    parts = []

    if should_part == "是":
        parts.append(f"表类型：{table_type}")

        if is_time_based:
            parts.append("分区方式：按时间自动分区，3个月一个分区")
        elif partition_key and partition_key != "待确认":
            parts.append(f"分区键：{partition_key}")

        if matched_rule and matched_rule != "启发式" and matched_rule != "默认":
            parts.append(f"匹配规则：{matched_rule}")

        parts.append("建议定期监控分区数据量，根据增长率调整分区策略")
    else:
        if matched_rule and matched_rule != "默认":
            parts.append(f"不分区原因：{matched_rule}")
        else:
            parts.append("不分区原因：数据量预估较小，暂不分区")
        parts.append("建议定期评审，如数据量超预期增长再考虑分区")

    return "；".join(parts)


def is_time_based_table(table_type: str, partition_key: str) -> bool:
    """
    判断是否按时间分区。
    """
    if table_type in ("日志/历史", "记录"):
        return True

    # 检查分区键是否时间相关
    time_indicators = ["TIME", "DATE", "DT"]
    pk_upper = partition_key.upper()
    for ti in time_indicators:
        if ti in pk_upper:
            return True

    return False


def get_field_names_list(fields: list) -> list:
    """提取字段英文名列表（大写）"""
    return [f.get("字段英文名", "").strip().upper() for f in fields]


# ============================================================
# 主处理逻辑
# ============================================================

def load_data():
    """加载JSON数据"""
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def process_existing_partitions(existing_data: list) -> list:
    """
    处理现有分区清单：
    - 保留所有现有信息
    - 补充缺失的J列（表分区策略）和K列（备注）
    - 补充缺失的H列（表分区键）和I列（初始表分区数）
    """
    result = []

    for record in existing_data:
        record = dict(record)  # 复制，避免修改原数据

        table_name = record.get("表名（英文）", "")
        partition_key = record.get("表分区键", "").strip()
        partition_count = record.get("初始表分区数", "").strip()
        partition_strategy = record.get("表分区策略", "").strip()
        remarks = record.get("备注", "").strip()

        # 分类表类型
        table_type = classify_table_type(table_name)

        # 补充分区键（如果为空）
        if not partition_key:
            # 尝试根据表类型推断分区键
            partition_key = infer_partition_key_from_table_type(table_type)

        # 补充分区数（如果为空）
        is_time = is_time_based_table(table_type, partition_key)
        if not partition_count:
            partition_count = estimate_partition_count(table_type, partition_key, is_time)

        # 补充分区策略（如果为空）
        if not partition_strategy:
            partition_strategy = generate_partition_strategy(
                table_type, partition_key, is_time, partition_count)

        # 补充备注（如果为空）
        if not remarks:
            remarks = generate_remarks("是", table_type, partition_key, is_time, table_type)

        record["表分区键"] = partition_key
        record["初始表分区数"] = partition_count
        record["表分区策略"] = partition_strategy
        record["备注"] = remarks

        result.append(record)

    return result


def infer_partition_key_from_table_type(table_type: str) -> str:
    """当没有字段信息时，根据表类型推断分区键"""
    type_key_map = {
        "日志/历史": "CREATE_TIME",
        "档案": "ARS_NO",
        "检查/监控": "TSK_NO",
        "任务": "TSK_NO",
        "消息/通知": "CREATE_TIME",
        "征信查询": "TENANT_ID",
        "合同/借据/贷款": "CTRT_NO",
        "申请/审批": "APLY_NO",
        "客户信息": "CUST_NO",
        "额度/授信": "LMT_NO",
        "评级/评分": "TENANT_ID",
        "催收/逾期": "TENANT_ID",
        "营销活动": "MKT_TSK_NO",
        "流程/工作流": "TENANT_ID",
        "明细/清单": "TENANT_ID",
        "结果": "TENANT_ID",
        "报表": "TENANT_ID",
        "批处理/作业": "TENANT_ID",
        "签署/电子": "TENANT_ID",
        "放还款/支付": "TENANT_ID",
        "记录": "CREATE_TIME",
        "通用": "TENANT_ID",
    }
    return type_key_map.get(table_type, "TENANT_ID")


def process_new_tables(all_tables: list, existing_table_names: set) -> list:
    """
    处理新表（不在现有分区清单中的表）：
    - 逐表分析是否需要分区
    - 选择分区键、估算分区数、生成分区策略和备注
    """
    result = []

    for table_info in all_tables:
        table_name = table_info.get("表英文名", "")
        table_name_cn = table_info.get("表中文名", "")
        db_name = table_info.get("所属数据库", "")
        module = table_info.get("所属模块", "")
        fields = table_info.get("字段列表", [])

        # 检查是否在现有分区清单中（大小写不敏感）
        tn_lower = table_name.lower()
        if tn_lower in existing_table_names:
            continue  # 已在现有清单中，跳过

        # 判断是否需要分区
        should_part, reason, matched_rule = should_partition(table_name)

        # 分类表类型
        table_type = classify_table_type(table_name)

        # 选择分区键
        partition_key = ""
        partition_count = ""
        partition_strategy = ""
        remarks = ""

        if should_part == "是":
            partition_key = select_partition_key(table_type, fields)
            is_time = is_time_based_table(table_type, partition_key)
            partition_count = estimate_partition_count(table_type, partition_key, is_time)
            partition_strategy = generate_partition_strategy(
                table_type, partition_key, is_time, partition_count)
            remarks = generate_remarks("是", table_type, partition_key, is_time, matched_rule)
        else:
            # 不需要分区的表
            partition_key = "无需分区"
            partition_count = "无需分区"
            partition_strategy = "数据量小，无需分区"
            remarks = generate_remarks("否", table_type, "", False, matched_rule)

        result.append({
            "表名（英文）": table_name.upper(),
            "表名（中文）": table_name_cn,
            "所属数据库": db_name,
            "所属模块": module,
            "责任人": "待确认",
            "是否表分区": should_part,
            "表分区键": partition_key,
            "初始表分区数": partition_count,
            "表分区策略": partition_strategy,
            "备注": remarks,
        })

    return result


def build_final_list(existing_processed: list, new_tables_processed: list) -> list:
    """
    合并现有分区清单和新分析的表，生成最终列表。
    现有多区清单保持原顺序，新表按数据库→模块→表名排序后追加。
    """
    final_list = []

    # 现有分区表保持原顺序
    for i, record in enumerate(existing_processed):
        item = {
            "序号": str(i + 1),
            "所属数据库": record.get("所属数据库", ""),
            "所属模块": record.get("所属模块", ""),
            "责任人": record.get("责任人", ""),
            "表名（英文）": record.get("表名（英文）", "").upper(),
            "表名（中文）": record.get("表名（中文）", ""),
            "是否表分区": record.get("是否表分区", ""),
            "表分区键": record.get("表分区键", ""),
            "初始表分区数": record.get("初始表分区数", ""),
            "表分区策略": record.get("表分区策略", ""),
            "备注": record.get("备注", ""),
        }
        final_list.append(item)

    # 新表按数据库、模块、表名排序
    new_tables_processed.sort(key=lambda x: (
        x.get("所属数据库", ""),
        x.get("所属模块", ""),
        x.get("表名（英文）", "")
    ))

    start_index = len(existing_processed)
    for i, record in enumerate(new_tables_processed):
        item = {
            "序号": str(start_index + i + 1),
            "所属数据库": record.get("所属数据库", ""),
            "所属模块": record.get("所属模块", ""),
            "责任人": record.get("责任人", "待确认"),
            "表名（英文）": record.get("表名（英文）", ""),
            "表名（中文）": record.get("表名（中文）", ""),
            "是否表分区": record.get("是否表分区", ""),
            "表分区键": record.get("表分区键", ""),
            "初始表分区数": record.get("初始表分区数", ""),
            "表分区策略": record.get("表分区策略", ""),
            "备注": record.get("备注", ""),
        }
        final_list.append(item)

    return final_list


def write_excel(final_list: list):
    """生成最终Excel文件"""
    wb = Workbook()
    ws = wb.active
    ws.title = "数据库表分区清单"

    # 列定义
    headers = [
        "序号", "所属数据库", "所属模块", "责任人",
        "表名（英文）", "表名（中文）", "是否表分区",
        "表分区键", "初始表分区数",
        "表分区策略(迁移数据量，8-10年增长量)", "备注"
    ]
    col_widths = [8, 24, 14, 10, 40, 36, 12, 22, 14, 60, 60]

    # 第1行：标题行
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    title_cell = ws.cell(row=1, column=1, value="湖北农信新信贷数据库表分区清单")
    title_cell.font = Font(name="微软雅黑", size=16, bold=True, color="FFFFFF")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    title_cell.fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
    ws.row_dimensions[1].height = 40

    # 第2行：表头
    header_fill = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
    header_font = Font(name="微软雅黑", size=11, bold=True)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=2, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    ws.row_dimensions[2].height = 36

    # 设置列宽
    for col_idx, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    # 数据行（从第3行开始）
    data_font = Font(name="微软雅黑", size=10)
    data_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    data_alignment_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # 分区标记颜色
    yes_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")  # 绿色
    no_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")   # 橙色

    for row_idx, record in enumerate(final_list):
        excel_row = row_idx + 3

        values = [
            record.get("序号", ""),
            record.get("所属数据库", ""),
            record.get("所属模块", ""),
            record.get("责任人", ""),
            record.get("表名（英文）", ""),
            record.get("表名（中文）", ""),
            record.get("是否表分区", ""),
            record.get("表分区键", ""),
            record.get("初始表分区数", ""),
            record.get("表分区策略", ""),
            record.get("备注", ""),
        ]

        for col_idx, value in enumerate(values, 1):
            cell = ws.cell(row=excel_row, column=col_idx, value=value)
            cell.font = data_font
            cell.border = thin_border

            # 列对齐
            if col_idx in (5, 6, 10, 11):  # 表名、中文名、策略、备注 左对齐
                cell.alignment = data_alignment_left
            else:
                cell.alignment = data_alignment

            # G列（是否表分区）特殊颜色
            if col_idx == 7:
                if value == "是":
                    cell.fill = yes_fill
                elif value == "否":
                    cell.fill = no_fill

        ws.row_dimensions[excel_row].height = 28

    # 冻结窗格：冻结标题行和表头行，以及前6列
    ws.freeze_panes = "G3"

    # 自动筛选
    ws.auto_filter.ref = f"A2:{get_column_letter(len(headers))}{len(final_list) + 2}"

    # 保存
    wb.save(OUTPUT_FILE)
    print(f"输出文件已生成: {OUTPUT_FILE}")


def print_statistics(final_list: list):
    """打印统计信息"""
    total = len(final_list)
    partition_yes = sum(1 for r in final_list if r["是否表分区"] == "是")
    partition_no = sum(1 for r in final_list if r["是否表分区"] == "否")

    print(f"\n{'='*60}")
    print(f"分区分析统计")
    print(f"{'='*60}")
    print(f"总表数：{total}")
    print(f"需要分区（是）：{partition_yes} ({partition_yes*100/total:.1f}%)")
    print(f"不需要分区（否）：{partition_no} ({partition_no*100/total:.1f}%)")

    # 按数据库统计
    db_stats = {}
    for r in final_list:
        db = r["所属数据库"]
        if db not in db_stats:
            db_stats[db] = {"total": 0, "yes": 0, "no": 0}
        db_stats[db]["total"] += 1
        if r["是否表分区"] == "是":
            db_stats[db]["yes"] += 1
        else:
            db_stats[db]["no"] += 1

    print(f"\n--- 按数据库统计 ---")
    for db, stats in sorted(db_stats.items()):
        print(f"  {db}: 总{stats['total']}张, 分区{stats['yes']}张, 不分区{stats['no']}张")

    # 分类统计
    type_stats = {}
    for r in final_list:
        if r["是否表分区"] == "是":
            table_name = r["表名（英文）"]
            table_type = classify_table_type(table_name)
            if table_type not in type_stats:
                type_stats[table_type] = 0
            type_stats[table_type] += 1

    print(f"\n--- 分区表类型分布 ---")
    for t, count in sorted(type_stats.items(), key=lambda x: -x[1]):
        print(f"  {t}: {count}张")


def main():
    print("=" * 60)
    print("湖北农信新信贷数据库表分区分析工具")
    print("=" * 60)

    # 1. 加载数据
    print("\n[1/5] 加载数据...")
    data = load_data()
    existing_partitions = data.get("existing_partitions", [])
    all_tables = data.get("all_tables", [])
    print(f"  - 现有分区清单：{len(existing_partitions)} 张表")
    print(f"  - 全量表清单：{len(all_tables)} 张表")

    # 2. 构建现有分区表名集合（小写）
    print("\n[2/5] 处理现有分区清单...")
    existing_table_names_lower = set()
    for ep in existing_partitions:
        tn = table_name_lower(ep.get("表名（英文）", ""))
        existing_table_names_lower.add(tn)

    # 3. 补全现有分区清单信息
    existing_processed = process_existing_partitions(existing_partitions)
    print(f"  - 现有分区清单已补全：{len(existing_processed)} 张表")

    # 4. 分析新表
    print("\n[3/5] 分析新表（不在现有分区清单中的表）...")
    new_tables_processed = process_new_tables(all_tables, existing_table_names_lower)
    print(f"  - 新增分析表：{len(new_tables_processed)} 张表")

    # 5. 合并生成最终列表
    print("\n[4/5] 合并生成最终列表...")
    final_list = build_final_list(existing_processed, new_tables_processed)
    print(f"  - 最终总表数：{len(final_list)} 张表")

    # 6. 输出Excel
    print("\n[5/5] 生成Excel文件...")
    write_excel(final_list)

    # 7. 统计
    print_statistics(final_list)

    print(f"\n{'='*60}")
    print("分析完成！")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()