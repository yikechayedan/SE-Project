import os
from pathlib import Path
from datetime import timedelta

# -----------------------------
# 基础路径配置
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# 安全配置
# -----------------------------
SECRET_KEY = 'django-insecure-1234567890-change-this-in-production'
DEBUG = True

ALLOWED_HOSTS = ["*"]   

# -----------------------------
# 已安装应用
# -----------------------------
INSTALLED_APPS = [
    # Django 内置功能
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 第三方库
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',


    # 项目应用
    'apps.users',
]


# -----------------------------
# 中间件配置
# -----------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 允许跨域
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# -----------------------------
# URL 配置入口
# -----------------------------
ROOT_URLCONF = 'PolyMetric.urls'


# -----------------------------
# 模板配置（后台管理等使用）
# -----------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
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

WSGI_APPLICATION = 'PolyMetric.wsgi.application'
ASGI_APPLICATION = 'PolyMetric.asgi.application'


# -----------------------------
# 数据库配置（可以切换 MySQL）
# -----------------------------
# 默认 SQLite，便于快速启动
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',      # 本地开发使用
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

"""
# 改成 MySQL，取消注释
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'polymetric',
        'USER': 'root',
        'PASSWORD': 'yourpassword',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
"""


# -----------------------------
# 密码验证
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]


# -----------------------------
# 国际化设置
# -----------------------------
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True


# -----------------------------
# 静态文件 & 媒体文件
# -----------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# -----------------------------
# 自定义用户模型（非常关键）
# -----------------------------
AUTH_USER_MODEL = "users.User"


# -----------------------------
# REST_FRAMEWORK 配置（启用 JWT）
# -----------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}


# -----------------------------
# JWT 配置
# -----------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# -----------------------------
# CORS 配置（允许跨域）
# -----------------------------
CORS_ALLOW_ALL_ORIGINS = True


# -----------------------------
# 默认主键类型
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
