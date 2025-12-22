# SE-Project
多模态大模型能力评测榜单

## 🚀 快速开始

### 本地部署

**方式一：使用快速部署脚本（推荐）**

```bash
# Linux/macOS
./scripts/quick-start.sh

# Windows (推荐使用简化版)
scripts\quick-start-simple.bat

# Windows (原版)
scripts\quick-start.bat
```

**方式二：手动部署**

- [通用本地部署指南](docs/本地部署指南.md)
- [Windows 专用部署指南](docs/Windows部署指南.md)
- [Docker 部署故障排除](docs/Docker部署故障排除.md)
- [Docker 常见错误解决](docs/Docker常见错误解决.md)
- [部署流程详解](docs/部署流程详解.md)
- [终端环境与命令差异](docs/终端环境与命令差异.md)

### 项目结构

```
SE-Project
├─ PolyMetric
│  ├─ backend
│  │  ├─ PolyMetric
│  │  │  ├─ _init_.py
│  │  │  ├─ asgi.py
│  │  │  ├─ celery.py
│  │  │  ├─ settings.py
│  │  │  ├─ urls.py
│  │  │  └─ wsgi.py
│  │  ├─ __init__.py
│  │  ├─ apps
│  │  │  ├─ __init__.py
│  │  │  ├─ datasets
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ admin.py
│  │  │  │  ├─ apps.py
│  │  │  │  ├─ examples
│  │  │  │  │  ├─ logistics_delivery_dataset.json
│  │  │  │  │  └─ user_profile_dataset.json
│  │  │  │  ├─ management
│  │  │  │  │  └─ commands
│  │  │  │  │     └─ import_examples.py
│  │  │  │  ├─ migrations
│  │  │  │  │  ├─ 0001_initial.py
│  │  │  │  │  ├─ 0002_initial.py
│  │  │  │  │  └─ __init__.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ permissions.py
│  │  │  │  ├─ serializers.py
│  │  │  │  ├─ tests.py
│  │  │  │  ├─ urls.py
│  │  │  │  └─ views.py
│  │  │  ├─ models
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ admin.py
│  │  │  │  ├─ apps.py
│  │  │  │  ├─ fixtures
│  │  │  │  │  └─ test_models_data.json
│  │  │  │  ├─ migrations
│  │  │  │  │  ├─ 0001_initial.py
│  │  │  │  │  ├─ 0002_initial.py
│  │  │  │  │  └─ __init__.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ permissions.py
│  │  │  │  ├─ serializers.py
│  │  │  │  ├─ test_key.py
│  │  │  │  ├─ tests.py
│  │  │  │  ├─ urls.py
│  │  │  │  └─ views.py
│  │  │  ├─ rankings
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ admin.py
│  │  │  │  ├─ apps.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ serializers.py
│  │  │  │  ├─ tests.py
│  │  │  │  ├─ urls.py
│  │  │  │  └─ views.py
│  │  │  ├─ tasks
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ admin.py
│  │  │  │  ├─ apps.py
│  │  │  │  ├─ migrations
│  │  │  │  │  ├─ 0001_initial.py
│  │  │  │  │  ├─ 0002_initial.py
│  │  │  │  │  └─ __init__.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ permissions.py
│  │  │  │  ├─ run_logic.py
│  │  │  │  ├─ serializers.py
│  │  │  │  ├─ services.py
│  │  │  │  ├─ task.py
│  │  │  │  ├─ test.http
│  │  │  │  ├─ test2.http
│  │  │  │  ├─ tests.py
│  │  │  │  ├─ urls.py
│  │  │  │  └─ views.py
│  │  │  └─ users
│  │  │     ├─ __init__.py
│  │  │     ├─ admin.py
│  │  │     ├─ apps.py
│  │  │     ├─ migrations
│  │  │     │  ├─ 0001_initial.py
│  │  │     │  ├─ 0002_user_show_followed_datasets_and_more.py
│  │  │     │  └─ __init__.py
│  │  │     ├─ models.py
│  │  │     ├─ serializers.py
│  │  │     ├─ test_avatar_upload.py
│  │  │     ├─ tests.py
│  │  │     ├─ tests2.py
│  │  │     ├─ urls.py
│  │  │     ├─ utils.py
│  │  │     └─ views.py
│  │  ├─ manage.py
│  │  ├─ media
│  │  │  ├─ avatars
│  │  │  │  ├─ 头像.png
│  │  │  │  ├─ 头像_ECkwTWx.png
│  │  │  │  ├─ 头像_HR9PJja.png
│  │  │  │  ├─ 头像_dyr8089.png
│  │  │  │  ├─ 微信图片_20251001154226_11_50.png
│  │  │  │  ├─ 微信图片_20251001154226_11_50_WbtvU1x.png
│  │  │  │  ├─ 微信图片_20251104124450_51_50.png
│  │  │  │  └─ 微信图片_20251201162903_91_50.png
│  │  │  └─ datasets
│  │  │     └─ 2025
│  │  │        └─ 12
│  │  │           ├─ 02
│  │  │           │  ├─ 人脸识别数据集.zip
│  │  │           │  ├─ 医学影像诊断数据集.zip
│  │  │           │  ├─ 猫狗图像分类数据集.zip
│  │  │           │  ├─ 电商评论情感分析数据集.csv
│  │  │           │  └─ 英文新闻摘要数据集.json
│  │  │           ├─ 03
│  │  │           │  ├─ A1.zip
│  │  │           │  └─ test_dataset.json
│  │  │           ├─ 04
│  │  │           │  ├─ book.json
│  │  │           │  ├─ test_dataset.json
│  │  │           │  └─ test_dataset_Vhm4Jzq.json
│  │  │           └─ 10
│  │  │              └─ book.json
│  │  ├─ nginx.conf
│  │  ├─ requirements.txt
│  │  └─ utils
│  │     ├─ __init__.py
│  │     ├─ auth.py
│  │     ├─ file.py
│  │     └─ validators.py
│  ├─ backendstart.txt
│  ├─ dataset-api.txt
│  ├─ frontend
│  │  ├─ package-lock.json
│  │  ├─ package.json
│  │  └─ frontend
│  │     ├─ README.md
│  │     ├─ index.html
│  │     ├─ package-lock.json
│  │     ├─ package.json
│  │     ├─ public
│  │     │  └─ vite.svg
│  │     ├─ src
│  │     │  ├─ App.vue
│  │     │  ├─ api
│  │     │  │  ├─ datasets.js
│  │     │  │  ├─ models.js
│  │     │  │  ├─ request.js
│  │     │  │  ├─ tasks.js
│  │     │  │  └─ users.js
│  │     │  ├─ assets
│  │     │  │  └─ vue.svg
│  │     │  ├─ components
│  │     │  │  ├─ common
│  │     │  │  │  ├─ EvalDialog.vue
│  │     │  │  │  └─ UserPopover.vue
│  │     │  │  ├─ layout
│  │     │  │  │  ├─ Header.vue
│  │     │  │  │  └─ Sidebar.vue
│  │     │  │  └─ profile
│  │     │  │     ├─ FollowContent.vue
│  │     │  │     ├─ MyDatasets.vue
│  │     │  │     └─ MyTasks.vue
│  │     │  ├─ main.js
│  │     │  ├─ router
│  │     │  │  └─ index.js
│  │     │  ├─ style.css
│  │     │  └─ views
│  │     │     ├─ LoggedHome.vue
│  │     │     ├─ UnloggedHome.vue
│  │     │     ├─ auth
│  │     │     │  ├─ ForgetView.vue
│  │     │     │  ├─ LoginView.vue
│  │     │     │  ├─ RegisterView.vue
│  │     │     │  └─ ResetView.vue
│  │     │     ├─ datasets
│  │     │     │  ├─ DatasetSquare.vue
│  │     │     │  ├─ MyDatasetDisplay.vue
│  │     │     │  └─ MyDatasetManage.vue
│  │     │     ├─ evaluation
│  │     │     │  ├─ AdversarialEval.vue
│  │     │     │  ├─ AdversarialResult.vue
│  │     │     │  ├─ EvalReport.vue
│  │     │     │  ├─ EvaluationHall.vue
│  │     │     │  ├─ SubjectResult.vue
│  │     │     │  └─ SubjectiveEval.vue
│  │     │     ├─ models
│  │     │     │  └─ ModelsView.vue
│  │     │     └─ profile
│  │     │        ├─ ProfileEdit.vue
│  │     │        ├─ ProfileView.vue
│  │     │        ├─ UserDatasets.vue
│  │     │        └─ UserProfile.vue
│  │     └─ vite.config.js
│  ├─ git_specification.pdf
│  ├─ models_api.md
│  ├─ need_api.txt
│  ├─ tasks-api.txt
│  └─ 会议文档.txt
├─ README.md
├─ book.json
└─ test_dataset.json

```
```
SE-Project
├─ PolyMetric
│  ├─ backend
│  │  ├─ PolyMetric
│  │  │  ├─ _init_.py
│  │  │  ├─ asgi.py
│  │  │  ├─ celery.py
│  │  │  ├─ settings.py
│  │  │  ├─ urls.py
│  │  │  └─ wsgi.py
│  │  ├─ __init__.py
│  │  ├─ apps
│  │  │  ├─ __init__.py
│  │  │  ├─ datasets
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ admin.py
│  │  │  │  ├─ apps.py
│  │  │  │  ├─ examples
│  │  │  │  │  ├─ logistics_delivery_dataset.json
│  │  │  │  │  └─ user_profile_dataset.json
│  │  │  │  ├─ management
│  │  │  │  │  └─ commands
│  │  │  │  │     └─ import_examples.py
│  │  │  │  ├─ migrations
│  │  │  │  │  ├─ 0001_initial.py
│  │  │  │  │  ├─ 0002_initial.py
│  │  │  │  │  └─ __init__.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ permissions.py
│  │  │  │  ├─ serializers.py
│  │  │  │  ├─ tests.py
│  │  │  │  ├─ urls.py
│  │  │  │  └─ views.py
│  │  │  ├─ models
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ admin.py
│  │  │  │  ├─ apps.py
│  │  │  │  ├─ fixtures
│  │  │  │  │  └─ test_models_data.json
│  │  │  │  ├─ migrations
│  │  │  │  │  ├─ 0001_initial.py
│  │  │  │  │  ├─ 0002_initial.py
│  │  │  │  │  └─ __init__.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ permissions.py
│  │  │  │  ├─ serializers.py
│  │  │  │  ├─ test_key.py
│  │  │  │  ├─ tests.py
│  │  │  │  ├─ urls.py
│  │  │  │  └─ views.py
│  │  │  ├─ rankings
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ admin.py
│  │  │  │  ├─ apps.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ serializers.py
│  │  │  │  ├─ tests.py
│  │  │  │  ├─ urls.py
│  │  │  │  └─ views.py
│  │  │  ├─ tasks
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ admin.py
│  │  │  │  ├─ apps.py
│  │  │  │  ├─ migrations
│  │  │  │  │  ├─ 0001_initial.py
│  │  │  │  │  ├─ 0002_initial.py
│  │  │  │  │  ├─ 0003_alter_evaluationtask_mymodel.py
│  │  │  │  │  └─ __init__.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ permissions.py
│  │  │  │  ├─ run_logic.py
│  │  │  │  ├─ serializers.py
│  │  │  │  ├─ services.py
│  │  │  │  ├─ task.py
│  │  │  │  ├─ test.http
│  │  │  │  ├─ test2.http
│  │  │  │  ├─ tests.py
│  │  │  │  ├─ urls.py
│  │  │  │  └─ views.py
│  │  │  └─ users
│  │  │     ├─ __init__.py
│  │  │     ├─ admin.py
│  │  │     ├─ apps.py
│  │  │     ├─ migrations
│  │  │     │  ├─ 0001_initial.py
│  │  │     │  ├─ 0002_user_show_followed_datasets_and_more.py
│  │  │     │  └─ __init__.py
│  │  │     ├─ models.py
│  │  │     ├─ serializers.py
│  │  │     ├─ test_avatar_upload.py
│  │  │     ├─ tests.py
│  │  │     ├─ tests2.py
│  │  │     ├─ urls.py
│  │  │     ├─ utils.py
│  │  │     └─ views.py
│  │  ├─ manage.py
│  │  ├─ media
│  │  │  ├─ avatars
│  │  │  │  ├─ 头像.png
│  │  │  │  ├─ 头像_ECkwTWx.png
│  │  │  │  ├─ 头像_HR9PJja.png
│  │  │  │  ├─ 头像_dyr8089.png
│  │  │  │  ├─ 微信图片_20251001154226_11_50.png
│  │  │  │  ├─ 微信图片_20251001154226_11_50_WbtvU1x.png
│  │  │  │  ├─ 微信图片_20251104124450_51_50.png
│  │  │  │  └─ 微信图片_20251201162903_91_50.png
│  │  │  └─ datasets
│  │  │     └─ 2025
│  │  │        └─ 12
│  │  │           ├─ 02
│  │  │           │  ├─ 人脸识别数据集.zip
│  │  │           │  ├─ 医学影像诊断数据集.zip
│  │  │           │  ├─ 猫狗图像分类数据集.zip
│  │  │           │  ├─ 电商评论情感分析数据集.csv
│  │  │           │  └─ 英文新闻摘要数据集.json
│  │  │           ├─ 03
│  │  │           │  ├─ A1.zip
│  │  │           │  └─ test_dataset.json
│  │  │           ├─ 04
│  │  │           │  ├─ book.json
│  │  │           │  ├─ test_dataset.json
│  │  │           │  └─ test_dataset_Vhm4Jzq.json
│  │  │           └─ 10
│  │  │              └─ book.json
│  │  ├─ nginx.conf
│  │  ├─ requirements.txt
│  │  └─ utils
│  │     ├─ __init__.py
│  │     ├─ auth.py
│  │     ├─ file.py
│  │     └─ validators.py
│  ├─ backendstart.txt
│  ├─ dataset-api.txt
│  ├─ frontend
│  │  ├─ package-lock.json
│  │  ├─ package.json
│  │  └─ frontend
│  │     ├─ README.md
│  │     ├─ index.html
│  │     ├─ package-lock.json
│  │     ├─ package.json
│  │     ├─ public
│  │     │  └─ vite.svg
│  │     ├─ src
│  │     │  ├─ App.vue
│  │     │  ├─ api
│  │     │  │  ├─ datasets.js
│  │     │  │  ├─ models.js
│  │     │  │  ├─ request.js
│  │     │  │  ├─ tasks.js
│  │     │  │  └─ users.js
│  │     │  ├─ assets
│  │     │  │  └─ vue.svg
│  │     │  ├─ components
│  │     │  │  ├─ common
│  │     │  │  │  ├─ EvalDialog.vue
│  │     │  │  │  └─ UserPopover.vue
│  │     │  │  ├─ layout
│  │     │  │  │  ├─ Header.vue
│  │     │  │  │  └─ Sidebar.vue
│  │     │  │  └─ profile
│  │     │  │     ├─ FollowContent.vue
│  │     │  │     ├─ MyDatasets.vue
│  │     │  │     └─ MyTasks.vue
│  │     │  ├─ main.js
│  │     │  ├─ router
│  │     │  │  └─ index.js
│  │     │  ├─ style.css
│  │     │  └─ views
│  │     │     ├─ LoggedHome.vue
│  │     │     ├─ UnloggedHome.vue
│  │     │     ├─ auth
│  │     │     │  ├─ ForgetView.vue
│  │     │     │  ├─ LoginView.vue
│  │     │     │  ├─ RegisterView.vue
│  │     │     │  └─ ResetView.vue
│  │     │     ├─ datasets
│  │     │     │  ├─ DatasetSquare.vue
│  │     │     │  ├─ MyDatasetDisplay.vue
│  │     │     │  └─ MyDatasetManage.vue
│  │     │     ├─ evaluation
│  │     │     │  ├─ AdversarialEval.vue
│  │     │     │  ├─ AdversarialResult.vue
│  │     │     │  ├─ EvalReport.vue
│  │     │     │  ├─ EvaluationHall.vue
│  │     │     │  ├─ SubjectResult.vue
│  │     │     │  └─ SubjectiveEval.vue
│  │     │     ├─ models
│  │     │     │  └─ ModelsView.vue
│  │     │     └─ profile
│  │     │        ├─ ProfileEdit.vue
│  │     │        ├─ ProfileView.vue
│  │     │        ├─ UserDatasets.vue
│  │     │        └─ UserProfile.vue
│  │     └─ vite.config.js
│  ├─ git_specification.pdf
│  ├─ models_api.md
│  ├─ need_api.txt
│  ├─ tasks-api.txt
│  └─ 会议文档.txt
├─ README.md
├─ book.json
└─ test_dataset.json

```