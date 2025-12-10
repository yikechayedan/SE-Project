from rest_framework import serializers
from .models import Dataset, DatasetFollow
import os


class DatasetSerializer(serializers.ModelSerializer):
    """
    数据集序列化器 - 业界标准实现
    
    设计理念：
    1. 前端通过 multipart/form-data 上传文件
    2. 后端保存文件到磁盘，数据库存储文件路径
    3. 返回文件下载 URL 供前端使用
    """
    creator_id = serializers.IntegerField(source='creator.id', read_only=True)  # 新增
    creator_username = serializers.CharField(source="creator.username", read_only=True)
    file_url = serializers.SerializerMethodField(read_only=True)
    has_file = serializers.SerializerMethodField(read_only=True)
    is_followed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Dataset
        fields = [
            "id", "name", "description", "category", "file_format",
            "file_size", "sample_count", "creator", "creator_id", "creator_username",
            "is_public", "is_verified", "is_followed", "has_file",
            "created_at", "updated_at", "file_url", "file_path"
        ]
        read_only_fields = ["id", "creator", "file_size", "sample_count", "created_at", "updated_at", "is_verified"]
        extra_kwargs = {
            'file_path': {'write_only': True, 'required': False}
        }

    def get_file_url(self, obj):
        """生成文件下载URL"""
        request = self.context.get("request")
        if obj.has_file() and request:
            return request.build_absolute_uri(f"/api/datasets/{obj.id}/download/")
        return None

    def get_has_file(self, obj):
        """检查是否有文件"""
        return obj.has_file()

    def get_is_followed(self, obj):
        """判断当前用户是否已关注"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.followers.filter(user=request.user).exists()

    def validate_file_path(self, file):
        """验证上传的文件"""
        if file is None:
            return file
            
        # 验证文件格式
        allowed_formats = ["csv", "json", "zip"]
        file_ext = file.name.split(".")[-1].lower()
        if file_ext not in allowed_formats:
            raise serializers.ValidationError(f"仅支持 {', '.join(allowed_formats)} 格式文件")

        # 验证文件大小 (100MB)
        max_size = 100 * 1024 * 1024
        if file.size > max_size:
            raise serializers.ValidationError("文件大小不能超过 100MB")
        
        return file

    def _count_samples(self, file_obj, file_format):
        """
        统计样本数量（用于预览，不存储到数据库）
        这是业界标准做法：只统计数量，不解析存储每条数据
        """
        try:
            file_obj.seek(0)
            content = file_obj.read()
            
            if file_format == "csv":
                # CSV: 统计行数（减去表头）
                try:
                    text = content.decode('utf-8')
                except:
                    text = content.decode('gbk', errors='ignore')
                lines = [l for l in text.strip().split('\n') if l.strip()]
                return max(0, len(lines) - 1)  # 减去表头
                
            elif file_format == "json":
                import json
                try:
                    data = json.loads(content.decode('utf-8'))
                    if isinstance(data, list):
                        return len(data)
                    elif isinstance(data, dict):
                        # 查找常见的数据数组键
                        for key in ['data', 'items', 'records', 'rows', 'samples']:
                            if key in data and isinstance(data[key], list):
                                return len(data[key])
                        return 1
                except:
                    return 0
                    
            elif file_format == "zip":
                # ZIP: 返回文件数量
                import zipfile
                import io
                try:
                    with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
                        return len([f for f in zf.namelist() if not f.endswith('/')])
                except:
                    return 0
        except Exception as e:
            print(f"统计样本数量时出错: {e}")
            return 0
        finally:
            file_obj.seek(0)

    def create(self, validated_data):
        """创建数据集"""
        validated_data["creator"] = self.context["request"].user
        
        file_obj = validated_data.get("file_path")
        
        if file_obj:
            # 计算文件大小 (MB)
            validated_data["file_size"] = round(file_obj.size / (1024 * 1024), 2)
            # 统计样本数量
            file_format = validated_data.get("file_format", "").lower()
            validated_data["sample_count"] = self._count_samples(file_obj, file_format)
        else:
            validated_data["file_size"] = 0.0
            validated_data["sample_count"] = 0
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """更新数据集"""
        file_obj = validated_data.get("file_path")
        
        if file_obj:
            # 删除旧文件
            if instance.has_file():
                try:
                    old_path = instance.file_path.path
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except:
                    pass
            
            validated_data["file_size"] = round(file_obj.size / (1024 * 1024), 2)
            file_format = validated_data.get("file_format", instance.file_format).lower()
            validated_data["sample_count"] = self._count_samples(file_obj, file_format)
        
        return super().update(instance, validated_data)


class DatasetDetailSerializer(DatasetSerializer):
    """数据集详情序列化器"""
    class Meta(DatasetSerializer.Meta):
        pass


class DatasetFollowSerializer(serializers.ModelSerializer):
    """关注序列化器"""
    class Meta:
        model = DatasetFollow
        fields = ["id", "dataset", "created_at"]
