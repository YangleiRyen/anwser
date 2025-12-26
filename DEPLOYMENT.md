# 微信问卷系统部署文档

## 项目介绍
微信问卷系统是基于Django开发的问卷调查系统，支持创建问卷、生成二维码、收集反馈等功能。本文档将介绍开发环境和生产环境的部署方案。

## 系统要求
- **开发环境**：Windows/macOS/Linux
  - Python 3.9+
  - SQLite（默认）
  
- **生产环境**：Linux系统（如Ubuntu/Debian、CentOS/RHEL）
  - Python 3.9+
  - MySQL 8.0+（推荐）或 SQLite
  - uWSGI 2.0+
  - Nginx 1.18+

## 目录结构
```
anwser/
├── survey/                # 问卷应用代码
├── wechat_survey/         # 项目配置目录
│   ├── settings.py        # 主配置文件（开发+生产）
│   └── ...
├── .env                   # 开发环境配置文件
├── .env.example           # 环境变量示例文件
├── .env.production        # 生产环境配置文件
├── nginx.conf             # Nginx配置模板
├── run_dev.bat/sh         # 开发环境启动脚本
├── run_prod.bat/sh        # 生产环境启动脚本
├── uwsgi.ini              # uWSGI配置文件
├── wechat_survey.service  # Systemd服务配置模板
└── ...
```

## 开发环境部署

### 1. 安装依赖

**Windows系统：**
```bash
# 安装Python 3.9+（略）

# 克隆项目代码
git clone https://github.com/your-repo/wechat_survey.git
cd wechat_survey

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

**Linux/macOS系统：**
```bash
# 安装Python 3.9+（Ubuntu示例）
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 克隆项目代码
git clone https://github.com/your-repo/wechat_survey.git
cd wechat_survey

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置开发环境

**开发环境默认配置：**
- 使用SQLite数据库
- DEBUG=True
- 允许所有主机访问（ALLOWED_HOSTS=*）
- 禁用SSL

**启动开发服务器：**

**方式1：使用启动脚本（推荐）**
```bash
# Windows
run_dev.bat

# Linux/macOS
chmod +x run_dev.sh
./run_dev.sh
```

**方式2：手动运行**
```bash
# 启动开发服务器
python manage.py runserver
```

### 3. 访问开发环境
- 应用地址：http://127.0.0.1:8000
- 管理后台：http://127.0.0.1:8000/admin
  - 初始无超级用户，需要创建：`python manage.py createsuperuser`

## 生产环境部署

### 1. 准备工作

**安装系统依赖（Ubuntu示例）：**
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y python3 python3-pip python3-venv mysql-server nginx uwsgi uwsgi-plugin-python3
```

**启动并配置MySQL：**
```bash
# 启动MySQL
sudo systemctl enable mysql
sudo systemctl start mysql

# 安全配置
sudo mysql_secure_installation

# 创建数据库和用户
mysql -u root -p
CREATE DATABASE wechat_survey CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'wechat_survey_user'@'localhost' IDENTIFIED BY 'your-strong-db-password';
GRANT ALL PRIVILEGES ON wechat_survey.* TO 'wechat_survey_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 2. 部署应用

**克隆项目代码：**
```bash
sudo mkdir -p /var/www
sudo chown -R $USER:$USER /var/www
cd /var/www
git clone https://github.com/your-repo/wechat_survey.git
sudo chown -R www-data:www-data /var/www/wechat_survey
cd /var/www/wechat_survey
```

**配置虚拟环境和依赖：**
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**配置生产环境：**
```bash
# 复制生产环境配置文件
cp .env.example .env.production

# 编辑生产环境配置
nano .env.production
```

**生产环境配置示例：**
```
# 核心配置
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECRET_KEY=your-production-secret-key  # 使用: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 数据库配置
DATABASE_URL=mysql://wechat_survey_user:your-strong-db-password@localhost:3306/wechat_survey

# 微信配置（可选）
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret

# SSL配置
USE_SSL=True  # 配置SSL后设置为True
```

**执行数据库迁移：**
```bash
export DJANGO_SETTINGS_MODULE=wechat_survey.settings
export ENV_FILE=.env.production
python manage.py migrate
```

**收集静态文件：**
```bash
python manage.py collectstatic --noinput
```

**创建超级用户：**
```bash
python manage.py createsuperuser
```

### 3. 配置uWSGI

**uWSGI配置文件已准备好**，位于项目根目录的`uwsgi.ini`，需要修改以下内容：
```ini
# 修改项目目录
chdir = /var/www/wechat_survey

# 修改日志和其他路径
logto = /var/www/wechat_survey/uwsgi.log
touch-reload = /var/www/wechat_survey/reload.txt
pidfile = /var/www/wechat_survey/uwsgi.pid
```

### 4. 配置Nginx

**复制Nginx配置文件：**
```bash
# 复制配置文件
sudo cp /var/www/wechat_survey/nginx.conf /etc/nginx/sites-available/wechat_survey

# 编辑配置文件
sudo nano /etc/nginx/sites-available/wechat_survey
```

**修改Nginx配置：**
```nginx
# 修改域名
server_name your-domain.com www.your-domain.com;

# 修改静态文件路径
location /static/ {
    alias /var/www/wechat_survey/staticfiles/;
    # ...
}

# 修改媒体文件路径
location /media/ {
    alias /var/www/wechat_survey/media/;
    # ...
}
```

**启用Nginx配置：**
```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/wechat_survey /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载Nginx
sudo systemctl reload nginx
```

### 5. 配置Systemd服务

**复制并修改Systemd服务文件：**
```bash
# 复制服务文件
sudo cp /var/www/wechat_survey/wechat_survey.service /etc/systemd/system/

# 编辑服务文件
sudo nano /etc/systemd/system/wechat_survey.service
```

**修改Systemd配置：**
```ini
# 修改运行用户
User=www-data
Group=www-data

# 修改工作目录
WorkingDirectory=/var/www/wechat_survey

# 修改uwsgi路径
ExecStart=/var/www/wechat_survey/venv/bin/uwsgi --ini uwsgi.ini
```

**启用并启动服务：**
```bash
sudo systemctl daemon-reload
sudo systemctl enable wechat_survey
sudo systemctl start wechat_survey
```

### 6. 访问生产环境
- 应用地址：http://your-domain.com 或 https://your-domain.com（如果配置了SSL）
- 管理后台：http://your-domain.com/admin

### 7. 配置SSL（可选）

**使用Let's Encrypt配置SSL：**
```bash
# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 配置SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 设置自动续期
sudo crontab -e
# 添加以下内容
0 3 * * * /usr/bin/certbot renew --quiet
```

## 生产环境管理

### 1. 常用命令

**服务管理：**
```bash
# 查看服务状态
sudo systemctl status wechat_survey

# 重启服务
sudo systemctl restart wechat_survey

# 停止服务
sudo systemctl stop wechat_survey

# 查看服务日志
sudo journalctl -u wechat_survey -f
```

**应用管理：**
```bash
# 激活虚拟环境
cd /var/www/wechat_survey
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=wechat_survey.settings
export ENV_FILE=.env.production

# 执行数据库迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 查看应用日志
tail -f uwsgi.log
```

### 2. 监控和维护

**监控服务状态：**
```bash
# 查看uWSGI状态
uwsgi --connect-and-read /var/www/wechat_survey/uwsgi.sock  # 如果使用Unix套接字

# 查看Nginx状态
nginx -t
```

**日志管理：**
```bash
# 查看Nginx日志
tail -f /var/log/nginx/wechat_survey_access.log
tail -f /var/log/nginx/wechat_survey_error.log

# 查看应用日志
tail -f /var/www/wechat_survey/uwsgi.log
```

**数据库备份：**
```bash
# 手动备份
mysqldump -u wechat_survey_user -p wechat_survey > wechat_survey_backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复备份
mysql -u wechat_survey_user -p wechat_survey < wechat_survey_backup.sql
```

## 常见问题和解决方案

### 1. 500错误
- 检查应用日志：`tail -f /var/www/wechat_survey/uwsgi.log`
- 确保数据库连接正确
- 检查静态文件是否正确收集

### 2. 静态文件无法访问
- 检查Nginx配置中的静态文件路径
- 确保执行了`collectstatic`命令
- 检查静态文件权限：`sudo chmod -R 755 /var/www/wechat_survey/staticfiles`

### 3. 数据库连接错误
- 检查MySQL服务是否运行：`sudo systemctl status mysql`
- 检查数据库用户名和密码是否正确
- 检查数据库名称是否正确

### 4. uWSGI服务无法启动
- 检查uWSGI配置文件：`uwsgi --ini uwsgi.ini --check-config`
- 查看uWSGI日志：`tail -f /var/www/wechat_survey/uwsgi.log`

## 部署最佳实践

1. **安全性：**
   - 生产环境务必设置`DEBUG=False`
   - 使用强随机`SECRET_KEY`
   - 配置具体的`ALLOWED_HOSTS`
   - 启用SSL
   - 定期更新依赖包

2. **性能优化：**
   - 根据服务器配置调整uWSGI的进程和线程数
   - 启用Nginx的gzip压缩
   - 配置适当的缓存策略
   - 优化数据库查询

3. **备份策略：**
   - 定期备份数据库
   - 备份媒体文件和静态文件
   - 考虑使用异地备份

4. **监控和日志：**
   - 配置集中式日志管理（如ELK Stack）
   - 设置监控告警（如Prometheus+Grafana）
   - 定期查看日志，发现问题及时处理

## 更新日志

- 2025-12-26：更新部署文档，包含开发和生产环境部署步骤
- 2025-12-23：初始版本

## 联系方式

如有问题或建议，请联系项目维护者：
- 邮箱：your-email@example.com
- GitHub：https://github.com/your-repo/wechat_survey
