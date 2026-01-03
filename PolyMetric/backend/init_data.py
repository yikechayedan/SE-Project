import os
import django
import random

# 设置 Django 环境，以便独立运行
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.settings')
django.setup()

from django.utils import timezone
from apps.models.models import My_Model
from apps.rankings.models import ModelDimensionScore
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models import Avg

User = get_user_model()

# ==========================================
# Part 1: 大模型数据 (包含更合理的预设初始分数范围)
# ==========================================
# score_range: (min, max) 用于生成随机初始分，模拟真实榜单
models_data = [
    # DeepSeek 系列
    {
        "name": "DeepSeek-R1", "company": "DeepSeek", "category": "text", "parameter_size": "671B", "description": "旗舰推理模型", "version": "R1",
        "score_base": 95.0  # 基准分
    },
    {
        "name": "DeepSeek-V3.2", "company": "DeepSeek", "category": "text", "parameter_size": "671B", "description": "主力通用模型", "version": "V3.2",
        "score_base": 92.0
    },
    {
        "name": "DeepSeek-OCR", "company": "DeepSeek", "category": "multimodal", "parameter_size": "N/A", "description": "视觉文本识别专家", "version": "OCR",
        "score_base": 88.0
    },
    {
        "name": "QwQ-32B", "company": "DeepSeek", "category": "text", "parameter_size": "32B", "description": "数学与逻辑推理模型", "version": "QwQ",
        "score_base": 85.0
    },

    # Alibaba Qwen 系列
    {
        "name": "Qwen3-235B-A22B-Instruct-2507", "company": "Alibaba", "category": "text", "parameter_size": "235B", "description": "旗舰指令微调模型", "version": "Qwen3",
        "score_base": 94.0
    },
    {
        "name": "Qwen3-235B-A22B-Thinking-2507", "company": "Alibaba", "category": "text", "parameter_size": "235B", "description": "旗舰推理增强模型", "version": "Qwen3",
        "score_base": 93.5
    },
    {
        "name": "Qwen-Long", "company": "Alibaba", "category": "text", "parameter_size": "Unknown", "description": "长文本专家", "version": "Long",
        "score_base": 90.0
    },
    {
        "name": "Qwen3-Coder-Plus", "company": "Alibaba", "category": "text", "parameter_size": "Unknown", "description": "代码能力增强模型", "version": "Coder",
        "score_base": 92.0
    },
    {
        "name": "Qwen2.5-VL-72B-Instruct", "company": "Alibaba", "category": "multimodal", "parameter_size": "72B", "description": "顶级视觉语言模型", "version": "2.5-VL",
        "score_base": 91.0
    },
    {
        "name": "Qwen3-VL-235B-A22B-Instruct", "company": "Alibaba", "category": "multimodal", "parameter_size": "235B", "description": "Qwen3 旗舰视觉模型", "version": "3-VL",
        "score_base": 93.0
    },
    
    # WanX (生图专用)
    {
        "name": "WanX2.1-T2I-Turbo", "company": "Alibaba", "category": "image", "parameter_size": "Unknown", "description": "万相文生图加速版", "version": "2.1",
        "score_base": 85.0
    },
    {
        "name": "WanX2.1-T2I-Plus", "company": "Alibaba", "category": "image", "parameter_size": "Unknown", "description": "万相文生图旗舰版", "version": "2.1",
        "score_base": 88.0
    },

    # Zhipu AI (智谱)
    {
        "name": "GLM-4-Plus", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "全能旗舰模型", "version": "4-Plus",
        "score_base": 93.0
    },
    {
        "name": "GLM-4-Long", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "超长上下文模型", "version": "4-Long",
        "score_base": 90.5
    },
    {
        "name": "GLM-4-Flash", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "极速低成本模型", "version": "4-Flash",
        "score_base": 86.0
    },
    {
        "name": "GLM-4.5", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "新一代基座模型", "version": "4.5",
        "score_base": 91.5
    },
    {
        "name": "GLM-Z1-Flash", "company": "Zhipu AI", "category": "text", "parameter_size": "Unknown", "description": "推理专用模型", "version": "Z1",
        "score_base": 88.5
    },
    {
        "name": "GLM-4V-Plus-0111", "company": "Zhipu AI", "category": "multimodal", "parameter_size": "Unknown", "description": "旗舰级多模态模型", "version": "4V-Plus",
        "score_base": 92.5
    },
    {
        "name": "GLM-CogView3-Flash", "company": "Zhipu AI", "category": "image", "parameter_size": "Unknown", "description": "快速图像生成模型", "version": "CogView3",
        "score_base": 84.0
    },

    # MiniMax
    {
        "name": "MiniMax-Text-01", "company": "MiniMax", "category": "text", "parameter_size": "456B", "description": "高智能通用模型", "version": "01",
        "score_base": 89.0
    },
    {
        "name": "MiniMax-Hailuo-02", "company": "MiniMax", "category": "image", "parameter_size": "Unknown", "description": "海螺多模态/生图模型", "version": "02",
        "score_base": 87.0
    },

    # ByteDance (字节/即梦)
    {
        "name": "Doubao-Seedream-3.0-T2I", "company": "ByteDance", "category": "image", "parameter_size": "Unknown", "description": "即梦专业文生图", "version": "3.0",
        "score_base": 89.5
    },
    {
        "name": "Doubao-Seedance-1.0-Pro", "company": "ByteDance", "category": "image", "parameter_size": "Unknown", "description": "专业级视频生成模型", "version": "1.0",
        "score_base": 86.5
    },

    # Moonshot AI (Kimi)
    {
        "name": "Kimi-K2", "company": "Moonshot AI", "category": "text", "parameter_size": "Unknown", "description": "Kimi 新一代智能模型", "version": "K2",
        "score_base": 91.0
    },

    # Baidu (文心一言)
    {
        "name": "ERNIE-4.5-Turbo-128K", "company": "Baidu", "category": "text", "parameter_size": "Unknown", "description": "文心最新性能增强版", "version": "4.5-Turbo",
        "score_base": 89.5
    },
    {
        "name": "ERNIE-4.5-Turbo-VL-32K", "company": "Baidu", "category": "multimodal", "parameter_size": "Unknown", "description": "文心最新多模态模型", "version": "4.5-VL",
        "score_base": 88.5
    },

    # Baichuan (百川)
    {
        "name": "Baichuan-M2-128K", "company": "Baichuan", "category": "text", "parameter_size": "Unknown", "description": "百川旗舰通用模型", "version": "M2",
        "score_base": 88.0
    },
]

def generate_score(base_score, variance=3.0):
    """在基准分附近生成随机分"""
    score = base_score + random.uniform(-variance, variance)
    return round(max(0, min(100, score)), 1)

print(f"Cleaning up existing models to avoid duplicates...")
try:
    with transaction.atomic():
        My_Model.objects.all().delete()
except Exception as e:
    print(f"Warning: Failed to clear old data: {e}")

print(f"Inserting {len(models_data)} models with initial scores...")
created_count = 0
score_count = 0

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
        
        # 1. 生成分项维度分数
        dimensions = ['language', 'math', 'code', 'multimodal']
        scores_buffer = []
        
        for dim in dimensions:
            # 根据模型特长微调分数
            current_base = data["score_base"]
            
            # 如果模型类别匹配当前维度，加分
            if (data["category"] == 'text' and dim in ['language']) or \
               (data["category"] == 'code' and dim == 'code') or \
               (data["category"] == 'multimodal' and dim == 'multimodal'):
                current_base += 2.0
            
            # 如果是文本模型，多模态能力通常较弱或没有
            if data["category"] == 'text' and dim == 'multimodal':
                score_val = 0.0 # 纯文本模型没有多模态分
            elif data["category"] == 'image' and dim in ['language', 'math', 'code']:
                 score_val = 0.0 # 纯生图模型通常没有这些能力
            else:
                score_val = generate_score(current_base)
            
            # 保存非零分数用于计算平均分
            if score_val > 0:
                scores_buffer.append(score_val)
                
            # 写入数据库
            ModelDimensionScore.objects.create(
                model=model,
                dimension=dim,
                score=score_val,
                previous_score=score_val
            )
            score_count += 1
            
        # 2. 计算并写入综合得分 (Overall)
        # 逻辑：综合得分 = 所有非零分项维度的平均值
        if scores_buffer:
            overall_score = sum(scores_buffer) / len(scores_buffer)
            overall_score = round(overall_score, 1)
        else:
            overall_score = 0.0
            
        ModelDimensionScore.objects.create(
            model=model,
            dimension='overall',
            score=overall_score,
            previous_score=overall_score
        )
        score_count += 1
            
    except Exception as e:
        print(f"Error inserting {data['name']}: {e}")

print(f"Successfully inserted {created_count} models.")

# --- Part 2: 用户初始化 ---
print("\nChecking users...")
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print(">>> Superuser 'admin' created.")
else:
    print(">>> Superuser 'admin' already exists.")

print(f"Initialized {score_count} score records with calculated overall scores.")