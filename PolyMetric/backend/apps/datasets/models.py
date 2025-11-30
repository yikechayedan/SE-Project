from django.db import models
from django.conf import settings
from apps.users.models import User  # 关联用户模型

class Dataset(models.Model):
    """数据集模型"""
    # 基础信息
    name = models.CharField(max_length=100, verbose_name="数据集名称")
    description = models.TextField(blank=True, null=True, verbose_name="数据集描述")
    category = models.CharField(max_length=50, verbose_name="数据集类型", 
                                choices=[("image", "图像"), ("text", "文本"), ("multimodal", "多模态")])
    file_format = models.CharField(max_length=20, verbose_name="文件格式", 
                                   choices=[("csv", "CSV"), ("json", "JSON"), ("zip", "ZIP")])
    file_size = models.FloatField(verbose_name="文件大小(MB)")  # 存储文件大小，单位MB
    file_path = models.FileField(upload_to="datasets/%Y/%m/%d/", verbose_name="数据集文件路径")  # 存储文件
    sample_count = models.IntegerField(verbose_name="样本数量", null=True, blank=True)  # 样本数（可选）
    
    # 权限与关联
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_datasets", verbose_name="创建者")
    is_public = models.BooleanField(default=True, verbose_name="是否公开")  # 公开/私有
    is_verified = models.BooleanField(default=False, verbose_name="是否通过管理员审核")  # 管理员审核
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "数据集"
        verbose_name_plural = "数据集"
        ordering = ["-created_at"]  # 按创建时间倒序

    def __str__(self):
        return self.name