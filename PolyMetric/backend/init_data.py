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
# Part 1: 大模型数据 (具有显著差异的初始分)
# ==========================================
# 评分逻辑：
# S级 (95+): 行业顶级突破 (如 DeepSeek-R1 的推理)
# A级 (90-94): 旗舰级水平 (如 Qwen3, GLM-4-Plus)
# B级 (85-89): 主流高性能 (如 MiniMax, Kimi-K2)
# C级 (75-84): 轻量级或上一代 (如 Flash版)
# 专用型: 在特定维度 (如 multimodal) 极高，其他维度较低
models_data = [
    # --- DeepSeek: 当前技术风向标 ---
    {
        "name": "DeepSeek-R1", "company": "DeepSeek", "category": "text", "parameter_size": "671B", "description": "旗舰推理模型，强化学习驱动，逻辑思维极强", "version": "R1",
        "scores": {"overall": 96.8, "language": 94.5, "math": 99.2, "code": 97.5, "multimodal": 85.0}
    },
    {
        "name": "DeepSeek-V3", "company": "DeepSeek", "category": "text", "parameter_size": "671B", "description": "MoE 架构旗舰模型，综合性能与性价比之王", "version": "V3",
        "scores": {"overall": 94.2, "language": 96.5, "math": 91.8, "code": 92.5, "multimodal": 82.0}
    },
    {
        "name": "QwQ-32B", "company": "DeepSeek", "category": "text", "parameter_size": "32B", "description": "专注数学与逻辑推理的中型模型", "version": "QwQ",
        "scores": {"overall": 85.5, "language": 82.0, "math": 94.0, "code": 88.5, "multimodal": 60.0}
    },

    # --- Alibaba Qwen: 全能生态位 ---
    {
        "name": "Qwen3-235B-Instruct", "company": "Alibaba", "category": "text", "parameter_size": "235B", "description": "阿里的新一代旗舰，指令遵循能力极强", "version": "Qwen3",
        "scores": {"overall": 93.5, "language": 95.0, "math": 91.0, "code": 90.5, "multimodal": 84.0}
    },
    {
        "name": "Qwen3-Coder-Plus", "company": "Alibaba", "category": "code", "parameter_size": "Unknown", "description": "代码专家模型，甚至超越部分通用旗舰", "version": "Coder",
        "scores": {"overall": 90.0, "language": 84.0, "math": 92.0, "code": 98.2, "multimodal": 65.0}
    },
    {
        "name": "Qwen2.5-VL-72B-Instruct", "company": "Alibaba", "category": "multimodal", "parameter_size": "72B", "description": "视频、图像理解能力顶级", "version": "2.5-VL",
        "scores": {"overall": 91.5, "language": 88.0, "math": 86.5, "code": 83.0, "multimodal": 97.8}
    },

    # --- Zhipu AI: 国内最早的基座之一 ---
    {
        "name": "GLM-4-Plus", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "智谱全能旗舰，中文语境理解深厚", "version": "4-Plus",
        "scores": {"overall": 92.0, "language": 94.8, "math": 89.5, "code": 88.0, "multimodal": 87.0}
    },
    {
        "name": "GLM-4-Flash", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "毫秒级响应，适合简单高频任务", "version": "4-Flash",
        "scores": {"overall": 79.5, "language": 82.0, "math": 74.0, "code": 75.5, "multimodal": 68.0}
    },

    # --- ByteDance / MiniMax: 后发制人 ---
    {
        "name": "Doubao-Seedream-3.0-T2I", "company": "ByteDance", "category": "image", "parameter_size": "Unknown", "description": "即梦文生图旗舰，审美与构图极佳", "version": "3.0",
        "scores": {"overall": 88.5, "language": 72.0, "math": 55.0, "code": 50.0, "multimodal": 96.5}
    },
    {
        "name": "MiniMax-Text-01", "company": "MiniMax", "category": "text", "parameter_size": "456B", "description": "超大规模模型，语言风格自然生动", "version": "01",
        "scores": {"overall": 90.8, "language": 93.5, "math": 86.0, "code": 85.0, "multimodal": 78.0}
    },

    # --- Moonshot / Baidu: 特色领域 ---
    {
        "name": "Kimi-K2", "company": "Moonshot AI", "category": "text", "parameter_size": "Unknown", "description": "超长上下文领军者，多文件分析王者", "version": "K2",
        "scores": {"overall": 91.2, "language": 95.5, "math": 85.5, "code": 87.0, "multimodal": 75.0}
    },
    {
        "name": "ERNIE-4.5-Turbo", "company": "Baidu", "category": "text", "parameter_size": "Unknown", "description": "文心一言最新版，知识覆盖面极广", "version": "4.5-Turbo",
        "scores": {"overall": 89.5, "language": 92.8, "math": 87.0, "code": 84.5, "multimodal": 80.0}
    },
    
    # --- 专用/多模态专家 ---
    {
        "name": "WanX2.1-T2I-Plus", "company": "Alibaba", "category": "image", "parameter_size": "Unknown", "description": "阿里的万相生图，写实与风格化兼备", "version": "2.1",
        "scores": {"overall": 87.8, "language": 70.0, "math": 50.0, "code": 45.0, "multimodal": 95.8}
    },
    {
        "name": "DeepSeek-OCR", "company": "DeepSeek", "category": "multimodal", "parameter_size": "N/A", "description": "极致的文本提取与文档理解", "version": "OCR",
        "scores": {"overall": 86.5, "language": 85.0, "math": 70.0, "code": 65.0, "multimodal": 98.5}
    },
    {
        "name": "GLM-4V-Plus", "company": "Zhipu AI", "category": "multimodal", "parameter_size": "Unknown", "description": "智谱多模态旗舰，视频理解出色", "version": "4V-Plus",
        "scores": {"overall": 90.2, "language": 89.0, "math": 83.5, "code": 81.0, "multimodal": 95.2}
    },
]

print(f"Cleaning up existing models to avoid duplicates...")
try:
    with transaction.atomic():
        # 清除模型，级联删除评分
        My_Model.objects.all().delete()
except Exception as e:
    print(f"Warning: Failed to clear old data: {e}")

print(f"Inserting {len(models_data)} models with differentiated expert scores...")
created_count = 0
score_created_count = 0

for data in models_data:
    try:
        # 1. 创建模型
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

        # 2. 创建评分记录 (根据预设的分数差异)
        scores = data.get("scores", {})
        dimensions = ['overall', 'language', 'math', 'code', 'multimodal']
        
        for dim in dimensions:
            initial_score = scores.get(dim, 60.0) # 默认 60 兜底
            
            ModelDimensionScore.objects.create(
                model=model,
                dimension=dim,
                score=initial_score,
                previous_score=initial_score
            )
            score_created_count += 1
            
    except Exception as e:
        print(f"Error inserting {data['name']}: {e}")

print(f"Successfully inserted {created_count} models and {score_created_count} scores.")

# --- Part 2: 用户初始化 ---
print("\nChecking superuser...")
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print(">>> Superuser 'admin' created (PW: admin123456).")
else:
    print(">>> Superuser 'admin' already exists.")
