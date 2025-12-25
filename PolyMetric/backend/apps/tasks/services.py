# apps/tasks/services.py

from openai import OpenAI
from django.conf import settings
import time
import logging
import requests
import os
import uuid

logger = logging.getLogger(__name__)

# ===================== 生图模型识别关键字 =====================
# 只要模型名称包含以下任一关键字（不区分大小写），系统将自动切换至生图接口
IMAGE_GEN_MODEL_KEYWORDS = ["wanx", "cogview", "seedream"]
# ============================================================

def load_generated_image_as_base64(relative_path):
    """
    加载由模型生成的本地图片并转换为 Base64。
    relative_path 格式通常为: generated_images/filename.png
    """
    import base64
    from django.conf import settings
    
    if not relative_path: return None
    
    try:
        # 去除可能存在的 markdown 格式头部 ![...](...)
        path = relative_path
        if "![" in path and "(" in path and ")" in path:
            path = path.split("(")[1].split(")")[0]
        
        # 去除开头的 /media/
        if path.startswith("/media/"):
            path = path.replace("/media/", "", 1)
            
        full_path = os.path.join(settings.MEDIA_ROOT, path)
        
        if os.path.exists(full_path):
            with open(full_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        else:
            logger.error(f"Generated image not found at: {full_path}")
    except Exception as e:
        logger.error(f"Error loading generated image: {e}")
    return None

def load_image_from_dataset(dataset_file_path, image_relative_path):
    """
    从数据集（通常是 ZIP）中加载图片并转换为 Base64
    """
    import zipfile
    import io
    import base64
    from django.conf import settings

    if not dataset_file_path or not image_relative_path:
        return None

    try:
        # 补全绝对路径
        if not os.path.isabs(str(dataset_file_path)):
            full_path = os.path.join(settings.MEDIA_ROOT, str(dataset_file_path))
        else:
            full_path = str(dataset_file_path)

        if not os.path.exists(full_path):
            logger.error(f"Dataset file not found: {full_path}")
            return None

        # 如果是 ZIP 文件
        if str(full_path).lower().endswith('.zip'):
            with zipfile.ZipFile(full_path, 'r') as zf:
                # 统一路径分隔符为正斜杠，并去除可能的开头斜杠
                target_path = image_relative_path.replace('\\', '/').lstrip('/')
                
                # 在 ZIP 中搜索文件
                if target_path in zf.namelist():
                    with zf.open(target_path) as f:
                        return base64.b64encode(f.read()).decode('utf-8')
                else:
                    # 尝试模糊匹配（处理有些 ZIP 内部带一层文件夹的情况）
                    for name in zf.namelist():
                        if name.endswith(target_path):
                            with zf.open(name) as f:
                                return base64.b64encode(f.read()).decode('utf-8')
        
        # 如果是普通图片文件（用于兼容性）
        elif any(str(full_path).lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
            with open(full_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')

    except Exception as e:
        logger.error(f"Error loading image from dataset: {e}")
    
    return None

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
        import base64
        try:
            # 彻底清洗：剥离可能存在的 data 头部并移除所有空白符
            s = b64_str.strip()
            if "," in s: s = s.split(",")[-1]
            s = "".join(s.split())
            
            # 自动补齐 Base64 填充
            missing_padding = len(s) % 4
            if missing_padding:
                s += "=" * (4 - missing_padding)
                
            data = base64.b64decode(s[:64])
            if data.startswith(b'\x89PNG\r\n\x1a\n'): return "image/png"
            if data.startswith(b'\xff\xd8'): return "image/jpeg"
            if data.startswith(b'GIF87a') or data.startswith(b'GIF89a'): return "image/gif"
            if data.startswith(b'RIFF') and data[8:12] == b'WEBP': return "image/webp"
            if b'JFIF' in data or b'Exif' in data: return "image/jpeg"
        except Exception as e:
            logger.error(f"MIME detection error: {e}")
        return "image/jpeg"

    backoff = 2
    
    # ... (此处省略逻辑，位置由 old_string 确定)
    
    if images:
        # [Verify] 记录图片发送情况
        logger.info(f"Sending LLM request to {model_name} with {len(images)} images and prompt length {len(prompt)}")
        content_payload = [{"type": "text", "text": prompt}]
        for img_b64 in images:
            # [Fix] 深度清理 Base64 字符串，确保网关能正确解析
            clean_b64 = img_b64.strip()
            if "," in clean_b64:
                clean_b64 = clean_b64.split(",")[-1]
            clean_b64 = "".join(clean_b64.split())
            
            # 补齐长度
            pad_needed = len(clean_b64) % 4
            if pad_needed:
                clean_b64 += "=" * (4 - pad_needed)
            
            mime = get_mime_type(clean_b64)
            content_payload.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime};base64,{clean_b64}",
                    "detail": "auto"
                }
            })
        messages = [{"role": "user", "content": content_payload}]
    else:
        messages = [{"role": "user", "content": prompt}]

    for attempt in range(max_retries + 1):
        try:
            model_lower = model_name.lower()
            # [Fix] 使用外部定义的关键字列表进行识别
            is_t2i_model = any(k in model_lower for k in IMAGE_GEN_MODEL_KEYWORDS)
            
            if is_t2i_model:
                # ========================== WanX 系列特殊处理 ==========================
                if "wanx" in model_lower:
                    try:
                        logger.info(f"Routing {model_name} to WanX specialized async endpoint.")
                        base_url = settings.LLM_BASE_URL.rstrip('/')
                        # 确保不包含 /v1 后缀，以便手动拼接 /v1/p003
                        if base_url.endswith('/v1'):
                            base_url = base_url[:-3]
                        
                        headers = {
                            "Authorization": f"Bearer {settings.LLM_API_KEY}",
                            "Content-Type": "application/json"
                        }
                        
                        # 第一步：发送生成请求
                        gen_url = f"{base_url}/v1/p003/text2image"
                        payload = {
                            "model": model_name,
                            "input": {"prompt": prompt},
                            "parameters": {"size": "1024*1024", "n": 1}
                        }
                        
                        gen_resp = requests.post(gen_url, headers=headers, json=payload, timeout=30)
                        gen_resp.raise_for_status()
                        gen_data = gen_resp.json()
                        
                        task_id = gen_data.get("output", {}).get("task_id")
                        if not task_id:
                            raise Exception(f"WanX task creation failed: {gen_data}")
                            
                        # 第二步：轮询任务结果
                        poll_url = f"{base_url}/v1/p003/tasks/{task_id}"
                        max_polls = 15 # 最大轮询次数
                        poll_interval = 3 # 轮询间隔(秒)
                        
                        for i in range(max_polls):
                            time.sleep(poll_interval)
                            poll_resp = requests.get(poll_url, headers=headers, timeout=20)
                            poll_resp.raise_for_status()
                            poll_data = poll_resp.json()
                            
                            status = poll_data.get("output", {}).get("task_status")
                            logger.info(f"WanX Task {task_id} status: {status}")
                            
                            if status == "SUCCEEDED":
                                results = poll_data.get("output", {}).get("results", [])
                                if results and "url" in results[0]:
                                    return _save_remote_image(results[0]["url"])
                                break
                            elif status == "FAILED":
                                raise Exception(f"WanX task failed: {poll_data}")
                        
                        raise Exception("WanX task polling timed out")
                    except Exception as e:
                        logger.error(f"WanX specialized call failed: {e}")
                        # 万象不支持标准 SDK 路径，这里不继续 fallback 到 SDK，直接抛错以便进入重试
                        raise e

                # ========================== 其他生图模型 (GLM, Doubao 等) ==========================
                else:
                    try:
                        logger.info(f"Routing {model_name} to standard OpenAI-compatible T2I endpoint.")
                        client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)
                        # [Fix] 显式增加 size 参数，某些模型（如 WanX）在缺失规格参数时可能返回空结果
                        response = client.images.generate(
                            model=model_name,
                            prompt=prompt,
                            n=1,
                            size="1024x1024" 
                        )
                        # [Fix] 增加长度校验，防止 list index out of range
                        if hasattr(response, 'data') and len(response.data) > 0:
                            image_url = response.data[0].url
                            if image_url:
                                return _save_remote_image(image_url)
                        
                        logger.error(f"T2I Response structure unexpected or empty: {response}")
                        raise Exception(f"No image data in successful 200 response from {model_name}")
                    except Exception as e:
                        logger.warning(f"T2I SDK call failed for {model_name}: {e}. Trying raw request fallback.")
                        # 只有在 SDK 明确报错后才尝试 raw 模式，且 raw 模式下也要处理可能的 URL 列表
                        headers = {"Authorization": f"Bearer {settings.LLM_API_KEY}", "Content-Type": "application/json"}
                        payload = {"model": model_name, "messages": messages, "stream": False}
                        base = settings.LLM_BASE_URL.rstrip('/')
                        if not base.endswith('/v1'): base += '/v1'
                        
                        # 尝试 chat 接口但手动解析 content 列表 (针对万一网关没拦截但返回 list 的情况)
                        resp = requests.post(f"{base}/chat/completions", json=payload, headers=headers, timeout=120)
                        if resp.status_code == 200:
                            data = resp.json()
                            content = data['choices'][0]['message']['content']
                            if isinstance(content, list):
                                for part in content:
                                    if isinstance(part, dict) and 'url' in part:
                                        return _save_remote_image(part['url'])
                            return str(content)
                        raise e # 如果还是不行，抛出原始 SDK 错误

            # 正常文本模型逻辑
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
