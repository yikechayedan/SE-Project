#!/bin/bash

# 环境切换脚本 - 快速在本地和服务器配置间切换

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  环境配置切换工具${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 显示当前配置
if [ -f "$DEPLOY_DIR/.env" ]; then
    CURRENT_IP=$(grep "^SERVER_IP=" "$DEPLOY_DIR/.env" | cut -d'=' -f2)
    echo -e "当前配置: ${YELLOW}SERVER_IP=$CURRENT_IP${NC}"
    echo ""
fi

echo "请选择要切换的环境:"
echo "  1) 本地开发 (127.0.0.1)"
echo "  2) 测试服务器 (49.232.40.152)"
echo "  3) 生产服务器 (124.220.26.26)"
echo "  4) 自定义 IP"
echo "  5) 从 .env.example 重置"
echo ""
read -p "请输入选项 [1-5]: " choice

case $choice in
    1)
        NEW_IP="127.0.0.1"
        ENV_NAME="本地开发"
        ;;
    2)
        NEW_IP="49.232.40.152"
        ENV_NAME="测试服务器"
        ;;
    3)
        NEW_IP="124.220.26.26"
        ENV_NAME="生产服务器"
        ;;
    4)
        read -p "请输入服务器 IP 或域名: " NEW_IP
        ENV_NAME="自定义"
        ;;
    5)
        if [ -f "$DEPLOY_DIR/.env.example" ]; then
            cp "$DEPLOY_DIR/.env.example" "$DEPLOY_DIR/.env"
            echo -e "${GREEN}✓ 已从 .env.example 重置配置${NC}"
            exit 0
        else
            echo -e "${RED}❌ 未找到 .env.example 文件${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}无效的选项${NC}"
        exit 1
        ;;
esac

# 备份当前配置
if [ -f "$DEPLOY_DIR/.env" ]; then
    BACKUP_FILE="$DEPLOY_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$DEPLOY_DIR/.env" "$BACKUP_FILE"
    echo -e "${BLUE}已备份当前配置到: $BACKUP_FILE${NC}"
fi

# 更新 SERVER_IP
if [ -f "$DEPLOY_DIR/.env" ]; then
    sed -i "s/^SERVER_IP=.*/SERVER_IP=$NEW_IP/" "$DEPLOY_DIR/.env"
else
    if [ -f "$DEPLOY_DIR/.env.example" ]; then
        cp "$DEPLOY_DIR/.env.example" "$DEPLOY_DIR/.env"
        sed -i "s/^SERVER_IP=.*/SERVER_IP=$NEW_IP/" "$DEPLOY_DIR/.env"
    else
        echo -e "${RED}❌ 未找到配置文件${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}✓ 已切换到: $ENV_NAME${NC}"
echo -e "${GREEN}✓ SERVER_IP=$NEW_IP${NC}"
echo ""

# 更新 CORS 和 ALLOWED_HOSTS
sed -i "s/^ALLOWED_HOSTS=.*/ALLOWED_HOSTS=localhost,127.0.0.1,$NEW_IP/" "$DEPLOY_DIR/.env"
sed -i "s/^CORS_ALLOWED_ORIGINS=.*/CORS_ALLOWED_ORIGINS=http:\/\/localhost,http:\/\/$NEW_IP/" "$DEPLOY_DIR/.env"

echo -e "${YELLOW}提示: 配置已更新，需要重新构建容器才能生效${NC}"
echo ""
echo "重新部署命令:"
echo -e "  ${BLUE}cd $DEPLOY_DIR/docker${NC}"
echo -e "  ${BLUE}sudo docker-compose down${NC}"
echo -e "  ${BLUE}sudo docker-compose build${NC}"
echo -e "  ${BLUE}sudo docker-compose up -d${NC}"
echo ""

read -p "是否立即重新部署？(y/N): " deploy_now
if [[ $deploy_now =~ ^[Yy]$ ]]; then
    cd "$DEPLOY_DIR/docker"
    echo -e "${YELLOW}停止服务...${NC}"
    sudo docker-compose down
    echo -e "${YELLOW}重新构建...${NC}"
    sudo docker-compose build
    echo -e "${YELLOW}启动服务...${NC}"
    sudo docker-compose up -d
    echo -e "${GREEN}✓ 部署完成！${NC}"
fi
