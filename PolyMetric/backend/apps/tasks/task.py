from celery import shared_task
from django.utils import timezone
from .models import EvaluationTask, EvaluationItem
from .services import call_llm_api

@shared_task
def run_evaluation_task(task_id):
    """
    执行评测任务：
    1. 遍历 EvaluationItem
    2. 调大模型 API
    3. 写入 predicted_answer
    4. 客观题计算是否正确
    5. 写入正确率 / 状态
    """
    try:
        task = EvaluationTask.objects.get(id=task_id)
    except EvaluationTask.DoesNotExist:
        return

    task.status = "running"
    task.save()

    model_name = task.model.name  
    items = task.items.all()

    correct = 0
    total = items.count()

    for item in items:
        predicted = call_llm_api(item.content, model_name)
        item.predicted_answer = predicted

        if task.method == "objective" and item.correct_answer:
            item.is_correct = 1 if predicted.strip() == item.correct_answer.strip() else 0
            if item.is_correct:
                correct += 1

        item.save()

    if task.method == "objective":
        task.accuracy = round(correct / total, 4) if total > 0 else 0

    task.status = "completed"
    task.time_used = timezone.now() - task.created_at
    task.save()

    return True
