from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # 用户模块
    path("api/users/", include("apps.users.urls")),

<<<<<<< HEAD
    path("api/", include("apps.datasets.urls")),     # 数据集模块

    path("api/tasks/", include("apps.tasks.urls")),  # 评测任务
=======
    # 数据集模块
    path("api/", include("apps.datasets.urls")),
>>>>>>> f85d89d8896a32eff99aa2d1a6dbc86d6c5311cb
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
