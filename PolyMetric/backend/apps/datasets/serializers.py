from rest_framework import serializers
from .models import Dataset, DatasetFollow
from django.contrib.contenttypes.models import ContentType
from apps.users.models import UserStar
import os
import json
import zipfile
import tempfile
from apps.datasets.services.ai_capability_judge import ai_judge_capability
import re
import chardet

class DatasetSerializer(serializers.ModelSerializer):
    """
    数据集序列化器 - 自动验证版本
    
    设计变更：
    - is_verified 字段不再需要人工审核，而是根据格式验证和能力分析结果自动设置
    - 格式验证通过 + 能力分析成功 = is_verified=True
    - 任一环节失败 = is_verified=False
    """
    creator_id = serializers.IntegerField(source='creator.id', read_only=True)
    creator_username = serializers.CharField(source="creator.username", read_only=True)
    evaluation_type = serializers.CharField(required=False, allow_null=True)
    file_url = serializers.SerializerMethodField(read_only=True)
    has_file = serializers.SerializerMethodField(read_only=True)
    is_followed = serializers.SerializerMethodField(read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    def _sample_dataset(self, file_obj, file_format, limit=None):
        """
        从数据集中抽样前 N 条，用于 AI 判断能力标签
        使用动态样本数量
        """
        file_obj.seek(0)
        content = file_obj.read()

        import csv, io
        
        # 如果没有指定limit，使用动态计算
        if limit is None:
            total_samples = self._count_samples(file_obj, file_format)
            from apps.datasets.services.ai_capability_judge import calculate_sample_count
            limit = calculate_sample_count(total_samples)

        if file_format == "json":
            try:
                data = json.loads(content.decode("utf-8"))
                if isinstance(data, list):
                    return data[:limit]
            except Exception:
                return []

        if file_format == "csv":
            try:
                # 使用智能编码检测
                detected = chardet.detect(content)
                encoding = detected['encoding']
                confidence = detected['confidence']
                
                # 如果置信度低，尝试常见编码
                if confidence is None or confidence < 0.7:
                    for enc in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                        try:
                            text = content.decode(enc)
                            encoding = enc
                            break
                        except:
                            continue
                else:
                    text = content.decode(encoding)
                
                if text is None:
                    print("CSV文件编码无法识别，使用默认样本")
                    # 返回默认样本，避免AI分析失败
                    return [
                        {"input": "示例问题1", "answer": "A"},
                        {"input": "示例问题2", "answer": "B"}
                    ]
                
                reader = csv.DictReader(io.StringIO(text))
                samples = list(reader)[:limit]
                
                # 转换为统一格式，确保有必要的字段
                converted_samples = []
                for sample in samples:
                    item = {}
                    
                    # 尝试获取输入字段
                    for key in ['input', 'question', 'prompt', 'text']:
                        if key in sample:
                            item['input'] = sample[key]
                            break
                    
                    # 如果没有找到输入字段，使用第一个字段
                    if 'input' not in item and sample:
                        first_key = next(iter(sample.keys()))
                        item['input'] = sample[first_key]
                    
                    # 尝试获取答案字段
                    for key in ['answer', 'label', 'target', 'reference']:
                        if key in sample:
                            item[key] = sample[key]
                    
                    converted_samples.append(item)
                
                return converted_samples
            except Exception as e:
                print(f"CSV抽样失败: {e}，使用默认样本")
                # 返回默认样本，避免AI分析失败
                return [
                    {"input": "示例问题1", "answer": "A"},
                    {"input": "示例问题2", "answer": "B"}
                ]

        if file_format == "zip":
            try:
                import zipfile
                with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
                    # 查找JSON文件
                    json_files = [
                        f for f in zf.namelist()
                        if f.lower().endswith('.json') and not f.endswith('/')
                    ]
                    
                    if not json_files:
                        return []
                    
                    # 优先使用data.json
                    target_file = "data.json" if "data.json" in json_files else json_files[0]
                    
                    with zf.open(target_file) as f:
                        json_content = f.read()
                        try:
                            data = json.loads(json_content.decode('utf-8'))
                            if isinstance(data, list):
                                return data[:limit]
                            elif isinstance(data, dict):
                                # 查找常见的数据数组键
                                data_keys = ['data', 'items', 'records', 'rows', 'samples', 'entries', 'test_cases', 'questions']
                                for key in data_keys:
                                    if key in data and isinstance(data[key], list):
                                        return data[key][:limit]
                                
                                # 如果是测评数据集，检查是否有特定测评类型的数据结构
                                for evaluation_type in ['subjective', 'objective', 'adversarial']:
                                    if evaluation_type in data and isinstance(data[evaluation_type], list):
                                        return data[evaluation_type][:limit]
                                
                                # 如果都没有找到，返回空列表
                                return []
                        except Exception:
                            return []
            except Exception:
                return []

        return []

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
            "updated_at", "star_count", "is_starred",
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
        直接抛出 ValidationError 供上层捕获
        """
        if file_obj is None:
            return
           
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
                    # 使用chardet进行智能编码检测
                    detected = chardet.detect(content)
                    encoding = detected['encoding']
                    confidence = detected['confidence']
                    
                    # 如果置信度低，尝试常见编码
                    if confidence is None or confidence < 0.7:
                        for enc in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                            try:
                                text = content.decode(enc)
                                encoding = enc
                                break
                            except:
                                continue
                    else:
                        text = content.decode(encoding)
                    
                    if text is None:
                        raise serializers.ValidationError("CSV文件编码无法识别")
                    
                    # 解析CSV内容
                    reader = csv.DictReader(io.StringIO(text))
                    csv_data = list(reader)
                    
                    if len(csv_data) == 0:
                        raise serializers.ValidationError("CSV文件不能为空")
                    
                    # 将CSV数据转换为与JSON相同的格式，便于统一验证
                    converted_data = self._convert_csv_to_json_format(csv_data, evaluation_type)
                    
                    # 根据测评类型验证格式
                    self._validate_data_by_evaluation_type(converted_data, evaluation_type, category)
                   
                except Exception as e:
                    if isinstance(e, serializers.ValidationError):
                        raise
                    raise serializers.ValidationError(f"CSV文件解析错误: {str(e)}")
                
            elif file_ext == "zip":
                import io
                try:
                    with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
                        # 1. ZIP安全性检查
                        self._validate_zip_security(zf)
                        
                        # 2. 查找JSON文件
                        json_files = [
                            f for f in zf.namelist()
                            if f.lower().endswith('.json') and not f.endswith('/')
                        ]
                        
                        if not json_files:
                            raise serializers.ValidationError("ZIP文件中未找到JSON文件")
                        
                        # 3. 优先使用data.json
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
                                
                            # 5. 根据测评类型验证格式 (传入 zf 以便检查图片路径)
                            self._validate_data_by_evaluation_type(data, evaluation_type, category, zf)
                                
                except Exception as e:
                    if isinstance(e, serializers.ValidationError):
                        raise
                    raise serializers.ValidationError(f"ZIP文件解析错误: {str(e)}")
            else:
                # 其他格式暂时跳过验证
                return
                        
            return True
           
        except serializers.ValidationError:
            # 验证失败，抛出异常
            raise
        except Exception as e:
            # 验证失败，抛出异常
            raise serializers.ValidationError(f"文件验证失败: {str(e)}")
        finally:
            file_obj.seek(0)
    
    def _convert_csv_to_json_format(self, csv_data, evaluation_type):
        """
        将CSV数据转换为与JSON相同的格式，便于统一验证
        使用更严格的字段映射逻辑
        """
        converted_data = []
        
        # 定义必需字段
        required_fields = self._get_required_fields(evaluation_type)
        
        for i, row in enumerate(csv_data):
            item = {}
            
            # 严格检查必需字段
            for field in required_fields:
                if field in row and row[field]:
                    item[field] = row[field]
                elif field == 'input':
                    # input字段特殊处理：尝试常见字段名
                    input_fields = ['input', 'question', 'prompt', 'text']
                    found_input = False
                    for input_field in input_fields:
                        if input_field in row and row[input_field]:
                            item['input'] = row[input_field]
                            found_input = True
                            break
                    
                    if not found_input:
                        # 如果没有找到标准输入字段，使用第一个非空字段
                        for key, value in row.items():
                            if value and value.strip():
                                item['input'] = value
                                break
                else:
                    # 其他必需字段必须有明确的字段名
                    pass
            
            # 验证必需字段是否存在
            missing_fields = [field for field in required_fields if field not in item]
            if missing_fields:
                raise serializers.ValidationError(
                    f"第{i+2}行数据缺少必需字段: {', '.join(missing_fields)}"
                )
            
            # 确保item不为空
            if item:
                converted_data.append(item)
        
        return converted_data
    
    def _get_required_fields(self, evaluation_type):
        """获取测评类型所需的字段"""
        if evaluation_type == 'subjective':
            return ['input', 'reference']
        elif evaluation_type == 'objective':
            return ['input', 'answer']
        elif evaluation_type == 'adversarial':
            return ['input']
        else:
            return ['input']
    
    def _validate_data_by_evaluation_type(self, data, evaluation_type, category=None, zip_file=None):
        """
        根据测评类型验证数据格式
        """
        if len(data) == 0:
            raise serializers.ValidationError("数据集不能为空")
        
        # 预先获取 ZIP 内文件清单 (如果是图像/多模态且是 ZIP)
        zip_namelist = set(zip_file.namelist()) if zip_file else set()
        
        # 为了性能，如果数据集极大，全量校验前 500 条
        check_data = data[:500]
        
        # 根据测评类型验证格式
        # ---------- 客观评测 ----------
        if evaluation_type == "objective":
            for i, item in enumerate(check_data):
                if not isinstance(item, dict):
                    raise serializers.ValidationError(f"第 {i+1} 条客观题必须是对象（dict）")

                # 字段存在性
                if "input" not in item:
                    raise serializers.ValidationError(f"第 {i+1} 条客观题缺少字段 'input'")
                if "answer" not in item:
                    raise serializers.ValidationError(f"第 {i+1} 条客观题缺少字段 'answer'")

                # 处理内容
                input_text = str(item["input"]).replace('\\n', '\n')
                answer = str(item["answer"])

                # 类型校验
                if not input_text.strip():
                    raise serializers.ValidationError(f"第 {i+1} 条客观题的 'input' 必须是非空内容")

                # 图像/多模态路径检查
                if category in ["image", "multimodal"]:
                    if "image" not in item:
                        raise serializers.ValidationError(f"第 {i+1} 条图像客观题缺少字段 'image'")
                    if item["image"] not in zip_namelist:
                        raise serializers.ValidationError(f"第 {i+1} 条题目引用的图片 '{item['image']}' 在压缩包中不存在")

                # 使用多个正则表达式匹配选项
                option_patterns = [
                    re.compile(r"\\n([A-Z])\.", re.IGNORECASE),
                    re.compile(r"\n([A-Z])\.", re.IGNORECASE),
                    re.compile(r"\b([A-Z])\.", re.IGNORECASE)
                ]
                
                options = []
                for pattern in option_patterns:
                    found_options = pattern.findall(input_text)
                    options.extend(found_options)
                
                options = list(set([opt.upper() for opt in options]))

                if len(options) != 4:
                    raise serializers.ValidationError(
                        f"第 {i+1} 条客观题必须包含且仅包含 A. B. C. D. 四个选项（当前检测到 {len(options)} 个）"
                    )

                # 校验答案格式
                answer = answer.strip().upper()
                if not re.fullmatch(r"[A-Z]", answer):
                    raise serializers.ValidationError(
                        f"第 {i+1} 条客观题的 'answer' 必须是单个选项字母（如 A / B / C）"
                    )

                if answer not in options:
                    raise serializers.ValidationError(
                        f"第 {i+1} 条客观题的答案 '{answer}' 不在题目选项 {options} 中"
                    )

        # ---------- 主观评测 ----------
        elif evaluation_type == "subjective":
            for i, item in enumerate(check_data):
                if not isinstance(item, dict):
                    raise serializers.ValidationError(f"第 {i+1} 条主观题必须是对象（dict）")

                if "input" not in item:
                    raise serializers.ValidationError(f"第 {i+1} 条主观题缺少字段 'input'")
                if "reference" not in item:
                    raise serializers.ValidationError(f"第 {i+1} 条主观题缺少字段 'reference'")

                if not str(item["input"]).strip():
                    raise serializers.ValidationError(f"第 {i+1} 条主观题的 'input' 必须是非空内容")

                if not str(item["reference"]).strip():
                    raise serializers.ValidationError(f"第 {i+1} 条主观题的 'reference' 必须是非空内容")
                
                # 图像/多模态路径检查
                if category in ["image", "multimodal"]:
                    if "image" not in item:
                        raise serializers.ValidationError(f"第 {i+1} 条图像主观题缺少字段 'image'")
                    if item["image"] not in zip_namelist:
                        raise serializers.ValidationError(f"第 {i+1} 条题目引用的图片 '{item['image']}' 在压缩包中不存在")

        # ---------- 对抗评测 ----------
        elif evaluation_type == "adversarial":
            for i, item in enumerate(check_data):
                if not isinstance(item, dict):
                    raise serializers.ValidationError(f"第 {i+1} 条对抗题必须是对象（dict）")

                if "input" not in item:
                    raise serializers.ValidationError(f"第 {i+1} 条对抗题缺少字段 'input'")

                if not str(item["input"]).strip():
                    raise serializers.ValidationError(f"第 {i+1} 条对抗题的 'input' 必须是非空内容")
                
                # 图像/多模态路径检查
                if category in ["image", "multimodal"]:
                    if "image" not in item:
                        raise serializers.ValidationError(f"第 {i+1} 条图像对抗题缺少字段 'image'")
                    if item["image"] not in zip_namelist:
                        raise serializers.ValidationError(f"第 {i+1} 条题目引用的图片 '{item['image']}' 在压缩包中不存在")

        else:
            raise serializers.ValidationError(f"未知的评测类型：{evaluation_type}")
    
    def _validate_zip_security(self, zip_file):
        """
        验证ZIP文件的安全性
        防止路径遍历攻击和ZIP炸弹
        """
        MAX_SINGLE_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        MAX_TOTAL_SIZE = 200 * 1024 * 1024  # 200MB
        MAX_FILE_COUNT = 1000  # 最大文件数量
        
        total_size = 0
        file_count = 0
        
        for file_info in zip_file.infolist():
            file_count += 1
            
            # 检查文件数量限制
            if file_count > MAX_FILE_COUNT:
                raise serializers.ValidationError(
                    f"ZIP文件包含过多文件（超过{MAX_FILE_COUNT}个），可能存在安全风险"
                )
            
            # 防止路径遍历攻击
            filename = file_info.filename
            if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
                raise serializers.ValidationError(
                    f"ZIP文件包含不安全的路径: {filename}"
                )
            
            # 检查文件大小
            file_size = file_info.file_size
            if file_size > MAX_SINGLE_FILE_SIZE:
                raise serializers.ValidationError(
                    f"ZIP文件中的文件 {filename} 过大（超过{MAX_SINGLE_FILE_SIZE//1024//1024}MB）"
                )
            
            total_size += file_size
            
            # 检查总大小
            if total_size > MAX_TOTAL_SIZE:
                raise serializers.ValidationError(
                    f"ZIP文件总大小过大（超过{MAX_TOTAL_SIZE//1024//1024}MB）"
                )
    
    def _validate_image_paths(self, zip_file, json_data):
        """
        验证JSON数据中的图片路径是否在ZIP中存在
        """
        zip_files = set(zip_file.namelist())
        missing_images = []
        
        for item in json_data:
            if 'image' in item:
                image_path = item['image']
                if image_path not in zip_files:
                    missing_images.append(image_path)
        
        if missing_images:
            raise serializers.ValidationError(
                f"以下图片文件在ZIP中不存在: {', '.join(missing_images[:5])}"
                f"{'...' if len(missing_images) > 5 else ''}"
            )

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
        
        file_format = validated_data.get("file_format")
        

        
        if file_obj and file_format:
        
            # 统计样本数量和图片信息
        
            file_format = validated_data.get("file_format", "").lower()
        
            validated_data["file_size"] = round(file_obj.size / (1024 * 1024), 6)
        
            validated_data["sample_count"] = self._count_samples(file_obj, file_format)
        
            validated_data["has_images"] = self._check_has_images(file_obj, file_format)
        
            validated_data["image_count"] = self._count_images(file_obj, file_format)
        
            
        
            # 设置初始状态
        
            validated_data["is_verified"] = False
        
            validated_data["capability_tag"] = "processing"
        
            validated_data["capability_dimension"] = "other"
        
        else:
        
            validated_data["file_size"] = 0.0
        
            validated_data["sample_count"] = 0
        
            validated_data["has_images"] = False
        
            validated_data["image_count"] = 0
        
            validated_data["capability_tag"] = "other"
        
            validated_data["capability_dimension"] = "other"
        
            validated_data["is_verified"] = False
        

        
        # 创建数据集
        
        dataset = super().create(validated_data)
        
        
        
        # 异步分析能力维度（如果有文件）
        
        if file_obj and file_format and validated_data.get("capability_tag") == "processing":
        
            from apps.tasks.tasks import analyze_dataset_capability
        
            analyze_dataset_capability.delay(dataset.id)
        
        
        
        return dataset
        

        
    def update(self, instance, validated_data):
        
        """更新数据集"""
        
        file_obj = validated_data.get("file_path")
        
        
        
        # 检查数据集是否已审核
        
        if not instance.is_verified:
        
            raise serializers.ValidationError("只有已审核通过的数据集才能修改")
        
        
        
        if file_obj:
        
            # 删除旧文件
        
            if instance.has_file():
        
                try:
        
                    old_path = instance.file_path.path
        
                    if os.path.exists(old_path):
        
                        os.remove(old_path)
        
                except:
        
                    pass
        
            
        
            # 计算文件大小和格式
        
            validated_data["file_size"] = round(file_obj.size / (1024 * 1024), 6)
        
            file_format = validated_data.get("file_format", instance.file_format).lower()
        
            
        
            # 统计样本数量和图片信息
        
            validated_data["sample_count"] = self._count_samples(file_obj, file_format)
        
            validated_data["has_images"] = self._check_has_images(file_obj, file_format)
        
            validated_data["image_count"] = self._count_images(file_obj, file_format)
        
            
        
            # 设置初始状态为处理中
        
            validated_data["capability_tag"] = "processing"
        
            validated_data["capability_dimension"] = "other"
        
        
        
        # 更新数据集
        
        dataset = super().update(instance, validated_data)
        
        
        
        # 异步分析能力维度
        
        if file_obj and validated_data.get("capability_tag") == "processing":
        
            from apps.tasks.tasks import analyze_dataset_capability
        
            analyze_dataset_capability.delay(dataset.id)
        
        
        
        return dataset
        

class DatasetDetailSerializer(DatasetSerializer):
    """数据集详情序列化器"""
    class Meta(DatasetSerializer.Meta):
        pass


class DatasetFollowSerializer(serializers.ModelSerializer):
    """关注序列化器"""
    class Meta:
        model = DatasetFollow
        fields = ["id", "dataset", "created_at"]
