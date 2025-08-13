"""
TaskWeaver AI 核心处理引擎

负责处理任务依赖关系、计算日期、验证数据完整性等核心逻辑。
"""

from typing import List, Dict, Set, Optional
from datetime import date, timedelta
from collections import deque

from .models import Task, ProjectPlan


class CoreProcessor:
    """
    核心处理引擎
    
    这是整个系统的核心，负责：
    1. 任务依赖关系的拓扑排序
    2. 日期计算和验证
    3. 工作日计算
    4. 数据完整性检查
    """
    
    def __init__(self, project_plan: ProjectPlan):
        """
        初始化处理引擎
        
        Args:
            project_plan: 项目计划对象
        """
        self.project_plan = project_plan
        self.task_map: Dict[str, Task] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.reverse_dependency_graph: Dict[str, Set[str]] = {}
        self.in_degree: Dict[str, int] = {}
        
        # 构建数据结构
        self._build_data_structures()
    
    def _build_data_structures(self):
        """构建内部数据结构"""
        # 创建任务映射
        for task in self.project_plan.tasks:
            self.task_map[task.id] = task
        
        # 构建依赖图
        for task in self.project_plan.tasks:
            self.dependency_graph[task.id] = set(task.dependencies)
            self.reverse_dependency_graph[task.id] = set()
            self.in_degree[task.id] = len(task.dependencies)
        
        # 构建反向依赖图
        for task_id, dependencies in self.dependency_graph.items():
            for dep_id in dependencies:
                self.reverse_dependency_graph[dep_id].add(task_id)
    
    def calculate_dates(self) -> ProjectPlan:
        """
        计算所有任务的日期
        
        使用拓扑排序算法处理依赖关系，确保任务按正确顺序计算日期。
        
        Returns:
            处理后的项目计划对象
        """
        # 找到所有没有依赖的任务（入度为0）
        queue = deque([
            task_id for task_id, degree in self.in_degree.items() 
            if degree == 0
        ])
        
        # 按拓扑顺序处理任务
        processed_tasks = set()
        
        while queue:
            task_id = queue.popleft()
            if task_id in processed_tasks:
                continue
                
            task = self.task_map[task_id]
            processed_tasks.add(task_id)
            
            # 计算当前任务的日期
            self._calculate_task_dates(task)
            
            # 更新后续任务的入度
            for dependent_id in self.reverse_dependency_graph[task_id]:
                self.in_degree[dependent_id] -= 1
                if self.in_degree[dependent_id] == 0:
                    queue.append(dependent_id)
        
        # 检查是否有循环依赖
        if len(processed_tasks) != len(self.project_plan.tasks):
            unprocessed = set(self.task_map.keys()) - processed_tasks
            raise ValueError(f"发现循环依赖，涉及任务: {unprocessed}")
        
        # 计算项目的开始和结束日期
        self._calculate_project_dates()
        
        return self.project_plan
    
    def _calculate_task_dates(self, task: Task):
        """
        计算单个任务的日期
        
        Args:
            task: 要计算日期的任务
        """
        # 如果是里程碑，确保持续时间为0
        if task.is_milestone:
            task.duration = 0
        
        # 如果有依赖，计算最早开始日期
        if task.dependencies:
            latest_end_date = None
            for dep_id in task.dependencies:
                dep_task = self.task_map[dep_id]
                if dep_task.end_date:
                    if latest_end_date is None or dep_task.end_date > latest_end_date:
                        latest_end_date = dep_task.end_date
            
            if latest_end_date:
                task.start_date = self._add_working_days(latest_end_date, 1)
        
        # 根据已知信息计算缺失的日期
        if task.start_date and task.duration is not None:
            # 计算结束日期
            task.end_date = self._add_working_days(task.start_date, task.duration - 1)
        elif task.start_date and task.end_date:
            # 计算持续时间
            task.duration = self._count_working_days(task.start_date, task.end_date) + 1
        elif task.end_date and task.duration is not None:
            # 计算开始日期
            task.start_date = self._subtract_working_days(task.end_date, task.duration - 1)
        
        # 如果任务没有明确的开始日期，设置为项目开始日期
        if task.start_date is None:
            task.start_date = self.project_plan.start_date or date.today()
            
            # 重新计算其他日期
            if task.duration is not None:
                task.end_date = self._add_working_days(task.start_date, task.duration - 1)
    
    def _calculate_project_dates(self):
        """计算项目的开始和结束日期"""
        if not self.project_plan.tasks:
            return
        
        # 找到最早的任务开始日期
        start_dates = [
            task.start_date for task in self.project_plan.tasks 
            if task.start_date is not None
        ]
        
        # 找到最晚的任务结束日期
        end_dates = [
            task.end_date for task in self.project_plan.tasks 
            if task.end_date is not None
        ]
        
        if start_dates:
            self.project_plan.start_date = min(start_dates)
        
        if end_dates:
            self.project_plan.end_date = max(end_dates)
    
    def _add_working_days(self, start_date: date, days: int) -> date:
        """
        添加工作日
        
        Args:
            start_date: 开始日期
            days: 要添加的工作日数
            
        Returns:
            计算后的日期
        """
        current_date = start_date
        remaining_days = days
        
        while remaining_days > 0:
            current_date += timedelta(days=1)
            if current_date.weekday() in self.project_plan.working_days:
                remaining_days -= 1
        
        return current_date
    
    def _subtract_working_days(self, end_date: date, days: int) -> date:
        """
        减去工作日
        
        Args:
            end_date: 结束日期
            days: 要减去的工作日数
            
        Returns:
            计算后的日期
        """
        current_date = end_date
        remaining_days = days
        
        while remaining_days > 0:
            current_date -= timedelta(days=1)
            if current_date.weekday() in self.project_plan.working_days:
                remaining_days -= 1
        
        return current_date
    
    def _count_working_days(self, start_date: date, end_date: date) -> int:
        """
        计算两个日期之间的工作日数
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            工作日数
        """
        if start_date > end_date:
            return 0
        
        current_date = start_date
        working_days = 0
        
        while current_date <= end_date:
            if current_date.weekday() in self.project_plan.working_days:
                working_days += 1
            current_date += timedelta(days=1)
        
        return working_days
    
    def validate_plan(self) -> List[str]:
        """
        验证项目计划的完整性
        
        Returns:
            验证错误列表，如果为空则表示验证通过
        """
        errors = []
        
        # 检查是否有任务
        if not self.project_plan.tasks:
            errors.append("项目计划中没有任务")
            return errors
        
        # 检查任务信息的完整性 - 只检查必要信息
        for task in self.project_plan.tasks:
            # 至少需要有开始日期或持续时间其中一个
            if (task.start_date is None and task.duration is None and 
                not task.dependencies):
                errors.append(f"任务 '{task.name}' ({task.id}) 缺少基本时间信息")
            
            # 检查日期逻辑（如果两个日期都存在）
            if (task.start_date and task.end_date and 
                task.start_date > task.end_date):
                errors.append(f"任务 '{task.name}' ({task.id}) 的开始日期晚于结束日期")
        
        # 检查循环依赖 - 使用临时对象避免修改原数据
        try:
            temp_processor = CoreProcessor(self.project_plan)
            temp_processor.calculate_dates()
        except ValueError as e:
            if "循环依赖" in str(e):
                errors.append(str(e))
        except Exception:
            # 其他错误不算验证失败，可能是数据不完整但可以修复
            pass
        
        return errors
    
    def get_critical_path(self) -> List[Task]:
        """
        获取关键路径
        
        关键路径是项目中决定总工期的任务序列。
        
        Returns:
            关键路径上的任务列表
        """
        # 计算每个任务的最早开始时间和最晚开始时间
        earliest_start = {}
        latest_start = {}
        
        # 计算最早开始时间
        for task_id in self._topological_sort():
            task = self.task_map[task_id]
            
            if not task.dependencies:
                earliest_start[task_id] = task.start_date
            else:
                max_dep_end = max(
                    self.task_map[dep_id].end_date 
                    for dep_id in task.dependencies
                )
                earliest_start[task_id] = self._add_working_days(max_dep_end, 1)
        
        # 计算最晚开始时间（从后往前）
        task_ids_reversed = list(reversed(self._topological_sort()))
        
        for task_id in task_ids_reversed:
            task = self.task_map[task_id]
            
            if not self.reverse_dependency_graph[task_id]:
                # 没有后续任务，最晚开始时间等于最早开始时间
                latest_start[task_id] = earliest_start[task_id]
            else:
                # 最晚开始时间等于后续任务的最晚开始时间减去当前任务的持续时间
                min_dependent_start = min(
                    latest_start[dep_id] 
                    for dep_id in self.reverse_dependency_graph[task_id]
                )
                latest_start[task_id] = self._subtract_working_days(
                    min_dependent_start, task.duration
                )
        
        # 找出时差为0的任务（关键路径上的任务）
        critical_tasks = []
        for task_id in earliest_start:
            if earliest_start[task_id] == latest_start[task_id]:
                critical_tasks.append(self.task_map[task_id])
        
        return critical_tasks
    
    def _topological_sort(self) -> List[str]:
        """
        拓扑排序
        
        Returns:
            拓扑排序后的任务ID列表
        """
        in_degree_copy = self.in_degree.copy()
        queue = deque([
            task_id for task_id, degree in in_degree_copy.items() 
            if degree == 0
        ])
        
        result = []
        while queue:
            task_id = queue.popleft()
            result.append(task_id)
            
            for dependent_id in self.reverse_dependency_graph[task_id]:
                in_degree_copy[dependent_id] -= 1
                if in_degree_copy[dependent_id] == 0:
                    queue.append(dependent_id)
        
        return result
    
    def get_project_statistics(self) -> Dict:
        """
        获取项目统计信息
        
        Returns:
            包含项目统计信息的字典
        """
        total_duration = 0
        if self.project_plan.start_date and self.project_plan.end_date:
            total_duration = self._count_working_days(
                self.project_plan.start_date, 
                self.project_plan.end_date
            ) + 1
        
        completed_tasks = len([
            task for task in self.project_plan.tasks 
            if 'done' in task.status
        ])
        
        active_tasks = len([
            task for task in self.project_plan.tasks 
            if 'active' in task.status
        ])
        
        critical_path = self.get_critical_path()
        
        return {
            'total_tasks': len(self.project_plan.tasks),
            'completed_tasks': completed_tasks,
            'active_tasks': active_tasks,
            'milestone_count': self.project_plan.milestone_count,
            'total_duration': total_duration,
            'start_date': self.project_plan.start_date,
            'end_date': self.project_plan.end_date,
            'completion_rate': (
                completed_tasks / len(self.project_plan.tasks) * 100 
                if self.project_plan.tasks else 0
            ),
            'critical_path_length': len(critical_path),
            'sections': self.project_plan.get_sections()
        }
