"""
TaskWeaver AI HTML 报告生成器

生成基于Mermaid.js的可交互HTML甘特图报告
"""

import os
from datetime import date
from typing import Dict, List
from jinja2 import Template

from core.models import ProjectPlan, Task


class HTMLGanttGenerator:
    """
    HTML甘特图生成器
    
    使用Mermaid.js生成可交互的HTML甘特图报告
    """
    
    def __init__(self, project_plan: ProjectPlan):
        """
        初始化HTML生成器
        
        Args:
            project_plan: 项目计划对象
        """
        self.project_plan = project_plan
    
    def generate_html(self, filename: str = None, include_statistics: bool = True):
        """
        生成HTML报告
        
        Args:
            filename: 输出文件名
            include_statistics: 是否包含项目统计信息
        """
        if filename is None:
            filename = f"{self.project_plan.title.replace(' ', '_')}.html"
        
        # 生成Mermaid代码
        mermaid_code = self._project_to_mermaid()
        
        # 生成统计信息
        statistics = self._generate_statistics() if include_statistics else None
        
        # 渲染HTML模板
        html_content = self._render_template(mermaid_code, statistics)
        
        # 保存文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML甘特图报告已生成: {filename}")
    
    def _project_to_mermaid(self) -> str:
        """将项目计划转换为Mermaid甘特图代码"""
        lines = ["gantt"]
        lines.append(f"    dateFormat  YYYY-MM-DD")
        lines.append(f"    title       {self.project_plan.title}")
        lines.append("")
        
        # 按section分组
        sections = {}
        for task in self.project_plan.tasks:
            section = task.section or "默认阶段"
            if section not in sections:
                sections[section] = []
            sections[section].append(task)
        
        # 生成各个section
        for section_name, tasks in sections.items():
            lines.append(f"    section {section_name}")
            
            for task in tasks:
                # 构建任务行 - 修复Mermaid语法
                line_parts = [f"    {task.name}", f" :{task.id}"]
                
                # 处理里程碑
                if task.is_milestone:
                    line_parts.append(", milestone")
                    # 添加开始信息
                    if task.dependencies:
                        line_parts.append(f", after {task.dependencies[0]}")
                    elif task.start_date:
                        line_parts.append(f", {task.start_date.strftime('%Y-%m-%d')}")
                else:
                    # 普通任务
                    # 添加状态
                    if task.status:
                        line_parts.append(f", {', '.join(task.status)}")
                    
                    # 添加开始信息
                    if task.dependencies:
                        line_parts.append(f", after {task.dependencies[0]}")
                    elif task.start_date:
                        line_parts.append(f", {task.start_date.strftime('%Y-%m-%d')}")
                    
                    # 添加持续时间
                    if task.duration and task.duration > 0:
                        line_parts.append(f", {task.duration}d")
                
                lines.append("".join(line_parts))
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_statistics(self) -> Dict:
        """生成项目统计信息"""
        total_tasks = len(self.project_plan.tasks)
        completed_tasks = len([t for t in self.project_plan.tasks if 'done' in t.status])
        active_tasks = len([t for t in self.project_plan.tasks if 'active' in t.status])
        critical_tasks = len([t for t in self.project_plan.tasks if 'crit' in t.status])
        milestones = len([t for t in self.project_plan.tasks if t.is_milestone])
        
        # 计算工期
        total_duration = 0
        if self.project_plan.start_date and self.project_plan.end_date:
            total_duration = (self.project_plan.end_date - self.project_plan.start_date).days + 1
        
        # 计算完成率
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'active_tasks': active_tasks,
            'critical_tasks': critical_tasks,
            'milestones': milestones,
            'total_duration': total_duration,
            'completion_rate': completion_rate,
            'start_date': self.project_plan.start_date,
            'end_date': self.project_plan.end_date,
            'sections': self.project_plan.get_sections()
        }
    
    def _render_template(self, mermaid_code: str, statistics: Dict = None) -> str:
        """渲染HTML模板"""
        template_str = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ project_title }} - 甘特图报告</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }
        .content {
            padding: 30px;
        }
        .gantt-container {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .statistics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .stat-card h3 {
            margin: 0 0 10px 0;
            color: #333;
            font-size: 1.1rem;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        .stat-unit {
            font-size: 0.9rem;
            color: #666;
            margin-left: 5px;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            margin-top: 10px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        .task-details {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .task-section {
            margin-bottom: 20px;
        }
        .task-section h4 {
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 5px;
        }
        .task-list {
            list-style: none;
            padding: 0;
        }
        .task-item {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .task-item:last-child {
            border-bottom: none;
        }
        .task-status {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        .status-done { background: #d4edda; color: #155724; }
        .status-active { background: #cce5ff; color: #004085; }
        .status-crit { background: #fff3cd; color: #856404; }
        .status-milestone { background: #f8d7da; color: #721c24; }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            background: #f8f9fa;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ project_title }}</h1>
            <p>项目甘特图报告 • 生成时间: {{ generation_time }}</p>
        </div>
        
        <div class="content">
            {% if statistics %}
            <div class="statistics">
                <div class="stat-card">
                    <h3>任务总数</h3>
                    <div class="stat-value">{{ statistics.total_tasks }}<span class="stat-unit">个</span></div>
                </div>
                <div class="stat-card">
                    <h3>项目进度</h3>
                    <div class="stat-value">{{ "%.1f"|format(statistics.completion_rate) }}<span class="stat-unit">%</span></div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {{ statistics.completion_rate }}%"></div>
                    </div>
                </div>
                <div class="stat-card">
                    <h3>项目工期</h3>
                    <div class="stat-value">{{ statistics.total_duration }}<span class="stat-unit">天</span></div>
                </div>
                <div class="stat-card">
                    <h3>里程碑</h3>
                    <div class="stat-value">{{ statistics.milestones }}<span class="stat-unit">个</span></div>
                </div>
                <div class="stat-card">
                    <h3>进行中任务</h3>
                    <div class="stat-value">{{ statistics.active_tasks }}<span class="stat-unit">个</span></div>
                </div>
                <div class="stat-card">
                    <h3>关键任务</h3>
                    <div class="stat-value">{{ statistics.critical_tasks }}<span class="stat-unit">个</span></div>
                </div>
            </div>
            {% endif %}
            
            <div class="gantt-container">
                <div class="mermaid">
{{ mermaid_code }}
                </div>
            </div>
            
            {% if task_details %}
            <div class="task-details">
                <h3>任务详情</h3>
                {% for section, tasks in task_details.items() %}
                <div class="task-section">
                    <h4>{{ section }}</h4>
                    <ul class="task-list">
                        {% for task in tasks %}
                        <li class="task-item">
                            <span>
                                {{ task.name }}
                                {% if task.is_milestone %}🎯{% endif %}
                            </span>
                            <span class="task-status status-{{ task.status[0] if task.status else 'default' }}">
                                {{ task.status[0] if task.status else '未开始' }}
                            </span>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>由 TaskWeaver AI 生成 • 智能项目规划助手</p>
        </div>
    </div>

    <script>
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            gantt: {
                fontSize: 12,
                gridLineStartPadding: 350,
                bottomPadding: 50,
                rightPadding: 75
            }
        });
    </script>
</body>
</html>"""
        
        template = Template(template_str)
        
        # 准备任务详情
        task_details = {}
        for task in self.project_plan.tasks:
            section = task.section or "默认阶段"
            if section not in task_details:
                task_details[section] = []
            task_details[section].append(task)
        
        return template.render(
            project_title=self.project_plan.title,
            generation_time=date.today().strftime('%Y年%m月%d日'),
            mermaid_code=mermaid_code,
            statistics=statistics,
            task_details=task_details
        )
