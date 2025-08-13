"""
TaskWeaver AI Mermaid 甘特图解析器

重构后的解析器，基于原始实现适配统一数据模型。
"""

import re
from datetime import datetime, date
from typing import List, Dict, Optional

from core.models import Task, ProjectPlan


class MermaidParser:
    """
    Mermaid 甘特图解析器
    
    解析 Mermaid Gantt 语法，生成统一的 Task 和 ProjectPlan 对象。
    基于原始实现重构，保持简单有效。
    """
    
    def __init__(self):
        self.date_format = "%Y-%m-%d"
        self.title = "甘特图"
        self.sections = []
        self.tasks_data = []
        
    def parse(self, mermaid_code: str) -> ProjectPlan:
        """
        解析 Mermaid 甘特图代码
        
        Args:
            mermaid_code: Mermaid Gantt 语法代码
            
        Returns:
            解析后的项目计划对象
        """
        # 重置状态
        self.tasks_data = []
        self.sections = []
        
        lines = mermaid_code.splitlines()
        current_section = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith('%') or line.startswith('%%'):
                continue

            if line.startswith('gantt'):
                pass
            elif line.startswith('dateFormat'):
                match = re.search(r'dateFormat\s+(.*)', line)
                if match:
                    mermaid_format = match.group(1).strip()
                    # 将 Mermaid 日期格式转换为 Python 日期格式
                    self.date_format = self._convert_mermaid_to_python_format(mermaid_format)
            elif line.startswith('title'):
                match = re.search(r'title\s+(.*)', line)
                if match:
                    self.title = match.group(1).strip()
            elif line.startswith('section'):
                match = re.search(r'section\s+(.*)', line)
                if match:
                    current_section = match.group(1).strip()
                    self.sections.append(current_section)
            else:
                # 任务行解析 - 支持中文和更灵活的格式
                task_match = re.match(
                    r'^(.+?)\s*:\s*([a-zA-Z0-9_-]+)'  # 任务名称和ID (支持中文)
                    r'(?:,\s*([a-zA-Z]+(?:,\s*[a-zA-Z]+)*)?)?' # 可选的状态关键词列表
                    r'(?:,\s*([a-zA-Z0-9\s/_-]+))'          # 开始信息 (日期或 'after ID') - 支持下划线
                    r'(?:,\s*([a-zA-Z0-9\s/_-]+))?$'    # 可选的结束信息 (日期或持续天数) - 支持下划线
                    , line
                )
                
                if task_match:
                    name = task_match.group(1).strip()
                    task_id = task_match.group(2).strip()
                    status_str = task_match.group(3)
                    start_info = task_match.group(4).strip()
                    end_info = task_match.group(5)
                    end_info = end_info.strip() if end_info else None

                    # 解析状态关键词
                    status = [s.strip() for s in status_str.split(',') if s.strip()] if status_str else []
                    
                    is_milestone = 'milestone' in status
                    dependency_id = None
                    
                    # 检查开始信息中是否包含依赖关系
                    dep_match = re.match(r'after\s+([a-zA-Z0-9_-]+)', start_info)
                    if dep_match:
                        dependency_id = dep_match.group(1)

                    # 解析日期和持续时间
                    start_date, end_date, duration = self._parse_date_info(
                        start_info, end_info, is_milestone, dependency_id is not None
                    )

                    task_data = {
                        'id': task_id,
                        'name': name,
                        'status': status,
                        'section': current_section,
                        'is_milestone': is_milestone,
                        'start_date': start_date,
                        'end_date': end_date,
                        'duration': duration,
                        'dependencies': [dependency_id] if dependency_id else []
                    }
                    self.tasks_data.append(task_data)
                else:
                    print(f"警告：无法解析任务行: '{line}'")
        
        # 转换为统一的数据模型
        return self._convert_to_project_plan()
    
    def _parse_date_info(self, start_info: str, end_info: str, 
                        is_milestone: bool, has_dependency: bool) -> tuple:
        """
        解析日期信息
        
        Returns:
            (start_date, end_date, duration)
        """
        start_date = None
        end_date = None
        duration = None
        
        # 如果是里程碑，持续时间为0
        if is_milestone:
            duration = 0
        
        # 解析开始日期（如果不是依赖关系）
        if not has_dependency:
            start_date = self._parse_date(start_info)
        
        # 解析结束信息
        if end_info:
            if end_info.endswith('d'):
                # 持续天数
                try:
                    duration = int(end_info[:-1])
                except ValueError:
                    duration = None
            else:
                # 结束日期
                end_date = self._parse_date(end_info)
                # 如果有开始日期，计算持续天数
                if start_date and end_date:
                    duration = (end_date - start_date).days + 1
        
        # 如果没有明确的结束信息但有开始日期，默认持续1天
        if start_date and end_info is None and duration is None:
            duration = 1
        
        # 如果是里程碑且有开始日期，结束日期与开始日期相同
        if is_milestone and start_date and not end_date:
            end_date = start_date
        
        return start_date, end_date, duration
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        try:
            # 尝试按照配置的日期格式解析
            dt = datetime.strptime(date_str, self.date_format)
            return dt.date()
        except ValueError:
            try:
                # 尝试常见格式
                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y']:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.date()
                    except ValueError:
                        continue
            except Exception:
                pass
        
        print(f"警告：无法解析日期: '{date_str}'")
        return None
    
    def _convert_mermaid_to_python_format(self, mermaid_format: str) -> str:
        """
        将 Mermaid 日期格式转换为 Python 日期格式
        
        Mermaid 格式:
        - YYYY-MM-DD -> %Y-%m-%d
        - YYYY/MM/DD -> %Y/%m/%d
        - DD-MM-YYYY -> %d-%m-%Y
        - MM-DD-YYYY -> %m-%d-%Y
        
        Args:
            mermaid_format: Mermaid 日期格式字符串
            
        Returns:
            Python 日期格式字符串
        """
        format_mapping = {
            'YYYY-MM-DD': '%Y-%m-%d',
            'YYYY/MM/DD': '%Y/%m/%d',
            'DD-MM-YYYY': '%d-%m-%Y',
            'MM-DD-YYYY': '%m-%d-%Y',
            'YYYY-MM': '%Y-%m',
            'YYYY/MM': '%Y/%m',
            'MM-YYYY': '%m-%Y',
            'MM/YYYY': '%m/%Y',
        }
        
        return format_mapping.get(mermaid_format, '%Y-%m-%d')
    
    def _convert_to_project_plan(self) -> ProjectPlan:
        """转换为统一的项目计划对象"""
        tasks = []
        
        # 创建任务对象
        for task_data in self.tasks_data:
            task = Task(
                id=task_data['id'],
                name=task_data['name'],
                status=task_data['status'],
                section=task_data['section'],
                is_milestone=task_data['is_milestone'],
                start_date=task_data['start_date'],
                end_date=task_data['end_date'],
                duration=task_data['duration'],
                dependencies=task_data['dependencies']
            )
            tasks.append(task)
        
        # 创建项目计划
        project_plan = ProjectPlan(
            title=self.title,
            tasks=tasks,
            date_format=self.date_format,
            created_date=date.today(),
            version="1.0"
        )
        
        return project_plan
    
    def get_parsed_data(self) -> Dict:
        """
        获取解析后的原始数据（用于调试和兼容性）
        
        Returns:
            包含解析结果的字典
        """
        return {
            'date_format': self.date_format,
            'title': self.title,
            'sections': self.sections,
            'tasks': self.tasks_data
        }


class MermaidValidator:
    """
    Mermaid 语法验证器
    
    验证 Mermaid Gantt 代码的语法正确性和数据一致性。
    """
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, mermaid_code: str) -> tuple:
        """
        验证 Mermaid 代码
        
        Args:
            mermaid_code: 要验证的 Mermaid 代码
            
        Returns:
            (是否有效, 错误列表, 警告列表)
        """
        self.errors = []
        self.warnings = []
        
        lines = mermaid_code.splitlines()
        task_ids = set()
        dependencies = set()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line or line.startswith('%') or line.startswith('%%'):
                continue
            
            # 验证基本语法
            if line.startswith('gantt'):
                continue
            elif line.startswith('dateFormat'):
                self._validate_date_format(line, line_num)
            elif line.startswith('title'):
                continue  # 标题不需要特殊验证
            elif line.startswith('section'):
                continue  # 章节不需要特殊验证
            else:
                # 验证任务行
                task_id, deps = self._validate_task_line(line, line_num)
                if task_id:
                    task_ids.add(task_id)
                    dependencies.update(deps)
        
        # 验证依赖关系的有效性
        self._validate_dependencies(task_ids, dependencies)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_date_format(self, line: str, line_num: int):
        """验证日期格式"""
        match = re.search(r'dateFormat\s+(.+)', line)
        if not match:
            self.errors.append(f"第{line_num}行：日期格式语法错误")
            return
        
        date_format = match.group(1).strip()
        # 简单验证日期格式是否包含基本的日期占位符
        if not any(fmt in date_format for fmt in ['YYYY', 'YY', 'MM', 'DD']):
            self.warnings.append(f"第{line_num}行：日期格式可能不正确")
    
    def _validate_task_line(self, line: str, line_num: int) -> tuple:
        """验证任务行语法"""
        # 使用与解析器相同的正则表达式
        task_match = re.match(
            r'^(.+?)\s*:\s*([a-zA-Z0-9_-]+)'  # 任务名称和ID (支持中文)
            r'(?:,\s*([a-zA-Z]+(?:,\s*[a-zA-Z]+)*)?)?' # 可选的状态关键词列表
            r'(?:,\s*([a-zA-Z0-9\s/_-]+))'          # 开始信息 (日期或 'after ID') - 支持下划线
            r'(?:,\s*([a-zA-Z0-9\s/_-]+))?$'    # 可选的结束信息 (日期或持续天数) - 支持下划线
            , line
        )
        
        if not task_match:
            self.errors.append(f"第{line_num}行：任务语法错误: '{line}'")
            return None, set()
        
        task_id = task_match.group(2).strip()
        start_info = task_match.group(4).strip()
        
        # 检查依赖关系
        dependencies = set()
        dep_match = re.match(r'after\s+([a-zA-Z0-9_-]+)', start_info)
        if dep_match:
            dep_id = dep_match.group(1)
            dependencies.add(dep_id)
        
        return task_id, dependencies
    
    def _validate_dependencies(self, task_ids: set, dependencies: set):
        """验证依赖关系的有效性"""
        # 检查是否有依赖的任务不存在
        missing_deps = dependencies - task_ids
        if missing_deps:
            for dep in missing_deps:
                self.errors.append(f"依赖的任务 '{dep}' 不存在")


# 使用示例和测试函数
def create_sample_mermaid_code() -> str:
    """创建示例 Mermaid 代码"""
    return """
    gantt
        dateFormat  YYYY-MM-DD
        title       TaskWeaver AI 项目计划

        section 项目启动
        需求分析    :req1, done, 2024-01-01, 5d
        环境搭建    :env1, done, after req1, 3d
        里程碑A     :milestone1, milestone, after env1

        section 开发阶段
        系统设计    :design1, active, after milestone1, 7d
        前端开发    :frontend1, active, after design1, 10d
        后端开发    :backend1, crit, after design1, 12d
        集成测试    :test1, active, after frontend1, 5d

        section 测试阶段
        系统测试    :systest1, after test1, 7d
        用户验收测试:uat1, after systest1, 5d
        里程碑B     :milestone2, milestone, after uat1

        section 发布阶段
        部署准备    :deploy1, after milestone2, 3d
        正式发布    :release1, after deploy1, 2d
        项目结束里程碑:end, milestone, after release1
    """


def test_mermaid_parser():
    """测试 Mermaid 解析器"""
    print("=== 测试 Mermaid 解析器 ===")
    
    # 创建示例代码
    mermaid_code = create_sample_mermaid_code()
    
    # 解析代码
    parser = MermaidParser()
    project_plan = parser.parse(mermaid_code)
    
    # 显示解析结果
    print(f"项目标题: {project_plan.title}")
    print(f"任务总数: {project_plan.total_tasks}")
    print(f"项目分组: {project_plan.get_sections()}")
    
    print("\n任务详情:")
    for task in project_plan.tasks:
        deps = ", ".join(task.dependencies) if task.dependencies else "无"
        status = ", ".join(task.status) if task.status else "无"
        print(f"  {task.name} ({task.id})")
        print(f"    状态: {status}")
        print(f"    分组: {task.section}")
        print(f"    开始: {task.start_date}")
        print(f"    结束: {task.end_date}")
        print(f"    持续: {task.duration}天")
        print(f"    依赖: {deps}")
        print(f"    里程碑: {'是' if task.is_milestone else '否'}")
        print()
    
    # 验证语法
    validator = MermaidValidator()
    is_valid, errors, warnings = validator.validate(mermaid_code)
    
    print("=== 语法验证结果 ===")
    print(f"语法正确: {'是' if is_valid else '否'}")
    
    if errors:
        print("错误:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("警告:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if is_valid and not errors and not warnings:
        print("✅ 语法验证通过")
    
    return project_plan


if __name__ == "__main__":
    test_mermaid_parser()
