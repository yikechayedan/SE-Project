from rest_framework import serializers
from .models import Dataset, DatasetFollow
from django.contrib.contenttypes.models import ContentType
from apps.users.models import UserStar
import os
import json
import zipfile
import io
import re
import chardet

class DatasetSerializer(serializers.ModelSerializer):
    """
    数据集序列化器 - 全能验证增强版
    支持文本/图像/多模态 x 主观/客观/对抗 15 种组合
    """
    creator_id = serializers.IntegerField(source='creator.id', read_only=True)
    creator_username = serializers.CharField(source="creator.username", read_only=True)
    evaluation_type = serializers.CharField(required=False, allow_null=True)
    file_url = serializers.SerializerMethodField(read_only=True)
    has_file = serializers.SerializerMethodField(read_only=True)
    is_followed = serializers.SerializerMethodField(read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    class Meta:
        model = Dataset
        fields = [
            "id", "name", "description", "category", "capability_dimension", "evaluation_type", "file_format",
            "file_size", "sample_count", "creator", "creator_id", "creator_username",
            "is_public", "is_verified", "status", "is_followed", "has_file", "star_count", "is_starred",
            "created_at", "updated_at", "file_url", "file_path","capability_tag","has_images", "image_count"
        ]
        read_only_fields = [
            "id", "creator", "file_size", "sample_count", "created_at", 
            "updated_at", "star_count", "is_starred",
            "capability_tag","has_images", "image_count"
        ]
        extra_kwargs = {
            'file_path': {'write_only': True, 'required': False}
        }

    # ========================== 核心方法：创建与更新 ==========================

    def _sample_dataset(self, file_obj, file_format, limit=5):
        """从数据集中抽样 N 条，用于 AI 分析能力标签"""
        file_obj.seek(0)
        content = file_obj.read()
        try:
            if file_format == "json":
                data = json.loads(content.decode("utf-8"))
                return data[:limit] if isinstance(data, list) else []
            
            if file_format == "csv":
                detected = chardet.detect(content)
                text = content.decode(detected['encoding'] or 'utf-8', errors='ignore')
                import csv
                reader = csv.DictReader(io.StringIO(text))
                return list(reader)[:limit]
                
            if file_format == "zip":
                with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
                    json_files = [f for f in zf.namelist() if f.lower().endswith('.json') and not f.endswith('/')]
                    if not json_files: return []
                    target = "data.json" if "data.json" in json_files else json_files[0]
                    with zf.open(target) as f:
                        data = json.loads(f.read().decode('utf-8'))
                        return data[:limit] if isinstance(data, list) else []
        except: return []
        finally: file_obj.seek(0)

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        file_obj = validated_data.get("file_path")
        file_format = validated_data.get("file_format")

        if file_obj and file_format:
            file_format = file_format.lower()
            validated_data["file_size"] = round(file_obj.size / (1024 * 1024), 6)
            validated_data["sample_count"] = self._count_samples(file_obj, file_format)
            validated_data["has_images"] = self._check_has_images(file_obj, file_format)
            validated_data["image_count"] = self._count_images(file_obj, file_format)
            
            validated_data["is_verified"] = False
            validated_data["status"] = "pending"
            validated_data["capability_tag"] = "processing"
            validated_data["capability_dimension"] = "other"
        else:
            validated_data.update({
                "file_size": 0.0, "sample_count": 0, "has_images": False, 
                "image_count": 0, "capability_tag": "other", "capability_dimension": "other", "is_verified": False
            })

        dataset = super().create(validated_data)
        
        if file_obj and validated_data.get("capability_tag") == "processing":
            from apps.tasks.tasks import analyze_dataset_capability
            analyze_dataset_capability.delay(dataset.id)
        
        return dataset

    def update(self, instance, validated_data):
        file_obj = validated_data.get("file_path")
        if not instance.is_verified:
            raise serializers.ValidationError("只有已审核通过的数据集才能修改")
        
        if file_obj:
            if instance.has_file():
                try:
                    if os.path.exists(instance.file_path.path): os.remove(instance.file_path.path)
                except: pass
            
            validated_data["file_size"] = round(file_obj.size / (1024 * 1024), 6)
            file_format = validated_data.get("file_format", instance.file_format).lower()
            validated_data["sample_count"] = self._count_samples(file_obj, file_format)
            validated_data["has_images"] = self._check_has_images(file_obj, file_format)
            validated_data["image_count"] = self._count_images(file_obj, file_format)
            validated_data["status"] = "pending"
            validated_data["capability_tag"] = "processing"
            validated_data["capability_dimension"] = "other"
        
        dataset = super().update(instance, validated_data)
        if file_obj and validated_data.get("capability_tag") == "processing":
            from apps.tasks.tasks import analyze_dataset_capability
            analyze_dataset_capability.delay(dataset.id)
        return dataset

    # ========================== 核心方法：验证逻辑 ==========================

    def validate(self, attrs):
        file_obj = attrs.get("file_path")
        evaluation_type = attrs.get("evaluation_type", "subjective")
        category = attrs.get("category")
        
        if file_obj:
            # 格式初检
            allowed_formats = ["csv", "json", "zip"]
            file_ext = file_obj.name.split(".")[-1].lower()
            if file_ext not in allowed_formats:
                raise serializers.ValidationError(f"仅支持 {', '.join(allowed_formats)} 格式文件")
            
            # 内容详检
            self.validate_dataset_content(file_obj, evaluation_type, category)
        
        return attrs

    def validate_dataset_content(self, file_obj, evaluation_type, category=None):
        """执行深度的内容字段与结构校验"""
        file_obj.seek(0)
        content = file_obj.read()
        file_ext = file_obj.name.split(".")[-1].lower()
        
        try:
            if file_ext == "json":
                data = json.loads(content.decode('utf-8'))
                self._validate_data_by_evaluation_type(data, evaluation_type, category)
            elif file_ext == "csv":
                detected = chardet.detect(content)
                text = content.decode(detected['encoding'] or 'utf-8', errors='ignore')
                import csv
                reader = csv.DictReader(io.StringIO(text))
                csv_data = list(reader)
                converted_data = self._convert_csv_to_json_format(csv_data, evaluation_type)
                self._validate_data_by_evaluation_type(converted_data, evaluation_type, category)
            elif file_ext == "zip":
                with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
                    self._validate_zip_security(zf)
                    json_files = [f for f in zf.namelist() if f.lower().endswith('.json') and not f.endswith('/')]
                    if not json_files: raise serializers.ValidationError("ZIP文件中未找到JSON文件")
                    target_file = "data.json" if "data.json" in json_files else json_files[0]
                    with zf.open(target_file) as f:
                        data = json.loads(f.read().decode('utf-8'))
                        self._validate_data_by_evaluation_type(data, evaluation_type, category, zf)
        except Exception as e:
            if isinstance(e, serializers.ValidationError): raise
            raise serializers.ValidationError(f"解析/校验失败: {str(e)}")
        finally:
            file_obj.seek(0)

    def _validate_data_by_evaluation_type(self, data, evaluation_type, category=None, zip_file=None):
        """逐条目校验核心逻辑：支持多模态混合校验"""
        if not isinstance(data, list) or not data:
            raise serializers.ValidationError("数据集内容必须是非空数组")
        
        zip_namelist = set(zip_file.namelist()) if zip_file else set()
        type_display = {"image": "图像", "multimodal": "多模态", "text": "文本"}.get(category, "文本")
        
        # 校验前 500 条
        for i, item in enumerate(data[:500]):
            if not isinstance(item, dict): raise serializers.ValidationError(f"第 {i+1} 条必须是对象")
            
            # 1. 必需字段校验 (input + [answer/reference])
            if "input" not in item: raise serializers.ValidationError(f"第 {i+1} 条{type_display}题缺少 'input'")
            
            if evaluation_type == "objective":
                if "answer" not in item: raise serializers.ValidationError(f"第 {i+1} 条{type_display}题缺少 'answer'")
            elif evaluation_type == "subjective":
                if "reference" not in item: raise serializers.ValidationError(f"第 {i+1} 条{type_display}题缺少 'reference'")

            # 2. 图像存在性校验
            if category == "image":
                # 图像数据集：强制要求 image 字段且文件必须存在
                if "image" not in item:
                    raise serializers.ValidationError(f"第 {i+1} 条图像数据集题目缺少 'image' 字段")
                if item["image"] not in zip_namelist:
                    raise serializers.ValidationError(f"第 {i+1} 条题目引用的图片 '{item['image']}' 在 ZIP 中不存在")
            
            elif category == "multimodal":
                # 多模态数据集：采用“有图必检”原则（兼容纯文本条目和混合条目）
                # 只有当字段存在且不为空时才校验
                image_path = item.get("image")
                if image_path: 
                    if image_path not in zip_namelist:
                        raise serializers.ValidationError(f"第 {i+1} 条多模态题目引用的图片 '{image_path}' 在 ZIP 中不存在")

            # 3. 客观题 A-D 选项正则校验
            if evaluation_type == "objective":
                input_text = str(item["input"])
                # 增强正则：匹配 A. B. C. D. 且允许前后有换行或空格
                options = list(set(re.findall(r"(?:^|[\n\r\s]|\\n)([A-D])\.", input_text, re.IGNORECASE)))
                
                if len(options) != 4:
                    raise serializers.ValidationError(f"第 {i+1} 条客观题必须包含 A. B. C. D. 四个选项（当前检测到 {len(options)} 个）")
                
                ans = str(item["answer"]).strip().upper()
                if ans not in [opt.upper() for opt in options]:
                    raise serializers.ValidationError(f"第 {i+1} 条答案 '{ans}' 不在检测到的选项 {options} 中")

    # ========================== 辅助工具方法 ==========================

    def _convert_csv_to_json_format(self, csv_data, evaluation_type):
        converted = []
        req_fields = {'subjective': ['input', 'reference'], 'objective': ['input', 'answer'], 'adversarial': ['input']}.get(evaluation_type, ['input'])
        for i, row in enumerate(csv_data):
            item = {f: row.get(f) for f in req_fields if row.get(f)}
            if len(item) < len(req_fields):
                # 兼容性映射
                if 'input' not in item:
                    for k in ['question', 'prompt', 'text']:
                        if row.get(k): item['input'] = row[k]; break
            if 'input' not in item: raise serializers.ValidationError(f"第 {i+2} 行缺少必需字段")
            converted.append(item)
        return converted

    def _validate_zip_security(self, zip_file):
        for info in zip_file.infolist():
            if '..' in info.filename or info.filename.startswith(('/', '\\')):
                raise serializers.ValidationError(f"非法路径: {info.filename}")

    def _count_samples(self, file_obj, file_format):
        file_obj.seek(0)
        content = file_obj.read()
        try:
            if file_format == "csv": return max(0, len(content.decode('utf-8', 'ignore').strip().split('\n')) - 1)
            if file_format == "json": return len(json.loads(content))
            if file_format == "zip":
                with zipfile.ZipFile(io.BytesIO(content)) as zf:
                    json_files = [f for f in zf.namelist() if f.endswith('.json')]
                    if not json_files: return 0
                    target = "data.json" if "data.json" in json_files else json_files[0]
                    return len(json.loads(zf.read(target)))
        except: return 0
        finally: file_obj.seek(0)

    def _check_has_images(self, file_obj, file_format):
        if file_format != "zip": return False
        file_obj.seek(0)
        try:
            with zipfile.ZipFile(io.BytesIO(file_obj.read())) as zf:
                exts = ('.jpg', '.jpeg', '.png', '.webp')
                return any(f.lower().endswith(exts) for f in zf.namelist())
        except: return False

    def _count_images(self, file_obj, file_format):
        if file_format != "zip": return 0
        file_obj.seek(0)
        try:
            with zipfile.ZipFile(io.BytesIO(file_obj.read())) as zf:
                exts = ('.jpg', '.jpeg', '.png', '.webp')
                return sum(1 for f in zf.namelist() if f.lower().endswith(exts))
        except: return 0

    # ========================== 其他序列化字段 ==========================

    def get_file_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(f"/api/datasets/{obj.id}/download/") if obj.has_file() and request else None

    def get_has_file(self, obj): return obj.has_file()
    def get_is_followed(self, obj):
        user = self.context.get("request").user
        return obj.followers.filter(user=user).exists() if user and user.is_authenticated else False

    def get_star_count(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return UserStar.objects.filter(content_type=ct, object_id=obj.id).count()

    def get_is_starred(self, obj):
        user = self.context.get('request').user
        if not user or not user.is_authenticated: return False
        ct = ContentType.objects.get_for_model(obj)
        return UserStar.objects.filter(user=user, content_type=ct, object_id=obj.id).exists()

class DatasetDetailSerializer(DatasetSerializer):
    class Meta(DatasetSerializer.Meta): pass

class DatasetFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetFollow
        fields = ["id", "dataset", "created_at"]