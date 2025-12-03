from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models

from .models import Dataset, DatasetFollow
from .serializers import (
    DatasetSerializer,
    DatasetDetailSerializer,
    DatasetFollowSerializer
)
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

    # ----------------------------------------
    # 列表查询（加入 with_follow 支持）
    # ----------------------------------------
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        with_follow = request.query_params.get("with_follow") == "true"

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data

            # 注入 is_followed 信息
            if with_follow and request.user.is_authenticated:
                user_follows = set(
                    request.user.followed_datasets.values_list("dataset_id", flat=True)
                )
                for item in data:
                    item["is_followed"] = item["id"] in user_follows

            return self.get_paginated_response({
                "code": 200,
                "msg": "查询成功",
                "data": data
            })

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        if with_follow and request.user.is_authenticated:
            user_follows = set(
                request.user.followed_datasets.values_list("dataset_id", flat=True)
            )
            for item in data:
                item["is_followed"] = item["id"] in user_follows

        return Response({
            "code": 200,
            "msg": "查询成功",
            "data": data
        })


    # ----------------------------------------
    # 关注数据集
    # ----------------------------------------
    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        """POST = 关注，DELETE = 取消关注"""

        try:
            dataset = self.get_object()
        except:
            return Response({"code": 404, "msg": "数据集不存在", "data": None}, status=404)

        # ----------- 关注 -----------
        if request.method == "POST":
            follow, created = DatasetFollow.objects.get_or_create(
                user=request.user, dataset=dataset
            )

            if not created:
               return Response(
                   {"code": 200, "msg": "已关注该数据集", "data": None},
                   status=200,
                )

            return Response(
                {
                    "code": 201,
                    "msg": "关注成功",
                    "data": DatasetFollowSerializer(follow).data,
                },
                status=201,
            )

        # ----------- 取消关注 -----------
        deleted, _ = DatasetFollow.objects.filter(
            user=request.user, dataset=dataset
        ).delete()

        if deleted == 0:
           return Response(
               {"code": 404, "msg": "未关注该数据集", "data": None},
                status=404,
            )

        return Response({"code": 200, "msg": "已取消关注", "data": None})


    # ----------------------------------------
    # 获取我关注的数据集列表
    # ----------------------------------------
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def followed(self, request):
        follows = DatasetFollow.objects.filter(user=request.user)
        datasets = [f.dataset for f in follows]

        serializer = DatasetSerializer(datasets, many=True, context={"request": request})
        data = serializer.data

        # 注入 followed_at
        for d in data:
            f = follows.get(dataset_id=d["id"])
            d["followed_at"] = f.created_at

        return Response({
            "code": 200,
            "msg": "查询成功",
            "data": data
        })

     # ----------------------------------------
    # 获取我创建的数据集列表
    # ----------------------------------------
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_datasets(self, request):
        """返回当前用户创建的数据集"""
        user = request.user
        queryset = Dataset.objects.filter(creator=user)

        serializer = DatasetSerializer(queryset, many=True, context={"request": request})
        return Response({
            "code": 200,
            "msg": "查询成功",
            "data": serializer.data
        })



    # （详情/创建/更新/删除/下载/审核）


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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"code": 200, "msg": "查询成功", "data": serializer.data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({"code": 200, "msg": "更新成功", "data": serializer.data})

        return Response({
            "code": 400,
            "msg": "更新失败",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"code": 200, "msg": "删除成功"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def verify(self, request, pk=None):
        dataset = self.get_object()
        dataset.is_verified = True
        dataset.save()
        return Response({"code": 200, "msg": "数据集审核通过"})

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        dataset = self.get_object()
        if not (dataset.is_public and dataset.is_verified) and not (
            request.user == dataset.creator or request.user.is_staff
        ):
            return Response({"code": 403, "msg": "无下载权限"}, status=403)

        response = Response(
            dataset.file_path,
            headers={
                "Content-Disposition": f'attachment; filename="{dataset.name}.{dataset.file_format}"',
                "Content-Type": "application/octet-stream"
            },
            status=200
        )
        return response

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        status_code = response.status_code
        return Response({
            "code": status_code,
            "msg": str(exc) if status_code != 403 else "权限不足",
            "data": None
        }, status=status_code)
