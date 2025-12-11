#!/bin/bash
# =========================================
# PolyMetric 一键部署脚本 (增强版)
# =========================================

set -e

echo "🚀 开始部署 PolyMetric..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 Docker 是否安装
echo "📦 检查环境依赖..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 Docker，请先安装 Docker${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 docker-compose，请先安装 docker-compose${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker 版本: $(docker --version)${NC}"
echo -e "${GREEN}✓ Docker Compose 版本: $(docker-compose --version)${NC}"
echo ""

# 进入 deploy/docker 目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../docker"

# 检查 .env 文件
if [ ! -f "../.env" ]; then
    echo -e "${YELLOW}⚠️  未找到 .env 文件，正在从模板创建...${NC}"
    if [ -f "../.env.example" ]; then
        cp ../.env.example ../.env
        echo -e "${GREEN}✅ 已创建 .env 文件${NC}"
    else
        echo -e "${RED}❌ 错误: .env.example 文件不存在${NC}"
        exit 1
    fi
    echo ""
    echo -e "${YELLOW}📝 请编辑 deploy/.env 配置以下必填项：${NC}"
    echo "   - SECRET_KEY (Django 密钥)"
    echo "   - DB_PASSWORD (数据库密码)"
    echo "   - REDIS_PASSWORD (Redis 密码)"
    echo "   - SERVER_IP (服务器 IP 地址)"
    echo ""
    echo "编辑完成后，重新运行此脚本"
    exit 0
fi

# 检查必填配置项
echo "🔍 检查配置文件..."
source ../.env

MISSING_VARS=()

if [[ -z "$SECRET_KEY" || "$SECRET_KEY" == "your-secret-key-here" ]]; then
    MISSING_VARS+=("SECRET_KEY")
fi

if [[ -z "$DB_PASSWORD" || "$DB_PASSWORD" == "your-db-password" ]]; then
    MISSING_VARS+=("DB_PASSWORD")
fi

if [[ -z "$REDIS_PASSWORD" || "$REDIS_PASSWORD" == "your-redis-password" ]]; then
    MISSING_VARS+=("REDIS_PASSWORD")
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}❌ 错误: 以下配置项未设置或使用了默认值：${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "请编辑 deploy/.env 文件并设置正确的值"
    exit 1
fi

echo -e "${GREEN}✓ 配置检查通过${NC}"
echo ""

# 拉取最新代码（可选）
if command -v git &> /dev/null; then
    echo "📥 拉取最新代码..."
    cd ../..
    if git rev-parse --git-dir > /dev/null 2>&1; then
        git pull || echo -e "${YELLOW}⚠️  Git pull 失败，继续部署...${NC}"
    else
        echo -e "${YELLOW}⚠️  不是 Git 仓库，跳过代码更新${NC}"
    fi
    cd deploy/docker
    echo ""
fi

# 停止旧容器
echo "🛑 停止旧容器..."
docker-compose --env-file ../.env down 2>/dev/null || true
echo ""

# 构建 Docker 镜像
echo "🏗️  构建 Docker 镜像（这可能需要 5-10 分钟）..."
echo -e "${YELLOW}提示: 首次构建会下载基础镜像，请耐心等待${NC}"
docker-compose --env-file ../.env build --no-cache
echo ""

# 启动容器
echo "🚢 启动容器..."
docker-compose --env-file ../.env up -d
echo ""

# 等待服务启动
echo "⏳ 等待服务启动（30 秒）..."
for i in {30..1}; do
    echo -ne "\r   倒计时: ${i} 秒 "
    sleep 1
done
echo ""
echo ""

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose --env-file ../.env ps
echo ""

# 检查健康状态
echo "🏥 检查容器健康状态..."
UNHEALTHY=$(docker-compose --env-file ../.env ps | grep -i "unhealthy" || true)
if [ -n "$UNHEALTHY" ]; then
    echo -e "${RED}⚠️  警告: 部分容器不健康${NC}"
    echo "$UNHEALTHY"
    echo ""
    echo "请检查日志: docker-compose logs [service-name]"
else
    echo -e "${GREEN}✓ 所有容器运行正常${NC}"
fi
echo ""

# 显示访问地址
echo -e "${GREEN}✅ 部署完成！${NC}"
echo ""
echo "📊 访问地址："
if [ -n "$SERVER_IP" ]; then
    echo "   - 前端页面: http://${SERVER_IP}"
    echo "   - 后端 API: http://${SERVER_IP}:${HTTP_PORT:-8080}/api/"
    echo "   - 管理后台: http://${SERVER_IP}:${HTTP_PORT:-8080}/admin/"
else
    echo "   - 前端页面: http://localhost"
    echo "   - 后端 API: http://localhost:${HTTP_PORT:-8080}/api/"
    echo "   - 管理后台: http://localhost:${HTTP_PORT:-8080}/admin/"
fi
echo ""
echo "📝 常用命令："
echo "   - 查看日志: cd deploy/docker && docker-compose logs -f"
echo "   - 停止服务: cd deploy && bash scripts/stop.sh"
echo "   - 重启服务: cd deploy && bash scripts/start.sh"
echo "   - 更新代码: cd deploy && bash scripts/update.sh"
echo ""
