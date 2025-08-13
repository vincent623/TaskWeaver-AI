"""
TaskWeaver AI 自然语言解析器

将自然语言项目描述转换为结构化的项目计划
"""

import json
import re
import os
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta

from core.models import Task, ProjectPlan
from core.llm_client import LLMClient, auto_select_provider


class NaturalLanguageParser:
    """
    自然语言解析器
    
    使用AI技术将自然语言描述转换为结构化的项目计划
    """
    
    def __init__(self, provider: str = None, api_key: str = None, model: str = None):
        """
        初始化解析器
        
        Args:
            provider: LLM提供商 ('siliconflow' 或 'openai')
            api_key: API密钥
            model: 使用的模型名称
        """
        try:
            # 自动选择或使用指定的提供商
            if not provider:
                provider = auto_select_provider()
            
            self.llm_client = LLMClient(provider, api_key, model)
            
            if self.llm_client.is_available():
                print(f"✅ 使用 {provider} 进行自然语言解析")
            else:
                print("⚠️ LLM客户端不可用，将使用模拟模式")
                self.llm_client = None
                
        except Exception as e:
            print(f"⚠️ LLM初始化失败，使用模拟模式: {e}")
            self.llm_client = None
    
    def parse(self, description: str, project_title: str = None) -> ProjectPlan:
        """
        解析自然语言描述
        
        Args:
            description: 项目的自然语言描述
            project_title: 项目标题（可选）
            
        Returns:
            解析后的项目计划
        """
        if self.llm_client:
            return self._parse_with_ai(description, project_title)
        else:
            return self._parse_with_simulation(description, project_title)
    
    def _parse_with_ai(self, description: str, project_title: str = None) -> ProjectPlan:
        """使用AI进行解析"""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(description, project_title)
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            content = self.llm_client.chat_completion(messages, temperature=0.1, max_tokens=2000)
            
            if content:
                return self._parse_ai_response(content)
            else:
                raise Exception("LLM返回空结果")
            
        except Exception as e:
            print(f"AI解析失败: {e}")
            return self._parse_with_simulation(description, project_title)
    
    def _parse_with_simulation(self, description: str, project_title: str = None) -> ProjectPlan:
        """模拟解析（当AI不可用时）"""
        print("使用模拟解析器...")
        
        # 简单的规则解析
        tasks = self._extract_tasks_with_rules(description)
        
        return ProjectPlan(
            title=project_title or "AI解析的项目",
            description=description,
            tasks=tasks,
            created_date=date.today(),
            version="1.0"
        )
    
    def _build_system_prompt(self) -> str:
        """构建系统提示"""
        return """你是一个专业的项目管理专家。你的任务是将用户的自然语言项目描述转换为结构化的项目计划。

分析要求：
1. 识别项目中的主要任务和里程碑
2. 估算合理的任务持续时间
3. 分析任务之间的依赖关系
4. 按逻辑将任务分组到不同阶段
5. 识别关键任务和里程碑

输出格式：
返回严格的JSON格式，包含以下结构：
{
    "title": "项目标题",
    "description": "项目描述",
    "tasks": [
        {
            "id": "task1",
            "name": "任务名称",
            "description": "任务描述",
            "duration": 5,
            "dependencies": ["前置任务ID"],
            "status": ["done/active/crit"],
            "is_milestone": false,
            "section": "阶段名称",
            "start_date": "2024-01-01"
        }
    ]
}

注意事项：
- 任务ID使用简短的英文标识符
- 持续时间以工作日为单位
- 依赖关系要确保逻辑正确
- 里程碑的持续时间为0
- 合理安排项目开始时间（通常从今天或下周开始）
- 状态：done(已完成), active(进行中), crit(关键任务)
- 确保返回的是有效的JSON格式"""
    
    def _build_user_prompt(self, description: str, project_title: str = None) -> str:
        """构建用户提示"""
        prompt = f"""请分析以下项目描述，生成结构化的项目计划：

项目描述：
{description}
"""
        
        if project_title:
            prompt += f"\n项目标题：{project_title}"
        
        prompt += "\n\n请返回JSON格式的项目计划。"
        
        return prompt
    
    def _parse_ai_response(self, response: str) -> ProjectPlan:
        """解析AI响应"""
        try:
            # 提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
            else:
                data = json.loads(response)
            
            # 转换为ProjectPlan对象
            tasks = []
            for task_data in data.get('tasks', []):
                # 解析日期
                start_date = None
                if task_data.get('start_date'):
                    try:
                        start_date = datetime.strptime(
                            task_data['start_date'], '%Y-%m-%d'
                        ).date()
                    except ValueError:
                        pass
                
                # 处理status字段（可能是字符串或列表）
                status = task_data.get('status', [])
                if isinstance(status, str):
                    status = [status]
                elif not isinstance(status, list):
                    status = []
                
                task = Task(
                    id=task_data.get('id', ''),
                    name=task_data.get('name', ''),
                    description=task_data.get('description'),
                    duration=task_data.get('duration', 1),
                    dependencies=task_data.get('dependencies', []),
                    status=status,
                    is_milestone=task_data.get('is_milestone', False),
                    section=task_data.get('section'),
                    start_date=start_date
                )
                tasks.append(task)
            
            return ProjectPlan(
                title=data.get('title', 'AI解析的项目'),
                description=data.get('description', ''),
                tasks=tasks,
                created_date=date.today(),
                version="1.0"
            )
            
        except Exception as e:
            print(f"解析AI响应失败: {e}")
            print(f"原始响应: {response}")
            raise ValueError("AI返回的数据格式不正确")
    
    def _extract_tasks_with_rules(self, description: str) -> List[Task]:
        """使用规则提取任务（模拟模式）"""
        tasks = []
        
        # 简单的关键词匹配
        keywords = [
            ("需求分析", 5, "项目启动"),
            ("系统设计", 7, "设计阶段"),
            ("架构设计", 5, "设计阶段"),
            ("前端开发", 10, "开发阶段"),
            ("后端开发", 12, "开发阶段"),
            ("数据库设计", 3, "设计阶段"),
            ("测试", 5, "测试阶段"),
            ("部署", 2, "发布阶段"),
            ("上线", 1, "发布阶段"),
        ]
        
        task_id = 1
        for keyword, duration, section in keywords:
            if keyword in description:
                # 检查是否为里程碑
                is_milestone = "里程碑" in keyword or "完成" in keyword
                
                task = Task(
                    id=f"task{task_id}",
                    name=keyword,
                    duration=0 if is_milestone else duration,
                    is_milestone=is_milestone,
                    section=section,
                    status=["active"] if not is_milestone else ["milestone"]
                )
                tasks.append(task)
                task_id += 1
        
        # 如果没有找到任务，创建默认任务
        if not tasks:
            tasks = [
                Task(
                    id="task1",
                    name="项目规划",
                    duration=3,
                    section="项目启动",
                    status=["active"]
                ),
                Task(
                    id="task2",
                    name="执行阶段",
                    duration=10,
                    dependencies=["task1"],
                    section="执行阶段",
                    status=["active"]
                ),
                Task(
                    id="milestone1",
                    name="项目完成",
                    duration=0,
                    dependencies=["task2"],
                    is_milestone=True,
                    section="项目结束",
                    status=["milestone"]
                )
            ]
        
        return tasks
    
    def enhance_with_ai(self, project_plan: ProjectPlan) -> ProjectPlan:
        """使用AI增强项目计划"""
        if not self.llm_client:
            return project_plan
        
        system_prompt = """你是一个项目管理专家。请分析给定的项目计划，提供优化建议和改进。

优化方向：
1. 检查任务依赖关系的合理性
2. 评估任务时间估算
3. 识别潜在的风险点
4. 建议添加缺失的任务或里程碑
5. 优化任务分组和阶段划分

返回优化后的完整项目计划，格式与输入相同。"""
        
        # 将项目计划转换为描述
        current_plan = self._project_plan_to_dict(project_plan)
        
        user_prompt = f"""请优化以下项目计划：

{json.dumps(current_plan, ensure_ascii=False, indent=2)}

请返回优化后的JSON格式项目计划。"""
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            content = self.llm_client.chat_completion(messages, temperature=0.1, max_tokens=2000)
            
            if content:
                return self._parse_ai_response(content)
            else:
                raise Exception("LLM返回空结果")
            
        except Exception as e:
            print(f"AI优化失败: {e}")
            return project_plan
    
    def _project_plan_to_dict(self, project_plan: ProjectPlan) -> Dict:
        """将项目计划转换为字典"""
        return {
            "title": project_plan.title,
            "description": project_plan.description,
            "tasks": [
                {
                    "id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "duration": task.duration,
                    "dependencies": task.dependencies,
                    "status": task.status,
                    "is_milestone": task.is_milestone,
                    "section": task.section,
                    "start_date": task.start_date.strftime('%Y-%m-%d') if task.start_date else None
                }
                for task in project_plan.tasks
            ]
        }


def create_project_from_description(description: str, title: str = None, 
                                  provider: str = None, api_key: str = None) -> ProjectPlan:
    """
    便捷函数：从自然语言描述创建项目
    
    Args:
        description: 项目描述
        title: 项目标题
        provider: LLM提供商
        api_key: API密钥
        
    Returns:
        项目计划对象
    """
    parser = NaturalLanguageParser(provider=provider, api_key=api_key)
    return parser.parse(description, title)
