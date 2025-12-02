from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsTaskCreatorOrAdmin(permissions.BasePermission):
    """评测任务权限控制"""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            raise PermissionDenied({"error": "请先登录"})
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if request.user == obj.creator:
            return True
        raise PermissionDenied({"error": "仅任务创建者或管理员可操作此评测任务"})