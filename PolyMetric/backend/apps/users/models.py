from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

class User(AbstractUser):
    # 覆盖 AbstractUser 的 email 字段，使其唯一
    email = models.EmailField(unique=True, verbose_name="邮箱")
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True, verbose_name="手机号")
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


class UserStar(models.Model):
    """
    通用用户点赞表
    支持对任意模型（Model, Dataset, Article...）进行点赞
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stars',
        verbose_name='用户'
    )
    
    # 通用外键配置
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')

    class Meta:
        verbose_name = '用户点赞'
        verbose_name_plural = verbose_name
        # 核心约束：一个用户对同一个对象只能点赞一次
        unique_together = ('user', 'content_type', 'object_id')
        indexes = [
            # 优化查询：按对象类型和ID查找（用于统计总数）
            models.Index(fields=["content_type", "object_id"]),
            # 优化查询：按用户查找（用于"我的点赞"）
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user} starred {self.content_type} {self.object_id}"