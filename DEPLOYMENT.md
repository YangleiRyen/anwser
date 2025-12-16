py# 微信问卷系统部署文档

## 项目介绍
微信问卷系统是基于Django开发的问卷调查系统，支持创建问卷、生成二维码、收集反馈等功能。本文档将介绍Docker部署方案（nginx+uwsgi），包括单应用部署和多应用部署方案。

## Docker部署方案

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

#### 4. 创建共享网络（多应用部署必需）

**创建共享网络：**
```bash
docker network create wechat_survey_network
```

**创建共享卷：**
```bash
docker volume create static_volume
docker volume create media_volume
docker volume create postgres_data
```

#### 5. 部署微信问卷系统

**启动微信问卷系统：**
```bash
docker-compose up -d
```

#### 6. 部署独立Nginx服务

**切换到独立Nginx目录：**
```bash
cd standalone_nginx
```

**启动Nginx服务：**
```bash
docker-compose up -d
```

### 访问应用
- 应用直接访问地址：http://localhost:8000
- 通过Nginx访问：http://localhost

### 常用命令

**启动服务：**
```bash
# 启动微信问卷系统
docker-compose up -d

# 启动Nginx服务
cd standalone_nginx && docker-compose up -d
```

**停止服务：**
```bash
# 停止微信问卷系统
docker-compose down

# 停止Nginx服务
cd standalone_nginx && docker-compose down
```

**查看日志：**
```bash
# 查看微信问卷系统日志
docker-compose logs -f web

# 查看Nginx日志
cd standalone_nginx && docker-compose logs -f nginx
```

**执行数据库迁移：**
```bash
# 执行数据库迁移
docker-compose run --rm web python manage.py migrate

# 创建超级用户
docker-compose run --rm web python manage.py createsuperuser

# 收集静态文件
docker-compose run --rm web python manage.py collectstatic --noinput
```

## 多应用部署指导

### 1. 多应用部署架构

我们采用了**独立Nginx服务**的架构，允许在同一服务器上部署多个应用，共享同一个Nginx服务。

**架构图：**
```
+---------------------------------------+
|           独立Nginx服务                |
|  (监听80/443端口，反向代理到多个应用)  |
+---------------------------------------+
|  |                |                |  |
|  v                v                v  |
| +---------+    +---------+    +---------+ |
| | 应用1   |    | 应用2   |    | 应用3   | |
| | (端口8000)|    | (端口8001)|    | (端口8002)| |
| +---------+    +---------+    +---------+ |
|       |                |                |  |
|       v                v                v  |
| +---------+    +---------+    +---------+ |
| | 数据库1 |    | 数据库2 |    | 数据库3 | |
| +---------+    +---------+    +---------+ |
+---------------------------------------+
```

### 2. 部署新应用

#### 2.1 准备新应用

1. **确保新应用使用与微信问卷系统相同的网络和卷**
2. **修改新应用的docker-compose.yml，添加网络配置**

```yaml
# 新应用docker-compose.yml示例
networks:
  wechat_survey_network:
    external: true

services:
  web:
    # ...
    networks:
      - wechat_survey_network
    # ...
```

#### 2.2 添加Nginx配置

1. **在standalone_nginx/conf.d目录下创建新应用的配置文件**

```bash
cd standalone_nginx/conf.d
touch new_app.conf
```

2. **编辑新应用的Nginx配置文件**

```nginx
# new_app.conf - 新应用配置
server {
    listen 80;
    server_name newapp.localhost;  # 或使用域名 newapp.your-domain.com

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

    # 应用代理
    location / {
        proxy_pass http://new_app_web:8001;  # 新应用的容器名和端口
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **重启Nginx服务**

```bash
cd standalone_nginx
docker-compose restart nginx
```

### 3. 多应用管理

#### 3.1 查看所有应用状态

```bash
# 查看微信问卷系统状态
docker-compose ps

# 查看Nginx状态
cd standalone_nginx && docker-compose ps

# 查看新应用状态
cd /path/to/new_app && docker-compose ps
```

#### 3.2 日志管理

```bash
# 查看所有应用日志
docker-compose logs -f
cd standalone_nginx && docker-compose logs -f
cd /path/to/new_app && docker-compose logs -f
```

#### 3.3 升级应用

```bash
# 升级微信问卷系统
git pull
docker-compose build
docker-compose up -d

# 升级Nginx配置（如果有修改）
cd standalone_nginx
docker-compose restart nginx
```

### 4. 多应用部署最佳实践

1. **使用不同的端口和容器名**：确保每个应用使用唯一的端口和容器名
2. **共享网络**：所有应用使用同一个Docker网络，便于容器间通信
3. **独立数据库**：每个应用使用独立的数据库，避免数据冲突
4. **统一Nginx配置**：使用独立的Nginx服务管理所有应用的反向代理
5. **使用域名或子域名**：为每个应用配置独立的域名或子域名
6. **SSL证书管理**：使用Let's Encrypt等工具为所有应用配置HTTPS

## 常见问题和解决方案

### 404错误
- 检查nginx配置文件中的静态文件路径是否正确
- 确保执行了`collectstatic`命令
- 检查uwsgi服务是否正常运行

### 502错误
- 检查uwsgi服务是否正在运行
- 检查nginx配置文件中的uwsgi地址是否正确
- 查看uwsgi日志和nginx错误日志

### 数据库连接错误
- 检查数据库配置是否正确
- 确保数据库服务正在运行
- 检查数据库用户权限

### Nginx无法连接到应用
- 确保所有应用都在同一个Docker网络中
- 检查容器名和端口是否正确
- 查看Nginx错误日志

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

部署文档更新时间：2025-12-12