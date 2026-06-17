# -*- coding: utf-8 -*-
"""
扫描EE目录下所有数据库设计文档,提取每张表的基本信息
用于后续归档策略分析
"""
import os
import pandas as pd
import json

EE_DIR = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\EE-湖北农信新信贷数据库设计文档'

# 已有的86张表
EXISTING_FILE = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\DD-湖北农信基础配置检核\湖北农信清理归档表清单_维度分析.xlsx'

# 模块名映射(文件名 -> 模块名)
MODULE_MAP = {
    '产品管理': '产品管理',
    '信贷引擎库': '信贷引擎',
    '合同管理': '合同管理',
    '客户中心库': '客户中心',
    '客户管理': '客户管理',
    '工作流程库': '工作流程',
    '批量管理': '批量管理',
    '押品管理': '押品管理',
    '授信管理': '授信管理',
    '放还款组': '放还款组',
    '架构管理': '架构管理',
    '档案管理': '档案管理',
    '用信管理': '用信管理',
    '电子文档库': '电子文档',
    '系统管理': '系统管理',
    '线上贷款': '线上贷款',
    '统一认证库': '统一认证',
    '营销管理': '营销管理',
    '评级管理': '评级管理',
    '贷后管理': '贷后管理',
    '额度中心库': '额度中心',
    '风控中心': '风控中心',
    '风控中心库': '风控中心',
}

# 数据库映射
DB_MAP = {
    '产品管理': 'NCMS_CREDIT',
    '信贷引擎库': 'NCMS_CREDIT',
    '合同管理': 'NCMS_CREDIT',
    '客户中心库': 'NCMS_CUST',
    '客户管理': 'NCMS_CREDIT',
    '工作流程库': 'NCMS_WF',
    '批量管理': 'NCMS_CREDIT',
    '押品管理': 'NCMS_CREDIT',
    '授信管理': 'NCMS_CREDIT',
    '放还款组': 'NCMS_CREDIT',
    '架构管理': 'NCMS_CREDIT',
    '档案管理': 'NCMS_CREDIT',
    '用信管理': 'NCMS_CREDIT',
    '电子文档库': 'NCMS_DOC',
    '系统管理': 'NCMS_CREDIT',
    '线上贷款': 'NCMS_CREDIT',
    '统一认证库': 'NCMS_AUTH',
    '营销管理': 'NCMS_CREDIT',
    '评级管理': 'NCMS_CREDIT',
    '贷后管理': 'NCMS_RCA',
    '额度中心库': 'NCMS_CLM',
    '风控中心': 'NCMS_RISK',
    '风控中心库': 'NCMS_RISK',
}


def extract_tables():
    """提取所有表的基本信息"""
    all_tables = []

    # 读取已有表名
    existing_df = pd.read_excel(EXISTING_FILE, sheet_name='目录')
    existing_tables = set(existing_df['表名（英文）'].astype(str).str.upper().tolist())

    # 遍历EE目录
    for filename in sorted(os.listdir(EE_DIR)):
        if not filename.endswith('.xlsx'):
            continue

        # 解析模块名
        module = None
        for key in MODULE_MAP:
            if key in filename:
                module = MODULE_MAP[key]
                break
        if not module:
            continue

        db = DB_MAP.get(module, 'NCMS_CREDIT')
        filepath = os.path.join(EE_DIR, filename)

        try:
            xl = pd.ExcelFile(filepath)
        except Exception as e:
            print(f'读取失败 {filename}: {e}')
            continue

        for sheet_name in xl.sheet_names:
            if sheet_name in ('目录', 'Sheet1', '说明'):
                continue

            try:
                df = xl.parse(sheet_name, nrows=3)
            except Exception as e:
                continue

            if df.empty or len(df.columns) < 3:
                continue

            # 获取表英文名和中文名
            table_en = None
            table_cn = sheet_name

            # 尝试从第二行获取表英文名
            if '表英文名' in df.columns:
                table_en = str(df['表英文名'].iloc[0]) if pd.notna(df['表英文名'].iloc[0]) else None
            elif len(df.columns) > 2:
                # 从第二列获取
                table_en = str(df.iloc[0, 1]) if pd.notna(df.iloc[0, 1]) else None

            if not table_en or table_en == 'nan' or table_en == 'None':
                # 使用sheet名作为表名
                table_en = sheet_name

            table_en = str(table_en).strip()

            # 跳过已有表
            if table_en.upper() in existing_tables:
                continue

            # 获取字段数量
            try:
                full_df = xl.parse(sheet_name)
                field_count = len(full_df)
            except:
                field_count = 0

            all_tables.append({
                '文件名': filename,
                '模块': module,
                '数据库': db,
                'sheet名': sheet_name,
                '表英文名': table_en,
                '表中文名': table_cn,
                '字段数': field_count,
            })

    return all_tables


def main():
    tables = extract_tables()
    print(f'共提取到 {len(tables)} 张新表(已排除已有86张)')

    # 按模块统计
    by_module = {}
    for t in tables:
        m = t['模块']
        by_module[m] = by_module.get(m, 0) + 1

    print('\n按模块统计:')
    for m, c in sorted(by_module.items(), key=lambda x: -x[1]):
        print(f'  {m}: {c}张')

    # 保存到临时文件
    df = pd.DataFrame(tables)
    output = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\all_tables_scan.xlsx'
    df.to_excel(output, index=False)
    print(f'\n已保存到: {output}')


if __name__ == '__main__':
    main()
