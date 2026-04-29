#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
递归遍历目录，解析 error-code.properties 文件并生成结构化输出
"""

import os
import re
import csv
from pathlib import Path
from typing import List, Tuple, Optional


def decode_unicode_escaped(text: str) -> str:
    """
    将Unicode转义序列（如 \u4EA4\u6613\u6210\u529F）转换为中文字符
    """
    def replace_unicode(match):
        try:
            return chr(int(match.group(1), 16))
        except ValueError:
            return match.group(0)
    
    pattern = r'\\u([0-9a-fA-F]{4})'
    return re.sub(pattern, replace_unicode, text)


def parse_properties_line(line: str) -> Optional[Tuple[str, str]]:
    """
    解析properties文件的一行，提取错误码和错误信息
    返回 (error_code, error_message) 或 None（如果是空行或注释）
    """
    line = line.strip()
    
    if not line or line.startswith('#') or line.startswith('!'):
        return None
    
    if '=' not in line:
        return None
    
    parts = line.split('=', 1)
    if len(parts) != 2:
        return None
    
    error_code = parts[0].strip()
    error_message = parts[1].strip()
    
    if not error_code:
        return None
    
    error_message = decode_unicode_escaped(error_message)
    
    return (error_code, error_message)


def get_service_module(file_path: str, root_dir: str) -> str:
    """
    获取服务模块名称（相对于根目录的二级目录名）
    根目录为一级，根目录下的直接子目录为二级目录
    """
    rel_path = os.path.relpath(file_path, root_dir)
    parts = rel_path.split(os.sep)
    
    if len(parts) >= 1:
        return parts[0]
    else:
        return "unknown"


def should_exclude_dir(dir_name: str, exclude_dirs: List[str]) -> bool:
    """
    检查目录是否应该被排除
    """
    return dir_name in exclude_dirs


def should_exclude_file(file_name: str, exclude_extensions: List[str]) -> bool:
    """
    检查文件是否应该被排除
    """
    for ext in exclude_extensions:
        if file_name.endswith(ext):
            return True
    return False


def find_properties_files(root_dir: str, 
                          target_filename: str = "default-error-code.properties",
                          exclude_dirs: List[str] = None,
                          exclude_extensions: List[str] = None) -> List[str]:
    """
    递归查找所有符合条件的properties文件
    """
    if exclude_dirs is None:
        exclude_dirs = ['.git', 'target', 'node_modules', '.idea', '.vscode', 'bin', 'dist', '__pycache__']
    
    if exclude_extensions is None:
        exclude_extensions = ['.class', '.jar', '.war']
    
    found_files = []
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not should_exclude_dir(d, exclude_dirs)]
        
        for file in files:
            if should_exclude_file(file, exclude_extensions):
                continue
            
            if file == target_filename:
                found_files.append(os.path.join(root, file))
    
    return found_files


def process_properties_file(file_path: str, root_dir: str) -> List[Tuple[str, str, str]]:
    """
    处理单个properties文件，返回 (服务模块, 错误码, 错误信息) 列表
    """
    results = []
    service_module = get_service_module(file_path, root_dir)
    
    encodings = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
    content = None
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.readlines()
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        print(f"警告: 无法读取文件 {file_path}")
        return results
    
    for line in content:
        parsed = parse_properties_line(line)
        if parsed:
            error_code, error_message = parsed
            results.append((service_module, error_code, error_message))
    
    return results


def generate_output_csv(results: List[Tuple[str, str, str]], output_file: str):
    """
    生成CSV格式的输出文件
    """
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['序号', '服务模块', '错误码', '错误信息'])
        
        for idx, (service_module, error_code, error_message) in enumerate(results, 1):
            writer.writerow([idx, service_module, error_code, error_message])


def main():
    root_dir = r"e:\AutoOffice\zzzzzzzz-common-inbox"
    output_file = r"e:\AutoOffice\error_codes_output.csv"
    target_filename = "default-error-code.properties"
    
    exclude_dirs = ['.git', 'target', 'node_modules', '.idea', '.vscode', 'bin', 'dist', '__pycache__', '.settings', '.gradle']
    exclude_extensions = ['.class', '.jar', '.war']
    
    print(f"开始扫描目录: {root_dir}")
    print(f"排除目录: {exclude_dirs}")
    print(f"排除文件扩展名: {exclude_extensions}")
    print(f"目标文件名: {target_filename}")
    print("-" * 50)
    
    found_files = find_properties_files(root_dir, target_filename, exclude_dirs, exclude_extensions)
    
    if not found_files:
        print(f"未找到文件: {target_filename}")
        return
    
    print(f"找到 {len(found_files)} 个文件:")
    for f in found_files:
        print(f"  - {f}")
    print("-" * 50)
    
    all_results = []
    for file_path in found_files:
        print(f"处理文件: {file_path}")
        results = process_properties_file(file_path, root_dir)
        all_results.extend(results)
        print(f"  提取了 {len(results)} 条错误码")
    
    print("-" * 50)
    print(f"总共提取了 {len(all_results)} 条错误码")
    
    generate_output_csv(all_results, output_file)
    print(f"输出文件已生成: {output_file}")
    
    print("\n前5条记录预览:")
    for idx, (service_module, error_code, error_message) in enumerate(all_results[:5], 1):
        print(f"  {idx}. [{service_module}] {error_code} = {error_message}")


if __name__ == "__main__":
    main()
