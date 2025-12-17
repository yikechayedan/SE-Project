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