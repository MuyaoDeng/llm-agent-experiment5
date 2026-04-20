"""
Markdown报告生成工具
"""
import time
import os
from datetime import datetime
from typing import Dict, Any
from .base_tool import BaseTool, ToolParameter


class ReportGeneratorTool(BaseTool):
    """Markdown报告生成工具"""
    
    def __init__(self, output_dir: str = "reports"):
        super().__init__()
        self.description = "生成结构化的Markdown格式研究报告并保存到本地文件"
        self.output_dir = output_dir
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        self.parameters = [
            ToolParameter(
                name="title",
                type="string",
                description="报告标题",
                required=True
            ),
            ToolParameter(
                name="content",
                type="string",
                description="报告主体内容（Markdown格式）",
                required=True
            ),
            ToolParameter(
                name="filename",
                type="string",
                description="文件名（不含扩展名），如不提供则自动生成",
                required=False
            )
        ]
    
    async def execute(self, title: str, content: str, filename: str = None) -> Dict[str, Any]:
        """
        生成并保存Markdown报告
        
        Args:
            title: 报告标题
            content: 报告内容
            filename: 文件名
            
        Returns:
            包含文件路径的字典
        """
        start_time = time.time()
        
        try:
            # 生成文件名
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"report_{timestamp}"
            
            # 确保文件名安全
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()
            filepath = os.path.join(self.output_dir, f"{filename}.md")
            
            # 构建完整报告
            report_content = f"""# {title}

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

{content}

---

*本报告由AI智能体自动生成*
"""
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "data": {
                    "filepath": filepath,
                    "filename": f"{filename}.md",
                    "title": title,
                    "size": len(report_content)
                },
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
