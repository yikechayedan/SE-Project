from rest_framework import serializers
from .models import Dataset, DatasetFollow
from django.contrib.contenttypes.models import ContentType
from apps.users.models import UserStar
import os
import json
from apps.datasets.services.ai_capability_judge import ai_judge_capability


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
    evaluation_type = serializers.CharField(required=False, allow_null=True)
    file_url = serializers.SerializerMethodField(read_only=True)
    has_file = serializers.SerializerMethodField(read_only=True)
    is_followed = serializers.SerializerMethodField(read_only=True)
    # 1. 统计总数
    star_count = serializers.SerializerMethodField()
    # 2. 当前用户状态
    is_starred = serializers.SerializerMethodField()

    def _sample_dataset(self, file_obj, file_format, limit=5):
        """
        从数据集中抽样前 N 条，用于 AI 判断能力标签
        """
        file_obj.seek(0)
        content = file_obj.read()

        import json, csv, io

        if file_format == "json":
            try:
                data = json.loads(content.decode("utf-8"))
                if isinstance(data, list):
                    return data[:limit]
            except Exception:
                return []

        if file_format == "csv":
            try:
                text = content.decode("utf-8", errors="ignore")
                reader = csv.DictReader(io.StringIO(text))
                return list(reader)[:limit]
            except Exception:
                return []

        return []

    
    def ai_judge_capability(samples):
        prompt = build_prompt(samples)
        response = call_llm_api(prompt)

        tag = response.strip().lower()

        if tag not in ["language", "reasoning", "coding"]:
            return "language"  # 兜底

        return tag
    

    
    class Meta:
        model = Dataset
        fields = [
            "id", "name", "description", "category", "capability_dimension", "evaluation_type", "file_format",
            "file_size", "sample_count", "creator", "creator_id", "creator_username",
            "is_public", "is_verified", "is_followed", "has_file", "star_count", "is_starred",
            "created_at", "updated_at", "file_url", "file_path","capability_tag","has_images", "image_count"
        ]
        read_only_fields = [
            "id", "creator", "file_size", "sample_count", "created_at", 
            "updated_at", "is_verified", "star_count", "is_starred",
            "capability_tag","has_images", "image_count"
        ]


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

    def get_star_count(self, obj):
        """获取点赞总数"""
        ct = ContentType.objects.get_for_model(obj)
        return UserStar.objects.filter(content_type=ct, object_id=obj.id).count()

    def get_is_starred(self, obj):
        """判断当前用户是否已点赞"""
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        ct = ContentType.objects.get_for_model(obj)
        return UserStar.objects.filter(user=user, content_type=ct, object_id=obj.id).exists()

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

    def validate(self, attrs):
        """
        全局验证方法，用于验证数据集格式
        """
        file_obj = attrs.get("file_path")
        evaluation_type = attrs.get("evaluation_type", "subjective")
        
        if file_obj:
            self.validate_dataset_format(file_obj, evaluation_type, attrs.get("category"))
        
        return attrs

    def validate_dataset_format(self, file_obj, evaluation_type, category=None):
        """
        验证数据集格式是否符合对应的测评类型要求
        """
        if file_obj is None:
            return True
            
        try:
            file_obj.seek(0)
            content = file_obj.read()
            file_ext = file_obj.name.split(".")[-1].lower()
            
            # 处理不同格式的文件
            if file_ext == "json":
                try:
                    data = json.loads(content.decode('utf-8'))
                except:
                    raise serializers.ValidationError("JSON文件格式错误，无法解析")
                    
                if not isinstance(data, list):
                    raise serializers.ValidationError("数据集必须是数组格式")
                    
                if len(data) == 0:
                    raise serializers.ValidationError("数据集不能为空")
                    
                # 根据测评类型验证格式
                self._validate_data_by_evaluation_type(data, evaluation_type, category)
                
            elif file_ext == "csv":
                import csv
                import io
                try:
                    # 尝试多种编码
                    text = None
                    for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                        try:
                            text = content.decode(encoding)
                            break
                        except:
                            continue
                    
                    if text is None:
                        raise serializers.ValidationError("CSV文件编码无法识别")
                    
                    # 解析CSV内容
                    reader = csv.DictReader(io.StringIO(text))
                    data = list(reader)
                    
                    if len(data) == 0:
                        raise serializers.ValidationError("CSV文件不能为空")
                    
                    # 根据测评类型验证格式
                    self._validate_data_by_evaluation_type(data, evaluation_type, category)
                    
                except Exception as e:
                    if isinstance(e, serializers.ValidationError):
                        raise
                    raise serializers.ValidationError(f"CSV文件解析错误: {str(e)}")
                
            elif file_ext == "zip":
                import zipfile
                import io
                try:
                    with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
                        # 查找JSON文件
                        json_files = [
                            f for f in zf.namelist()
                            if f.lower().endswith('.json') and not f.endswith('/')
                        ]
                        
                        if not json_files:
                            raise serializers.ValidationError("ZIP文件中未找到JSON文件")
                        
                        # 优先使用data.json
                        target_file = "data.json" if "data.json" in json_files else json_files[0]
                        
                        with zf.open(target_file) as f:
                            json_content = f.read()
                            try:
                                data = json.loads(json_content.decode('utf-8'))
                            except:
                                raise serializers.ValidationError(f"ZIP文件中的{target_file}格式错误，无法解析")
                            
                            if not isinstance(data, list):
                                raise serializers.ValidationError("数据集必须是数组格式")
                                
                            if len(data) == 0:
                                raise serializers.ValidationError("数据集不能为空")
                            
                            # 根据测评类型验证格式
                            self._validate_data_by_evaluation_type(data, evaluation_type, category)
                            
                except Exception as e:
                    if isinstance(e, serializers.ValidationError):
                        raise
                    raise serializers.ValidationError(f"ZIP文件解析错误: {str(e)}")
            else:
                # 其他格式暂时跳过验证
                return True
                        
            return True
            
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(f"验证数据集格式时出错: {str(e)}")
        finally:
            file_obj.seek(0)
    
    def _validate_data_by_evaluation_type(self, data, evaluation_type, category=None):
        """
        根据测评类型验证数据格式
        """
        # 图像类别的数据集可以有更灵活的结构
        if category == "image":
            # 图像数据集：只验证基本结构，不强制特定字段
            for i, item in enumerate(data[:5]):  # 只检查前5个项目，提高性能
                if not isinstance(item, dict):
                    raise serializers.ValidationError(f"第{i+1}个项目必须是对象格式")
                # 图像数据集至少需要有一个字段
                if len(item.keys()) == 0:
                    raise serializers.ValidationError(f"图像数据集第{i+1}个项目不能为空")
            return
        
        # 根据测评类型验证格式
        if evaluation_type == "subjective":
            # 主观测评：每个项目必须包含 input 和 reference 字段
            for i, item in enumerate(data[:5]):  # 只检查前5个项目，提高性能
                if not isinstance(item, dict):
                    raise serializers.ValidationError(f"第{i+1}个项目必须是对象格式")
                if "input" not in item:
                    raise serializers.ValidationError(f"主观测评数据集第{i+1}个项目缺少必需的 'input' 字段")
                if "reference" not in item:
                    raise serializers.ValidationError(f"主观测评数据集第{i+1}个项目缺少必需的 'reference' 字段")
                    
        elif evaluation_type == "objective":
            # 客观测评：每个项目必须包含 input 和 answer 字段
            for i, item in enumerate(data[:5]):
                if not isinstance(item, dict):
                    raise serializers.ValidationError(f"第{i+1}个项目必须是对象格式")
                if "input" not in item:
                    raise serializers.ValidationError(f"客观测评数据集第{i+1}个项目缺少必需的 'input' 字段")
                if "answer" not in item:
                    raise serializers.ValidationError(f"客观测评数据集第{i+1}个项目缺少必需的 'answer' 字段")
                    
        elif evaluation_type == "adversarial":
            # 对抗测评：每个项目只需包含 input 字段
            for i, item in enumerate(data[:5]):
                if not isinstance(item, dict):
                    raise serializers.ValidationError(f"第{i+1}个项目必须是对象格式")
                if "input" not in item:
                    raise serializers.ValidationError(f"对抗测评数据集第{i+1}个项目缺少必需的 'input' 字段")

    def _count_images(self, file_obj, file_format):
        """
        统计ZIP文件中的图片数量
        """
        if file_format != "zip":
            return 0
            
        try:
            file_obj.seek(0)
            content = file_obj.read()
            
            import zipfile
            import io
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
            
            with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
                image_files = [
                    f for f in zf.namelist()
                    if any(f.lower().endswith(ext) for ext in image_extensions) and not f.endswith('/')
                ]
                return len(image_files)
        except Exception as e:
            print(f"统计图片数量时出错: {e}")
            return 0
        finally:
            file_obj.seek(0)
    
    def _check_has_images(self, file_obj, file_format):
        """
        检查数据集是否包含图片
        """
        if file_format != "zip":
            return False
            
        try:
            file_obj.seek(0)
            content = file_obj.read()
            
            import zipfile
            import io
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
            
            with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
                image_files = [
                    f for f in zf.namelist()
                    if any(f.lower().endswith(ext) for ext in image_extensions) and not f.endswith('/')
                ]
                return len(image_files) > 0
        except Exception as e:
            print(f"检查图片时出错: {e}")
            return False
        finally:
            file_obj.seek(0)
    
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
                try:
                    data = json.loads(content.decode('utf-8'))
                    if isinstance(data, list):
                        return len(data)
                    elif isinstance(data, dict):
                        # 查找常见的数据数组键，包括测评相关的键
                        data_keys = ['data', 'items', 'records', 'rows', 'samples', 'entries', 'test_cases', 'questions']
                        for key in data_keys:
                            if key in data and isinstance(data[key], list):
                                return len(data[key])
                        
                        # 如果是测评数据集，检查是否有特定测评类型的数据结构
                        for evaluation_type in ['subjective', 'objective', 'adversarial']:
                            if evaluation_type in data and isinstance(data[evaluation_type], list):
                                return len(data[evaluation_type])
                        
                        # 如果都没有找到，返回1（单个对象）
                        return 1
                except json.JSONDecodeError:
                    return 0
                except Exception:
                    return 0
                    
            elif file_format == "zip":
                # ZIP: 返回JSON文件中的数据条目数量，如果没有JSON则返回文件数量
                import zipfile
                import io
                import json
                try:
                    with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
                        # 查找JSON文件
                        json_files = [
                            f for f in zf.namelist()
                            if f.lower().endswith('.json') and not f.endswith('/')
                        ]
                        
                        if json_files:
                            # 优先查找data.json
                            target_file = "data.json" if "data.json" in json_files else json_files[0]
                            
                            with zf.open(target_file) as f:
                                json_content = f.read()
                                try:
                                    data = json.loads(json_content.decode('utf-8'))
                                    if isinstance(data, list):
                                        return len(data)
                                    elif isinstance(data, dict):
                                        # 查找常见的数据数组键
                                        data_keys = ['data', 'items', 'records', 'rows', 'samples', 'entries', 'test_cases', 'questions']
                                        for key in data_keys:
                                            if key in data and isinstance(data[key], list):
                                                return len(data[key])
                                        
                                        # 如果是测评数据集，检查是否有特定测评类型的数据结构
                                        for evaluation_type in ['subjective', 'objective', 'adversarial']:
                                            if evaluation_type in data and isinstance(data[evaluation_type], list):
                                                return len(data[evaluation_type])
                                        
                                        return 1
                                except json.JSONDecodeError:
                                    pass
                                except Exception:
                                    pass
                         
                        # 如果没有JSON文件或解析失败，返回0（无法确定样本数量）
                        return 0
                except Exception:
                    return 0
        except Exception as e:
            print(f"统计样本数量时出错: {e}")
            return 0
        finally:
            file_obj.seek(0)

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user

        file_obj = validated_data.get("file_path")
        evaluation_type = validated_data.get("evaluation_type", "subjective")
        file_format = validated_data.get("file_format")

        if file_obj and file_format:
            # 1️⃣ 抽样
            samples = self._sample_dataset(file_obj, file_format)
            # 验证数据集格式
            self.validate_dataset_format(file_obj, evaluation_type, validated_data.get("category"))
            
            # 计算文件大小 (MB)

            # 2️⃣ AI 判断能力标签
            if samples:
                capability = ai_judge_capability(samples)
                validated_data["capability_tag"] = capability

                        # 统计样本数量
            file_format = validated_data.get("file_format", "").lower()
            validated_data["file_size"] = round(file_obj.size / (1024 * 1024), 6)
            validated_data["sample_count"] = self._count_samples(file_obj, file_format)
            validated_data["has_images"] = self._check_has_images(file_obj, file_format)
            validated_data["image_count"] = self._count_images(file_obj, file_format)
        else:
            validated_data["file_size"] = 0.0
            validated_data["sample_count"] = 0
            validated_data["has_images"] = False
            validated_data["image_count"] = 0

        return super().create(validated_data)


    def update(self, instance, validated_data):
        """更新数据集"""
        file_obj = validated_data.get("file_path")
        evaluation_type = validated_data.get("evaluation_type", instance.evaluation_type)
        
        if file_obj:
            # 验证数据集格式
            self.validate_dataset_format(file_obj, evaluation_type, validated_data.get("category"))
            
            # 删除旧文件
            if instance.has_file():
                try:
                    old_path = instance.file_path.path
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except:
                    pass
            
            validated_data["file_size"] = round(file_obj.size / (1024 * 1024), 6)
            file_format = validated_data.get("file_format", instance.file_format).lower()
            validated_data["sample_count"] = self._count_samples(file_obj, file_format)
            validated_data["has_images"] = self._check_has_images(file_obj, file_format)
            validated_data["image_count"] = self._count_images(file_obj, file_format)
        
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
