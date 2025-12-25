#!/bin/bash
# 微信问卷系统 - 开发环境启动脚本（Linux版本）

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}正在启动开发环境...${NC}"
echo -e "${GREEN}=====================================${NC}"
echo -e "${YELLOW}配置：${NC}"
echo -e "  DJANGO_SETTINGS_MODULE=wechat_survey.settings"
echo -e "  ENV_FILE=.env"
echo -e "${GREEN}=====================================${NC}"

# 设置环境变量
export DJANGO_SETTINGS_MODULE=wechat_survey.settings
export ENV_FILE=.env

# 启动开发服务器
echo -e "${GREEN}启动Django开发服务器...${NC}"
echo -e "${YELLOW}访问地址：http://127.0.0.1:8000${NC}"
echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}"
echo -e "${GREEN}=====================================${NC}"
echo -e "${YELLOW}注意：这是开发服务器，请勿在生产环境使用！${NC}"
echo -e "${GREEN}=====================================${NC}"

python manage.py runserver
