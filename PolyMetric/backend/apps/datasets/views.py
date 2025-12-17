import os
import json
import csv
import io
import zipfile
from rest_framework import viewsets, filters, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.http import FileResponse
from django.contrib.auth import get_user_model
from apps.users.models import UserFollow

from .models import Dataset, DatasetFollow
from .serializers import (
    DatasetSerializer,
    DatasetDetailSerializer,
    DatasetFollowSerializer,
)
from .permissions import IsCreatorOrAdminOrPublic

User = get_user_model()

class DatasetViewSet(viewsets.ModelViewSet):
    """
    数据集视图集 - 业界标准实现
    
    功能：
    - 列表/详情查询
    - 创建数据集（支持文件上传）
    - 更新/删除数据集
    - 文件下载
    - 文件预览（动态读取，不存数据库）
    - 关注/取消关注
    """
    queryset = Dataset.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "file_format", "is_public", "is_verified"]
    search_fields = ["name", "description", "creator__username"]
    ordering_fields = ["created_at", "updated_at", "sample_count", "file_size"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DatasetDetailSerializer
        return DatasetSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "preview", "download"]:
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        with_follow = request.query_params.get("with_follow") == "true"

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data

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
        return Response({
            "code": 200,
            "msg": "查询成功",
            "data": serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=partial
        )

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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 删除关联文件
        if instance.has_file():
            try:
                file_path = instance.file_path.path
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
        self.perform_destroy(instance)
        return Response(
            {"code": 200, "msg": "删除成功"}, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """下载数据集文件"""
        dataset = self.get_object()
        
        # 检查文件是否存在
        if not dataset.has_file():
            return Response(
                {"code": 404, "msg": "该数据集没有上传文件"}, 
                status=404
            )
        
        try:
            file_path = dataset.file_path.path
            if not os.path.exists(file_path):
                return Response(
                    {"code": 404, "msg": "文件不存在"}, 
                    status=404
                )
            
            # 获取原始文件名
            original_name = os.path.basename(dataset.file_path.name)
            # 或使用数据集名称
            filename = f"{dataset.name}.{dataset.file_format}"
            
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = os.path.getsize(file_path)
            return response
            
        except Exception as e:
            return Response(
                {"code": 500, "msg": f"下载失败: {str(e)}"}, 
                status=500
            )

    @action(detail=True, methods=["get"])
    def preview(self, request, pk=None):
        """
        预览数据集内容 - 业界标准实现
        
        动态读取文件内容，返回前 N 条记录
        不在数据库中存储条目，因为不同数据集格式差异大
        """
        dataset = self.get_object()
        
        if not dataset.has_file():
            return Response({
                "code": 404, 
                "msg": "该数据集没有上传文件",
                "data": None
            }, status=404)
        
        try:
            file_path = dataset.file_path.path
            if not os.path.exists(file_path):
                return Response(
                    {"code": 404, "msg": "文件不存在"}, 
                    status=404
                )
            
            # 获取预览行数
            limit = min(int(request.query_params.get("limit", 20)), 100)
            
            preview_data = self._read_file_preview(
                file_path, 
                dataset.file_format, 
                limit
            )
            
            return Response({
                "code": 200,
                "msg": "预览成功",
                "data": preview_data
            })
            
        except Exception as e:
            return Response(
                {"code": 500, "msg": f"预览失败: {str(e)}"}, 
                status=500
            )

    def _read_file_preview(self, file_path, file_format, limit=20):
        """读取文件预览内容"""
        result = {
            "format": file_format,
            "headers": [],
            "rows": [],
            "total": 0
        }
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            if file_format == "csv":
                # 尝试多种编码
                text = None
                for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                    try:
                        text = content.decode(encoding)
                        break
                    except:
                        continue
                
                if text:
                    reader = csv.DictReader(io.StringIO(text))
                    result["headers"] = reader.fieldnames or []
                    rows = list(reader)
                    result["total"] = len(rows)
                    result["rows"] = rows[:limit]
                    
            elif file_format == "json":
                data = json.loads(content.decode('utf-8'))
                
                if isinstance(data, list):
                    result["total"] = len(data)
                    result["rows"] = data[:limit]
                    if data and isinstance(data[0], dict):
                        result["headers"] = list(data[0].keys())
                elif isinstance(data, dict):
                    # 查找数据数组
                    for key in ['data', 'items', 'records', 'rows', 'samples']:
                        if key in data and isinstance(data[key], list):
                            items = data[key]
                            result["total"] = len(items)
                            result["rows"] = items[:limit]
                            if items and isinstance(items[0], dict):
                                result["headers"] = list(items[0].keys())
                            break
                    else:
                        result["rows"] = [data]
                        result["total"] = 1
                        result["headers"] = list(data.keys()) if isinstance(data, dict) else []
                        
            elif file_format == "zip":
                with zipfile.ZipFile(file_path, 'r') as zf:
                    file_list = [f for f in zf.namelist() if not f.endswith('/')]
                    result["total"] = len(file_list)
                    result["headers"] = ["filename", "size"]
                    result["rows"] = [
                        {"filename": f, "size": zf.getinfo(f).file_size}
                        for f in file_list[:limit]
                    ]
                    
        except Exception as e:
            result["error"] = str(e)
            
        return result

    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        """关注/取消关注数据集"""
        try:
            dataset = self.get_object()
        except:
            return Response(
                {"code": 404, "msg": "数据集不存在", "data": None}, 
                status=404
            )

        if request.method == "POST":
            follow, created = DatasetFollow.objects.get_or_create(
                user=request.user, 
                dataset=dataset
            )
            if not created:
                return Response({
                    "code": 200, 
                    "msg": "已关注该数据集", 
                    "data": None
                })
            return Response({
                "code": 201,
                "msg": "关注成功",
                "data": DatasetFollowSerializer(follow).data,
            }, status=201)

        deleted, _ = DatasetFollow.objects.filter(
            user=request.user, 
            dataset=dataset
        ).delete()

        if deleted == 0:
            return Response(
                {"code": 404, "msg": "未关注该数据集", "data": None}, 
                status=404
            )

        return Response({
            "code": 200, 
            "msg": "已取消关注", 
            "data": None
        })

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def followed(self, request):
        """获取我关注的数据集"""
        follows = DatasetFollow.objects.filter(user=request.user)
        datasets = [f.dataset for f in follows]
        serializer = DatasetSerializer(
            datasets, 
            many=True, 
            context={"request": request}
        )
        data = serializer.data

        for d in data:
            f = follows.get(dataset_id=d["id"])
            d["followed_at"] = f.created_at

        return Response({
            "code": 200, 
            "msg": "查询成功", 
            "data": data
        })

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_datasets(self, request):
        """获取我创建的数据集"""
        queryset = Dataset.objects.filter(creator=request.user)
        serializer = DatasetSerializer(
            queryset, 
            many=True, 
            context={"request": request}
        )
        return Response({
            "code": 200, 
            "msg": "查询成功", 
            "data": serializer.data
        })

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def verify(self, request, pk=None):
        """审核数据集（管理员）"""
        dataset = self.get_object()
        dataset.is_verified = True
        dataset.save()
        return Response({
            "code": 200, 
            "msg": "数据集审核通过"
        })

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        status_code = response.status_code
        return Response({
            "code": status_code,
            "msg": str(exc) if status_code != 403 else "权限不足",
            "data": None
        }, status=status_code)

    @action(detail=True, methods=["get"])
    def entries(self, request, pk=None):
        """分页获取数据集中的数据条目"""
        dataset = self.get_object()
        
        # 检查文件是否存在
        if not dataset.has_file():
            return Response(
                {"code": 404, "msg": "该数据集没有上传文件", "data": None},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查文件格式是否支持
        if dataset.file_format not in ["json", "zip"]:
            return Response(
                {"code": 400, "msg": "该数据集格式不支持预览", "data": None},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 获取分页参数
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 10))
            
            # 限制page_size范围
            page_size = max(5, min(page_size, 50))
            
            # 读取并解析文件内容
            file_path = dataset.file_path.path
            all_entries, fields = self._parse_dataset_file(
                file_path, 
                dataset.file_format
            )
            
            # 计算总条目数
            total = len(all_entries)
            
            # 计算分页偏移量
            start = (page - 1) * page_size
            end = start + page_size
            current_entries = all_entries[start:end]
            
            # 为条目添加id字段（如果不存在）
            for idx, entry in enumerate(current_entries, start=start + 1):
                if "id" not in entry:
                    entry["id"] = idx
            
            # 准备响应数据
            response_data = {
                "entries": current_entries,
                "total": total,
                "page": page,
                "page_size": page_size,
                "fields": fields if fields else (
                    list(current_entries[0].keys()) if current_entries else []
                )
            }
            
            return Response({
                "code": 200,
                "msg": "查询成功",
                "data": response_data
            })
            
        except FileNotFoundError:
            return Response(
                {"code": 404, "msg": "数据集文件不存在", "data": None},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"code": 500, "msg": f"数据集文件读取失败: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _parse_dataset_file(self, file_path, file_format):
        """解析数据集文件，返回所有条目和字段列表"""
        entries = []
        fields = []
        
        if file_format == "json":
            with open(file_path, 'rb') as f:
                content = f.read()
            data = json.loads(content.decode('utf-8'))
            
            # 处理不同JSON结构
            if isinstance(data, list):
                entries = data
            elif isinstance(data, dict):
                # 查找常见的数据数组键
                for key in ['data', 'items', 'records', 'rows', 'samples', 'entries']:
                    if key in data and isinstance(data[key], list):
                        entries = data[key]
                        break
                else:
                    # 如果没有找到数组，将整个对象作为一个条目
                    entries = [data]
        
        elif file_format == "zip":
            with open(file_path, 'rb') as f:
                zip_content = f.read()
            
            with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zf:
                # 查找data.json或第一个json文件
                json_files = [
                    f for f in zf.namelist() 
                    if f.lower().endswith('.json') and not f.endswith('/')
                ]
                
                if not json_files:
                    raise Exception("ZIP文件中未找到JSON文件")
                
                # 优先使用data.json
                target_file = "data.json" if "data.json" in json_files else json_files[0]
                
                with zf.open(target_file) as f:
                    content = f.read()
                    data = json.loads(content.decode('utf-8'))
                    
                    # 处理不同JSON结构
                    if isinstance(data, list):
                        entries = data
                    elif isinstance(data, dict):
                        # 查找常见的数据数组键
                        for key in ['data', 'items', 'records', 'rows', 'samples', 'entries']:
                            if key in data and isinstance(data[key], list):
                                entries = data[key]
                                break
                        else:
                            # 如果没有找到数组，将整个对象作为一个条目
                            entries = [data]
        
        # 提取字段列表（从第一条数据）
        if entries and isinstance(entries[0], dict):
            fields = list(entries[0].keys())
            # 确保id字段在最前面
            if "id" in fields:
                fields.remove("id")
                fields.insert(0, "id")
        
        return entries, fields
    
    @action(detail=False, methods=["get"])
    def followed(self, request):
        """获取关注的数据集列表，支持user_id参数"""
        user_id = request.query_params.get('user_id')
        
        if user_id:
            # 查询他人的关注列表
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    "code": 404,
                    "msg": "用户不存在",
                    "data": None
                })
                
            # 检查隐私设置
            if target_user != request.user and not target_user.show_followed_datasets:
                return Response({
                    "code": 200,
                    "msg": "该用户未公开关注的数据集",
                    "data": None
                })
                
            follows = DatasetFollow.objects.filter(user=target_user)
        else:
            # 查询自己的关注列表
            follows = DatasetFollow.objects.filter(user=request.user)
            
        datasets = [follow.dataset for follow in follows]
        page = self.paginate_queryset(datasets)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "code": 200,
                "msg": "查询成功",
                "data": serializer.data
            })
            
        serializer = self.get_serializer(datasets, many=True)
        return Response({
            "code": 200,
            "msg": "查询成功",
            "data": serializer.data
        })
    
class FollowedDatasetsListAPIView(generics.ListAPIView):
    serializer_class = DatasetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        
        if user_id:
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Dataset.objects.none()
                
            if target_user != self.request.user and not target_user.show_followed_datasets:
                return Dataset.objects.none()
                
            queryset = Dataset.objects.filter(followers__user=target_user)
        else:
            queryset = Dataset.objects.filter(followers__user=self.request.user)
            
        return queryset.prefetch_related(
            models.Prefetch(
                'followers',
                queryset=DatasetFollow.objects.filter(user=self.request.user if not user_id else target_user),
                to_attr='datasetfollow'
            )
        ).order_by('-followers__created_at')
