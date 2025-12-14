# PolyMetric 部署文档

## 📋 目录结构

```
deploy/
├── docker/                    # Docker 相关文件
│   ├── Dockerfile.backend    # 后端镜像定义
│   ├── Dockerfile.frontend   # 前端镜像定义
│   ├── docker-compose.yml    # 容器编排配置
│   └── .dockerignore         # Docker 构建忽略文件
├── nginx/                     # Nginx 配置
│   ├── nginx.conf            # Nginx 主配置
│   ├── backend.conf          # 后端反向代理配置
│   └── frontend.conf         # 前端服务配置
├── scripts/                   # 部署脚本
│   ├── deploy.sh             # 一键部署脚本
│   ├── start.sh              # 启动服务
│   ├── stop.sh               # 停止服务
│   └── update.sh             # 更新服务
├── .env.example              # 环境变量模板
└── DEPLOY.md                 # 本文档
```

## 🚀 快速部署

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- Git

### 部署步骤

1. **配置环境变量**
```bash
cd deploy
cp .env.example .env
# 编辑 .env 文件，修改数据库密码、SECRET_KEY 等
vim .env
```

2. **一键部署**
```bash
bash scripts/deploy.sh
```

3. **访问服务**
- 前端: http://your-server-ip
- 后端API: http://your-server-ip:8080/api/
- 管理后台: http://your-server-ip:8080/admin/

## 📦 服务组件

### 容器列表

- **polymetric-db**: PostgreSQL 15 数据库
- **polymetric-redis**: Redis 7 缓存
- **polymetric-backend**: Django 后端应用
- **polymetric-celery-worker**: Celery 异步任务
- **polymetric-frontend**: Vue 前端应用
- **polymetric-nginx**: Nginx 反向代理

### 端口映射

- **80**: 前端静态页面
- **8080**: 后端 API (通过 Nginx 代理)
- **8443**: HTTPS (需配置 SSL 证书)

## 🛠️ 日常运维

### 查看日志
```bash
cd deploy/docker
docker-compose logs -f                    # 所有服务
docker-compose logs -f backend            # 后端日志
docker-compose logs -f frontend           # 前端日志
docker-compose logs -f celery-worker      # Celery 日志
```

### 启动/停止服务
```bash
cd deploy
bash scripts/start.sh     # 启动
bash scripts/stop.sh      # 停止
bash scripts/update.sh    # 更新
```

### 进入容器
```bash
docker exec -it polymetric-backend bash   # 后端容器
docker exec -it polymetric-db psql -U polymetric_user -d polymetric  # 数据库
```

### 数据库备份
```bash
docker exec polymetric-db pg_dump -U polymetric_user polymetric > backup_$(date +%Y%m%d).sql
```

### 数据库恢复
```bash
cat backup_20250101.sql | docker exec -i polymetric-db psql -U polymetric_user polymetric
```

## 🔧 配置说明

### Django Settings 修改

生产环境需要修改 `PolyMetric/backend/PolyMetric/settings.py`:

```python
# 从环境变量读取配置
import os
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='polymetric'),
        'USER': config('DB_USER', default='polymetric_user'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='db'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Redis 配置
CELERY_BROKER_URL = f"redis://:{config('REDIS_PASSWORD')}@{config('REDIS_HOST')}:6379/0"
```

### 前端 API 地址修改

修改 `PolyMetric/frontend/src/api/request.js`:

```javascript
const service = axios.create({
  baseURL: process.env.VUE_APP_API_URL || "http://your-domain.com:8080",
  timeout: 5000
});
```

## 🔒 安全建议

1. **修改默认密码**: 务必修改 `.env` 中的所有密码
2. **启用 HTTPS**: 配置 SSL 证书（Let's Encrypt 免费）
3. **防火墙**: 仅开放 80, 443 端口
4. **定期备份**: 设置自动备份数据库和媒体文件
5. **日志监控**: 使用 ELK 或 Grafana 监控日志

## 📊 性能优化

- **Nginx 缓存**: 已配置静态资源缓存
- **Gzip 压缩**: 已启用
- **数据库连接池**: 使用 pgbouncer
- **CDN**: 可将静态资源上传到 CDN

## ❓ 常见问题

### Q: 容器启动失败
A: 检查端口占用 `netstat -tlnp | grep :8080`

### Q: 数据库连接失败
A: 检查 `.env` 中的数据库配置是否正确

### Q: 前端无法访问后端 API
A: 检查 CORS 配置和 Nginx 反向代理设置

## 📞 技术支持

遇到问题请提交 Issue: https://github.com/your-repo/issues
