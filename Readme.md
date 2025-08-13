# TaskWeaver AI - 智能项目规划助手

TaskWeaver AI 是一个强大的效率工具，旨在将高阶的项目构想或 Mermaid 代码快速转化为具体、可执行的计划。它能理解自然语言描述，也能解析 Mermaid 甘特图代码，并自动生成包含动态公式的专业 Excel 甘特图和交互式 HTML 报告。

## 项目目标

本项目的核心目标是弥合"想法"与"计划"之间的鸿沟，通过 AI 技术自动化项目规划流程，从而：
- **节省时间**: 将数小时的手动规划工作缩短为几分钟
- **降低门槛**: 使非项目管理专业人士也能轻松创建出结构清晰的项目计划
- **提升灵活性**: 支持多种输入和输出格式，适应不同的工作流和分享场景
- **文件组织**: 每个项目生成独立文件夹，便于管理和分享
- **项目质量**: 精简高效的代码结构，完整的测试覆盖

## 🎯 项目优势

### 版本 1.0.0 特性
- **🏗️ 精简架构**: 移除所有冗余文件，保持项目结构清洁高效
- **⚙️ 现代化配置**: 使用 `pyproject.toml` 符合Python最佳实践
- **🧪 完整测试**: 核心模块和解析器的全面测试覆盖
- **📁 智能管理**: 文件夹结构化输出，便于项目管理和分享
- **🔄 多提供商**: 支持硅基流动、OpenAI等多个LLM提供商
- **🛡️ 稳定可靠**: 备用机制确保在任何情况下都能正常工作

## 主要功能

### 🤖 AI 智能解析
- **自然语言处理**: 使用硅基流动等LLM提供商，智能解析中文项目描述
- **智能任务识别**: 自动识别任务、估算时长、推断依赖关系
- **语法修正**: AI自动修正Mermaid语法错误

### 🔄 多源输入支持
- **自然语言**: 直接输入一段关于项目的文字描述
- **Mermaid 代码**: 完美兼容标准的 Mermaid 甘特图语法
- **交互式创建**: 支持问答式项目创建

### 📊 多格式输出 - 每个项目生成独立文件夹
每次输出都会在 `outputs/项目名称/` 下生成完整的项目文件：

- **📈 Excel 图表甘特图** (`_chart.xlsx`)
  - 包含视觉甘特图和数据表
  - 自动生成 Excel 公式实现日期联动
  - 里程碑高亮显示

- **📅 Excel 表格甘特图** (`_table.xlsx`)  
  - 单元格填充式甘特图
  - 直观的时间轴展示
  - 任务状态颜色标识

- **🌐 HTML 交互报告** (`_report.html`)
  - 基于 Mermaid.js 的交互式甘特图
  - 无需安装软件，浏览器直接查看
  - 支持缩放、悬停等交互功能

- **📄 项目信息文件** (`project_info.txt`)
  - 项目基本信息和统计数据
  - 文件说明和生成时间
  - 便于项目归档管理

## 技术栈

- **核心框架**: Python 3.12+
- **AI & NLP**: 硅基流动、OpenAI 等多LLM提供商支持
- **数据模型**: Pydantic (类型安全和数据验证)
- **Excel 操作**: openpyxl (动态公式生成)
- **HTML 生成**: Jinja2 + Mermaid.js
- **依赖管理**: UV (快速Python包管理器)
- **环境配置**: .env文件自动加载

## 项目文件结构

```
TaskWeaver AI/                          # 精简高效的项目结构
├── 🚀 main.py                          # 程序入口和CLI界面
├── 📁 core/                            # 核心模块
│   ├── __init__.py
│   ├── models.py                       # 📋 数据模型 (Task, ProjectPlan)
│   ├── processor.py                    # ⚙️ 核心处理引擎
│   └── llm_client.py                   # 🤖 统一LLM客户端
├── 📁 parsers/                         # 解析器模块
│   ├── __init__.py
│   ├── mermaid_parser.py               # 📝 Mermaid语法解析器
│   ├── ai_mermaid_parser.py            # 🧠 AI增强解析器
│   └── nlp_parser.py                   # 💬 自然语言解析器
├── 📁 generators/                      # 生成器模块
│   ├── __init__.py
│   ├── excel_generator.py              # 📊 Excel甘特图生成器
│   └── html_generator.py               # 🌐 HTML报告生成器
├── 📁 templates/                       # 模板文件
│   └── gantt_template.html             # 🎨 HTML模板
├── 📁 test/                            # 测试模块
│   ├── __init__.py
│   ├── test_core.py                    # 核心模块测试
│   ├── test_mermaid_parser.py          # 解析器测试
│   └── test_ai_mermaid_parser.py       # AI解析器测试
├── 📁 examples/                        # 示例文件
│   └── sample_project.mermaid          # 示例项目文件
├── 📁 outputs/                         # 输出目录（自动生成）
│   ├── project1/                       # 每个项目独立文件夹
│   │   ├── project1_chart.xlsx         # Excel图表甘特图
│   │   ├── project1_table.xlsx         # Excel表格甘特图
│   │   ├── project1_report.html        # HTML交互报告
│   │   └── project_info.txt            # 项目信息文件
│   └── project2/
│       └── ...
├── ⚙️ pyproject.toml                   # 现代化项目配置
├── 📦 requirements.txt                 # 精简依赖列表
├── 🔧 env.example                      # 环境配置模板
├── 🛡️ .gitignore                       # Git忽略规则
└── 📚 Readme.md                        # 项目文档
```

### 🌟 结构特点

- **📦 模块化设计**: 清晰的功能分离，便于维护和扩展
- **🗂️ 精简高效**: 移除所有冗余文件，保持结构清洁
- **⚙️ 现代化配置**: 使用 `pyproject.toml` 符合Python最佳实践
- **🧪 完整测试**: 每个模块都有对应的测试文件
- **📁 智能输出**: 每个项目生成独立文件夹，便于管理

## 安装与使用

### 1. 环境准备

```bash
# 方法1: 使用 UV（推荐，速度更快）
uv venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
uv pip install -r requirements.txt

# 方法2: 使用传统 pip
python -m venv venv
source venv/bin/activate   # macOS/Linux  
# venv\Scripts\activate    # Windows
pip install -r requirements.txt

# 方法3: 开发模式安装（推荐开发者）
pip install -e .
```

### 2. 配置 AI 功能

复制环境配置文件并配置API密钥：
```bash
cp env.example .env
# 编辑 .env 文件，添加您的API密钥
```

**支持的LLM提供商**：
- **硅基流动**（推荐）：性价比高，支持中文
- **OpenAI**：功能强大，需科学上网

### 3. 快速开始

#### 🎯 从自然语言创建项目（推荐）：
```bash
python main.py create --from-text "开发一个电商网站：需求分析5天，UI设计7天，前端开发15天，后端开发20天，测试8天，部署2天" -o ecommerce_project
```
**输出**: `outputs/ecommerce_project/` 文件夹，包含完整项目文件

#### 📝 解析Mermaid文件：
```bash
python main.py parse examples/sample_project.mermaid -o sample_analysis
```
**输出**: `outputs/sample_analysis/` 文件夹

#### ✅ 验证Mermaid语法：
```bash
python main.py validate examples/sample_project.mermaid
```

#### 🧪 运行功能测试：
```bash
python main.py test
```

## 🧪 测试与验证

TaskWeaver AI 提供完整的测试套件，确保代码质量和功能稳定性：

### 运行所有测试
```bash
# 运行完整测试套件
python main.py test

# 运行特定模块测试
python main.py test --module core      # 核心模块测试
python main.py test --module parser   # 解析器测试
python main.py test --module ai       # AI功能测试
```

### 测试覆盖范围
- **✅ 核心模块测试** (`test_core.py`)
  - 数据模型验证
  - 处理引擎测试
  - 依赖关系计算
  - 错误处理机制

- **✅ 解析器测试** (`test_mermaid_parser.py`) 
  - Mermaid语法解析
  - 日期格式处理
  - 依赖关系解析
  - 里程碑处理

- **✅ AI功能测试** (`test_ai_mermaid_parser.py`)
  - LLM客户端初始化
  - AI解析功能
  - 自然语言处理

### 预期测试结果
```
🎉 所有测试通过！核心模块工作正常。
🎉 所有测试通过！Mermaid 解析器工作正常。
✅ AI客户端和解析器模块正常加载
```

### 4. 主要命令参考

| 命令 | 说明 | 输出 | 示例 |
|------|------|------|------|
| `create --from-text` | 🤖 AI解析自然语言创建项目 | 项目文件夹 | `python main.py create --from-text "描述" -o 项目名` |
| `parse` | 📝 解析Mermaid文件 | 项目文件夹 | `python main.py parse input.mermaid -o 输出名` |
| `validate` | ✅ 验证Mermaid语法 | 验证结果 | `python main.py validate input.mermaid` |
| `create --interactive` | 💬 交互式创建项目 | 项目文件夹 | `python main.py create --interactive` |
| `test` | 🧪 运行功能测试 | 测试报告 | `python main.py test` |

### 5. 文件夹输出说明

**每个项目都会生成独立的文件夹**，包含：

```
outputs/项目名称/
├── 📊 项目名称_chart.xlsx     # Excel图表甘特图
├── 📅 项目名称_table.xlsx     # Excel表格甘特图  
├── 🌐 项目名称_report.html    # HTML交互报告
└── 📄 project_info.txt        # 项目信息和说明
```

### 6. 高级用法

#### 查看详细帮助：
```bash
python main.py --help
python main.py create --help
python main.py parse --help
```

#### 指定输出目录：
```bash
python main.py create --from-text "项目描述" -o custom_project_name
# 输出到: outputs/custom_project_name/
```

## 使用示例

### 🎯 自然语言项目创建示例

#### 软件开发项目：
```bash
python main.py create --from-text "开发一个在线教育平台：需求调研3天，原型设计5天，UI/UX设计8天，前端开发20天，后端API开发25天，数据库设计3天，系统集成5天，功能测试10天，性能优化3天，部署上线2天" -o education_platform
```

#### 营销活动项目：
```bash
python main.py create --from-text "春节营销活动策划：市场调研5天，创意策划3天，素材制作7天，渠道对接2天，活动上线1天，效果监控14天，数据分析2天，总结报告1天" -o spring_campaign
```

#### 产品发布项目：
```bash
python main.py create --from-text "新产品发布：产品定位2天，功能设计5天，开发阶段30天，内测阶段7天，公测阶段14天，发布准备3天，正式发布1天，后续支持持续" -o product_launch
```

### 📝 Mermaid文件解析示例

```bash
# 解析现有的Mermaid项目文件
python main.py parse examples/sample_project.mermaid -o analyzed_project

# 验证Mermaid语法
python main.py validate my_project.mermaid
```

## 输出文件说明

每个项目文件夹包含4种类型的文件：

### 📊 Excel图表甘特图 (`*_chart.xlsx`)
- **可视化甘特图**：专业的条形图展示
- **动态公式**：修改数据自动更新图表
- **里程碑突出**：重要节点特殊标记
- **适用场景**：正式汇报、项目跟踪

### 📅 Excel表格甘特图 (`*_table.xlsx`)
- **单元格填充**：直观的时间轴视图
- **状态颜色**：不同任务状态用颜色区分
- **紧凑布局**：适合打印和快速浏览
- **适用场景**：日常管理、团队协作

### 🌐 HTML交互报告 (`*_report.html`)
- **Mermaid.js驱动**：现代化的交互体验
- **无需软件**：浏览器直接打开
- **响应式设计**：支持各种设备
- **适用场景**：在线分享、客户展示

### 📄 项目信息文件 (`project_info.txt`)
- **元数据记录**：项目基本信息
- **生成时间**：便于版本管理
- **统计信息**：任务数量、工期等
- **文件说明**：各文件用途介绍

## 最佳实践

### 🎯 项目命名建议
- 使用有意义的项目名称：`python main.py create --from-text "..." -o website_redesign`
- 避免特殊字符，使用下划线或连字符
- 包含日期信息：`-o project_2024Q1`

### 🤖 AI 提示词优化
1. **详细描述**：包含具体的任务和时间估算
2. **明确依赖**：说明任务之间的先后关系
3. **使用中文**：AI更好地理解中文项目描述
4. **包含里程碑**：标明重要的检查点

**好的示例**：
```
"开发电商网站：需求分析(3天) -> UI设计(5天) -> 前端开发(15天，依赖UI设计) -> 后端开发(20天，与前端并行) -> 集成测试(5天，依赖前后端) -> 部署上线(2天) -> 运维监控(持续)"
```

### 📁 文件管理建议
- **定期清理**: 定期清理`outputs/`目录中的旧项目文件夹
- **项目备份**: 重要项目可以直接压缩整个文件夹进行备份
- **版本管理**: 使用Git管理Mermaid源文件和项目配置
- **文件夹命名**: 使用有意义的项目名称，便于后续查找

### 🛠️ 开发和维护
- **代码规范**: 项目使用Black进行代码格式化
- **类型检查**: 使用MyPy进行静态类型检查
- **测试驱动**: 每个新功能都应该有对应的测试
- **依赖管理**: 优先使用UV进行包管理，保持依赖最新

## 技术架构

### 核心设计理念

TaskWeaver AI 采用**"输入 -> 标准化 -> 输出"**的解耦架构：

```
输入层 (Parsers)    核心层 (Processor)    输出层 (Generators)
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ 🤖 自然语言解析  │  │ 📋 统一数据模型  │  │ 📊 Excel生成器   │
│ 📝 Mermaid解析  │──│ ⚙️ 依赖计算引擎  │──│ 🌐 HTML生成器    │
│ 💬 交互式创建   │  │ 📅 日期计算引擎  │  │ 📁 文件夹管理   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 核心特性

- **🔄 多源输入统一**: 无论什么输入格式，都转换为标准数据模型
- **🧠 智能依赖计算**: 自动解析任务依赖关系，计算关键路径
- **📊 多格式输出**: 一次生成多种格式，满足不同使用场景
- **📁 文件夹管理**: 项目文件有序组织，便于管理和分享

## 📊 项目状态

| 项目信息 | 详情 |
|---------|------|
| **当前版本** | 1.0.0 |
| **开发状态** | 🟢 稳定发布 |
| **Python版本** | 3.12+ |
| **测试覆盖** | 🧪 完整覆盖 |
| **代码质量** | ⭐ 生产级别 |

## 🔄 更新日志

### v1.0.0 (2024-08-14)
- ✅ **项目重构**: 完成模块化架构重构
- ✅ **结构优化**: 移除冗余文件，精简项目结构
- ✅ **配置现代化**: 更新为 `pyproject.toml` 配置
- ✅ **文件夹输出**: 实现项目文件夹化管理
- ✅ **多LLM支持**: 集成硅基流动等多个提供商
- ✅ **测试完善**: 添加完整的测试套件
- ✅ **文档更新**: 完善README和使用指南

## 许可证

MIT License - 开源免费使用

## 🤝 贡献指南

欢迎参与TaskWeaver AI的开发和改进！

### 贡献方式
- 🐛 **Bug报告**: 在Issues中提供详细的问题描述和复现步骤
- 💡 **功能建议**: 描述具体的使用场景和期望效果
- 🔧 **代码贡献**: Fork项目后提交Pull Request
- 📖 **文档改进**: 帮助完善文档和示例

### 开发环境设置
```bash
# 1. Fork并克隆项目
git clone your-fork-url
cd TaskWeaver-AI

# 2. 设置开发环境
uv venv
source .venv/bin/activate
pip install -e .[dev]

# 3. 运行测试
python main.py test

# 4. 代码格式化
black .
mypy .
```

### 代码规范
- 遵循PEP 8编码规范
- 使用Black进行代码格式化
- 通过MyPy类型检查
- 为新功能添加测试用例

## 联系方式

- 📧 **Issues**: [GitHub Issues](https://github.com/username/taskweaver-ai/issues)
- 📝 **讨论**: [GitHub Discussions](https://github.com/username/taskweaver-ai/discussions)
- 🌟 **支持**: 如果项目对您有帮助，请给个Star ⭐

---

<div align="center">

**TaskWeaver AI v1.0.0** 

*让项目规划变得简单高效！* 🚀

[![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red.svg)](https://github.com/username/taskweaver-ai)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

</div>

