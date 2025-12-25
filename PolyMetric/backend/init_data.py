import os
import django

# 设置 Django 环境，以便独立运行
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.settings')
django.setup()

from django.utils import timezone
from apps.models.models import My_Model
from apps.rankings.models import ModelDimensionScore
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()

# ==========================================
# Part 1: 官方大模型数据 (严格子集 & 差异化初始分)
# ==========================================
models_data = [
    # --- DeepSeek 系列 ---
    {
        "name": "DeepSeek-R1", "company": "DeepSeek", "category": "text", "parameter_size": "671B", "description": "旗舰推理模型", "version": "R1",
        "scores": {"overall": 97.5, "language": 94.8, "math": 99.5, "code": 98.5, "multimodal": 86.0}
    },
    {
        "name": "DeepSeek-V3.2", "company": "DeepSeek", "category": "text", "parameter_size": "671B", "description": "最新一代通用旗舰", "version": "V3.2",
        "scores": {"overall": 96.5, "language": 97.8, "math": 93.5, "code": 94.0, "multimodal": 88.0}
    },
    {
        "name": "DeepSeek-V3.2-Thinking", "company": "DeepSeek", "category": "text", "parameter_size": "671B", "description": "旗舰推理增强版", "version": "V3.2",
        "scores": {"overall": 96.0, "language": 93.5, "math": 98.5, "code": 97.0, "multimodal": 84.0}
    },
    {
        "name": "DeepSeek-OCR", "company": "DeepSeek", "category": "multimodal", "parameter_size": "N/A", "description": "视觉文本识别专家", "version": "OCR",
        "scores": {"overall": 88.5, "language": 85.0, "math": 75.0, "code": 70.0, "multimodal": 99.2}
    },
    {
        "name": "QwQ-32B", "company": "DeepSeek", "category": "text", "parameter_size": "32B", "description": "数学与逻辑推理模型", "version": "QwQ",
        "scores": {"overall": 86.8, "language": 82.0, "math": 95.8, "code": 90.0, "multimodal": 62.0}
    },

    # --- Qwen 系列 ---
    {
        "name": "Qwen3-Coder-480B-A35B-Instruct", "company": "Alibaba", "category": "code", "parameter_size": "480B", "description": "顶级代码专家", "version": "Qwen3",
        "scores": {"overall": 95.8, "language": 92.5, "math": 95.0, "code": 99.5, "multimodal": 80.0}
    },
    {
        "name": "Qwen3-235B-A22B-Instruct-2507", "company": "Alibaba", "category": "text", "parameter_size": "235B", "description": "旗舰指令微调", "version": "Qwen3",
        "scores": {"overall": 96.0, "language": 97.2, "math": 93.8, "code": 93.5, "multimodal": 85.0}
    },
    {
        "name": "Qwen3-235B-A22B-Thinking-2507", "company": "Alibaba", "category": "text", "parameter_size": "235B", "description": "旗舰推理模型", "version": "Qwen3",
        "scores": {"overall": 95.5, "language": 94.0, "math": 98.6, "code": 96.2, "multimodal": 83.0}
    },
    {
        "name": "Qwen3-VL-235B-A22B-Instruct", "company": "Alibaba", "category": "multimodal", "parameter_size": "235B", "description": "旗舰视觉模型", "version": "Qwen3",
        "scores": {"overall": 95.2, "language": 92.8, "math": 91.5, "code": 89.5, "multimodal": 98.8}
    },
    {
        "name": "Qwen-Long", "company": "Alibaba", "category": "text", "parameter_size": "Unknown", "description": "长文本深度优化", "version": "Long",
        "scores": {"overall": 89.5, "language": 96.8, "math": 84.5, "code": 82.0, "multimodal": 72.0}
    },

    # --- GLM 系列 ---
    {
        "name": "GLM-4.6", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "最新全能旗舰", "version": "4.6",
        "scores": {"overall": 96.6, "language": 98.0, "math": 93.5, "code": 94.5, "multimodal": 90.0}
    },
    {
        "name": "GLM-4.5", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "高性能基座旗舰", "version": "4.5",
        "scores": {"overall": 95.0, "language": 96.5, "math": 92.0, "code": 91.8, "multimodal": 88.0}
    },
    {
        "name": "GLM-4V-Plus-0111", "company": "Zhipu AI", "category": "multimodal", "parameter_size": "Unknown", "description": "视觉旗舰模型", "version": "4V",
        "scores": {"overall": 91.8, "language": 90.0, "math": 85.8, "code": 83.0, "multimodal": 96.8}
    },
    {
        "name": "GLM-Z1-Flash", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "极速推理版", "version": "Z1",
        "scores": {"overall": 83.8, "language": 80.0, "math": 93.5, "code": 87.8, "multimodal": 62.0}
    },

    # --- 生图模型 (T2I) ---
    {
        "name": "WanX2.1-T2I-Plus", "company": "Alibaba", "category": "image", "parameter_size": "Unknown", "description": "万相生图旗舰版", "version": "2.1",
        "scores": {"overall": 88.8, "language": 73.5, "math": 53.5, "code": 48.5, "multimodal": 97.5}
    },
    {
        "name": "WanX2.1-T2I-Turbo", "company": "Alibaba", "category": "image", "parameter_size": "Unknown", "description": "万相生图加速版", "version": "2.1",
        "scores": {"overall": 84.5, "language": 71.0, "math": 51.0, "code": 46.0, "multimodal": 93.0}
    },
    {
        "name": "Doubao-Seedream-3.0-T2I", "company": "ByteDance", "category": "image", "parameter_size": "Unknown", "description": "即梦专业生图旗舰", "version": "3.0",
        "scores": {"overall": 88.5, "language": 74.5, "math": 55.5, "code": 50.5, "multimodal": 97.8}
    },
    {
        "name": "GLM-CogView3-Flash", "company": "Zhipu AI", "category": "image", "parameter_size": "Unknown", "description": "快速图像生成模型", "version": "CogView3",
        "scores": {"overall": 82.8, "language": 70.5, "math": 50.5, "code": 45.5, "multimodal": 93.8}
    },

    # --- 其他核心 ---
    {
        "name": "Kimi-K2", "company": "Moonshot AI", "category": "text", "parameter_size": "Unknown", "description": "智能旗舰", "version": "K2",
        "scores": {"overall": 93.0, "language": 97.5, "math": 89.0, "code": 91.0, "multimodal": 82.0}
    },
    {
        "name": "ERNIE-4.5-Turbo-128K", "company": "Baidu", "category": "text", "parameter_size": "Unknown", "description": "长文本增强旗舰", "version": "4.5",
        "scores": {"overall": 91.0, "language": 94.5, "math": 88.8, "code": 87.5, "multimodal": 81.8}
    },
    {
        "name": "Baichuan-M2-128K", "company": "Baichuan", "category": "text", "parameter_size": "Unknown", "description": "最新通用旗舰", "version": "M2",
        "scores": {"overall": 89.5, "language": 93.5, "math": 85.8, "code": 84.5, "multimodal": 76.8}
    },
    {
        "name": "MiniMax-Text-01", "company": "MiniMax", "category": "text", "parameter_size": "456B", "description": "高智能文本旗舰", "version": "01",
        "scores": {"overall": 92.2, "language": 95.0, "math": 87.8, "code": 86.8, "multimodal": 80.5}
    },
]

print(f"Cleaning up existing models to avoid duplicates...")
try:
    with transaction.atomic():
        My_Model.objects.all().delete()
except Exception as e:
    print(f"Warning: Failed to clear old data: {e}")

print(f"Inserting {len(models_data)} official subset models with calibrated scores...")
created_count = 0
score_created_count = 0

for data in models_data:
    try:
        model = My_Model.objects.create(
            name=data["name"],
            company=data["company"],
            category=data["category"],
            parameter_size=data["parameter_size"],
            description=data["description"],
            version=data["version"],
            release_date=timezone.now().date()
        )
        created_count += 1

        scores = data.get("scores", {})
        dimensions = ['overall', 'language', 'math', 'code', 'multimodal']
        
        for dim in dimensions:
            initial_score = scores.get(dim, 65.0) 
            
            ModelDimensionScore.objects.create(
                model=model,
                dimension=dim,
                score=initial_score,
                previous_score=initial_score
            )
            score_created_count += 1
            
    except Exception as e:
        print(f"Error inserting {data['name']}: {e}")

print(f"Successfully updated {created_count} official models.")

# --- Part 2: 用户初始化 ---
print("\nChecking superuser...")
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print(">>> Superuser 'admin' created.")
else:
    print(">>> Superuser 'admin' already exists.")
