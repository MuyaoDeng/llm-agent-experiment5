# 使用文档

## 项目概述

这是一个基于云端LLM API的Agent（智能体）工具系统，具备自主思考与工具调用能力（Function Calling）。系统可以自动规划步骤、调用外部工具，并生成结构化的研究报告。

## 核心功能

### 1. Agentic Workflow（智能体工作流）

- **System Prompt设计**: 定义了资深AI研究员的角色，擅长文献收集和综述撰写
- **Function Calling**: 集成了3个外部工具
  - ArxivSearchTool: 搜索学术论文
  - WebScraperTool: 抓取网页内容
  - ReportGeneratorTool: 生成Markdown报告
- **自主规划**: LLM根据用户输入自动规划调研步骤并执行

### 2. API接入与高并发处理

- 支持DeepSeek-V3、Kimi等主流大模型API
- 使用AsyncIO实现异步并发请求
- 内置重试机制和错误处理
- 支持API限流控制

### 3. 可视化与执行日志追踪

- 前端清晰展示智能体的思考链路（Chain-of-Thought）
- 显示每个步骤的详细信息：
  - 规划了什么步骤
  - 调用了哪个API
  - 耗时多少
  - 提取了哪些关键信息

## 快速开始

### 🚀 方式一：一键启动（最简单）

这是最简单的启动方式，一个命令同时启动前后端。

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 一键启动

**Windows:**

```bash
start.bat
```

或

```bash
python start.py
```

**Linux/Mac:**

```bash
chmod +x start.sh
./start.sh
```

或

```bash
python3 start.py
```

系统会自动启动：

- 后端服务：<http://localhost:8000>
- 前端界面：<http://localhost:8501（浏览器自动打开）>

按 `Ctrl+C` 可同时停止所有服务。

#### 3. 在前端界面配置

在侧边栏的"系统配置"和"LLM配置"部分填入：

- **后端服务地址**: <http://localhost:8000（默认）>
- **API Key**: 您的LLM服务API密钥（如：sk-xxx）
- **API Base URL**: LLM API地址（如：<https://api.deepseek.com/v1）>
- **模型名称**: 使用的模型（如：deepseek-chat）

### 方式二：分别启动

如果需要更灵活的控制，可以分别启动前后端：

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 启动后端服务

```bash
python backend/main.py
```

后端服务将在 <http://localhost:8000> 启动

#### 3. 启动前端界面

打开新的终端窗口：

```bash
streamlit run frontend/app.py
```

前端界面将在浏览器中自动打开（通常是 <http://localhost:8501）>

### 方式三：配置文件方式

如果您希望使用配置文件，可以按以下步骤操作：

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置API密钥

```bash
# 复制配置文件模板
copy config\config.example.yaml config\config.yaml

# 编辑config.yaml，填入您的API密钥
```

配置示例：

```yaml
llm:
  provider: "deepseek"
  api_key: "sk-your-api-key-here"  # 填入真实API密钥
  base_url: "https://api.deepseek.com/v1"
  model: "deepseek-chat"
  max_tokens: 4096
  temperature: 0.7
```

#### 3. 启动后端服务

```bash
python backend/main.py
```

#### 4. 启动前端界面

```bash
streamlit run frontend/app.py
```

**注意**: 使用配置文件方式时，前端界面的LLM配置将被忽略，系统会使用配置文件中的设置。

## 使用示例

### 示例1：调研DPO算法

**输入查询：**

```
帮我调研2026年关于DPO算法的最新进展
```

**系统执行流程：**

1. LLM分析查询，规划调研步骤
2. 调用ArxivSearchTool搜索相关论文
3. 分析论文摘要，提取关键信息
4. 调用ReportGeneratorTool生成Markdown报告
5. 返回最终结果

### 示例2：强化学习综述

**输入查询：**

```
搜索强化学习领域的最新论文并生成综述
```

### 示例3：Transformer架构调研

**输入查询：**

```
调研Transformer架构的最新改进
```

## 核心代码说明

### 1. 工具调用（Function Calling）

**工具定义示例** (`backend/tools/arxiv_tool.py`):

```python
class ArxivSearchTool(BaseTool):
    def __init__(self, max_results: int = 10):
        super().__init__()
        self.description = "搜索Arxiv学术论文数据库"
        self.parameters = [
            ToolParameter(
                name="query",
                type="string",
                description="搜索关键词",
                required=True
            )
        ]
    
    async def execute(self, query: str, **kwargs):
        # 执行搜索逻辑
        ...
```

### 2. Agent工作流核心逻辑

**ResearchAgent** (`backend/agent/research_agent.py`):

```python
class ResearchAgent:
    SYSTEM_PROMPT = """你是一个资深人工智能研究员..."""
    
    async def run(self, user_query: str):
        # 初始化对话历史
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ]
        
        # 迭代执行
        while iteration < self.max_iterations:
            # 调用LLM
            llm_response = await self.llm_client.chat_completion(
                messages=messages,
                tools=self.tool_definitions
            )
            
            # 执行工具调用
            if llm_response["tool_calls"]:
                for tool_call in llm_response["tool_calls"]:
                    result = await self.execute_tool(...)
                    messages.append(result)
            else:
                break  # 任务完成
```

### 3. 异步并发处理

**LLMClient** (`backend/agent/llm_client.py`):

```python
async def batch_chat_completion(
    self,
    messages_list: List[List[Dict[str, str]]],
    max_concurrent: int = 5
):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def limited_chat_completion(messages):
        async with semaphore:
            return await self.chat_completion(messages)
    
    tasks = [limited_chat_completion(m) for m in messages_list]
    results = await asyncio.gather(*tasks)
    return results
```

## 项目结构

```
llm_agent_project/
├── README.md                    # 项目说明
├── USAGE.md                     # 使用文档（本文件）
├── requirements.txt             # Python依赖
├── config/
│   ├── config.example.yaml     # 配置模板
│   └── config.yaml             # 实际配置（需创建）
├── backend/
│   ├── main.py                 # FastAPI后端服务
│   ├── config_loader.py        # 配置加载
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── llm_client.py       # LLM API客户端
│   │   └── research_agent.py   # Agent核心逻辑
│   └── tools/
│       ├── __init__.py
│       ├── base_tool.py        # 工具基类
│       ├── arxiv_tool.py       # Arxiv检索工具
│       ├── web_scraper_tool.py # 网页抓取工具
│       └── report_generator_tool.py  # 报告生成工具
├── frontend/
│   └── app.py                  # Streamlit前端界面
├── reports/                    # 生成的报告目录
└── logs/                       # 日志目录
```

## API接口文档

### 后端API端点

#### 1. 健康检查

```
GET /health
```

#### 2. 处理查询

```
POST /query
Content-Type: application/json

{
  "query": "帮我调研2026年关于DPO算法的最新进展",
  "max_iterations": 10
}
```

#### 3. 列出工具

```
GET /tools
```

## 检查要求对照

### ✅ 工具调用（Function Calling）

- [x] API声明代码：`backend/tools/base_tool.py` - `get_definition()`方法
- [x] 本地执行逻辑：每个工具的`execute()`方法
- [x] 至少2个外部工具：ArxivSearchTool、WebScraperTool、ReportGeneratorTool

### ✅ Agent工作流核心代码

- [x] System Prompt模板：`backend/agent/research_agent.py` - `SYSTEM_PROMPT`
- [x] 多步推理逻辑：`ResearchAgent.run()`方法
- [x] 工具调用流程：完整的迭代执行循环

### ✅ 应用界面及执行日志

- [x] 前端界面：`frontend/app.py` - Streamlit应用
- [x] 执行日志展示：详细的步骤追踪和可视化
- [x] 思考链路追踪：每个步骤的类型、描述、耗时、详情

## 注意事项

1. **API密钥安全**: 不要将包含真实API密钥的`config.yaml`提交到版本控制
2. **网络连接**: 确保能够访问LLM API和Arxiv
3. **依赖安装**: 某些依赖可能需要额外的系统库（如lxml）
4. **并发限制**: 根据API提供商的限制调整并发数

## 故障排除

### 问题1: 无法连接后端服务

- 确保后端服务已启动
- 检查端口8000是否被占用

### 问题2: API调用失败

- 检查API密钥是否正确
- 确认API额度是否充足
- 检查网络连接

### 问题3: 工具执行失败

- 查看执行日志中的错误信息
- 检查工具参数是否正确

## 扩展开发

### 添加新工具

1. 在`backend/tools/`创建新工具文件
2. 继承`BaseTool`类
3. 实现`execute()`方法
4. 在`ResearchAgent`中注册工具

### 自定义System Prompt

编辑`backend/agent/research_agent.py`中的`SYSTEM_PROMPT`

### 调整并发参数

编辑`config/config.yaml`中的`concurrency`配置

## 技术支持

如有问题，请查看：

- 执行日志中的详细错误信息
- 后端服务的控制台输出
- API提供商的文档

