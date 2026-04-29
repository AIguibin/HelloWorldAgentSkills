#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import zipfile
import shutil
from pathlib import Path


def package_skill(skill_dir, output_dir=None):
    """
    打包skill目录为.skill文件
    
    Args:
        skill_dir: skill目录路径
        output_dir: 输出目录路径（可选，默认为skill目录的父目录）
    
    Returns:
        str: 生成的.skill文件路径
    """
    skill_path = Path(skill_dir)
    
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")
    
    # 读取skill名称
    skill_name = skill_path.name
    
    # 设置输出目录
    if output_dir is None:
        output_path = skill_path.parent
    else:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    
    # 创建.skill文件路径
    skill_file = output_path / f"{skill_name}.skill"
    
    print(f"打包skill: {skill_name}")
    print(f"源目录: {skill_path}")
    print(f"输出文件: {skill_file}")
    
    # 创建zip文件
    with zipfile.ZipFile(skill_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历skill目录
        for root, dirs, files in os.walk(skill_path):
            # 跳过__pycache__等目录
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.idea']]
            
            for file in files:
                # 跳过.pyc文件
                if file.endswith('.pyc'):
                    continue
                
                file_path = Path(root) / file
                # 计算相对路径
                arcname = file_path.relative_to(skill_path)
                
                print(f"  添加文件: {arcname}")
                zipf.write(file_path, arcname)
    
    print(f"\n✓ 打包完成: {skill_file}")
    print(f"文件大小: {skill_file.stat().st_size / 1024:.2f} KB")
    
    return str(skill_file)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='打包Claude Code skill')
    parser.add_argument('skill_dir', help='Skill目录路径')
    parser.add_argument('--output', help='输出目录路径（可选）')
    
    args = parser.parse_args()
    
    try:
        skill_file = package_skill(args.skill_dir, args.output)
        print(f"\nSkill文件已创建: {skill_file}")
        return 0
    except Exception as e:
        print(f"\n✗ 打包失败: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
