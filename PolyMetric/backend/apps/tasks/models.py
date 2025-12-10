# apps/tasks/models.py
from django.db import models
from django.contrib.auth import get_user_model
from apps.datasets.models import Dataset
from apps.models.models import My_Model  # 使用大模型模块中的 My_Model

User = get_user_model()


# -----------------------------
# 评测任务 Task
# -----------------------------
class EvaluationTask(models.Model):
    METHOD_CHOICES = (
        ("objective", "客观评测"),
        ("subjective", "主观评测"),
        ("adversarial", "对抗评测"),
    )

    name = models.CharField(max_length=255, verbose_name="任务名称")
    description = models.TextField(null=True, blank=True, verbose_name="任务描述")

    # 创建者
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_tasks",
        verbose_name="创建者",
    )

    # 关联数据集
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="数据集",
    )

    # 评测方式：客观 / 主观 / 对抗
    method = models.CharField(
        max_length=20, choices=METHOD_CHOICES, verbose_name="评测方式"
    )

    # ⭐ 对齐 API 文档字段：myModel（ForeignKey 到 My_Model）
    myModel = models.ForeignKey(
        My_Model,
        on_delete=models.CASCADE,
        related_name="evaluation_tasks",
        verbose_name="评测模型",
        null=True,
        blank=True,
    )

    # 任务状态：pending / running / completed
    status = models.CharField(max_length=20, default="pending", verbose_name="任务状态")

    # 客观评测 accuracy
    accuracy = models.FloatField(null=True, blank=True, verbose_name="准确率")

    # 主观评测最终得分（平均分）
    score = models.FloatField(null=True, blank=True, verbose_name="评分")

    # 评测总用时
    time_used = models.DurationField(null=True, blank=True, verbose_name="用时")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "评测任务"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# -----------------------------
# 评测条目（数据集中的每一条数据）
# -----------------------------
class EvaluationItem(models.Model):
    task = models.ForeignKey(
        EvaluationTask,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="所属任务",
    )

    # 原始内容（例如题目 / 输入）
    content = models.TextField(verbose_name="内容")

    # 标准答案（客观评测用）
    correct_answer = models.TextField(null=True, blank=True, verbose_name="标准答案")

    # 模型预测答案
    predicted_answer = models.TextField(
        null=True, blank=True, verbose_name="模型预测答案"
    )

    # 客观评测是否正确（1/0）
    is_correct = models.IntegerField(null=True, blank=True, verbose_name="是否正确")

    # 主观评测得分（1-10）
    score = models.IntegerField(null=True, blank=True, verbose_name="主观评分")

    # 对抗评测结果：left/right
    preference = models.CharField(
        max_length=10, null=True, blank=True, verbose_name="偏好"
    )

    class Meta:
        verbose_name = "评测条目"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"Item {self.id} for Task {self.task_id}"
