# apps/tasks/run_logic.py
from .services import call_llm_api
from .models import EvaluationTask, EvaluationItem
from django.utils import timezone


def run_evaluation(task_id: int):
    """
    同步执行（非 Celery）版本的任务执行函数：
    供前端 / 测试环境直接使用
    """

    try:
        task = EvaluationTask.objects.get(id=task_id)
    except EvaluationTask.DoesNotExist:
        return {"error": "task not found"}

    task.status = "running"
    task.save()

    # ⭐ 使用 myModel
    model_name = task.myModel.name
    items = task.items.all()

    correct = 0
    total = items.count()

    for item in items:
        # 调用统一的大模型 API
        prediction = call_llm_api(item.content, model_name)
        item.predicted_answer = prediction

        # 客观评测：判断是否正确
        if task.method == "objective" and item.correct_answer:
            item.is_correct = (
                1 if prediction.strip() == item.correct_answer.strip() else 0
            )
            correct += item.is_correct or 0

        item.save()

    # 计算 accuracy
    if task.method == "objective":
        task.accuracy = round(correct / total, 4) if total > 0 else 0.0

    task.status = "completed"
    task.time_used = timezone.now() - task.created_at
    task.save()

    return {"status": "completed", "accuracy": task.accuracy}
