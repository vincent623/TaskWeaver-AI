#!/usr/bin/env python3
"""
TaskWeaver AI 核心模块测试脚本

用于测试统一数据模型和核心处理引擎的功能。
"""

from datetime import date, timedelta
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import Task, ProjectPlan
from core.processor import CoreProcessor


def create_sample_project():
    """创建一个示例项目用于测试"""
    
    # 创建任务列表
    tasks = [
        Task(
            id="task1",
            name="项目启动",
            start_date=date(2024, 1, 1),
            duration=3,
            status=["done"],
            section="项目启动"
        ),
        Task(
            id="task2",
            name="需求分析",
            dependencies=["task1"],
            duration=5,
            status=["done"],
            section="项目启动"
        ),
        Task(
            id="milestone1",
            name="需求确认里程碑",
            dependencies=["task2"],
            duration=0,
            is_milestone=True,
            status=["milestone"],
            section="项目启动"
        ),
        Task(
            id="task3",
            name="系统设计",
            dependencies=["milestone1"],
            duration=7,
            status=["active"],
            section="开发阶段"
        ),
        Task(
            id="task4",
            name="前端开发",
            dependencies=["task3"],
            duration=10,
            status=["active"],
            section="开发阶段"
        ),
        Task(
            id="task5",
            name="后端开发",
            dependencies=["task3"],
            duration=12,
            status=["crit"],
            section="开发阶段"
        ),
        Task(
            id="task6",
            name="系统测试",
            dependencies=["task4", "task5"],
            duration=5,
            status=["active"],
            section="测试阶段"
        ),
        Task(
            id="milestone2",
            name="项目完成里程碑",
            dependencies=["task6"],
            duration=0,
            is_milestone=True,
            status=["milestone"],
            section="测试阶段"
        )
    ]
    
    # 创建项目计划
    project = ProjectPlan(
        title="TaskWeaver AI 测试项目",
        description="用于测试核心功能的示例项目",
        tasks=tasks,
        created_date=date.today(),
        version="1.0"
    )
    
    return project


def test_data_model():
    """测试数据模型功能"""
    print("=== 测试数据模型 ===")
    
    # 创建示例项目
    project = create_sample_project()
    
    # 基本属性测试
    print(f"项目标题: {project.title}")
    print(f"任务总数: {project.total_tasks}")
    print(f"已完成任务: {project.completed_tasks}")
    print(f"里程碑数量: {project.milestone_count}")
    print(f"关键任务数量: {len(project.critical_tasks)}")
    
    # 分组测试
    sections = project.get_sections()
    print(f"项目分组: {sections}")
    
    for section in sections:
        section_tasks = project.get_tasks_by_section(section)
        print(f"  '{section}' 分组有 {len(section_tasks)} 个任务")
    
    # 任务查询测试
    task = project.get_task_by_id("task4")
    if task:
        print(f"\n任务详情 - {task.name}:")
        print(f"  ID: {task.id}")
        print(f"  状态: {task.status}")
        print(f"  分组: {task.section}")
        print(f"  持续时间: {task.duration} 天")
        
        # 依赖关系测试
        dependencies = project.get_task_dependencies(task.id)
        print(f"  前置任务: {[dep.name for dep in dependencies]}")
        
        dependents = project.get_task_dependents(task.id)
        print(f"  后续任务: {[dep.name for dep in dependents]}")
    
    print("\n✅ 数据模型测试通过\n")


def test_processor():
    """测试核心处理引擎功能"""
    print("=== 测试核心处理引擎 ===")
    
    # 创建示例项目
    project = create_sample_project()
    
    # 创建处理引擎
    processor = CoreProcessor(project)
    
    # 验证项目计划
    errors = processor.validate_plan()
    if errors:
        print("❌ 项目计划验证失败:")
        for error in errors:
            print(f"  - {error}")
        return
    else:
        print("✅ 项目计划验证通过")
    
    # 计算日期
    try:
        processed_project = processor.calculate_dates()
        print("✅ 日期计算完成")
        
        # 显示计算后的任务日期
        print("\n任务日期计算结果:")
        for task in processed_project.tasks:
            print(f"  {task.name}: {task.start_date} ~ {task.end_date} ({task.duration}天)")
        
    except Exception as e:
        print(f"❌ 日期计算失败: {e}")
        return
    
    # 获取关键路径
    try:
        critical_path = processor.get_critical_path()
        print(f"\n关键路径上的任务数量: {len(critical_path)}")
        print("关键路径任务:")
        for task in critical_path:
            print(f"  - {task.name} ({task.id})")
    except Exception as e:
        print(f"❌ 关键路径计算失败: {e}")
    
    # 获取项目统计信息
    try:
        stats = processor.get_project_statistics()
        print(f"\n项目统计信息:")
        print(f"  总工期: {stats['total_duration']} 天")
        print(f"  完成率: {stats['completion_rate']:.1f}%")
        print(f"  进行中任务: {stats['active_tasks']}")
        print(f"  项目开始日期: {stats['start_date']}")
        print(f"  项目结束日期: {stats['end_date']}")
        
    except Exception as e:
        print(f"❌ 统计信息获取失败: {e}")
    
    print("\n✅ 核心处理引擎测试通过\n")


def test_error_handling():
    """测试错误处理"""
    print("=== 测试错误处理 ===")
    
    # 测试循环依赖
    try:
        tasks = [
            Task(id="A", name="任务A", dependencies=["C"], duration=1),
            Task(id="B", name="任务B", dependencies=["A"], duration=1),
            Task(id="C", name="任务C", dependencies=["B"], duration=1),
        ]
        
        project = ProjectPlan(title="循环依赖测试", tasks=tasks)
        processor = CoreProcessor(project)
        processor.calculate_dates()
        
        print("❌ 应该检测到循环依赖")
        
    except ValueError as e:
        print(f"✅ 正确检测到循环依赖: {e}")
    
    # 测试无效依赖
    try:
        tasks = [
            Task(id="A", name="任务A", dependencies=["B"], duration=1),
            Task(id="B", name="任务B", dependencies=["C"], duration=1),
        ]
        
        project = ProjectPlan(title="无效依赖测试", tasks=tasks)
        # 这个应该在 Pydantic 验证时失败
        print("❌ 应该检测到无效依赖")
        
    except Exception as e:
        print(f"✅ 正确检测到无效依赖: {e}")
    
    print("\n✅ 错误处理测试通过\n")


def main():
    """主测试函数"""
    print("TaskWeaver AI 核心模块测试")
    print("=" * 50)
    
    try:
        test_data_model()
        test_processor()
        test_error_handling()
        
        print("🎉 所有测试通过！核心模块工作正常。")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
