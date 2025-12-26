@echo off
:: 微信问卷系统 - 启动生产环境脚本

echo 正在启动生产环境...
echo =====================================
echo 配置：
echo   DJANGO_SETTINGS_MODULE=wechat_survey.production_settings
echo   ENV_FILE=.env.production
echo   环境：生产环境
echo =====================================

:: 设置环境变量
set DJANGO_SETTINGS_MODULE=wechat_survey.settings
set ENV_FILE=.env.production

:: 启动生产服务器
:: 注意：在Windows上，uWSGI安装有兼容性问题
:: 生产环境建议使用Linux系统，然后使用uwsgi.ini配置文件
:: Windows上仅用于测试

echo 启动Django开发服务器（生产配置）...
echo 按 Ctrl+C 停止服务器
echo =====================================
echo 生产环境建议：
echo 1. 使用Linux系统部署
echo 2. 安装uWSGI：pip install uwsgi
echo 3. 使用配置文件启动：uwsgi --ini uwsgi.ini
echo 4. 配合Nginx使用（推荐）
echo =====================================
python manage.py runserver
