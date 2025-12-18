from django.contrib import admin
from .models import Comment, CommentLike


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """评论管理后台"""
    list_display = ['id', 'user', 'content_preview', 'content_type', 'object_id', 'created_at', 'likes_count']
    list_filter = ['content_type', 'created_at']
    search_fields = ['content', 'user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        """显示内容预览"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容预览'
    
    def likes_count(self, obj):
        """显示点赞数"""
        return obj.likes.count()
    likes_count.short_description = '点赞数'


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    """评论点赞管理后台"""
    list_display = ['id', 'user', 'comment', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'comment__content']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
