# 微信问卷系统

微信问卷系统是一个基于Django框架开发的在线问卷系统，支持微信扫码填写、问卷统计分析等功能。

## 项目结构

### 项目根目录
| 文件/目录 | 作用 |
| --- | --- |
| `wechat_survey/` | 项目主目录，包含Django项目配置 |
| `survey/` | 问卷应用目录，包含所有业务逻辑 |
| `nginx/` | Nginx配置目录，包含反向代理和静态文件服务配置 |
| `.git` | Git版本控制目录，存储项目的Git仓库信息 |
| `.venv` | Python虚拟环境目录，存储项目的Python虚拟环境 |
| `.gitignore` | Git忽略文件配置，指定Git需要忽略的文件和目录 |
| `requirements.txt` | Python依赖列表，包含项目所需的所有Python依赖包 |
| `Dockerfile` | Docker镜像构建文件，定义了应用的运行环境 |
| `docker-compose.yml` | Docker Compose配置文件，定义了多容器部署方案 |
| `deploy.sh` | 部署脚本，用于简化Docker容器的管理和操作 |
| `DEPLOYMENT.md` | 部署文档，详细说明项目的Docker部署步骤 |
| `manage.py` | Django项目管理脚本，用于执行各种Django命令 |
| `create_initial_categories.py` | 初始分类创建脚本，用于创建系统初始的问题分类 |
| `create_test_survey.py` | 测试问卷创建脚本，用于创建测试问卷数据 |
| `drop_category_table.py` | 分类表删除脚本，用于删除分类表 |
| `manage_qrcodes.py` | 二维码管理脚本，用于生成和管理问卷的二维码 |
| `test_import.py` | 导入测试脚本，测试数据导入功能 |
| `test_qrcode.py` | 二维码测试脚本，测试二维码生成和扫描功能 |
| `test_survey_display.py` | 问卷展示测试脚本，测试问卷页面的展示效果 |
| `test_survey_submit.py` | 问卷提交测试脚本，测试问卷提交功能 |
| `db.sqlite3` | SQLite数据库文件，存储所有数据（开发环境使用） |
| `qrcode_*.png` | 生成的二维码图片，用于扫码填写问卷 |

### 项目主目录（wechat_survey）
| 文件 | 作用 |
| --- | --- |
| `settings.py` | Django项目设置文件，包含数据库配置、应用配置、中间件配置等 |
| `urls.py` | Django项目URL配置文件，定义了项目的路由规则 |
| `wsgi.py` | WSGI入口文件，用于部署Django应用 |
| `asgi.py` | ASGI入口文件，用于部署支持异步的Django应用 |

### 问卷应用目录（survey）
| 目录/文件 | 作用 |
| --- | --- |
| `admin/` | 包含自定义的Django Admin站点配置和模型管理类 |
| `views/` | 包含所有视图类和函数，按照功能模块拆分 |
| `serializers/` | 包含Django REST Framework序列化器，按照功能模块拆分 |
| `services/` | 包含业务逻辑服务层，封装复杂的业务逻辑 |
| `utils/` | 包含工具函数，提供通用的辅助功能 |
| `management/` | 包含自定义的Django管理命令 |
| `migrations/` | 包含Django数据库迁移文件 |
| `static/` | 包含静态文件，如CSS、JavaScript、图片等 |
| `templates/` | 包含HTML模板文件 |
| `urls.py` | 应用URL配置文件，定义了应用的路由规则 |
| `apps.py` | 应用配置文件，包含应用的元数据 |
| `tests.py` | 应用测试文件，包含单元测试和集成测试 |

### admin目录
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

### models目录
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

### views目录
| 文件 | 作用 |
| --- | --- |
| `__init__.py` | 导入所有视图类和函数，方便统一引用 |
| `api.py` | 包含API视图，如SurveyViewSet、QRCodeViewSet和survey_statistics函数 |
| `survey.py` | 包含问卷相关视图，如SurveyDetailView和SubmitSurveyView |
| `qrcode.py` | 包含二维码相关视图，如QRCodeRedirectView和QRCodeImageView |
| `wechat.py` | 包含微信相关视图，如WeChatAuthView和WeChatCallbackView |

### serializers目录
| 文件 | 作用 |
| --- | --- |
| `__init__.py` | 导入所有序列化器，方便统一引用 |
| `question_serializer.py` | 包含QuestionSerializer，用于序列化Question模型 |
| `survey_serializer.py` | 包含SurveySerializer，用于序列化Survey模型 |
| `answer_serializer.py` | 包含AnswerSerializer，用于序列化Answer模型 |
| `response_serializer.py` | 包含ResponseSerializer，用于序列化Response模型 |
| `qrcode_serializer.py` | 包含QRCodeSerializer，用于序列化QRCode模型 |

### services目录
| 文件 | 作用 |
| --- | --- |
| （待实现） | 包含业务逻辑服务层，封装复杂的业务逻辑 |

### utils目录
| 文件 | 作用 |
| --- | --- |
| （待实现） | 包含工具函数，提供通用的辅助功能 |

### nginx目录
| 文件 | 作用 |
| --- | --- |
| `nginx.conf` | Nginx配置文件，包含静态文件服务、媒体文件服务和Django应用代理配置 |

## 项目根目录文件详解

### 1. 目录

- **.git**: Git版本控制目录，存储项目的Git仓库信息，包括提交历史、分支、标签等
- **.venv**: Python虚拟环境目录，存储项目的Python虚拟环境，包括安装的依赖包
- **nginx**: Nginx配置目录，存储Nginx的配置文件，用于反向代理和静态文件服务
- **survey**: 问卷应用目录，项目的核心应用，包含所有业务逻辑（模型、视图、序列化器等）
- **wechat_survey**: 项目主目录，Django项目的主目录，包含项目配置、URL路由、WSGI入口等

### 2. 配置文件

- **.gitignore**: Git忽略文件配置，指定Git版本控制中需要忽略的文件和目录，如虚拟环境、日志文件等
- **requirements.txt**: Python依赖列表，列出项目所需的所有Python依赖包及其版本，用于安装依赖
- **Dockerfile**: Docker镜像构建文件，定义Docker镜像的构建步骤，包括基础镜像、依赖安装、文件复制等
- **docker-compose.yml**: Docker Compose配置，定义多容器部署方案，包括web、db、nginx三个服务的配置

### 3. 部署相关

- **deploy.sh**: 部署脚本，简化Docker容器的管理和操作，提供deploy、stop、logs等命令
- **DEPLOYMENT.md**: 部署文档，详细说明项目的Docker部署步骤、配置和常用命令

### 4. Django管理文件

- **manage.py**: Django项目管理脚本，用于执行各种Django命令，如创建应用、数据库迁移、启动开发服务器等

### 5. 脚本文件

- **create_initial_categories.py**: 初始分类创建脚本，用于创建系统初始的问题分类
- **create_test_survey.py**: 测试问卷创建脚本，用于创建测试问卷数据，方便开发和测试
- **drop_category_table.py**: 分类表删除脚本，用于删除分类表，通常用于数据库结构调整
- **manage_qrcodes.py**: 二维码管理脚本，用于生成和管理问卷的二维码

### 6. 测试文件

- **test_import.py**: 导入测试脚本，测试数据导入功能
- **test_qrcode.py**: 二维码测试脚本，测试二维码生成和扫描功能
- **test_survey_display.py**: 问卷展示测试脚本，测试问卷页面的展示效果
- **test_survey_submit.py**: 问卷提交测试脚本，测试问卷提交功能

### 7. 数据库文件

- **db.sqlite3**: SQLite数据库文件，项目的SQLite数据库文件，存储所有数据（开发环境使用）

### 8. 其他文件

- **qrcode_*.png**: 生成的二维码图片，系统生成的问卷二维码图片，用于扫码填写问卷

## 部署说明

### 使用Docker部署

1. **启动应用**：
   ```bash
   ./deploy.sh deploy
   ```
   或
   ```bash
   docker-compose up -d
   ```

2. **访问应用**：
   - Django应用：http://localhost:8000
   - Nginx访问：http://localhost

3. **停止应用**：
   ```bash
   ./deploy.sh stop
   ```
   或
   ```bash
   docker-compose down
   ```

4. **执行数据库迁移**：
   ```bash
   ./deploy.sh migrate
   ```
   或
   ```bash
   docker-compose run --rm web python manage.py migrate
   ```

5. **创建超级用户**：
   ```bash
   ./deploy.sh superuser
   ```
   或
   ```bash
   docker-compose run --rm web python manage.py createsuperuser
   ```

6. **收集静态文件**：
   ```bash
   ./deploy.sh collectstatic
   ```
   或
   ```bash
   docker-compose run --rm web python manage.py collectstatic --noinput
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

## 技术栈

- **后端框架**：Django 5.2
- **API框架**：Django REST Framework 3.16.1
- **数据库**：PostgreSQL 15+ / SQLite
- **前端**：HTML, CSS, JavaScript
- **容器化**：Docker, Docker Compose
- **反向代理**：Nginx
- **应用服务器**：uWSGI 2.0.25

## 项目状态

项目正在开发中，欢迎贡献代码和提出建议。

## 许可证

MIT License