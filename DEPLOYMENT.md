# 微信问卷系统部署文档

## 项目介绍
微信问卷系统是基于Django开发的问卷调查系统，支持创建问卷、生成二维码、收集反馈等功能。本文档将介绍Docker部署方案（nginx+uwsgi），采用单应用部署方式。

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
sudo apt install -y docker compose
```

**CentOS/RHEL系统：**
```bash
# 安装Docker
yum install -y yum-utils
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
yum install -y docker compose
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

1. **创建.env文件**

在项目根目录创建`.env`文件：
```bash
cp .env.example .env
```

2. **编辑.env文件**

修改`.env`文件中的环境变量：
```bash
# Django配置
DEBUG=False
SECRET_KEY=your-secret-key-here-change-this-in-production  # 请替换为实际的密钥
BASE_URL=http://localhost

# 数据库配置
DATABASE_URL=postgres://postgres:postgres@db:5432/wechat_survey

# 微信配置（可选，根据实际需求配置）
WECHAT_APP_ID=
WECHAT_APP_SECRET=
```

3. **查看所有可用环境变量**

`.env`文件中包含了所有可用的环境变量，你可以根据实际需求进行配置。

#### 4. 部署微信问卷系统

**启动微信问卷系统：**
```bash
docker compose up -d
```

> 说明：docker compose会自动创建所需的网络和卷，无需手动创建。

### 访问应用
- 应用访问地址：http://localhost

### 常用命令

**启动服务：**
```bash
docker compose up -d
```

**停止服务：**
```bash
docker compose down
```

**查看日志：**
```bash
docker compose logs -f
```

**执行数据库迁移：**
```bash
# 执行数据库迁移
docker compose run --rm web python manage.py migrate

# 创建超级用户
docker compose run --rm web python manage.py createsuperuser

# 收集静态文件
docker compose run --rm web python manage.py collectstatic --noinput
```

## 生产环境部署最佳实践

### 1. 安全配置

#### 1.1 基本安全设置
- **修改SECRET_KEY**：使用强随机字符串作为SECRET_KEY
  ```bash
  # 生成强随机字符串（Linux/macOS）
  openssl rand -hex 32
  ```
- **关闭DEBUG模式**：确保`DEBUG=False`
- **配置ALLOWED_HOSTS**：只允许特定域名访问
  ```bash
  ALLOWED_HOSTS=your-domain.com,www.your-domain.com
  ```
- **启用HTTPS**：生产环境必须使用HTTPS
  ```bash
  USE_SSL=True
  ```

#### 1.2 数据库安全
- **修改默认数据库密码**：
  ```bash
  # 在.env文件中修改数据库连接URL
  DATABASE_URL=postgres://postgres:your-strong-db-password@db:5432/wechat_survey
  ```
- **定期备份数据库**：
  ```bash
  # 手动备份示例
  docker compose exec db pg_dump -U postgres wechat_survey > backup_$(date +%Y%m%d_%H%M%S).sql
  ```

### 2. 性能优化

#### 2.1 uWSGI配置优化
- 根据服务器CPU核心数调整uwsgi.ini中的workers和threads
  ```ini
  # uwsgi.ini
  workers = 4  # 建议设置为CPU核心数
  threads = 2  # 每个worker的线程数
  ```

#### 2.2 静态文件优化
- 确保已执行`collectstatic`命令
- 考虑使用CDN加速静态文件访问

#### 2.3 数据库优化
- 定期执行数据库优化
  ```bash
  docker compose run --rm web python manage.py dbshell
  VACUUM ANALYZE;
  ```

### 3. 备份策略

#### 3.1 自动备份脚本示例
```bash
#!/bin/bash
# 数据库自动备份脚本

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"
CONTAINER_NAME="wechat_survey_db"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
docker compose exec $CONTAINER_NAME pg_dump -U postgres wechat_survey > $BACKUP_DIR/backup_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/backup_$DATE.sql

# 保留最近7天的备份
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

#### 3.2 备份频率建议
- **数据库**：每天备份一次
- **静态文件和媒体文件**：每周备份一次
- **配置文件**：每次修改后备份

### 4. 监控和日志管理

#### 4.1 日志查看
```bash
# 查看所有服务日志
./deploy.sh logs

# 查看特定服务日志
docker compose logs -f web
```

#### 4.2 日志持久化
- 考虑使用ELK Stack或Loki等工具进行日志集中管理
- 定期清理旧日志

### 5. 升级和维护

#### 5.1 应用升级流程
```bash
# 1. 拉取最新代码
git pull

# 2. 停止并移除旧容器
./deploy.sh stop

# 3. 构建新镜像并部署
./deploy.sh --prod deploy

# 4. 验证部署
docker compose ps
```

#### 5.2 定期维护任务
- 检查Docker镜像更新
- 清理未使用的Docker资源
  ```bash
  docker system prune -f
  ```
- 更新依赖包
  ```bash
  pip install -r requirements.txt --upgrade
  ```

### 6. 生产环境一键部署

#### 6.1 部署命令
```bash
# 生产环境一键部署
./deploy.sh --prod deploy
```

#### 6.2 部署脚本特点
- 自动检查Docker和Docker Compose安装
- 验证生产环境配置安全性
- 自动构建镜像
- 执行数据库迁移
- 收集静态文件
- 启动所有服务
- 显示服务状态和访问地址

#### 6.3 生产环境注意事项
- 部署前确保已备份数据
- 部署过程中应用会短暂不可用
- 部署后验证应用功能

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