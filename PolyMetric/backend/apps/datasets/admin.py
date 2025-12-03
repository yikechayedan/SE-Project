from django.contrib import admin
from .models import Dataset, DatasetFollow

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "creator", "category", "file_format", "is_public", "is_verified", "created_at")
    list_filter = ("category", "file_format", "is_public", "is_verified")
    search_fields = ("name", "creator__username")
    ordering = ("-created_at",)

@admin.register(DatasetFollow)
class DatasetFollowAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "dataset", "created_at")
    search_fields = ("user__username", "dataset__name")
    ordering = ("-created_at",)
