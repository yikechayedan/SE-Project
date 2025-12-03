from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # 用户模块
    path("api/users/", include("apps.users.urls")),

    path("api/datasets/", include("apps.datasets.urls")),     # 数据集模块

    path('api/models/', include('apps.models.urls')),      # 新增：模型路由（前缀 api/）

    path("api/tasks/", include("apps.tasks.urls")),  # 评测任务
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
