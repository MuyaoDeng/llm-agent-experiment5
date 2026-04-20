"""
LLM API客户端
"""
import asyncio
import time
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


class LLMClient:
    """LLM API客户端（支持DeepSeek等兼容OpenAI格式的API）"""
    
    def __init__(self, api_key: str, base_url: str, model: str, max_tokens: int = 4096, temperature: float = 0.7):
        """
        初始化LLM客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
        """
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto"
    ) -> Dict[str, Any]:
        """
        调用聊天补全API
        
        Args:
            messages: 消息列表
            tools: 工具定义列表
            tool_choice: 工具选择策略
            
        Returns:
            API响应结果
        """
        start_time = time.time()
        
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = tool_choice
            
            response = await self.client.chat.completions.create(**kwargs)
            
            execution_time = time.time() - start_time
            
            # 解析响应
            message = response.choices[0].message
            
            result = {
                "success": True,
                "content": message.content,
                "tool_calls": [],
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "execution_time": execution_time
            }
            
            # 处理工具调用
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    result["tool_calls"].append({
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    async def batch_chat_completion(
        self,
        messages_list: List[List[Dict[str, str]]],
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        批量并发调用聊天补全API
        
        Args:
            messages_list: 多个消息列表
            max_concurrent: 最大并发数
            
        Returns:
            API响应结果列表
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_chat_completion(messages):
            async with semaphore:
                return await self.chat_completion(messages)
        
        tasks = [limited_chat_completion(messages) for messages in messages_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "index": i
                })
            else:
                processed_results.append(result)
        
        return processed_results
