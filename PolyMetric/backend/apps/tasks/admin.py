# apps/tasks/admin.py
from django.contrib import admin
from .models import EvaluationTask, EvaluationItem
from .models import EvaluationSummary
from apps.tasks.run_logic import generate_adversarial_summary
from django.db.models import Avg
from django.db import models
@admin.register(EvaluationTask)
class EvaluationTaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "method",
        "creator",
        "dataset",
        "myModel",      
        "avg_score_display",
        "status",
        "created_at",
    )
    search_fields = ("name", "creator__username", "dataset__name")
    list_filter = ("method", "status", "myModel")
    def avg_score_display(self, obj):
            if hasattr(obj, "summary") and obj.summary.avg_score is not None:
                return obj.summary.avg_score
            return "-"
    avg_score_display.short_description = "平均分"


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
        items = task.items.all()
        total = items.count()

        if total == 0:
            return

        # =========================
        # 主观评测（人工裁判）
        # =========================
        if task.method == "subjective":
            valid = items.filter(score__isnull=False).count()
            if valid == total:
                avg = items.aggregate(avg=models.Avg("score"))["avg"]
                EvaluationSummary.objects.update_or_create(
                    task=task,
                    defaults={
                        "model_name": task.myModel.name,
                        "total": total,
                        "avg_score": round(avg, 4),
                    },
                )
                task.status = "completed"
                task.save(update_fields=["status"])

        # =========================
        # 对抗评测（人工裁判）
        # =========================
        elif task.method == "adversarial":
            valid = items.filter(preference__in=["left", "right", "tie"]).count()
            if valid == total:
                generate_adversarial_summary(task)
                task.status = "completed"
                task.save(update_fields=["status"])



@admin.register(EvaluationSummary)
class EvaluationSummaryAdmin(admin.ModelAdmin):
    list_display = (
        "task",
        "model_name",
        "total",
        "correct",
        "accuracy",
        "avg_score",
        "created_at",
    )
