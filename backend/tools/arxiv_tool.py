"""
Arxiv论文检索工具
"""
import time
import arxiv
from typing import Dict, Any, List
from .base_tool import BaseTool, ToolParameter

class ArxivSearchTool(BaseTool):
    """Arxiv论文检索工具"""
    
    def __init__(self, max_results: int = 10):
        super().__init__()
        self.description = "搜索Arxiv学术论文数据库，获取最新研究论文的标题、摘要、作者等信息"
        self.max_results = max_results
        
        self.parameters = [
            ToolParameter(
                name="query",
                type="string",
                description="搜索关键词，例如：'DPO algorithm', 'reinforcement learning'",
                required=True
            ),
            ToolParameter(
                name="max_results",
                type="integer",
                description=f"返回的最大结果数量，默认{max_results}",
                required=False
            ),
            ToolParameter(
                name="sort_by",
                type="string",
                description="排序方式",
                required=False,
                enum=["relevance", "lastUpdatedDate", "submittedDate"]
            )
        ]
    
    async def execute(self, query: str, max_results: int = None, sort_by: str = "relevance") -> Dict[str, Any]:
        """
        执行Arxiv搜索
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            sort_by: 排序方式
            
        Returns:
            包含论文列表的字典
        """
        start_time = time.time()
        
        try:
            # 设置排序方式
            sort_criterion = arxiv.SortCriterion.Relevance
            if sort_by == "lastUpdatedDate":
                sort_criterion = arxiv.SortCriterion.LastUpdatedDate
            elif sort_by == "submittedDate":
                sort_criterion = arxiv.SortCriterion.SubmittedDate
            
            # 执行搜索
            search = arxiv.Search(
                query=query,
                max_results=max_results or self.max_results,
                sort_by=sort_criterion
            )
            
            papers = []
            for result in search.results():
                paper = {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "published": result.published.strftime("%Y-%m-%d"),
                    "updated": result.updated.strftime("%Y-%m-%d"),
                    "pdf_url": result.pdf_url,
                    "entry_id": result.entry_id,
                    "categories": result.categories,
                    "primary_category": result.primary_category
                }
                papers.append(paper)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "data": {
                    "query": query,
                    "total_results": len(papers),
                    "papers": papers
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
