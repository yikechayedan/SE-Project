# apps/models/admin.py
from django.contrib import admin

from apps.models.models import Model, ModelFollow  # 改为绝对导入

@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'company', 'category', 'version', 'release_date', 'created_at']
    search_fields = ['name', 'company', 'description']
    list_filter = ['category', 'release_date']
    date_hierarchy = 'created_at'

@admin.register(ModelFollow)
class ModelFollowAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'model', 'created_at']
    search_fields = ['user__username', 'model__name']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'