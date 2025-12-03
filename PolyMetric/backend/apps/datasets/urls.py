from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DatasetViewSet

router = DefaultRouter()
router.register(r"datasets", DatasetViewSet)  # 数据集接口前缀：/api/datasets/

urlpatterns = [
    path("my_datasets/", DatasetViewSet.as_view({"get": "my_datasets"})),
    path("", include(router.urls)),
]