# apps/tasks/task.py
from celery import shared_task
from django.utils import timezone
from .models import EvaluationTask, EvaluationItem
from .services import call_llm_api


@shared_task
def run_evaluation_task(task_id):
    """
    异步执行评测任务（Celery）
    """

    try:
        task = EvaluationTask.objects.get(id=task_id)
    except EvaluationTask.DoesNotExist:
        return {"error": "Task not found"}

    task.status = "running"
    task.save()

    # ⭐ 统一改成 myModel
    model_name = task.myModel.name
    items = task.items.all()

    correct = 0
    total = items.count()

    for item in items:
        predicted = call_llm_api(item.content, model_name)
        item.predicted_answer = predicted

        if task.method == "objective" and item.correct_answer:
            item.is_correct = (
                1 if predicted.strip() == item.correct_answer.strip() else 0
            )
            correct += item.is_correct or 0

        item.save()

    if task.method == "objective":
        task.accuracy = round(correct / total, 4) if total > 0 else 0.0

    task.status = "completed"
    task.time_used = timezone.now() - task.created_at
    task.save()

    return {"msg": "evaluation finished", "accuracy": task.accuracy}
