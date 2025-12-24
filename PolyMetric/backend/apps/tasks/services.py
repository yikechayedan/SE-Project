# apps/tasks/services.py

from openai import OpenAI
from django.conf import settings
import time
import logging
import requests
import os
import uuid

logger = logging.getLogger(__name__)

def _save_remote_image(url):
    """从远程 URL 下载图片并保存到本地"""
    import requests
    import os
    import uuid
    from django.conf import settings
    
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        
        # 简单判断后缀
        content_type = r.headers.get("Content-Type", "")
        ext = ".png"
        if "jpeg" in content_type: ext = ".jpg"
        elif "webp" in content_type: ext = ".webp"
        
        filename = f"gen_{uuid.uuid4()}{ext}"
        save_dir = os.path.join(settings.MEDIA_ROOT, "generated_images")
        os.makedirs(save_dir, exist_ok=True)
        
        save_path = os.path.join(save_dir, filename)
        with open(save_path, "wb") as f:
            f.write(r.content)
            
        return f"![Generated Image](/media/generated_images/{filename})"
    except Exception as e:
        logger.error(f"Failed to download remote image {url}: {e}")
        return f"Error downloading image: {url}"

def call_llm_api(prompt: str, model_name: str, images: list = None, max_retries: int = 3):
    """
    使用 OpenAI SDK（Paratera 接入）
    images: list of base64 strings
    增强了错误处理和超时机制
    """
    import base64
    import httpx
    
    def get_mime_type(b64_str):
        try:
            data = base64.b64decode(b64_str[:32])
            if data.startswith(b'\x89PNG\r\n\x1a\n'): return "image/png"
            if data.startswith(b'\xff\xd8'): return "image/jpeg"
            if data.startswith(b'GIF87a') or data.startswith(b'GIF89a'): return "image/gif"
            if data.startswith(b'RIFF') and data[8:12] == b'WEBP': return "image/webp"
        except: pass
        return "image/jpeg" # 兜底

    backoff = 2
    
    # 检查prompt长度，避免过长导致API调用失败
    if len(prompt) > 10000:
        logger.warning(f"Prompt is too long ({len(prompt)} chars), truncating...")
        prompt = prompt[:9500] + "...[内容已截断]"
    
    if images:
        content_payload = [{"type": "text", "text": prompt}]
        for img_b64 in images:
            # 清理 Base64 字符串（移除可能存在的换行或空格）
            img_b64_clean = "".join(img_b64.split())
            mime = get_mime_type(img_b64_clean)
            content_payload.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime};base64,{img_b64_clean}",
                    "detail": "auto"
                }
            })
        messages = [{"role": "user", "content": content_payload}]
    else:
        messages = [{"role": "user", "content": prompt}]

    for attempt in range(max_retries + 1):
        try:
            # 增加超时时间，特别是对于CSV数据分析任务
            timeout = 120.0 if len(prompt) > 5000 else 60.0
            
            client = OpenAI(
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL,
                timeout=timeout,
                max_retries=0, # 我们自己在外层控制重试，禁用 SDK 内部重试以免混淆
                # 添加更多连接配置
                http_client=httpx.Client(
                    timeout=timeout,
                    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
                )
            )

            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                # 添加更多参数以提高稳定性
                temperature=0.1,  # 降低随机性
                max_tokens=1000,   # 限制输出长度
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")
                
            logger.info(f"LLM API success on attempt {attempt+1}")
            return content

        except Exception as e:
            error_str = str(e).lower()
            
            # 记录详细错误信息
            logger.error(f"LLM API error (Attempt {attempt+1}/{max_retries}): {e}")
            logger.error(f"Error type: {type(e).__name__}")
            
            if attempt < max_retries:
                # 根据错误类型调整重试时间
                if "timeout" in error_str or "read timeout" in error_str:
                    sleep_time = backoff * (2 ** attempt) * 2  # 超时错误等待更长时间
                elif "rate limit" in error_str or "too many requests" in error_str:
                    sleep_time = backoff * (3 ** attempt)  # 限流错误等待更长时间
                else:
                    sleep_time = backoff * (2 ** attempt)
                
                logger.warning(f"LLM API failed (Attempt {attempt+1}/{max_retries}). Retrying in {sleep_time}s... Error: {e}")
                time.sleep(sleep_time)
            else:
                logger.error(f"LLM API permanently failed after {max_retries} retries. Error: {e}")
                
                # 返回更详细的错误信息
                if "timeout" in error_str:
                    return "[Error] API调用超时，请检查网络连接或稍后重试"
                elif "connection" in error_str:
                    return "[Error] 网络连接失败，请检查网络设置"
                elif "rate limit" in error_str:
                    return "[Error] API调用频率超限，请稍后重试"
                elif "authentication" in error_str or "unauthorized" in error_str:
                    return "[Error] API认证失败，请检查API密钥"
                else:
                    return f"[Error] {str(e)}"
                
    return "[Error] Unknown failure"
