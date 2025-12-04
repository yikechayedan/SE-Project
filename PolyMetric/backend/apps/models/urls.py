# apps/models/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModelViewSet, FollowedModelsListAPIView

# 注册视图集
router = DefaultRouter()
# 路由前缀为 models，最终接口路径：/api/models/
router.register(r"models", ModelViewSet, basename="my-model")

urlpatterns = [
    # 包含视图集的路由（列表、详情、follow/unfollow 操作）
    path("", include(router.urls)),
    # 用户关注的模型列表：/api/models/followed/
    path("models/followed/", FollowedModelsListAPIView.as_view(), name="followed-models"),
]