from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="手机号")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="头像")
    bio = models.TextField(blank=True, null=True, verbose_name="个人简介")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="注册时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    # 新增隐私设置字段
    show_followed_models = models.BooleanField(default=True, verbose_name="公开关注的模型")
    show_followed_datasets = models.BooleanField(default=True, verbose_name="公开关注的数据集")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户管理"

# 新增用户关注关系模型
class UserFollow(models.Model):
    """用户关注关系"""
    follower = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='following',
        verbose_name='关注者'
    )
    followed = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='followers',
        verbose_name='被关注者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='关注时间')

    class Meta:
        unique_together = ('follower', 'followed')
        ordering = ['-created_at']
        verbose_name = "用户关注"
        verbose_name_plural = "用户关注"

    def __str__(self):
        return f"{self.follower.username} -> {self.followed.username}"