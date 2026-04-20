# 基于云端API的Agent智能体系统

## 项目介绍

这是一个基于大语言模型的智能体对话系统，具备自主思考与工具调用能力。主要应用于金融舆情分析、学术文献调研等领域。

## 功能特性

- **智能体工作流设计**：基于云端LLM API，实现自主规划和执行
- **外部工具调用**：集成多种工具，包括论文检索、网页抓取、报告生成
- **Chain-of-Thought展示**：清晰展示智能体的思考链路和执行过程
- **异步并发处理**：支持多篇文献同时处理，提高调研效率
- **交互式Web界面**：基于Streamlit的现代化用户界面

## 技术栈

- **后端框架**: FastAPI
- **前端框架**: Streamlit
- **大模型API**: DeepSeek / OpenAI / Kimi 等兼容API
- **异步处理**: Asyncio

## 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行项目

```bash
python start.py
```

### 访问地址

- 前端界面: http://localhost:8501
- 后端API: http://localhost:8000

## 配置说明

### 侧边栏配置

1. **系统配置**
   - 后端服务地址: http://localhost:8000

2. **LLM配置**
   - API Key: 您的LLM服务API密钥
   - API Base URL: API地址（默认: https://api.deepseek.com/v1）
   - 模型名称: 使用的模型（默认: deepseek-chat）

3. **高级选项**
   - 最大迭代次数: 智能体执行的最大迭代次数

### 使用方法

1. 在侧边栏填入您的API Key
2. 在主界面输入研究需求
3. 点击"开始调研"按钮
4. 查看生成的调研报告和执行日志

## 项目结构

```
llm_agent_project/
├── backend/
│   ├── main.py              # 后端API服务
│   ├── agent/
│   │   └── research_agent.py # 智能体核心逻辑
│   └── tools/
│       ├── arxiv_tool.py     # ArXiv论文检索工具
│       ├── web_crawler.py    # 网页抓取工具
│       └── report_generator.py # 报告生成工具
├── frontend/
│   └── app.py              # 前端界面
├── config/
│   └── config.yaml         # 配置文件
├── start.py               # 统一启动脚本
└── requirements.txt       # 依赖文件
```

## 核心模块

### 1. 智能体模块 (backend/agent/)

- `research_agent.py`: 智能体核心逻辑，包含Prompt模板、规划执行流程

### 2. 工具模块 (backend/tools/)

- `arxiv_tool.py`: ArXiv论文检索工具
- `web_crawler.py`: 网页正文抓取工具
- `report_generator.py`: Markdown报告生成工具

### 3. 前端界面 (frontend/)

- `app.py`: Streamlit Web界面，包含查询输入、结果展示、执行日志

## 实验要求

本项目满足"第三方向：基于云端API的Agent工具系统"的全部要求：

- ✅ Agentic Workflow设计
- ✅ 外部工具定义（Function Calling）
- ✅ API接入与高并发处理
- ✅ 可视化与执行日志追踪

## License

MIT License

## Author

[您的名字]

## Acknowledgments

- 基于Streamlit框架构建
- 使用DeepSeek API作为默认LLM服务
