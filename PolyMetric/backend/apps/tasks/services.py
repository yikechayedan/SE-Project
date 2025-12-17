# apps/tasks/services.py

from openai import OpenAI
from django.conf import settings

def call_llm_api(prompt: str, model_name: str):
    """
    使用 OpenAI SDK（Paratera 接入）
    """
    try:
        client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"[LLM Error] {e}"
