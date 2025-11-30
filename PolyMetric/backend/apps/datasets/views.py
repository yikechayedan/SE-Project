from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models  # 新增导入
from .models import Dataset
from .serializers import DatasetSerializer, DatasetDetailSerializer
from .permissions import IsCreatorOrAdminOrPublic

class DatasetViewSet(viewsets.ModelViewSet):
    """数据集视图集：支持增删查改、上传、下载"""
    queryset = Dataset.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "file_format", "is_public", "is_verified"]
    search_fields = ["name", "description", "creator__username"]
    ordering_fields = ["created_at", "updated_at", "sample_count", "file_size"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DatasetDetailSerializer
        return DatasetSerializer

    def get_permissions(self):
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
        user = self.request.user
        if not user.is_authenticated:
            return Dataset.objects.filter(is_public=True, is_verified=True)
        elif user.is_staff:
            return Dataset.objects.all()
        else:
            return Dataset.objects.filter(
                models.Q(creator=user) | models.Q(is_public=True, is_verified=True)
            )

    # 列表查询
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "code": 200,
                "msg": "查询成功",
                "data": serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "msg": "查询成功",
            "data": serializer.data
        })

    # 创建数据集
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({
                "code": 201,
                "msg": "创建成功",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED, headers=headers)
        
        return Response({
            "code": 400,
            "msg": "创建失败",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    # 获取详情
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 200,
            "msg": "查询成功",
            "data": serializer.data
        })

    # 更新数据集
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "code": 200,
                "msg": "更新成功",
                "data": serializer.data
            })
        
        return Response({
            "code": 400,
            "msg": "更新失败",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    # 删除数据集
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "msg": "删除成功"
        }, status=status.HTTP_200_OK)

    # 我的数据集
    @action(detail=False, methods=["get"])
    def my_datasets(self, request):
        datasets = Dataset.objects.filter(creator=request.user)
        serializer = self.get_serializer(datasets, many=True)
        return Response({
            "code": 200,
            "msg": "查询成功",
            "data": serializer.data
        })

    # 审核数据集
    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def verify(self, request, pk=None):
        dataset = self.get_object()
        dataset.is_verified = True
        dataset.save()
        return Response({
            "code": 200,
            "msg": "数据集审核通过"
        })

    # 下载数据集
    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        dataset = self.get_object()
        # 验证权限
        if not (dataset.is_public and dataset.is_verified) and not (
            request.user == dataset.creator or request.user.is_staff
        ):
            return Response({
                "code": 403,
                "msg": "无下载权限"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 返回文件下载响应（文件下载保持二进制响应格式）
        response = Response(
            dataset.file_path,
            headers={
                "Content-Disposition": f'attachment; filename="{dataset.name}.{dataset.file_format}"',
                "Content-Type": "application/octet-stream"
            },
            status=status.HTTP_200_OK
        )
        return response

    # 异常处理
    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        status_code = response.status_code
        
        # 统一异常响应格式
        return Response({
            "code": status_code,
            "msg": str(exc) if status_code != 403 else "权限不足",
            "data": None
        }, status=status_code)