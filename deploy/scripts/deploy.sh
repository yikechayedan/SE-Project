#!/bin/bash
# =========================================
# PolyMetric 一键部署脚本
# =========================================

set -e

echo "🚀 开始部署 PolyMetric..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未找到 Docker，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: 未找到 docker-compose，请先安装 docker-compose"
    exit 1
fi

# 进入 deploy/docker 目录
cd "$(dirname "$0")/../docker"

# 检查 .env 文件
if [ ! -f "../.env" ]; then
    echo "⚠️  未找到 .env 文件，正在从模板创建..."
    cp ../.env.example ../.env
    echo "✅ 已创建 .env 文件，请编辑 deploy/.env 配置后重新运行此脚本"
    exit 0
fi

# 拉取最新代码
echo "📥 拉取最新代码..."
cd ../..
git pull || echo "⚠️  Git pull 失败，继续部署..."

# 构建并启动容器
echo "🏗️  构建 Docker 镜像..."
cd deploy/docker
docker-compose --env-file ../.env build

echo "🚢 启动容器..."
docker-compose --env-file ../.env up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose --env-file ../.env ps

echo ""
echo "✅ 部署完成！"
echo "📊 访问地址："
echo "   - 前端: http://localhost"
echo "   - 后端API: http://localhost:8080/api/"
echo "   - 管理后台: http://localhost:8080/admin/"
echo ""
echo "📝 查看日志: cd deploy/docker && docker-compose logs -f"
echo "🛑 停止服务: cd deploy/docker && docker-compose down"
