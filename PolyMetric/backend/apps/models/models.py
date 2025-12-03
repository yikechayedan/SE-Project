# 确保文件开头有正确的导入，且类定义无语法错误
from django.db import models

class Model(models.Model):
    """大模型信息"""
    name = models.CharField(max_length=100, verbose_name='模型名称')
    company = models.CharField(max_length=100, blank=True, null=True, verbose_name='所属公司')
    category = models.CharField(
        max_length=20,
        choices=[
            ('text', '文本生成'),
            ('image', '图像生成'),
            ('multimodal', '多模态'),
            ('code', '代码生成'),
        ],
        default='text',
        verbose_name='类型'
    )
    parameter_size = models.CharField(max_length=50, blank=True, null=True, verbose_name='参数量')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    version = models.CharField(max_length=50, blank=True, null=True, verbose_name='版本')
    release_date = models.DateField(blank=True, null=True, verbose_name='发布日期')
    official_url = models.URLField(blank=True, null=True, verbose_name='官方链接')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'models_model'
        verbose_name = '大模型'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class ModelFollow(models.Model):
    """模型关注关系"""
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='followed_models',
        verbose_name='用户'
    )
    model = models.ForeignKey(
        'Model',
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='模型'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='关注时间')

    class Meta:
        db_table = 'models_modelfollow'
        verbose_name = '模型关注'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'model')  # 防止重复关注
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 关注 {self.model.name}"