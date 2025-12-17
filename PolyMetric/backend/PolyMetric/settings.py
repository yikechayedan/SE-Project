import os
from pathlib import Path
from datetime import timedelta

# -----------------------------
# 基础路径配置
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


LLM_API_KEY = "sk-lvu1gprkETFqF587yTOFjg"   
LLM_BASE_URL = "https://llmapi.paratera.com/v1/"

# 媒体文件配置（上传的数据集文件存储路径）
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

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

    #数据集模块
    "apps.datasets",
    "django_filters",  # 筛选插件

    #评测任务模块
    "apps.tasks",

    #数据集模块
    "apps.models",

    # 系统动态模块
    "apps.system.apps.SystemConfig",
    
    # 模型排名模块
    "apps.rankings.apps.RankingsConfig",

    # 项目应用
    'apps.users',
]


# -----------------------------
# 中间件配置
# -----------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
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
# 模板配置
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


# -----------------------------
# 数据库配置
# -----------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'polymetric',
        'USER': 'postgres',
        'PASSWORD': 'yhblsqt',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}




# -----------------------------
# 密码校验
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# -----------------------------
# 国际化
# -----------------------------
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True


# -----------------------------
# 静态文件 & 媒体文件
# -----------------------------
STATIC_URL = 'static/'
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# -----------------------------
# 自定义用户模型
# -----------------------------
AUTH_USER_MODEL = 'users.User'


# -----------------------------
# 跨域配置
# -----------------------------
CORS_ALLOW_ALL_ORIGINS = True


# -----------------------------
# DRF 配置
# -----------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}


# -----------------------------
# JWT 配置
# -----------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}


# -----------------------------
# CORS 配置（允许跨域）
# -----------------------------
CORS_ALLOW_ALL_ORIGINS = True


# -----------------------------
# 默认主键类型
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# =======================
#  qq 邮箱 SMTP 配置
# =======================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = "1605014812@qq.com"
EMAIL_HOST_PASSWORD = "bzidtqejzaxygifh"   # 授权码
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# =======================
#  163 邮箱 SMTP 配置
# =======================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True

EMAIL_HOST_USER = '15777303630@163.com'
EMAIL_HOST_PASSWORD = 'TMjmTBPDLNqVjfb2'  # 授权码
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ============================
# Celery 配置
# ============================
CELERY_BROKER_URL = f"redis://:{os.getenv('REDIS_PASSWORD', 'redis_pass')}@{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/0"
CELERY_RESULT_BACKEND = f"redis://:{os.getenv('REDIS_PASSWORD', 'redis_pass')}@{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/0"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Static files collection directory
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
