# apps/models/admin.py
from django.contrib import admin
from .models import My_Model, ModelFollow

@admin.register(My_Model)
class MyModelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'company',
        'category',
        'version',
        'parameter_size',
        'release_date',
        'created_at'
    )
    search_fields = ('name', 'company')
    list_filter = ('category', 'company')
    ordering = ('-created_at',)


@admin.register(ModelFollow)
class ModelFollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'model', 'created_at')
    search_fields = ('user__username', 'model__name')
    ordering = ('-created_at',)
