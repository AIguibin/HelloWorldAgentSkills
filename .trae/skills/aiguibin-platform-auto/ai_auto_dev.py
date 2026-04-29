#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI自动化编程执行脚本
基于《AI编程技能规范文档V4.0_整合版》
"""

import argparse
import datetime
import yaml
from pathlib import Path

SKILL_DIR = Path(__file__).parent / ".trae" / "skills" / "aiguibin-platform-auto"

def load_exec_index():
    index_path = SKILL_DIR / "exec_index.yaml"
    if not index_path.exists():
        print(f"错误: 执行索引文件不存在 - {index_path}")
        return None
    with open(index_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_exec_index(index_data):
    index_path = SKILL_DIR / "exec_index.yaml"
    with open(index_path, 'w', encoding='utf-8') as f:
        yaml.dump(index_data, f, allow_unicode=True, default_flow_style=False)

def get_task_by_id(task_id):
    index_data = load_exec_index()
    if index_data is None:
        return None, None, None
    for stage_name, stage_info in index_data.get('stages', {}).items():
        for task in stage_info.get('tasks', []):
            if task.get('task_id') == task_id:
                return task, stage_name, stage_info
    return None, None, None

def update_task_status(task_id, status):
    index_data = load_exec_index()
    if index_data is None:
        return
    for stage_name, stage_info in index_data.get('stages', {}).items():
        for task in stage_info.get('tasks', []):
            if task.get('task_id') == task_id:
                task['status'] = status
                break
    save_exec_index(index_data)

def add_log(message, level="INFO"):
    index_data = load_exec_index()
    if index_data is None:
        return
    log_entry = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'level': level,
        'message': message
    }
    if 'logs' not in index_data:
        index_data['logs'] = []
    index_data['logs'].append(log_entry)
    save_exec_index(index_data)
    print(f"[{log_entry['timestamp']}] [{level}] {message}")

def execute_task(task_id):
    task, stage_name, stage_info = get_task_by_id(task_id)
    
    if task is None:
        print(f"错误: 未找到任务 {task_id}")
        return False
    
    print(f"\n{'='*60}")
    print(f"执行任务: {task_id}")
    print(f"任务名称: {task.get('name')}")
    print(f"所属阶段: {stage_name}")
    print(f"AI角色: {task.get('ai_role')}")
    print(f"{'='*60}\n")
    
    update_task_status(task_id, 'running')
    add_log(f"开始执行任务: {task_id} - {task.get('name')}")
    
    try:
        output_file = task.get('output')
        if output_file:
            output_path = SKILL_DIR / output_file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            task_content = generate_task_content(task_id, task)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(task_content)
            
            print(f"输出文件: {output_path}")
            print(f"任务状态: 完成")
        
        update_task_status(task_id, 'completed')
        add_log(f"任务执行完成: {task_id}", "INFO")
        return True
        
    except Exception as e:
        update_task_status(task_id, 'failed')
        add_log(f"任务执行失败: {task_id} - {str(e)}", "ERROR")
        print(f"错误: {str(e)}")
        return False

def generate_task_content(task_id, task):
    task_name = task.get('name', '')
    ai_role = task.get('ai_role', '')
    
    content = f"""# {task_name}

## 任务信息

| 项目 | 内容 |
|-----|------|
| 任务ID | {task_id} |
| 任务名称 | {task_name} |
| AI角色 | {ai_role} |
| 生成时间 | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |

## 执行说明

此任务由AI自动执行，基于《AI编程技能规范文档V4.0_整合版》生成。

## 输出内容

请根据任务描述和详细设计文档完成此任务的实现。

---

**生成方式**: AI自动生成
"""
    return content

def execute_stage(stage_num):
    index_data = load_exec_index()
    if index_data is None:
        return False
    stage_key = f"stage{stage_num}"
    
    if stage_key not in index_data.get('stages', {}):
        print(f"错误: 未找到阶段 {stage_num}")
        return False
    
    stage_info = index_data['stages'][stage_key]
    print(f"\n执行阶段: {stage_info.get('name')}")
    print(f"任务数: {len(stage_info.get('tasks', []))}")
    
    for task in stage_info.get('tasks', []):
        if task.get('status') != 'completed':
            execute_task(task.get('task_id'))
    
    return True

def execute_range(from_task, to_task):
    index_data = load_exec_index()
    if index_data is None:
        return False
    
    all_tasks = []
    for stage_name, stage_info in index_data.get('stages', {}).items():
        for task in stage_info.get('tasks', []):
            all_tasks.append(task.get('task_id'))
    
    try:
        from_idx = all_tasks.index(from_task)
        to_idx = all_tasks.index(to_task)
        
        for task_id in all_tasks[from_idx:to_idx+1]:
            execute_task(task_id)
        
        return True
    except ValueError as e:
        print(f"错误: 任务ID不存在 - {str(e)}")
        return False

def show_status():
    index_data = load_exec_index()
    if index_data is None:
        return
    
    print("\n" + "="*60)
    print("AI自动化编程执行状态")
    print("="*60)
    
    total_tasks = 0
    completed_tasks = 0
    running_tasks = 0
    pending_tasks = 0
    failed_tasks = 0
    
    for stage_name, stage_info in index_data.get('stages', {}).items():
        print(f"\n{stage_info.get('name')}:")
        
        for task in stage_info.get('tasks', []):
            total_tasks += 1
            status = task.get('status', 'pending')
            
            if status == 'completed':
                completed_tasks += 1
                status_icon = '[OK]'
            elif status == 'running':
                running_tasks += 1
                status_icon = '[..]'
            elif status == 'failed':
                failed_tasks += 1
                status_icon = '[XX]'
            else:
                pending_tasks += 1
                status_icon = '[  ]'
            
            print(f"  {status_icon} {task.get('task_id')}: {task.get('name')}")
    
    print(f"\n统计:")
    print(f"总任务: {total_tasks}")
    print(f"完成: {completed_tasks}")
    print(f"执行中: {running_tasks}")
    print(f"待执行: {pending_tasks}")
    print(f"失败: {failed_tasks}")
    print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(description='AI自动化编程执行脚本')
    parser.add_argument('--stage', type=int, help='执行指定阶段')
    parser.add_argument('--task', type=str, help='执行指定任务')
    parser.add_argument('--from', dest='from_task', type=str, help='起始任务ID')
    parser.add_argument('--to', dest='to_task', type=str, help='结束任务ID')
    parser.add_argument('--status', action='store_true', help='显示执行状态')
    parser.add_argument('--confirm', type=str, help='确认任务')
    parser.add_argument('--pass', dest='pass_confirm', action='store_true', help='通过确认')
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.task:
        execute_task(args.task)
    elif args.stage is not None:
        execute_stage(args.stage)
    elif args.from_task and args.to_task:
        execute_range(args.from_task, args.to_task)
    elif args.confirm:
        if args.pass_confirm:
            add_log(f"人工确认通过: {args.confirm}")
            print(f"确认通过: {args.confirm}")
        else:
            print(f"请使用 --pass 参数确认通过")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
