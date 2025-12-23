# 微信问卷系统

微信问卷系统是一个基于Django框架开发的在线问卷系统，支持微信扫码填写、问卷统计分析等功能。

## 项目结构

### 项目根目录
| 文件/目录 | 作用 |
| --- | --- |
| `wechat_survey/` | 项目主目录，包含Django项目配置 |
| `survey/` | 问卷应用目录，包含所有业务逻辑 |
| `standalone_nginx/` | 独立Nginx配置目录，支持多应用部署 |
| `.git` | Git版本控制目录，存储项目的Git仓库信息 |
| `.venv` | Python虚拟环境目录，存储项目的Python虚拟环境 |
| `.gitignore` | Git忽略文件配置，指定Git需要忽略的文件和目录 |
| `requirements.txt` | Python依赖列表，包含项目所需的所有Python依赖包 |
| `Dockerfile` | Docker镜像构建文件，定义了应用的运行环境 |
| `docker compose.yml` | Docker Compose配置文件，定义了多容器部署方案 |
| `deploy.sh` | 部署脚本，用于简化Docker容器的管理和操作 |
| `DEPLOYMENT.md` | 部署文档，详细说明项目的Docker部署步骤 |
| `manage.py` | Django项目管理脚本，用于执行各种Django命令 |
| `README.md` | 项目说明文档 |

## 目录详细结构

### 项目主目录（wechat_survey/）

**目录结构：**
```
wechat_survey/
├── __pycache__/           # Python编译文件目录
├── asgi.py                # ASGI入口文件，用于部署支持异步的Django应用
├── production_settings.py  # 生产环境配置文件
├── settings.py            # Django项目主要设置文件
├── urls.py                # 项目URL配置文件
├── wsgi.py                # WSGI入口文件，用于部署Django应用
└── __init__.py            # Python包标识文件
```

**文件说明：**
| 文件 | 作用 |
| --- | --- |
| `asgi.py` | ASGI入口文件，用于部署支持异步的Django应用 |
| `production_settings.py` | 生产环境配置文件，包含生产环境特有的设置 |
| `settings.py` | Django项目主要设置文件，包含数据库配置、应用配置、中间件配置等 |
| `urls.py` | 项目URL配置文件，定义了项目的路由规则 |
| `wsgi.py` | WSGI入口文件，用于部署Django应用，是uwsgi加载Django应用的入口 |
| `__init__.py` | Python包标识文件，使目录成为Python包 |

### 问卷应用目录（survey/）

**目录结构：**
```
survey/
├── admin/                 # 自定义Django Admin站点配置
├── migrations/            # 数据库迁移文件
├── models/                # 数据模型定义（模块化设计）
├── serializers/           # DRF序列化器
├── services/              # 业务逻辑服务层（待实现）
├── static/                # 静态文件（CSS、JavaScript、图片等）
├── templates/             # HTML模板文件
├── utils/                 # 工具函数（待实现）
├── views/                 # 视图类和函数
├── __pycache__/           # Python编译文件目录
├── apps.py                # 应用配置文件
├── tests.py               # 应用测试文件
├── urls.py                # 应用URL路由配置
└── __init__.py            # Python包标识文件
```

#### admin目录
| 文件 | 作用 |
| --- | --- |
| `__init__.py` | 导入所有admin模块，方便统一引用 |
| `base.py` | 自定义AdminSite实现，扩展了Django默认的Admin站点 |
| `category_admin.py` | Category模型的Admin管理类 |
| `question_admin.py` | Question模型的Admin管理类，包含导出功能 |
| `survey_admin.py` | Survey模型的Admin管理类，包含统计功能 |
| `response_admin.py` | Response模型的Admin管理类 |
| `answer_admin.py` | Answer模型的Admin管理类 |
| `qrcode_admin.py` | QRCode模型的Admin管理类 |
| `admin.py` | 原始admin.py文件，现在只包含导入语句：`from .admin import *` |

#### models目录
| 文件 | 作用 |
| --- | --- |
| `__init__.py` | 导入所有模型，方便统一引用 |
| `survey.py` | 包含Survey模型，定义问卷的基本信息 |
| `category.py` | 包含Category模型，定义问题分类 |
| `question.py` | 包含Question和Option模型，定义问题和选项 |
| `survey_question.py` | 包含SurveyQuestion模型，定义问卷和问题的多对多关系 |
| `response.py` | 包含Response模型，定义问卷回答 |
| `answer.py` | 包含Answer模型，定义问题答案 |
| `qrcode.py` | 包含QRCode模型，定义问卷二维码 |

#### views目录
| 文件 | 作用 |
| --- | --- |
| `__init__.py` | 导入所有视图类和函数，方便统一引用 |
| `api.py` | 包含API视图，如SurveyViewSet、QRCodeViewSet和survey_statistics函数 |
| `survey.py` | 包含问卷相关视图，如SurveyDetailView和SubmitSurveyView |
| `qrcode.py` | 包含二维码相关视图，如QRCodeRedirectView和QRCodeImageView |
| `wechat.py` | 包含微信相关视图，如WeChatAuthView和WeChatCallbackView |

#### serializers目录
| 文件 | 作用 |
| --- | --- |
| `__init__.py` | 导入所有序列化器，方便统一引用 |
| `question_serializer.py` | 包含QuestionSerializer，用于序列化Question模型 |
| `survey_serializer.py` | 包含SurveySerializer，用于序列化Survey模型 |
| `answer_serializer.py` | 包含AnswerSerializer，用于序列化Answer模型 |
| `response_serializer.py` | 包含ResponseSerializer，用于序列化Response模型 |
| `qrcode_serializer.py` | 包含QRCodeSerializer，用于序列化QRCode模型 |

#### services目录
| 文件 | 作用 |
| --- | --- |
| （待实现） | 包含业务逻辑服务层，封装复杂的业务逻辑 |

#### utils目录
| 文件 | 作用 |
| --- | --- |
| （待实现） | 包含工具函数，提供通用的辅助功能 |

### standalone_nginx目录

**目录结构：**
```
standalone_nginx/
├── conf.d/                # 应用配置目录，包含各应用的Nginx配置
│   └── wechat_survey.conf  # 微信问卷系统Nginx配置
├── ssl/                   # SSL证书目录
├── nginx.conf             # Nginx主配置文件
└── docker compose.yml     # Nginx的Docker Compose配置
```

**文件说明：**
| 文件/目录 | 作用 |
| --- | --- |
| `nginx.conf` | Nginx主配置文件，包含全局配置和基础设置 |
| `conf.d/` | 应用配置目录，包含各应用的Nginx配置 |
| `conf.d/wechat_survey.conf` | 微信问卷系统Nginx配置，包含反向代理、静态文件服务等 |
| `ssl/` | SSL证书目录，用于存放HTTPS所需的SSL证书和密钥 |
| `docker compose.yml` | Nginx的Docker Compose配置，定义了Nginx服务的部署方式 |

## 项目根目录文件详解

### 1. 目录

- **.git**: Git版本控制目录，存储项目的Git仓库信息，包括提交历史、分支、标签等
- **.venv**: Python虚拟环境目录，存储项目的Python虚拟环境，包括安装的依赖包
- **standalone_nginx**: 独立Nginx配置目录，支持多应用部署，包含反向代理和静态文件服务配置
- **survey**: 问卷应用目录，项目的核心应用，包含所有业务逻辑（模型、视图、序列化器等）
- **wechat_survey**: 项目主目录，Django项目的主目录，包含项目配置、URL路由、WSGI入口等

### 4. 配置文件

- **.gitignore**: Git忽略文件配置，指定Git版本控制中需要忽略的文件和目录，如虚拟环境、日志文件等
- **requirements.txt**: Python依赖列表，列出项目所需的所有Python依赖包及其版本，用于安装依赖

### 3. 部署相关

- **DEPLOYMENT.md**: 部署文档，详细说明项目的传统部署步骤、配置和常用命令

### 4. Django管理文件

- **manage.py**: Django项目管理脚本，用于执行各种Django命令，如创建应用、数据库迁移、启动开发服务器等

## 部署说明

### 开发环境部署

#### 1. 开发环境部署前准备
- 确保已安装Python 3.9+
- 克隆项目代码到本地
- 配置环境变量（.env文件）

  ```bash
  # 创建.env文件
  cp .env.example .env
  
  # 编辑.env文件，修改必要的环境变量
  # 开发环境建议设置DEBUG=True
  ```

#### 2. 执行开发环境部署
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate
# Windows
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 执行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

#### 3. 访问应用
- 应用访问地址：http://localhost:8000
- 管理后台：http://localhost:8000/admin

### 生产环境部署

生产环境部署请参考`DEPLOYMENT.md`文件，该文件包含详细的：
- 系统要求
- 依赖安装
- MySQL数据库配置
- 环境变量配置
- Web服务器配置（Gunicorn/uWSGI）
- Nginx反向代理配置
- 服务管理（Systemd）

#### 生产环境部署特点
- 支持MySQL数据库
- 提供安全配置建议
- 支持HTTPS配置
- 提供备份策略建议
- 提供性能优化建议

### 常用命令

```bash
# 执行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic --noinput

# 启动开发服务器
python manage.py runserver

# 运行测试
python manage.py test
```



### 开发环境设置

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **执行数据库迁移**：
   ```bash
   python manage.py migrate
   ```

3. **创建超级用户**：
   ```bash
   python manage.py createsuperuser
   ```

4. **启动开发服务器**：
   ```bash
   python manage.py runserver
   ```

5. **访问应用**：
   - 应用地址：http://localhost:8000
   - 管理后台：http://localhost:8000/admin

## 功能特点

- ✅ 问卷创建与管理
- ✅ 支持多种问题类型（单选题、多选题、填空题等）
- ✅ 微信扫码填写问卷
- ✅ 问卷统计分析
- ✅ 二维码管理
- ✅ REST API支持
- ✅ 模块化设计
- ✅ Docker部署支持
- ✅ 多应用部署支持

## 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Django | 5.2 |
| API框架 | Django REST Framework | 3.16.1 |
| 数据库 | PostgreSQL 15+ / SQLite | - |
| 前端 | HTML, CSS, JavaScript | - |
| 容器化 | Docker, Docker Compose | - |
| 反向代理 | Nginx | - |
| 应用服务器 | uWSGI | 2.0.25 |
| 二维码生成 | qrcode | 8.2 |
| 图像处理 | Pillow | 12.0.0 |
| 办公文档 | openpyxl | 3.1.5 |

## 项目状态

项目正在开发中，欢迎贡献代码和提出建议。

## 许可证

MIT License