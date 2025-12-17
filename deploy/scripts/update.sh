#!/bin/bash
# 更新服务（拉取代码、重新构建、重启）

set -e

cd "$(dirname "$0")/../docker"

echo "🔄 开始更新 PolyMetric..."

# 拉取最新代码
echo "📥 拉取最新代码..."
cd ../..
git pull

# 重新构建镜像
echo "🏗️  重新构建镜像..."
cd deploy/docker
docker-compose --env-file ../.env build

# 重启服务
echo "🔄 重启服务..."
docker-compose --env-file ../.env up -d

# 清理旧镜像
echo "🧹 清理旧镜像..."
docker image prune -f

echo "✅ 更新完成！"
docker-compose --env-file ../.env ps
