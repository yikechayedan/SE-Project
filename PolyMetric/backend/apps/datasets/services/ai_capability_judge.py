import json
import logging
import os
from apps.tasks.services import call_llm_api, load_image_from_dataset

logger = logging.getLogger(__name__)

def build_prompt(samples, has_images=False):
    image_context = ""
    if has_images:
        image_context = "\n注意：这是一个多模态/图像数据集，我已经为你附带了其中几条样本的图片。请结合图片内容判断其测试维度。"

    return f"""
你是一个 AI 能力评测专家。{image_context}

我将给你一个数据集的若干条样本，请你判断：
这个数据集主要用于评测大模型的哪一项核心能力。

可选能力只有以下五种（只能选一个）：
1. language：自然语言理解、生成、翻译、摘要、文本分析、图像描述、视觉识别、文学创作。
2. reasoning：数学推理、逻辑计算、多步算术、几何证明、代数问题、图像逻辑推理、常识推理。
3. code：代码生成、代码理解、算法实现、程序修复。
4. multimodal：复杂的跨模态理解、图表分析、图像QA、多模态指令遵循。
5. other：都不属于上述四类，或者内容非常杂乱无法定性。

请只返回一个字符串，必须是：
language / reasoning / code / multimodal / other

数据集样本如下：
{json.dumps(samples, ensure_ascii=False, indent=2)}
""".strip()


def ai_judge_capability(samples, dataset=None):
    """
    调用大模型判断数据集能力标签，支持图像分析
    完全仿照 run_logic.py 的图片发送逻辑
    """
    from apps.tasks.services import call_llm_api, load_image_from_dataset

    has_images = dataset.has_images if dataset else False
    images_to_send = []
    
    # 1. 仿照 run_logic.py：如果是图像数据集，提取图片 Base64
    if has_images and dataset and dataset.file_path:
        try:
            count = 0
            for item in samples:
                if isinstance(item, dict) and item.get('image'):
                    # 调用与评测引擎相同的图片加载函数
                    img_data = load_image_from_dataset(dataset.file_path, item['image'])
                    if img_data:
                        images_to_send.append(img_data)
                        count += 1
                if count >= 3: break 
        except Exception as e:
            print(f"[Error] 提取分析样本图片失败: {e}")

    prompt = build_prompt(samples, has_images=has_images)
    
    # 2. 选用授权列表中最稳定的多模态模型
    model_name = "Qwen2.5-VL-72B-Instruct" if has_images else "DeepSeek-R1-0528"

    print(f"[DEBUG] 数据集能力分析启动 - 模型: {model_name}, 样本数: {len(samples)}, 图片数: {len(images_to_send)}")

    # 3. 严格按照 call_llm_api 的签名调用，不改动该函数
    try:
        response = call_llm_api(
            prompt=prompt,
            model_name=model_name,
            images=images_to_send if images_to_send else None
        )
        
        if not isinstance(response, str):
            return "other"

        tag = response.strip().lower()
        
        # 结果匹配
        valid_tags = ["language", "reasoning", "code", "multimodal", "other"]
        for valid_tag in valid_tags:
            if valid_tag in tag:
                return valid_tag
                
        return "other"
        
    except Exception as e:
        print(f"[Error] AI 能力分析调用异常: {e}")
        return "other"
