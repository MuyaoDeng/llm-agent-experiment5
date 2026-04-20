"""
研究智能体核心逻辑
"""
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from .llm_client import LLMClient
import sys
import os
# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import ArxivSearchTool, WebScraperTool, ReportGeneratorTool


class ExecutionLog:
    """执行日志记录"""
    
    def __init__(self):
        self.steps = []
        self.start_time = datetime.now()
    
    def add_step(self, step_type: str, description: str, details: Dict[str, Any], execution_time: float = 0):
        """添加执行步骤"""
        self.steps.append({
            "step_number": len(self.steps) + 1,
            "timestamp": datetime.now().isoformat(),
            "type": step_type,
            "description": description,
            "details": details,
            "execution_time": execution_time
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        total_time = (datetime.now() - self.start_time).total_seconds()
        return {
            "total_steps": len(self.steps),
            "total_time": total_time,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "steps": self.steps
        }


class ResearchAgent:
    """研究智能体 - 具备自主思考与工具调用能力"""
    
    # System Prompt - 定义Agent的角色和能力
    SYSTEM_PROMPT = """你是一个资深人工智能研究员，擅长收集文献并撰写综述报告。

你的能力：
1. 使用ArxivSearchTool搜索学术论文
2. 使用WebScraperTool抓取网页内容
3. 使用ReportGeneratorTool生成Markdown格式的研究报告

工作流程：
1. 分析用户的研究需求，明确研究主题和关键词
2. 规划调研步骤（例如：搜索论文 -> 分析摘要 -> 提取关键信息 -> 生成报告）
3. 调用合适的工具执行每个步骤
4. 汇总信息并生成结构化的研究报告

注意事项：
- 使用清晰的思考链路（Chain-of-Thought）
- 每次工具调用都要说明原因和预期结果
- 提取的信息要准确、完整
- 生成的报告要结构清晰、内容丰富"""
    
    def __init__(self, llm_client: LLMClient, max_iterations: int = 10):
        """
        初始化研究智能体
        
        Args:
            llm_client: LLM客户端
            max_iterations: 最大迭代次数
        """
        self.llm_client = llm_client
        self.max_iterations = max_iterations
        
        # 初始化工具
        self.tools = {
            "ArxivSearchTool": ArxivSearchTool(),
            "WebScraperTool": WebScraperTool(),
            "ReportGeneratorTool": ReportGeneratorTool()
        }
        
        # 获取工具定义
        self.tool_definitions = [tool.get_definition() for tool in self.tools.values()]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
        
        tool = self.tools[tool_name]
        return await tool.execute(**arguments)
    
    async def run(self, user_query: str) -> Dict[str, Any]:
        """
        运行智能体
        
        Args:
            user_query: 用户查询
            
        Returns:
            包含最终结果和执行日志的字典
        """
        execution_log = ExecutionLog()
        
        # 初始化对话历史
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ]
        
        execution_log.add_step(
            "user_query",
            "接收用户查询",
            {"query": user_query}
        )
        
        iteration = 0
        final_response = None
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # 调用LLM
            execution_log.add_step(
                "llm_thinking",
                f"第{iteration}轮：LLM思考中...",
                {"iteration": iteration}
            )
            
            llm_response = await self.llm_client.chat_completion(
                messages=messages,
                tools=self.tool_definitions,
                tool_choice="auto"
            )
            
            if not llm_response["success"]:
                execution_log.add_step(
                    "error",
                    "LLM调用失败",
                    {"error": llm_response["error"]},
                    llm_response.get("execution_time", 0)
                )
                break
            
            execution_log.add_step(
                "llm_response",
                f"LLM响应（耗时{llm_response['execution_time']:.2f}秒）",
                {
                    "content": llm_response["content"],
                    "tool_calls": llm_response["tool_calls"],
                    "usage": llm_response["usage"]
                },
                llm_response["execution_time"]
            )
            
            # 将LLM响应添加到消息历史
            assistant_message = {
                "role": "assistant",
                "content": llm_response["content"]
            }
            
            if llm_response["tool_calls"]:
                assistant_message["tool_calls"] = llm_response["tool_calls"]
            
            messages.append(assistant_message)
            
            # 如果没有工具调用，说明任务完成
            if not llm_response["tool_calls"]:
                final_response = llm_response["content"]
                execution_log.add_step(
                    "completion",
                    "任务完成",
                    {"final_response": final_response}
                )
                break
            
            # 执行工具调用
            for tool_call in llm_response["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                try:
                    arguments = json.loads(tool_call["function"]["arguments"])
                except json.JSONDecodeError:
                    arguments = {}
                
                execution_log.add_step(
                    "tool_call",
                    f"调用工具：{tool_name}",
                    {
                        "tool": tool_name,
                        "arguments": arguments
                    }
                )
                
                # 执行工具
                tool_result = await self.execute_tool(tool_name, arguments)
                
                execution_log.add_step(
                    "tool_result",
                    f"工具执行结果（耗时{tool_result.get('execution_time', 0):.2f}秒）",
                    {
                        "tool": tool_name,
                        "success": tool_result["success"],
                        "result": tool_result.get("data") if tool_result["success"] else tool_result.get("error")
                    },
                    tool_result.get("execution_time", 0)
                )
                
                # 将工具结果添加到消息历史
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
        
        if iteration >= self.max_iterations:
            execution_log.add_step(
                "max_iterations",
                "达到最大迭代次数",
                {"iterations": iteration}
            )
        
        return {
            "success": final_response is not None,
            "final_response": final_response,
            "execution_log": execution_log.get_summary(),
            "iterations": iteration
        }
