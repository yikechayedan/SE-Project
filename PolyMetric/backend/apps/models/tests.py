# apps/tasks/tests.py

from django.test import TestCase
from django.conf import settings
import requests


class LLMApiConnectionTests(TestCase):
    """
    测试 Paratera LLM API 是否可用
    """

    def test_llm_basic_call(self):
        """
        使用最简单 "Hello World" Prompt 测试是否能成功调用 API
        """

        url = settings.LLM_BASE_URL + "chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "DeepSeek-V3.1-Terminus",   
            "messages": [
                {"role": "user", "content": "Hello! 请回答：1+1=？"}
            ],
            "stream": False,
        }
        

        print("\n--- 发送请求到 LLM API ---")
        print(url)
        print(payload)

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print("\n--- API 返回内容 ---")
        print(response.text)

        self.assertEqual(response.status_code, 200, "LLM API 调用失败")
        
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        print("\n模型回答：", answer)

        self.assertTrue(len(answer) > 0, "模型未返回内容")
