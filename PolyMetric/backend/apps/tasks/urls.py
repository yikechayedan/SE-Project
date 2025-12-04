# apps/tasks/urls.py
from .views import run_task
from django.urls import path
from .views import (
    EvaluationTaskViewSet,
    get_pending_items,
    get_item_detail,
)

# 我们不用 DefaultRouter，而是手动绑定所有 HTTP 方法到 ViewSet 的 action，
# 这样可以完全控制 URL 形态，严格对齐 API 文档。

evaluation_task_list = EvaluationTaskViewSet.as_view({
    "get": "list",      # GET /evaluation-tasks/
    "post": "create",   # POST /evaluation-tasks/
})

evaluation_task_detail = EvaluationTaskViewSet.as_view({
    "get": "retrieve",          # GET /evaluation-tasks/{id}/
    "put": "update",            # PUT /evaluation-tasks/{id}/
    "patch": "partial_update",  # PATCH /evaluation-tasks/{id}/
    "delete": "destroy",        # DELETE /evaluation-tasks/{id}/
    "post": "submit_score",     # POST /evaluation-tasks/{id}/  7/8 提交评分
})

urlpatterns = [
    # 1/2 创建 & 列表
    path("evaluation-tasks/", evaluation_task_list, name="evaluation-task-list"),

    # 3/4/5/6/7/8 详情+修改+删除+提交评分
    path("evaluation-tasks/<int:pk>/", evaluation_task_detail, name="evaluation-task-detail"),

    # 9 请求待测条目列表
    path("get-pending-items", get_pending_items, name="get-pending-items"),

    # 10 请求条目详情
    path("get-item-detail", get_item_detail, name="get-item-detail"),

    path("run-task", run_task),
]
