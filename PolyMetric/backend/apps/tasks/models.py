from django.db import models
from django.contrib.auth import get_user_model
from apps.datasets.models import Dataset
from apps.models.models import My_Model  # 大模型表
User = get_user_model()


# =============================
# 评测任务 Task
# =============================
class EvaluationTask(models.Model):
    METHOD_CHOICES = (
        ("objective", "客观评测"),
        ("subjective", "主观评测"),
        ("adversarial", "对抗评测"),
    )

    name = models.CharField(max_length=255, verbose_name="任务名称")
    description = models.TextField(null=True, blank=True, verbose_name="任务描述")

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_tasks",
        verbose_name="创建者",
    )

    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="数据集",
    )

    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        verbose_name="评测方式",
    )

    # =============================
    # Model A（所有评测都用）
    # =============================
    myModel = models.ForeignKey(
        My_Model,
        on_delete=models.CASCADE,
        related_name="evaluation_tasks_as_model_a",
        verbose_name="评测模型 A",
    )

    # =============================
    # ⭐ Model B（仅对抗评测使用）
    # =============================
    myModel_2 = models.ForeignKey(
        My_Model,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="evaluation_tasks_as_model_b",
        verbose_name="评测模型 B（对抗）",
    )

    status = models.CharField(
        max_length=20,
        default="pending",
        verbose_name="任务状态",
    )

    # 客观评测
    accuracy = models.FloatField(null=True, blank=True, verbose_name="准确率")

    # 主观评测
    score = models.FloatField(null=True, blank=True, verbose_name="评分")

    time_used = models.DurationField(null=True, blank=True, verbose_name="用时")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "评测任务"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# =============================
# 评测条目 Item
# =============================
class EvaluationItem(models.Model):
    task = models.ForeignKey(
        EvaluationTask,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="所属任务",
    )

    content = models.TextField(verbose_name="内容")

    correct_answer = models.TextField(
        null=True,
        blank=True,
        verbose_name="标准答案",
    )

    # ===== Model A 回答 =====
    predicted_answer = models.TextField(
        null=True,
        blank=True,
        verbose_name="模型 A 回答",
    )

    # ===== Model B 回答（对抗）=====
    predicted_answer_2 = models.TextField(
        null=True,
        blank=True,
        verbose_name="模型 B 回答",
    )

    # 客观评测
    is_correct = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="是否正确",
    )

    # 主观评测
    score = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="主观评分",
    )

    # 对抗评测（人类裁判）
    preference = models.CharField(
        max_length=10,
        choices=(
            ("left", "Model A"),
            ("right", "Model B"),
            ("tie", "Tie"),
        ),
        null=True,
        blank=True,
        verbose_name="偏好",
    )

    

    class Meta:
        verbose_name = "评测条目"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"Item {self.id} for Task {self.task_id}"


# =============================
# 评测结果汇总 Summary
# =============================
class EvaluationSummary(models.Model):
    task = models.OneToOneField(
        EvaluationTask,
        on_delete=models.CASCADE,
        related_name="summary",
        verbose_name="评测任务",
    )

    model_name = models.CharField(max_length=200, verbose_name="模型信息")

    total = models.IntegerField(null=True, blank=True, verbose_name="总数")

    # 客观 / 对抗：语义化使用
    correct = models.IntegerField(null=True, blank=True, verbose_name="胜场 / 正确数")

    accuracy = models.FloatField(null=True, blank=True, verbose_name="准确率 / 胜率")

    # 主观评测
    avg_score = models.FloatField(null=True, blank=True, verbose_name="平均分")

    summary = models.TextField(null=True, blank=True, verbose_name="文本总结")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "评测结果汇总"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"Task {self.task_id} - {self.model_name}"
