# PolyMetric 多模态大模型评测平台

![Vue 3](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js)
![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django)
![Celery](https://img.shields.io/badge/Celery-5.4-37814A?logo=celery)
![Redis](https://img.shields.io/badge/Redis-7.0-DC382D?logo=redis)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

PolyMetric 是一个全流程、多维度的 LLM（大语言模型）与多模态模型评测平台。它支持用户上传自定义数据集，对 DeepSeek、Qwen、GLM 等主流模型进行主观、客观及对抗性评测，并生成详细的排行榜与分析报告。

## ✨ 核心特性

*   **多维度评测流水线**
    *   **客观评测 (Objective)**：支持选择题、填空题的自动化准确率计算。
    *   **主观评测 (Subjective)**：基于 LLM-as-a-Judge 或人工评分（1-10分），评估生成质量。
    *   **对抗评测 (Adversarial)**：类似 Chatbot Arena，让两个模型“互搏”，由裁判判决胜负（Win/Tie/Loss）。

*   **全格式数据集支持**
    *   支持 **CSV、JSON、ZIP** 格式上传。
    *   支持 **文本、图像、多模态（图文混合）** 数据集。
    *   **智能分析**：上传时自动调用大模型分析数据集内容，打标“推理”、“代码”、“视觉”等能力维度。

*   **高效复用与去重**
    *   **内容指纹**：基于哈希去重，相同内容仅存储一份。
    *   **结果复用**：智能识别已跑过的模型+数据组合，秒级输出结果，节省 90%+ 的 API 费用与时间。

*   **强大的模型生态**
    *   预置 DeepSeek-R1, Qwen2.5, GLM-4 等 20+ 主流模型。
    *   **生图模型支持**：特别适配 WanX (万相)、CogView、MiniMax-Hailuo 等文生图模型，支持图片结果的直接展示与对比。

*   **异步高并发架构**
    *   后端采用 **Celery + Redis** 消息队列，支持千级并发任务调度。
    *   Nginx 反向代理支持大文件（100MB+）断点续传。

## 🛠️ 技术栈

| 模块 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **Frontend** | Vue 3, Vite, Element Plus | 响应式 SPA，支持 Markdown/Code/Image 渲染 |
| **Backend** | Django 5, DRF | RESTful API，JWT 认证 |
| **Async** | Celery, Redis | 分布式任务队列，支持任务分片与进度追踪 |
| **Database** | PostgreSQL 15 | 高并发关系型存储 |
| **Deploy** | Docker Compose | 六容器编排，一键拉起全套环境 |

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/YourRepo/SE-Project.git
cd SE-Project
```

### 2. 环境配置

我们提供了自动化的环境切换脚本。

```bash
cd deploy/scripts
./switch-env.sh
```
*   选择 `1` (本地开发) 或 `3` (生产服务器)。
*   脚本会自动配置 IP、端口与 CORS 策略。

### 3. 启动服务 (Docker)

确保本地已安装 Docker 和 Docker Compose。

```bash
cd deploy/docker
docker-compose --env-file ../.env up -d --build
```

等待 1-2 分钟，直到所有容器（Frontend, Backend, Celery, DB, Redis, Nginx）启动完毕。

### 4. 数据初始化

首次启动需初始化数据库、管理员账号及预置模型数据：

```bash
docker-compose --env-file ../.env exec backend python init_data.py
```

*   **默认管理员**: `admin` / `admin123456`
*   **访问地址**: `http://127.0.0.1`

## 📂 目录结构

```
SE-Project/
├── PolyMetric/
│   ├── backend/           # Django 后端源码
│   │   ├── apps/          # 业务模块 (datasets, tasks, rankings...)
│   │   └── PolyMetric/    # 项目配置
│   └── frontend/          # Vue3 前端源码
├── deploy/                # 部署相关
│   ├── docker/            # Dockerfile & Compose 文件
│   ├── nginx/             # Nginx 配置
│   └── scripts/           # 运维脚本 (update, switch-env)
└── docs/                  # 详细文档
```

## 🧪 测试

项目包含完整的单元测试与集成测试体系。

```bash
# 运行后端测试
docker-compose --env-file ../.env exec backend pytest
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[MIT License](LICENSE)
