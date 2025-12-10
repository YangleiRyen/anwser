#!/bin/bash

# 微信问卷系统部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}微信问卷系统部署脚本${NC}"
echo -e "${BLUE}======================================${NC}"

# 检查Docker和Docker Compose是否安装
check_dependencies() {
    echo -e "${YELLOW}检查依赖...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker未安装，请先安装Docker。${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Docker Compose未安装，请先安装Docker Compose。${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}依赖检查通过！${NC}"
}

# 构建并启动容器
deploy() {
    echo -e "${YELLOW}开始部署...${NC}"
    
    # 构建镜像
    echo -e "${BLUE}构建Docker镜像...${NC}"
    docker-compose build
    
    # 启动容器
    echo -e "${BLUE}启动Docker容器...${NC}"
    docker-compose up -d
    
    echo -e "${GREEN}部署完成！${NC}"
    echo -e "${GREEN}应用访问地址: http://localhost:8000${NC}"
    echo -e "${GREEN}Nginx访问地址: http://localhost${NC}"
}

# 停止并移除容器
stop() {
    echo -e "${YELLOW}停止容器...${NC}"
    docker-compose down
    echo -e "${GREEN}容器已停止！${NC}"
}

# 查看日志
logs() {
    echo -e "${YELLOW}查看应用日志...${NC}"
    docker-compose logs -f web
}

# 数据库迁移
db_migrate() {
    echo -e "${YELLOW}执行数据库迁移...${NC}"
    docker-compose run --rm web python manage.py migrate
    echo -e "${GREEN}数据库迁移完成！${NC}"
}

# 创建超级用户
create_superuser() {
    echo -e "${YELLOW}创建超级用户...${NC}"
    docker-compose run --rm web python manage.py createsuperuser
    echo -e "${GREEN}超级用户创建完成！${NC}"
}

# 收集静态文件
collectstatic() {
    echo -e "${YELLOW}收集静态文件...${NC}"
    docker-compose run --rm web python manage.py collectstatic --noinput
    echo -e "${GREEN}静态文件收集完成！${NC}"
}

# 帮助信息
show_help() {
    echo -e "${BLUE}使用方法:${NC} $0 [选项]"
    echo -e "${BLUE}选项:${NC}"
    echo -e "  ${GREEN}deploy${NC}     - 构建并启动容器"
    echo -e "  ${GREEN}stop${NC}       - 停止并移除容器"
    echo -e "  ${GREEN}logs${NC}       - 查看应用日志"
    echo -e "  ${GREEN}migrate${NC}    - 执行数据库迁移"
    echo -e "  ${GREEN}superuser${NC}  - 创建超级用户"
    echo -e "  ${GREEN}collectstatic${NC} - 收集静态文件"
    echo -e "  ${GREEN}help${NC}       - 显示帮助信息"
}

# 主函数
main() {
    check_dependencies
    
    case "$1" in
        deploy)
            deploy
            ;;
        stop)
            stop
            ;;
        logs)
            logs
            ;;
        migrate)
            db_migrate
            ;;
        superuser)
            create_superuser
            ;;
        collectstatic)
            collectstatic
            ;;
        help|
        *)
            show_help
            ;;
    esac
}

main "$@"
