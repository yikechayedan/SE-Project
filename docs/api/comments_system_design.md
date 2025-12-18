# 评论系统设计文档 (Comments System Design)

**注意：此文档定义了前端对接所需的 API 规范，并提供了后端的具体实现参考。**

## 1. 数据模型概念 (Data Model Concept)

为了支持对不同类型的对象（如“模型”和“数据集”）进行评论，后端应采用 **通用外键 (Generic Relations)** 的设计模式。

- **Comment (评论)**
    - `id`: 主键
    - `user`: 评论发布者
    - `content`: 评论内容
    - `content_type`: 目标对象类型（指向 Django ContentType）
    - `object_id`: 目标对象ID
    - `created_at`: 创建时间
    - `likes_count`: 点赞数 (可作为缓存字段或动态计算)

- **CommentLike (评论点赞)**
    - `user`: 点赞用户
    - `comment`: 关联评论
    - `created_at`: 点赞时间

## 2. API 接口规范 (API Specification)

所有接口的基础路径建议为 `/api/comments/`。

### 2.1 获取评论列表 (支持分页)
- **Method**: `GET`
- **URL**: `/api/comments/`
- **Query Params**:
    - `target_type`: string ("model" 或 "dataset") —— **必填**
    - `target_id`: int —— **必填**
    - `page`: int (默认 1)
    - `page_size`: int (默认 10)
- **Response Example**:
```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "results": [
            {
                "id": 101,
                "content": "这个模型在处理中文时效果很好！",
                "created_at": "2023-12-18T10:30:00Z",
                "likes_count": 12,
                "is_liked": true,
                "is_owner": false,
                "user": {
                    "id": 5,
                    "username": "AI_Expert",
                    "avatar": "/media/avatars/user_5.png"
                }
            }
        ],
        "total": 50,
        "has_next": true
    }
}
```

### 2.2 发布评论
- **Method**: `POST`
- **URL**: `/api/comments/`
- **Body**:
```json
{
    "target_type": "model",
    "target_id": 123,
    "content": "期待更新更多版本！"
}
```
*注: `target_type` 可选值为 "model" 或 "dataset"*

- **Response**:
```json
{
    "code": 201,
    "msg": "评论发布成功",
    "data": {
        "id": 102,
        "content": "期待更新更多版本！",
        "created_at": "2023-12-18T12:00:00Z",
        "likes_count": 0,
        "is_liked": false,
        "is_owner": true,
        "user": {
            "id": 5,
            "username": "Current_User",
            "avatar": "/media/default.png"
        }
    }
}
```

### 2.3 删除评论
- **Method**: `DELETE`
- **URL**: `/api/comments/{id}/`
- **Response**:
```json
{
    "code": 200,
    "msg": "删除成功"
}
```

### 2.4 点赞/取消点赞
- **Method**: `POST`
- **URL**: `/api/comments/{id}/like/`
- **Response**:
```json
{
    "code": 200,
    "msg": "操作成功",
    "data": {
        "is_liked": true,
        "likes_count": 13
    }
}
```

## 3. 后端实现参考 (Backend Implementation Reference)

### 3.1 建模思路 (Modeling Strategy)

采用 Django 的 `contenttypes` 框架实现多态关联。这种方式允许 `Comment` 模型关联到系统中的任何其他模型（Model, Dataset 等），而无需为每种关联对象创建外键字段。

**核心逻辑：**
1.  **Frontend**: 传递 `target_type` (字符串别名) 和 `target_id`。
2.  **Backend (Serializer)**: 将 `target_type` 映射到具体的 Django `ContentType`。
3.  **Backend (Model)**: 使用 `GenericForeignKey` 存储关联关系。

### 3.2 数据库模型 (apps/comments/models.py)

```python
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name="评论者"
    )
    content = models.TextField(verbose_name="评论内容")
    
    # 通用外键配置
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

class CommentLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')
        verbose_name = "评论点赞"
        verbose_name_plural = verbose_name
```

### 3.3 序列化器 (apps/comments/serializers.py)

```python
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import Comment, CommentLike

User = get_user_model()

class CommentUserSerializer(serializers.ModelSerializer):
    """仅用于评论展示的用户信息"""
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']

class CommentSerializer(serializers.ModelSerializer):
    user = CommentUserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    
    # 接收前端的 target_type 和 target_id (write_only)
    target_type = serializers.CharField(write_only=True)
    target_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'content', 'created_at', 
            'likes_count', 'is_liked', 'is_owner',
            'target_type', 'target_id'
        ]
        read_only_fields = ['id', 'created_at']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return CommentLike.objects.filter(user=user, comment=obj).exists()
        return False

    def get_is_owner(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and obj.user == user

    def validate(self, attrs):
        target_type = attrs.get('target_type')
        target_id = attrs.get('target_id')
        
        # 映射 target_type 到 ContentType
        # 格式: 'frontend_alias': ('app_label', 'model_name')
        # 请根据实际项目 app 名字修改
        model_mapping = {
            'model': ('models', 'my_model'), 
            'dataset': ('datasets', 'dataset')
        }
        
        if target_type not in model_mapping:
            raise serializers.ValidationError({"target_type": "Invalid target type"})
            
        app_label, model_name = model_mapping[target_type]
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model_name)
            attrs['content_type'] = ct
        except ContentType.DoesNotExist:
             raise serializers.ValidationError({"target_type": "System configuration error: ContentType not found"})
             
        # 验证目标对象是否存在
        model_class = ct.model_class()
        if not model_class.objects.filter(id=target_id).exists():
             raise serializers.ValidationError({"target_id": "Target object does not exist"})
             
        attrs['object_id'] = target_id
        
        # 移除辅助字段，保留模型所需字段
        del attrs['target_type']
        del attrs['target_id']
        
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        return Comment.objects.create(user=user, **validated_data)
```

### 3.4 视图集 (apps/comments/views.py)

```python
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from .models import Comment, CommentLike
from .serializers import CommentSerializer

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
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
        
        return queryset

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own comments.")
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        user = request.user
        
        like_obj, created = CommentLike.objects.get_or_create(user=user, comment=comment)
        
        if not created:
            like_obj.delete()
            is_liked = False
        else:
            is_liked = True
            
        return Response({
            "code": 200,
            "msg": "Success",
            "data": {
                "is_liked": is_liked,
                "likes_count": comment.likes.count()
            }
        })
```

## 4. 前端实现代码位置 (Frontend Implementation Location)

前端部分已经对接完成，相关代码位于以下文件：

1.  **API 接口封装**:
    -   路径: `PolyMetric/frontend/src/api/comments.js`
    -   说明: 包含 `getComments`, `postComment`, `deleteComment`, `toggleCommentLike` 等方法的定义。

2.  **UI 组件**:
    -   路径: `PolyMetric/frontend/src/components/common/CommentSection.vue`
    -   说明: 基于 Element Plus 的评论区组件，实现了列表展示、分页加载、发表评论及点赞交互。