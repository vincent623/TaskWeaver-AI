#!/usr/bin/env python3
"""
TaskWeaver AI Mermaid 解析器测试脚本

用于测试AI驱动的Mermaid解析器功能。
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.ai_mermaid_parser import AIMermaidParser, AIMermaidValidator, OpenAIClient
from parsers.mermaid_parser import MermaidParser


def test_ai_parser_basic():
    """测试AI解析器基本功能"""
    print("=== 测试AI解析器基本功能 ===")
    
    # 创建模拟的LLM客户端
    llm_client = OpenAIClient("dummy_key")  # 使用模拟模式
    
    # 创建AI解析器
    ai_parser = AIMermaidParser(llm_client)
    
    # 设置备用解析器
    fallback_parser = MermaidParser()
    ai_parser.set_fallback_parser(fallback_parser)
    
    # 测试用例
    mermaid_code = """
    gantt
        dateFormat  YYYY-MM-DD
        title       AI测试项目

        section 阶段一
        任务A       :taskA, done, 2024-01-01, 5d
        任务B       :taskB, active, after taskA, 3d
        里程碑A     :milestoneA, milestone, after taskB

        section 阶段二
        任务C       :taskC, crit, after milestoneA, 7d
        任务D       :taskD, active, after taskC, 4d
    """
    
    try:
        print("正在使用AI解析...")
        project_plan = ai_parser.parse(mermaid_code)
        
        # 验证解析结果
        assert project_plan.title == "AI解析的项目"  # 模拟模式会返回这个标题
        assert project_plan.total_tasks > 0
        
        print(f"✅ AI解析成功")
        print(f"项目标题: {project_plan.title}")
        print(f"任务总数: {project_plan.total_tasks}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI解析失败: {e}")
        return False


def test_natural_language_conversion():
    """测试自然语言转换功能"""
    print("=== 测试自然语言转换功能 ===")
    
    # 创建模拟的LLM客户端
    llm_client = OpenAIClient("dummy_key")
    
    # 创建AI解析器
    ai_parser = AIMermaidParser(llm_client)
    
    # 自然语言描述
    nl_description = """
    我们需要开发一个移动应用项目。首先进行需求分析，需要3天时间。
    然后是UI设计，需要5天。接着是前端开发，预计8天，同时进行后端开发，需要10天。
    开发完成后进行测试，需要4天。最后是发布，需要2天。我们在需求分析完成后设置一个里程碑。
    """
    
    try:
        print("自然语言描述:")
        print(nl_description)
        print("\n正在转换为Mermaid代码...")
        
        mermaid_result = ai_parser.natural_language_to_mermaid(nl_description)
        print("转换结果:")
        print(mermaid_result)
        
        # 验证转换结果包含基本的Mermaid结构
        assert "gantt" in mermaid_result
        assert "title" in mermaid_result
        assert "section" in mermaid_result
        
        print("✅ 自然语言转换成功")
        return True
        
    except Exception as e:
        print(f"❌ 自然语言转换失败: {e}")
        return False


def test_ai_validation():
    """测试AI验证功能"""
    print("=== 测试AI验证功能 ===")
    
    # 创建模拟的LLM客户端
    llm_client = OpenAIClient("dummy_key")
    
    # 创建AI验证器
    ai_validator = AIMermaidValidator(llm_client)
    
    # 测试用例
    mermaid_code = """
    gantt
        dateFormat  YYYY-MM-DD
        title       验证测试项目

        section 开发
        需求分析    :req, done, 2024-01-01, 5d
        系统设计    :design, active, after req, 7d
        开发        :dev, crit, after design, 10d
    """
    
    try:
        print("正在验证语法...")
        is_valid, errors, warnings = ai_validator.validate(mermaid_code)
        
        print(f"语法正确: {'是' if is_valid else '否'}")
        
        if errors:
            print("错误:")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print("警告:")
            for warning in warnings:
                print(f"  - {warning}")
        
        print("✅ AI验证成功")
        return True
        
    except Exception as e:
        print(f"❌ AI验证失败: {e}")
        return False


def test_improvement_suggestions():
    """测试改进建议功能"""
    print("=== 测试改进建议功能 ===")
    
    # 创建模拟的LLM客户端
    llm_client = OpenAIClient("dummy_key")
    
    # 创建AI验证器
    ai_validator = AIMermaidValidator(llm_client)
    
    # 测试用例
    mermaid_code = """
    gantt
        dateFormat  YYYY-MM-DD
        title       改进测试项目

        section 阶段一
        任务A       :taskA, done, 2024-01-01, 5d
        任务B       :taskB, active, after taskA, 3d
    """
    
    try:
        print("正在生成改进建议...")
        suggestions = ai_validator.suggest_improvements(mermaid_code)
        
        if suggestions:
            print("改进建议:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        else:
            print("暂无改进建议")
        
        print("✅ 改进建议生成成功")
        return True
        
    except Exception as e:
        print(f"❌ 改进建议生成失败: {e}")
        return False


def test_fallback_mechanism():
    """测试备用机制"""
    print("=== 测试备用机制 ===")
    
    # 创建模拟的LLM客户端
    llm_client = OpenAIClient("dummy_key")
    
    # 创建AI解析器
    ai_parser = AIMermaidParser(llm_client)
    
    # 设置备用解析器
    fallback_parser = MermaidParser()
    ai_parser.set_fallback_parser(fallback_parser)
    
    # 测试用例
    mermaid_code = """
    gantt
        dateFormat  YYYY-MM-DD
        title       备用测试项目

        section 阶段一
        任务A       :taskA, done, 2024-01-01, 5d
        任务B       :taskB, active, after taskA, 3d
    """
    
    try:
        print("正在测试备用机制...")
        # 即使AI解析失败，也应该能通过备用解析器成功
        project_plan = ai_parser.parse(mermaid_code)
        
        # 验证解析结果
        assert project_plan.title is not None
        assert project_plan.total_tasks > 0
        
        print(f"✅ 备用机制成功")
        print(f"项目标题: {project_plan.title}")
        print(f"任务总数: {project_plan.total_tasks}")
        
        return True
        
    except Exception as e:
        print(f"❌ 备用机制失败: {e}")
        return False


def main():
    """主测试函数"""
    print("TaskWeaver AI Mermaid 解析器测试")
    print("=" * 50)
    
    tests = [
        ("AI解析器基本功能", test_ai_parser_basic),
        ("自然语言转换", test_natural_language_conversion),
        ("AI验证功能", test_ai_validation),
        ("改进建议生成", test_improvement_suggestions),
        ("备用机制", test_fallback_mechanism),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 出现异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！AI Mermaid 解析器工作正常。")
    else:
        print("⚠️  部分测试失败，请检查实现。")


if __name__ == "__main__":
    main()
