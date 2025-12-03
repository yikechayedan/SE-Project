from rest_framework import serializers
from .models import Dataset, DatasetFollow
from django.conf import settings
import os


class DatasetSerializer(serializers.ModelSerializer):
    """数据集序列化器（用于列表展示、创建、更新）"""
    creator_username = serializers.CharField(source="creator.username", read_only=True)
    file_url = serializers.SerializerMethodField(read_only=True)

    # ⭐ 新增字段
    is_followed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Dataset
        fields = [
            "id", "name", "description", "category", "file_format",
            "file_size", "sample_count", "creator", "creator_username",
            "is_public", "is_verified",
            "is_followed",   # ⭐ 新增
            "created_at", "updated_at", "file_url"
        ]
        read_only_fields = ["id", "creator", "file_size", "created_at", "updated_at", "is_verified"]

    def get_file_url(self, obj):
        """生成文件下载URL"""
        request = self.context.get("request")
        if obj.file_path and hasattr(obj.file_path, "url"):
            return request.build_absolute_uri(obj.file_path.url)
        return None

    # ⭐ 关键：判断当前用户是否已关注
    def get_is_followed(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.followers.filter(user=request.user).exists()

    def validate_file_path(self, file):
        """验证文件格式和大小"""
        allowed_formats = ["csv", "json", "zip"]
        file_ext = file.name.split(".")[-1].lower()
        if file_ext not in allowed_formats:
            raise serializers.ValidationError(f"仅支持{','.join(allowed_formats)}格式文件")

        max_size = 100 * 1024 * 1024  # 100MB
        if file.size > max_size:
            raise serializers.ValidationError("文件大小不能超过100MB")
        return file

    def create(self, validated_data):
        """创建时自动关联当前用户"""
        validated_data["creator"] = self.context["request"].user
        validated_data["file_size"] = round(validated_data["file_path"].size / (1024 * 1024), 2)
        return super().create(validated_data)



class DatasetDetailSerializer(DatasetSerializer):
    """数据集详情序列化器（返回更多信息）"""
    class Meta(DatasetSerializer.Meta):
        fields = DatasetSerializer.Meta.fields + ["file_path"]



# ==============================
# ⭐ 新增关注序列化器
# ==============================
class DatasetFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetFollow
        fields = ["id", "dataset", "created_at"]
