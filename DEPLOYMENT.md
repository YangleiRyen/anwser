# 微信问卷系统部署文档

## 项目介绍
微信问卷系统是基于Django开发的问卷调查系统，支持创建问卷、生成二维码、收集反馈等功能。本文档将介绍传统部署方案，采用单应用部署方式。

## 系统要求
- Linux系统（如Ubuntu/Debian、CentOS/RHEL）
- Python 3.9+
- MySQL 8.0+

## 安装步骤

### 1. 安装依赖

#### 1.1 安装系统依赖

**Ubuntu/Debian系统：**
```bash
# 更新系统
apt update && apt upgrade -y

# 安装Python和MySQL
apt install -y python3 python3-pip python3-venv mysql-server
```

**CentOS/RHEL系统：**
```bash
# 更新系统
yum update -y

# 安装Python和MySQL
yum install -y python3 python3-pip python3-venv mysql-server
```

#### 1.2 启动MySQL服务

**Ubuntu/Debian系统：**
```bash
systemctl enable mysql
systemctl start mysql
```

**CentOS/RHEL系统：**
```bash
systemctl enable mysqld
systemctl start mysqld
```

### 2. 准备项目

#### 2.1 克隆项目代码
```bash
git clone https://github.com/your-repo/wechat_survey.git
cd wechat_survey
```

#### 2.2 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或在Windows上使用：venv\Scripts\activate
```

#### 2.3 安装Python依赖
```bash
pip install -r requirements.txt
```

### 3. 配置数据库

#### 3.1 创建数据库
```bash
# 登录MySQL
mysql -u root -p

# 创建数据库和用户
CREATE DATABASE wechat_survey CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'wechat'@'localhost' IDENTIFIED BY 'your-strong-password';
GRANT ALL PRIVILEGES ON wechat_survey.* TO 'wechat'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3.2 配置环境变量

创建`.env`文件并配置数据库连接：
```bash
# 复制示例文件
cp .env.example .env

# 编辑.env文件
nano .env
```

配置内容：
```
# Django配置
DEBUG=False
SECRET_KEY=your-secret-key-here-change-this-in-production
BASE_URL=http://your-domain.com
ALLOWED_HOSTS=your-domain.com

# SSL配置
USE_SSL=False

# 数据库配置（MySQL）
DATABASE_URL=mysql://wechat:your-strong-password@localhost:3306/wechat_survey

# 微信配置（可选）
WECHAT_APP_ID=
WECHAT_APP_SECRET=

# 日志配置
DJANGO_LOG_LEVEL=ERROR
```

### 4. 部署应用

#### 4.1 执行数据库迁移
```bash
# 激活虚拟环境（如果尚未激活）
source venv/bin/activate

# 执行数据库迁移
python manage.py migrate
```

#### 4.2 收集静态文件
```bash
python manage.py collectstatic --noinput
```

#### 4.3 创建超级用户
```bash
python manage.py createsuperuser
```

#### 4.4 配置Web服务器

##### 使用Gunicorn（推荐）
```bash
# 安装Gunicorn
pip install gunicorn

# 启动Gunicorn
gunicorn --bind 0.0.0.0:8000 wechat_survey.wsgi:application
```

##### 使用uWSGI（可选）
```bash
# 安装uWSGI
pip install uwsgi

# 启动uWSGI
uwsgi --http :8000 --module wechat_survey.wsgi:application
```

#### 4.5 配置Nginx反向代理

**安装Nginx：**
```bash
# Ubuntu/Debian
apt install -y nginx

# CentOS/RHEL
yum install -y nginx
```

**创建Nginx配置文件：**
```bash
nano /etc/nginx/sites-available/wechat_survey
```

**配置内容：**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 静态文件服务
    location /static/ {
        alias /path/to/wechat_survey/staticfiles/;
        expires 30d;
        add_header Cache-Control public;
    }

    # 媒体文件服务
    location /media/ {
        alias /path/to/wechat_survey/media/;
    }

    # 应用代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**启用配置：**
```bash
ln -s /etc/nginx/sites-available/wechat_survey /etc/nginx/sites-enabled/
nginx -t  # 测试配置
systemctl reload nginx
```

### 5. 启动服务

**使用Systemd管理服务：**

创建服务文件：
```bash
nano /etc/systemd/system/wechat_survey.service
```

配置内容：
```ini
[Unit]
Description=WeChat Survey System
After=network.target mysql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/wechat_survey
ExecStart=/path/to/wechat_survey/venv/bin/gunicorn --bind 127.0.0.1:8000 wechat_survey.wsgi:application
Restart=always
Environment="PATH=/path/to/wechat_survey/venv/bin"

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
systemctl daemon-reload
systemctl enable wechat_survey
systemctl start wechat_survey
```

## 访问应用
- 应用访问地址：http://your-domain.com
- 管理后台：http://your-domain.com/admin

## 常用命令

**查看服务状态：**
```bash
systemctl status wechat_survey
```

**查看服务日志：**
```bash
journalctl -u wechat_survey -f
```

**重启服务：**
```bash
systemctl restart wechat_survey
```

**停止服务：**
```bash
systemctl stop wechat_survey
```

**执行数据库迁移：**
```bash
cd /path/to/wechat_survey
source venv/bin/activate
python manage.py migrate
```

## 生产环境部署最佳实践

### 1. 安全配置

#### 1.1 基本安全设置
- **修改SECRET_KEY**：使用强随机字符串作为SECRET_KEY
  ```bash
  openssl rand -hex 32
  ```
- **关闭DEBUG模式**：确保`DEBUG=False`
- **配置ALLOWED_HOSTS**：只允许特定域名访问
- **启用HTTPS**：生产环境建议配置HTTPS

#### 1.2 数据库安全
- 使用强密码
- 限制数据库用户的权限
- 定期备份数据库

### 2. 性能优化

#### 2.1 Web服务器配置
- 根据服务器配置调整Gunicorn/uWSGI的worker数量
- 启用Nginx的gzip压缩
- 配置适当的缓存策略

#### 2.2 数据库优化
- 定期优化数据库表
- 配置适当的索引

### 3. 备份策略

**自动备份脚本示例**：
```bash
#!/bin/bash
# 数据库自动备份脚本

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"
DB_USER="wechat"
DB_NAME="wechat_survey"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/db_backup_$DATE.sql

# 保留最近7天的备份
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete
```

## 常见问题和解决方案

### 500错误
- 检查应用日志：`journalctl -u wechat_survey -f`
- 确保数据库连接正确
- 检查静态文件是否正确收集

### 数据库连接错误
- 检查数据库服务是否运行
- 检查数据库用户名和密码
- 检查数据库名称是否正确

### 静态文件无法访问
- 检查Nginx配置中的静态文件路径
- 确保执行了`collectstatic`命令
- 检查静态文件权限

## 注意事项

1. **安全性**：
   - 在生产环境中，务必修改`SECRET_KEY`为强随机字符串
   - 设置`DEBUG=False`
   - 配置合适的`ALLOWED_HOSTS`
   - 考虑使用HTTPS

2. **性能优化**：
   - 根据服务器配置调整Web服务器的worker数量
   - 启用gzip压缩
   - 配置适当的缓存策略

3. **数据备份**：
   - 定期备份数据库
   - 备份媒体文件和静态文件

4. **日志管理**：
   - 定期清理日志文件
   - 考虑使用日志管理工具

## 联系方式

如有问题或建议，请联系项目维护者：
- 邮箱：your-email@example.com
- GitHub：https://github.com/your-repo/wechat_survey

---

部署文档更新时间：2025-12-23
