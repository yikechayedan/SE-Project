# apps/tasks/run_logic.py

import json
import re
from django.utils import timezone
from django.db import transaction

from .services import call_llm_api
from .models import EvaluationTask, EvaluationItem
from apps.datasets.models import Dataset
from .models import EvaluationSummary
from apps.system.services import log_task_complete

# =========================================================
# Step 3 核心：Prompt 工业级约束 + 输出清洗
# =========================================================

def build_objective_prompt(item: EvaluationItem) -> str:
    """
    构造【工业级客观题 Prompt】
    目标：让模型【只能】输出一个可判别的最终答案
    """
    return f"""
你是一个自动判题系统。

下面是一道客观题，请你认真作答。
你的任务是：给出唯一正确的选项。

【非常重要的输出要求】
1. 只输出最终答案本身
2. 如果是选择题，只输出 A / B / C / D（大写）
3. 如果是数字题，只输出数字本身
4. 不要解释，不要多说一句话，不要输出多余字符

题目如下：
{item.content}

请直接输出答案：
""".strip()

def build_subjective_prompt(question, model_answer, reference=None):
    return f"""
你是一个严格的评分员，请根据问题和模型回答进行评分。

【评分规则】
- 评分范围：1 到 10 分
- 10 分：回答准确、完整、清晰
- 5 分：回答部分正确但不完整
- 1 分：回答错误或无关

【输出要求】
- 只输出一个整数（1-10）
- 不要解释，不要多余文字

【问题】
{question}

【模型回答】
{model_answer}

【参考答案】
{reference or "无"}

请给出评分：
""".strip()


def build_subjective_answer_prompt(item: EvaluationItem) -> str:
    return f"""
请认真回答下面的主观问题。

问题：
{item.content}

请直接给出你的回答，不要自我评价，不要打分。
""".strip()



def build_subjective_judge_prompt(item: EvaluationItem) -> str:
    return f"""
你是一个严格、公正的评测专家。

【问题】
{item.content}

【参考答案 / 评分要点】
{item.correct_answer}

【模型回答】
{item.predicted_answer}

请你根据参考答案，对模型回答进行评分。

评分要求：
1. 评分范围：1–10 的整数
2. 只输出一个数字
3. 不要解释，不要输出多余内容

请直接输出分数：
""".strip()



def clean_choice_answer(raw_text: str) -> str:
    """
    从模型输出中提取最终答案（兜底防御）
    """
    if not raw_text:
        return ""

    text = raw_text.strip().upper()

    # 优先提取字母选项
    for ch in ["A", "B", "C", "D", "E", "F"]:
        if ch in text:
            return ch

    # 再提取数字
    match = re.search(r"-?\d+(\.\d+)?", text)
    if match:
        return match.group(0)

    return text


def normalize_answer(text: str) -> str:
    """
    标准化答案（防止空格、大小写差异）
    """
    if not text:
        return ""
    return re.sub(r"\s+", "", str(text)).lower()


# =========================================================
# Dataset → EvaluationItem
# =========================================================

def load_dataset_entries(dataset: Dataset):
    """
    从 Dataset.file_path 读取 JSON
    要求：顶层是 list
    """
    if not dataset.file_path:
        raise ValueError("Dataset has no file")

    if dataset.file_format.lower() != "json":
        raise ValueError("Objective evaluation only supports JSON dataset")

    with open(dataset.file_path.path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Dataset JSON must be a list")

    return data


@transaction.atomic
def prepare_evaluation_items(task: EvaluationTask):
    """
    如果 EvaluationItem 不存在 → 由 Dataset 自动生成
    """
    if task.items.exists():
        return

    entries = load_dataset_entries(task.dataset)
    items = []

    for entry in entries:
        content = (
            entry.get("input")
            or entry.get("question")
            or entry.get("prompt")
        )

        answer = (
            entry.get("answer")
            or entry.get("label")
            or entry.get("target")
        )

        if not content:
            continue

        items.append(
            EvaluationItem(
                task=task,
                content=content,
                correct_answer=answer,
            )
        )

    EvaluationItem.objects.bulk_create(items)


# =========================================================
# 客观评测主逻辑
# =========================================================

def run_objective_evaluation(task: EvaluationTask):
    """
    客观评测完整流程（Step 1–3）
    """
    prepare_evaluation_items(task)

    items = task.items.all()
    total = items.count()

    if total == 0:
        raise ValueError("No evaluation items found")

    model_name = task.myModel.name
    correct = 0

    for item in items:
        # 已跑过的不重复跑
        if item.predicted_answer:
            if item.is_correct:
                correct += 1
            continue

        # ✅ Step 3：使用工业级 Prompt
        prompt = build_objective_prompt(item)

        raw_prediction = call_llm_api(
            prompt=prompt,
            model_name=model_name
        )

        item.predicted_answer = raw_prediction

        # ✅ Step 3：清洗 + 判分
        pred = normalize_answer(clean_choice_answer(raw_prediction))
        gold = normalize_answer(item.correct_answer)

        item.is_correct = 1 if pred == gold else 0
        correct += item.is_correct

        item.save()

    task.accuracy = round(correct / total, 4)
    task.status = "completed"
    task.time_used = timezone.now() - task.created_at
    task.save()
    
    # 记录系统事件：评测完成
    log_task_complete(task, task.creator)

    # ✅ 写入 / 更新 Summary（幂等）
    EvaluationSummary.objects.update_or_create(
        task=task,
        defaults={
            "model_name": model_name,
            "total": total,
            "correct": correct,
            "accuracy": task.accuracy,
        }
    )

    return {
        "task_id": task.id,
        "method": task.method,
        "model": model_name,
        "total": total,
        "correct": correct,
        "accuracy": task.accuracy,
    }


def run_subjective_evaluation(task: EvaluationTask):
    prepare_evaluation_items(task)

    items = task.items.all()
    if not items.exists():
        raise ValueError("No evaluation items found")

    scorer_model = task.myModel.name  # 当前先用同一个模型打分
    scores = []

    for item in items:
        if item.score is not None:
            scores.append(item.score)
            continue

        # ① 先让模型回答
        answer = call_llm_api(
            prompt=item.content,
            model_name=scorer_model
        )
        item.predicted_answer = answer

        # ② 再让模型给自己打分
        score_prompt = build_subjective_prompt(
            question=item.content,
            model_answer=answer,
            reference=item.correct_answer,
        )

        raw_score = call_llm_api(
            prompt=score_prompt,
            model_name=scorer_model
        )

        try:
            score = int(raw_score.strip())
            score = max(1, min(10, score))
        except:
            score = 1

        item.score = score
        item.save()
        scores.append(score)

    avg_score = round(sum(scores) / len(scores), 4)

    task.score = avg_score
    task.status = "completed"
    task.save(update_fields=["score", "status"])
    
    # 记录系统事件：评测完成
    log_task_complete(task, task.creator)

    EvaluationSummary.objects.update_or_create(
        task=task,
        defaults={
            "model_name": scorer_model,
            "total": len(scores),
            "correct": None,
            "accuracy": None,
            "avg_score": avg_score,
        }
    )

    return {
        "task_id": task.id,
        "method": "subjective",
        "model": scorer_model,
        "avg_score": avg_score,
    }

def run_adversarial_generation(task: EvaluationTask):
    prepare_evaluation_items(task)

    items = task.items.all()
    if not items.exists():
        raise ValueError("No evaluation items found")

    # ⭐ 从 task 中取模型（而不是从参数传）
    if not task.myModel_2:
        raise ValueError("Adversarial task requires myModel_2 (Model B)")

    model_a = task.myModel.name
    model_b = task.myModel_2.name

    for item in items:
        if item.predicted_answer and item.predicted_answer_2:
            continue

        answer_a = call_llm_api(
            prompt=item.content,
            model_name=model_a,
        )

        answer_b = call_llm_api(
            prompt=item.content,
            model_name=model_b,
        )

        item.predicted_answer = answer_a
        item.predicted_answer_2 = answer_b
        item.save()

    task.status = "completed"
    task.save()
    
    # 记录系统事件：评测完成
    log_task_complete(task, task.creator)

    return {
        "task_id": task.id,
        "method": "adversarial",
        "model_a": model_a,
        "model_b": model_b,
        "total": items.count(),
    }




def generate_adversarial_summary(task):
    """
    根据人类裁判 preference，生成对抗评测汇总结果
    preference:
        - left  : Model A 胜
        - right : Model B 胜
        - tie   : 平局
    """

    items = EvaluationItem.objects.filter(task=task)

    total = items.count()
    if total == 0:
        raise ValueError("No evaluation items found")

    win_a = items.filter(preference="left").count()
    win_b = items.filter(preference="right").count()
    tie = items.filter(preference="tie").count()

    # 防止除 0
    win_rate_a = round(win_a / total, 4) if total > 0 else 0.0

    model_a_name = task.myModel.name
    model_b_name = task.myModel_2.name if task.myModel_2 else "Unknown"

    summary_text = (
        f"对抗评测结果（人类裁判）：\n"
        f"模型 A（{model_a_name}） vs 模型 B（{model_b_name}）\n"
        f"总题数：{total}\n"
        f"模型 A 胜：{win_a}\n"
        f"模型 B 胜：{win_b}\n"
        f"平局：{tie}\n"
        f"模型 A 胜率：{win_rate_a * 100:.2f}%\n"
    )

    summary, _ = EvaluationSummary.objects.update_or_create(
        task=task,
        defaults={
            "model_name": f"{model_a_name} vs {model_b_name}",
            "total": total,
            "correct": win_a,        # A 胜场
            "accuracy": win_rate_a,  # A 胜率
            "summary": summary_text,
        },
    )

    return summary



# =========================================================
# 对外统一入口
# =========================================================

def run_evaluation(task_id: int):
    try:
        task = EvaluationTask.objects.select_related(
            "dataset", "myModel"
        ).get(id=task_id)
    except EvaluationTask.DoesNotExist:
        return {"error": "task not found"}

    task.status = "running"
    task.save(update_fields=["status"])

    if task.method == "objective":
        return run_objective_evaluation(task)

    elif task.method == "subjective":
        return run_subjective_evaluation(task)

    elif task.method == "adversarial":
        # 人类裁判对抗评测
        return run_adversarial_generation(task)

    else:
        return {"error": f"unknown task method: {task.method}"}

