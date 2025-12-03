# apps/models/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import OuterRef, Subquery
from .models import Model, ModelFollow
from .serializers import (
    ModelSerializer, ModelListSerializer, 
    ModelFollowSerializer, FollowedModelSerializer
)
from .permissions import IsAuthenticatedOrReadOnly

class ModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    模型视图集：提供列表查询、详情查询、关注/取消关注、我的关注列表功能
    """
    queryset = Model.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'company', 'description', 'category']
    ordering_fields = ['created_at', 'release_date', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """根据不同操作返回不同序列化器"""
        if self.action == 'list':
            return ModelListSerializer
        return ModelSerializer

    def get_queryset(self):
        """
        列表查询时：根据with_follow参数添加关注状态
        """
        queryset = super().get_queryset()
        with_follow = self.request.query_params.get('with_follow', 'false').lower() == 'true'
        
        if with_follow and self.request.user.is_authenticated:
            # 子查询：查询当前用户关注的模型ID
            followed_ids = ModelFollow.objects.filter(
                user=self.request.user,
                model=OuterRef('pk')
            ).values('id')
            
            # 添加is_followed字段（是否存在关注记录）
            queryset = queryset.annotate(
                is_followed=Subquery(followed_ids)
            ).values(
                *[f.name for f in Model._meta.fields],
                'is_followed', 'get_category_display'
            )
        
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        """关注模型"""
        model = self.get_object()
        user = request.user
        
        # 检查是否已关注
        follow, created = ModelFollow.objects.get_or_create(user=user, model=model)
        
        if created:
            serializer = ModelFollowSerializer(follow, context={'request': request})
            return Response({
                'code': 201,
                'msg': '关注成功',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'code': 200,
                'msg': '已关注该模型',
                'data': None
            })

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        """取消关注模型"""
        model = self.get_object()
        user = request.user
        
        try:
            follow = ModelFollow.objects.get(user=user, model=model)
            follow.delete()
            return Response({
                'code': 200,
                'msg': '已取消关注',
                'data': None
            })
        except ModelFollow.DoesNotExist:
            return Response({
                'code': 404,
                'msg': '未关注该模型',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def followed(self, request):
        """获取当前用户关注的模型列表"""
        # 关联查询：通过ModelFollow关联到Model
        followed_models = Model.objects.filter(
            followers__user=request.user
        ).annotate(
            followed_at=Subquery(
                ModelFollow.objects.filter(
                    user=request.user,
                    model=OuterRef('pk')
                ).values('created_at')[:1]
            )
        ).order_by('-followed_at')
        
        serializer = FollowedModelSerializer(followed_models, many=True)
        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        """重写详情查询：处理404情况"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': serializer.data
        })

    def list(self, request, *args, **kwargs):
        """重写列表查询：统一返回格式"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'code': 200,
                'msg': '查询成功',
                'data': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': serializer.data
        })

    def handle_exception(self, exc):
        """全局异常处理：统一错误返回格式"""
        from rest_framework.exceptions import NotFound
        if isinstance(exc, NotFound):
            return Response({
                'code': 404,
                'msg': '模型不存在',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 未登录异常处理
        from rest_framework.exceptions import NotAuthenticated
        if isinstance(exc, NotAuthenticated):
            return Response({
                'code': 401,
                'msg': '请先登录',
                'data': None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 其他异常
        return super().handle_exception(exc)