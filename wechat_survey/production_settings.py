# production_settings.py
import os
from .settings import *

DEBUG = False

# 允许所有主机访问，或根据实际情况设置具体域名
ALLOWED_HOSTS = ['*']

# 使用DATABASE_URL环境变量配置数据库（与docker-compose.yml匹配）
import dj_database_url
database_url = os.environ.get('DATABASE_URL', 'postgres://postgres:postgres@db:5432/wechat_survey')
DATABASES = {
    'default': dj_database_url.parse(database_url, conn_max_age=600),
}

# 安全设置 - 初始部署使用http，后续可改为https
SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'http')

# 静态文件路径（与docker-compose.yml中的卷配置匹配）
STATIC_ROOT = '/app/static/'
MEDIA_ROOT = '/app/media/'

# 静态文件URL
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# 日志 - 使用相对路径或确保容器内目录存在
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'ERROR'),
        },
        'survey': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}
