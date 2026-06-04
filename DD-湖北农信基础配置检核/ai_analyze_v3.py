# -*- coding: utf-8 -*-
"""
Task 3: AI 逐表业务语义分析
基于信贷业务知识，分析每张表的业务角色、增长模式、3-5年预估数据量
核心逻辑：结合实际字段结构 + 信贷业务语义 + 生产数据量
"""
import json
import math
import os
from collections import defaultdict

# ==================== 加载数据 ====================
BASE_DIR = r"e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\DD-湖北农信基础配置检核"

with open(os.path.join(BASE_DIR, "table_structures.json"), "r", encoding="utf-8") as f:
    structures_data = json.load(f)

with open(os.path.join(BASE_DIR, "prod_data_volume.json"), "r", encoding="utf-8") as f:
    prod_data = json.load(f)

tables = structures_data["tables"]
volume_map = prod_data["volume_map"]

# ==================== 信贷业务知识库 ====================

# 模块 → 业务定位
MODULE_BUSINESS_CONTEXT = {
    "产品管理": "产品定义与配置，包括产品要素、产品阶段、产品参数等，属于配置类数据",
    "信贷引擎库": "信贷决策引擎，包括规则配置、策略配置、决策结果、引擎日志等",
    "风控中心库": "风控中心数据，包括风控规则、风控策略、风控模型、风控结果等",
    "风控中心": "风控中心业务数据，包括风控申请、审批、结果等",
    "贷后管理": "贷后检查、贷后监控、预警、催收、资产分类等，核心业务数据",
    "押品管理": "押品信息管理，包括押品登记、评估、变更、处置等",
    "客户管理": "客户信息管理，包括个人客户、对公客户、关联方、地址、证件等",
    "线上贷款": "线上贷款业务，包括申请、审批、签约、放款等",
    "用信管理": "用信/放款管理，包括放款申请、放款明细、还款计划等",
    "合同管理": "合同管理，包括合同签订、合同变更、担保合同、合同与押品关联等",
    "系统管理": "系统管理，包括用户、角色、权限、参数、日志、消息、批量等",
    "营销管理": "营销活动管理，包括营销任务、营销名单、营销结果等",
    "工作流程库": "工作流引擎，包括流程定义、流程实例、任务、历史等",
    "批量管理": "批量任务管理，包括批量任务定义、调度、执行日志等",
    "客户中心库": "客户中心数据，客户信息整合、客户关系、客户画像等",
    "架构管理": "架构管理，包括机构、部门、岗位、人员等基础架构数据",
    "电子文档库": "电子文档管理，包括文档存储、文档索引、文档版本等",
    "放还款组": "放款和还款组操作，包括放款申请、还款申请、划拨等",
    "额度中心库": "额度管理，包括额度定义、额度占用、额度释放、额度流水等",
    "授信管理": "授信管理，包括授信申请、授信审批、授信额度等",
    "档案管理": "档案管理，包括档案登记、归档、借阅、销毁等",
    "统一认证库": "统一认证，包括用户认证、单点登录、会话管理等",
    "评级管理": "客户评级，包括评级模型、评级申请、评级结果等",
}

# 表名关键词 → 业务类型分类（用于数据增长模式判断）
BUSINESS_TYPE_KEYWORDS = {
    # 日志/审计/历史类 — 高增长
    "LOG": {"type": "日志/审计类", "growth_factor": 5.0, "desc": "操作日志、审计日志，随时间线性增长，年增长50-100%"},
    "AUDIT": {"type": "日志/审计类", "growth_factor": 5.0, "desc": "审计记录，随时间线性增长"},
    "HIS": {"type": "历史轨迹类", "growth_factor": 4.0, "desc": "历史数据，随时间累积增长"},
    "HISTORY": {"type": "历史轨迹类", "growth_factor": 4.0, "desc": "历史数据，随时间累积增长"},
    "TRACE": {"type": "追踪轨迹类", "growth_factor": 4.0, "desc": "追踪记录，随时间累积增长"},
    "ACT_HI": {"type": "工作流历史类", "growth_factor": 4.0, "desc": "Activiti工作流历史数据，随业务量增长"},
    "ACT_RU": {"type": "工作流运行时类", "growth_factor": 2.0, "desc": "Activiti工作流运行时数据，随当前活跃业务量"},
    "MSG": {"type": "消息通知类", "growth_factor": 5.0, "desc": "消息记录，随时间线性增长"},
    "MESSAGE": {"type": "消息通知类", "growth_factor": 5.0, "desc": "消息记录，随时间线性增长"},
    "NOTIFY": {"type": "消息通知类", "growth_factor": 5.0, "desc": "通知记录，随时间线性增长"},
    "ALERT": {"type": "预警类", "growth_factor": 3.0, "desc": "预警记录，随业务量增长"},
    "WARN": {"type": "预警类", "growth_factor": 3.0, "desc": "预警记录，随业务量增长"},
    "REC": {"type": "记录/流水类", "growth_factor": 3.0, "desc": "业务记录/流水，随业务量增长"},
    "RECORD": {"type": "记录/流水类", "growth_factor": 3.0, "desc": "业务记录/流水，随业务量增长"},
    "JNL": {"type": "流水类", "growth_factor": 3.0, "desc": "业务流水，随业务量增长"},
    "JOURNAL": {"type": "流水类", "growth_factor": 3.0, "desc": "业务流水，随业务量增长"},
    "FLOW": {"type": "流水类", "growth_factor": 3.0, "desc": "业务流水，随业务量增长"},
    "EVENT": {"type": "事件类", "growth_factor": 4.0, "desc": "事件记录，随时间累积"},
    
    # 配置/字典/参数类 — 几乎不增长
    "PARAM": {"type": "配置/参数类", "growth_factor": 1.05, "desc": "系统参数配置，几乎不增长"},
    "CONFIG": {"type": "配置类", "growth_factor": 1.05, "desc": "系统配置，几乎不增长"},
    "CONF": {"type": "配置类", "growth_factor": 1.05, "desc": "系统配置，几乎不增长"},
    "DIC": {"type": "字典类", "growth_factor": 1.05, "desc": "数据字典，几乎不增长"},
    "CODE": {"type": "代码表类", "growth_factor": 1.05, "desc": "代码表，几乎不增长"},
    "CD": {"type": "代码表类", "growth_factor": 1.05, "desc": "代码表，几乎不增长"},
    "RULE": {"type": "规则配置类", "growth_factor": 1.10, "desc": "规则配置，缓慢增长"},
    "TEMPLATE": {"type": "模板类", "growth_factor": 1.05, "desc": "模板，几乎不增长"},
    "TMPL": {"type": "模板类", "growth_factor": 1.05, "desc": "模板，几乎不增长"},
    "MODEL": {"type": "模型类", "growth_factor": 1.10, "desc": "模型配置，缓慢增长"},
    "STRATEGY": {"type": "策略配置类", "growth_factor": 1.10, "desc": "策略配置，缓慢增长"},
    "POLICY": {"type": "策略配置类", "growth_factor": 1.10, "desc": "策略配置，缓慢增长"},
    "PRODUCT": {"type": "产品配置类", "growth_factor": 1.10, "desc": "产品配置，缓慢增长"},
    "PRDT": {"type": "产品配置类", "growth_factor": 1.10, "desc": "产品配置，缓慢增长"},
    "PROD": {"type": "产品配置类", "growth_factor": 1.10, "desc": "产品配置，缓慢增长"},
    "ELMT": {"type": "要素配置类", "growth_factor": 1.05, "desc": "要素配置，几乎不增长"},
    "ELEMENT": {"type": "要素配置类", "growth_factor": 1.05, "desc": "要素配置，几乎不增长"},
    "STG": {"type": "阶段配置类", "growth_factor": 1.05, "desc": "阶段配置，几乎不增长"},
    "STAGE": {"type": "阶段配置类", "growth_factor": 1.05, "desc": "阶段配置，几乎不增长"},
    "LINK": {"type": "关联配置类", "growth_factor": 1.10, "desc": "关联关系，缓慢增长"},
    "MAP": {"type": "映射关系类", "growth_factor": 1.10, "desc": "映射关系，缓慢增长"},
    "REL": {"type": "关联关系类", "growth_factor": 1.10, "desc": "关联关系，缓慢增长"},
    
    # 核心业务数据类 — 随业务量增长
    "CUST": {"type": "客户信息类", "growth_factor": 1.25, "desc": "客户信息，随客户数增长，年增长5-10%"},
    "CTR": {"type": "合同类", "growth_factor": 1.50, "desc": "合同数据，随业务量增长，年增长10-20%"},
    "CONT": {"type": "合同类", "growth_factor": 1.50, "desc": "合同数据，随业务量增长"},
    "CONTRACT": {"type": "合同类", "growth_factor": 1.50, "desc": "合同数据，随业务量增长"},
    "IOU": {"type": "借据类", "growth_factor": 1.50, "desc": "借据数据，随业务量增长"},
    "DSBR": {"type": "放款类", "growth_factor": 1.50, "desc": "放款数据，随业务量增长"},
    "DISBURSE": {"type": "放款类", "growth_factor": 1.50, "desc": "放款数据，随业务量增长"},
    "PAY": {"type": "还款/支付类", "growth_factor": 1.50, "desc": "还款/支付数据，随业务量增长"},
    "REPAY": {"type": "还款类", "growth_factor": 1.50, "desc": "还款数据，随业务量增长"},
    "REPY": {"type": "还款类", "growth_factor": 1.50, "desc": "还款数据，随业务量增长"},
    "GRANT": {"type": "授信/额度类", "growth_factor": 1.35, "desc": "授信数据，随客户数增长，年增长10-15%"},
    "CREDIT": {"type": "授信/额度类", "growth_factor": 1.35, "desc": "授信数据，随客户数增长"},
    "CRLINE": {"type": "额度类", "growth_factor": 1.35, "desc": "额度数据，随客户数增长"},
    "LIMIT": {"type": "额度类", "growth_factor": 1.35, "desc": "额度数据，随客户数增长"},
    "LMT": {"type": "额度类", "growth_factor": 1.35, "desc": "额度数据，随客户数增长"},
    "APLY": {"type": "申请类", "growth_factor": 1.50, "desc": "申请数据，随业务量增长"},
    "APPLY": {"type": "申请类", "growth_factor": 1.50, "desc": "申请数据，随业务量增长"},
    "APPR": {"type": "审批类", "growth_factor": 1.50, "desc": "审批数据，随业务量增长"},
    "APPROVE": {"type": "审批类", "growth_factor": 1.50, "desc": "审批数据，随业务量增长"},
    "REPLY": {"type": "批复类", "growth_factor": 1.50, "desc": "批复数据，随业务量增长"},
    "CHK": {"type": "检查/贷后类", "growth_factor": 1.80, "desc": "检查/贷后数据，随业务量增长，年增长20-30%"},
    "CHECK": {"type": "检查/贷后类", "growth_factor": 1.80, "desc": "检查/贷后数据，随业务量增长"},
    "INSPECT": {"type": "检查/贷后类", "growth_factor": 1.80, "desc": "检查/贷后数据，随业务量增长"},
    "POSTLOAN": {"type": "贷后类", "growth_factor": 1.80, "desc": "贷后数据，随业务量增长"},
    "PSTLOAN": {"type": "贷后类", "growth_factor": 1.80, "desc": "贷后数据，随业务量增长"},
    "LOAN": {"type": "贷款业务类", "growth_factor": 1.50, "desc": "贷款业务数据，随业务量增长"},
    "TASK": {"type": "任务类", "growth_factor": 2.00, "desc": "任务数据，随业务量增长，年增长20-30%"},
    "TSK": {"type": "任务类", "growth_factor": 2.00, "desc": "任务数据，随业务量增长"},
    "COLL": {"type": "押品类", "growth_factor": 1.40, "desc": "押品数据，随业务量增长，年增长10-15%"},
    "COLLATERAL": {"type": "押品类", "growth_factor": 1.40, "desc": "押品数据，随业务量增长"},
    "CLTL": {"type": "押品类", "growth_factor": 1.40, "desc": "押品数据，随业务量增长"},
    "ARCH": {"type": "档案类", "growth_factor": 1.55, "desc": "档案数据，随业务量增长，年增长15-20%"},
    "ARCHIVE": {"type": "档案类", "growth_factor": 1.55, "desc": "档案数据，随业务量增长"},
    "DOC": {"type": "文档类", "growth_factor": 1.55, "desc": "文档数据，随业务量增长"},
    "MARKET": {"type": "营销类", "growth_factor": 1.65, "desc": "营销数据，随活动量增长，年增长15-25%"},
    "MKT": {"type": "营销类", "growth_factor": 1.65, "desc": "营销数据，随活动量增长"},
    "CAMPAIGN": {"type": "营销类", "growth_factor": 1.65, "desc": "营销数据，随活动量增长"},
    "RATING": {"type": "评级类", "growth_factor": 1.35, "desc": "评级数据，随客户数增长"},
    "RTG": {"type": "评级类", "growth_factor": 1.35, "desc": "评级数据，随客户数增长"},
    "QUERY": {"type": "查询类", "growth_factor": 2.50, "desc": "查询记录，随业务量和监管要求增长，年增长30-50%"},
    "SIGN": {"type": "签约类", "growth_factor": 1.50, "desc": "签约数据，随业务量增长"},
    "WARRANT": {"type": "担保类", "growth_factor": 1.40, "desc": "担保数据，随业务量增长"},
    "GUARANTEE": {"type": "担保类", "growth_factor": 1.40, "desc": "担保数据，随业务量增长"},
    "GNT": {"type": "担保类", "growth_factor": 1.40, "desc": "担保数据，随业务量增长"},
    "BATCH": {"type": "批量处理类", "growth_factor": 3.00, "desc": "批量处理数据，随时间累积"},
    "BAT": {"type": "批量处理类", "growth_factor": 3.00, "desc": "批量处理数据，随时间累积"},
    "SCHED": {"type": "调度类", "growth_factor": 3.00, "desc": "调度数据，随时间累积"},
    "SCHEDULE": {"type": "调度类", "growth_factor": 3.00, "desc": "调度数据，随时间累积"},
    "REPORT": {"type": "报表类", "growth_factor": 2.00, "desc": "报表数据，随时间累积"},
    "STAT": {"type": "统计类", "growth_factor": 2.00, "desc": "统计数据，随时间累积"},
    "SUMMARY": {"type": "汇总类", "growth_factor": 1.80, "desc": "汇总数据，随业务量增长"},
    "SUM": {"type": "汇总类", "growth_factor": 1.80, "desc": "汇总数据，随业务量增长"},
    "SNAPSHOT": {"type": "快照类", "growth_factor": 2.50, "desc": "快照数据，定期生成，随时间累积"},
    "SNAP": {"type": "快照类", "growth_factor": 2.50, "desc": "快照数据，定期生成，随时间累积"},
    "MIGRATE": {"type": "迁移类", "growth_factor": 1.00, "desc": "迁移数据，一次性导入，不增长"},
    "TEMP": {"type": "临时类", "growth_factor": 1.00, "desc": "临时数据，不累积"},
    "BAK": {"type": "备份类", "growth_factor": 1.00, "desc": "备份数据，不增长"},
    "BACKUP": {"type": "备份类", "growth_factor": 1.00, "desc": "备份数据，不增长"},
    "SEQ": {"type": "序列号类", "growth_factor": 1.00, "desc": "序列号，不增长"},
    "SEQUENCE": {"type": "序列号类", "growth_factor": 1.00, "desc": "序列号，不增长"},
    "LOCK": {"type": "锁类", "growth_factor": 1.00, "desc": "分布式锁，不增长"},
    "SESSION": {"type": "会话类", "growth_factor": 1.00, "desc": "会话数据，不累积"},
}

# 模块 × 表名关键词 → 业务类型覆盖（某些模块下的特定表需要特殊处理）
MODULE_SPECIAL_RULES = {
    "系统管理": {
        # 系统管理模块下的业务表，可能不是纯配置
        "user": {"type": "用户信息类", "growth_factor": 1.15, "desc": "用户信息，随机构人员缓慢增长"},
        "role": {"type": "角色配置类", "growth_factor": 1.05, "desc": "角色配置，几乎不增长"},
        "perm": {"type": "权限配置类", "growth_factor": 1.05, "desc": "权限配置，几乎不增长"},
        "org": {"type": "机构配置类", "growth_factor": 1.05, "desc": "机构配置，几乎不增长"},
        "dept": {"type": "部门配置类", "growth_factor": 1.05, "desc": "部门配置，几乎不增长"},
        "menu": {"type": "菜单配置类", "growth_factor": 1.05, "desc": "菜单配置，几乎不增长"},
        "resource": {"type": "资源配置类", "growth_factor": 1.05, "desc": "资源配置，几乎不增长"},
    },
    "工作流程库": {
        # Activiti表
        "act_ge": {"type": "工作流配置类", "growth_factor": 1.05, "desc": "Activiti通用配置，几乎不增长"},
        "act_re": {"type": "工作流定义类", "growth_factor": 1.05, "desc": "Activiti流程定义，几乎不增长"},
        "act_ru": {"type": "工作流运行时类", "growth_factor": 2.00, "desc": "Activiti运行时数据，随当前活跃业务量"},
        "act_hi": {"type": "工作流历史类", "growth_factor": 4.00, "desc": "Activiti历史数据，随业务量累积增长"},
    },
    "信贷引擎库": {
        "rule": {"type": "规则配置类", "growth_factor": 1.10, "desc": "规则配置，缓慢增长"},
        "decision": {"type": "决策结果类", "growth_factor": 2.50, "desc": "决策结果，随业务量增长"},
        "score": {"type": "评分结果类", "growth_factor": 2.50, "desc": "评分结果，随业务量增长"},
    },
    "风控中心库": {
        "rule": {"type": "风控规则类", "growth_factor": 1.10, "desc": "风控规则，缓慢增长"},
        "model": {"type": "风控模型类", "growth_factor": 1.10, "desc": "风控模型，缓慢增长"},
    },
    "客户中心库": {
        "ecif": {"type": "客户信息类", "growth_factor": 1.25, "desc": "ECIF客户数据，随客户数增长"},
    },
    "额度中心库": {
        "ulm": {"type": "额度类", "growth_factor": 1.35, "desc": "额度数据，随客户和业务量增长"},
        "crlmt": {"type": "额度类", "growth_factor": 1.35, "desc": "额度数据，随客户和业务量增长"},
    },
    "电子文档库": {
        "elec": {"type": "电子文档类", "growth_factor": 1.55, "desc": "电子文档，随业务量增长"},
        "doc": {"type": "电子文档类", "growth_factor": 1.55, "desc": "电子文档，随业务量增长"},
    },
    "统一认证库": {
        "auth": {"type": "认证配置类", "growth_factor": 1.05, "desc": "认证配置，几乎不增长"},
        "sso": {"type": "认证配置类", "growth_factor": 1.05, "desc": "单点登录配置，几乎不增长"},
        "token": {"type": "令牌类", "growth_factor": 1.00, "desc": "令牌数据，不累积"},
    },
}

# 分区阈值
PARTITION_THRESHOLD = 10_000_000  # 1000万
MAX_PARTITION_COUNT = 50
ROWS_PER_PARTITION = 3_000_000  # 300万

# ==================== 分析逻辑 ====================

def get_business_type(table_en, table_cn, module, columns):
    """
    根据表名、模块、字段结构分析业务类型
    返回: (type_name, growth_factor, description)
    """
    table_en_upper = table_en.upper()
    table_cn_upper = table_cn.upper() if table_cn else ""
    
    # 1. 先检查模块特殊规则
    if module in MODULE_SPECIAL_RULES:
        for keyword, rule in MODULE_SPECIAL_RULES[module].items():
            if keyword.upper() in table_en_upper:
                return rule["type"], rule["growth_factor"], rule["desc"]
    
    # 2. 检查表名关键词（按优先级）
    # 首先排除特殊误判：undo_log、base_ddct等
    if table_en_upper == "UNDO_LOG":
        return "中间件日志类", 3.00, "Seata AT模式undo日志，随时间累积，但数据量相对可控"
    if "DDCT" in table_en_upper or "DICT" in table_en_upper:
        return "字典类", 1.05, "数据字典，几乎不增长"
    
    # 高优先级：日志/审计/历史（但要排除CODE/CD等已被配置类覆盖的）
    high_priority = ["AUDIT", "HISTORY", "TRACE", "ACT_HI", "EVENT", "MSG", "MESSAGE", "NOTIFY", "ALERT", "WARN"]
    for kw in high_priority:
        if kw in table_en_upper:
            matched = BUSINESS_TYPE_KEYWORDS.get(kw, {"type": "日志/审计类", "growth_factor": 5.0, "desc": "审计/历史记录"})
            return matched["type"], matched["growth_factor"], matched["desc"]
    
    # LOG关键词特殊处理：排除一些非高数据量的LOG
    if "LOG" in table_en_upper:
        # 排除：undo_log, catalog, 等
        if "CATALOG" in table_en_upper or "UNDO" in table_en_upper:
            return "中间件日志类", 3.00, "中间件日志，随时间累积"
        return "日志/审计类", 4.00, "操作日志/审计日志，随时间线性增长"
    
    # 中优先级：配置/字典类（先检查CODE/CD避免被HIS等误匹配）
    config_keywords = ["PARAM", "CONFIG", "CONF", "DIC", "CODE", "CD", "TEMPLATE", "TMPL", "ELMT", "ELEMENT", "STG", "STAGE", "RULE", "MODEL", "STRATEGY", "POLICY", "PRODUCT", "PRDT", "PROD"]
    for kw in config_keywords:
        if kw in table_en_upper:
            matched = BUSINESS_TYPE_KEYWORDS[kw]
            return matched["type"], matched["growth_factor"], matched["desc"]
    
    # 3. 检查字段结构中的业务字段，推断业务类型
    field_names = [c["name"].upper() for c in columns]
    field_names_str = " ".join(field_names)
    
    # 检查是否有业务主键字段（按优先级：更具体的业务类型优先）
    has_ctrt_no = "CTRT_NO" in field_names
    has_cust_no = "CUST_NO" in field_names
    has_bus_no = "BUS_NO" in field_names
    has_iou_no = "IOU_NO" in field_names
    has_aply_no = "APLY_NO" in field_names
    has_tsk_no = "TSK_NO" in field_names
    has_ars_no = "ARS_NO" in field_names
    has_lmt_no = "LMT_NO" in field_names
    has_create_time = "CREATE_TIME" in field_names or "CRT_TIME" in field_names or "CRT_DT" in field_names
    
    # 优先检查更具体的业务类型：任务、档案、借据先于合同/客户
    # 注意：部分表可能同时有TSK_NO和CTRT_NO，以更具体的为准
    if has_tsk_no:
        return "任务类", 2.00, "包含任务编号字段，任务数据，随业务量增长"
    if has_ars_no:
        return "档案类", 1.55, "包含档案编号字段，档案数据，随业务量增长"
    if has_iou_no:
        return "借据类", 1.50, "包含借据编号字段，借据数据，随业务量增长"
    if has_aply_no:
        return "申请类", 1.50, "包含申请编号字段，申请数据，随业务量增长"
    if has_lmt_no:
        return "额度类", 1.35, "包含额度编号字段，额度数据，随客户数增长"
    if has_ctrt_no:
        return "合同类", 1.50, "包含合同编号字段，核心合同数据，随业务量增长"
    if has_bus_no:
        return "业务类", 1.50, "包含业务编号字段，业务流水数据"
    if has_cust_no:
        return "客户信息类", 1.25, "包含客户编号字段，客户相关数据，随客户数增长"
    
    # 4. 检查其他业务关键词（按优先级：更具体的优先）
    business_keywords = [
        "TASK", "TSK", "CHK", "CHECK", "INSPECT", "POSTLOAN", "PSTLOAN",
        "IOU", "APLY", "APPLY", "APPR", "APPROVE", "REPLY",
        "CUST", "CTR", "CONT", "CONTRACT", "DSBR", "DISBURSE", "PAY", "REPAY", "REPY",
        "GRANT", "CREDIT", "CRLINE", "LIMIT", "LMT",
        "LOAN", "COLL", "COLLATERAL", "CLTL", "ARCH", "ARCHIVE", "DOC", "MARKET", "MKT", "CAMPAIGN",
        "RATING", "RTG", "QUERY", "SIGN", "WARRANT", "GUARANTEE", "GNT",
        "BATCH", "BAT", "SCHED", "SCHEDULE", "REPORT", "STAT", "SUMMARY", "SUM", "SNAPSHOT", "SNAP"
    ]
    for kw in business_keywords:
        if kw in table_en_upper:
            matched = BUSINESS_TYPE_KEYWORDS.get(kw, {"type": "业务数据类", "growth_factor": 1.50, "desc": "业务数据"})
            return matched["type"], matched["growth_factor"], matched["desc"]
    
    # 5. 默认：根据模块判断
    if module in ["产品管理", "架构管理"]:
        return "配置类", 1.05, "配置数据，几乎不增长"
    elif module in ["贷后管理", "线上贷款"]:
        return "业务数据类", 1.80, "业务数据，随业务量增长"
    elif module in ["系统管理"]:
        return "配置类", 1.05, "系统管理类配置，几乎不增长"
    elif module in ["营销管理"]:
        return "营销类", 1.65, "营销数据，随活动量增长"
    elif module in ["批量管理"]:
        return "批量处理类", 3.00, "批量处理数据，随时间累积"
    else:
        return "业务数据类", 1.50, "业务数据，随业务量增长"


def estimate_3_5_year_volume(table_en, current_volume, growth_factor, business_type):
    """
    预估3-5年数据量
    """
    en_lower = table_en.lower()
    
    if en_lower in volume_map:
        # 有生产数据，基于生产数据预估
        current = volume_map[en_lower]
        # 使用增长系数
        estimated = int(current * growth_factor)
        return estimated, current, growth_factor
    else:
        # 无生产数据，新系统新增表
        # 根据业务类型和模块估算，保守估算：新系统上线3-5年，数据量不会太大
        if "日志" in business_type or "审计" in business_type:
            # 新系统日志：假设日均500条，5年 = 500 * 365 * 5 = 912,500，但考虑峰值，按200万估算
            estimated = 2_000_000
        elif "历史" in business_type or "轨迹" in business_type:
            estimated = 5_000_000  # 变更历史类，保守估计
        elif "中间件日志" in business_type:
            estimated = 5_000_000  # undo_log、catalog等中间件日志
        elif "配置" in business_type or "字典" in business_type or "代码" in business_type:
            estimated = 5_000  # 配置类数据量很小
        elif "模型" in business_type or "规则" in business_type or "策略" in business_type:
            estimated = 5_000
        elif "客户" in business_type:
            estimated = 500_000  # 新系统客户相关表，500万客户规模
        elif "合同" in business_type or "借据" in business_type:
            estimated = 2_000_000  # 新系统合同相关表
        elif "放款" in business_type or "还款" in business_type:
            estimated = 1_000_000
        elif "押品" in business_type:
            estimated = 500_000
        elif "贷后" in business_type or "检查" in business_type:
            estimated = 1_000_000
        elif "任务" in business_type:
            estimated = 2_000_000
        elif "额度" in business_type:
            estimated = 500_000
        elif "申请" in business_type or "审批" in business_type:
            estimated = 1_000_000
        elif "消息" in business_type or "通知" in business_type:
            estimated = 5_000_000
        elif "批量" in business_type:
            estimated = 3_000_000
        elif "流水" in business_type or "记录" in business_type:
            estimated = 2_000_000
        elif "营销" in business_type:
            estimated = 500_000
        elif "文档" in business_type or "档案" in business_type:
            estimated = 1_000_000
        elif "报表" in business_type or "统计" in business_type:
            estimated = 500_000
        elif "工作流" in business_type:
            estimated = 3_000_000
        elif "事件" in business_type:
            estimated = 2_000_000
        else:
            estimated = 500_000  # 默认保守估计
        
        return estimated, 0, growth_factor


def select_partition_key(table_en, columns, business_type):
    """
    选择分区键——排除TENANT_ID，优先业务主键
    """
    field_names = [c["name"].upper() for c in columns]
    field_set = set(field_names)
    
    # 排除 TENANT_ID
    # 优先级顺序：业务主键 > 流水号 > 编号字段 > 时间字段
    
    # 日志类/审计类：优先使用 CREATE_TIME
    if "日志" in business_type or "审计" in business_type or "历史" in business_type:
        for time_field in ["CREATE_TIME", "CRT_TIME", "CRT_DT", "CREATE_DATE", "OPR_TIME", "UPD_TIME"]:
            if time_field in field_set:
                return time_field, "时间字段", f"日志/审计类表，按{time_field}时间分区，3个月一个分区"
    
    # 优先级1：明确的业务主键
    # TSK_NO/ARS_NO优先于CTRT_NO（任务表、档案表可能有多个业务键）
    # DOC_NO放最后（很多表都有文档编号字段，但不适合做分区键）
    priority_1 = ["TSK_NO", "CHK_TASK_NO", "ARS_NO", "CTRT_NO", "CUST_NO", "IOU_NO", "BUS_NO", "APLY_NO", "LMT_NO", "CRLMT_NO", "CLTR_NO", "PRDT_NO", "MKT_TSK_NO", "QUERY_NO", "DOC_NO"]
    for pk in priority_1:
        if pk in field_set:
            return pk, "业务主键", f"第1优先级业务主键{pk}，基数高、分布均匀"
    
    # 优先级2：其他编号类字段
    priority_2 = ["CUST_INTL_SEQ_NO", "ECIF_CUST_NO", "CONTRACT_NO", "AGREEMENT_NO", "APPLY_NO", "ORDER_NO", "SEQ_NO", "SERIAL_NO", "TRANS_NO", "FLOW_NO", "BATCH_NO", "TASK_ID", "PROC_INST_ID", "EXECUTION_ID"]
    for pk in priority_2:
        if pk in field_set:
            return pk, "编号字段", f"第2优先级编号字段{pk}，分布较均匀"
    
    # 优先级3：时间字段
    priority_3 = ["CREATE_TIME", "CRT_TIME", "CRT_DT", "CREATE_DATE", "BUSI_DATE", "TRANS_DATE", "ACCT_DATE"]
    for pk in priority_3:
        if pk in field_set:
            return pk, "时间字段", f"第3优先级时间字段{pk}，按时间分区"
    
    # 优先级4：ID字段（如果基数足够）
    if "ID" in field_set:
        return "ID", "主键ID", "第4优先级主键ID，作为兜底分区键"
    
    return "待确认", "无合适字段", "未找到合适的分区键字段，需人工确认"


def calculate_partition_count(estimated_volume, business_type, partition_key):
    """计算分区数"""
    if "日志" in business_type or "审计" in business_type or "历史" in business_type:
        # 如果分区键是时间字段，返回0表示按时间自动创建
        if partition_key in ["CREATE_TIME", "CRT_TIME", "CRT_DT", "CREATE_DATE", "OPR_TIME", "UPD_TIME"]:
            return 0, "按时间自动创建"
    
    count = math.ceil(estimated_volume / ROWS_PER_PARTITION)
    count = max(1, min(count, MAX_PARTITION_COUNT))
    return count, "按HASH分区"


def generate_partition_strategy(partition_key, partition_count, business_type):
    """生成分区策略描述"""
    if partition_count == 0:
        return f"按{partition_key}时间分区，3个月一个分区，保留3年数据，按时间自动创建分区"
    else:
        return f"按{partition_key} HASH分区，初始{partition_count}个分区，后续按需扩容"


# ==================== 主分析流程 ====================

def analyze_all_tables():
    results = []
    stats = {
        "total_tables": len(tables),
        "need_partition": 0,
        "no_partition": 0,
        "matched_prod_data": 0,
        "new_tables": 0,
        "by_module": defaultdict(lambda: {"total": 0, "need_partition": 0}),
        "by_business_type": defaultdict(int),
    }
    
    for table_cn, table_info in tables.items():
        table_en = table_info["table_en"]
        module = table_info["module"]
        columns = table_info["columns"]
        
        # 获取业务类型和增长系数
        business_type, growth_factor, type_desc = get_business_type(table_en, table_cn, module, columns)
        
        # 预估3-5年数据量
        estimated_volume, current_volume, actual_factor = estimate_3_5_year_volume(table_en, 0, growth_factor, business_type)
        
        # 判断是否需要分区
        need_partition = estimated_volume > PARTITION_THRESHOLD
        
        # 记录统计
        stats["by_module"][module]["total"] += 1
        stats["by_business_type"][business_type] += 1
        
        if table_en.lower() in volume_map:
            stats["matched_prod_data"] += 1
        else:
            stats["new_tables"] += 1
        
        if need_partition:
            stats["need_partition"] += 1
            stats["by_module"][module]["need_partition"] += 1
            
            # 选择分区键
            partition_key, key_source, key_reason = select_partition_key(table_en, columns, business_type)
            
            # 计算分区数
            partition_count, count_method = calculate_partition_count(estimated_volume, business_type, partition_key)
            
            # 生成分区策略
            strategy = generate_partition_strategy(partition_key, partition_count, business_type)
            
            # 构建备注
            if current_volume > 0:
                remark = f"类型：{business_type}；当前数据量：{current_volume}；预估3-5年：{estimated_volume}；增长系数：{actual_factor:.2f}；分区键：{key_reason}"
            else:
                remark = f"类型：{business_type}；预估3-5年：{estimated_volume}（新系统新增，预估）；分区键：{key_reason}"
            
            results.append({
                "table_cn": table_cn,
                "table_en": table_en,
                "module": module,
                "need_partition": True,
                "business_type": business_type,
                "current_volume": current_volume,
                "estimated_volume": estimated_volume,
                "growth_factor": actual_factor,
                "partition_key": partition_key,
                "partition_count": partition_count if partition_count > 0 else "0（按时间自动）",
                "partition_strategy": strategy,
                "remark": remark,
                "type_desc": type_desc,
            })
        else:
            stats["no_partition"] += 1
            
            if current_volume > 0:
                remark = f"类型：{business_type}；当前数据量：{current_volume}；预估3-5年：{estimated_volume}；增长系数：{actual_factor:.2f}；未达1000万分区阈值"
            else:
                remark = f"类型：{business_type}；预估3-5年：{estimated_volume}（新系统新增，预估）；未达1000万分区阈值"
            
            results.append({
                "table_cn": table_cn,
                "table_en": table_en,
                "module": module,
                "need_partition": False,
                "business_type": business_type,
                "current_volume": current_volume,
                "estimated_volume": estimated_volume,
                "growth_factor": actual_factor,
                "partition_key": "",
                "partition_count": "",
                "partition_strategy": "",
                "remark": remark,
                "type_desc": type_desc,
            })
    
    # 输出结果
    output = {
        "stats": {
            "总表数": stats["total_tables"],
            "需分区": stats["need_partition"],
            "不分区": stats["no_partition"],
            "分区占比": f"{stats['need_partition']/stats['total_tables']*100:.1f}%",
            "匹配生产数据": stats["matched_prod_data"],
            "新系统新增": stats["new_tables"],
            "按模块": {k: v for k, v in stats["by_module"].items()},
            "按业务类型": dict(stats["by_business_type"]),
        },
        "tables": results,
    }
    
    with open(os.path.join(BASE_DIR, "ai_analysis_result.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # 打印统计
    print("=" * 60)
    print("AI 业务语义分析结果")
    print("=" * 60)
    print(f"总表数: {stats['total_tables']}")
    print(f"需分区: {stats['need_partition']} ({stats['need_partition']/stats['total_tables']*100:.1f}%)")
    print(f"不分区: {stats['no_partition']} ({stats['no_partition']/stats['total_tables']*100:.1f}%)")
    print(f"匹配生产数据: {stats['matched_prod_data']}")
    print(f"新系统新增: {stats['new_tables']}")
    print()
    print("按模块统计:")
    for module, counts in sorted(stats["by_module"].items()):
        pct = counts["need_partition"] / counts["total"] * 100 if counts["total"] > 0 else 0
        print(f"  {module}: {counts['total']}张表, 需分区{counts['need_partition']}张 ({pct:.1f}%)")
    print()
    print("按业务类型统计:")
    for btype, count in sorted(stats["by_business_type"].items(), key=lambda x: -x[1]):
        print(f"  {btype}: {count}张表")
    print()
    print("需分区Top 20表（按预估数据量）:")
    partition_tables = sorted([t for t in results if t["need_partition"]], key=lambda x: -x["estimated_volume"])
    for i, t in enumerate(partition_tables[:20]):
        print(f"  {i+1}. {t['table_cn']}({t['table_en']}): 预估{t['estimated_volume']:,}行, 分区键={t['partition_key']}, 分区数={t['partition_count']}, 类型={t['business_type']}")
    
    return output


if __name__ == "__main__":
    analyze_all_tables()