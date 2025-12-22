# apps/tasks/services.py

from openai import OpenAI
from django.conf import settings
import time
import logging

logger = logging.getLogger(__name__)

def call_llm_api(prompt: str, model_name: str, max_retries: int = 3):
    """
    使用 OpenAI SDK（Paratera 接入）
    增加重试机制和退避策略
    """
    backoff = 2  # 初始退避 2秒
    
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
                messages=[
                    {"role": "user", "content": prompt}
                ],
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
