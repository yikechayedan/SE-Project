from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="手机号")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="头像")
    bio = models.TextField(blank=True, null=True, verbose_name="个人简介")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="注册时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户管理"