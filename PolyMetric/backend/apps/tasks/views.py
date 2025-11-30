from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import EvaluationTask
from .serializers import EvaluationTaskSerializer
from .permissions import IsTaskCreatorOrAdmin

class EvaluationTaskViewSet(viewsets.ModelViewSet):
    """
    评测任务视图集（对齐用户接口格式）
    - 成功响应：直接返回数据（无 code/msg 字段）
    - 失败响应：返回 {"error": "错误信息"}
    """
    serializer_class = EvaluationTaskSerializer
    permission_classes = [IsTaskCreatorOrAdmin]

    def get_queryset(self):
        """数据过滤：管理员看全部，普通用户看自己的任务"""
        user = self.request.user
        return EvaluationTask.objects.all() if user.is_staff else EvaluationTask.objects.filter(creator=user)

    def create(self, request, *args, **kwargs):
        """新建评测任务（POST /api/tasks/evaluation-tasks/）"""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """查看单个任务详情（GET /api/tasks/evaluation-tasks/{id}/）"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """全量更新任务（PUT /api/tasks/evaluation-tasks/{id}/）"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """部分更新任务（PATCH /api/tasks/evaluation-tasks/{id}/）"""
        return self.update(request, *args, **kwargs, partial=True)

    def destroy(self, request, *args, **kwargs):
        """删除任务（DELETE /api/tasks/evaluation-tasks/{id}/）"""
        instance = self.get_object()
        self.perform_destroy(instance)
        # 删除成功返回空响应（符合 RESTful 规范）
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        """查看任务列表（GET /api/tasks/evaluation-tasks/）"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        # 列表响应：直接返回数据数组（与用户列表接口格式一致）
        return Response(serializer.data)