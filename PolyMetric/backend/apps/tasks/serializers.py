from rest_framework import serializers
from .models import EvaluationTask, EvaluationItem, EvaluationModel


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
    model_name = serializers.CharField(source="model.name", read_only=True)

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
            "model",
            "model_name",
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

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)


# ------------------------------------
# Task 详情 Serializer（多一个 data 字段）
# ------------------------------------
class EvaluationTaskDetailSerializer(EvaluationTaskSerializer):
    data = EvaluationItemSerializer(source="items", many=True, read_only=True)

    class Meta(EvaluationTaskSerializer.Meta):
        fields = EvaluationTaskSerializer.Meta.fields + ["data"]
