# apps/tasks/admin.py
from django.contrib import admin
from .models import EvaluationTask, EvaluationItem


@admin.register(EvaluationTask)
class EvaluationTaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "method",
        "creator",
        "dataset",
        "myModel",      # ⭐ 改成 myModel
        "status",
        "created_at",
    )
    search_fields = ("name", "creator__username", "dataset__name")
    list_filter = ("method", "status", "myModel")


@admin.register(EvaluationItem)
class EvaluationItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task",
        "content",
        "correct_answer",
        "predicted_answer",
        "score",
        "preference",
    )
    search_fields = ("content",)
    list_filter = ("score", "preference")
