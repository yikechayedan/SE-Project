from django.db import models
from apps.models.models import My_Model


class ModelRanking(models.Model):
    """
    模型排名表
    记录模型在不同数据集上的排名情况
    """
    model = models.ForeignKey(
        My_Model,
        on_delete=models.CASCADE,
        related_name='rankings',
        verbose_name='模型'
    )
    dataset = models.ForeignKey(
        'datasets.Dataset',
        on_delete=models.CASCADE,
        related_name='model_rankings',
        verbose_name='数据集'
    )
    rank = models.IntegerField(verbose_name='当前排名')
    score = models.FloatField(verbose_name='评分')
    previous_rank = models.IntegerField(null=True, blank=True, verbose_name='上次排名')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'rankings_model_ranking'
        verbose_name = '模型排名'
        verbose_name_plural = '模型排名'
        unique_together = ('model', 'dataset')
        ordering = ['dataset', 'rank']
    
    def __str__(self):
        return f"{self.model.name} - {self.dataset.name} - 排名: {self.rank}"


class RankingHistory(models.Model):
    """
    排名历史记录
    用于追踪模型排名的变化
    """
    model = models.ForeignKey(
        My_Model,
        on_delete=models.CASCADE,
        related_name='ranking_history',
        verbose_name='模型'
    )
    dataset = models.ForeignKey(
        'datasets.Dataset',
        on_delete=models.CASCADE,
        related_name='ranking_history',
        verbose_name='数据集'
    )
    rank = models.IntegerField(verbose_name='排名')
    score = models.FloatField(verbose_name='评分')
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name='记录时间')
    
    class Meta:
        db_table = 'rankings_history'
        verbose_name = '排名历史'
        verbose_name_plural = '排名历史'
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.model.name} - {self.dataset.name} - 排名: {self.rank} - {self.recorded_at}"


class ModelDimensionScore(models.Model):
    """
    模型维度得分表
    存储模型在各个特定能力维度上的聚合分数
    """
    DIMENSION_CHOICES = [
        ('overall', '综合能力'),
        ('language', '语言理解'),
        ('math', '数学推理'),
        ('code', '代码能力'),
        ('multimodal', '多模态'),
    ]

    model = models.ForeignKey(
        'models.My_Model',
        on_delete=models.CASCADE,
        related_name='dimension_scores',
        verbose_name='模型'
    )
    dimension = models.CharField(
        max_length=20,
        choices=DIMENSION_CHOICES,
        db_index=True,
        verbose_name="评测维度"
    )
    score = models.FloatField(default=0.0, verbose_name="得分")
    
    # 用于趋势计算：存储上一次更新时的分数或排名
    previous_score = models.FloatField(default=0.0, verbose_name="上次得分")
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'rankings_dimension_score'
        verbose_name = '模型维度得分'
        verbose_name_plural = '模型维度得分'
        unique_together = ('model', 'dimension')  # 核心约束
        indexes = [
            models.Index(fields=['dimension', '-score']),  # 核心索引：加速"按维度查排行榜"
        ]
        ordering = ['dimension', '-score']
    
    def __str__(self):
        return f"{self.model.name} - {self.get_dimension_display()} - {self.score}"
    
    def get_trend(self):
        """获取趋势：up/down/stable"""
        if self.previous_score == 0:
            return 'stable'
        if self.score > self.previous_score:
            return 'up'
        elif self.score < self.previous_score:
            return 'down'
        else:
            return 'stable'