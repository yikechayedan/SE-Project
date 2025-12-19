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
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return CommentLike.objects.filter(user=request.user, comment=obj).exists()

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.user == request.user

    def validate(self, attrs):
        target_type = attrs.get('target_type')
        target_id = attrs.get('target_id')
        
        # 映射 target_type 到 ContentType
        # 格式: 'frontend_alias': ('app_label', 'model_name')
        # 根据实际项目 app 名字修改
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
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")
        return Comment.objects.create(user=request.user, **validated_data)