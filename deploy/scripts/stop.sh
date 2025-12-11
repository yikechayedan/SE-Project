#!/bin/bash
# 停止所有服务

cd "$(dirname "$0")/../docker"

echo "🛑 停止 PolyMetric 服务..."
docker-compose --env-file ../.env down

echo "✅ 服务已停止"
