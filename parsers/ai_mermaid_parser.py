"""
TaskWeaver AI 驱动的 Mermaid 甘特图解析器

基于LLM的智能解析器，将AI作为项目的核心中枢，实现更智能、更灵活的Mermaid语法解析。
"""

import json
import re
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod

from core.models import Task, ProjectPlan
from core.llm_client import LLMClient as CoreLLMClient, auto_select_provider


class LLMClientBase(ABC):
    """LLM客户端抽象基类"""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """生成文本"""
        pass


class OpenAIClient(LLMClientBase):
    """OpenAI客户端实现"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.client = None
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            print("警告：未安装openai库，将使用模拟模式")
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """生成文本"""
        if self.client is None:
            # 模拟模式
            return self._simulate_response(prompt)
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            return self._simulate_response(prompt)
    
    def _simulate_response(self, prompt: str) -> str:
        """模拟AI响应（用于测试）"""
        # 这是一个简化的模拟，实际使用时应该连接真实的LLM
        return json.dumps({
            "tasks": [
                {
                    "id": "simulated_task",
                    "name": "模拟任务",
                    "start_date": "2024-01-01",
                    "duration": 5,
                    "dependencies": []
                }
            ]
        })


class AIMermaidParser:
    """
    AI驱动的Mermaid甘特图解析器
    
    利用LLM理解Mermaid语法，实现智能解析和纠错。
    """
    
    def __init__(self, llm_client: LLMClientBase = None, provider: str = None, api_key: str = None):
        # 兼容旧接口
        if llm_client:
            self.llm_client = llm_client
        else:
            # 使用新的统一LLM客户端
            try:
                if not provider:
                    provider = auto_select_provider()
                self.core_llm_client = CoreLLMClient(provider, api_key)
                self.llm_client = self._wrap_core_client()
            except Exception as e:
                print(f"⚠️ LLM客户端初始化失败，将使用备用模式: {e}")
                self.llm_client = None
                
        self.fallback_parser = None  # 备用解析器
        
    def _wrap_core_client(self):
        """包装核心LLM客户端以适配旧接口"""
        class WrappedClient(LLMClientBase):
            def __init__(self, core_client):
                self.core_client = core_client
                
            def generate(self, prompt: str, system_prompt: str = None) -> str:
                return self.core_client.simple_completion(prompt, system_prompt)
        
        return WrappedClient(self.core_llm_client)
        
    def set_fallback_parser(self, parser):
        """设置备用解析器"""
        self.fallback_parser = parser
    
    def parse(self, mermaid_code: str) -> ProjectPlan:
        """
        使用AI解析Mermaid代码
        
        Args:
            mermaid_code: Mermaid Gantt 语法代码
            
        Returns:
            解析后的项目计划对象
        """
        try:
            # 首先尝试AI解析
            return self._parse_with_ai(mermaid_code)
        except Exception as e:
            print(f"AI解析失败: {e}")
            # 如果AI解析失败，使用备用解析器
            if self.fallback_parser:
                return self.fallback_parser.parse(mermaid_code)
            else:
                raise RuntimeError("AI解析失败且无备用解析器")
    
    def _parse_with_ai(self, mermaid_code: str) -> ProjectPlan:
        """使用AI进行解析"""
        # 步骤1：语法纠错
        corrected_code = self._correct_syntax(mermaid_code)
        
        # 步骤2：智能解析
        parsed_data = self._intelligent_parse(corrected_code)
        
        # 步骤3：转换为统一数据模型
        return self._convert_to_project_plan(parsed_data)
    
    def _correct_syntax(self, mermaid_code: str) -> str:
        """使用AI纠正语法错误"""
        system_prompt = """你是一个Mermaid甘特图语法专家。你的任务是纠正用户提供的Mermaid代码中的语法错误，保持原意不变。
        
        纠正原则：
        1. 保持任务名称、ID、日期、依赖关系等核心信息不变
        2. 修正语法格式，使其符合标准Mermaid Gantt语法
        3. 补充缺失的必要信息（如持续时间）
        4. 统一日期格式
        5. 确保依赖关系的正确性
        
        返回纠正后的Mermaid代码，不要添加任何解释。"""
        
        prompt = f"""请纠正以下Mermaid代码中的语法错误：

```mermaid
{mermaid_code}
```"""
        
        corrected = self.llm_client.generate(prompt, system_prompt)
        
        # 提取Mermaid代码部分
        mermaid_match = re.search(r'```mermaid\n(.*?)\n```', corrected, re.DOTALL)
        if mermaid_match:
            return mermaid_match.group(1)
        
        return corrected
    
    def _intelligent_parse(self, mermaid_code: str) -> Dict[str, Any]:
        """智能解析Mermaid代码"""
        system_prompt = """你是一个Mermaid甘特图解析专家。你的任务是将Mermaid代码解析为结构化的任务数据。
        
        解析要求：
        1. 提取所有任务信息，包括：任务ID、名称、状态、开始日期、持续时间、依赖关系
        2. 识别里程碑任务（标记为milestone状态）
        3. 确定任务所属的阶段（section）
        4. 计算任务的结束日期
        5. 验证依赖关系的正确性
        
        返回JSON格式的数据，包含以下字段：
        - title: 项目标题
        - date_format: 日期格式
        - sections: 项目阶段列表
        - tasks: 任务列表，每个任务包含：
          - id: 任务ID
          - name: 任务名称
          - status: 状态列表
          - section: 所属阶段
          - is_milestone: 是否为里程碑
          - start_date: 开始日期
          - end_date: 结束日期
          - duration: 持续时间（天数）
          - dependencies: 依赖的任务ID列表
        
        确保返回的是有效的JSON格式。"""
        
        prompt = f"""请解析以下Mermaid代码，返回结构化的任务数据：

```mermaid
{mermaid_code}
```"""
        
        response = self.llm_client.generate(prompt, system_prompt)
        
        # 解析JSON响应
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"原始响应: {response}")
            raise ValueError("AI返回的数据格式不正确")
    
    def _convert_to_project_plan(self, parsed_data: Dict[str, Any]) -> ProjectPlan:
        """转换为统一的项目计划对象"""
        tasks = []
        
        # 创建任务对象
        for task_data in parsed_data.get('tasks', []):
            # 解析日期
            start_date = self._parse_date(task_data.get('start_date'))
            end_date = self._parse_date(task_data.get('end_date'))
            
            task = Task(
                id=task_data.get('id', ''),
                name=task_data.get('name', ''),
                status=task_data.get('status', []),
                section=task_data.get('section'),
                is_milestone=task_data.get('is_milestone', False),
                start_date=start_date,
                end_date=end_date,
                duration=task_data.get('duration'),
                dependencies=task_data.get('dependencies', [])
            )
            tasks.append(task)
        
        # 创建项目计划
        project_plan = ProjectPlan(
            title=parsed_data.get('title', 'AI解析的项目'),
            tasks=tasks,
            date_format=parsed_data.get('date_format', '%Y-%m-%d'),
            created_date=date.today(),
            version="1.0"
        )
        
        return project_plan
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """解析日期字符串"""
        if not date_str:
            return None
        
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
    
    def natural_language_to_mermaid(self, description: str) -> str:
        """将自然语言描述转换为Mermaid代码"""
        system_prompt = """你是一个项目规划专家。你的任务是将用户的自然语言描述转换为标准的Mermaid甘特图代码。
        
        转换要求：
        1. 识别项目中的主要任务和里程碑
        2. 确定任务之间的依赖关系
        3. 合理安排任务的时间顺序
        4. 使用标准的Mermaid Gantt语法
        5. 添加适当的section来组织任务
        
        返回完整的Mermaid代码，包含必要的dateFormat和title。"""
        
        prompt = f"""请将以下项目描述转换为Mermaid甘特图代码：

{description}"""
        
        response = self.llm_client.generate(prompt, system_prompt)
        
        # 提取Mermaid代码部分
        mermaid_match = re.search(r'```mermaid\n(.*?)\n```', response, re.DOTALL)
        if mermaid_match:
            return mermaid_match.group(1)
        
        return response
    
    def optimize_project_plan(self, project_plan: ProjectPlan) -> ProjectPlan:
        """使用AI优化项目计划"""
        # 将项目计划转换为描述
        description = self._project_plan_to_description(project_plan)
        
        system_prompt = """你是一个项目管理专家。你的任务是优化项目计划，提供更好的建议。
        
        优化方向：
        1. 识别并解决依赖冲突
        2. 优化任务时间安排
        3. 建议关键路径优化
        4. 提供风险评估
        5. 建议资源分配优化
        
        返回优化后的项目计划数据，格式与输入相同。"""
        
        prompt = f"""请优化以下项目计划：

{description}"""
        
        response = self.llm_client.generate(prompt, system_prompt)
        
        try:
            # 解析优化后的数据
            optimized_data = json.loads(response)
            return self._convert_to_project_plan(optimized_data)
        except Exception as e:
            print(f"优化解析失败: {e}")
            return project_plan
    
    def _project_plan_to_description(self, project_plan: ProjectPlan) -> str:
        """将项目计划转换为描述"""
        description = f"项目标题: {project_plan.title}\n\n"
        description += "任务列表:\n"
        
        for task in project_plan.tasks:
            deps = ", ".join(task.dependencies) if task.dependencies else "无"
            status = ", ".join(task.status) if task.status else "无"
            description += f"- {task.name} ({task.id}): "
            description += f"状态[{status}], 开始[{task.start_date}], "
            description += f"持续[{task.duration}天], 依赖[{deps}]\n"
        
        return description


class AIMermaidValidator:
    """AI驱动的Mermaid语法验证器"""
    
    def __init__(self, llm_client: LLMClientBase):
        self.llm_client = llm_client
    
    def validate(self, mermaid_code: str) -> tuple:
        """使用AI验证Mermaid代码"""
        system_prompt = """你是一个Mermaid甘特图语法专家。你的任务是验证用户提供的Mermaid代码的正确性。
        
        验证内容：
        1. 语法正确性
        2. 依赖关系的完整性
        3. 日期格式的一致性
        4. 任务信息的完整性
        5. 循环依赖检测
        
        返回JSON格式的验证结果：
        {
            "is_valid": true/false,
            "errors": ["错误1", "错误2"],
            "warnings": ["警告1", "警告2"],
            "suggestions": ["建议1", "建议2"]
        }"""
        
        prompt = f"""请验证以下Mermaid代码的正确性：

```mermaid
{mermaid_code}
```"""
        
        response = self.llm_client.generate(prompt, system_prompt)
        
        try:
            # 解析JSON响应
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                return (
                    result.get('is_valid', False),
                    result.get('errors', []),
                    result.get('warnings', [])
                )
            else:
                result = json.loads(response)
                return (
                    result.get('is_valid', False),
                    result.get('errors', []),
                    result.get('warnings', [])
                )
        except Exception as e:
            print(f"验证解析失败: {e}")
            return False, ["AI验证失败"], []
    
    def suggest_improvements(self, mermaid_code: str) -> List[str]:
        """使用AI提供改进建议"""
        system_prompt = """你是一个Mermaid甘特图专家。请为用户提供的Mermaid代码提供改进建议。
        
        建议方向：
        1. 语法优化
        2. 结构改进
        3. 可读性提升
        4. 最佳实践应用
        
        返回JSON格式的建议列表：
        {
            "suggestions": ["建议1", "建议2", "建议3"]
        }"""
        
        prompt = f"""请为以下Mermaid代码提供改进建议：

```mermaid
{mermaid_code}
```"""
        
        response = self.llm_client.generate(prompt, system_prompt)
        
        try:
            # 解析JSON响应
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                return result.get('suggestions', [])
            else:
                result = json.loads(response)
                return result.get('suggestions', [])
        except Exception as e:
            print(f"建议解析失败: {e}")
            return []


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


def test_ai_mermaid_parser():
    """测试 AI Mermaid 解析器"""
    print("=== 测试 AI Mermaid 解析器 ===")
    
    # 创建模拟的LLM客户端
    llm_client = OpenAIClient("dummy_key")  # 使用模拟模式
    
    # 创建AI解析器
    ai_parser = AIMermaidParser(llm_client)
    
    # 设置备用解析器
    from parsers.mermaid_parser import MermaidParser
    fallback_parser = MermaidParser()
    ai_parser.set_fallback_parser(fallback_parser)
    
    # 创建示例代码
    mermaid_code = create_sample_mermaid_code()
    
    print("原始Mermaid代码:")
    print(mermaid_code)
    print("\n" + "="*50 + "\n")
    
    try:
        # 使用AI解析
        print("正在使用AI解析...")
        project_plan = ai_parser.parse(mermaid_code)
        
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
        
        print("✅ AI解析成功")
        
    except Exception as e:
        print(f"❌ AI解析失败: {e}")
    
    # 测试自然语言转换
    print("\n=== 测试自然语言转换 ===")
    nl_description = """
    我们需要开发一个电商网站项目。首先进行需求分析，大概需要5天时间。
    然后是系统设计，需要7天。接着是前端开发，预计10天，同时进行后端开发，需要12天。
    开发完成后进行集成测试，需要5天。然后是系统测试和用户验收测试，各需要5天。
    最后是部署准备和正式发布，分别需要3天和2天。我们在需求分析完成后设置一个里程碑，
    在用户验收测试完成后设置另一个里程碑。
    """
    
    try:
        print("自然语言描述:")
        print(nl_description)
        print("\n正在转换为Mermaid代码...")
        
        mermaid_result = ai_parser.natural_language_to_mermaid(nl_description)
        print("转换结果:")
        print(mermaid_result)
        
    except Exception as e:
        print(f"❌ 自然语言转换失败: {e}")
    
    # 测试AI验证
    print("\n=== 测试AI验证 ===")
    ai_validator = AIMermaidValidator(llm_client)
    
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
        
        if is_valid and not errors and not warnings:
            print("✅ 语法验证通过")
        
    except Exception as e:
        print(f"❌ AI验证失败: {e}")
    
    # 测试改进建议
    print("\n=== 测试改进建议 ===")
    try:
        print("正在生成改进建议...")
        suggestions = ai_validator.suggest_improvements(mermaid_code)
        
        if suggestions:
            print("改进建议:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        else:
            print("暂无改进建议")
        
    except Exception as e:
        print(f"❌ 生成建议失败: {e}")


if __name__ == "__main__":
    test_ai_mermaid_parser()
