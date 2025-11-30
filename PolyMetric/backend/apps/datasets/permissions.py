from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsCreatorOrAdminOrPublic(permissions.BasePermission):
    """
    权限规则：
    - 公开且已审核的数据集：允许所有用户访问
    - 私有数据集/未审核的公开数据集：仅创建者或管理员访问
    """
    def has_object_permission(self, request, view, obj):
        # 管理员拥有所有权限
        if request.user.is_staff:
            return True
        # 创建者拥有所有权限
        if request.user == obj.creator:
            return True
        # 公开且已审核的数据集：允许访问（列表/详情）
        if obj.is_public and obj.is_verified:
            return True
        
        # 权限不足时抛出带信息的异常
        raise PermissionDenied("无访问权限：该数据集为私有或未通过审核")