from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.contenttypes.models import ContentType
from .models import Comment, CommentLike
from .serializers import CommentSerializer

class CommentPagination(PageNumberPagination):
    """评论分页器"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CommentPagination
    
    def get_queryset(self):
        # 基础查询集，预加载关联数据以优化性能
        queryset = Comment.objects.select_related('user').prefetch_related('likes')
        
        # 根据 target_type 和 target_id 过滤
        target_type = self.request.query_params.get('target_type')
        target_id = self.request.query_params.get('target_id')
        
        if target_type and target_id:
            model_mapping = {
                'model': ('models', 'my_model'),
                'dataset': ('datasets', 'dataset')
            }
            if target_type in model_mapping:
                app_label, model_name = model_mapping[target_type]
                try:
                    ct = ContentType.objects.get(app_label=app_label, model=model_name)
                    queryset = queryset.filter(content_type=ct, object_id=target_id)
                except ContentType.DoesNotExist:
                    return queryset.none()
            else:
                # 如果target_type无效，返回空查询集
                return queryset.none()
        
        return queryset

    def list(self, request, *args, **kwargs):
        """重写list方法以返回统一的响应格式"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # 检查是否提供了必要的查询参数
        target_type = request.query_params.get('target_type')
        target_id = request.query_params.get('target_id')
        
        if not target_type or not target_id:
            return Response({
                "code": 400,
                "msg": "target_type和target_id参数是必填的",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # 获取分页响应数据
            paginated_data = self.get_paginated_response(serializer.data)
            # 重新格式化为统一的响应格式
            return Response({
                "code": 200,
                "msg": "success",
                "data": {
                    "results": serializer.data,
                    "total": paginated_data.data['count'],
                    "has_next": paginated_data.data['next'] is not None
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "msg": "success",
            "data": {
                "results": serializer.data,
                "total": len(serializer.data),
                "has_next": False
            }
        })

    def create(self, request, *args, **kwargs):
        """重写create方法以返回统一的响应格式"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            "code": 201,
            "msg": "评论发布成功",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """重写destroy方法以返回统一的响应格式"""
        instance = self.get_object()
        
        # 检查权限：只有评论作者可以删除评论
        if instance.user != request.user:
            return Response({
                "code": 403,
                "msg": "您只能删除自己的评论",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)
        
        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "msg": "删除成功",
            "data": None
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """点赞/取消点赞评论"""
        comment = self.get_object()
        user = request.user
        
        like_obj, created = CommentLike.objects.get_or_create(user=user, comment=comment)
        
        if not created:
            # 如果已存在，则取消点赞
            like_obj.delete()
            is_liked = False
            msg = "取消点赞成功"
        else:
            # 如果不存在，则创建点赞
            is_liked = True
            msg = "点赞成功"
            
        # 重新获取最新的点赞数
        likes_count = CommentLike.objects.filter(comment=comment).count()
        
        return Response({
            "code": 200,
            "msg": msg,
            "data": {
                "is_liked": is_liked,
                "likes_count": likes_count
            }
        })
