#!/usr/bin/env python3
"""
Excel Splitter - 按指定列拆分Excel文件

Usage:
    python split.py --input <input_file> --output <output_dir> --column <column_name_or_index> [--sheet <sheet_name>]
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd


def sanitize_filename(name: str) -> str:
    """将字符串转换为安全的文件名"""
    safe_name = str(name)
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        safe_name = safe_name.replace(char, '_')
    safe_name = safe_name.strip()
    if not safe_name:
        safe_name = "unnamed"
    return safe_name


def split_excel(
    input_file: str,
    output_dir: str,
    split_column: str,
    sheet_name: str = None
) -> dict:
    """
    按指定列拆分Excel文件
    
    Args:
        input_file: 输入Excel文件路径
        output_dir: 输出目录路径
        split_column: 拆分列名或列索引
        sheet_name: 工作表名称(可选)
    
    Returns:
        dict: 拆分结果统计
    """
    input_path = Path(input_file)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_file}")
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"读取文件: {input_path}")
    
    if sheet_name:
        df = pd.read_excel(input_path, sheet_name=sheet_name)
        print(f"工作表: {sheet_name}")
    else:
        df = pd.read_excel(input_path)
        print(f"工作表: 默认(第一个)")
    
    print(f"总行数: {len(df)}")
    print(f"列名: {list(df.columns)}")
    
    if split_column.isdigit():
        col_index = int(split_column)
        if col_index >= len(df.columns):
            raise ValueError(f"列索引 {col_index} 超出范围(共 {len(df.columns)} 列)")
        column_name = df.columns[col_index]
    else:
        column_name = split_column
        if column_name not in df.columns:
            raise ValueError(f"列名 '{column_name}' 不存在于文件中")
    
    print(f"拆分列: {column_name}")
    print()
    
    unique_values = df[column_name].dropna().unique()
    print(f"共有 {len(unique_values)} 个唯一值")
    print()
    
    results = []
    
    for value in unique_values:
        if pd.isna(value):
            continue
        
        subset = df[df[column_name] == value]
        safe_name = sanitize_filename(value)
        output_file = output_path / f"{safe_name}.xlsx"
        
        subset.to_excel(output_file, index=False, sheet_name='Sheet1')
        
        results.append({
            'value': str(value),
            'file': output_file.name,
            'rows': len(subset)
        })
        print(f"  - {output_file.name} ({len(subset)} 行)")
    
    print()
    print(f"拆分完成! 共生成 {len(results)} 个文件")
    print(f"输出目录: {output_path}")
    
    return {
        'total_rows': len(df),
        'split_column': column_name,
        'files_generated': len(results),
        'output_dir': str(output_path),
        'details': results
    }


def main():
    parser = argparse.ArgumentParser(
        description='按指定列拆分Excel文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python split.py -i data.xlsx -o output -c "部门"
  python split.py -i data.xlsx -o output -c 0
  python split.py -i data.xlsx -o output -c "部门" -s "Sheet2"
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='输入Excel文件路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='输出目录路径'
    )
    
    parser.add_argument(
        '-c', '--column',
        required=True,
        help='拆分列名或列索引(从0开始)'
    )
    
    parser.add_argument(
        '-s', '--sheet',
        default=None,
        help='工作表名称(可选，默认使用第一个sheet)'
    )
    
    args = parser.parse_args()
    
    try:
        split_excel(
            input_file=args.input,
            output_dir=args.output,
            split_column=args.column,
            sheet_name=args.sheet
        )
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
