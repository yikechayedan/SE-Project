from django.apps import AppConfig


class SystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.system'
    verbose_name = '系统动态'

    def ready(self):
        import apps.system.signals