#!/bin/bash

# 微信问卷系统一键部署脚本
# 功能：自动构建和启动整个应用栈（web + db + nginx）
# 支持生产环境和开发环境部署

set -e  # 遇到错误立即退出

# 全局变量
ENVIRONMENT="development"

# 显示帮助信息
show_help() {
    echo "用法：$0 [选项] [命令]"
    echo ""
    echo "命令："
    echo "  deploy   构建并启动服务（默认）"
    echo "  stop     停止服务"
    echo "  logs     查看服务日志"
    echo "  restart  重启服务"
    echo ""
    echo "选项："
    echo "  -p, --prod  生产环境部署模式"
    echo "  -h, --help  显示帮助信息"
    echo ""
    echo "示例："
    echo "  开发环境部署：$0 deploy"
    echo "  生产环境部署：$0 --prod deploy"
    exit 0
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--prod)
                ENVIRONMENT="production"
                shift
                ;;
            -h|--help)
                show_help
                ;;
            *)
                COMMAND=$1
                shift
                ;;
        esac
    done
    
    # 设置默认命令
    COMMAND=${COMMAND:-"deploy"}
}

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
    # 检查Docker Compose（支持docker-compose和docker compose两种形式）
    if ! docker compose version &> /dev/null && ! docker-compose version &> /dev/null; then
        echo "错误：Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    echo "✓ Docker和Docker Compose已安装"
}

# 检查生产环境配置
check_production_config() {
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "检查生产环境配置..."
        
        # 检查.env文件是否存在
        if [ ! -f ".env" ]; then
            echo "错误：.env文件不存在，请先创建并配置.env文件"
            echo "提示：可以复制.env.example创建.env文件"
            exit 1
        fi
        
        # 检查SECRET_KEY是否已修改
        if grep -q "your-secret-key-here" .env; then
            echo "警告：SECRET_KEY仍使用默认值，这在生产环境中不安全！"
            echo "请修改.env文件中的SECRET_KEY为强随机字符串"
            read -p "是否继续部署？(y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
        
        # 检查DEBUG模式是否已关闭
        if grep -q "^DEBUG=True" .env; then
            echo "警告：DEBUG模式已开启，这在生产环境中不安全！"
            echo "请将.env文件中的DEBUG设置为False"
            read -p "是否继续部署？(y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
        
        echo "✓ 生产环境配置检查完成"
    fi
}

# 构建和启动服务
deploy() {
    echo "开始部署..."
    echo "部署环境：$ENVIRONMENT"
    
    # 检查生产环境配置
    check_production_config
    
    # 构建镜像并启动服务
    echo "构建镜像并启动服务..."
    
    # 生产环境专属配置
    if [ "$ENVIRONMENT" = "production" ]; then
        # 生产环境：使用生产环境配置，添加环境变量
        export DJANGO_SETTINGS_MODULE=wechat_survey.production_settings
        docker compose up -d --build
        
        # 收集静态文件
        echo "收集静态文件..."
        docker compose run --rm web python manage.py collectstatic --noinput
    else
        # 开发环境：默认配置
        docker compose up -d --build
    fi
    
    echo "等待服务启动..."
    sleep 5
    
    # 执行数据库迁移（确保数据库结构最新）
    echo "执行数据库迁移..."
    docker compose run --rm web python manage.py migrate
    
    # 显示服务状态
    echo "显示服务状态..."
    docker compose ps
    
    echo ""
    echo "====================================="
    echo "部署完成！"
    echo "====================================="
    echo "应用访问地址：http://localhost"
    echo "管理后台：http://localhost/admin"
    echo ""
    echo "常用命令："
    echo "  查看日志：docker compose logs -f"
    echo "  停止服务：docker compose down"
    echo "  重启服务：docker compose restart"
    echo "  创建超级用户：docker compose run --rm web python manage.py createsuperuser"
    echo ""
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "生产环境注意事项："
        echo "  1. 确保已修改SECRET_KEY为强随机字符串"
        echo "  2. 确保DEBUG=False"
        echo "  3. 考虑配置HTTPS"
        echo "  4. 定期备份数据库"
    fi
    echo "====================================="
}

# 停止服务
stop() {
    echo "停止服务..."
    docker compose down
    echo "服务已停止"
}

# 查看日志
logs() {
    echo "查看服务日志..."
    docker compose logs -f
}

# 主函数
main() {
    # 解析命令行参数
    parse_args "$@"
    
    check_dependencies
    
    # 根据命令执行不同功能
    case "$COMMAND" in
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
        "deploy")
            deploy
            ;;
        *)
            echo "未知命令：$COMMAND"
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"