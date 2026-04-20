"""
网页内容抓取工具
"""
import time
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Any
from .base_tool import BaseTool, ToolParameter


class WebScraperTool(BaseTool):
    """网页内容抓取工具"""
    
    def __init__(self, timeout: int = 30):
        super().__init__()
        self.description = "抓取指定URL的网页内容，提取正文文本信息"
        self.timeout = timeout
        
        self.parameters = [
            ToolParameter(
                name="url",
                type="string",
                description="要抓取的网页URL",
                required=True
            ),
            ToolParameter(
                name="extract_type",
                type="string",
                description="提取内容类型",
                required=False,
                enum=["text", "html", "title"]
            )
        ]
    
    async def execute(self, url: str, extract_type: str = "text") -> Dict[str, Any]:
        """
        执行网页抓取
        
        Args:
            url: 网页URL
            extract_type: 提取类型（text/html/title）
            
        Returns:
            包含网页内容的字典
        """
        start_time = time.time()
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=self.timeout) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}: {response.reason}")
                    
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'lxml')
                    
                    # 移除script和style标签
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    result_data = {}
                    
                    if extract_type == "text" or extract_type == "all":
                        # 提取纯文本
                        text = soup.get_text(separator='\n', strip=True)
                        # 清理多余空行
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        result_data["text"] = '\n'.join(lines)
                    
                    if extract_type == "html" or extract_type == "all":
                        result_data["html"] = str(soup)
                    
                    if extract_type == "title" or extract_type == "all":
                        title = soup.find('title')
                        result_data["title"] = title.string if title else ""
                    
                    # 提取元数据
                    result_data["url"] = url
                    result_data["status_code"] = response.status
                    
                    execution_time = time.time() - start_time
                    
                    return {
                        "success": True,
                        "data": result_data,
                        "execution_time": execution_time
                    }
                    
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
