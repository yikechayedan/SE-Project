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

echo "Initializing data via Django Shell..."

# 3. 数据初始化（模型 + 用户 + 得分）
python3 manage.py shell <<EOF
import os
from django.utils import timezone
from apps.models.models import My_Model
from apps.rankings.models import ModelDimensionScore
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()

# ==========================================
# Part 1: 大模型数据 (精简去重版)
# ==========================================
models_data = [
    # DeepSeek 系列 (保留推理、通用及多模态核心)
    {"name": "DeepSeek-R1", "company": "DeepSeek", "category": "text", "parameter_size": "671B", "description": "旗舰推理模型", "version": "R1"},
    {"name": "DeepSeek-V3", "company": "DeepSeek", "category": "text", "parameter_size": "671B", "description": "主力通用模型", "version": "V3"},
    {"name": "DeepSeek-OCR", "company": "DeepSeek", "category": "multimodal", "parameter_size": "N/A", "description": "视觉文本识别专家", "version": "OCR"},
    {"name": "QwQ-32B", "company": "DeepSeek", "category": "text", "parameter_size": "32B", "description": "数学与逻辑推理模型", "version": "QwQ"},

    # Alibaba Qwen 系列 (保留各尺寸旗舰及专用模型)
    {"name": "Qwen3-235B-Instruct", "company": "Alibaba", "category": "text", "parameter_size": "235B", "description": "旗舰指令微调模型", "version": "Qwen3"},
    {"name": "Qwen3-235B-Thinking", "company": "Alibaba", "category": "text", "parameter_size": "235B", "description": "旗舰推理增强模型", "version": "Qwen3"},
    {"name": "Qwen-Long", "company": "Alibaba", "category": "text", "parameter_size": "Unknown", "description": "长文本专家", "version": "Long"},
    {"name": "Qwen3-Coder-Plus", "company": "Alibaba", "category": "code", "parameter_size": "Unknown", "description": "代码能力增强模型", "version": "Coder"},
    {"name": "Qwen2.5-VL-72B-Instruct", "company": "Alibaba", "category": "multimodal", "parameter_size": "72B", "description": "顶级视觉语言模型", "version": "2.5-VL"},
    {"name": "Qwen3-VL-235B-Instruct", "company": "Alibaba", "category": "multimodal", "parameter_size": "235B", "description": "Qwen3 旗舰视觉模型", "version": "3-VL"},
    
    # WanX (生图专用)
    {"name": "WanX2.1-T2I-Turbo", "company": "Alibaba", "category": "image", "parameter_size": "Unknown", "description": "万相文生图加速版", "version": "2.1"},
    {"name": "WanX2.1-T2I-Plus", "company": "Alibaba", "category": "image", "parameter_size": "Unknown", "description": "万相文生图旗舰版", "version": "2.1"},

    # Zhipu AI (智谱)
    {"name": "GLM-4-Plus", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "全能旗舰模型", "version": "4-Plus"},
    {"name": "GLM-4-Long", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "超长上下文模型", "version": "4-Long"},
    {"name": "GLM-4-Flash", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "极速低成本模型", "version": "4-Flash"},
    {"name": "GLM-4.5", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "新一代基座模型", "version": "4.5"},
    {"name": "GLM-Z1-Flash", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "推理专用模型", "version": "Z1"},
    {"name": "GLM-4V-Plus", "company": "Zhipu AI", "category": "multimodal", "parameter_size": "Unknown", "description": "旗舰级多模态模型", "version": "4V-Plus"},
    {"name": "GLM-CogView3-Flash", "company": "Zhipu AI", "category": "image", "parameter_size": "Unknown", "description": "快速图像生成模型", "version": "CogView3"},

    # MiniMax
    {"name": "MiniMax-Text-01", "company": "MiniMax", "category": "text", "parameter_size": "456B", "description": "高智能通用模型", "version": "01"},
    {"name": "MiniMax-Hailuo-02", "company": "MiniMax", "category": "image", "parameter_size": "Unknown", "description": "海螺多模态/生图模型", "version": "02"},

    # ByteDance (字节/即梦)
    {"name": "Doubao-Seedream-3.0-T2I", "company": "ByteDance", "category": "image", "parameter_size": "Unknown", "description": "即梦专业文生图", "version": "3.0"},
    {"name": "Doubao-Seedance-1.0-Pro", "company": "ByteDance", "category": "image", "parameter_size": "Unknown", "description": "专业级视频生成模型", "version": "1.0"},

    # Moonshot AI (Kimi)
    {"name": "Kimi-K2", "company": "Moonshot AI", "category": "text", "parameter_size": "Unknown", "description": "Kimi 新一代智能模型", "version": "K2"},

    # Baidu (文心一言)
    {"name": "ERNIE-4.5-Turbo", "company": "Baidu", "category": "text", "parameter_size": "Unknown", "description": "文心最新性能增强版", "version": "4.5-Turbo"},
    {"name": "ERNIE-4.5-Turbo-VL", "company": "Baidu", "category": "multimodal", "parameter_size": "Unknown", "description": "文心最新多模态模型", "version": "4.5-VL"},

    # Baichuan (百川)
    {"name": "Baichuan-M2", "company": "Baichuan", "category": "text", "parameter_size": "Unknown", "description": "百川旗舰通用模型", "version": "M2"},
]

print(f"Cleaning up existing models to avoid duplicates...")
try:
    with transaction.atomic():
        My_Model.objects.all().delete()
except Exception as e:
    print(f"Warning: Failed to clear old data: {e}")

print(f"Inserting {len(models_data)} representative models...")
created_count = 0
for data in models_data:
    try:
        My_Model.objects.create(
            name=data["name"],
            company=data["company"],
            category=data["category"],
            parameter_size=data["parameter_size"],
            description=data["description"],
            version=data["version"],
            release_date=timezone.now().date()
        )
        created_count += 1
    except Exception as e:
        print(f"Error inserting {data['name']}: {e}")
print(f"Successfully inserted {created_count} models.")

# --- Part 2: 用户初始化 ---
print("\nChecking users...")
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print(">>> Superuser 'admin' created.")

# --- Part 3: 得分记录初始化 ---
print("\nInitializing score records...")
models = My_Model.objects.all()
dimensions = ['overall', 'language', 'math', 'code', 'multimodal']
score_count = 0
for model in models:
    for dim in dimensions:
        _, created = ModelDimensionScore.objects.get_or_create(
            model=model,
            dimension=dim,
            defaults={'score': 0.0, 'previous_score': 0.0}
        )
        if created: score_count += 1
print(f"Initialized {score_count} score records.")
EOF

echo "Starting Django Server..."
python3 manage.py runserver 0.0.0.0:8000
