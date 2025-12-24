# apps/tasks/serializers.py
from rest_framework import serializers
from .models import EvaluationTask, EvaluationItem
from apps.models.models import My_Model  # 仅供类型提示 / 可选引用


# ------------------------------------
# 单条评测 item 序列化
# ------------------------------------
class EvaluationItemSerializer(serializers.ModelSerializer):
    # 定义用于存放图片 Base64 的虚拟字段
    predicted_image_data = serializers.SerializerMethodField()
    predicted_image_2_data = serializers.SerializerMethodField()

    class Meta:
        model = EvaluationItem
        fields = "__all__"

    def get_predicted_image_data(self, obj):
        return self._get_base64_from_answer(obj.predicted_answer)

    def get_predicted_image_2_data(self, obj):
        return self._get_base64_from_answer(obj.predicted_answer_2)

    def _get_base64_from_answer(self, answer):
        if not answer or '/media/generated_images/' not in answer:
            return None
            
        import re
        import os
        import base64
        from django.conf import settings
        
        # 匹配 Markdown 中的路径：![...](/media/generated_images/xxx.png)
        match = re.search(r'\/media\/(generated_images\/[^)]+)', answer)
        if match:
            rel_path = match.group(1).strip().rstrip(')')
            filename = os.path.basename(rel_path)
            full_path = os.path.join(settings.MEDIA_ROOT, "generated_images", filename)
            
            if os.path.exists(full_path):
                try:
                    with open(full_path, "rb") as f:
                        return base64.b64encode(f.read()).decode('utf-8')
                except Exception:
                    return None
        return None


# ------------------------------------
# Task 列表 & 创建 Serializer
# ------------------------------------
class EvaluationTaskSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source="creator.username", read_only=True)
    dataset_name = serializers.CharField(source="dataset.name", read_only=True)

    # ⭐ 对齐 API 文档：myModel_name
    myModel_name = serializers.CharField(source="myModel.name", read_only=True)

    # ⭐ Model B（对抗评测）
    myModel_2_name = serializers.CharField(
        source="myModel_2.name", read_only=True
    )

    class Meta:
        model = EvaluationTask
        fields = [
            "id",
            "name",
            "description",
            "creator",
            "creator_username",
            "dataset",
            "dataset_name",
            "judge_type",
            "method",
            "myModel",        # 前端传入 myModel = My_Model 的 ID
            "myModel_name",
            "myModel_2",        
            "myModel_2_name",  
            "judge_model",  
            "status",
            "accuracy",
            "score",
            "created_at",
            "updated_at",
            "time_used",
        ]
        read_only_fields = [
            "creator",
            "status",
            "accuracy",
            "score",
            "created_at",
            "updated_at",
            "time_used",
        ]

    def validate(self, data):
        method = data.get("method", self.instance.method if self.instance else None)
        judge_type = data.get(
            "judge_type",
            self.instance.judge_type if self.instance else "human"
        )

        # 允许使用裁判的评测类型
        if method not in ("subjective", "adversarial"):
            if judge_type != "human":
                raise serializers.ValidationError({
                    "judge_type": "Only subjective/adversarial tasks can set judge_type"
                })

        # judge_type 合法性
        if method in ("subjective", "adversarial"):
            if judge_type not in ("human", "model"):
                raise serializers.ValidationError({
                    "judge_type": "judge_type must be human or model"
                })

        # ⭐ 只有「模型裁判」才强制要求 judge_model
        if judge_type == "model":
            judge_model = data.get("judge_model") or getattr(self.instance, "judge_model", None)
            if not judge_model:
                raise serializers.ValidationError({
                    "judge_model": "模型裁判模式下必须指定裁判模型"
                })

        # ⭐ 新增：验证任务的 method 与数据集的 evaluation_type 是否匹配
        dataset = data.get("dataset")
        if dataset and method:
            # 如果是更新操作且没有提供新的 dataset，则使用现有的
            if self.instance and not data.get("dataset"):
                dataset = self.instance.dataset
            
            # 验证评测类型匹配
            if dataset.evaluation_type != method:
                evaluation_type_map = {
                    "subjective": "主观评测",
                    "objective": "客观评测",
                    "adversarial": "对抗评测"
                }
                dataset_type = evaluation_type_map.get(dataset.evaluation_type, dataset.evaluation_type)
                task_type = evaluation_type_map.get(method, method)
                raise serializers.ValidationError({
                    "dataset_format_error": f"数据集格式错误：当前数据集为{dataset_type}格式，但创建的评测任务为{task_type}类型，两者不匹配。请选择正确的评测类型或使用匹配的数据集。"
                })

        return data


    def create(self, validated_data):
        # 保险起见，从 context 中再写一次 creator
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["creator"] = request.user
        return super().create(validated_data)


# ------------------------------------
# Task 详情 Serializer（多一个 data 字段）
# ------------------------------------
class EvaluationTaskDetailSerializer(EvaluationTaskSerializer):
    # API 文档中的 data 字段，包含所有条目列表
    data = EvaluationItemSerializer(source="items", many=True, read_only=True)

    class Meta(EvaluationTaskSerializer.Meta):
        fields = EvaluationTaskSerializer.Meta.fields + ["data"]