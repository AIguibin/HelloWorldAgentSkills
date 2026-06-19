import os
import zipfile
import json
from pathlib import Path

def package_skill(skill_path):
    skill_path = Path(skill_path)
    skill_name = skill_path.name
    
    output_path = skill_path.parent / f"{skill_name}.skill"
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zipf.write(file_path, arcname)
    
    print(f"技能已打包: {output_path}")
    print(f"文件大小: {os.path.getsize(output_path)} 字节")
    return output_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        package_skill(sys.argv[1])
    else:
        print("用法: python package_skill.py <技能目录路径>")
