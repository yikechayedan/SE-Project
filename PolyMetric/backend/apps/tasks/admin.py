from django.contrib import admin
from .models import EvaluationTask

@admin.register(EvaluationTask)
class EvaluationTaskAdmin(admin.ModelAdmin):
    """后台评测任务管理界面配置"""
    list_display = ["id", "name", "creator", "dataset", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["name", "description", "creator__username", "dataset__name"]
    readonly_fields = ["created_at", "updated_at", "accuracy", "precision", "recall", "f1_score"]
    fieldsets = (
        ("基本信息", {
            "fields": ("name", "description", "creator", "dataset")
        }),
        ("任务状态", {
            "fields": ("status",)
        }),
        ("评测结果", {
            "fields": ("accuracy", "precision", "recall", "f1_score"),
            "classes": ("collapse",)  # 可折叠
        }),
        ("时间信息", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )