# apps/tasks/permissions.py
from rest_framework import permissions


class IsTaskOwnerOrAdmin(permissions.BasePermission):
    """
    仅任务创建者或管理员可操作此评测任务
    """

    message = "仅任务创建者或管理员可操作此评测任务"

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return getattr(obj, "creator_id", None) == user.id
