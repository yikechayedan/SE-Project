"""
测试环境配置
基于主配置文件，但使用SQLite数据库
"""
from .settings import *

# 修改数据库配置为SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # 使用内存数据库
    }
}

# 禁用迁移以提高测试速度
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# 禁用密码验证器以提高测试速度
AUTH_PASSWORD_VALIDATORS = []

# 禁用邮件发送
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 禁用Celery
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True