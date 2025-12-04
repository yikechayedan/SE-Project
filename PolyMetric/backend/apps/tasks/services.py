import requests
from django.conf import settings

def call_llm_api(prompt: str, model_name: str):
    """
    调用外部大模型 API，统一封装，方便任务评测使用
    """
    url = settings.LLM_BASE_URL + "chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[LLM Error] {str(e)}"
