#!/bin/bash
# 微信问卷系统 - 生产环境启动脚本（Linux版本）
# 使用uWSGI服务器

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}正在启动生产环境...${NC}"
echo -e "${GREEN}=====================================${NC}"
echo -e "${YELLOW}配置：${NC}"
echo -e "  使用uWSGI服务器"
echo -e "  配置文件：uwsgi.ini"
echo -e "  环境：生产环境"
echo -e "${GREEN}=====================================${NC}"

# 检查uwsgi是否安装
if ! command -v uwsgi &> /dev/null
then
    echo -e "${YELLOW}正在安装uwsgi...${NC}"
    pip install uwsgi
fi

# 创建reload.txt文件（用于热重载）
touch reload.txt

# 设置环境变量
export DJANGO_SETTINGS_MODULE=wechat_survey.production_settings
export ENV_FILE=.env.production

# 启动生产服务器
echo -e "${GREEN}启动uWSGI服务器...${NC}"
echo -e "${YELLOW}日志文件：uwsgi.log${NC}"
echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}"
echo -e "${GREEN}=====================================${NC}"

# 使用uwsgi.ini配置文件启动
uwsgi --ini uwsgi.ini
