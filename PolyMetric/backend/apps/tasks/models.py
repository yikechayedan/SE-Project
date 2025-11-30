from django.db import models
from apps.users.models import User  # 关联用户模型
from apps.datasets.models import Dataset  # 关联数据集模型

class EvaluationTask(models.Model):
    """评测任务模型（对应 tasks 模块核心数据）"""
    # 任务状态枚举
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败')
    ]
    
    # 核心字段
    name = models.CharField(max_length=100, verbose_name="任务名称")
    description = models.TextField(blank=True, null=True, verbose_name="任务描述")
    creator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="created_tasks",  # 用户关联的任务（反向查询）
        verbose_name="创建者"
    )
    dataset = models.ForeignKey(
        Dataset, 
        on_delete=models.CASCADE, 
        related_name="related_tasks",  # 数据集关联的任务（反向查询）
        verbose_name="关联数据集"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending', 
        verbose_name="任务状态"
    )
    
    # 评测指标（自动计算，不可手动修改）
    accuracy = models.FloatField(null=True, blank=True, verbose_name="准确率")
    precision = models.FloatField(null=True, blank=True, verbose_name="精确率")
    recall = models.FloatField(null=True, blank=True, verbose_name="召回率")
    f1_score = models.FloatField(null=True, blank=True, verbose_name="F1分数")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "评测任务"
        verbose_name_plural = "评测任务"
        ordering = ["-created_at"]  # 按创建时间倒序排列
        db_table = "tasks_evaluation"  # 数据库表名（统一前缀 tasks_）

    def __str__(self):
        return f"[{self.status}] {self.name}"