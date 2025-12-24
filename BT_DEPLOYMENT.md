# 微信问卷系统 - 宝塔面板部署文档

## 一、部署前准备

### 1. 服务器要求
- **操作系统**：CentOS 7/8/9、Ubuntu 18.04+、Debian 10+
- **内存**：至少 2GB RAM
- **CPU**：至少 2 核
- **硬盘**：至少 20GB 可用空间
- **网络**：公网 IP 地址

### 2. 安装宝塔面板

#### 2.1 一键安装宝塔面板
```bash
# CentOS/RedHat
yum install -y wget && wget -O install.sh https://download.bt.cn/install/install_6.0.sh && sh install.sh ed8484bec

# Ubuntu/Debian
wget -O install.sh https://download.bt.cn/install/install-ubuntu_6.0.sh && sudo bash install.sh ed8484bec
```

#### 2.2 登录宝塔面板
- 安装完成后，根据提示获取登录地址、用户名和密码
- 登录宝塔面板：`http://你的服务器IP:8888/随机字符`
- 首次登录需要绑定宝塔账号，建议注册并绑定

### 3. 安装必要软件

登录宝塔面板后，安装以下软件：

1. **Web 服务器**：Nginx 1.20+
2. **数据库**：MySQL 8.0+ 或 PostgreSQL 15+
3. **Python 管理器**：宝塔自带的 Python 管理器 3.0+
4. **其他**：Git（用于克隆代码）

### 4. 创建数据库

1. 登录宝塔面板，点击左侧菜单「数据库」
2. 点击「添加数据库」
3. 填写数据库信息：
   - 数据库名：`wechat_survey`
   - 用户名：`wechat_survey_user`
   - 密码：`设置强密码`
   - 字符集：`utf8mb4`
   - 排序规则：`utf8mb4_general_ci`
4. 点击「提交」，记录数据库信息

## 二、部署步骤

### 1. 克隆项目代码

#### 1.1 创建网站目录
1. 登录宝塔面板，点击左侧菜单「网站」
2. 点击「添加站点」
3. 填写基本信息：
   - 域名：`your-domain.com`（或使用临时域名）
   - 根目录：`/www/wwwroot/wechat_survey`
   - PHP版本：`纯静态`（后续会修改为Python）
   - 数据库：`不创建`（已手动创建）
4. 点击「提交」

#### 1.2 克隆代码
1. 进入网站根目录：`/www/wwwroot/wechat_survey`
2. 点击「终端」，执行以下命令：
   ```bash
   # 克隆代码（替换为你的实际仓库地址）
   git clone https://github.com/your-repo/wechat_survey.git .
   
   # 或上传压缩包并解压
   # wget https://your-repo/wechat_survey.tar.gz && tar -zxvf wechat_survey.tar.gz --strip-components=1
   ```

### 2. 配置Python环境

#### 2.1 安装Python虚拟环境
1. 点击左侧菜单「Python项目」
2. 点击「添加Python项目」
3. 填写项目信息：
   - 项目名称：`微信问卷系统`
   - 项目路径：`/www/wwwroot/wechat_survey`
   - Python版本：`3.9+`（推荐3.11）
   - 框架：`Django`
   - 启动方式：`uWSGI`
4. 点击「创建」，等待虚拟环境创建完成

#### 2.2 安装项目依赖
1. 进入项目虚拟环境目录：`/www/wwwroot/wechat_survey/.venv/bin`
2. 执行以下命令安装依赖：
   ```bash
   # 激活虚拟环境
   source /www/wwwroot/wechat_survey/.venv/bin/activate
   
   # 安装项目依赖
   pip install -r requirements.txt
   ```

### 3. 配置项目

#### 3.1 修改配置文件
1. 编辑生产环境配置文件：`production_settings.py`
2. 修改以下配置：
   ```python
   # 域名配置（替换为你的实际域名）
   ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
   
   # 数据库配置（替换为你的实际数据库信息）
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',  # 或 postgresql
           'NAME': 'wechat_survey',
           'USER': 'wechat_survey_user',
           'PASSWORD': 'your-db-password',
           'HOST': 'localhost',
           'PORT': '3306',
           'OPTIONS': {
               'charset': 'utf8mb4',
               'sql_mode': 'STRICT_TRANS_TABLES',
           },
       }
   }
   
   # 密钥配置（生成随机字符串）
   SECRET_KEY = 'your-production-secret-key'
   ```

#### 3.2 执行数据库迁移
1. 进入项目虚拟环境
2. 执行以下命令：
   ```bash
   # 激活虚拟环境
   source /www/wwwroot/wechat_survey/.venv/bin/activate
   
   # 执行数据库迁移
   python manage.py migrate
   
   # 收集静态文件
   python manage.py collectstatic --noinput
   
   # 创建超级用户
   python manage.py createsuperuser
   ```

### 4. 配置uWSGI

#### 4.1 导入uWSGI配置
1. 点击左侧菜单「Python项目」
2. 找到刚创建的项目，点击「管理」
3. 点击「配置文件」，替换为以下内容：
   ```ini
   [uwsgi]
   chdir = /www/wwwroot/wechat_survey
   module = wechat_survey.wsgi:application
   home = /www/wwwroot/wechat_survey/.venv
   master = true
   workers = 4
   threads = 2
   socket = 127.0.0.1:8001
   chmod-socket = 666
   vacuum = true
   logto = /www/wwwlogs/wechat_survey_uwsgi.log
   socket-log = true
   logdate = true
   env = DJANGO_SETTINGS_MODULE=wechat_survey.production_settings
   buffer-size = 65536
   harakiri = 60
   max-requests = 5000
   max-requests-delta = 30
   enable-threads = true
   lazy-apps = true
   limit-post = 0
   ```
4. 点击「保存」

### 5. 配置Nginx

#### 5.1 修改Nginx配置
1. 点击左侧菜单「网站」
2. 找到刚创建的站点，点击「设置」
3. 点击「配置文件」，替换为以下内容：
   ```nginx
   server {
       listen 80;
       server_name your-domain.com www.your-domain.com;
       root /www/wwwroot/wechat_survey;
       index index.html index.htm index.php;
       
       # 禁止访问隐藏文件
       location ~ ^/\. {
           deny all;
       }
       
       # 静态文件处理
       location /static/ {
           alias /www/wwwroot/wechat_survey/staticfiles/;
           expires 30d;
           add_header Cache-Control public;
           location ~ \.php$ {
               deny all;
           }
       }
       
       # 媒体文件处理
       location /media/ {
           alias /www/wwwroot/wechat_survey/media/;
           expires 7d;
           add_header Cache-Control public;
           location ~ \.php$ {
               deny all;
           }
       }
       
       # Django应用代理
       location / {
           include uwsgi_params;
           uwsgi_pass 127.0.0.1:8001;
           uwsgi_param Host $host;
           uwsgi_param X-Real-IP $remote_addr;
           uwsgi_param X-Forwarded-For $proxy_add_x_forwarded_for;
           uwsgi_param X-Forwarded-Proto $scheme;
       }
       
       access_log /www/wwwlogs/wechat_survey_access.log;
       error_log /www/wwwlogs/wechat_survey_error.log;
   }
   ```
4. 点击「保存」

### 6. 启动项目

1. 点击左侧菜单「Python项目」
2. 找到刚创建的项目，点击「启动」
3. 查看启动状态，确保显示「运行中」
4. 点击左侧菜单「网站」，找到刚创建的站点，点击「管理」
5. 点击「Nginx状态」，确保显示「运行中」

## 三、部署验证

### 1. 访问应用
- 应用首页：`http://your-domain.com`
- 管理后台：`http://your-domain.com/admin`
- 使用之前创建的超级用户登录管理后台

### 2. 检查日志

1. 查看uWSGI日志：
   ```bash
   tail -f /www/wwwlogs/wechat_survey_uwsgi.log
   ```

2. 查看Nginx日志：
   ```bash
   tail -f /www/wwwlogs/wechat_survey_access.log
   tail -f /www/wwwlogs/wechat_survey_error.log
   ```

3. 查看Django日志：
   ```bash
   # Django日志默认输出到控制台，可通过uWSGI日志查看
   ```

## 四、SSL配置（可选）

### 1. 申请SSL证书

1. 点击左侧菜单「网站」
2. 找到刚创建的站点，点击「设置」
3. 点击「SSL」
4. 选择「Let's Encrypt」
5. 勾选需要申请证书的域名
6. 选择「文件验证」
7. 点击「申请」，等待证书申请完成

### 2. 启用HTTPS

1. 证书申请成功后，勾选「强制HTTPS」
2. 点击「保存」
3. 修改Django配置：
   ```python
   # production_settings.py
   USE_SSL = True
   ```
4. 重启Python项目

## 五、常见问题

### 1. 502 Bad Gateway

**可能原因**：
- uWSGI服务未启动
- uWSGI配置错误
- Nginx配置错误

**解决方案**：
- 检查uWSGI状态和日志
- 检查Nginx配置文件
- 检查端口是否被占用：`netstat -tlnp | grep 8001`

### 2. 静态文件404

**可能原因**：
- 未执行`collectstatic`命令
- Nginx静态文件路径配置错误
- 静态文件权限问题

**解决方案**：
- 执行`python manage.py collectstatic --noinput`
- 检查Nginx配置中的静态文件路径
- 设置静态文件权限：`chmod -R 755 /www/wwwroot/wechat_survey/staticfiles/`

### 3. 数据库连接错误

**可能原因**：
- 数据库配置错误
- 数据库服务未启动
- 数据库用户权限问题

**解决方案**：
- 检查数据库配置信息
- 检查数据库服务状态
- 授予数据库用户权限：`GRANT ALL PRIVILEGES ON wechat_survey.* TO 'wechat_survey_user'@'localhost';`

## 六、维护指南

### 1. 代码更新

```bash
# 进入项目目录
cd /www/wwwroot/wechat_survey

# 拉取最新代码
git pull

# 激活虚拟环境
source .venv/bin/activate

# 安装新依赖（如果有）
pip install -r requirements.txt

# 执行数据库迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 重启Python项目
```

### 2. 定期备份

1. 数据库备份：
   - 宝塔面板 → 数据库 → 选择数据库 → 备份
   - 建议设置自动备份

2. 文件备份：
   - 宝塔面板 → 文件 → 选择网站目录 → 压缩
   - 建议定期备份`media`目录和数据库

### 3. 性能优化

1. 调整uWSGI参数：
   - 根据CPU核心数调整`workers`数量
   - 调整`threads`数量

2. Nginx优化：
   - 启用gzip压缩（已配置）
   - 调整缓冲区大小
   - 配置静态文件缓存

3. 数据库优化：
   - 定期优化表结构
   - 添加必要的索引
   - 调整MySQL/PostgreSQL配置

## 七、技术支持

- 项目文档：`README.md`
- 部署文档：`BT_DEPLOYMENT.md`
- 常见问题：`BT_DEPLOYMENT.md#四、常见问题`

---

部署文档更新时间：2025-12-24
