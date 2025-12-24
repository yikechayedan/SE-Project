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
    调用大模型判断数据集能力标签。
    针对多模态数据集，优先抽样带图片的条目发送给视觉模型。
    """
    from apps.tasks.services import call_llm_api, load_image_from_dataset

    has_images = dataset.has_images if dataset else False
    images_to_send = []
    
    # 1. 抽样策略优化：如果是多模态，尽量寻找带图片的样本
    analysis_samples = []
    if has_images and dataset and dataset.file_path:
        try:
            # 第一轮：搜寻带图片的样本（最多 3 个）
            img_count = 0
            for item in samples:
                if isinstance(item, dict) and item.get('image'):
                    img_data = load_image_from_dataset(dataset.file_path, item['image'])
                    if img_data:
                        images_to_send.append(img_data)
                        analysis_samples.append(item)
                        img_count += 1
                if img_count >= 3: break
            
            # 第二轮：如果带图片的样本不足，补充一些文本样本凑齐上下文
            if len(analysis_samples) < 5:
                for item in samples:
                    if item not in analysis_samples:
                        analysis_samples.append(item)
                    if len(analysis_samples) >= 5: break
        except Exception as e:
            print(f"[Error] 多模态样本提取失败: {e}")
            analysis_samples = samples[:5]
    else:
        analysis_samples = samples[:5]

    # 2. 构建 Prompt
    prompt = build_prompt(analysis_samples, has_images=bool(images_to_send))
    
    # 3. 模型选择：只要有图片提取成功，就必须用多模态模型
    model_name = "Qwen2.5-VL-72B-Instruct" if images_to_send else "DeepSeek-R1-0528"

    print(f"[DEBUG] AI 能力分析 - 类别: {dataset.category if dataset else 'unknown'}, 模型: {model_name}, 包含图片: {len(images_to_send)}")

    try:
        # 4. 严格按照评测引擎验证过的签名调用
        response = call_llm_api(
            prompt=prompt,
            model_name=model_name,
            images=images_to_send if images_to_send else None
        )
        
        if not response or not isinstance(response, str):
            return "other"

        tag = response.strip().lower()
        
        # 结果映射
        valid_tags = ["language", "reasoning", "code", "multimodal", "other"]
        for valid_tag in valid_tags:
            if valid_tag in tag:
                return valid_tag
                
        return "other"
        
    except Exception as e:
        print(f"[Error] AI 能力分析异常: {e}")
        return "other"
