# apps/models/permissions.py
from rest_framework import permissions

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    读操作允许匿名访问，写操作（关注/取消关注）需要登录
    """
    def has_permission(self, request, view):
        # GET、HEAD、OPTIONS请求允许匿名访问
        if request.method in permissions.SAFE_METHODS:
            return True
        # 其他请求需要登录
        return request.user and request.user.is_authenticated