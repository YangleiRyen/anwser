# production_settings.py
import os
from .settings import *

# 生产环境核心配置
DEBUG = False

# 允许的主机配置
# 注意：生产环境中应设置为具体的域名，而不是通配符
# 示例：ALLOWED_HOSTS = ['example.com', 'www.example.com']
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# 使用DATABASE_URL环境变量配置数据库（MySQL）
import dj_database_url
# 默认使用MySQL数据库
DATABASE_URL = os.environ.get('DATABASE_URL', 'mysql://root:password@localhost:3306/wechat_survey')
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600),
}

# 安全设置
# 从环境变量读取SSL配置，方便切换HTTP/HTTPS
USE_SSL = os.environ.get('USE_SSL', 'False') == 'True'

if USE_SSL:
    # HTTPS配置
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1年
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    # HTTP配置（初始部署时使用）
    SECURE_SSL_REDIRECT = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'http')

# 额外的安全设置
SECURE_CONTENT_TYPE_NOSNIFF = True  # 防止浏览器猜测内容类型
SECURE_BROWSER_XSS_FILTER = True  # 启用浏览器XSS过滤器
X_FRAME_OPTIONS = 'DENY'  # 防止点击劫持

# 静态文件路径（与docker-compose.yml中的卷配置匹配）
STATIC_ROOT = '/app/static/'
MEDIA_ROOT = '/app/media/'

# 静态文件URL
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# 日志配置 - 增强生产环境日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'ERROR'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'survey': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# 生产环境特定配置
# 会话配置
SESSION_COOKIE_HTTPONLY = True  # 防止JavaScript访问会话cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # 限制跨站点请求

# CSRF配置
CSRF_COOKIE_HTTPONLY = True  # 防止JavaScript访问CSRF cookie
CSRF_COOKIE_SAMESITE = 'Lax'  # 限制跨站点请求

# 禁用调试工具栏和其他开发工具
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')
if 'debug_toolbar.middleware.DebugToolbarMiddleware' in MIDDLEWARE:
    MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

# 移除开发环境的中间件
if 'django.middleware.security.SecurityMiddleware' in MIDDLEWARE:
    # 确保安全中间件在首位
    middleware_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
    if middleware_index != 0:
        MIDDLEWARE.insert(0, MIDDLEWARE.pop(middleware_index))
