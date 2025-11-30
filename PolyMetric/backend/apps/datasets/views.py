from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Dataset
from .serializers import DatasetSerializer, DatasetDetailSerializer
from .permissions import IsCreatorOrAdminOrPublic  # 自定义权限

class DatasetViewSet(viewsets.ModelViewSet):
    """数据集视图集：支持增删查改、上传、下载"""
    queryset = Dataset.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "file_format", "is_public", "is_verified"]  # 筛选字段
    search_fields = ["name", "description", "creator__username"]  # 搜索字段
    ordering_fields = ["created_at", "updated_at", "sample_count", "file_size"]  # 排序字段

    def get_serializer_class(self):
        """列表用简略序列化器，详情用完整序列化器"""
        if self.action == "retrieve":
            return DatasetDetailSerializer
        return DatasetSerializer

    def get_permissions(self):
        """权限控制：
        - 列表/详情：公开数据集允许匿名访问，私有数据集仅创建者/管理员访问
        - 创建：仅登录用户
        - 更新/删除：仅创建者或管理员
        - 审核：仅管理员
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsCreatorOrAdminOrPublic]
        elif self.action == "create":
            permission_classes = [IsAuthenticated]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsCreatorOrAdminOrPublic]
        elif self.action == "verify":
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """数据过滤：
        - 匿名用户：仅查看公开且已审核的数据集
        - 登录用户：可查看自己的所有数据集 + 公开且已审核的数据集
        - 管理员：查看所有数据集
        """
        user = self.request.user
        if not user.is_authenticated:
            return Dataset.objects.filter(is_public=True, is_verified=True)
        elif user.is_staff:
            return Dataset.objects.all()
        else:
            return Dataset.objects.filter(
                models.Q(creator=user) | models.Q(is_public=True, is_verified=True)
            )

    @action(detail=False, methods=["get"])
    def my_datasets(self, request):
        """自定义接口：获取当前用户创建的所有数据集"""
        datasets = Dataset.objects.filter(creator=request.user)
        serializer = self.get_serializer(datasets, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def verify(self, request, pk=None):
        """管理员审核数据集（标记为已审核）"""
        dataset = self.get_object()
        dataset.is_verified = True
        dataset.save()
        return Response({"message": "数据集审核通过"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """数据集下载接口"""
        dataset = self.get_object()
        # 验证权限（仅创建者/管理员/公开数据集可下载）
        if not (dataset.is_public and dataset.is_verified) and not (
            request.user == dataset.creator or request.user.is_staff
        ):
            return Response({"error": "无下载权限"}, status=status.HTTP_403_FORBIDDEN)
        
        # 返回文件下载响应
        response = Response(
            dataset.file_path,
            headers={
                "Content-Disposition": f'attachment; filename="{dataset.name}.{dataset.file_format}"',
                "Content-Type": "application/octet-stream"
            },
            status=status.HTTP_200_OK
        )
        return response