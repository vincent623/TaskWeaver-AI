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
    
    使用AI技术将自然语言描述转换为结构化的项目计划。
    需要配置有效的LLM提供商（SiliconFlow或OpenAI）来工作。
    """
    
    def __init__(self, provider: str = None, api_key: str = None, model: str = None):
        """
        初始化解析器
        
        Args:
            provider: LLM提供商 ('siliconflow' 或 'openai')
            api_key: API密钥
            model: 使用的模型名称
        """
        # 自动选择或使用指定的提供商
        if not provider:
            provider = auto_select_provider()
        
        self.llm_client = LLMClient(provider, api_key, model)
        
        if not self.llm_client.is_available():
            raise Exception(f"LLM客户端不可用: {provider}。请检查API密钥和网络连接。")
        
        print(f"✅ 使用 {provider} 进行自然语言解析")
    
    def parse(self, description: str, project_title: str = None) -> ProjectPlan:
        """
        解析自然语言描述
        
        Args:
            description: 项目的自然语言描述
            project_title: 项目标题（可选）
            
        Returns:
            解析后的项目计划
        """
        return self._parse_with_ai(description, project_title)
    
    def _parse_with_ai(self, description: str, project_title: str = None) -> ProjectPlan:
        """使用AI进行解析"""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(description, project_title)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 尝试多次，逐步增加max_tokens
        max_attempts = 3
        token_limits = [3000, 4000, 5000]
        
        for attempt in range(max_attempts):
            try:
                content = self.llm_client.chat_completion(
                    messages, 
                    temperature=0.1, 
                    max_tokens=token_limits[attempt]
                )
                
                if not content:
                    raise Exception("LLM返回空结果")
                
                return self._parse_ai_response(content)
                
            except ValueError as e:
                if "AI返回的数据格式不正确" in str(e) and attempt < max_attempts - 1:
                    print(f"⚠️ 第{attempt + 1}次解析失败，重试中...")
                    continue
                else:
                    raise
            except Exception as e:
                if attempt < max_attempts - 1:
                    print(f"⚠️ 第{attempt + 1}次请求失败，重试中...")
                    continue
                else:
                    raise Exception(f"AI解析失败，已重试{max_attempts}次: {str(e)}")
        
        raise Exception("AI解析失败，请检查网络连接或API配置")
    

    
    def _build_system_prompt(self) -> str:
        """构建系统提示"""
        return """你是项目管理专家。将自然语言项目描述转换为JSON格式的项目计划。

要求：
1. 识别主要任务和里程碑
2. 合理估算持续时间（工作日）
3. 分析任务依赖关系
4. 按阶段分组任务

返回JSON格式：
{
    "title": "项目标题",
    "description": "项目描述",
    "tasks": [
        {
            "id": "task1",
            "name": "任务名称",
            "description": "任务描述",
            "duration": 5,
            "dependencies": [],
            "status": ["active"],
            "is_milestone": false,
            "section": "阶段名称",
            "start_date": "2025-01-01"
        }
    ]
}

注意：
- 任务ID用简短英文标识符
- 里程碑duration为0
- status可选：["active"]、["crit"]、["done"]
- 确保JSON格式正确完整
- 控制任务数量在合理范围内（建议10-20个主要任务）"""
    
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
            # 清理响应文本，移除markdown代码块标记
            clean_response = response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            if clean_response.startswith('```'):
                clean_response = clean_response[3:]
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            # 尝试修复截断的JSON
            if not clean_response.endswith('}'):
                # 查找最后一个完整的对象
                depth = 0
                last_complete_pos = -1
                for i, char in enumerate(clean_response):
                    if char == '{':
                        depth += 1
                    elif char == '}':
                        depth -= 1
                        if depth == 0:
                            last_complete_pos = i + 1
                
                if last_complete_pos > 0:
                    clean_response = clean_response[:last_complete_pos]
                else:
                    # 如果找不到完整结构，尝试添加缺失的大括号
                    open_braces = clean_response.count('{')
                    close_braces = clean_response.count('}')
                    missing_braces = open_braces - close_braces
                    clean_response += '}' * missing_braces
            
            # 解析JSON
            try:
                data = json.loads(clean_response)
            except json.JSONDecodeError as json_error:
                # 如果还是失败，尝试提取JSON部分
                json_match = re.search(r'\{.*?\}', clean_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)
                else:
                    raise json_error
            
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
            print(f"原始响应长度: {len(response)}")
            print(f"响应前500字符: {response[:500]}")
            print(f"响应后500字符: {response[-500:]}")
            raise ValueError(f"AI返回的数据格式不正确: {str(e)}")
    
    def enhance_with_ai(self, project_plan: ProjectPlan) -> ProjectPlan:
        """使用AI增强项目计划"""
        
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
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        content = self.llm_client.chat_completion(messages, temperature=0.1, max_tokens=2000)
        
        if not content:
            raise Exception("LLM返回空结果，优化失败")
        
        return self._parse_ai_response(content)
    
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
