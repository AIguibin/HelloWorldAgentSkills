# -*- coding: utf-8 -*-
"""
基于信贷业务逻辑分析每张表的归档必要性
业务逻辑分类:
1. 业务交易数据(需归档): 合同/借据/放款/还款/担保/抵质押等核心业务数据
2. 流程审批数据(需归档): 申请/审批/流程节点/意见等
3. 贷后管理数据(需归档): 检查/预警/催收/风险分类等
4. 日志审计数据(需归档): 操作日志/登录日志/审计日志等
5. 历史变更数据(需归档): 变更历史/版本记录等
6. 临时中间数据(不归档): 临时表/中间表/批量临时表
7. 配置参数数据(不归档): 产品配置/参数/字典/模板等
8. 基础定义数据(不归档): 基础代码/枚举/规则定义等
"""
import pandas as pd
import re

SCAN_FILE = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\all_tables_with_fields.xlsx'


def classify_by_business_logic(table_en, table_cn, module, fields_cn, fields_en):
    """基于信贷业务逻辑判断表的归档必要性
    返回: (是否需要归档, 业务分类, 归档理由)
    """
    name = str(table_en).upper()
    cn = str(table_cn)
    f_cn = str(fields_cn) if pd.notna(fields_cn) else ''
    f_en = str(fields_en) if pd.notna(fields_en) else ''

    # ===== 不归档类 =====

    # 1. 临时表/中间表 - 业务逻辑: 批处理或数据同步的临时存储,无业务保留价值
    if any(kw in name for kw in ['_TEMP', '_TMP', 'TEMP_', 'TMP_']):
        return (False, '临时数据', '临时表,批处理或同步用,无业务保留价值')
    if name.startswith('BTCH_FILE_') or name.startswith('BTCH_U_'):
        return (False, '临时数据', '批量文件临时表,卸数用,无业务保留价值')
    if 'MIDDLE' in name or '_MID_' in name:
        return (False, '临时数据', '中间表,数据转换用,无业务保留价值')
    if 'UNDO_LOG' in name:
        return (False, '临时数据', '事务回滚表,系统自动管理')

    # 2. 配置参数表 - 业务逻辑: 系统配置,变更频率低,不属于业务数据
    config_patterns = [
        '_CFG', '_CONFIG', 'CONFIG_', '_PARAM', 'PARAM_',
        '_SETTING', 'SETTING_', '_PROPS', 'PROPS_',
    ]
    if any(p in name for p in config_patterns):
        return (False, '配置参数', '系统配置/参数表,非业务交易数据')
    if '基础配置' in cn or '参数配置' in cn or '系统配置' in cn:
        return (False, '配置参数', '系统配置表,非业务交易数据')

    # 3. 字典代码表 - 业务逻辑: 枚举值/代码定义,基础数据
    dict_patterns = ['_DICT', 'DICT_', '_CODE', 'CODE_', '_ENUM', 'ENUM_', '_TYPE', 'TYPE_DEF']
    if any(p in name for p in dict_patterns):
        if 'RECORD' not in name and 'HIST' not in name:
            return (False, '字典代码', '字典/代码定义表,基础数据')
    if '字典' in cn or '代码表' in cn or '枚举' in cn:
        return (False, '字典代码', '字典/代码表,基础数据')

    # 4. 模板表 - 业务逻辑: 业务模板定义,非交易数据
    if '_TPL' in name or 'TEMPLATE' in name or '_TEMPLATE' in name:
        return (False, '模板定义', '模板定义表,非业务交易数据')
    if '模板' in cn:
        return (False, '模板定义', '模板定义表,非业务交易数据')

    # 5. 产品定义/规则定义 - 业务逻辑: 产品/规则的基础定义,非交易实例
    if module == '产品管理':
        # 产品定义表不归档,但产品发布历史/变更记录需归档
        if 'HIST' in name or '变更' in cn or '发布' in cn or '记录' in cn:
            return (True, '历史变更', '产品发布历史/变更记录,需保留追溯')
        return (False, '产品定义', '产品定义/要素表,基础配置数据')

    # 6. 规则定义 - 业务逻辑: 风控规则/评级模型定义
    if module == '风控中心' or module == '信贷引擎':
        if any(kw in name for kw in ['_DEF', '_RULE_DEF', '_MODEL_DEF', '_VAR_DEF', '_SCORE_DEF']):
            return (False, '规则定义', '规则/模型定义表,基础配置数据')
        if '规则定义' in cn or '模型定义' in cn or '变量定义' in cn:
            return (False, '规则定义', '规则/模型定义表,基础配置数据')

    # 7. 映射关系表 - 业务逻辑: 配置映射,非交易数据
    if '_MAP' in name or '_MAPPING' in name:
        if 'RECORD' not in name and 'HIST' not in name:
            return (False, '映射配置', '映射关系配置表,非业务交易数据')

    # 8. 组织机构/用户权限 - 业务逻辑: 基础架构数据
    if module == '系统管理':
        org_patterns = ['ORG_', '_ORG', 'DEPT_', '_DEPT', 'ROLE_', '_ROLE', 'USER_', '_USER', 'MENU_', '_MENU', 'PERMISSION', 'AUTH_']
        if any(p in name for p in org_patterns):
            if 'LOG' not in name and 'RECORD' not in name and 'HIST' not in name:
                return (False, '基础架构', '组织/用户/权限基础数据,非业务交易数据')

    # ===== 需要归档类 =====

    # 1. 日志类 - 业务逻辑: 系统运维/安全审计/操作追溯,法律要求保留6个月
    log_patterns = ['_LOG', 'LOG_', '_LOGS', 'LOGS_']
    if any(p in name for p in log_patterns):
        if 'UNDO' in name:
            return (False, '临时数据', '事务回滚表')
        return (True, '日志审计', '系统日志/操作审计,网络安全法要求保留6个月,1年以上归档')

    if '日志' in cn or '审计' in cn:
        return (True, '日志审计', '系统日志/审计数据,需按规定保留')

    # 2. 历史变更类 - 业务逻辑: 业务数据变更轨迹,需保留追溯
    hist_patterns = ['_HIST', 'HIST_', '_HISTORY', 'HISTORY_']
    if any(p in name for p in hist_patterns):
        return (True, '历史变更', '业务数据变更历史,需保留追溯,5年以上归档')
    if '历史' in cn or '变更记录' in cn or '变更历史' in cn:
        return (True, '历史变更', '业务数据变更历史,需保留追溯')

    # 3. 流水记录类 - 业务逻辑: 业务交易流水,会计档案要求保留10年
    record_patterns = ['_REC', 'REC_', '_RECORD', 'RECORD_', '_STTN', 'STTN_']
    if any(p in name for p in record_patterns):
        return (True, '流水记录', '业务流水/记录数据,会计档案要求保留10年,5年以上归档')
    if '记录' in cn or '流水' in cn:
        return (True, '流水记录', '业务流水/记录数据,需保留追溯')

    # 4. 任务类 - 业务逻辑: 业务流程任务,任务完结后可归档
    tsk_patterns = ['_TSK', 'TSK_', '_TASK', 'TASK_']
    if any(p in name for p in tsk_patterns):
        return (True, '流程任务', '业务流程任务数据,任务完结后可归档')

    # 5. 明细类 - 业务逻辑: 业务明细数据,随主业务归档
    dtl_patterns = ['_DTL', 'DTL_', '_DETAIL', 'DETAIL_']
    if any(p in name for p in dtl_patterns):
        # 排除配置明细
        if 'CFG' in name or 'CONFIG' in name or 'PARAM' in name:
            return (False, '配置参数', '配置明细表,非业务交易数据')
        return (True, '业务明细', '业务明细数据,随主业务归档,5年以上归档')

    # 6. 按模块业务逻辑判断

    # 营销管理 - 业务逻辑: 营销数据受个保法约束,目的达成后应删除
    if module == '营销管理':
        if 'CFG' in name or 'CONFIG' in name or '模板' in cn:
            return (False, '配置参数', '营销配置/模板,非业务数据')
        return (True, '营销数据', '营销业务数据,个保法要求目的达成后删除,1年以上归档')

    # 客户管理 - 业务逻辑: 客户信息是核心数据,但变更记录/合并记录需归档
    if module == '客户管理':
        if any(kw in name for kw in ['_HIST', '_RECORD', '_LOG', '_AUDIT']):
            return (True, '历史变更', '客户信息变更历史,反洗钱法要求保留10年')
        if '变更' in cn or '历史' in cn or '记录' in cn or '合并' in cn or '停用' in cn:
            return (True, '历史变更', '客户信息变更/合并记录,需保留追溯')
        # 客户基本信息表不归档(主数据)
        if any(kw in name for kw in ['_INFO', '_INF', '_BASIC', '_BASE']):
            if 'RECORD' not in name and 'HIST' not in name:
                return (False, '客户主数据', '客户基本信息主数据,不归档(随业务归档)')

    # 授信管理 - 业务逻辑: 授信申请/批复/审批数据,需保留10年
    if module == '授信管理':
        if 'CFG' in name or 'CONFIG' in name or '参数' in cn:
            return (False, '配置参数', '授信配置/参数,非业务数据')
        return (True, '授信审批', '授信申请/批复/审批数据,授信档案要求保留10年')

    # 用信管理 - 业务逻辑: 用信申请/批复数据
    if module == '用信管理':
        if 'CFG' in name or 'CONFIG' in name:
            return (False, '配置参数', '用信配置,非业务数据')
        return (True, '用信审批', '用信申请/批复数据,信贷档案要求保留10年')

    # 合同管理 - 业务逻辑: 合同是核心法律凭证,需长期保留
    if module == '合同管理':
        if 'CFG' in name or 'CONFIG' in name or '模板' in cn:
            return (False, '配置参数', '合同配置/模板,非业务数据')
        return (True, '合同数据', '合同数据,民法典要求保留至诉讼时效届满,10年以上归档')

    # 放还款组 - 业务逻辑: 放还款是核心交易,会计档案要求保留10年
    if module == '放还款组':
        if 'CFG' in name or 'CONFIG' in name:
            return (False, '配置参数', '放还款配置,非业务数据')
        return (True, '放还款交易', '放还款交易数据,会计档案要求保留10年')

    # 贷后管理 - 业务逻辑: 贷后检查/预警/催收数据
    if module == '贷后管理':
        if 'CFG' in name or 'CONFIG' in name or '模板' in cn or '策略' in cn:
            if 'RECORD' not in name and 'HIST' not in name and 'LOG' not in name:
                return (False, '配置参数', '贷后配置/策略/模板,非业务数据')
        return (True, '贷后管理', '贷后检查/预警/催收数据,信贷档案要求保留10年')

    # 风险分类 - 业务逻辑: 五级分类数据,监管要求保留
    if module == '风险分类' or 'RISK_CL' in name:
        return (True, '风险分类', '风险分类数据,1104监管要求保留,10年归档')

    # 额度中心 - 业务逻辑: 额度数据,监管要求保留
    if module == '额度中心':
        if 'CFG' in name or 'CONFIG' in name or '_TEMP' in name:
            return (False, '配置参数', '额度配置/临时表,非业务数据')
        if '_TEMP' in name or '_TMP' in name:
            return (False, '临时数据', '额度同步临时表,无业务保留价值')
        return (True, '额度数据', '额度数据,1104大额风险暴露要求保留,10年归档')

    # 押品管理 - 业务逻辑: 抵质押物数据,担保档案要求保留
    if module == '押品管理':
        if 'CFG' in name or 'CONFIG' in name or '模板' in cn:
            return (False, '配置参数', '押品配置/模板,非业务数据')
        if '_TEMP' in name or '_PCS' in name:  # PCS=过程表
            return (False, '临时数据', '押品过程/临时表,无业务保留价值')
        return (True, '押品数据', '抵质押物数据,担保档案要求保留10年')

    # 档案管理 - 业务逻辑: 档案管理任务/调阅记录
    if module == '档案管理':
        if 'CFG' in name or 'CONFIG' in name:
            return (False, '配置参数', '档案配置,非业务数据')
        return (True, '档案管理', '档案管理任务/调阅记录,档案法要求保留')

    # 评级管理 - 业务逻辑: 信用评级数据
    if module == '评级管理':
        if 'CFG' in name or 'CONFIG' in name or '_DEF' in name or '模型' in cn:
            if 'RECORD' not in name and 'HIST' not in name:
                return (False, '配置参数', '评级模型/配置,非业务数据')
        return (True, '评级数据', '信用评级数据,授信档案要求保留10年')

    # 线上贷款 - 业务逻辑: 线上贷款业务数据
    if module == '线上贷款':
        if 'CFG' in name or 'CONFIG' in name or '模板' in cn:
            return (False, '配置参数', '线上贷款配置,非业务数据')
        return (True, '线上贷款', '线上贷款业务数据,互联网贷款管理办法要求保留')

    # 工作流程 - 业务逻辑: 流程实例/任务/意见
    if module == '工作流程':
        if 'CFG' in name or 'CONFIG' in name or '_DEF' in name or '模板' in cn:
            if 'LOG' not in name and 'RECORD' not in name:
                return (False, '配置参数', '流程定义/配置,非业务数据')
        if 'LOG' in name or 'RECORD' in name or 'HIST' in name:
            return (True, '流程数据', '流程日志/记录/历史,审批档案要求保留')
        return (True, '流程数据', '流程实例/任务数据,审批档案要求保留')

    # 批量管理 - 业务逻辑: 批量任务执行记录
    if module == '批量管理':
        if 'CFG' in name or 'CONFIG' in name or '_DEF' in name:
            return (False, '配置参数', '批量配置/定义,非业务数据')
        if 'LOG' in name or 'RECORD' in name or 'HIST' in name:
            return (True, '批量日志', '批量执行日志/记录,运维要求保留6个月')
        return (False, '批量配置', '批量任务配置,非业务数据')

    # 电子文档 - 业务逻辑: 电子文档/影像数据
    if module == '电子文档':
        if 'CFG' in name or 'CONFIG' in name:
            return (False, '配置参数', '电子文档配置,非业务数据')
        if 'LOG' in name:
            return (True, '日志审计', '电子文档操作日志,保留6个月')
        return (False, '文档存储', '电子文档存储表,随业务归档')

    # 统一认证 - 业务逻辑: 认证日志
    if module == '统一认证':
        if 'LOG' in name or 'RECORD' in name or 'HIST' in name:
            return (True, '日志审计', '认证日志/记录,网络安全法要求保留6个月')
        return (False, '认证配置', '认证配置/基础数据,非业务数据')

    # 架构管理 - 业务逻辑: 系统架构配置
    if module == '架构管理':
        if 'LOG' in name or 'RECORD' in name or 'HIST' in name:
            return (True, '日志审计', '架构变更日志/记录,保留追溯')
        return (False, '架构配置', '架构配置/定义,非业务数据')

    # 风控中心 - 业务逻辑: 风控决策/征信数据
    if module == '风控中心':
        if '_DEF' in name or '_CFG' in name or '_CONFIG' in name:
            return (False, '规则定义', '风控规则/模型定义,基础配置数据')
        if '模板' in cn or '配置' in cn or '参数' in cn:
            return (False, '配置参数', '风控配置/参数,非业务数据')
        if 'LOG' in name or 'RECORD' in name or 'HIST' in name:
            return (True, '风控数据', '风控决策/征信数据,模型治理要求保留5年')
        # 征信信息单元(二代征信)
        if name.startswith('E_R_') or name.startswith('I_R_'):
            return (True, '征信数据', '二代征信信息单元,征信业管理条例要求保留5年')
        return (True, '风控数据', '风控决策数据,模型治理要求保留')

    # 信贷引擎 - 业务逻辑: 规则引擎执行数据
    if module == '信贷引擎':
        if '_DEF' in name or '_CFG' in name or '_CONFIG' in name:
            return (False, '规则定义', '规则引擎定义/配置,基础配置数据')
        if '模板' in cn or '配置' in cn:
            return (False, '配置参数', '引擎配置,非业务数据')
        if 'LOG' in name or 'RECORD' in name or 'HIST' in name:
            return (True, '引擎日志', '规则引擎执行日志,模型治理要求保留5年')
        return (False, '引擎配置', '规则引擎配置/定义,非业务数据')

    # 系统管理 - 业务逻辑: 系统配置/日志
    if module == '系统管理':
        if 'LOG' in name or 'RECORD' in name or 'HIST' in name:
            return (True, '日志审计', '系统日志/记录,网络安全法要求保留6个月')
        if '消息' in cn or '通知' in cn or '短信' in cn:
            return (True, '消息通知', '消息/通知记录,保留6个月')
        return (False, '系统配置', '系统配置/基础数据,非业务数据')

    # 客户中心 - 业务逻辑: 客户基础数据
    if module == '客户中心':
        if 'LOG' in name or 'RECORD' in name or 'HIST' in name:
            return (True, '历史变更', '客户数据变更记录,反洗钱法要求保留10年')
        return (False, '客户主数据', '客户中心基础数据,主数据不归档')

    # 默认: 含金额/日期/状态字段的视为业务数据
    business_field_indicators = ['金额', '日期', '状态', '余额', '利率', '期限', '编号']
    if any(ind in f_cn for ind in business_field_indicators):
        if 'CFG' in name or 'CONFIG' in name or '模板' in cn:
            return (False, '配置参数', '配置表,非业务数据')
        return (True, '业务数据', '含业务核心字段,判定为业务交易数据,需归档')

    # 默认不归档
    return (False, '其他', '未识别为需归档的业务数据')


def main():
    df = pd.read_excel(SCAN_FILE)
    print(f'待分析表数: {len(df)}')

    results = []
    archive_count = 0
    no_archive_count = 0

    for _, row in df.iterrows():
        need_archive, biz_class, reason = classify_by_business_logic(
            row['表英文名'], row['表中文名'], row['模块'],
            row['字段中文列表'], row['字段英文列表']
        )

        results.append({
            '模块': row['模块'],
            '数据库': row['数据库'],
            '表英文名': row['表英文名'],
            '表中文名': row['表中文名'],
            '字段数': row['字段数'],
            '是否需要归档': '是' if need_archive else '否',
            '业务分类': biz_class,
            '归档理由': reason,
        })

        if need_archive:
            archive_count += 1
        else:
            no_archive_count += 1

    result_df = pd.DataFrame(results)
    output = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\archive_analysis_by_logic.xlsx'
    result_df.to_excel(output, index=False)

    print(f'\n分析完成:')
    print(f'  需要归档: {archive_count}张')
    print(f'  不需归档: {no_archive_count}张')
    print(f'  总计: {len(df)}张')
    print(f'\n输出文件: {output}')

    # 按业务分类统计
    print('\n需归档表按业务分类统计:')
    archive_df = result_df[result_df['是否需要归档'] == '是']
    print(archive_df.groupby('业务分类').size().sort_values(ascending=False))

    print('\n不需归档表按业务分类统计:')
    no_archive_df = result_df[result_df['是否需要归档'] == '否']
    print(no_archive_df.groupby('业务分类').size().sort_values(ascending=False))


if __name__ == '__main__':
    main()
