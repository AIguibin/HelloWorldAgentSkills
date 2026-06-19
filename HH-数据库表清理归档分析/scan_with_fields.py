# -*- coding: utf-8 -*-
"""
深度扫描EE目录,读取每张表的字段结构信息
基于信贷业务逻辑判断归档必要性(非关键词匹配)
"""
import os
import pandas as pd
import json

EE_DIR = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\EE-湖北农信新信贷数据库设计文档'
EXISTING_FILE = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\DD-湖北农信基础配置检核\湖北农信清理归档表清单_维度分析.xlsx'

MODULE_MAP = {
    '产品管理': '产品管理', '信贷引擎库': '信贷引擎', '合同管理': '合同管理',
    '客户中心库': '客户中心', '客户管理': '客户管理', '工作流程库': '工作流程',
    '批量管理': '批量管理', '押品管理': '押品管理', '授信管理': '授信管理',
    '放还款组': '放还款组', '架构管理': '架构管理', '档案管理': '档案管理',
    '用信管理': '用信管理', '电子文档库': '电子文档', '系统管理': '系统管理',
    '线上贷款': '线上贷款', '统一认证库': '统一认证', '营销管理': '营销管理',
    '评级管理': '评级管理', '贷后管理': '贷后管理', '额度中心库': '额度中心',
    '风控中心': '风控中心', '风控中心库': '风控中心',
}
DB_MAP = {
    '产品管理': 'NCMS_CREDIT', '信贷引擎': 'NCMS_CREDIT', '合同管理': 'NCMS_CREDIT',
    '客户中心': 'NCMS_CUST', '客户管理': 'NCMS_CREDIT', '工作流程': 'NCMS_WF',
    '批量管理': 'NCMS_CREDIT', '押品管理': 'NCMS_CREDIT', '授信管理': 'NCMS_CREDIT',
    '放还款组': 'NCMS_CREDIT', '架构管理': 'NCMS_CREDIT', '档案管理': 'NCMS_CREDIT',
    '用信管理': 'NCMS_CREDIT', '电子文档': 'NCMS_DOC', '系统管理': 'NCMS_CREDIT',
    '线上贷款': 'NCMS_CREDIT', '统一认证': 'NCMS_AUTH', '营销管理': 'NCMS_CREDIT',
    '评级管理': 'NCMS_CREDIT', '贷后管理': 'NCMS_RCA', '额度中心': 'NCMS_CLM',
    '风控中心': 'NCMS_RISK',
}


def scan_all_tables_with_fields():
    """扫描所有表并读取字段结构"""
    all_tables = []

    # 读取已有表名
    existing_df = pd.read_excel(EXISTING_FILE, sheet_name='目录')
    existing_tables = set(existing_df['表名（英文）'].astype(str).str.upper().tolist())

    for filename in sorted(os.listdir(EE_DIR)):
        if not filename.endswith('.xlsx'):
            continue

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
                df = xl.parse(sheet_name)
            except Exception as e:
                continue

            if df.empty or len(df.columns) < 3:
                continue

            # 获取表英文名和中文名
            table_en = None
            table_cn = sheet_name

            if '表英文名' in df.columns:
                table_en = str(df['表英文名'].iloc[0]) if pd.notna(df['表英文名'].iloc[0]) else None
            elif len(df.columns) > 2:
                table_en = str(df.iloc[0, 1]) if pd.notna(df.iloc[0, 1]) else None

            if not table_en or table_en in ('nan', 'None'):
                table_en = sheet_name

            table_en = str(table_en).strip()

            # 过滤异常表名(修订记录页/日期/索引目录等非业务表)
            if table_en.startswith('2025') or table_en.startswith('2024') or table_en.startswith('2026'):
                continue
            if '索引目录' in table_en or '修订记录' in table_en or '返回目录' in table_en:
                continue
            if sheet_name in ('修订记录', '索引目录', '说明', 'Sheet1'):
                continue

            if table_en.upper() in existing_tables:
                continue

            # 提取字段信息
            fields = []
            field_cn = []
            if '字段英文名' in df.columns:
                fields = df['字段英文名'].dropna().astype(str).tolist()
            if '字段中文名' in df.columns:
                field_cn = df['字段中文名'].dropna().astype(str).tolist()
            elif '字段中文' in df.columns:
                field_cn = df['字段中文'].dropna().astype(str).tolist()

            # 提取字段类型
            field_types = []
            if '字段类型' in df.columns:
                field_types = df['字段类型'].dropna().astype(str).tolist()

            all_tables.append({
                '模块': module,
                '数据库': db,
                '表英文名': table_en,
                '表中文名': table_cn,
                '字段数': len(df),
                '字段英文列表': '|'.join(fields[:30]),  # 前30个字段
                '字段中文列表': '|'.join(field_cn[:30]),
                '字段类型列表': '|'.join(field_types[:30]),
            })

    return all_tables


def main():
    tables = scan_all_tables_with_fields()
    print(f'共扫描到 {len(tables)} 张新表')

    df = pd.DataFrame(tables)
    output = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\all_tables_with_fields.xlsx'
    df.to_excel(output, index=False)
    print(f'已保存到: {output}')

    # 按模块统计
    print('\n按模块统计:')
    print(df.groupby('模块').size().sort_values(ascending=False))


if __name__ == '__main__':
    main()
