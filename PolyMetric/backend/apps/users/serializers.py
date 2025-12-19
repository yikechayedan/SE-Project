from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .models import User, UserFollow

User = get_user_model()

# ========== 基础序列化器（保留） ==========
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "phone"]

    def validate_phone(self, value):
        """如果手机号为空字符串，转为 None"""
        if not value:
            return None
        return value

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "avatar", "bio"]

    def validate_phone(self, value):
        """如果手机号为空字符串，转为 None"""
        if not value:
            return None
        return value

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码错误")
        return value
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True)

class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.ImageField()

# ========== API1：用户公开信息序列化器（已正确） ==========
class UserPublicSerializer(serializers.ModelSerializer):
    is_followed = serializers.SerializerMethodField()
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'avatar', 'bio',
            'show_followed_models', 'show_followed_datasets',
            'is_followed', 'followers_count', 'following_count'
        ]
        extra_kwargs = {
            'email': {'read_only': True},
            'phone': {'read_only': True}
        }

    def get_is_followed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return UserFollow.objects.filter(follower=request.user, followed=obj).exists()

# ========== API6：当前用户信息序列化器（已正确） ==========
class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'avatar', 'bio',
            'show_followed_models', 'show_followed_datasets'
        ]
        read_only_fields = ['id', 'username', 'email']

# ========== API5：隐私设置序列化器（二选一，保留一个即可） ==========
# 推荐保留 PrivacySettingSerializer（与视图对应）
class PrivacySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['show_followed_models', 'show_followed_datasets']
        extra_kwargs = {
            'show_followed_models': {'required': False},
            'show_followed_datasets': {'required': False},
        }

class FollowedUserSerializer(serializers.ModelSerializer):
    """
    序列化当前用户关注的用户列表（关联UserFollow模型）
    数据源：UserFollow实例 → 关联followed（被关注用户）+ created_at（关注时间）
    """
    # 从UserFollow的followed关联中获取用户字段
    id = serializers.IntegerField(source='followed.id', read_only=True)
    username = serializers.CharField(source='followed.username', read_only=True)
    avatar = serializers.CharField(source='followed.avatar', read_only=True, allow_null=True)
    bio = serializers.CharField(source='followed.bio', read_only=True, allow_null=True)
    show_followed_models = serializers.BooleanField(source='followed.show_followed_models', read_only=True)
    show_followed_datasets = serializers.BooleanField(source='followed.show_followed_datasets', read_only=True)
    # 关注时间（直接从UserFollow的created_at获取）
    followed_at = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = UserFollow  # 数据源是UserFollow，而非User
        fields = [
            'id', 'username', 'avatar', 'bio',
            'show_followed_models', 'show_followed_datasets',
            'followed_at'
        ]