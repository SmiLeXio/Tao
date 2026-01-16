# /// script
# dependencies = [
#   "mcp[cli]",
# ]
# ///
import os
import glob
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP
mcp = FastMCP("LocalFilesystem")

@mcp.tool()
def list_directory(path: str) -> list[str]:
    """列出目录下的所有文件和文件夹"""
    try:
        # 转换路径为绝对路径并检查
        abs_path = os.path.abspath(path)
        return os.listdir(abs_path)
    except Exception as e:
        return [f"错误: {str(e)}"]

@mcp.tool()
def read_file(path: str) -> str:
    """读取文件内容"""
    try:
        abs_path = os.path.abspath(path)
        with open(abs_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"读取失败: {str(e)}"

@mcp.tool()
def write_file(path: str, content: str) -> str:
    """写入内容到文件"""
    try:
        abs_path = os.path.abspath(path)
        # 确保目录存在
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"成功写入到: {abs_path}"
    except Exception as e:
        return f"写入失败: {str(e)}"

@mcp.tool()
def search_files(directory: str, pattern: str) -> list[str]:
    """在指定目录中按模式搜索文件 (例如: *.py)"""
    try:
        search_path = os.path.join(directory, "**", pattern)
        return glob.glob(search_path, recursive=True)
    except Exception as e:
        return [f"搜索出错: {str(e)}"]

if __name__ == "__main__":
    # 运行服务器
    mcp.run()
