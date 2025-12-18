# apps/models/views.py
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from apps.users.models import UserFollow, UserStar

User = get_user_model()
import django.db.models as models  # 显式导入 models 避免混淆
# 关键修改：导入 My_Model
from .models import My_Model, ModelFollow
from .serializers import (
    ModelListSerializer, ModelDetailSerializer,
    ModelFollowSerializer, FollowedModelSerializer
)

class ModelViewSet(viewsets.ReadOnlyModelViewSet):
    """模型视图集：提供列表、详情查询，以及关注/取消关注操作"""
    # 关键修改：查询集改为 My_Model
    queryset = My_Model.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return ModelListSerializer
        return ModelDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        with_follow = self.request.query_params.get('with_follow', 'false').lower() == 'true'
        
        if with_follow and self.request.user.is_authenticated:
            # 关联当前用户的关注状态
            queryset = queryset.annotate(
                is_followed=models.Exists(
                    ModelFollow.objects.filter(
                        user=self.request.user,
                        model=models.OuterRef('pk')
                    )
                )
            )
        return queryset

    # 核心修改：合并关注/取消关注逻辑，支持 POST/DELETE
    @action(
        detail=True, 
        methods=['post', 'delete'],  # 同时支持 POST（关注）/ DELETE（取消关注）
        permission_classes=[IsAuthenticated],
        url_path='follow',  # URL 路径：/api/models/{id}/follow/
        url_name='follow'
    )
    def follow(self, request, pk=None):
        """
        统一处理关注/取消关注：
        - POST /api/models/{id}/follow/ → 关注模型
        - DELETE /api/models/{id}/follow/ → 取消关注模型
        """
        model = self.get_object()  # 关联 My_Model
        user = request.user

        # 1. POST 请求：关注模型
        if request.method == 'POST':
            follow, created = ModelFollow.objects.get_or_create(
                user=user,
                model=model
            )
            if created:
                serializer = ModelFollowSerializer(follow)
                return Response(
                    {'code': 201, 'msg': '关注成功', 'data': serializer.data},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'code': 200, 'msg': '已关注该模型', 'data': None},
                status=status.HTTP_200_OK
            )
        
        # 2. DELETE 请求：取消关注模型
        elif request.method == 'DELETE':
            try:
                follow = ModelFollow.objects.get(user=user, model=model)
                follow.delete()
                return Response({'code': 200, 'msg': '已取消关注', 'data': None})
            except ModelFollow.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '未关注该模型', 'data': None},
                    status=status.HTTP_404_NOT_FOUND
                )

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def star(self, request, pk=None):
        """
        点赞/取消点赞接口
        POST   /api/models/{id}/star/ -> 点赞
        DELETE /api/models/{id}/star/ -> 取消点赞
        """
        obj = self.get_object()  # 获取具体的模型实例
        content_type = ContentType.objects.get_for_model(obj)
        user = request.user

        # ====== 1. 点赞逻辑 (POST) ======
        if request.method == 'POST':
            # get_or_create 自动处理去重
            _, created = UserStar.objects.get_or_create(
                user=user,
                content_type=content_type,
                object_id=obj.id
            )
            msg = "点赞成功" if created else "已点赞"
            status_code = 201 if created else 200

        # ====== 2. 取消点赞逻辑 (DELETE) ======
        elif request.method == 'DELETE':
            deleted_count, _ = UserStar.objects.filter(
                user=user,
                content_type=content_type,
                object_id=obj.id
            ).delete()
            msg = "已取消点赞" if deleted_count > 0 else "未曾点赞"
            status_code = 200

        # ====== 3. 返回最新统计数据 ======
        # 前端需要这两个字段来更新 UI
        current_count = UserStar.objects.filter(
            content_type=content_type,
            object_id=obj.id
        ).count()
        
        # 判断当前状态（POST肯定是True, DELETE肯定是False）
        is_starred = True if request.method == 'POST' else False

        return Response({
            "code": status_code,
            "msg": msg,
            "data": {
                "star_count": current_count,
                "is_starred": is_starred
            }
        })

class FollowedModelsListAPIView(generics.ListAPIView):
    """获取当前用户关注的模型列表：GET /api/models/followed/"""
    serializer_class = FollowedModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        
        if user_id:
            # 查询他人的关注列表
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return My_Model.objects.none()
                
            # 检查隐私设置
            if target_user != self.request.user and not target_user.show_followed_models:
                return My_Model.objects.none()
                
            queryset = My_Model.objects.filter(
                followers__user=target_user
            )
        else:
            # 查询自己的关注列表
            queryset = My_Model.objects.filter(
                followers__user=self.request.user
            )
            
        # 关联关注时间
        return queryset.prefetch_related(
            models.Prefetch(
                'followers',
                queryset=ModelFollow.objects.filter(user=self.request.user if not user_id else target_user),
                to_attr='modelfollow'
            )
        ).order_by('-followers__created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        user_id = request.query_params.get('user_id')
        
        # 处理隐私限制返回
        if user_id and queryset.count() == 0:
            target_user = User.objects.filter(id=user_id).first()
            if target_user and target_user != request.user and not target_user.show_followed_models:
                return Response({
                    'code': 200,
                    'msg': '该用户未公开关注的模型',
                    'data': None
                })
                
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': serializer.data
        })