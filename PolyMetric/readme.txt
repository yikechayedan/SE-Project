PolyMetric/
├── frontend/                # 前端项目目录
├── backend/                 # 后端项目目录
├── docker/                  # Docker 部署相关配置
├── docs/                    # 项目文档
│   ├── api-docs/            # API 接口文档
│   └── user-guide/          # 用户使用教程
└── README.md                # 项目说明文档

frontend/
├── public/                  # 静态资源
├── src/
├── package.json             # 项目依赖配置
└── vue.config.js            # Vue 项目配置

backend/
├── PolyMetric/              # 项目主目录
│   ├── __init__.py
│   ├── asgi.py              # ASGI 配置
│   ├── celery.py            # Celery 配置（异步任务）
│   ├── settings.py          # 项目设置
│   ├── urls.py              # 主路由配置
│   └── wsgi.py              # WSGI 配置
├── apps/                    # 应用模块
│   ├── users/               # 用户模块
│   │   ├── __init__.py
│   │   ├── admin.py         # 后台管理配置
│   │   ├── apps.py          # 应用配置
│   │   ├── models.py        # 数据模型（用户、关注关系等）
│   │   ├── serializers.py   # 序列化器（数据格式转换）
│   │   ├── urls.py          # 模块路由
│   │   ├── views.py         # 视图函数/类（接口逻辑）
│   │   └── tests.py         # 测试用例
│   ├── datasets/            # 数据集模块
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py        # 数据集、标签模型
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── tests.py
│   ├── tasks/               # 评估任务模块
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py        # 任务、评测结果模型
│   │   ├── serializers.py
│   │   ├── tasks.py         # Celery 异步任务（评测逻辑）
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── tests.py
│   ├── models/              # 模型模块
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py        # 模型、能力指标模型
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── tests.py
│   └── rankings/            # 排行榜模块
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py        # 排行榜记录模型
│       ├── serializers.py
│       ├── urls.py
│       ├── views.py
│       └── tests.py
├── utils/                   # 工具模块
│   ├── __init__.py
│   ├── auth.py              # 认证工具（JWT 生成、验证）
│   ├── file.py              # 文件处理（上传、下载、格式验证）
│   └── validators.py        # 数据验证工具
├── media/                   # 媒体文件（上传的数据集文件）
├── static/                  # 静态文件（后端管理界面资源）
├── manage.py                # Django 命令行工具
├── requirements.txt         # 项目依赖
└── nginx.conf               # Nginx 配置（高并发处理）