from rest_framework import serializers
from .models import SystemEvent


class SystemEventSerializer(serializers.ModelSerializer):
    """
    系统事件序列化器，用于API返回
    """
    id = serializers.IntegerField(read_only=True)
    content = serializers.CharField(source='message', read_only=True)
    time = serializers.DateTimeField(source='created_at', read_only=True, format='%Y-%m-%dT%H:%M:%SZ')
    
    # 根据事件类型映射到前端需要的类型
    type = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    class Meta:
        model = SystemEvent
        fields = ['id', 'content', 'time', 'type', 'icon']

    def get_type(self, obj):
        """将事件类型映射到前端需要的类型"""
        type_mapping = {
            'dataset_upload': 'success',  # 绿色
            'model_add': 'primary',       # 蓝色
            'rank_up': 'warning',         # 金色/橙色
            'task_complete': 'info',      # 灰色
        }
        return type_mapping.get(obj.event_type, 'info')

    def get_icon(self, obj):
        """根据事件类型返回图标"""
        icon_mapping = {
            'dataset_upload': 'Folder',
            'model_add': 'Box',
            'rank_up': 'Top',
            'task_complete': 'CheckCircle',
        }
        return icon_mapping.get(obj.event_type, 'Info')