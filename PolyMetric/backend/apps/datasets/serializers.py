from rest_framework import serializers
from .models import Dataset
from django.conf import settings
import os

class DatasetSerializer(serializers.ModelSerializer):
    """数据集序列化器（用于列表展示、创建、更新）"""
    creator_username = serializers.CharField(source="creator.username", read_only=True)  # 额外返回创建者用户名
    file_url = serializers.SerializerMethodField(read_only=True)  # 下载链接

    class Meta:
        model = Dataset
        fields = [
            "id", "name", "description", "category", "file_format", 
            "file_size", "sample_count", "creator", "creator_username",
            "is_public", "is_verified", "created_at", "updated_at", "file_url"
        ]
        read_only_fields = ["id", "creator", "file_size", "created_at", "updated_at", "is_verified"]  # 不可编辑字段

    def get_file_url(self, obj):
        """生成文件下载URL"""
        request = self.context.get("request")
        if obj.file_path and hasattr(obj.file_path, "url"):
            return request.build_absolute_uri(obj.file_path.url)
        return None

    def validate_file_path(self, file):
        """验证文件格式和大小"""
        allowed_formats = ["csv", "json", "zip"]
        file_ext = file.name.split(".")[-1].lower()
        if file_ext not in allowed_formats:
            raise serializers.ValidationError(f"仅支持{','.join(allowed_formats)}格式文件")
        
        # 验证文件大小（最大100MB）
        max_size = 100 * 1024 * 1024  # 100MB
        if file.size > max_size:
            raise serializers.ValidationError("文件大小不能超过100MB")
        return file

    def create(self, validated_data):
        """创建时自动关联当前用户"""
        validated_data["creator"] = self.context["request"].user
        # 计算文件大小（MB）
        validated_data["file_size"] = round(validated_data["file_path"].size / (1024 * 1024), 2)
        return super().create(validated_data)

class DatasetDetailSerializer(DatasetSerializer):
    """数据集详情序列化器（返回更多信息）"""
    class Meta(DatasetSerializer.Meta):
        fields = DatasetSerializer.Meta.fields + ["file_path"]  # 详情页可返回文件路径（仅用于内部）