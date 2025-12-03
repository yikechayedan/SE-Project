# apps/tasks/views.py

from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from .models import EvaluationTask, EvaluationItem, EvaluationModel
from .serializers import (
    EvaluationTaskSerializer,
    EvaluationTaskDetailSerializer,
)
from .permissions import IsTaskOwnerOrAdmin

User = get_user_model()


class EvaluationTaskViewSet(viewsets.ModelViewSet):
    """
    严格对齐 API 文档的 Task ViewSet：
    - POST   /evaluation-tasks/           创建任务
    - GET    /evaluation-tasks/           列表
    - GET    /evaluation-tasks/{id}/      详情（仅创建者或管理员）
    - PUT    /evaluation-tasks/{id}/      全量更新（仅创建者或管理员）
    - PATCH  /evaluation-tasks/{id}/      部分更新（仅创建者或管理员）
    - DELETE /evaluation-tasks/{id}/      删除（仅创建者或管理员）
    - POST   /evaluation-tasks/{id}/      提交主观 / 对抗评分
    """

    queryset = EvaluationTask.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EvaluationTaskDetailSerializer
        return EvaluationTaskSerializer

    # -----------------------------
    # 工具：检查是否任务创建者或管理员
    # 返回 Response 表示无权限；返回 None 表示通过
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
    # 1 创建任务  POST /evaluation-tasks/
    # -----------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # 文档中 400 的 error 是一个字符串形式的 dict
            return Response({"error": str(serializer.errors)}, status=400)

        # creator 从当前登录用户自动填充
        serializer.save(creator=request.user)
        task = serializer.instance
        # 返回完整对象，字段与文档一致
        data = self.get_serializer(task).data
        return Response(data, status=status.HTTP_201_CREATED)

    # -----------------------------
    # 2 获取列表  GET /evaluation-tasks/
    # -----------------------------
    def list(self, request, *args, **kwargs):
        tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    # -----------------------------
    # 3 获取单条详情  GET /evaluation-tasks/{id}/
    # 仅创建者或管理员
    # -----------------------------
    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        perm = self._check_owner_or_admin(request, task)
        if perm is not None:
            return perm

        serializer = self.get_serializer(task)
        return Response(serializer.data)

    # -----------------------------
    # 4 全量更新  PUT /evaluation-tasks/{id}/
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
    # 5 部分更新  PATCH /evaluation-tasks/{id}/
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
    # 6 删除任务  DELETE /evaluation-tasks/{id}/
    # -----------------------------
    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        perm = self._check_owner_or_admin(request, task)
        if perm is not None:
            return perm

        task.delete()
        return Response(status=204)

    # -----------------------------
    # 7 / 8 提交主观 / 对抗评测（一题一传）
    # POST /evaluation-tasks/{id}/
    # -----------------------------
    def submit_score(self, request, pk=None):
        """
        请求示例（主观）：
        {
          "method": "subjective",
          "model": 1,
          "dataset": 1,
          "reviewer": 1,
          "time_stamp": "2025-11-30T10:00:00Z",
          "itemID": 1,
          "score": 6
        }

        请求示例（对抗）：
        {
          "method": "adversarial",
          "model": 1,
          "dataset": 1,
          "reviewer": 1,
          "time_stamp": "2025-11-30T10:00:00Z",
          "itemID": 1,
          "preference": "left"
        }

        失败响应（400）：
        {
          "error": "Task or Reviewer ID not found, or all items are completed."
        }
        """
        try:
            task = EvaluationTask.objects.get(pk=pk)
        except EvaluationTask.DoesNotExist:
            return Response(
                {"error": "Task or Reviewer ID not found, or all items are completed."},
                status=400
            )

        method = request.data.get("method")
        model_id = request.data.get("model")
        dataset_id = request.data.get("dataset")
        reviewer_id = request.data.get("reviewer")
        item_id = request.data.get("itemID")
        score = request.data.get("score")
        preference = request.data.get("preference")

        # 校验 reviewer 存在
        try:
            reviewer = User.objects.get(id=reviewer_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Task or Reviewer ID not found, or all items are completed."},
                status=400
            )

        # 校验 model/dataset 与 task 一致
        if task.model_id != int(model_id) or task.dataset_id != int(dataset_id):
            return Response(
                {"error": "Task or Reviewer ID not found, or all items are completed."},
                status=400
            )

        # 获取条目
        try:
            item = EvaluationItem.objects.get(task=task, id=item_id)
        except EvaluationItem.DoesNotExist:
            return Response(
                {"error": "Task or Reviewer ID not found, or all items are completed."},
                status=400
            )

        # 根据 method 写入不同字段
        if method == "subjective":
            if score is None:
                return Response(
                    {"error": "Task or Reviewer ID not found, or all items are completed."},
                    status=400
                )
            item.score = int(score)
        elif method == "adversarial":
            if preference is None:
                return Response(
                    {"error": "Task or Reviewer ID not found, or all items are completed."},
                    status=400
                )
            item.preference = preference
        else:
            return Response(
                {"error": "Task or Reviewer ID not found, or all items are completed."},
                status=400
            )

        item.save()
        # 文档没有要求返回内容，返回一个空对象即可
        return Response({}, status=200)


# --------------------------------------------------
# 9. 请求待测条目列表
# GET /api/tasks/get-pending-items?task=1&reviewer=1
# --------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_items(request):
    """
    成功响应（200）：
    {
      "task": 1,
      "reviewer": 1,
      "pending_count": 98,
      "pengdingItem_ids": ["1", "2", ...]
    }
    """
    # 兼容几种参数名：task / taskid / task_id
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
        return Response({"error": "Task or Reviewer ID not found, or all items are completed."}, status=400)

    try:
        task = EvaluationTask.objects.get(id=task_id)
    except EvaluationTask.DoesNotExist:
        return Response({"error": "Task or Reviewer ID not found, or all items are completed."}, status=400)

    # reviewer 仅用于记录，可以校验是否存在
    try:
        User.objects.get(id=reviewer_id)
    except User.DoesNotExist:
        return Response({"error": "Task or Reviewer ID not found, or all items are completed."}, status=400)

    pending = task.items.filter(score__isnull=True, preference__isnull=True)
    ids = [str(i.id) for i in pending]

    # 注意：字段名故意使用文档中的拼写 pengdingItem_ids
    return Response({
        "task": task.id,
        "reviewer": reviewer_id,
        "pending_count": len(ids),
        "pengdingItem_ids": ids,
    }, status=200)


# --------------------------------------------------
# 10. 请求条目详情（主观 / 对抗评测界面条目展示）
# GET /api/tasks/get-item-detail
# --------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_item_detail(request):
    """
    请求格式（JSON 或 query）：
    {
      "task": 1,
      "itemID": 1
    }

    成功响应（200）：
    {
      "method": "subjective",
      "itemID": 1,
      "item_content": {
        "input_query": "...",
        "model1_response": "...",
        "model2_response": null
      }
    }
    """
    # 兼容 query 参数和 body
    task_param = (
        request.query_params.get("task")
        or request.data.get("task")
    )
    item_param = (
        request.query_params.get("itemID")
        or request.data.get("itemID")
    )

    try:
        task_id = int(task_param)
        item_id = int(item_param)
    except (TypeError, ValueError):
        return Response({"error": "Task or item not found"}, status=400)

    try:
        task = EvaluationTask.objects.get(id=task_id)
        item = EvaluationItem.objects.get(task=task, id=item_id)
    except (EvaluationTask.DoesNotExist, EvaluationItem.DoesNotExist):
        return Response({"error": "Task or item not found"}, status=400)

    return Response({
        "method": task.method,
        "itemID": item.id,
        "item_content": {
            "input_query": item.content,
            "model1_response": item.predicted_answer,
            "model2_response": None,   # 对抗评测模式下可用
        },
    }, status=200)
