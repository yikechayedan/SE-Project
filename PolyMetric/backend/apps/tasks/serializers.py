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
