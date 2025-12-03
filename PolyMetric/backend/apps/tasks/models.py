from django.db import models
from django.contrib.auth import get_user_model
from apps.datasets.models import Dataset

User = get_user_model()


# -----------------------------
# 模型：可评测模型（GPT-4V、Gemini 等）
# -----------------------------
class EvaluationModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


# -----------------------------
# 评测任务 Task
# -----------------------------
class EvaluationTask(models.Model):
    METHOD_CHOICES = (
        ("objective", "客观评测"),
        ("subjective", "主观评测"),
        ("adversarial", "对抗评测"),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_tasks"
    )

    dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE, related_name="tasks"
    )

    method = models.CharField(max_length=20, choices=METHOD_CHOICES)

    model = models.ForeignKey(
        EvaluationModel, on_delete=models.CASCADE, related_name="tasks"
    )

    # 任务状态：pending / running / completed
    status = models.CharField(max_length=20, default="pending")

    # 客观评测 accuracy
    accuracy = models.FloatField(null=True, blank=True)

    # 主观评测最终得分（平均分）
    score = models.FloatField(null=True, blank=True)

    # 评测总用时
    time_used = models.DurationField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


# -----------------------------
# 评测条目（数据集中的每一条数据）
# -----------------------------
class EvaluationItem(models.Model):
    task = models.ForeignKey(
        EvaluationTask, on_delete=models.CASCADE, related_name="items"
    )

    content = models.TextField()  # 题目内容 / 输入
    correct_answer = models.TextField(null=True, blank=True)
    predicted_answer = models.TextField(null=True, blank=True)

    # 客观评测是否正确
    is_correct = models.IntegerField(null=True, blank=True)

    # 主观评测得分（1-10）
    score = models.IntegerField(null=True, blank=True)

    # 对抗评测结果：left/right
    preference = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"Item {self.id} for Task {self.task_id}"
