from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # 用户模块
    path("api/users/", include("apps.users.urls")),

    path("api/", include("apps.datasets.urls")),     # 数据集模块

    path("api/tasks/", include("apps.tasks.urls")),  # 评测任务

    # 大模型模块（核心）
    path("api/", include("apps.models.urls")),

    # 系统动态模块
    path("api/system/", include("apps.system.urls")),
    
    # 模型排名模块
    path("api/rankings/", include("apps.rankings.urls")),
    
    # 评论系统模块
    path("api/", include("apps.comments.urls")),

    path('api/users/', include('apps.users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
