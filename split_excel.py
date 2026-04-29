import pandas as pd
from pathlib import Path

input_file = r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\湖北农信异常信息业务提示信息.xlsx'
output_dir = Path(r'e:\WorkSpace\HelloWorldAgentSkills\aiguibin-common-excel\拆分文件')

output_dir.mkdir(exist_ok=True)

df = pd.read_excel(input_file, sheet_name='Sheet3')

print(f"总行数: {len(df)}")
print(f"列名: {list(df.columns)}")

project_col = df.columns[0]
print(f"\n工程名列: {project_col}")

projects = df[project_col].dropna().unique()
print(f"\n共有 {len(projects)} 个工程:")
for p in projects[:10]:
    print(f"  - {p}")
if len(projects) > 10:
    print(f"  ... 还有 {len(projects) - 10} 个工程")

for project in projects:
    if pd.isna(project):
        continue
    
    project_df = df[df[project_col] == project]
    
    safe_name = str(project).replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    output_file = output_dir / f"{safe_name}.xlsx"
    
    project_df.to_excel(output_file, index=False, sheet_name='Sheet1')
    print(f"已生成: {output_file.name} ({len(project_df)} 行)")

print(f"\n拆分完成! 文件保存在: {output_dir}")
