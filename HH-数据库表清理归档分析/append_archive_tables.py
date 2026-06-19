# -*- coding: utf-8 -*-
"""
为129张新增归档表生成清理策略(H列)和维度说明(J列)
追加到湖北农信清理归档表清单_维度分析.xlsx
"""
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
import re

SRC = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\DD-湖北农信基础配置检核\湖北农信清理归档表清单_维度分析.xlsx'
SCAN_FILE = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\all_tables_scan.xlsx'


def generate_cleanup_strategy(table_en, table_cn, module):
    """根据表名和模块生成清理策略(H列)"""
    name_upper = table_en.upper()
    cn_name = str(table_cn)

    # 1. 日志类 - 保留6个月到1年
    if 'LOG' in name_upper:
        if 'OPERATION' in name_upper or 'AUDIT' in name_upper:
            return '按月创建历史表,表命名规则为{TABLE}_YYYYMM,保留6个月数据,6个月以上数据清理至历史表,1年以上历史表归档至冷存储'
        elif 'EXCEPTION' in name_upper:
            return '按月创建历史表,保留3个月数据,3个月以上清理至历史表,1年以上归档'
        elif 'LOGIN' in name_upper or 'PWD' in name_upper:
            return '按月创建历史表,保留6个月数据(网络安全法要求),6个月以上清理至历史表'
        elif 'CALLBACK' in name_upper:
            return '保留3个月数据,3个月以上清理至历史表'
        elif 'SYNC' in name_upper:
            return '保留1个月数据,1个月以上清理'
        elif 'CREDIT_REPORT' in name_upper or 'CREDIT_REPORT_LOG' in name_upper:
            return '保留2年数据(征信业管理条例),2年以上清理至历史表,5年以上归档'
        else:
            return '按月创建历史表,保留1年数据,1年以上清理至历史表,3年以上归档至冷存储'

    # 2. 历史类 - 按年归档
    if 'HIST' in name_upper:
        return '按年创建历史表,表命名规则为{TABLE}_YYYY,2年以上数据清理至历史表,5年以上历史表归档'

    # 3. 流水/记录类
    if 'REC' in name_upper or 'RECORD' in name_upper:
        if 'AUDIT' in name_upper or 'APPROVE' in name_upper:
            return '按年创建历史表,2年以上数据清理至历史表,5年以上归档(审批档案10年)'
        elif 'IMPORT' in name_upper or 'TRANSFER' in name_upper:
            return '保留1年数据,1年以上清理至历史表'
        elif 'MERGER' in name_upper or 'DEACT' in name_upper:
            return '按年创建历史表,2年以上数据清理至历史表,5年以上归档'
        elif 'RVRS' in name_upper:
            return '按年创建历史表,2年以上数据清理至历史表,5年以上归档(会计凭证10年)'
        elif 'SMS' in name_upper:
            return '保留1年数据,1年以上清理(通信短信息服务管理规定3年)'
        elif 'ERR' in name_upper:
            return '保留3个月数据,3个月以上清理'
        elif 'CALC' in name_upper:
            return '保留6个月数据,6个月以上清理'
        elif 'SIGN' in name_upper:
            return '按年创建历史表,2年以上数据清理至历史表(电子签名法)'
        elif 'SEARCH' in name_upper:
            return '保留6个月数据,6个月以上清理'
        elif 'OPER' in name_upper:
            return '按年创建历史表,1年以上数据清理至历史表,3年以上归档'
        else:
            return '按年创建历史表,2年以上数据清理至历史表,5年以上归档'

    # 4. 流水表
    if 'STTN' in name_upper:
        return '按年创建历史表,2年以上数据清理至历史表,5年以上归档'

    # 5. 任务类
    if 'TSK' in name_upper:
        if 'ALCT' in name_upper or 'TRGT' in name_upper:
            return '任务完结后1年清理至历史表,3年以上归档'
        else:
            return '按年创建历史表,通过业务编号关联任务表,流程状态为完结(3/5/6)的2年以上数据清理至历史表,5年以上归档'

    # 6. 临时表 - 实时清理
    if 'TEMP' in name_upper:
        return '临时表,每日清理,仅保留当日数据,不归档'

    # 7. 中间表
    if 'MIDDLE' in name_upper:
        return '中间表,每日清理,仅保留当日数据,不归档'

    # 8. 批量文件临时表
    if name_upper.startswith('BTCH_FILE_') or name_upper.startswith('BTCH_U_'):
        return '批量临时表,每次批量执行后清理,不归档'

    # 9. undo_log
    if 'UNDO_LOG' in name_upper:
        return '事务回滚表,系统自动管理,不归档'

    # 10. 消息发送记录
    if 'MSG_SEND' in name_upper:
        return '保留3个月数据,3个月以上清理'

    # 11. 报告/审批相关
    if 'REPORT' in name_upper or 'APPROVE' in name_upper:
        return '按年创建历史表,2年以上数据清理至历史表,5年以上归档'

    # 默认策略
    return '按年创建历史表,2年以上数据清理至历史表,5年以上归档'


def generate_dimension_note(table_en, table_cn, module):
    """根据表名和模块生成维度说明(J列)"""
    name_upper = table_en.upper()
    cn = str(table_cn)

    # 基础维度
    lifecycle = ''
    product = ''
    legal = ''
    regulatory = ''
    priority = 'P2'

    # 1. 业务生命周期维度判断
    if any(kw in name_upper for kw in ['CMPN', 'MARKET']):
        lifecycle = '业务生命周期/营销阶段'
        priority = 'P0'
    elif any(kw in name_upper for kw in ['APLY', 'APPL', 'APPROVE', 'APRV']):
        lifecycle = '业务生命周期/申请审批阶段'
    elif any(kw in name_upper for kw in ['CTR', 'CONT', 'CONTRACT']):
        lifecycle = '业务生命周期/合同阶段'
    elif any(kw in name_upper for kw in ['DSBR', 'PAY', 'LDRP', 'REPY']):
        lifecycle = '业务生命周期/放还款阶段'
    elif any(kw in name_upper for kw in ['PSTLOAN', 'POSTLOAN', 'COLL', 'CHK', 'WARN']):
        lifecycle = '业务生命周期/贷后阶段'
    elif any(kw in name_upper for kw in ['RTG', 'RATING']):
        lifecycle = '业务生命周期/评级阶段'
    elif any(kw in name_upper for kw in ['CRLMT', 'ULM', 'LMT']):
        lifecycle = '业务生命周期/授信阶段'
    elif any(kw in name_upper for kw in ['ARCH']):
        lifecycle = '业务生命周期/档案阶段'
    elif any(kw in name_upper for kw in ['SYS', 'UAC', 'AUTH']):
        lifecycle = '系统运维维度'
        priority = 'P0' if 'LOG' in name_upper else 'P1'
    elif 'LOG' in name_upper:
        lifecycle = '系统运维维度'
        priority = 'P0'
    else:
        lifecycle = '业务生命周期/全流程'

    # 2. 产品维度判断
    if any(kw in name_upper for kw in ['CP_', 'CORP', 'CORPORAT']):
        product = '产品维度(对公)'
    elif any(kw in name_upper for kw in ['RT_', 'PRVT', 'PERSONAL', 'RTL']):
        product = '产品维度(零售)'
    elif any(kw in name_upper for kw in ['OL_', 'ONLINE']):
        product = '产品维度(线上贷款/普惠)'

    # 3. 法律维度判断
    if 'LOG' in name_upper:
        if any(kw in name_upper for kw in ['LOGIN', 'PWD', 'OPERATION', 'AUDIT']):
            legal = '法律维度(网络安全法日志留存6个月)'
        elif 'CREDIT' in name_upper:
            legal = '法律维度(征信业管理条例查询记录5年)'
        else:
            legal = '法律维度(网络安全法日志留存6个月)'
    elif 'HIST' in name_upper:
        legal = '法律维度(信贷档案10年)'
    elif any(kw in name_upper for kw in ['REC', 'RECORD']):
        if 'AUDIT' in name_upper or 'APPROVE' in name_upper:
            legal = '法律维度(授信尽职指引档案10年)'
        elif 'RVRS' in name_upper:
            legal = '法律维度(会计档案管理办法10年)'
        elif 'SMS' in name_upper:
            legal = '法律维度(通信短信息服务管理规定3年)'
        else:
            legal = '法律维度(业务档案10年)'
    elif 'STTN' in name_upper:
        legal = '法律维度(业务流水10年)'
    elif 'TSK' in name_upper:
        legal = '法律维度(业务档案10年)'
    elif 'TEMP' in name_upper:
        legal = '法律维度(数据最小化原则)'
        priority = 'P1'

    # 4. 监管维度判断
    if any(kw in name_upper for kw in ['G14', 'G40']):
        regulatory = '监管维度(1104大额风险暴露/资本充足率)'
    elif 'CREDIT' in name_upper and 'LOG' in name_upper:
        regulatory = '监管维度(征信报送)'
    elif 'WARN' in name_upper:
        regulatory = '监管维度(风险预警管理)'
    elif 'RULE' in name_upper:
        regulatory = '监管维度(金融科技模型治理可解释性)'
        priority = 'P1'
    elif 'COLL' in name_upper:
        regulatory = '监管维度(不良贷款处置)'
    elif 'CHK' in name_upper:
        regulatory = '监管维度(贷后管理指引)'

    # 组装维度说明
    parts = [lifecycle]
    if product:
        parts.append(product)
    if legal:
        parts.append(legal)
    if regulatory:
        parts.append(regulatory)
    parts.append(f'归档优先级{priority}')

    return '；'.join(parts)


def generate_archive_strategy(table_en, module):
    """生成归档策略(I列)"""
    name_upper = table_en.upper()

    if 'TEMP' in name_upper or name_upper.startswith('BTCH_FILE_') or name_upper.startswith('BTCH_U_'):
        return '不涉及(临时表)'
    if 'UNDO_LOG' in name_upper:
        return '不涉及(系统自动管理)'
    if 'LOG' in name_upper:
        return '针对1年以上的历史数据表,进行归档操作'
    if 'HIST' in name_upper:
        return '针对5年以上的历史数据表,进行归档操作'
    return '针对5年以上的历史数据表,进行归档操作'


def main():
    # 读取扫描结果
    scan_df = pd.read_excel(SCAN_FILE)

    # 排除不需要归档的表
    exclude_keywords = ['CONFIG', '_CFG', 'TEMPLATE', '_TPL', '_DEF_', '_DICT_', '_MAP_']
    mask = pd.Series(True, index=scan_df.index)
    for kw in exclude_keywords:
        mask &= ~scan_df['表英文名'].str.upper().str.contains(kw, na=False)

    archive_keywords = ['LOG', 'HIST', 'REC', 'STTN', 'TSK', 'MIDDLE', 'TEMP', 'RECORD']
    archive_mask = pd.Series(False, index=scan_df.index)
    for kw in archive_keywords:
        archive_mask |= scan_df['表英文名'].str.upper().str.contains(kw, na=False)

    archive_df = scan_df[mask & archive_mask].copy()

    # 去重(按表英文名)
    archive_df = archive_df.drop_duplicates(subset='表英文名', keep='first')

    # 限制在150条以内
    if len(archive_df) > 150:
        archive_df = archive_df.head(150)

    print(f'最终需要追加的表: {len(archive_df)}张')

    # 加载已有工作簿
    wb = load_workbook(SRC)
    ws = wb['目录']

    # 找到最后一行
    last_row = ws.max_row
    print(f'当前最后一行: {last_row}')

    # 获取已有表名(避免重复)
    existing_tables = set()
    for row_idx in range(2, last_row + 1):
        table_name = ws.cell(row=row_idx, column=5).value
        if table_name:
            existing_tables.add(str(table_name).strip().upper())

    # 优先级颜色
    priority_colors = {
        'P0': 'FFC7CE',
        'P1': 'FFEB9C',
        'P2': 'C6EFCE',
        'P3': 'BDD7EE',
    }

    # 追加新表
    added = 0
    skipped = 0
    current_row = last_row + 1

    for _, row in archive_df.iterrows():
        table_en = str(row['表英文名']).strip()
        if table_en.upper() in existing_tables:
            skipped += 1
            continue

        # 生成各列内容
        table_cn = str(row['表中文名'])
        module = str(row['模块'])
        db = str(row['数据库'])

        cleanup_strategy = generate_cleanup_strategy(table_en, table_cn, module)
        archive_strategy = generate_archive_strategy(table_en, module)
        dimension_note = generate_dimension_note(table_en, table_cn, module)

        # 写入数据
        ws.cell(row=current_row, column=1, value=added + 1)  # 序号
        ws.cell(row=current_row, column=2, value=db)  # 所属数据库
        ws.cell(row=current_row, column=3, value=module)  # 所属模块
        ws.cell(row=current_row, column=4, value='系统分析')  # 责任人
        ws.cell(row=current_row, column=5, value=table_en)  # 表名(英文)
        ws.cell(row=current_row, column=6, value=table_cn)  # 表名(中文)
        ws.cell(row=current_row, column=7, value='是')  # 是否数据清理
        ws.cell(row=current_row, column=8, value=cleanup_strategy)  # 清理策略
        ws.cell(row=current_row, column=9, value=archive_strategy)  # 归档策略

        # J列维度说明
        cell_j = ws.cell(row=current_row, column=10, value=dimension_note)
        cell_j.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

        # 根据优先级设置颜色
        for priority, color in priority_colors.items():
            if f'归档优先级{priority}' in dimension_note:
                cell_j.fill = PatternFill('solid', start_color=color)
                break

        # 设置H列和I列的换行
        ws.cell(row=current_row, column=8).alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
        ws.cell(row=current_row, column=9).alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

        added += 1
        current_row += 1

    # 调整列宽
    ws.column_dimensions['H'].width = 50
    ws.column_dimensions['I'].width = 30
    ws.column_dimensions['J'].width = 60

    # 保存
    OUTPUT = SRC.replace('.xlsx', '_完整版.xlsx')
    wb.save(OUTPUT)

    print(f'追加完成: 新增 {added} 张表, 跳过 {skipped} 张已存在表')
    print(f'总表数: {last_row - 1 + added}张')
    print(f'输出文件: {OUTPUT}')


if __name__ == '__main__':
    main()
