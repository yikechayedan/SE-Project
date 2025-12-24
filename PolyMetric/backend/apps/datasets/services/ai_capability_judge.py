import json


def build_prompt(samples):
    return f"""
你是一个 AI 能力评测专家。

我将给你一个数据集的若干条样本，请你判断：
这个数据集主要用于评测大模型的哪一项核心能力。

可选能力只有以下四种（只能选一个）：
1. language：自然语言理解、生成、翻译、摘要、文本分析、图像描述、视觉理解
2. reasoning：数学推理、逻辑推理、多步推理、选择题、判断题、图像推理
3. coding：代码生成、代码理解、算法实现、程序修复
4. other: 如果数据集非常混乱或无法分类，则返回other

重要提示：
- 如果样本包含图片和图像相关问题，优先考虑 language（视觉理解）或 reasoning（图像推理）
- 如果样本是简单的图像识别或描述，通常属于 language 能力
- 只有明确的编程相关任务才归类为 coding

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

    # 添加调试日志
    print(f"[DEBUG] 发送给AI的样本数量: {len(samples)}")
    print(f"[DEBUG] 样本内容: {samples[:2] if len(samples) > 2 else samples}")
    print(f"[DEBUG] 构建的prompt长度: {len(prompt)} 字符")
    print(f"[DEBUG] Prompt前100字符: {prompt[:100]}...")

    response = call_llm_api(
        prompt=prompt,
        model_name="DeepSeek-R1-0528"   # 或你们已有的模型名
    )
    # response 必须是字符串
    if not isinstance(response, str):
        print(f"[DEBUG] AI返回非字符串响应: {type(response)} - {response}")
        return "language"

    tag = response.strip().lower()
    print(f"[DEBUG] AI原始响应: '{response}'")
    print(f"[DEBUG] 处理后的标签: '{tag}'")

    if tag not in ("language", "reasoning", "coding"):
        # 改进的兜底策略：基于关键词本地判断
        samples_text = str(samples).lower()
        
        # 视觉/图像相关关键词
        vision_keywords = ['图片', '图像', '视觉', '颜色', '识别', '描述', '看图', '图像描述']
        # 语言理解关键词
        language_keywords = ['问题', '回答', '解释', '翻译', '摘要', '生成', '理解', '分析', '描述']
        # 推理关键词
        reasoning_keywords = ['推理', '计算', '逻辑', '数学', '解题', '选择', '判断']
        # 编程关键词
        coding_keywords = ['代码', '编程', '算法', '函数', '程序', '实现', '修复']
        
        # 计算关键词匹配分数
        vision_score = sum(1 for keyword in vision_keywords if keyword in samples_text)
        language_score = sum(1 for keyword in language_keywords if keyword in samples_text)
        reasoning_score = sum(1 for keyword in reasoning_keywords if keyword in samples_text)
        coding_score = sum(1 for keyword in coding_keywords if keyword in samples_text)
        
        print(f"[DEBUG] 关键词匹配分数 - vision: {vision_score}, language: {language_score}, reasoning: {reasoning_score}, coding: {coding_score}")
        
        # 根据分数决定标签
        if vision_score > 0 and vision_score >= max(language_score, reasoning_score, coding_score):
            fallback_tag = "language"  # 图像相关归类为语言理解（视觉理解）
            print(f"[DEBUG] 基于关键词判断，使用兜底策略返回'{fallback_tag}'")
            return fallback_tag
        elif language_score >= max(reasoning_score, coding_score, vision_score):
            fallback_tag = "language"
            print(f"[DEBUG] 基于关键词判断，使用兜底策略返回'{fallback_tag}'")
            return fallback_tag
        elif reasoning_score >= max(language_score, coding_score, vision_score):
            fallback_tag = "reasoning"
            print(f"[DEBUG] 基于关键词判断，使用兜底策略返回'{fallback_tag}'")
            return fallback_tag
        elif coding_score >= max(language_score, reasoning_score, vision_score):
            fallback_tag = "coding"
            print(f"[DEBUG] 基于关键词判断，使用兜底策略返回'{fallback_tag}'")
            return fallback_tag
        else:
            print(f"[DEBUG] 关键词匹配不足，使用兜底策略返回'other'")
            return "other"

    print(f"[DEBUG] 最终返回标签: '{tag}'")
    return tag
