# /// script
# dependencies = [
#   "mcp[cli]",
#   "tavily-python",
# ]
# ///
import os
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient

# 初始化 FastMCP
mcp = FastMCP("Tao-Search")

# 从环境变量获取 API Key
def get_tavily_client():
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return None
    return TavilyClient(api_key=api_key)

@mcp.tool()
def search_internet(query: str, search_depth: str = "smart") -> str:
    """使用 Tavily 在互联网上搜索信息。search_depth 可选 'basic' 或 'smart'。"""
    client = get_tavily_client()
    if not client:
        return "错误: 未配置 TAVILY_API_KEY 环境变量。"
    
    try:
        response = client.search(query=query, search_depth=search_depth)
        results = response.get("results", [])
        if not results:
            return "未找到相关结果。"
        
        output = []
        for res in results[:5]: # 取前5个结果
            output.append(f"标题: {res['title']}\n链接: {res['url']}\n摘要: {res['content']}\n")
        return "\n---\n".join(output)
    except Exception as e:
        return f"搜索出错: {str(e)}"

if __name__ == "__main__":
    mcp.run()
