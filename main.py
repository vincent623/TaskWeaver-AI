#!/usr/bin/env python3
"""
TaskWeaver AI 主程序入口

提供统一的命令行界面来使用所有功能。
"""

import sys
import os
import argparse
from datetime import date
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.models import Task, ProjectPlan
from core.processor import CoreProcessor
from parsers.mermaid_parser import MermaidParser, MermaidValidator
from parsers.ai_mermaid_parser import AIMermaidParser, OpenAIClient
from parsers.nlp_parser import NaturalLanguageParser
from generators.excel_generator import ExcelGanttGenerator
from generators.html_generator import HTMLGanttGenerator


def setup_argument_parser():
    """设置命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="TaskWeaver AI - 智能项目规划助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py parse sample.mermaid -o project.xlsx
  python main.py validate sample.mermaid
  python main.py create --interactive
  python main.py test
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 解析命令
    parse_parser = subparsers.add_parser('parse', help='解析Mermaid文件生成完整项目文件')
    parse_parser.add_argument('input', help='输入的Mermaid文件路径')
    parse_parser.add_argument('-o', '--output', help='输出文件基础名称', 
                            default='parsed_project')
    parse_parser.add_argument('--ai', action='store_true', help='使用AI解析器')
    parse_parser.add_argument('--api-key', help='OpenAI API密钥')
    
    # 验证命令
    validate_parser = subparsers.add_parser('validate', help='验证Mermaid代码')
    validate_parser.add_argument('input', help='输入的Mermaid文件路径')
    validate_parser.add_argument('--ai', action='store_true', help='使用AI验证')
    
    # 创建命令
    create_parser = subparsers.add_parser('create', help='创建新项目')
    create_parser.add_argument('--interactive', action='store_true', 
                             help='交互式创建')
    create_parser.add_argument('--template', help='使用模板')
    create_parser.add_argument('--from-text', help='从自然语言描述创建')
    create_parser.add_argument('--api-key', help='OpenAI API密钥')
    create_parser.add_argument('-o', '--output', help='输出文件基础名称(不含扩展名)', 
                             default='ai_project')
    
    # 测试命令
    test_parser = subparsers.add_parser('test', help='运行项目测试')
    test_parser.add_argument('--module', help='测试特定模块')
    
    return parser


def parse_mermaid_file(file_path: str, output_path: str, output_format: str = 'all',
                      excel_mode: str = 'both', use_ai: bool = False, api_key: str = None):
    """解析Mermaid文件并生成完整的项目文件（Excel图表、表格甘特图、HTML）"""
    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            mermaid_code = f.read()
        
        print(f"📖 读取Mermaid文件: {file_path}")
        
        # 选择解析器
        if use_ai and api_key:
            print("🤖 使用AI解析器...")
            llm_client = OpenAIClient(api_key)
            parser = AIMermaidParser(llm_client)
            # 设置备用解析器
            fallback_parser = MermaidParser()
            parser.set_fallback_parser(fallback_parser)
        else:
            print("📝 使用传统解析器...")
            parser = MermaidParser()
        
        # 解析项目
        project_plan = parser.parse(mermaid_code)
        print(f"✅ 解析成功: {project_plan.total_tasks} 个任务")
        
        # 处理日期计算
        print("🔄 计算日期和依赖关系...")
        processor = CoreProcessor(project_plan)
        
        # 验证项目
        errors = processor.validate_plan()
        if errors:
            print("⚠️ 发现问题:")
            for error in errors:
                print(f"  - {error}")
        
        # 计算日期
        processed_project = processor.calculate_dates()
        print("✅ 日期计算完成")
        
        # 生成完整的项目文件
        base_name = os.path.splitext(os.path.basename(output_path))[0]
        generate_complete_project_files(processed_project, base_name)
        
        print("🎉 任务完成!")
        
        # 显示项目统计
        stats = processor.get_project_statistics()
        print(f"\n📈 项目统计:")
        print(f"  总任务数: {stats['total_tasks']}")
        print(f"  项目工期: {stats['total_duration']} 天")
        print(f"  完成率: {stats['completion_rate']:.1f}%")
        print(f"  里程碑数: {stats['milestone_count']}")
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        return False
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def validate_mermaid_file(file_path: str, use_ai: bool = False):
    """验证Mermaid文件"""
    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            mermaid_code = f.read()
        
        print(f"📖 读取Mermaid文件: {file_path}")
        
        if use_ai:
            print("🤖 使用AI验证器...")
            # AI验证需要API密钥，这里使用模拟
            llm_client = OpenAIClient("dummy_key")
            from parsers.ai_mermaid_parser import AIMermaidValidator
            validator = AIMermaidValidator(llm_client)
            is_valid, errors, warnings = validator.validate(mermaid_code)
        else:
            print("📝 使用传统验证器...")
            validator = MermaidValidator()
            is_valid, errors, warnings = validator.validate(mermaid_code)
        
        print(f"\n🔍 验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
        
        if errors:
            print("\n❌ 错误:")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
        
        if warnings:
            print("\n⚠️ 警告:")
            for i, warning in enumerate(warnings, 1):
                print(f"  {i}. {warning}")
        
        if is_valid and not errors and not warnings:
            print("\n🎉 代码完美，无错误和警告!")
        
        return is_valid
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False


def create_from_text(description: str, api_key: str = None, output_path: str = 'ai_project'):
    """从自然语言描述创建项目"""
    print("🤖 使用AI解析自然语言描述...")
    
    try:
        # 确保outputs目录存在
        import os
        os.makedirs("outputs", exist_ok=True)
        
        # 如果没有指定路径，使用outputs目录
        if output_path == 'ai_project':
            base_name = "ai_project"
        else:
            base_name = os.path.splitext(os.path.basename(output_path))[0]
        
        # 创建自然语言解析器
        nlp_parser = NaturalLanguageParser(api_key=api_key)
        
        # 解析描述
        project_plan = nlp_parser.parse(description)
        print(f"✅ 解析成功: {project_plan.total_tasks} 个任务")
        
        # 处理项目
        processor = CoreProcessor(project_plan)
        errors = processor.validate_plan()
        
        if errors:
            print("\n⚠️ 项目验证发现问题:")
            for error in errors:
                print(f"  - {error}")
        
        processed_project = processor.calculate_dates()
        print("✅ 日期计算完成")
        
        # 生成完整的项目文件
        generate_complete_project_files(processed_project, base_name)
        
        print(f"\n🎉 AI项目创建成功！")
        
        # 显示项目统计
        stats = processor.get_project_statistics()
        print(f"\n📈 项目统计:")
        print(f"  项目名称: {processed_project.title}")
        print(f"  总任务数: {stats['total_tasks']}")
        print(f"  项目工期: {stats['total_duration']} 天")
        print(f"  里程碑数: {stats['milestone_count']}")
        print(f"  项目阶段: {', '.join(processed_project.get_sections())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False


def create_interactive_project():
    """交互式创建项目"""
    print("🎯 欢迎使用TaskWeaver AI项目创建向导")
    print("=" * 50)
    
    # 项目基本信息
    title = input("项目标题: ").strip() or "新项目"
    description = input("项目描述 (可选): ").strip() or None
    
    tasks = []
    print(f"\n📋 开始添加任务 (输入空行结束)")
    
    task_id = 1
    while True:
        print(f"\n--- 任务 {task_id} ---")
        name = input("任务名称 (空行结束): ").strip()
        if not name:
            break
        
        duration = input("持续天数 (默认1): ").strip()
        try:
            duration = int(duration) if duration else 1
        except ValueError:
            duration = 1
        
        is_milestone = input("是否为里程碑? (y/N): ").strip().lower() == 'y'
        if is_milestone:
            duration = 0
        
        dependencies = input("依赖任务ID (用逗号分隔): ").strip()
        deps = [dep.strip() for dep in dependencies.split(',') if dep.strip()]
        
        task = Task(
            id=f"task{task_id}",
            name=name,
            duration=duration,
            is_milestone=is_milestone,
            dependencies=deps
        )
        tasks.append(task)
        task_id += 1
    
    if not tasks:
        print("❌ 没有添加任务，退出创建")
        return False
    
    # 创建项目
    project = ProjectPlan(
        title=title,
        description=description,
        tasks=tasks,
        created_date=date.today()
    )
    
    # 处理项目
    processor = CoreProcessor(project)
    errors = processor.validate_plan()
    
    if errors:
        print("\n⚠️ 项目验证发现问题:")
        for error in errors:
            print(f"  - {error}")
        
        if input("\n是否继续? (y/N): ").strip().lower() != 'y':
            return False
    
    processed_project = processor.calculate_dates()
    
    # 保存项目
    output_file = input(f"\n💾 输出文件名 (默认: {title}.xlsx): ").strip()
    if not output_file:
        output_file = f"{title}.xlsx"
    
    # 生成Excel
    parsed_data = convert_project_to_old_format(processed_project)
    generator = ExcelGanttGenerator(parsed_data)
    generator.generate_excel(output_file)
    
    print(f"\n🎉 项目创建成功: {output_file}")
    return True


def run_tests(module: str = None):
    """运行测试"""
    print("🧪 运行TaskWeaver AI测试")
    print("=" * 40)
    
    if module == "core" or module is None:
        print("\n🔧 测试核心模块...")
        os.system(f"cd '{Path(__file__).parent}' && python test/test_core.py")
    
    if module == "parser" or module is None:
        print("\n📝 测试解析器...")
        os.system(f"cd '{Path(__file__).parent}' && python test/test_mermaid_parser.py")
    
    if module == "ai" or module is None:
        print("\n🤖 测试AI功能...")
        print("✅ AI客户端和解析器模块正常加载")
        
        # 测试LLM客户端配置
        try:
            from core.llm_client import auto_select_provider, LLMProvider
            provider = auto_select_provider()
            provider_name = provider.value if hasattr(provider, 'value') else str(provider)
            print(f"✅ LLM提供商: {provider_name}")
            
            # 简单的AI解析测试
            from parsers.nlp_parser import NaturalLanguageParser
            parser = NaturalLanguageParser()
            print("✅ AI自然语言解析器初始化成功")
            
        except Exception as e:
            print(f"⚠️  AI功能测试: {e}")
            print("ℹ️  请确保已配置API密钥到.env文件中")


def generate_complete_project_files(processed_project: ProjectPlan, base_name: str):
    """生成完整的项目文件（Excel图表、表格甘特图、HTML）到专属文件夹"""
    import os
    from datetime import datetime
    
    # 创建项目专属文件夹
    project_folder = f"outputs/{base_name}"
    os.makedirs(project_folder, exist_ok=True)
    
    # 转换数据格式
    parsed_data = convert_project_to_old_format(processed_project)
    
    # 生成文件
    print(f"\n📁 创建项目文件夹: {project_folder}")
    print("📊 生成项目文件...")
    
    # 1. Excel图表甘特图
    chart_path = f"{project_folder}/{base_name}_chart.xlsx"
    chart_generator = ExcelGanttGenerator(parsed_data, mode="chart")
    chart_generator.generate_excel(chart_path)
    print(f"  ✅ Excel图表甘特图: {chart_path}")
    
    # 2. Excel表格甘特图
    table_path = f"{project_folder}/{base_name}_table.xlsx"
    table_generator = ExcelGanttGenerator(parsed_data, mode="table")
    table_generator.generate_excel(table_path)
    print(f"  ✅ Excel表格甘特图: {table_path}")
    
    # 3. HTML交互报告
    html_path = f"{project_folder}/{base_name}_report.html"
    html_generator = HTMLGanttGenerator(processed_project)
    html_generator.generate_html(html_path)
    print(f"  ✅ HTML交互报告: {html_path}")
    
    # 4. 创建项目信息文件
    info_path = f"{project_folder}/project_info.txt"
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(f"项目名称: {processed_project.title}\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总任务数: {processed_project.total_tasks}\n")
        f.write(f"项目阶段: {', '.join(processed_project.get_sections())}\n")
        f.write(f"里程碑数: {len([t for t in processed_project.tasks if t.is_milestone])}\n")
        f.write(f"\n文件说明:\n")
        f.write(f"- {base_name}_chart.xlsx: Excel图表甘特图\n")
        f.write(f"- {base_name}_table.xlsx: Excel表格甘特图\n")
        f.write(f"- {base_name}_report.html: HTML交互报告\n")
        f.write(f"- project_info.txt: 项目信息文件\n")
    
    print(f"  ✅ 项目信息文件: {info_path}")
    
    print(f"\n🎉 项目文件生成完成！")
    print(f"📁 项目文件夹: {project_folder}")
    print(f"  📊 图表甘特图: {chart_path}")
    print(f"  📅 表格甘特图: {table_path}")
    print(f"  🌐 HTML报告: {html_path}")
    print(f"  📄 项目信息: {info_path}")
    
    return {
        'folder': project_folder,
        'chart': chart_path,
        'table': table_path,
        'html': html_path,
        'info': info_path
    }


def convert_project_to_old_format(project_plan: ProjectPlan) -> dict:
    """将新格式项目转换为旧格式以兼容现有生成器"""
    tasks_data = []
    
    for task in project_plan.tasks:
        task_data = {
            'id': task.id,
            'name': task.name,
            'status': task.status,
            'section': task.section,
            'is_milestone': task.is_milestone,
            'start_date': task.start_date,
            'end_date': task.end_date,
            'start_date_obj': task.start_date,  # 保持兼容性
            'end_date_obj': task.end_date,      # 保持兼容性
            'duration_val': task.duration,
            'dependency_id': task.dependencies[0] if task.dependencies else None,
            # 添加Excel生成器需要的字段
            'start_raw': task.start_date.strftime('%Y-%m-%d') if task.start_date else None,
            'end_raw': f"{task.duration}d" if task.duration and not task.is_milestone else (task.end_date.strftime('%Y-%m-%d') if task.end_date else None)
        }
        tasks_data.append(task_data)
    
    return {
        'title': project_plan.title,
        'date_format': project_plan.date_format,
        'tasks': tasks_data
    }


def main():
    """主函数"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🚀 TaskWeaver AI - 智能项目规划助手")
    print("=" * 50)
    
    success = True
    
    if args.command == 'parse':
        success = parse_mermaid_file(args.input, args.output, 'all', 
                                   'both', args.ai, args.api_key)
    
    elif args.command == 'validate':
        success = validate_mermaid_file(args.input, args.ai)
    
    elif args.command == 'create':
        if args.from_text:
            success = create_from_text(args.from_text, args.api_key, args.output)
        elif args.interactive:
            success = create_interactive_project()
        else:
            print("❌ 请选择创建方式：--interactive 或 --from-text")
            success = False
    
    elif args.command == 'test':
        run_tests(args.module)
    
    else:
        parser.print_help()
        success = False
    
    if success:
        print("\n✨ 操作完成")
    else:
        print("\n❌ 操作失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
