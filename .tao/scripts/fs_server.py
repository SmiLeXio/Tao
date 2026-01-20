# /// script
# dependencies = [
#   "mcp[cli]",
#   "pandas",
#   "openpyxl",
#   "xmindparser",
# ]
# ///
import os
import glob
import subprocess
import pandas as pd
from xmindparser import xmind_to_dict
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP
mcp = FastMCP("Tao-Core-Tools")

@mcp.tool()
def process_excel(path: str, action: str = "read") -> str:
    """处理 Excel 文件。action 可以是 'read' (读取摘要) 或 'info' (获取结构)"""
    try:
        abs_path = os.path.abspath(path)
        if action == "read":
            df = pd.read_excel(abs_path)
            return df.head(10).to_string()
        elif action == "info":
            df = pd.read_excel(abs_path)
            return f"工作表信息: {df.columns.tolist()}, 总行数: {len(df)}"
        return "未知操作"
    except Exception as e:
        return f"Excel 处理失败: {str(e)}"

@mcp.tool()
def convert_document(input_path: str, output_format: str) -> str:
    """使用 Pandoc 转换文档格式。例如将 .md 转换为 .docx"""
    try:
        input_abs = os.path.abspath(input_path)
        output_path = os.path.splitext(input_abs)[0] + f".{output_format}"
        subprocess.run(["pandoc", input_abs, "-o", output_path], check=True)
        return f"转换成功: {output_path}"
    except Exception as e:
        return f"Pandoc 转换失败: {str(e)}。请确保系统中已安装 Pandoc。"

@mcp.tool()
def video_info(path: str) -> str:
    """获取视频文件信息 (需安装 FFmpeg)"""
    try:
        abs_path = os.path.abspath(path)
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_format", "-show_streams", abs_path],
            capture_output=True, text=True
        )
        return result.stdout
    except Exception as e:
        return f"FFmpeg 获取信息失败: {str(e)}。请确保系统中已安装 FFmpeg。"

@mcp.tool()
def sequential_thinking(thought: str, step: int, total_steps: int) -> str:
    """顺序思考工具，用于拆解复杂问题。描述当前步骤、当前步数和总步数。"""
    return f"[思考进度 {step}/{total_steps}]: {thought}"

@mcp.tool()
def parse_xmind(path: str) -> str:
    """解析 Xmind 文件并返回其结构的 JSON 字符串"""
    try:
        abs_path = os.path.abspath(path)
        data = xmind_to_dict(abs_path)
        return str(data)
    except Exception as e:
        return f"Xmind 解析失败: {str(e)}"

@mcp.tool()
def save_to_excel(path: str, data: list[dict]) -> str:
    """将数据列表（字典数组）保存为 Excel 文件"""
    try:
        abs_path = os.path.abspath(path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        df = pd.DataFrame(data)
        df.to_excel(abs_path, index=False)
        return f"Excel 文件已成功保存至: {abs_path}"
    except Exception as e:
        return f"保存 Excel 失败: {str(e)}"

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
