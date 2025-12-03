# apps/models/apps.py
from django.apps import AppConfig

class ModelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.models'
    verbose_name = '大模型管理'