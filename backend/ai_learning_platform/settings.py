"""
Django settings for ai_learning_platform project.
"""

import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

# 生产环境严格配置
if not DEBUG:
    raw_hosts = os.getenv('ALLOWED_HOSTS', 'localhost')
    parsed_hosts = []
    for host in raw_hosts.split(','):
        host = host.strip()
        if not host:
            continue
        # Django 支持 .example.com 形式，不支持 *.example.com 形式。
        if host.startswith('*.'):
            host = f".{host[2:]}"
        parsed_hosts.append(host)

    # Railway 自动注入公开域名，确保当前实例域名始终可访问。
    railway_public_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN', '').strip()
    if railway_public_domain and railway_public_domain not in parsed_hosts:
        parsed_hosts.append(railway_public_domain)

    ALLOWED_HOSTS = parsed_hosts or ['localhost']
else:
    ALLOWED_HOSTS = ['*']  # 开发环境允许所有主机

# Application definition
INSTALLED_APPS = [
    'daphne',  # ASGI server for channels
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'channels',
    
    # Local apps
    'courses',
    'chat',
    'ai_service',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 静态文件服务（生产环境）
    'corsheaders.middleware.CorsMiddleware',  # CORS必须在CommonMiddleware之前
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ai_learning_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'ai_learning_platform.wsgi.application'
ASGI_APPLICATION = 'ai_learning_platform.asgi.application'

# Database - 支持 DATABASE_URL 环境变量（用于生产部署）
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # 开发环境默认使用 SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Redis配置 (用于Channels和Celery)
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
USE_REDIS_CHANNEL_LAYER = os.getenv('USE_REDIS_CHANNEL_LAYER', 'False') == 'True'

if USE_REDIS_CHANNEL_LAYER:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [(REDIS_HOST, REDIS_PORT)],
            },
        },
    }
else:
    # 开发环境默认使用内存层，避免本地未启动 Redis 导致 WebSocket 无法连接。
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# CORS配置
if DEBUG:
    # 开发环境允许本地前端
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:3002',
        'http://localhost:5173',
        'http://127.0.0.1:5173',
    ]
else:
    # 生产环境严格配置 - 从环境变量读取
    CORS_ALLOW_ALL_ORIGINS = False
    cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000')
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins.split(',')]

CORS_ALLOW_CREDENTIALS = True

# AI服务配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '') or os.getenv('GITHUB_TOKEN', '')
AI_MODEL_NAME = os.getenv('AI_MODEL_NAME', 'gpt-4o-mini')

# GitHub Models配置（免费使用AI模型）
USE_GITHUB_MODELS = os.getenv('USE_GITHUB_MODELS', 'False') == 'True'
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://models.inference.ai.azure.com')

# FAISS向量数据库路径
VECTOR_DB_PATH = BASE_DIR / 'vector_db'

# Celery配置
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# -----------------------------------------------
# 邮件配置（163邮箱 SMTP）
# 在 .env 文件中配置以下环境变量：
#   EMAIL_HOST_USER=your_account@163.com
#   EMAIL_HOST_PASSWORD=your_smtp_auth_code   # 163授权码，非登录密码
# -----------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Quiz提醒邮件：DDL多少小时前发送提醒（默认24小时）
QUIZ_REMINDER_HOURS_BEFORE = int(os.getenv('QUIZ_REMINDER_HOURS_BEFORE', 24))

# 前端URL（用于邮件中的答题链接）
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
