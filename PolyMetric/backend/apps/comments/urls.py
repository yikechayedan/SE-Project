from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet

# 注册视图集
router = DefaultRouter()
# 路由前缀为 comments，最终接口路径：/api/comments/
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    # 包含视图集的路由（列表、详情、like 操作）
    path("", include(router.urls)),
]