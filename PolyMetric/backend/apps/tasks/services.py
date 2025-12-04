import requests
from django.conf import settings

def call_llm_api(prompt: str, model_name: str):
    """
    通用大模型调用接口
    :param prompt: 输入文本
    :param model_name: My_Model.name 字段，例如 "gpt-4o-mini"
    """

    url = settings.LLM_BASE_URL.rstrip("/") + "/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        # 通用返回结构
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"[LLM Error] {str(e)}"
