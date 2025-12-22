# apps/tasks/services.py

from openai import OpenAI
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import EvaluationTask
from .models import EvaluationItem
REUSE_WINDOW_SECONDS = 3600  # 1 小时
#拷贝回答
def reuse_model_answers(task):
    reused = 0
    new_items = list(task.items.all())

    print("NEW items count:", len(new_items))

    old_items = EvaluationItem.objects.filter(
        task__dataset_id=task.dataset_id,
        task__myModel_id=task.myModel_id,
        predicted_answer__isnull=False,
        task__status="completed",
    )

    print("OLD candidates:", old_items.count())

    for item in new_items:
        old_item = old_items.filter(
            dataset_item_index=item.dataset_item_index
        ).first()

        if old_item:
            item.predicted_answer = old_item.predicted_answer
            item.save(update_fields=["predicted_answer"])
            reused += 1

    print(f"♻️ reused {reused}/{len(new_items)} answers")


#任务搜索函数
def find_reusable_task(
    *,
    dataset_id,
    method,
    myModel_id,
    myModel_2_id=None,
    judge_type="human",
    judge_model_id=None,
):
    now = timezone.now()
    window_start = now - timedelta(seconds=REUSE_WINDOW_SECONDS)

    qs = EvaluationTask.objects.filter(
        dataset_id=dataset_id,
        method=method,
        myModel_id=myModel_id,
    ).exclude(status="failed")

    if method == "adversarial":
        qs = qs.filter(
            myModel_2_id=myModel_2_id,
            judge_type=judge_type,
            judge_model_id=judge_model_id,
        )

    if method == "subjective":
        qs = qs.filter(
            judge_type=judge_type,
        )
        if judge_type == "model":
            qs = qs.filter(judge_model_id=judge_model_id)

    # ① 先找 1 小时内已完成的
    completed = qs.filter(
        status="completed",
        updated_at__gte=window_start,
    ).order_by("updated_at")

    if completed.exists():
        return completed.first()

    # ② 再找正在进行的
    running = qs.filter(
        status__in=["pending", "running", "awaiting_human_judge"]
    ).order_by("created_at")

    if running.exists():
        return running.first()

    return None

def call_llm_api(prompt: str, model_name: str):
    """
    使用 OpenAI SDK（Paratera 接入）
    """
    print("🚨 CALL LLM:", model_name)
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
