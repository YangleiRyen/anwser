@echo off
:: 微信问卷系统 - 启动生产环境脚本

echo 正在启动生产环境...
echo =====================================
echo 配置：
echo   DJANGO_SETTINGS_MODULE=wechat_survey.production_settings
echo   ENV_FILE=.env.production
echo =====================================

:: 设置环境变量
set DJANGO_SETTINGS_MODULE=wechat_survey.production_settings
set ENV_FILE=.env.production

:: 检查gunicorn是否安装
pip list | findstr gunicorn >nul
if errorlevel 1 (
    echo 正在安装gunicorn...
    pip install gunicorn
)

:: 启动生产服务器
echo 启动gunicorn服务器...
gunicorn wechat_survey.wsgi:application --bind 0.0.0.0:8000 --workers 4
