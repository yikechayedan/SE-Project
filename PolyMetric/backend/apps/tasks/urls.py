from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EvaluationTaskViewSet

# 注册路由：使用 DefaultRouter 自动生成 CRUD 接口
router = DefaultRouter()
router.register(r"evaluation-tasks", EvaluationTaskViewSet, basename="evaluation-task")

urlpatterns = [
    path("", include(router.urls)),  # 接口前缀：/api/tasks/evaluation-tasks/
]