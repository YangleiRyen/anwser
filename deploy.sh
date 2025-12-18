#!/bin/bash

# 微信问卷系统一键部署脚本
# 功能：自动构建和启动整个应用栈（web + db + nginx）

set -e  # 遇到错误立即退出

echo "====================================="
echo "微信问卷系统一键部署脚本"
echo "====================================="

# 检查Docker和Docker Compose是否安装
check_dependencies() {
    echo "检查Docker和Docker Compose..."
    if ! command -v docker &> /dev/null; then
        echo "错误：Docker未安装，请先安装Docker"
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null; then
        echo "错误：Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    echo "✓ Docker和Docker Compose已安装"
}

# 构建和启动服务
deploy() {
    echo "开始部署..."
    
    # 构建镜像并启动服务
    echo "构建镜像并启动服务..."
    docker-compose up -d --build
    
    echo "等待服务启动..."
    sleep 5
    
    # 显示服务状态
    echo "显示服务状态..."
    docker-compose ps
    
    echo ""
    echo "====================================="
    echo "部署完成！"
    echo "====================================="
    echo "应用访问地址：http://localhost"
    echo "管理后台：http://localhost/admin"
    echo ""
    echo "常用命令："
    echo "  查看日志：docker-compose logs -f"
    echo "  停止服务：docker-compose down"
    echo "  重启服务：docker-compose restart"
    echo "  创建超级用户：docker-compose run --rm web python manage.py createsuperuser"
    echo "====================================="
}

# 停止服务
stop() {
    echo "停止服务..."
    docker-compose down
    echo "服务已停止"
}

# 查看日志
logs() {
    echo "查看服务日志..."
    docker-compose logs -f
}

# 主函数
main() {
    check_dependencies
    
    # 根据参数执行不同功能
    case "$1" in
        "stop")
            stop
            ;;
        "logs")
            logs
            ;;
        "restart")
            stop
            deploy
            ;;
        "deploy" | "")
            deploy
            ;;
        *)
            echo "用法：$0 [deploy|stop|logs|restart]"
            echo "  deploy：构建并启动服务（默认）"
            echo "  stop：停止服务"
            echo "  logs：查看服务日志"
            echo "  restart：重启服务"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"