import json


def build_prompt(samples):
    return f"""
你是一个 AI 能力评测专家。

我将给你一个数据集的若干条样本，请你判断：
这个数据集主要用于评测大模型的哪一项核心能力。

可选能力只有以下四种（只能选一个）：
1. language：自然语言理解、生成、翻译、摘要、文本分析
2. reasoning：数学推理、逻辑推理、多步推理、选择题、判断题
3. coding：代码生成、代码理解、算法实现、程序修复
4. other: 如果数据集非常混乱，则返回other
请根据任务本质判断，而不是字段名或文件格式。

请只返回一个字符串，必须是：
language / reasoning / coding / other

数据集样本如下：
{json.dumps(samples, ensure_ascii=False, indent=2)}
""".strip()


def ai_judge_capability(samples):
    """
    调用大模型判断数据集能力标签
    """
    from apps.tasks.services import call_llm_api

    prompt = build_prompt(samples)

    
    response = call_llm_api(
        prompt=prompt,
        model_name="DeepSeek-R1-0528"   # 或你们已有的模型名
    )
    # response 必须是字符串
    if not isinstance(response, str):
        return "language"

    tag = response.strip().lower()

    if tag not in ("language", "reasoning", "coding"):
        # 兜底策略
        return "other"

    
    return tag
