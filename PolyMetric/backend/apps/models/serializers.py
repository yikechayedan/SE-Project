# apps/models/serializers.py
from rest_framework import serializers
from .models import Model, ModelFollow
from apps.users.models import User

class ModelSerializer(serializers.ModelSerializer):
    """模型基础序列化器（用于列表和详情）"""
    # 处理choices字段的显示（返回中文名称）
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Model
        fields = [
            'id', 'name', 'company', 'category', 'category_display',
            'parameter_size', 'description', 'version', 'release_date',
            'official_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ModelListSerializer(ModelSerializer):
    """模型列表序列化器（包含关注状态）"""
    is_followed = serializers.BooleanField(read_only=True)
    
    class Meta(ModelSerializer.Meta):
        fields = ModelSerializer.Meta.fields + ['is_followed']

class ModelFollowSerializer(serializers.ModelSerializer):
    """模型关注序列化器"""
    class Meta:
        model = ModelFollow
        fields = ['id', 'model_id', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        # 自动关联当前登录用户
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class FollowedModelSerializer(ModelSerializer):
    """用户关注的模型序列化器（包含关注时间）"""
    followed_at = serializers.DateTimeField(source='modelfollow.created_at', read_only=True)
    
    class Meta(ModelSerializer.Meta):
        fields = ModelSerializer.Meta.fields + ['followed_at']