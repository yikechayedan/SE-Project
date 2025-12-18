"""
测试环境设置文件
"""
import os
from pathlib import Path
from datetime import timedelta

# 继承主设置文件
try:
    from .settings import *
except ImportError:
    # 如果无法导入主设置，使用默认配置
    import os
    from pathlib import Path
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    DEBUG = True
    SECRET_KEY = 'django-test-secret-key-for-testing-only'
    
    # 使用SQLite数据库进行测试
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'test_db.sqlite3',
        }
    }
    
    # 测试时禁用密码验证
    AUTH_PASSWORD_VALIDATORS = []
    
    # 禁用邮件发送
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    
    # 简化CORS设置
    CORS_ALLOW_ALL_ORIGINS = True
    
    # 测试时不需要静态文件收集
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    
    # 禁用迁移警告
    SILENCE = True
    
    # 设置测试环境标记
    TESTING = True
    
    # 禁用CSRF保护（测试时）
    MIDDLEWARE = [
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
    
    # 简化JWT设置
    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
        'ROTATE_REFRESH_TOKENS': False,
        'BLACKLIST_AFTER_ROTATION': False,
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': SECRET_KEY,
    }
    
    # 禁用Celery（测试时不需要）
    CELERY_TASK_ALWAYS_EAGER = True
    
    # 添加其他必要的设置
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
        'rest_framework_simplejwt',
        'corsheaders',
        'django_filters',
        'apps.users',
        'apps.datasets',
        'apps.models',
        'apps.tasks',
        'apps.rankings',
        'apps.system',
    ]
    
    ROOT_URLCONF = 'PolyMetric.urls'
    
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': [],
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]
    
    LANGUAGE_CODE = 'en-us'
    TIME_ZONE = 'UTC'
    USE_I18N = True
    USE_TZ = True

# 覆盖测试相关设置
DEBUG = True
SECRET_KEY = 'django-test-secret-key-for-testing-only'

# 使用SQLite数据库进行测试
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# 测试时禁用密码验证
AUTH_PASSWORD_VALIDATORS = []

# 禁用邮件发送
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 简化CORS设置
CORS_ALLOW_ALL_ORIGINS = True

# 测试时不需要静态文件收集
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# 禁用迁移警告
SILENCE = True

# 设置测试环境标记
TESTING = True

# 禁用CSRF保护（测试时）
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 简化JWT设置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

# 禁用Celery（测试时不需要）
CELERY_TASK_ALWAYS_EAGER = True