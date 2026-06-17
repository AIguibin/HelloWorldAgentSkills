# -*- coding: utf-8 -*-
"""
基于业务逻辑分析结果,按优先级筛选150张以内需归档表
追加到维度分析文件,填写H列清理策略和J列维度说明
"""
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

SRC = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\DD-湖北农信基础配置检核\湖北农信清理归档表清单_维度分析.xlsx'
ANALYSIS_FILE = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\archive_analysis_by_logic.xlsx'


def generate_cleanup_strategy(biz_class, table_cn):
    """根据业务分类生成清理策略(H列)"""
    cn = str(table_cn)

    if biz_class == '日志审计':
        if '登录' in cn or '密码' in cn:
            return '按月创建历史表,表命名规则为{TABLE}_YYYYMM,保留6个月数据(网络安全法),6个月以上清理至历史表,1年以上归档至冷存储'
        elif '操作' in cn or '审计' in cn:
            return '按月创建历史表,保留6个月数据,6个月以上清理至历史表,1年以上归档'
        elif '异常' in cn:
            return '按月创建历史表,保留3个月数据,3个月以上清理至历史表'
        elif '征信' in cn:
            return '保留2年数据(征信业管理条例),2年以上清理至历史表,5年以上归档'
        else:
            return '按月创建历史表,保留1年数据,1年以上清理至历史表,3年以上归档'

    elif biz_class == '历史变更':
        return '按年创建历史表,表命名规则为{TABLE}_YYYY,2年以上数据清理至历史表,5年以上历史表归档'

    elif biz_class == '流水记录':
        if '还款' in cn or '放款' in cn or '扣款' in cn:
            return '按年创建历史表,2年以上数据清理至历史表,5年以上归档(会计档案10年)'
        elif '征信' in cn:
            return '保留2年数据,2年以上清理至历史表,5年以上归档(征信业管理条例)'
        elif '短信' in cn or '消息' in cn:
            return '保留1年数据,1年以上清理(通信短信息服务管理规定3年)'
        else:
            return '按年创建历史表,2年以上数据清理至历史表,5年以上归档'

    elif biz_class == '流程任务':
        return '按年创建历史表,通过业务编号关联任务表,流程状态为完结(3/5/6)的2年以上数据清理至历史表,5年以上归档'

    elif biz_class == '业务明细':
        return '按年创建历史表,2年以上数据清理至历史表,5年以上归档(信贷档案10年)'

    elif biz_class == '营销数据':
        return '清理创建时间大于等于1年的数据,个保法要求目的达成后删除'

    elif biz_class == '授信审批':
        return '按年创建历史表,2年以上数据清理至历史表,5年以上归档(授信档案10年)'

    elif biz_class == '用信审批':
        return '按年创建历史表,2年以上数据清理至历史表,5年以上归档(信贷档案10年)'

    elif biz_class == '合同数据':
        return '按年创建历史表,合同结清满2年数据清理至历史表,5年以上归档(民法典诉讼时效3年)'

    elif biz_class == '放还款交易':
        return '按年创建历史表,合同结清满2年数据清理至历史表,5年以上归档(会计档案10年)'

    elif biz_class == '贷后管理':
        if '催收' in cn:
            return '按年创建历史表,针对更新日期5年以上的数据清理至历史表(诉讼时效3年)'
        elif '检查' in cn:
            return '按年创建历史表,通过业务编号关联检查任务表,流程状态为完结的2年以上数据清理至历史表,5年以上归档'
        elif '预警' in cn:
            return '按年创建历史表,流程状态为完结的2年以上数据清理至历史表,5年以上归档'
        else:
            return '按年创建历史表,2年以上数据清理至历史表,5年以上归档(信贷档案10年)'

    elif biz_class == '风险分类':
        return '按年创建历史表,针对借据状态为2或8的1年以上数据清理至历史表,5年以上归档(1104 G11)'

    elif biz_class == '额度数据':
        return '失效超过1年的备份至历史表,清理原表数据(1104大额风险暴露G14)'

    elif biz_class == '押品数据':
        return '按年创建历史表,2年以上数据清理至历史表,5年以上归档(担保档案10年)'

    elif biz_class == '档案管理':
        return '按年创建历史表,任务完结后2年以上数据清理至历史表,5年以上归档(档案法)'

    elif biz_class == '评级数据':
        return '按年创建历史表,2年以上数据清理至历史表,5年以上归档(授信档案10年)'

    elif biz_class == '线上贷款':
        return '按年创建历史表,业务终结满2年数据清理至历史表,5年以上归档(互联网贷款管理办法)'

    elif biz_class == '流程数据':
        return '按年创建历史表,流程完结后2年以上数据清理至历史表,5年以上归档(审批档案10年)'

    elif biz_class == '风控数据':
        if '征信' in cn:
            return '保留2年数据,2年以上清理至历史表,5年以上归档(征信业管理条例)'
        elif '预警' in cn:
            return '按年创建历史表,2年以上数据清理至历史表,5年以上归档(风险预警管理)'
        else:
            return '保留1年数据,1年以上清理至历史表,5年以上归档(模型治理要求)'

    elif biz_class == '征信数据':
        return '保留2年数据,2年以上清理至历史表,5年以上归档(征信业管理条例第20条)'

    elif biz_class == '消息通知':
        return '保留6个月数据,6个月以上清理'

    elif biz_class == '引擎日志':
        return '保留1年数据,1年以上清理至历史表,3年以上归档(模型治理可解释性)'

    elif biz_class == '批量日志':
        return '保留6个月数据,6个月以上清理至历史表'

    else:
        return '按年创建历史表,2年以上数据清理至历史表,5年以上归档'


def generate_archive_strategy(biz_class):
    """生成归档策略(I列)"""
    if biz_class in ['日志审计', '消息通知', '批量日志']:
        return '针对1年以上的历史数据表,进行归档操作'
    elif biz_class == '营销数据':
        return '不涉及(直接清理)'
    elif biz_class == '临时数据':
        return '不涉及(临时表)'
    else:
        return '针对5年以上的历史数据表,进行归档操作'


def generate_dimension_note(biz_class, module, table_cn):
    """生成维度说明(J列)"""
    cn = str(table_cn)

    # 业务生命周期维度
    lifecycle_map = {
        '营销数据': '业务生命周期/营销阶段',
        '授信审批': '业务生命周期/授信审批阶段',
        '用信审批': '业务生命周期/用信阶段',
        '合同数据': '业务生命周期/合同阶段',
        '放还款交易': '业务生命周期/放还款阶段',
        '贷后管理': '业务生命周期/贷后阶段',
        '风险分类': '业务生命周期/贷后阶段(风险分类)',
        '额度数据': '业务生命周期/授信阶段(额度管理)',
        '押品数据': '业务生命周期/合同阶段(担保)',
        '档案管理': '业务生命周期/档案阶段',
        '评级数据': '业务生命周期/评级阶段',
        '线上贷款': '业务生命周期/线上贷款全流程',
        '流程数据': '业务生命周期/审批流程',
        '流程任务': '业务生命周期/审批流程',
        '风控数据': '业务生命周期/风控决策',
        '征信数据': '业务生命周期/风控决策(征信)',
        '日志审计': '系统运维维度',
        '历史变更': '业务生命周期/全流程(变更追溯)',
        '流水记录': '业务生命周期/交易流水',
        '业务明细': '业务生命周期/业务明细',
        '消息通知': '系统运维维度(消息)',
        '引擎日志': '系统运维维度(规则引擎)',
        '批量日志': '系统运维维度(批量)',
    }
    lifecycle = lifecycle_map.get(biz_class, '业务生命周期/全流程')

    # 法律维度
    legal_map = {
        '日志审计': '法律维度(网络安全法日志留存6个月)',
        '历史变更': '法律维度(业务档案10年)',
        '流水记录': '法律维度(会计档案管理办法10年)',
        '营销数据': '法律维度(个保法数据最小化原则)',
        '授信审批': '法律维度(授信尽职指引档案10年)',
        '用信审批': '法律维度(信贷档案10年)',
        '合同数据': '法律维度(民法典合同编诉讼时效3年)',
        '放还款交易': '法律维度(会计档案管理办法10年)',
        '贷后管理': '法律维度(信贷档案10年)',
        '风险分类': '法律维度(1104监管要求10年)',
        '额度数据': '法律维度(1104大额风险暴露)',
        '押品数据': '法律维度(担保法/民法典担保编)',
        '档案管理': '法律维度(档案法信贷档案10年)',
        '评级数据': '法律维度(授信档案10年)',
        '线上贷款': '法律维度(互联网贷款管理办法)',
        '流程数据': '法律维度(审批档案10年)',
        '流程任务': '法律维度(审批档案10年)',
        '风控数据': '法律维度(模型治理可解释性5年)',
        '征信数据': '法律维度(征信业管理条例5年)',
        '消息通知': '法律维度(通信短信息服务管理规定3年)',
        '引擎日志': '法律维度(模型治理可解释性5年)',
        '批量日志': '法律维度(运维日志6个月)',
        '业务明细': '法律维度(信贷档案10年)',
    }
    legal = legal_map.get(biz_class, '法律维度(业务档案10年)')

    # 监管维度
    regulatory = ''
    if biz_class == '风险分类':
        regulatory = '监管维度(1104 G11五级分类)'
    elif biz_class == '额度数据':
        regulatory = '监管维度(1104 G14大额风险暴露)'
    elif biz_class == '风控数据':
        regulatory = '监管维度(金融科技模型治理)'
    elif biz_class == '征信数据':
        regulatory = '监管维度(征信报送)'
    elif biz_class == '贷后管理':
        if '催收' in cn:
            regulatory = '监管维度(不良贷款处置)'
        elif '预警' in cn:
            regulatory = '监管维度(风险预警管理)'
        else:
            regulatory = '监管维度(贷后管理指引)'
    elif biz_class == '放还款交易':
        regulatory = '监管维度(EAST还款明细)'
    elif biz_class == '合同数据':
        regulatory = '监管维度(EAST信贷合同)'
    elif biz_class == '线上贷款':
        regulatory = '监管维度(互联网贷款管理办法)'

    # 归档优先级
    priority_map = {
        '日志审计': 'P0', '营销数据': 'P0', '消息通知': 'P0',
        '流水记录': 'P2', '历史变更': 'P2', '业务明细': 'P2',
        '授信审批': 'P2', '用信审批': 'P2', '合同数据': 'P2',
        '放还款交易': 'P2', '贷后管理': 'P2', '风险分类': 'P2',
        '额度数据': 'P2', '押品数据': 'P2', '档案管理': 'P2',
        '评级数据': 'P2', '线上贷款': 'P2', '流程数据': 'P2',
        '流程任务': 'P2', '风控数据': 'P1', '征信数据': 'P1',
        '引擎日志': 'P1', '批量日志': 'P1',
    }
    priority = priority_map.get(biz_class, 'P2')

    # 组装
    parts = [lifecycle]
    if legal:
        parts.append(legal)
    if regulatory:
        parts.append(regulatory)
    parts.append(f'归档优先级{priority}')

    return '；'.join(parts)


def main():
    # 读取业务逻辑分析结果
    analysis_df = pd.read_excel(ANALYSIS_FILE)
    archive_df = analysis_df[analysis_df['是否需要归档'] == '是'].copy()

    print(f'需归档表总数: {len(archive_df)}')

    # 按业务分类优先级筛选,控制在150条以内
    # 策略: 按各业务分类的表数量比例分配配额,确保覆盖全业务场景
    # 同时保证核心业务(交易/审批/贷后)有足够代表性
    class_counts = archive_df.groupby('业务分类').size().to_dict()
    total_archive = len(archive_df)

    # 业务分类优先级权重(数字越大优先级越高)
    class_priority_weight = {
        '日志审计': 3, '营销数据': 3, '消息通知': 3,  # P0 高优先级
        '风控数据': 2, '征信数据': 2, '引擎日志': 2, '批量日志': 2,  # P1
        '流水记录': 2, '历史变更': 2, '业务明细': 2,  # P2 高频
        '贷后管理': 2, '线上贷款': 2, '押品数据': 2,  # P2 业务
        '授信审批': 2, '用信审批': 2, '合同数据': 2,  # P2 审批
        '放还款交易': 2, '额度数据': 2, '评级数据': 2,  # P2 核心
        '流程数据': 2, '流程任务': 2, '档案管理': 2, '风险分类': 2,  # P2 其他
    }

    # 计算每个业务分类的配额(按权重+数量比例)
    # 总配额: 86(已有) + 新增 <= 230, 所以新增 <= 144
    MAX_NEW = 144
    quota = {}
    total_weight = 0
    for cls, count in class_counts.items():
        weight = class_priority_weight.get(cls, 1)
        total_weight += weight * count

    for cls, count in class_counts.items():
        weight = class_priority_weight.get(cls, 1)
        # 配额 = (权重*数量 / 总权重) * MAX_NEW, 至少1张
        q = max(1, int(MAX_NEW * weight * count / total_weight))
        quota[cls] = min(q, count)  # 不能超过该分类实际数量

    # 调整配额总数到MAX_NEW
    total_quota = sum(quota.values())
    if total_quota > MAX_NEW:
        # 按配额从大到小依次减1
        sorted_cls = sorted(quota.items(), key=lambda x: -x[1])
        idx = 0
        while total_quota > MAX_NEW:
            cls, q = sorted_cls[idx % len(sorted_cls)]
            if quota[cls] > 1:
                quota[cls] -= 1
                total_quota -= 1
            idx += 1
    elif total_quota < MAX_NEW:
        # 补足到MAX_NEW
        sorted_cls = sorted(class_counts.items(), key=lambda x: -x[1])
        idx = 0
        while total_quota < MAX_NEW:
            cls = sorted_cls[idx % len(sorted_cls)][0]
            if quota.get(cls, 0) < class_counts[cls]:
                quota[cls] = quota.get(cls, 0) + 1
                total_quota += 1
            idx += 1

    print('各业务分类配额分配:')
    for cls in sorted(quota.keys(), key=lambda x: -quota[x]):
        print(f'  {cls}: {quota[cls]}/{class_counts[cls]}')

    # 按配额筛选
    selected = []
    for biz_class, q in quota.items():
        class_df = archive_df[archive_df['业务分类'] == biz_class].head(q)
        for _, row in class_df.iterrows():
            selected.append(row.to_dict())

    selected_df = pd.DataFrame(selected)
    print(f'\n筛选后追加表数: {len(selected_df)}')

    # 加载已有工作簿
    wb = load_workbook(SRC)
    ws = wb['目录']
    last_row = ws.max_row
    print(f'当前最后一行: {last_row}')

    # 获取已有表名
    existing_tables = set()
    for row_idx in range(2, last_row + 1):
        table_name = ws.cell(row=row_idx, column=5).value
        if table_name:
            existing_tables.add(str(table_name).strip().upper())

    priority_colors = {
        'P0': 'FFC7CE', 'P1': 'FFEB9C', 'P2': 'C6EFCE', 'P3': 'BDD7EE',
    }

    added = 0
    skipped = 0
    current_row = last_row + 1

    for _, row in selected_df.iterrows():
        table_en = str(row['表英文名']).strip()
        if table_en.upper() in existing_tables:
            skipped += 1
            continue

        table_cn = str(row['表中文名'])
        module = str(row['模块'])
        db = str(row['数据库'])
        biz_class = str(row['业务分类'])

        cleanup_strategy = generate_cleanup_strategy(biz_class, table_cn)
        archive_strategy = generate_archive_strategy(biz_class)
        dimension_note = generate_dimension_note(biz_class, module, table_cn)

        # 写入数据
        ws.cell(row=current_row, column=1, value=added + 1)
        ws.cell(row=current_row, column=2, value=db)
        ws.cell(row=current_row, column=3, value=module)
        ws.cell(row=current_row, column=4, value='系统分析')
        ws.cell(row=current_row, column=5, value=table_en)
        ws.cell(row=current_row, column=6, value=table_cn)
        ws.cell(row=current_row, column=7, value='是')
        ws.cell(row=current_row, column=8, value=cleanup_strategy)
        ws.cell(row=current_row, column=9, value=archive_strategy)

        cell_j = ws.cell(row=current_row, column=10, value=dimension_note)
        cell_j.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

        for priority, color in priority_colors.items():
            if f'归档优先级{priority}' in dimension_note:
                cell_j.fill = PatternFill('solid', start_color=color)
                break

        ws.cell(row=current_row, column=8).alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
        ws.cell(row=current_row, column=9).alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

        added += 1
        current_row += 1

    ws.column_dimensions['H'].width = 50
    ws.column_dimensions['I'].width = 30
    ws.column_dimensions['J'].width = 60

    OUTPUT = SRC.replace('.xlsx', '_业务逻辑版.xlsx')
    wb.save(OUTPUT)

    print(f'\n追加完成: 新增 {added} 张表, 跳过 {skipped} 张已存在表')
    print(f'总表数: {last_row - 1 + added}张')
    print(f'输出文件: {OUTPUT}')

    # 统计
    print('\n新增表按业务分类统计:')
    print(selected_df.groupby('业务分类').size().sort_values(ascending=False))


if __name__ == '__main__':
    main()
