# apps/tasks/services.py

from openai import OpenAI
from django.conf import settings
import time
import logging

logger = logging.getLogger(__name__)

def call_llm_api(prompt: str, model_name: str, images: list = None, max_retries: int = 3):
    """
    使用 OpenAI SDK（Paratera 接入）
    images: list of base64 strings
    """
    import base64
    
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
            client = OpenAI(
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL,
                timeout=60.0,  # [Fix] 设置 60秒 超时，防止 Worker 卡死
                max_retries=0, # 我们自己在外层控制重试，禁用 SDK 内部重试以免混淆
            )

            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")
                
            return content

        except Exception as e:
            if attempt < max_retries:
                sleep_time = backoff * (2 ** attempt)
                logger.warning(f"LLM API failed (Attempt {attempt+1}/{max_retries}). Retrying in {sleep_time}s... Error: {e}")
                time.sleep(sleep_time)
            else:
                logger.error(f"LLM API permanently failed after {max_retries} retries. Error: {e}")
                return f"[Error] {str(e)}"
                
    return "[Error] Unknown failure"
