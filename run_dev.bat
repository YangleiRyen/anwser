@echo off
:: 微信问卷系统 - 启动开发环境脚本

echo 正在启动开发环境...
echo =====================================
echo 配置：
echo   DJANGO_SETTINGS_MODULE=wechat_survey.settings
echo   ENV_FILE=.env
echo =====================================

:: 设置环境变量
set DJANGO_SETTINGS_MODULE=wechat_survey.settings
set ENV_FILE=.env

:: 启动开发服务器
python manage.py runserver
