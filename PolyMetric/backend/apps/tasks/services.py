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
            model_lower = model_name.lower()
            # [Fix] 针对生图模型，直接使用 images.generate 接口，避开网关对 chat 接口的字符串校验
            if any(k in model_lower for k in ["wanx", "cogview", "seedream"]):
                try:
                    client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)
                    response = client.images.generate(
                        model=model_name,
                        prompt=prompt,
                        n=1,
                        # 部分模型可能需要特定尺寸，此处先使用默认
                    )
                    image_url = response.data[0].url
                    if image_url:
                        return _save_remote_image(image_url)
                    raise Exception("No image URL returned from SDK")
                except Exception as e:
                    logger.warning(f"T2I SDK call failed: {e}. Trying raw request as fallback.")
                    # 如果 SDK 调用也失败，尝试之前的原生 requests 方式
                    headers = {
                        "Authorization": f"Bearer {settings.LLM_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "model": model_name,
                        "messages": messages,
                        "stream": False
                    }
                    base = settings.LLM_BASE_URL.rstrip('/')
                    if not base.endswith('/v1'):
                         base += '/v1'
                    url = f"{base}/chat/completions"

                    resp = requests.post(url, json=payload, headers=headers, timeout=120)
                    content_type = resp.headers.get("Content-Type", "")
                    
                    if "application/json" in content_type:
                        data = resp.json()
                        if 'error' in data:
                            raise Exception(f"API Error: {data['error'].get('message', 'Unknown error')}")
                            
                        content = data['choices'][0]['message']['content']
                        if isinstance(content, list):
                            for part in content:
                                if isinstance(part, dict) and 'url' in part:
                                    return _save_remote_image(part['url'])
                        return str(content)
                    
                    resp.raise_for_status()
                    return _save_remote_image(url) # 兜底

            client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)

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
