#!/usr/bin/env python3
"""
TaskWeaver AI Mermaid 解析器测试脚本

用于测试重构后的 Mermaid 解析器功能。
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.mermaid_parser import MermaidParser, MermaidValidator
from core.processor import CoreProcessor


def test_basic_parsing():
    """测试基本解析功能"""
    print("=== 测试基本解析功能 ===")
    
    mermaid_code = """
    gantt
        dateFormat  YYYY-MM-DD
        title       测试项目

        section 阶段一
        任务A       :taskA, done, 2024-01-01, 3d
        任务B       :taskB, active, after taskA, 5d
        里程碑A     :milestoneA, milestone, after taskB

        section 阶段二
        任务C       :taskC, crit, after milestoneA, 7d
        任务D       :taskD, active, after taskC, 4d
    """
    
    parser = MermaidParser()
    project_plan = parser.parse(mermaid_code)
    
    # 基本验证
    assert project_plan.title == "测试项目"
    assert project_plan.total_tasks == 5
    assert len(project_plan.get_sections()) == 2
    
    # 任务验证
    task_a = project_plan.get_task_by_id("taskA")
    assert task_a is not None
    assert task_a.name == "任务A"
    assert "done" in task_a.status
    assert task_a.duration == 3
    assert task_a.section == "阶段一"
    
    # 依赖验证
    task_b = project_plan.get_task_by_id("taskB")
    assert task_b is not None
    assert "taskA" in task_b.dependencies
    
    # 里程碑验证
    milestone_a = project_plan.get_task_by_id("milestoneA")
    assert milestone_a is not None
    assert milestone_a.is_milestone
    assert milestone_a.duration == 0
    
    print("✅ 基本解析功能测试通过")


def test_date_formats():
    """测试不同日期格式"""
    print("=== 测试日期格式支持 ===")
    
    # 测试不同的日期格式
    test_cases = [
        {
            "code": """
            gantt
                dateFormat  YYYY/MM/DD
                title       日期格式测试
                任务A       :taskA, done, 2024/01/01, 3d
            """,
            "expected_format": "%Y/%m/%d"
        },
        {
            "code": """
            gantt
                dateFormat  DD-MM-YYYY
                title       日期格式测试
                任务A       :taskA, done, 01-01-2024, 3d
            """,
            "expected_format": "%d-%m-%Y"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        parser = MermaidParser()
        project_plan = parser.parse(test_case["code"])
        
        print(f"测试用例 {i+1}: 期望格式 '{test_case['expected_format']}', 实际格式 '{project_plan.date_format}'")
        assert project_plan.date_format == test_case["expected_format"]
        print(f"✅ 日期格式测试用例 {i+1} 通过")


def test_dependency_handling():
    """测试依赖关系处理"""
    print("=== 测试依赖关系处理 ===")
    
    mermaid_code = """
    gantt
        dateFormat  YYYY-MM-DD
        title       依赖关系测试

        section 阶段一
        基础任务     :base, done, 2024-01-01, 5d
        中间任务     :middle, active, after base, 3d
        最终任务     :final, crit, after middle, 2d
    """
    
    parser = MermaidParser()
    project_plan = parser.parse(mermaid_code)
    
    # 验证依赖链
    base_task = project_plan.get_task_by_id("base")
    middle_task = project_plan.get_task_by_id("middle")
    final_task = project_plan.get_task_by_id("final")
    
    assert len(base_task.dependencies) == 0
    assert "base" in middle_task.dependencies
    assert "middle" in final_task.dependencies
    
    print("✅ 依赖关系处理测试通过")


def test_milestone_handling():
    """测试里程碑处理"""
    print("=== 测试里程碑处理 ===")
    
    mermaid_code = """
    gantt
        dateFormat  YYYY-MM-DD
        title       里程碑测试

        section 项目阶段
        需求分析     :req, done, 2024-01-01, 5d
        设计完成     :design_milestone, milestone, after req
        开发阶段     :dev, active, after design_milestone, 10d
        项目完成     :complete_milestone, milestone, after dev
    """
    
    parser = MermaidParser()
    project_plan = parser.parse(mermaid_code)
    
    # 验证解析结果
    assert project_plan.total_tasks == 4
    
    # 验证里程碑
    milestones = [task for task in project_plan.tasks if task.is_milestone]
    assert len(milestones) == 2
    
    for milestone in milestones:
        assert milestone.duration == 0
        assert "milestone" in milestone.status
    
    # 验证依赖关系
    dev_task = project_plan.get_task_by_id("dev")
    assert dev_task is not None
    assert "design_milestone" in dev_task.dependencies
    
    complete_milestone = project_plan.get_task_by_id("complete_milestone")
    assert complete_milestone is not None
    assert "dev" in complete_milestone.dependencies
    
    print("✅ 里程碑处理测试通过")


def test_status_handling():
    """测试状态处理"""
    print("=== 测试状态处理 ===")
    
    mermaid_code = """
    gantt
        dateFormat  YYYY-MM-DD
        title       状态测试

        section 各种状态
        已完成任务    :done_task, done, 2024-01-01, 3d
        进行中任务   :active_task, active, after done_task, 5d
        关键任务     :crit_task, crit, after active_task, 2d
        多状态任务    :multi_task, done, active, crit, after crit_task, 1d
    """
    
    parser = MermaidParser()
    project_plan = parser.parse(mermaid_code)
    
    # 验证状态
    done_task = project_plan.get_task_by_id("done_task")
    active_task = project_plan.get_task_by_id("active_task")
    crit_task = project_plan.get_task_by_id("crit_task")
    multi_task = project_plan.get_task_by_id("multi_task")
    
    assert "done" in done_task.status
    assert "active" in active_task.status
    assert "crit" in crit_task.status
    assert "done" in multi_task.status
    assert "active" in multi_task.status
    assert "crit" in multi_task.status
    
    print("✅ 状态处理测试通过")


def test_validator():
    """测试语法验证器"""
    print("=== 测试语法验证器 ===")
    
    # 测试正确的语法
    valid_code = """
    gantt
        dateFormat  YYYY-MM-DD
        title       有效语法测试
        任务A       :taskA, done, 2024-01-01, 3d
        任务B       :taskB, active, after taskA, 5d
    """
    
    validator = MermaidValidator()
    is_valid, errors, warnings = validator.validate(valid_code)
    
    assert is_valid
    assert len(errors) == 0
    print("✅ 有效语法验证通过")
    
    # 测试无效的依赖
    invalid_code = """
    gantt
        dateFormat  YYYY-MM-DD
        title       无效依赖测试
        任务A       :taskA, done, 2024-01-01, 3d
        任务B       :taskB, active, after nonexistent, 5d
    """
    
    is_valid, errors, warnings = validator.validate(invalid_code)
    
    assert not is_valid
    assert len(errors) > 0
    assert any("nonexistent" in error for error in errors)
    print("✅ 无效依赖检测通过")


def test_integration_with_processor():
    """测试与核心处理引擎的集成"""
    print("=== 测试与核心处理引擎的集成 ===")
    
    mermaid_code = """
    gantt
        dateFormat  YYYY-MM-DD
        title       集成测试项目

        section 开发阶段
        需求分析     :req, done, 2024-01-01, 5d
        系统设计     :design, active, after req, 7d
        前端开发     :frontend, active, after design, 10d
        后端开发     :backend, crit, after design, 12d
        测试阶段     :test, active, after backend, 5d
        项目完成     :complete, milestone, after test
    """
    
    # 解析 Mermaid 代码
    parser = MermaidParser()
    project_plan = parser.parse(mermaid_code)
    
    # 使用核心处理引擎处理
    processor = CoreProcessor(project_plan)
    
    # 验证项目计划
    errors = processor.validate_plan()
    assert len(errors) == 0, f"项目计划验证失败: {errors}"
    
    # 计算日期
    processed_plan = processor.calculate_dates()
    
    # 验证日期计算
    req_task = processed_plan.get_task_by_id("req")
    design_task = processed_plan.get_task_by_id("design")
    
    assert req_task.start_date is not None
    assert req_task.end_date is not None
    assert design_task.start_date is not None
    
    # 验证依赖关系
    assert "req" in design_task.dependencies
    assert design_task.start_date > req_task.end_date
    
    # 获取关键路径
    critical_path = processor.get_critical_path()
    assert len(critical_path) > 0
    
    # 获取统计信息
    stats = processor.get_project_statistics()
    assert stats['total_tasks'] == 6
    assert stats['completed_tasks'] == 1
    assert stats['milestone_count'] == 1
    
    print("✅ 与核心处理引擎集成测试通过")


def test_error_handling():
    """测试错误处理"""
    print("=== 测试错误处理 ===")
    
    # 测试空输入
    parser = MermaidParser()
    empty_plan = parser.parse("")
    assert empty_plan.title == "甘特图"  # 修正默认标题
    assert empty_plan.total_tasks == 0
    
    # 测试无效的日期格式
    invalid_date_code = """
    gantt
        dateFormat  INVALID_FORMAT
        title       无效日期格式测试
        任务A       :taskA, done, 2024-01-01, 3d
    """
    
    parser = MermaidParser()
    plan = parser.parse(invalid_date_code)
    # 应该能够处理，不会崩溃
    assert plan is not None
    
    # 测试无效的任务行
    invalid_task_code = """
    gantt
        dateFormat  YYYY-MM-DD
        title       无效任务行测试
        这是一个无效的任务行
        任务A       :taskA, done, 2024-01-01, 3d
    """
    
    parser = MermaidParser()
    plan = parser.parse(invalid_task_code)
    # 应该跳过无效行，继续解析有效行
    assert plan.total_tasks == 1
    
    print("✅ 错误处理测试通过")


def main():
    """主测试函数"""
    print("TaskWeaver AI Mermaid 解析器测试")
    print("=" * 50)
    
    try:
        test_basic_parsing()
        test_date_formats()
        test_dependency_handling()
        test_milestone_handling()
        test_status_handling()
        test_validator()
        test_integration_with_processor()
        test_error_handling()
        
        print("\n🎉 所有测试通过！Mermaid 解析器工作正常。")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
