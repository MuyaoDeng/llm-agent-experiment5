"""
基础工具类定义
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """工具参数定义"""
    name: str
    type: str
    description: str
    required: bool = True
    enum: List[str] = None


class ToolDefinition(BaseModel):
    """工具定义（Function Calling格式）"""
    name: str
    description: str
    parameters: Dict[str, Any]


class BaseTool(ABC):
    """工具基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = ""
        self.parameters = []
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行工具
        
        Returns:
            Dict包含:
            - success: bool
            - data: Any
            - error: str (如果失败)
            - execution_time: float
        """
        pass
    
    def get_definition(self) -> Dict[str, Any]:
        """
        获取工具的Function Calling定义
        
        Returns:
            符合OpenAI Function Calling格式的工具定义
        """
        properties = {}
        required = []
        
        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description
            }
            if param.enum:
                prop["enum"] = param.enum
            
            properties[param.name] = prop
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
