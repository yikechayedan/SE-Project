from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DatasetViewSet

router = DefaultRouter()
router.register(r"datasets", DatasetViewSet)  # 数据集接口前缀：/api/datasets/

urlpatterns = [
    path("", include(router.urls)),
]