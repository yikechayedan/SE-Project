# apps/tasks/views.py
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from .run_logic import run_evaluation
from .tasks import init_evaluation_task
from .models import EvaluationTask, EvaluationItem
from .serializers import (
    EvaluationTaskSerializer,
    EvaluationTaskDetailSerializer,
)
from .benchmark import run_benchmark


User = get_user_model()


class EvaluationTaskViewSet(viewsets.ModelViewSet):
    queryset = EvaluationTask.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EvaluationTaskDetailSerializer
        return EvaluationTaskSerializer

    # -----------------------------
    # 工具：检查是否任务创建者或管理员
    # -----------------------------
    def _check_owner_or_admin(self, request, task: EvaluationTask):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "仅任务创建者或管理员可操作此评测任务"}, status=403)
        if user.is_staff:
            return None
        if task.creator_id != user.id:
            return Response({"error": "仅任务创建者或管理员可操作此评测任务"}, status=403)
        return None

    # -----------------------------
    # 1 创建任务：POST /api/tasks/evaluation-tasks/
    # -----------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": str(serializer.errors)}, status=400)

        # creator 固定为当前登录用户
        serializer.save(creator=request.user)
        task = serializer.instance
        data = self.get_serializer(task).data
        return Response(data, status=status.HTTP_201_CREATED)

    # -----------------------------
    # 2 列表：GET /api/tasks/evaluation-tasks/
    # -----------------------------
    def list(self, request, *args, **kwargs):
        tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    # -----------------------------
    # 3 详情：GET /api/tasks/evaluation-tasks/{id}/
    # -----------------------------
    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        perm = self._check_owner_or_admin(request, task)
        if perm is not None:
            return perm

        serializer = self.get_serializer(task)
        return Response(serializer.data)

    # -----------------------------
    # 4 全量更新：PUT /api/tasks/evaluation-tasks/{id}/
    # -----------------------------
    def update(self, request, *args, **kwargs):
        task = self.get_object()
        perm = self._check_owner_or_admin(request, task)
        if perm is not None:
            return perm

        serializer = self.get_serializer(task, data=request.data)
        if not serializer.is_valid():
            return Response({"error": str(serializer.errors)}, status=400)
        serializer.save()
        return Response(serializer.data)

    # -----------------------------
    # 5 部分更新：PATCH /api/tasks/evaluation-tasks/{id}/
    # -----------------------------
    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        perm = self._check_owner_or_admin(request, task)
        if perm is not None:
            return perm

        serializer = self.get_serializer(task, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({"error": str(serializer.errors)}, status=400)
        serializer.save()
        return Response(serializer.data)

    # -----------------------------
    # 6 删除任务：DELETE /api/tasks/evaluation-tasks/{id}/
    # -----------------------------
    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        perm = self._check_owner_or_admin(request, task)
        if perm is not None:
            return perm

        task.delete()
        return Response(status=204)

    # -----------------------------
    # 7 / 8 提交主观 / 对抗评分：
    #    POST /api/tasks/evaluation-tasks/{id}/
    #    body 里包含：
    #    {
    #      "myModel": 1,
    #      "dataset": 1,
    #      "reviewer": 1,
    #      "time_stamp": "...",   # 可选，目前未使用
    #      "itemID": 1,
    #      "score": 6,           # 主观
    #      "preference": "left"  # 对抗
    #    }
    # -----------------------------
    def submit_score(self, request, pk=None):
        try:
            task = EvaluationTask.objects.get(pk=pk)
        except EvaluationTask.DoesNotExist:
            return Response({"error": "Task not found"}, status=400)

        # method 直接以任务本身为准，不强依赖前端传的 method
        method = task.method

        my_model_id = request.data.get("myModel")
        dataset_id = request.data.get("dataset")
        reviewer_id = request.data.get("reviewer")
        item_id = request.data.get("itemID")
        score = request.data.get("score")
        preference = request.data.get("preference")

        # 校验 reviewer 是否存在
        try:
            reviewer = User.objects.get(id=reviewer_id)
        except (User.DoesNotExist, TypeError, ValueError):
            return Response({"error": "Reviewer not found"}, status=400)

        # ⭐ 校验 myModel 和 dataset 是否与任务一致（使用 My_Model）
        try:
            if int(my_model_id) != task.myModel_id or int(dataset_id) != task.dataset_id:
                return Response({"error": "Model or dataset mismatch"}, status=400)
        except (TypeError, ValueError):
            return Response({"error": "Invalid myModel or dataset id"}, status=400)

        # 找到对应条目
        try:
            item = EvaluationItem.objects.get(task=task, id=item_id)
        except (EvaluationItem.DoesNotExist, TypeError, ValueError):
            return Response({"error": "Item not found"}, status=400)

        # 根据任务类型填充字段
        if method == "subjective":
            # 主观评分必须有 score
            try:
                item.score = int(score)
            except (TypeError, ValueError):
                return Response({"error": "Invalid score"}, status=400)

        elif method == "adversarial":
            # 对抗评测必须有 preference
            if preference not in ("left", "right", "tie"):
                return Response({"error": "Invalid preference"}, status=400)
            item.preference = preference
        else:
            # 目前文档只定义了主观 & 对抗两类提交
            return Response({"error": "Invalid method for submit_score"}, status=400)

        item.save()
        
        # -----------------------------
        # 新增：检查是否所有条目都已评测完成
        # -----------------------------
        is_completed = False
        if method == "subjective":
            # 检查是否还有未评分的条目
            if not task.items.filter(score__isnull=True).exists():
                is_completed = True
                # 计算平均分
                from django.db.models import Avg
                avg_score = task.items.aggregate(Avg("score"))["score__avg"]
                task.score = avg_score

        elif method == "adversarial":
            # 检查是否还有未选偏好的条目
            if not task.items.filter(preference__isnull=True).exists():
                is_completed = True
                # 对抗评测可能需要计算胜率等，暂只更新状态

        if is_completed:
            task.status = "completed"
            task.save()

            # --- 新增：自动生成汇总报告并更新排行榜 ---
            from .models import EvaluationSummary
            from apps.rankings.services import update_model_rankings

            # 1. 创建/更新 EvaluationSummary
            summary, created = EvaluationSummary.objects.get_or_create(task=task)
            summary.model_name = task.myModel.name
            
            if method == "subjective":
                summary.avg_score = task.score
            elif method == "adversarial":
                # 简单计算对抗评测的胜率（相对于 Model A），平局算 0.5 胜
                total_items = task.items.count()
                if total_items > 0:
                    win_count = task.items.filter(preference="left").count()
                    tie_count = task.items.filter(preference="tie").count()
                    
                    summary.correct = win_count  # 胜场仅记录完全胜利
                    summary.total = total_items
                    # 胜率 = (胜场 + 0.5 * 平局) / 总数
                    summary.accuracy = (win_count + 0.5 * tie_count) / total_items
            
            summary.save()

            # 2. 触发排行榜更新
            update_model_rankings(task.dataset_id)

        # 此处暂不记录 reviewer / time_stamp，可根据需要扩展模型
        return Response({}, status=200)


# --------------------------------------------------
# 9. 请求待测条目列表：
#    GET /api/tasks/get-pending-items?taskid=1&reviewerid=1
# --------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_items(request):
    task_param = (
        request.query_params.get("task")
        or request.query_params.get("taskid")
        or request.query_params.get("task_id")
    )
    reviewer_param = (
        request.query_params.get("reviewer")
        or request.query_params.get("reviewerid")
        or request.query_params.get("reviewer_id")
    )

    try:
        task_id = int(task_param)
        reviewer_id = int(reviewer_param)
    except (TypeError, ValueError):
        return Response({"error": "Invalid parameters"}, status=400)

    try:
        task = EvaluationTask.objects.get(id=task_id)
    except EvaluationTask.DoesNotExist:
        return Response({"error": "Task not found"}, status=400)

    try:
        User.objects.get(id=reviewer_id)
    except User.DoesNotExist:
        return Response({"error": "Reviewer not found"}, status=400)

    # 1. 获取全部条目的 QuerySet
    all_items_qs = task.items.all()
    all_ids = [str(item.id) for item in all_items_qs]

    # 2. 获取“待评测”条目 (score 和 preference 都为空)
    pending_items_qs = all_items_qs.filter(score__isnull=True, preference__isnull=True)
    pending_ids = [str(item.id) for item in pending_items_qs]

    # 3. 获取“已评测”条目 (score 不为空 OR preference 不为空)
    completed_items_qs = all_items_qs.exclude(score__isnull=True, preference__isnull=True)
    
    # 构造已评测数据的列表，包含 id 及其评分/偏好
    completed_data = []
    for item in completed_items_qs:
        completed_data.append({
            "id": str(item.id),
            "score": item.score,
            "preference": item.preference
        })

    return Response(
        {
            "task": task.id,
            "reviewer": reviewer_id,
            "total_count": len(all_ids),
            "all_item_ids": all_ids,
            "pending_count": len(pending_ids),
            "pending_item_ids": pending_ids,
            "completed_count": len(completed_data),
            "completed_items": completed_data  # 返回详细的已评测信息
        }
    )

# --------------------------------------------------
# 10. 请求单条条目详情：
#     GET /api/tasks/get-item-detail?task=1&itemID=1
# --------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_item_detail(request):
    task_param = request.query_params.get("task") or request.data.get("task")
    item_param = request.query_params.get("itemID") or request.data.get("itemID")

    try:
        task_id = int(task_param)
        item_id = int(item_param)
    except (TypeError, ValueError):
        return Response({"error": "Invalid parameters"}, status=400)

    try:
        task = EvaluationTask.objects.get(id=task_id)
        item = EvaluationItem.objects.get(task=task, id=item_id)
    except (EvaluationTask.DoesNotExist, EvaluationItem.DoesNotExist):
        return Response({"error": "Task or item not found"}, status=400)

    return Response(
        {
            "method": task.method,
            "itemID": item.id,
            "item_content": {
                "input_query": item.content,
                "myModel1_response": item.predicted_answer,  # 对齐文档中的 myModel1_response
                "myModel2_response": item.predicted_answer_2,  # 对抗评测下启用，可后续扩展
            },
        }
    )


# --------------------------------------------------
# 11. 手动运行任务：POST /api/tasks/run-task
# --------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def run_task(request):
    task_id = request.data.get("task_id")

    try:
        task = EvaluationTask.objects.get(id=task_id)
    except EvaluationTask.DoesNotExist:
        return Response({"error": "task not found"}, status=404)

    # 改为异步调用：提交给 Celery Worker
    from .tasks import init_evaluation_task
    init_evaluation_task.delay(task_id)
    
    # 立即返回，前端无需等待 60s+
    return Response({
        "msg": "Task submitted to background queue", 
        "status": "pending",
        "task_id": task_id
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def run_benchmark_view(request):
    """
    POST /api/tasks/run-benchmark/
    {
        "dataset": 1,
        "models": [1,2,3],
        "max_workers": 3   # 可选
    }
    """
    dataset_id = request.data.get("dataset")
    model_ids = request.data.get("models")
    max_workers = request.data.get("max_workers", 3)
    method = request.data.get("method", "objective")
    if not dataset_id or not model_ids:
        return Response({"error": "dataset and models are required"}, status=400)

    results = run_benchmark(
        creator=request.user,
        dataset_id=dataset_id,
        model_ids=model_ids,
        method=method,
        max_workers=max_workers,
    )

    return Response(results, status=200)
