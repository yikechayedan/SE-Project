from .services_llm import call_llm
from .models import EvaluationTask, EvaluationItem
from django.utils import timezone

def run_evaluation(task_id: int):
    """
    测试版评测逻辑：
    不依赖 EvaluationTask.start_evaluation()
    也不依赖 Celery（你们之后可以再加）
    """

    try:
        task = EvaluationTask.objects.get(id=task_id)
    except EvaluationTask.DoesNotExist:
        return {"error": "task not found"}

    task.status = "running"
    task.save()

    model_name = task.model.name
    items = task.items.all()

    correct = 0
    total = items.count()

    for item in items:
        prediction = call_llm(item.content, model_name)
        item.predicted_answer = prediction

        if task.method == "objective" and item.correct_answer:
            if prediction.strip() == item.correct_answer.strip():
                item.is_correct = 1
                correct += 1
            else:
                item.is_correct = 0

        item.save()

    if task.method == "objective":
        task.accuracy = correct / total if total > 0 else 0.0

    task.status = "completed"
    task.time_used = timezone.now() - task.created_at
    task.save()

    return {"status": "completed", "accuracy": task.accuracy}
