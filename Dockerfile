# 基于Python 3.11的官方镜像 - 使用slim版本减小镜像体积
FROM python:3.11-slim

# 设置工作目录为/app，后续命令都在此目录执行
WORKDIR /app

# 安装系统依赖
# gcc, g++等编译工具用于编译Python依赖包
# libpq-dev用于PostgreSQL数据库连接
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*  # 清理apt缓存，减小镜像体积

# 复制requirements.txt到工作目录
COPY requirements.txt .
# 安装Python依赖包，使用--no-cache-dir避免缓存依赖，减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目所有文件到工作目录
COPY . .

# 创建静态文件目录，用于存储收集的静态文件
RUN mkdir -p static

# 收集Django静态文件到STATIC_ROOT目录
RUN python manage.py collectstatic --noinput

# 设置环境变量，确保Python输出直接打印到控制台，便于日志查看
ENV PYTHONUNBUFFERED 1

# 暴露容器的8000端口，用于外部访问
EXPOSE 8000

# 容器启动命令 - 使用uwsgi作为WSGI服务器
# --http-socket: 使用HTTP socket模式，可直接处理HTTP请求
# --module: 指定Django应用的WSGI入口
# --workers: 设置4个工作进程
# --threads: 每个工作进程使用2个线程
# --master: 启用主进程模式
# --vacuum: 退出时清理临时文件
CMD ["uwsgi", "--http-socket", "0.0.0.0:8000", "--module", "wechat_survey.wsgi:application", "--workers", "4", "--threads", "2", "--master", "--vacuum"]