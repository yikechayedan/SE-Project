from rest_framework import serializers
from .models import EvaluationTask

class EvaluationTaskSerializer(serializers.ModelSerializer):
    """评测任务序列化器（对齐用户接口格式）"""
    creator_username = serializers.CharField(source="creator.username", read_only=True)
    dataset_name = serializers.CharField(source="dataset.name", read_only=True)

    class Meta:
        model = EvaluationTask
        fields = [
            "id", "name", "description", "creator", "creator_username",
            "dataset", "dataset_name", "status", "accuracy", 
            "precision", "recall", "f1_score", "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "creator", "creator_username", "dataset_name",
            "status", "accuracy", "precision", "recall", "f1_score",
            "created_at", "updated_at"
        ]

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)