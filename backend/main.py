"""
后端主程序 - FastAPI服务
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_loader import ConfigLoader
from agent import LLMClient, ResearchAgent

# 创建FastAPI应用
app = FastAPI(
    title="研究智能体API",
    description="基于云端LLM API的Agent工具系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
config_loader = None
research_agent = None


class LLMConfig(BaseModel):
    """LLM配置模型"""
    api_key: str
    base_url: str
    model: str
    max_tokens: Optional[int] = 4096
    temperature: Optional[float] = 0.7


class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str
    max_iterations: Optional[int] = 10
    llm_config: Optional[LLMConfig] = None


class QueryResponse(BaseModel):
    """查询响应模型"""
    success: bool
    final_response: Optional[str] = None
    execution_log: dict
    iterations: int
    error: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    global config_loader, research_agent
    
    try:
        # 尝试加载配置文件（可选）
        try:
            config_loader = ConfigLoader()
            llm_config = config_loader.get_llm_config()
            llm_client = LLMClient(
                api_key=llm_config['api_key'],
                base_url=llm_config['base_url'],
                model=llm_config['model'],
                max_tokens=llm_config.get('max_tokens', 4096),
                temperature=llm_config.get('temperature', 0.7)
            )
            research_agent = ResearchAgent(llm_client)
            print("[OK] Backend service started with config file")
            print(f"[Model] {llm_config['model']}")
            print(f"[API] {llm_config['base_url']}")
        except (FileNotFoundError, ValueError) as e:
            # 配置文件不存在或无效，使用前端动态配置模式
            print("[INFO] Config file not found or invalid, using dynamic configuration mode")
            print("[INFO] Please provide LLM config through frontend interface")
            research_agent = None
        
        print("[OK] Backend service started successfully")
        
    except Exception as e:
        print(f"[ERROR] Startup failed: {str(e)}")
        raise


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "研究智能体API服务",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "agent_ready": research_agent is not None
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    处理用户查询
    
    Args:
        request: 查询请求
        
    Returns:
        查询响应
    """
    try:
        # 如果提供了LLM配置，使用动态配置创建新的agent
        if request.llm_config:
            # 创建临时LLM客户端
            temp_llm_client = LLMClient(
                api_key=request.llm_config.api_key,
                base_url=request.llm_config.base_url,
                model=request.llm_config.model,
                max_tokens=request.llm_config.max_tokens,
                temperature=request.llm_config.temperature
            )
            # 创建临时agent
            temp_agent = ResearchAgent(temp_llm_client, max_iterations=request.max_iterations)
            result = await temp_agent.run(request.query)
        else:
            # 使用默认的全局agent
            if research_agent is None:
                raise HTTPException(status_code=500, detail="智能体未初始化")
            result = await research_agent.run(request.query)
        
        return QueryResponse(
            success=result["success"],
            final_response=result.get("final_response"),
            execution_log=result["execution_log"],
            iterations=result["iterations"]
        )
        
    except Exception as e:
        return QueryResponse(
            success=False,
            final_response=None,
            execution_log={"error": str(e)},
            iterations=0,
            error=str(e)
        )


@app.get("/tools")
async def list_tools():
    """列出可用工具"""
    if research_agent is None:
        raise HTTPException(status_code=500, detail="智能体未初始化")
    
    tools_info = []
    for tool_name, tool in research_agent.tools.items():
        tools_info.append({
            "name": tool_name,
            "description": tool.description,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required
                }
                for p in tool.parameters
            ]
        })
    
    return {"tools": tools_info}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
