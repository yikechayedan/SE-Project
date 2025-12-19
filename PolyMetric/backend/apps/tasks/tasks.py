from celery import shared_task
from django.utils import timezone
from .models import EvaluationTask
from .run_logic import run_evaluation
import traceback

@shared_task(bind=True)
def run_evaluation_task(self, task_id):
    """
    异步执行评测任务的 Celery Task
    """
    try:
        # 再次确认任务存在
        task = EvaluationTask.objects.get(id=task_id)
        
        # 执行同步的评测逻辑
        # run_evaluation 内部负责了状态流转 (running -> completed/awaiting_judge)
        result = run_evaluation(task_id)
        
        return result
        
    except EvaluationTask.DoesNotExist:
        return {"error": f"Task {task_id} not found"}
        
    except Exception as e:
        # 捕获未知异常，更新数据库状态为 failed
        print(f"Error processing task {task_id}: {str(e)}")
        print(traceback.format_exc())
        
        try:
            task = EvaluationTask.objects.get(id=task_id)
            task.status = "failed"
            # 将错误信息追加到描述中方便排查
            task.description = (task.description or "") + f"\n\n[Error Log] {str(e)}"
            task.save(update_fields=["status", "description"])
        except Exception as db_err:
            print(f"Failed to update task status: {db_err}")
            
        raise e
