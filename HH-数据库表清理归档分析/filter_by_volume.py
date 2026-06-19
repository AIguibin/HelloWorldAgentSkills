# -*- coding: utf-8 -*-
"""
基于行业经验判断144张表的数据量级别和增长趋势
排除非大表/非快速增长表,保留3-5年成为大表的表

行业经验判断依据:
- 大表标准: 3-5年内数据量达到百万级(100万+)或千万级(1000万+)
- 快速增长: 每年增长10万+记录
- 排除: 配置类/主数据类/低频业务类/关联关系类(数据量小且增长慢)
"""
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

SRC = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\DD-湖北农信基础配置检核\湖北农信清理归档表清单_维度分析.xlsx'


def judge_data_volume(table_en, table_cn, module):
    """基于行业经验判断表的数据量级别和增长趋势
    返回: (是否保留, 数据量级别, 增长趋势, 排除理由)
    """
    name = str(table_en).upper()
    cn = str(table_cn)

    # ===== 1. 必须保留的大表/快速增长表 =====

    # 1.1 日志类 - 增长极快(千万级/年),每次操作产生记录
    log_keywords = ['_LOG', 'LOG_', '_LOGS', 'LOGS_', 'LOG_DETAILS', 'LOG_REPORT', 'LOG_BACKUP']
    if any(kw in name for kw in log_keywords):
        return (True, '千万级', '极快(每次操作产生记录)', '')
    if '日志' in cn or '审计' in cn or '回滚' in cn:
        return (True, '千万级', '极快(每次操作产生记录)', '')

    # 1.2 明细类 - 增长快(百万级/年),随业务交易增长
    if '_DTL' in name or '_DETAIL' in name or '_DETAILS' in name:
        # 排除配置明细
        if 'CFG' in name or 'CONFIG' in name or 'PARAM' in name:
            return (False, '万级', '慢(配置数据)', '配置明细表,数据量小且不增长')
        return (True, '百万级', '快(随业务交易增长)', '')

    # 1.3 变更记录/历史类 - 增长较快(十万级/年),每次变更产生记录
    if '_CHG' in name or '_CHANGE' in name or '_HIS' in name or '_HIST' in name:
        return (True, '十万级', '较快(每次变更产生记录)', '')
    if '变更' in cn or '历史' in cn or '记录' in cn:
        return (True, '十万级', '较快(每次变更产生记录)', '')

    # 1.4 征信信息单元 - 增长快(百万级/年),每次申请查询征信
    if name.startswith('E_R_') or name.startswith('I_R_'):
        return (True, '百万级', '快(每次申请查询征信产生)', '')

    # 1.5 风控决策类 - 增长快(百万级/年),每次申请产生决策记录
    if 'RISK_RULE_INPUT_RESULT' in name or 'DECISION' in name:
        return (True, '百万级', '快(每次申请产生决策记录)', '')
    if 'RISK_REQUEST_MESSAGE' in name or 'REQUEST_MESSAGE' in name:
        return (True, '百万级', '快(风控轮询任务,高频)', '')

    # 1.6 流程任务类 - 增长快(百万级/年),每笔业务多节点
    if 'ACT_RU_TASK' in name or 'RUNTIME_TASK' in name:
        return (True, '百万级', '快(每笔业务多流程节点)', '')
    if 'WF_TASK_EXPAND' in name or 'TASK_EXPAND' in name:
        return (True, '百万级', '快(流程待办扩展数据)', '')

    # 1.7 营销名单类 - 增长快(百万级),营销活动客户量大
    if 'CMPN_' in name and ('NMLST' in name or 'CST' in name or 'COLO' in name):
        return (True, '百万级', '快(营销活动客户量大)', '')
    if ('营销' in cn or '活动' in cn) and '白名单' not in cn:
        return (True, '百万级', '快(营销活动客户量大)', '')
    if '名单' in cn and '白名单' not in cn and '黑名单' not in cn:
        return (True, '百万级', '快(营销活动客户量大)', '')

    # 1.8 贷后检查/预警类 - 增长较快(十万级/年)
    # 排除预警映射/规则配置/解除信息/信号表(量小或不增长)
    warn_exclude = ('MPNG' in name or '映射' in cn or 'RLV_RULE' in name or '解除规则' in cn
                    or 'RLV_INF_PRIM' in name or '解除信息主表' in cn
                    or 'SGNL_TBL' in name or '预警信号' in cn)
    if ('WARN' in name or '预警' in cn) and not warn_exclude:
        return (True, '十万级', '较快(贷后预警信号)', '')
    if 'ALARM' in name or '告警' in cn:
        return (True, '十万级', '较快(监控告警)', '')

    # 1.9 客户财报数据 - 增长较快(十万级/年),定期更新
    if 'FL_INDEX_DATA' in name or '财报' in cn:
        return (True, '十万级', '较快(财报定期更新)', '')

    # 1.10 客户指标数据 - 增长较快(十万级/年)
    # 排除利率定价指标/评级指标(量小,定期计算)
    if ('INDEX_DATA' in name or '指标' in cn) and 'CFG' not in name and 'CONFIG' not in name:
        if 'INTRT_PCNM' not in name and '利率定价' not in cn and 'RTG_IDX' not in name and '评级指标' not in cn:
            if 'SINGLE_INDEX' not in name and '单项指标' not in cn:
                return (True, '十万级', '较快(客户指标定期计算)', '')

    # 1.11 联网核查记录 - 增长快(百万级/年),每次开户/贷款核查
    if 'NETWORK_CHECK' in name or '联网核查' in cn:
        return (True, '百万级', '快(每次开户/贷款核查)', '')

    # 1.12 客户合并/停用记录 - 中等增长(万级/年)
    if 'MERGER' in name or 'MRG' in name or '合并' in cn:
        return (True, '万级', '中等(客户合并低频但需保留)', '')
    if 'DEACT' in name or '停用' in cn:
        return (True, '万级', '中等(客户停用记录)', '')

    # 1.13 担保情况/对外担保 - 中等增长(万级/年)
    if 'GUAT' in name or '担保情况' in cn:
        return (True, '万级', '中等(对外担保情况)', '')

    # 1.14 申请人授信情况 - 中等增长(万级/年)
    if 'PROPOSER_INFO' in name or '申请人授信' in cn:
        return (True, '万级', '中等(申请人授信情况)', '')

    # ===== 2. 必须排除的非大表 =====

    # 2.1 配置参数类 - 不增长
    config_patterns = ['_CFG', '_CONFIG', 'CONFIG_', '_PARAM', 'PARAM_', '_SETTING', 'SETTING_']
    if any(p in name for p in config_patterns):
        return (False, '千级', '不增长(配置数据)', '配置参数表,数据量极小且不增长')
    if '配置' in cn or '参数' in cn:
        return (False, '千级', '不增长(配置数据)', '配置参数表,数据量极小且不增长')

    # 2.2 押品种类/必输项配置 - 不增长
    if 'CLT_CTLG' in name or '种类配置' in cn:
        return (False, '百级', '不增长(字典数据)', '押品种类配置,字典数据')
    if 'RQFLD' in name or '必输项' in cn:
        return (False, '百级', '不增长(配置数据)', '押品必输项配置')

    # 2.3 系统通用参数/流程定义资源 - 不增长
    if 'ACT_GE_PROPERTY' in name or '通用参数' in cn:
        return (False, '十级', '不增长(系统参数)', '系统通用参数,极少量数据')
    if 'ACT_GE_BYTEARRAY' in name or '流程定义' in cn:
        return (False, '百级', '慢(流程部署时产生)', '流程定义资源,部署时产生')

    # 2.4 用户组/用户扩展信息 - 缓慢增长
    if 'ACT_ID_GROUP' in name or '用户组' in cn:
        return (False, '百级', '极慢(用户组有限)', '用户组数量有限,不增长')
    if 'ACT_ID_INFO' in name or '用户扩展' in cn:
        return (False, '千级', '慢(随用户增长)', '用户扩展信息,随用户缓慢增长')

    # 2.5 白名单类 - 不增长或极慢
    if 'WHITE_LIST' in name or 'WHITELIST' in name or '白名单' in cn:
        return (False, '万级', '慢(维护性数据)', '白名单表,维护性数据,增长极慢')

    # 2.6 映射关系类 - 不增长
    if '_REGION' in name and 'MAPPING' in cn:
        return (False, '千级', '不增长(映射配置)', '映射关系配置,不增长')
    if 'MAPPING' in name or '映射' in cn:
        return (False, '千级', '不增长(映射配置)', '映射关系配置')
    if 'ORG_FRBANK' in name or '机构映射' in cn:
        return (False, '百级', '不增长(机构映射)', '机构映射配置,数量有限')
    if 'BUSINESS_ADDRESS_REGION' in name:
        return (False, '千级', '不增长(映射配置)', '登记机关与法人行映射,配置数据')
    if 'CERT_NO_FIRST6_REGION' in name:
        return (False, '千级', '不增长(映射配置)', '身份证号与法人行映射,配置数据')
    if 'WARN_MPNG' in name or '预警映射' in cn:
        return (False, '百级', '不增长(映射配置)', '预警映射配置,配置数据')

    # 2.7 征信查询用户映射 - 不增长
    if 'RISK_CREDIT_CUST_REL' in name or '征信查询用户映射' in cn:
        return (False, '百级', '不增长(映射配置)', '征信查询用户映射,配置数据')

    # 2.8 场景模型映射 - 不增长
    if 'SCENE_MODEL_REL' in name or '场景模型映射' in cn:
        return (False, '百级', '不增长(映射配置)', '场景模型映射,配置数据')

    # 2.9 风控机构信息 - 缓慢增长
    if 'RISK_ORG_INFO' in name or '风控机构' in cn:
        return (False, '百级', '极慢(机构有限)', '风控机构信息,机构数量有限')

    # 2.10 客户基本信息(主数据) - 缓慢增长
    if 'RISK_CUST_BASE_INF' in name or '客户信息表' in cn:
        return (False, '十万级', '慢(随客户增长)', '客户基本信息主数据,随客户缓慢增长')
    if 'E_R_BSCINF' in name or '基本概况' in cn:
        return (False, '十万级', '慢(随征信查询)', '征信基本概况,随查询缓慢增长')

    # 2.11 客户关联人信息 - 中等增长但量小
    if 'RISK_CUST_REL_INF' in name or '客户关联人' in cn:
        return (False, '万级', '中等(关联人有限)', '客户关联人信息,每客户1-3条')

    # 2.12 押品基本信息 - 缓慢增长(随贷款笔数)
    if 'B_COL_BASE_INFO' in name or '基本信息表' in cn:
        return (False, '万级', '慢(随贷款笔数)', '押品基本信息,随贷款笔数缓慢增长')

    # 2.13 不动产查询类 - 低频查询
    if 'CERTNO' in name and ('OBJTN' in name or 'SEACUR' in name or 'SEALUP' in name):
        return (False, '万级', '慢(低频查询)', '不动产查询信息,低频查询产生')

    # 2.14 押品管理流程信息 - 中等增长
    if 'B_COL_ALRDYEFF_MOD' in name or '押品管理流程' in cn:
        return (False, '万级', '慢(随押品业务)', '押品管理流程,随押品业务缓慢增长')

    # 2.15 押品房产云评估预警 - 低频
    if 'CLTL_HSPTY_CLOU_ASES_VAL_CHG_WARN' in name or '价值变动预警' in cn:
        return (False, '万级', '慢(低频评估)', '押品价值变动预警,低频评估产生')

    # 2.16 资产证券化/处置方案类 - 极低频业务
    if 'B_AP_ABS_' in name or '资产证券化' in cn:
        return (False, '百级', '极慢(低频业务)', '资产证券化方案,极低频业务,每年几十条')
    if 'B_AP_ASSET_' in name or '资产处置' in cn or '资产转让' in cn:
        return (False, '百级', '极慢(低频业务)', '资产处置/转让方案,极低频业务')
    if 'B_AP_ASSET_PLAN_' in name or '方案申请' in cn:
        return (False, '百级', '极慢(低频业务)', '资产处置方案申请,极低频业务')

    # 2.17 共同申请人/共借人/委托人 - 中等增长但量小
    if 'JNT_APLY_PSN_INF' in name or '共同申请人' in cn:
        return (False, '万级', '中等(每笔1-3条)', '共同申请人,每笔业务1-3条')
    if 'CO_BORROWER' in name or '共借人' in cn:
        return (False, '万级', '中等(每笔1-3条)', '共借人信息,每笔业务1-3条')
    if 'TRSTR_INFO' in name or '委托人' in cn:
        return (False, '万级', '中等(每笔1-3条)', '委托人信息,每笔业务1-3条')

    # 2.18 用信审查/流程条件 - 中等增长
    if 'USE_EXAM' in name or '审查表' in cn:
        return (False, '万级', '中等(随用信笔数)', '用信审查表,随用信笔数增长')
    if 'USE_PCS_CD_INF' in name or '流程条件' in cn:
        return (False, '万级', '中等(随用信笔数)', '用信流程条件,随用信笔数增长')

    # 2.19 用信投向行业/绿色贷款分类 - 中等增长
    if 'IVSIN_IDY_INF' in name or '投向行业' in cn:
        return (False, '万级', '中等(随用信笔数)', '用信投向行业,随用信笔数增长')
    if 'GRN_LOAN' in name or '绿色贷款' in cn:
        return (False, '万级', '中等(随用信笔数)', '绿色贷款分类,随用信笔数增长')

    # 2.20 个人房屋装修贷款表 - 中等增长
    if 'HS_DCRT_LOAN' in name or '房屋装修贷款' in cn:
        return (False, '万级', '中等(随贷款笔数)', '房屋装修贷款,随贷款笔数增长')

    # 2.21 楚天贷款码企业科创积分 - 低频
    if 'LOANAD_ENTPSCIINNO' in name or '科创积分' in cn:
        return (False, '千级', '慢(低频业务)', '企业科创积分,低频业务')

    # 2.22 中征平台对接类 - 低频外部对接
    if 'OL_CC_' in name or '中征' in cn:
        return (False, '万级', '慢(外部平台对接)', '中征平台对接数据,外部平台低频同步')

    # 2.23 标签方案/标签数据 - 缓慢增长
    if 'REGIDX_SCHEME' in name or '标签方案' in cn:
        return (False, '百级', '不增长(方案配置)', '标签方案配置,不增长')
    if 'REGIDX_DATA' in name or '标签数据' in cn:
        return (False, '万级', '慢(随客户增长)', '标签数据,随客户缓慢增长')

    # 2.24 产品发布历史 - 低频
    if 'PROD_ELMT_DTL_ANC_HIST' in name or '产品要素发布历史' in cn:
        return (False, '百级', '极慢(产品发布时)', '产品要素发布历史,产品发布时产生')
    if 'PROD_PD_INF_ANC_HIST' in name or '产品信息发布历史' in cn:
        return (False, '百级', '极慢(产品发布时)', '产品信息发布历史,产品发布时产生')

    # 2.25 QA记录表 - 低频
    if 'QA_RECORD' in name or '记录表' == cn:
        return (False, '千级', '慢(低频记录)', 'QA记录表,低频记录')

    # 2.26 变量修改历史 - 低频
    if 'DATAPARAMS_HIS' in name or '变量修改历史' in cn:
        return (False, '千级', '极慢(变量变更时)', '变量修改历史,变量变更时产生')

    # 2.27 客户入股情况 - 低频
    if 'OURBNK_JOIN_STK_STTN' in name or '入股情况' in cn:
        return (False, '千级', '极慢(低频业务)', '本行入股情况,低频业务')

    # 2.28 企业异常名录 - 低频
    if 'ENTP_ABNML_NM_REC' in name or '异常名录' in cn:
        return (False, '千级', '慢(低频查询)', '企业异常名录,低频查询')

    # 2.29 企业水电气费缴纳明细 - 中等增长
    if 'ELCTRFEE_PAY_DTL' in name or '电费缴纳' in cn:
        return (False, '万级', '中等(定期更新)', '企业电费缴纳明细,定期更新')
    if 'GS_FEE_PAY_DTL' in name or '燃气费缴纳' in cn:
        return (False, '万级', '中等(定期更新)', '企业燃气费缴纳明细,定期更新')
    if 'WTRFEE_PAY_DTL' in name or '水费缴纳' in cn:
        return (False, '万级', '中等(定期更新)', '企业水费缴纳明细,定期更新')

    # 2.30 集群客户贷款情况 - 低频
    if 'CLSTR_LOAN_STTN' in name or '集群贷款情况' in cn:
        return (False, '千级', '慢(低频业务)', '集群客户贷款情况,低频业务')

    # 2.31 集群客户变更历史 - 低频
    if 'COLO_HISTORY' in name or '集群客户变更历史' in cn:
        return (False, '千级', '慢(低频变更)', '集群客户变更历史,低频变更')

    # 2.32 支行管辖村组 - 不增长
    if 'BRANCH_JURISDICTION_GROUP' in name or '管辖村组' in cn:
        return (False, '千级', '不增长(配置数据)', '支行管辖村组,配置数据')

    # 2.33 放款账务异常 - 低频
    if 'ACG_ABNML_INFO' in name or '账务异常' in cn:
        return (False, '千级', '慢(异常低频)', '放款账务异常,异常情况低频产生')

    # 2.34 调阅纸质资料登记 - 低频
    if 'ACCS_PAP' in name or '调阅纸质资料' in cn:
        return (False, '千级', '慢(低频调阅)', '调阅纸质资料登记,低频调阅')

    # 2.35 合同状态任务表 - 中等增长
    if 'CNTR_STS_TSK_TBL' in name or '合同状态任务' in cn:
        return (False, '万级', '中等(随合同笔数)', '合同状态任务,随合同笔数增长')

    # 2.36 合同撤销废止终止明细 - 低频
    if 'UDO_REPL_TMT_DTL' in name or '撤销废止终止' in cn:
        return (False, '千级', '慢(低频业务)', '合同撤销废止终止,低频业务')

    # 2.37 合同签订明细 - 中等增长
    if 'CONT_SIGN_DTL' in name or '合同签订明细' in cn:
        return (False, '万级', '中等(随合同笔数)', '合同签订明细,随合同笔数增长')

    # 2.38 批量开户明细 - 低频
    if 'BHACTPON_DTL' in name or '批量开户明细' in cn:
        return (False, '万级', '慢(低频批量)', '批量开户明细,低频批量业务')

    # 2.39 手机号打标明细 - 低频
    if 'MOB_TAG_DTL' in name or '手机号打标' in cn:
        return (False, '千级', '慢(低频操作)', '手机号打标明细,低频操作')

    # 2.40 客户信息变更基础表 - 中等增长
    if 'CUST_INFO_CHANGE_APLY' in name and '_DTL' not in name:
        return (False, '万级', '中等(随变更申请)', '客户信息变更基础表,随变更申请增长')

    # 2.41 标签历史数据更新记录 - 低频
    if 'REGIDX_IMPT_HIS' in name or '标签历史' in cn:
        return (False, '千级', '慢(低频更新)', '标签历史数据更新,低频更新')

    # 2.42 评级申请基本信息 - 中等增长
    if 'RTG_APLY_BSC_INF' in name or '评级申请' in cn:
        return (False, '万级', '中等(随评级申请)', '评级申请基本信息,随评级申请增长')

    # 2.43 降低额度锁 - 临时数据
    if 'LOCK_REDU_LMT' in name or '降低额度锁' in cn:
        return (False, '十级', '临时(处理完删除)', '降低额度锁,临时数据处理完删除')

    # 2.45 风控_供数_客户利率定价指标 - 中等增长
    if 'CUST_INTRT_PCNM_IDX' in name or '利率定价指标' in cn:
        return (False, '万级', '中等(定期计算)', '客户利率定价指标,定期计算产生')

    # 2.46 贷后预警映射 - 配置数据
    if 'PST_LOAN_WARN_MPNG' in name or '贷后预警映射' in cn:
        return (False, '百级', '不增长(配置数据)', '贷后预警映射,配置数据')

    # 2.46b 风险预警解除规则 - 配置数据
    if 'RSK_WARN_RLV_RULE' in name or '预警解除规则' in cn:
        return (False, '百级', '不增长(规则配置)', '风险预警解除规则,配置数据')

    # 2.46c 客户评级指标表 - 中等增长但量小
    if 'CUST_RTG_IDX_TBL' in name or '客户评级指标' in cn:
        return (False, '万级', '中等(随评级计算)', '客户评级指标,随评级计算增长,量小')

    # 2.47 风险预警解除信息主表/规则 - 低频
    if 'RSK_WARN_RLV_INF_PRIM' in name or '预警解除信息主表' in cn:
        return (False, '千级', '慢(低频解除)', '风险预警解除信息,低频解除产生')
    if 'RSK_WARN_RLV_RULE' in name or '预警解除规则' in cn:
        return (False, '百级', '不增长(规则配置)', '风险预警解除规则,配置数据')

    # 2.48 风险预警信号表 - 中等增长
    if 'RSK_WARN_SGNL_TBL' in name or '预警信号' in cn:
        return (False, '万级', '中等(随预警产生)', '风险预警信号,随预警产生增长')

    # 2.49 对公/对私单项指标 - 中等增长
    if 'ENT_SINGLE_INDEX' in name or '对公单项指标' in cn:
        return (False, '万级', '中等(定期计算)', '对公单项指标,定期计算产生')
    if 'IND_SINGLE_INDEX' in name or '对私单项指标' in cn:
        return (False, '万级', '中等(定期计算)', '对私单项指标,定期计算产生')

    # 2.50 m_ind_info_day - 日级指标数据
    if 'M_IND_INFO_DAY' in name:
        return (True, '十万级', '较快(日级指标每日产生)', '')  # 日级数据增长较快

    # 2.51 事业单位资产负债/收入支出表 - 低频
    if 'CAREERDEBT' in name or 'CAREERINEX' in name:
        return (False, '千级', '慢(低频报表)', '事业单位财务报表,低频报表数据')

    # 2.52 已结清借贷/担保交易汇总 - 中等增长
    if 'ALRDYCLSGDBTCTNSMYINF' in name or '已结清借贷交易汇总' in cn:
        return (False, '万级', '中等(随征信查询)', '已结清借贷交易汇总,随征信查询增长')
    if 'ALREADYWRNTTXNCLSMYINF' in name or '已结清担保交易汇总' in cn:
        return (False, '万级', '中等(随征信查询)', '已结清担保交易汇总,随征信查询增长')
    if 'AWLAINSTSMY' in name or '担保账户分机构汇总' in cn:
        return (False, '万级', '中等(随征信查询)', '担保账户分机构汇总,随征信查询增长')

    # 2.53 实际控制人信息 - 低频
    if 'ACTCTRLRINF' in name or '实际控制人' in cn:
        return (False, '千级', '慢(低频查询)', '实际控制人信息,低频查询产生')

    # 2.54 消息app - 低频
    if 'BASE_MSG_APP' in name or '消息app' in cn:
        return (False, '百级', '不增长(配置数据)', '消息app配置,配置数据')

    # 2.55 规则流程修正 - 低频
    if 'FLOW_RECTS' in name:
        return (False, '千级', '慢(低频修正)', '规则流程修正,低频修正产生')

    # 2.56 客户合并记录表 - 中等增长
    if 'ECIF_MRG_TRANS' in name and '_DTL' not in name:
        return (False, '千级', '慢(低频合并)', '客户合并记录,低频合并产生')

    # 默认: 无法判断的保留
    return (True, '未知', '需评估', '')


def main():
    # 读取已有工作簿(原始86张表)
    wb = load_workbook(SRC)
    ws = wb['目录']
    last_row = ws.max_row

    # 读取144张新增表
    df = pd.read_excel(SRC.replace('.xlsx', '_业务逻辑版.xlsx'), sheet_name='目录')
    new_df = df.iloc[86:].copy()

    print(f'待评估表数: {len(new_df)}')

    # 逐表评估
    results = []
    keep_count = 0
    exclude_count = 0

    for _, row in new_df.iterrows():
        table_en = str(row.iloc[4])
        table_cn = str(row.iloc[5])
        module = str(row.iloc[2])

        keep, volume, growth, reason = judge_data_volume(table_en, table_cn, module)

        results.append({
            '模块': module,
            '表英文名': table_en,
            '表中文名': table_cn,
            '是否保留': '是' if keep else '否',
            '数据量级别': volume,
            '增长趋势': growth,
            '排除理由': reason,
        })

        if keep:
            keep_count += 1
        else:
            exclude_count += 1

    result_df = pd.DataFrame(results)

    print(f'\n评估结果:')
    print(f'  保留: {keep_count}张')
    print(f'  排除: {exclude_count}张')

    # 输出排除的表
    excluded = result_df[result_df['是否保留'] == '否']
    print(f'\n排除的表({len(excluded)}张):')
    for _, row in excluded.iterrows():
        print(f'  [{row["模块"]}] {row["表英文名"]} | {row["表中文名"]} | {row["排除理由"]}')

    # 保存评估结果
    output = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\volume_assessment.xlsx'
    result_df.to_excel(output, index=False)
    print(f'\n评估结果已保存: {output}')


if __name__ == '__main__':
    main()
