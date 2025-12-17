# apps/tasks/admin.py
from django.contrib import admin
from .models import EvaluationTask, EvaluationItem
from .models import EvaluationSummary
from apps.tasks.run_logic import generate_adversarial_summary
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
        "predicted_answer_2", 
        "score",
        "preference",
    )
    search_fields = ("content",)
    list_filter = ("score", "preference")
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        task = obj.task
        if task.method != "adversarial":
            return

        # 如果所有 item 都已经打分，自动生成 Summary
        items = task.items.all()
        if items.exists() and not items.filter(preference__isnull=True).exists():
            generate_adversarial_summary(task)


@admin.register(EvaluationSummary)
class EvaluationSummaryAdmin(admin.ModelAdmin):
    list_display = (
        "task",
        "model_name",
        "total",
        "correct",
        "accuracy",
        "created_at",
    )
