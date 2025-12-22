#PolyMetric\backend\apps\tasks\tasks.py
from celery import shared_task
from .models import EvaluationTask
from .run_logic import (
    run_evaluation, 
    prepare_evaluation_items, 
    run_single_item_logic, 
    try_finalize_task,
    get_pending_item_ids
)
import traceback

# 批处理大小：每批 Worker 处理 5 条
BATCH_SIZE = 5

# 调度限制：每次 Init Task 往队列里塞多少条数据（防止洪水）
# 100 条 = 20 个 Celery Tasks
DISPATCH_LIMIT = 50 

@shared_task(bind=True)
def init_evaluation_task(self, task_id, phase='both'):
    """
    【智能调度任务】Smart Dispatcher
    支持分阶段调度 (generation / judging / both)
    """
    try:
        task = EvaluationTask.objects.get(id=task_id)
        
        # 1. 首次运行时，确保所有 Item 已创建
        if not task.items.exists():
            from .run_logic import prepare_evaluation_items
            prepare_evaluation_items(task)
            if task.status != "running":
                task.status = "running"
                task.save(update_fields=["status"])
        
        # 2. 捞取一小批待处理的 ID
        # 如果是补全模式，get_pending_item_ids 需要感知 phase
        from .run_logic import get_pending_item_ids, try_finalize_task
        pending_ids = get_pending_item_ids(task, limit=DISPATCH_LIMIT)
        
        if not pending_ids:
            # 如果是 generation 阶段跑完了，不要 finalize，而是同步并进入 judging
            if phase == 'generation':
                from .run_logic import sync_downstream_tasks
                sync_downstream_tasks(task)
                if task.judge_type == 'model':
                    # 递归进入打分阶段
                    init_evaluation_task.delay(task_id, phase='judging')
                    return f"Generation finished, switching to judging for Task {task_id}."
            
            try_finalize_task(task_id, from_dispatcher=True)
            return f"Task {task_id} phase {phase} finished."

        # 3. 切片分发
        chunks = [pending_ids[i:i + BATCH_SIZE] for i in range(0, len(pending_ids), BATCH_SIZE)]

        for chunk_ids in chunks:
            process_evaluation_batch.delay(task_id, chunk_ids, phase=phase)
            
        # 4. 自我驱动
        if len(pending_ids) >= DISPATCH_LIMIT:
            init_evaluation_task.apply_async(args=[task_id, phase], countdown=3)
            return f"Dispatched {len(chunks)} batches for phase {phase}."
        else:
            # 最后一批，10秒后检查
            try_finalize_task_delayed.apply_async(args=[task_id], countdown=10)
            return f"Dispatched final batches for phase {phase}."

    except EvaluationTask.DoesNotExist:
        return f"Task {task_id} not found"
    except Exception as e:
        print(f"Error initializing task {task_id}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        _mark_task_failed(task_id, str(e))
        raise e


@shared_task
def process_evaluation_batch(task_id, item_ids, phase='both'):
    """
    【执行任务】Worker
    支持 phase 参数以配合双阶段执行逻辑
    """
    try:
        from .run_logic import run_single_item_logic
        for item_id in item_ids:
            run_single_item_logic(item_id, phase=phase)
    except Exception as e:
        print(f"Error processing batch for task {task_id}: {e}")
        traceback.print_exc()

@shared_task
def try_finalize_task_delayed(task_id):
    """
    【结算任务】Finalizer
    由 Dispatcher 触发，支持自我重试
    """
    try_finalize_task(task_id, from_dispatcher=True)

def _mark_task_failed(task_id, error_msg):
    try:
        t = EvaluationTask.objects.get(id=task_id)
        t.status = "failed"
        t.save()
    except:
        pass

