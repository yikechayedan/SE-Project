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
def init_evaluation_task(self, task_id):
    """
    【智能调度任务】Smart Dispatcher
    采用 "Lazy/Chunked Dispatch" 模式
    """
    try:
        task = EvaluationTask.objects.get(id=task_id)
        
        # 1. 首次运行时，确保所有 Item 已创建
        # 修正：检查 items 是否存在，而不是状态。因为 run_task 可能已将其设为 running
        if not task.items.exists():
            prepare_evaluation_items(task)
            if task.status != "running":
                task.status = "running"
                task.save(update_fields=["status"])
        
        # 2. 捞取一小批待处理的 ID
        pending_ids = get_pending_item_ids(task, limit=DISPATCH_LIMIT)
        print(f"[DEBUG] Task {task_id}: Fetched {len(pending_ids)} pending IDs. Batch Size: {BATCH_SIZE}")
        
        if not pending_ids:
            # 没有待处理的了？触发 Finalizer，并告诉它是调度器触发的
            try_finalize_task(task_id, from_dispatcher=True)
            return f"Task {task_id} dispatch finished (no pending items)."

        # 3. 切片分发
        chunks = [pending_ids[i:i + BATCH_SIZE] for i in range(0, len(pending_ids), BATCH_SIZE)]

        for chunk_ids in chunks:
            process_evaluation_batch.delay(task_id, chunk_ids)
            
        # 4. 自我驱动
        if len(pending_ids) >= DISPATCH_LIMIT:
            # 还有更多，继续调度
            init_evaluation_task.apply_async(args=[task_id], countdown=3)
            return f"Dispatched {len(chunks)} batches. Scheduled next dispatch in 3s."
        else:
            # 这是最后一批了！
            # 安排一个延后的 Finalize Check，给 Worker 一点时间跑完最后一批
            # 这里调用 delayed task，而不是直接调用同步函数
            try_finalize_task_delayed.apply_async(args=[task_id], countdown=10)
            return f"Dispatched final {len(chunks)} batches. Scheduled finalize check."

    except EvaluationTask.DoesNotExist:
        return f"Task {task_id} not found"
    except Exception as e:
        print(f"Error initializing task {task_id}: {str(e)}")
        print(traceback.format_exc())
        _mark_task_failed(task_id, str(e))
        raise e

@shared_task
def process_evaluation_batch(task_id, item_ids):
    """
    【执行任务】Worker
    只负责执行，不再负责触发 Finalize (优化性能)
    """
    try:
        for item_id in item_ids:
            run_single_item_logic(item_id)
        
        # 移除 try_finalize_task(task_id) 的调用
        # 由 Dispatcher 统一触发结算
        
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

