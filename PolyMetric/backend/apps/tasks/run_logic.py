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

# =========================================================
# 对抗评测：模型裁判 Prompt
# =========================================================

def build_adversarial_judge_prompt(item):
    """
    构造对抗评测的裁判 Prompt
    输出必须是：left / right / tie
    """
    return f"""
你是一个严格、公正的评测裁判。

下面给出同一个问题的两个模型回答，请你判断哪一个更好。

【评判标准】
- 准确性
- 完整性
- 逻辑清晰度
- 与问题的相关性

【问题】
{item.content}

【模型 A 回答】
{item.predicted_answer}

【模型 B 回答】
{item.predicted_answer_2}

【输出要求（非常重要）】
- 如果模型 A 更好，只输出：left
- 如果模型 B 更好，只输出：right
- 如果两者水平相当，只输出：tie
- 不要解释
- 不要输出任何多余字符

请直接输出裁判结果：
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
        # 避免报错，如果还没生成 items，直接返回 None
        return None

    win_a = items.filter(preference="left").count()
    win_b = items.filter(preference="right").count()
    tie = items.filter(preference="tie").count()

    # 防止除 0
    # 胜率计算：(胜场 + 0.5 * 平局) / 总场次
    win_rate_a = round((win_a + 0.5 * tie) / total, 4) if total > 0 else 0.0

    model_a_name = task.myModel.name
    model_b_name = task.myModel_2.name if task.myModel_2 else "Unknown"

    summary_text = (
        f"对抗评测结果：\n"
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
    返回所有关联的 Item IDs (供 Dispatcher 使用)
    """
    if task.items.exists():
        # 即使已经存在，也返回 IDs，防止重试时拿不到 ID
        return list(task.items.values_list("id", flat=True))

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

    created_items = EvaluationItem.objects.bulk_create(items)
    # bulk_create 在 Django (某些 DB 后端) 返回的对象可能没有 ID，
    # 但通常 Postgres/SQLite 支持。为了保险，重新查一次。
    return list(task.items.values_list("id", flat=True))


def get_pending_item_ids(task: EvaluationTask, limit: int = 100):
    """
    高效获取待处理条目的 ID 列表（用于分批调度）
    优先获取还没有 predicted_answer 的条目
    """
    # 针对不同 Method，"待处理"定义略有不同，但通常是 predicted_answer 为空
    # 简单起见，只要 predicted_answer 为空就需要跑 LLM
    # 如果是 adversarial，需要 predicted_answer_2 为空
    
    qs = task.items.all().order_by("id")
    
    if task.method == "adversarial":
        from django.db.models import Q
        # 只要缺一个回答，就算待处理
        qs = qs.filter(Q(predicted_answer__isnull=True) | Q(predicted_answer_2__isnull=True))
    else:
        # objective / subjective
        qs = qs.filter(predicted_answer__isnull=True)
        
    return list(qs.values_list("id", flat=True)[:limit])


# ... (imports remain similar, assume existing context)

# =========================================================
# Single Item Logic (Granular Execution)
# =========================================================

def run_single_item_logic(item_id: int):
    """
    执行单个 Item 的评测逻辑 (Worker 核心逻辑)
    根据 Task Method 分发
    """
    try:
        # 必须 select_related task，以便访问 task.method 等配置
        try:
            item = EvaluationItem.objects.select_related(
                "task", 
                "task__myModel", 
                "task__myModel_2", 
                "task__judge_model"
            ).get(id=item_id)
        except EvaluationItem.DoesNotExist:
            return

        task = item.task
        method = task.method

        # 1. 客观评测
        if method == "objective":
            # 幂等性检查：如果已经有值（包括错误信息），直接跳过
            if item.predicted_answer: 
                return

            prompt = build_objective_prompt(item)
            raw_prediction = call_llm_api(prompt, task.myModel.name)
            
            item.predicted_answer = raw_prediction
            
            # 如果是报错信息，不计算 is_correct，直接保存
            if raw_prediction.startswith("[Error]"):
                item.is_correct = 0 # 视为错误
            else:
                pred = normalize_answer(clean_choice_answer(raw_prediction))
                gold = normalize_answer(item.correct_answer)
                item.is_correct = 1 if pred == gold else 0
                
            item.save(update_fields=["predicted_answer", "is_correct"])

        # 2. 主观评测
        elif method == "subjective":
            # (A) 生成回答
            if not item.predicted_answer:
                answer = call_llm_api(
                    build_subjective_answer_prompt(item), 
                    task.myModel.name
                )
                item.predicted_answer = answer
                item.save(update_fields=["predicted_answer"])

            # (B) 如果是模型裁判，紧接着打分
            # 注意：如果回答生成失败（[Error]），则跳过打分或给最低分
            if task.judge_type == "model":
                # 只有当回答正常且尚未打分时才打分
                if item.predicted_answer and not item.predicted_answer.startswith("[Error]") and item.score is None:
                    judge_model_name = task.judge_model.name if task.judge_model else task.myModel.name
                    raw_score = call_llm_api(
                        build_subjective_judge_prompt(item), 
                        judge_model_name
                    )
                    
                    if raw_score.startswith("[Error]"):
                        # [修复死循环] 打分失败，必须写入一个值，不能留 None
                        # 这里写入 -1 表示评分失败
                        item.score = -1
                    else:
                        try:
                            score = int(raw_score.strip())
                            score = max(1, min(10, score))
                        except:
                            score = 1
                        item.score = score
                        
                    item.save(update_fields=["score"])

        # 3. 对抗评测
        elif method == "adversarial":
            # (A) 生成 A/B 回答
            updated = False
            
            # Model 1
            if not item.predicted_answer:
                item.predicted_answer = call_llm_api(item.content, task.myModel.name)
                updated = True
                
            # Model 2
            if not item.predicted_answer_2:
                if task.myModel_2:
                    item.predicted_answer_2 = call_llm_api(item.content, task.myModel_2.name)
                    updated = True
            
            if updated:
                item.save(update_fields=["predicted_answer", "predicted_answer_2"])

            # (B) 如果是模型裁判，紧接着判胜负
            if task.judge_type == "model":
                if item.preference is None:
                    # 必须保证两者都已生成且无 Error
                    ans1 = item.predicted_answer
                    ans2 = item.predicted_answer_2
                    
                    valid_1 = ans1 and not ans1.startswith("[Error]")
                    valid_2 = ans2 and not ans2.startswith("[Error]")
                    
                    if valid_1 and valid_2:
                        judge_model_name = task.judge_model.name if task.judge_model else task.myModel.name
                        raw_judge = call_llm_api(
                            build_adversarial_judge_prompt(item),
                            judge_model_name
                        )
                        
                        if raw_judge.startswith("[Error]"):
                            # [修复死循环] 判题失败，写入 "error"
                            item.preference = "error"
                        else:
                            item.preference = parse_adversarial_judge(raw_judge)
                            
                        item.save(update_fields=["preference"])
                    elif (ans1 and ans1.startswith("[Error]")) or (ans2 and ans2.startswith("[Error]")):
                         # 如果回答生成本身就 Error 了，preference 也直接标记 error，防止永久等待
                         item.preference = "error"
                         item.save(update_fields=["preference"])

    except Exception as outer_e:
        # [Ultimate Fail-Safe] 兜底异常捕获
        # 如果发生任何未捕获异常，强制将 predicted_answer 标记为 Error，
        # 防止该条目无限期卡在 pending 状态导致死循环。
        try:
            if 'item' in locals() and item:
                error_msg = f"[Error] System Failure: {str(outer_e)}"
                # 只有当字段为空时才覆盖，保留部分结果
                if not item.predicted_answer:
                    item.predicted_answer = error_msg
                if item.task.method == "adversarial" and not item.predicted_answer_2:
                    item.predicted_answer_2 = error_msg
                
                # 针对打分字段也要兜底
                if item.task.method == "subjective" and item.score is None:
                    item.score = -1
                if item.task.method == "adversarial" and item.preference is None:
                    item.preference = "error"
                    
                item.save()
        except:
            # 如果连 save 都失败（例如 DB 挂了），那确实没办法了，
            # 但至少 Worker 不会崩溃，Log 会记录下来。
            pass
        print(f"Critical error in run_single_item_logic: {outer_e}")


# =========================================================
# Task Finalizer (Thread-Safe & Optimized)
# =========================================================

def try_finalize_task(task_id: int, from_dispatcher: bool = False):
    """
    检查任务是否全部完成，如果是，执行汇总逻辑。
    
    优化逻辑：
    - 如果 from_dispatcher=True，说明调度器已经发完了所有任务。
      此时如果发现还有 pending items，不再只是 return，而是安排一个延时检查 (reschedule)。
      这避免了 Worker 每次都 select_for_update 的开销。
    """
    from apps.tasks.tasks import try_finalize_task_delayed # 避免循环引用，lazy import
    
    with transaction.atomic():
        try:
            task = EvaluationTask.objects.select_related("dataset", "myModel").select_for_update().get(id=task_id)
        except EvaluationTask.DoesNotExist:
            return

        if task.status != "running":
            return

        method = task.method
        has_pending = False
        
        # 判定 pending 逻辑 (包含 [Error] 视为已处理)
        # 注意：这里我们只看“是否还有没填值的”。[Error] 也是值，所以不算 pending。
        
        if method == "objective":
            # 只要有 predicted_answer 为空的，就算没完
            has_pending = task.items.filter(predicted_answer__isnull=True).exists()
            
        elif method == "subjective":
            # 1. 必须都有 predicted_answer
            # 2. 如果是 model judge，还必须都有 score (前提是 predicted_answer 正常)
            if task.items.filter(predicted_answer__isnull=True).exists():
                has_pending = True
            elif task.judge_type == "model":
                # 复杂的 pending 检查：
                # 还有“预测成功(非Error) 但 分数为空”的吗？
                # 如果预测失败([Error])，score 可以为空，不算 pending
                has_pending = task.items.exclude(predicted_answer__startswith="[Error]").filter(score__isnull=True).exists()
                
        elif method == "adversarial":
            if task.items.filter(predicted_answer__isnull=True).exists() or \
               task.items.filter(predicted_answer_2__isnull=True).exists():
                has_pending = True
            elif task.judge_type == "model":
                has_pending = task.items.exclude(predicted_answer__startswith="[Error]") \
                                        .exclude(predicted_answer_2__startswith="[Error]") \
                                        .filter(preference__isnull=True).exists()

        if has_pending:
            if from_dispatcher:
                # 调度器说发完了，但数据库说没做完 -> 可能是 Worker 还在跑
                # 触发“延时最终检查”，过 5 秒再来看看
                try_finalize_task_delayed.apply_async(args=[task_id], countdown=5)
            return

        # === 到这里说明所有条目都已处理完毕 ===
        
        # 1. 特殊情况：如果是 人类裁判，状态转为 awaiting
        if method in ["subjective", "adversarial"] and task.judge_type == "human":
            task.status = "awaiting_human_judge"
            task.save(update_fields=["status"])
            return

        # 2. 正常情况：计算统计数据 & 标记 Completed
        if method == "objective":
            # 聚合计算
            total = task.items.count()
            # 排除 [Error]
            valid_items = task.items.exclude(predicted_answer__startswith="[Error]")
            correct = valid_items.filter(is_correct=1).count()
            
            # 分母用 total 还是 valid_total？通常用 total 统计完成率，但准确率可能仅针对 valid
            # 这里简单起见，[Error] 算错
            acc = round(correct / total, 4) if total > 0 else 0
            
            task.accuracy = acc
            task.status = "completed"
            task.time_used = timezone.now() - task.created_at
            task.save(update_fields=["accuracy", "status", "time_used"])
            
            EvaluationSummary.objects.update_or_create(
                task=task,
                defaults={
                    "model_name": task.myModel.name,
                    "total": total,
                    "correct": correct,
                    "accuracy": acc,
                }
            )

        elif method == "subjective":
            from django.db.models import Avg
            valid_items = task.items.exclude(predicted_answer__startswith="[Error]")
            avg = valid_items.aggregate(Avg("score"))["score__avg"] or 0
            avg = round(avg, 4)
            
            task.score = avg
            task.status = "completed"
            task.time_used = timezone.now() - task.created_at
            task.save(update_fields=["score", "status", "time_used"])
            
            EvaluationSummary.objects.update_or_create(
                task=task,
                defaults={
                    "model_name": f"{task.myModel.name} (judge=Model)",
                    "total": task.items.count(),
                    "avg_score": avg,
                }
            )

        elif method == "adversarial":
            summary_obj = generate_adversarial_summary(task)
            task.status = "completed"
            task.time_used = timezone.now() - task.created_at
            task.save(update_fields=["status", "time_used"])

        # 3. 通用收尾
        log_task_complete(task, task.creator)
        
        from apps.rankings.services import update_model_rankings
        update_model_rankings(task.dataset_id)


# =========================================================
# 对外统一入口
# =========================================================

def run_evaluation(task_id: int):
    # 同步测试入口 (Legacy Wrapper)
    task = EvaluationTask.objects.get(id=task_id)
    item_ids = prepare_evaluation_items(task)
    task.status = "running"
    task.save()
    
    for iid in item_ids:
        run_single_item_logic(iid)
        
    try_finalize_task(task_id, from_dispatcher=True)
    return {"status": "submitted_sync"}




