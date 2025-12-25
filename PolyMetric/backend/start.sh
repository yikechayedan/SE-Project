#!/bin/bash
set -e

# 确保进入脚本所在目录
cd "$(dirname "$0")"

echo "Creating database migrations..."
# 1. 强制为核心应用生成初始迁移
python3 manage.py makemigrations system rankings models datasets tasks users comments

echo "Applying database migrations..."
# 2. 应用所有迁移
python3 manage.py migrate

echo "Initializing data via init_data.py..."
# 3. 使用统一的初始化脚本（包含正确的官方模型名称和初始分）
if [ -f "init_data.py" ]; then
    python3 init_data.py
else
    echo "Warning: init_data.py not found, skipping data initialization."
fi

echo "Starting Django Server..."
python3 manage.py runserver 0.0.0.0:8000