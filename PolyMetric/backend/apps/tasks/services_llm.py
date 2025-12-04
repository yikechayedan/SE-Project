import requests
from django.conf import settings

def call_llm(prompt: str, model_name: str):
    """
    调用大模型 API（测试可用版本）
    """
    url = settings.LLM_BASE_URL + "chat/completions"

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
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"[LLM ERROR] {str(e)}"
