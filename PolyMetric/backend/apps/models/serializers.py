# apps/models/serializers.py
from rest_framework import serializers
# 关键修改：导入 My_Model 而非 Model/LargeModel
from .models import My_Model, ModelFollow
from apps.users.models import User
from django.contrib.contenttypes.models import ContentType
from apps.users.models import UserStar

class ModelListSerializer(serializers.ModelSerializer):
    is_followed = serializers.BooleanField(read_only=True)
    # 1. 统计总数
    star_count = serializers.SerializerMethodField()
    # 2. 当前用户状态
    is_starred = serializers.SerializerMethodField()

    def get_star_count(self, obj):
        # 简单实现：实时查询（数据量大时建议增加冗余字段或缓存）
        ct = ContentType.objects.get_for_model(obj)
        return UserStar.objects.filter(content_type=ct, object_id=obj.id).count()

    def get_is_starred(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        ct = ContentType.objects.get_for_model(obj)
        return UserStar.objects.filter(user=user, content_type=ct, object_id=obj.id).exists()

    class Meta:
        model = My_Model  # 改为 My_Model
        fields = [
            'id', 'name', 'company', 'category', 'parameter_size',
            'description', 'version', 'release_date', 'official_url',
            'is_followed', 'star_count', 'is_starred', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class ModelDetailSerializer(serializers.ModelSerializer):
    # 1. 统计总数
    star_count = serializers.SerializerMethodField()
    # 2. 当前用户状态
    is_starred = serializers.SerializerMethodField()

    def get_star_count(self, obj):
        # 简单实现：实时查询（数据量大时建议增加冗余字段或缓存）
        ct = ContentType.objects.get_for_model(obj)
        return UserStar.objects.filter(content_type=ct, object_id=obj.id).count()

    def get_is_starred(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        ct = ContentType.objects.get_for_model(obj)
        return UserStar.objects.filter(user=user, content_type=ct, object_id=obj.id).exists()

    class Meta:
        model = My_Model  # 改为 My_Model
        fields = [
            'id', 'name', 'company', 'category', 'parameter_size',
            'description', 'version', 'release_date', 'official_url',
            'star_count', 'is_starred', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class ModelFollowSerializer(serializers.ModelSerializer):
    model_id = serializers.IntegerField(source='model.id', read_only=True)

    class Meta:
        model = ModelFollow
        fields = ['id', 'model_id', 'created_at']
        read_only_fields = fields


class FollowedModelSerializer(serializers.ModelSerializer):
    followed_at = serializers.DateTimeField(source='modelfollow.created_at', read_only=True)

    class Meta:
        model = My_Model  # 改为 My_Model
        fields = [
            'id', 'name', 'company', 'category', 'parameter_size',
            'description', 'version', 'release_date', 'official_url',
            'created_at', 'updated_at', 'followed_at'
        ]