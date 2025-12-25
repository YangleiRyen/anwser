# production_settings.py
# 生产环境配置文件
# 继承自settings.py，仅覆盖生产环境特定配置

import os
from .settings import *

# ====================================
# 生产环境核心配置
# ====================================

# 生产环境必须关闭DEBUG模式
DEBUG = False

# 生产环境必须指定具体的域名，不能使用通配符
# 多个域名用列表形式配置
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['your-domain.com', 'www.your-domain.com'])

# 生产环境密钥，必须使用强随机字符串
SECRET_KEY = env('SECRET_KEY', default='your-production-secret-key-change-this-to-random-string')

# ====================================
# 数据库配置（MySQL）
# ====================================

# 生产环境使用MySQL数据库
# 使用django-environ的db()方法从环境变量获取数据库配置
# 优先使用DATABASE_URL，其次使用DB_*环境变量
DATABASES = {
    'default': env.db(
        default='mysql://wechat_survey_user:your-strong-db-password@localhost:3306/wechat_survey',
        engine='django.db.backends.mysql',
        **{
            'OPTIONS': {
                'charset': 'utf8mb4',
                'sql_mode': 'STRICT_TRANS_TABLES',
            }
        }
    )
}

# ====================================
# 安全配置
# ====================================

# 生产环境SSL配置
# 初始部署时可设置为False，后续配置SSL后改为True
USE_SSL = env('USE_SSL', default=False)

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

# ====================================
# 静态文件和媒体文件配置
# ====================================

# 静态文件根目录 - 使用相对路径
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 媒体文件根目录 - 使用相对路径
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 静态文件URL
STATIC_URL = '/static/'

# 媒体文件URL
MEDIA_URL = '/media/'

# ====================================
# 日志配置
# ====================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
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
            'level': 'ERROR',  # 生产环境只记录错误日志
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',  # 请求相关日志记录到WARNING级别
            'propagate': False,
        },
        'survey': {
            'handlers': ['console'],
            'level': 'INFO',  # 业务日志记录到INFO级别
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
