# apps/tasks/serializers.py
from rest_framework import serializers
from .models import EvaluationTask, EvaluationItem
from apps.models.models import My_Model  # 仅供类型提示 / 可选引用


# ------------------------------------
# 单条评测 item 序列化
# ------------------------------------
class EvaluationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationItem
        fields = [
            "id",
            "content",
            "correct_answer",
            "predicted_answer",
            "predicted_answer_2", 
            "is_correct",
            "score",
            "preference",
        ]


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
            "method",
            "myModel",        # 前端传入 myModel = My_Model 的 ID
            "myModel_name",
            "myModel_2",        
            "myModel_2_name",   
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
        method = data.get('method', self.instance.method if self.instance else None)
        my_model = data.get('myModel')

        # 如果是客观评测或主观评测，myModel 必须存在
        if method in ['objective', 'subjective'] and not my_model:
            raise serializers.ValidationError({"myModel": "客观评测和主观评测任务必须选择一个评测模型。"})

        # 如果是对抗评测，则 myModel 允许为空。

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
