from django.contrib import admin
from .models import SystemEvent


@admin.register(SystemEvent)
class SystemEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'actor_name', 'target_name', 'message_preview', 'created_at')
    list_filter = ('event_type', 'created_at')
    search_fields = ('actor_name', 'target_name', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def message_preview(self, obj):
        """显示消息预览，限制长度"""
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = '消息预览'
    
    def has_add_permission(self, request):
        """禁止手动添加系统事件"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改系统事件"""
        return False