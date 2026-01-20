# /// script
# dependencies = [
#   "mcp[cli]",
#   "openai",
#   "python-dotenv",
#   "requests"
# ]
# ///
import os
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化 FastMCP
mcp = FastMCP("Tao-Image-Gen")

@mcp.tool()
def generate_image(prompt: str, size: str = "1024x1024", quality: str = "standard", n: int = 1) -> str:
    """
    使用兼容 OpenAI 格式的 API (如 DALL-E 3 或 SiliconFlow Flux) 生成图片。
    
    配置优先顺序: 环境变量 > 默认值
    - IMAGE_GEN_API_KEY (或 OPENAI_API_KEY)
    - IMAGE_GEN_BASE_URL (默认: https://api.openai.com/v1)
    - IMAGE_GEN_MODEL (默认: dall-e-3)
    
    Args:
        prompt: 图片描述
        size: 图片尺寸 (默认 "1024x1024")
        quality: 图片质量 ("standard" 或 "hd")
        n: 生成数量 (默认 1)
        
    Returns:
        生成的图片 URL 或错误信息
    """
    api_key = os.getenv("IMAGE_GEN_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("IMAGE_GEN_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("IMAGE_GEN_MODEL", "dall-e-3")

    if not api_key:
        return "错误: 未找到 API Key。请设置 IMAGE_GEN_API_KEY 或 OPENAI_API_KEY 环境变量。"

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        # 准备参数
        params = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "n": n,
        }
        
        # 针对不同服务商的特殊处理
        if "dall-e" in model:
            params["quality"] = quality
            
        # 豆包/火山引擎 (Volcengine Ark) 通常使用 endpoint-id 作为 model
        # 且可能需要移除不支持的参数，并确保尺寸足够大
        if "ark.cn-beijing.volces.com" in base_url:
            # 某些 Ark 模型可能不支持 standard/hd 参数，安全起见移除
            if "quality" in params:
                del params["quality"]
            
            # Seedream 模型通常要求至少 3.6MP (如 2048x2048)
            # 如果请求的是默认的 1024x1024，自动升级为 2048x2048 以避免报错
            if params.get("size") == "1024x1024":
                params["size"] = "2048x2048"

        response = client.images.generate(**params)
        
        image_url = response.data[0].url
        return f"图片生成成功! URL: {image_url}"
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg and "ark.cn-beijing.volces.com" in base_url:
             return f"调用失败: 火山引擎(Doubao) 可能不支持通过 OpenAI 兼容接口 ({base_url}) 进行绘图，或者您的 Endpoint ID 填写错误。\n建议：\n1. 检查 .env 中的 IMAGE_GEN_MODEL 是否为 'ep-xxx' 格式的接入点 ID。\n2. 尝试使用 SiliconFlow (硅基流动) 的免费 Flux 服务代替 (兼容性更好)。\n\n原始错误: {error_msg}"
        return f"图片生成失败: {error_msg} (Base URL: {base_url}, Model: {model})"

@mcp.tool()
def download_image(url: str, save_path: str) -> str:
    """
    下载图片到本地。
    
    Args:
        url: 图片 URL
        save_path: 本地保存路径
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        abs_path = os.path.abspath(save_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        with open(abs_path, 'wb') as f:
            f.write(response.content)
            
        return f"图片已保存至: {abs_path}"
    except Exception as e:
        return f"图片下载失败: {str(e)}"

if __name__ == "__main__":
    mcp.run()
