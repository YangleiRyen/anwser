# 基于Python 3.11的官方镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建静态文件目录
RUN mkdir -p static

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 设置环境变量
ENV PYTHONUNBUFFERED 1

# 暴露端口
EXPOSE 8000

# 运行命令 - 使用uwsgi
CMD ["uwsgi", "--http-socket", "0.0.0.0:8000", "--module", "wechat_survey.wsgi:application", "--workers", "4", "--threads", "2", "--master", "--vacuum"]
