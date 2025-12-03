# apps/models/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModelViewSet

router = DefaultRouter()
# 原配置：router.register(r'models', ModelViewSet, basename='model')
router.register(r'', ModelViewSet, basename='model')  # 去掉前缀，直接使用主项目的 /api/models/

urlpatterns = [
    path('', include(router.urls)),
]