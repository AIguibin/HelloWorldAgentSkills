# -*- coding: utf-8 -*-
"""
为湖北农信清理归档表清单.xlsx 的 J列(备注说明) 填写归档维度分析
维度体系:
1. 业务生命周期维度: 营销/申请/审批/合同/放款/还款/贷后/结清
2. 产品类型维度: 对公/零售/信用卡/普惠/同业
3. 法律合规维度: 民法典诉讼时效/个保法/会计档案/反洗钱/征信条例
4. 监管报送维度: 1104/EAST/征信报送
5. 归档优先级: P0紧急/P1高/P2中/P3低
"""
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

SRC = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\DD-湖北农信基础配置检核\湖北农信清理归档表清单.xlsx'

# 归档维度映射表 - 基于业务分析
DIMENSION_MAP = {
    # ===== 合同管理模块 =====
    'PRVT_CTR_INF': '业务生命周期/合同阶段；法律维度(民法典合同编诉讼时效3年)；监管维度(EAST信贷合同表)；归档优先级P2',
    'R_RTL_CONT_SIGN_DTL': '业务生命周期/合同阶段；产品维度(零售)；法律维度(电子签名法)；归档优先级P2',
    'RTL_CONT_ACC_INF': '业务生命周期/合同阶段；监管维度(EAST合同账户)；会计档案维度(10年)；归档优先级P2',
    'ULM_CONT_REVOKE_INF_BATCH': '业务生命周期/合同阶段；额度联动；归档优先级P2',
    'ULM_CONT_REVOKE_INF_BATCH_HISTORY': '业务生命周期/合同阶段；历史表(已归档)；归档优先级P3',

    # ===== 授信管理模块 =====
    'CRLMT_CRG_PD_LMT_APLY': '业务生命周期/授信审批阶段；监管维度(授信尽职指引)；归档优先级P2',
    'CRLMT_CRGLN_APLY': '业务生命周期/授信审批阶段；监管维度(授信尽职指引第42条)；归档优先级P2',
    'CRLMT_LMT_REPLY': '业务生命周期/授信审批阶段；监管维度(1104授信批复G01/G14)；法律维度(授信档案10年)；归档优先级P2',
    'CRLMT_LMT_REPLY_RECORD': '业务生命周期/授信审批阶段；审批轨迹留痕；归档优先级P2',
    'CRLMT_SITMLMT_REPLY': '业务生命周期/授信审批阶段；监管维度(分项额度管理)；归档优先级P2',
    'CRLMT_SITMLMT_REPLY_RECORD': '业务生命周期/授信审批阶段；审批轨迹留痕；归档优先级P2',

    # ===== 放还款组模块 =====
    'DSBR_ACG_PCSG_INFO': '业务生命周期/放款阶段；会计档案维度(会计凭证10年)；归档优先级P2',
    'DSBR_AGM_PAY_REPY_PLN': '业务生命周期/还款阶段；还款计划(信贷档案10年)；归档优先级P2',
    'DSBR_BANKSYND_RLTV_REL_TBL': '业务生命周期/放款阶段；产品维度(银团贷款)；归档优先级P2',
    'DSBR_CMB_PAY_REPY_PLN': '业务生命周期/还款阶段；还款计划(信贷档案10年)；归档优先级P2',
    'DSBR_CONT_ACC_INF': '业务生命周期/放款阶段；监管维度(EAST贷款台账)；会计档案维度(10年)；归档优先级P2',
    'DSBR_MRGN_DTL': '业务生命周期/放款阶段；保证金管理；归档优先级P2',
    'DSBR_RLTV_BILL_INF': '业务生命周期/放款阶段；法律维度(票据法)；归档优先级P2',
    'IOU_INF': '业务生命周期/放款阶段；监管维度(EAST借据信息)；法律维度(民法典诉讼时效3年)；大表(2000万+)；归档优先级P2',
    'LDRP_REPY_ONLINE_REC': '业务生命周期/还款阶段；产品维度(线上贷款)；归档优先级P2',
    'LDRP_REPY_REPY_REC': '业务生命周期/还款阶段；会计档案维度(还款凭证10年)；监管维度(EAST还款明细)；归档优先级P2',
    'LDRP_REPY_RESULT_REC': '业务生命周期/还款阶段；会计档案维度(核算凭证10年)；归档优先级P2',
    'LDRP_REPY_SSONINT_REPY_SUB_IOU_INF': '业务生命周期/还款阶段；产品维度(贴息业务)；归档优先级P2',
    'PAY_RLTV_IOU': '业务生命周期/放款阶段；借据关联；归档优先级P2',
    'RTL_PAY_CHANGE': '业务生命周期/放款阶段；支付变更；归档优先级P2',
    'RTL_PAY_DSBR_DTL_INF': '业务生命周期/放款阶段；监管维度(EAST受托支付/资金流向)；大表(300万+)；归档优先级P2',
    'RTL_PAY_DSBR_ONLINE_RCD': '业务生命周期/放款阶段；产品维度(线上贷款)；归档优先级P2',
    'RTL_PAY_DSBR_ONLINE_RCD_DUBL': '业务生命周期/放款阶段；产品维度(线上贷款)；归档优先级P2',
    'RTL_PAY_DTL': '业务生命周期/放款阶段；监管维度(受托支付明细)；大表(115万+)；归档优先级P2',
    'RSTG_STS_UPDATE_LOG_INF': '业务生命周期/贷后阶段(贷款重组)；监管维度(重组贷款管理)；归档优先级P2',

    # ===== 档案管理模块 =====
    'ARCH_ELEC_DT': '业务生命周期/合同阶段；法律维度(档案法信贷档案10年)；大表(175万+)；归档优先级P2',
    'ARCH_INFO': '业务生命周期/合同阶段；法律维度(档案法信贷档案10年)；大表(1800万+)；归档优先级P2',
    'ARCH_WH_TSK': '业务生命周期/合同阶段；档案入库任务；归档优先级P2',
    'ARCH_WH_TSK_DTL': '业务生命周期/合同阶段；档案入库清单；归档优先级P2',
    'ARCH_WH_MIDDLE': '业务生命周期/合同阶段；档案入库中间表；归档优先级P1',

    # ===== 用信管理模块 =====
    'PRVT_CRLINE_USE_REPLY': '业务生命周期/用信阶段；产品维度(零售)；大表(447万+)；归档优先级P2',
    'R_RTL_CONT_INF': '业务生命周期/用信阶段；产品维度(零售)；大表(1700万+)；归档优先级P2',

    # ===== 系统管理模块 =====
    'SYS_LOG': '系统运维维度；法律维度(网络安全法日志留存6个月)；归档优先级P0',
    'SYS_LOGIN_LOG': '系统运维维度；法律维度(网络安全法日志留存6个月)；归档优先级P0',

    # ===== 线上贷款模块 =====
    'OL_APL_MGT_MNPLT_REC': '业务生命周期/申请阶段；产品维度(普惠/线上贷款)；归档优先级P1',
    'OL_APL_RSLT_NTC_REC': '业务生命周期/申请阶段；产品维度(普惠/线上贷款)；归档优先级P1',

    # ===== 统一认证模块 =====
    'UAC_APP_LOG': '系统运维维度；法律维度(网络安全法日志留存6个月)；归档优先级P0',

    # ===== 营销管理模块 =====
    'CMPN_ACS_REAIL': '业务生命周期/营销阶段；法律维度(个保法数据最小化)；归档优先级P0',
    'CMPN_ACS_RGS': '业务生命周期/营销阶段；法律维度(个保法数据最小化)；归档优先级P0',
    'CMPN_AVY_DIG_NMLST_CST': '业务生命周期/营销阶段；法律维度(个保法营销授权撤销后删除)；归档优先级P0',
    'CMPN_AVY_LBL_CST': '业务生命周期/营销阶段；法律维度(个保法数据最小化)；归档优先级P0',
    'CMPN_DLHP_DIG_NMLST_CST': '业务生命周期/营销阶段；法律维度(个保法数据最小化)；归档优先级P0',
    'CMPN_DLHP_LBL_CST': '业务生命周期/营销阶段；法律维度(个保法数据最小化)；归档优先级P0',
    'CMPN_DLHP_TRGR_EV_CST': '业务生命周期/营销阶段；法律维度(个保法数据最小化)；归档优先级P0',
    'CMPN_NMLST_CST': '业务生命周期/营销阶段；法律维度(个保法营销授权)；归档优先级P0',
    'CMPN_TSK_CST': '业务生命周期/营销阶段；法律维度(个保法营销授权)；归档优先级P0',
    'CMPN_TSK_MGT_DTL': '业务生命周期/营销阶段；法律维度(个保法营销授权)；归档优先级P0',

    # ===== 贷后管理模块 =====
    'LOAN_COLL_AI_CALL_PSH_RCRD': '业务生命周期/贷后阶段(催收)；法律维度(诉讼时效3年)；产品维度(智能催收)；归档优先级P2',
    'LOAN_COLL_BACKINFO_TBL': '业务生命周期/贷后阶段(催收)；法律维度(诉讼时效3年)；归档优先级P2',
    'LOAN_COLL_STR_ADJ_DETAIL': '业务生命周期/贷后阶段(催收策略)；归档优先级P2',
    'LOAN_COLL_STRTG_ADJ_APRV': '业务生命周期/贷后阶段(催收策略)；审批留痕；归档优先级P2',
    'LOAN_COLL_TSK_IOU_INF': '业务生命周期/贷后阶段(催收)；法律维度(诉讼时效3年)；归档优先级P2',
    'LOAN_COLL_TSK_OBJECT_TBL': '业务生命周期/贷后阶段(催收)；法律维度(诉讼时效3年)；归档优先级P2',
    'LOAN_COLL_TSK_TBL': '业务生命周期/贷后阶段(催收)；法律维度(诉讼时效3年)；归档优先级P2',
    'LOAN_CP_LABOUR_GEN_CHK': '业务生命周期/贷后阶段(检查)；产品维度(对公)；监管维度(贷后管理指引)；归档优先级P2',
    'LOAN_CST_CTR_SCOR_TBL': '业务生命周期/贷后阶段(检查)；客户合同评分；归档优先级P2',
    'LOAN_CTR_COLL_AND_RMNDR_RCR': '业务生命周期/贷后阶段(催收提醒)；法律维度(诉讼时效3年)；归档优先级P2',
    'LOAN_POSTLOAN_CHK_RESULT': '业务生命周期/贷后阶段(检查)；监管维度(贷后管理指引)；大表(740万+)；归档优先级P2',
    'LOAN_RT_LABOUR_GEN_CHK': '业务生命周期/贷后阶段(检查)；产品维度(零售)；监管维度(贷后管理指引)；大表(1000万+)；归档优先级P2',
    'PSTLOAN_CHK_CUST_REL_INF': '业务生命周期/贷后阶段(检查)；关联人信息；归档优先级P2',
    'PSTLOAN_CHK_INDEX_SUMM_INF': '业务生命周期/贷后阶段(检查)；征信指标汇总；法律维度(征信业管理条例5年)；归档优先级P2',
    'PSTLOAN_CHK_LOAN_INF': '业务生命周期/贷后阶段(检查)；贷款信息；归档优先级P2',
    'PSTLOAN_CHK_NON_LOAN_INF': '业务生命周期/贷后阶段(检查)；行内未结清贷款；归档优先级P2',
    'PSTLOAN_PSTINS_CORP_WARN_REC': '业务生命周期/贷后阶段(预警)；产品维度(对公)；监管维度(风险预警)；归档优先级P2',
    'PSTLOAN_PSTINS_PRVT_WARN_REC': '业务生命周期/贷后阶段(预警)；产品维度(零售)；监管维度(风险预警)；大表(262万+)；归档优先级P2',
    'PSTLOAN_WARN_DISPL_RCRD': '业务生命周期/贷后阶段(预警处置)；归档优先级P2',
    'PSTLOAN_WARN_DISPL_SCHEM': '业务生命周期/贷后阶段(预警处置方案)；归档优先级P2',
    'PSTLOAN_WARN_INFO': '业务生命周期/贷后阶段(预警)；监管维度(风险预警管理)；归档优先级P2',
    'R_LOAN_FTM_CHK_TSK_TBL': '业务生命周期/贷后阶段(检查任务)；监管维度(贷后管理指引)；大表(673万+)；归档优先级P2',
    'R_LOAN_FTM_CHK_TSK_TBL_MNG': '业务生命周期/贷后阶段(检查任务管理)；归档优先级P2',

    # ===== 风险分类模块 =====
    'RTL_RISK_ASSET_CL_INF': '业务生命周期/贷后阶段(风险分类)；监管维度(1104 G11五级分类)；归档优先级P2',
    'RTL_RISK_CL_RECORD_INF': '业务生命周期/贷后阶段(风险分类)；监管维度(1104 G11分类变更链)；归档优先级P2',
    'RTL_RISK_CL_RES_INF': '业务生命周期/贷后阶段(风险分类)；监管维度(1104 G11分类结果)；归档优先级P2',

    # ===== 额度中心模块 =====
    'ULM_IOU_INF': '业务生命周期/授信阶段(额度借据)；监管维度(1104大额风险暴露G14)；大表(212万+)；归档优先级P2',
    'ULM_LMT_PRIM_INF': '业务生命周期/授信阶段(额度主表)；监管维度(1104大额风险暴露G14)；大表(407万+)；归档优先级P2',
    'ULM_LMT_PRIM_SNPST': '业务生命周期/授信阶段(额度快照)；监管维度(1104时点快照)；归档优先级P2',
    'ULM_LMT_RL_OCP_SUM': '业务生命周期/授信阶段(额度实占汇总)；监管维度(1104风险暴露)；大表(431万+)；归档优先级P2',
    'ULM_LMT_USE_STTN': '业务生命周期/授信阶段(额度使用流水)；监管维度(1104风险暴露)；归档优先级P2',

    # ===== 风控中心模块 =====
    'DEAL_WITH_FILE_LOG': '业务生命周期/审批阶段(征信报告处理)；法律维度(征信业管理条例第20条查询记录5年)；归档优先级P1',
    'RULE_LOG_MODEL_MONITOR': '风控决策维度；监管维度(金融科技模型治理可解释性)；归档优先级P1',
    'RULE_LOGS': '风控决策维度；监管维度(金融科技模型治理可解释性)；归档优先级P1',
}


def main():
    # 加载工作簿(保留格式)
    wb = load_workbook(SRC)
    ws = wb['目录']

    # 找到表名所在列(E列)和备注说明列(J列)
    # 列: A=序号 B=所属数据库 C=所属模块 D=责任人 E=表名(英文) F=表名(中文)
    #     G=是否数据清理 H=清理策略 I=归档策略 J=备注说明
    table_col = 5   # E
    remark_col = 10  # J

    # 设置表头
    header_cell = ws.cell(row=1, column=remark_col, value='备注说明(归档维度分析)')
    header_cell.font = Font(bold=True, color='FFFFFF')
    header_cell.fill = PatternFill('solid', start_color='4472C4')
    header_cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # 按优先级设置颜色
    priority_colors = {
        'P0': 'FFC7CE',  # 红色 - 紧急
        'P1': 'FFEB9C',  # 黄色 - 高
        'P2': 'C6EFCE',  # 绿色 - 中
        'P3': 'BDD7EE',  # 蓝色 - 低
    }

    updated = 0
    not_found = []

    for row_idx in range(2, ws.max_row + 1):
        table_name = ws.cell(row=row_idx, column=table_col).value
        if not table_name:
            continue

        table_name_upper = str(table_name).strip().upper()

        # 查找维度说明
        dimension = DIMENSION_MAP.get(table_name_upper)
        if dimension:
            cell = ws.cell(row=row_idx, column=remark_col, value=dimension)
            cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

            # 根据优先级设置背景色
            for priority, color in priority_colors.items():
                if f'归档优先级{priority}' in dimension:
                    cell.fill = PatternFill('solid', start_color=color)
                    break

            updated += 1
        else:
            not_found.append(table_name_upper)

    # 调整列宽
    ws.column_dimensions['J'].width = 60

    # 保存(原文件被占用,保存为新文件)
    OUTPUT = SRC.replace('.xlsx', '_维度分析.xlsx')
    wb.save(OUTPUT)
    print(f'更新完成: 共更新 {updated} 张表的维度说明')
    print(f'输出文件: {OUTPUT}')
    if not_found:
        print(f'未找到匹配的表({len(not_found)}张):')
        for t in not_found:
            print(f'  - {t}')


if __name__ == '__main__':
    main()
