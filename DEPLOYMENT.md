# 微信问卷系统部署文档

## 项目介绍
微信问卷系统是基于Django开发的问卷调查系统，支持创建问卷、生成二维码、收集反馈等功能。本文档将介绍Docker部署方案（nginx+uwsgi）。

## Docker部署方案（nginx+uwsgi）

### 系统要求
- Linux系统
- Docker 19.03+
- Docker Compose 1.27+

### 安装步骤

#### 1. 安装Docker和Docker Compose

**Ubuntu/Debian系统：**
```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo apt install -y docker-compose
```

**CentOS/RHEL系统：**
```bash
# 安装Docker
yum install -y yum-utils
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
yum install -y docker-compose
```

**启动Docker服务：**
```bash
sudo systemctl enable docker
sudo systemctl start docker
```

#### 2. 克隆项目代码
```bash
git clone https://github.com/your-repo/wechat_survey.git
cd wechat_survey
```

#### 3. 配置环境变量

编辑`docker-compose.yml`文件，修改以下环境变量：
```yaml
environment:
  - DEBUG=False
  - SECRET_KEY=your-secret-key-here  # 请替换为实际的密钥
  - DATABASE_URL=postgres://postgres:postgres@db:5432/wechat_survey
  - BASE_URL=http://localhost:8000
```

#### 4. 构建并启动容器

**使用部署脚本（推荐）：**
```bash
chmod +x deploy.sh
./deploy.sh deploy
```

**手动构建和启动：**
```bash
# 构建镜像
docker-compose build

# 启动容器
docker-compose up -d
```

### 访问应用
- 应用直接访问地址：http://localhost:8000
- Nginx反向代理地址：http://localhost

### 常用命令

**启动服务：**
```bash
./deploy.sh deploy  # 使用脚本
# 或
docker-compose up -d  # 手动启动
```

**停止服务：**
```bash
./deploy.sh stop  # 使用脚本
# 或
docker-compose down  # 手动停止
```

**查看日志：**
```bash
./deploy.sh logs  # 使用脚本
# 或
docker-compose logs -f web  # 手动查看
```

**执行数据库迁移：**
```bash
./deploy.sh migrate  # 使用脚本
# 或
docker-compose run --rm web python manage.py migrate  # 手动执行
```

**创建超级用户：**
```bash
./deploy.sh superuser  # 使用脚本
# 或
docker-compose run --rm web python manage.py createsuperuser  # 手动创建
```

**收集静态文件：**
```bash
./deploy.sh collectstatic  # 使用脚本
# 或
docker-compose run --rm web python manage.py collectstatic --noinput  # 手动收集
```

## 常见问题和解决方案

### 404错误
- 检查nginx配置文件中的静态文件路径是否正确
- 确保`collectstatic`命令已执行
- 检查uwsgi服务是否正常运行

### 502错误
- 检查uwsgi服务是否正在运行
- 检查nginx配置文件中的uwsgi地址是否正确
- 查看uwsgi日志和nginx错误日志

### 数据库连接错误
- 检查数据库配置是否正确
- 确保数据库服务正在运行
- 检查数据库用户权限

## 注意事项

1. **安全性**：
   - 在生产环境中，务必修改`SECRET_KEY`为强随机字符串
   - 设置`DEBUG=False`
   - 配置合适的`ALLOWED_HOSTS`
   - 考虑使用HTTPS

2. **性能优化**：
   - 根据服务器配置调整uwsgi的`workers`和`threads`参数
   - 启用nginx的gzip压缩
   - 配置适当的缓存策略

3. **数据备份**：
   - 定期备份数据库
   - 备份媒体文件和静态文件

4. **日志管理**：
   - 定期清理日志文件
   - 考虑使用日志管理工具（如ELK Stack）

5. **版本更新**：
   - 在更新代码前备份数据
   - 更新后执行数据库迁移
   - 重启服务

## 联系方式

如有问题或建议，请联系项目维护者：
- 邮箱：your-email@example.com
- GitHub：https://github.com/your-repo/wechat_survey

---

部署文档更新时间：2025-12-11





# 微信问卷系统部署文件及部署流程详解

## 1. 涉及部署的核心文件

项目中涉及部署的文件主要有以下几个：

| 文件名 | 作用 | 核心内容 |
|--------|------|----------|
| `Dockerfile` | Docker镜像构建文件 | 定义镜像构建步骤、依赖安装、文件复制等 |
| `docker-compose.yml` | Docker Compose配置 | 定义多容器部署方案，包括web、db、nginx服务 |
| `nginx/nginx.conf` | Nginx配置文件 | 配置静态文件服务、反向代理、媒体文件服务 |
| `deploy.sh` | 部署脚本 | 简化Docker容器管理，提供deploy、stop、logs等命令 |
| `DEPLOYMENT.md` | 部署文档 | 详细说明部署步骤、配置和常用命令 |
| `requirements.txt` | Python依赖列表 | 列出项目所需的所有Python依赖包 |
| `wechat_survey/wsgi.py` | WSGI入口文件 | uwsgi加载Django应用的入口点 |

## 2. 各部署文件详解

### 2.1 Dockerfile

**核心功能**：定义Docker镜像的构建步骤

**关键配置**：
```dockerfile
# 基于Python 3.11镜像
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc-dev \
    libpq-dev

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 运行命令 - 使用uwsgi启动Django应用
CMD ["uwsgi", "--http-socket", "0.0.0.0:8000", "--module", "wechat_survey.wsgi:application", "--workers", "4", "--threads", "2", "--master", "--vacuum"]
```

### 2.2 docker-compose.yml

**核心功能**：定义多容器部署方案

**关键配置**：
```yaml
services:
  # Django应用服务（使用uwsgi）
  web:
    build: .
    ports:
      - "8000:8000"
    command: >
      sh -c "python manage.py migrate && uwsgi --http-socket 0.0.0.0:8000 --module wechat_survey.wsgi:application --workers 4 --threads 2 --master --vacuum"
  
  # PostgreSQL数据库服务
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=wechat_survey
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
  
  # Nginx反向代理服务
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/static
      - media_volume:/app/media
```

### 2.3 nginx/nginx.conf

**核心功能**：配置Nginx反向代理和静态文件服务

**关键配置**：
```nginx
# 静态文件服务
location /static/ {
    alias /app/static/;
    expires 30d;
    add_header Cache-Control public;
}

# 媒体文件服务
location /media/ {
    alias /app/media/;
}

# Django应用代理
location / {
    proxy_pass http://web:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 2.4 deploy.sh

**核心功能**：简化Docker容器的管理和操作

**主要命令**：
- `./deploy.sh deploy` - 构建并启动容器
- `./deploy.sh stop` - 停止并移除容器
- `./deploy.sh logs` - 查看应用日志
- `./deploy.sh migrate` - 执行数据库迁移
- `./deploy.sh superuser` - 创建超级用户
- `./deploy.sh collectstatic` - 收集静态文件

### 2.5 requirements.txt

**核心功能**：列出项目所需的所有Python依赖包

**关键依赖**：
```
Django==5.2
djangorestframework==3.16.1
uwsgi==2.0.25
qrcode==8.2
requests==2.32.5
```

## 3. 部署流程详解

### 3.1 环境准备

1. **安装Docker和Docker Compose**：
   - Ubuntu/Debian: `sudo apt install docker docker-compose`
   - CentOS/RHEL: `sudo yum install docker docker-compose`
   - 其他系统：参考[Docker官方文档](https://docs.docker.com/get-docker/)

2. **启动Docker服务**：
   ```bash
   sudo systemctl enable docker
   sudo systemctl start docker
   ```

### 3.2 部署步骤

#### 3.2.1 克隆项目代码
```bash
git clone https://github.com/your-repo/wechat_survey.git
cd wechat_survey
```

#### 3.2.2 配置环境变量

编辑`docker-compose.yml`文件，修改以下关键环境变量：
```yaml
environment:
  - DEBUG=False  # 生产环境设置为False
  - SECRET_KEY=your-secret-key-here  # 生成一个强随机字符串
  - DATABASE_URL=postgres://postgres:postgres@db:5432/wechat_survey
  - BASE_URL=http://your-domain.com  # 替换为实际域名
```

#### 3.2.3 构建并启动容器

**使用部署脚本（推荐）**：
```bash
chmod +x deploy.sh
./deploy.sh deploy
```

**手动部署**：
```bash
# 构建镜像
docker-compose build

# 启动容器
docker-compose up -d
```

#### 3.2.4 验证部署

1. **查看容器状态**：
   ```bash
   docker-compose ps
   ```

2. **访问应用**：
   - 直接访问Django应用：http://localhost:8000
   - 通过Nginx访问：http://localhost
   - 管理后台：http://localhost:8000/admin 或 http://localhost/admin

3. **查看日志**：
   ```bash
   ./deploy.sh logs
   # 或
   docker-compose logs -f web
   ```

### 3.3 常用部署管理命令

| 命令 | 作用 | 说明 |
|------|------|------|
| `./deploy.sh deploy` | 部署应用 | 构建镜像并启动容器 |
| `./deploy.sh stop` | 停止应用 | 停止并移除容器 |
| `./deploy.sh logs` | 查看日志 | 查看应用日志 |
| `./deploy.sh migrate` | 数据库迁移 | 执行Django数据库迁移 |
| `./deploy.sh superuser` | 创建超级用户 | 创建Django管理后台超级用户 |
| `./deploy.sh collectstatic` | 收集静态文件 | 收集Django静态文件 |
| `docker-compose down` | 停止并移除容器 | 与`./deploy.sh stop`功能相同 |
| `docker-compose up -d` | 启动容器 | 与`./deploy.sh deploy`中的启动部分相同 |
| `docker-compose build` | 构建镜像 | 与`./deploy.sh deploy`中的构建部分相同 |

## 4. 部署架构说明

### 4.1 容器架构

```
+---------------------+      +---------------------+      +---------------------+
|    Nginx容器        |      |    Django容器       |      |    PostgreSQL容器    |
|  (wechat_survey_nginx)|      |  (wechat_survey_web)|      |  (wechat_survey_db) |
+---------------------+      +---------------------+      +---------------------+
|  - 监听80/443端口   |      |  - 监听8000端口     |      |  - 监听5432端口     |
|  - 静态文件服务     |      |  - 运行uwsgi        |      |  - 存储数据         |
|  - 反向代理到web容器|      |  - 处理Django请求   |      |                     |
+---------------------+      +---------------------+      +---------------------+
```

### 4.2 请求流程

1. **用户请求** → Nginx容器（端口80/443）
2. **静态资源请求** → Nginx直接返回静态文件（/static/和/media/）
3. **动态请求** → Nginx反向代理到Django容器（http://web:8000）
4. **Django处理** → uwsgi运行Django应用，处理请求
5. **数据库操作** → Django容器连接PostgreSQL容器，执行数据库操作
6. **响应返回** → 从Django容器 → Nginx容器 → 用户

## 5. 部署注意事项

1. **安全性**：
   - 生产环境中设置`DEBUG=False`
   - 使用强随机字符串作为`SECRET_KEY`
   - 配置合适的`ALLOWED_HOSTS`
   - 考虑使用HTTPS（配置SSL证书）

2. **性能优化**：
   - 根据服务器配置调整uwsgi的`workers`和`threads`参数
   - 启用Nginx的gzip压缩
   - 配置合适的静态文件缓存策略

3. **数据备份**：
   - 定期备份PostgreSQL数据库
   - 备份媒体文件和静态文件

4. **日志管理**：
   - 定期清理日志文件
   - 考虑使用日志管理工具（如ELK Stack）

## 6. 常见部署问题及解决方案

### 6.1 容器启动失败

**解决方案**：
1. 查看容器日志：`docker-compose logs web`
2. 检查环境变量配置是否正确
3. 检查端口是否被占用

### 6.2 静态文件无法访问

**解决方案**：
1. 确保执行了`collectstatic`命令：`./deploy.sh collectstatic`
2. 检查Nginx配置中的静态文件路径是否正确
3. 检查静态文件目录权限

### 6.3 数据库连接失败

**解决方案**：
1. 检查数据库服务是否正常运行：`docker-compose ps db`
2. 检查`DATABASE_URL`配置是否正确
3. 检查数据库用户权限

## 7. 学习建议

1. **先理解Docker基础**：学习Docker和Docker Compose的基本概念和命令
2. **阅读部署文档**：详细阅读`DEPLOYMENT.md`文件，了解部署细节
3. **实践部署流程**：在本地环境或测试服务器上实际部署一次
4. **修改配置参数**：尝试修改uwsgi参数、Nginx配置等，观察效果
5. **学习日志分析**：学会查看和分析Docker容器日志，排查问题
6. **了解CI/CD**：考虑学习CI/CD流程，实现自动化部署

通过学习这些部署文件和流程，您可以掌握Django项目的Docker部署方法，为后续部署其他Django项目打下基础。