# ================================
# PolyMetric Backend Init Script
# Windows PowerShell Version
# ================================

# 出错就停
$ErrorActionPreference = "Stop"

Write-Host "========================================"
Write-Host " PolyMetric Backend Initialization (Win)"
Write-Host "========================================"

# 1️⃣ 切换到脚本所在目录（确保和 manage.py 同级）
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "`n[1/5] Creating database migrations..."

# 2️⃣ 生成迁移（分 app + 兜底）
python manage.py makemigrations system rankings
python manage.py makemigrations

Write-Host "`n[2/5] Applying database migrations..."
python manage.py migrate

Write-Host "`n[3/5] Initializing data via Django shell..."

# 3️⃣ Django Shell 初始化数据
$initScript = @'
import os
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from apps.models.models import My_Model
from apps.rankings.models import ModelDimensionScore

User = get_user_model()

print(">>> Cleaning existing model data...")
try:
    with transaction.atomic():
        My_Model.objects.all().delete()
except Exception as e:
    print("Warning:", e)

models_data = [
    {"name": "DeepSeek-R1", "company": "DeepSeek", "category": "text", "parameter_size": "70B+", "description": "高强度推理模型", "version": "R1"},
    {"name": "Qwen3-Coder-480B-A35B-Instruct", "company": "Alibaba", "category": "code", "parameter_size": "480B", "description": "代码专家模型", "version": "Coder"},
    {"name": "GLM-4-Plus", "company": "Zhipu AI", "category": "text", "parameter_size": "130B", "description": "旗舰增强版", "version": "4-Plus"},
]

print(f">>> Inserting {len(models_data)} models...")
for m in models_data:
    try:
        My_Model.objects.create(
            name=m["name"],
            company=m["company"],
            category=m["category"],
            parameter_size=m["parameter_size"],
            description=m["description"],
            version=m["version"],
            release_date=timezone.now().date()
        )
    except Exception as e:
        print("Insert failed:", e)

print(">>> Checking users...")

if not User.objects.filter(username="shadow").exists():
    User.objects.create_superuser("shadow", "shadow@example.com", "123456789")
    print(">>> Superuser 'shadow' created (password: 123456789)")
else:
    print(">>> Superuser 'shadow' already exists")

print(">>> Initializing model scores...")
dimensions = ["overall", "language", "reasoning", "coding"]

for model in My_Model.objects.all():
    for dim in dimensions:
        ModelDimensionScore.objects.get_or_create(
            model=model,
            dimension=dim,
            defaults={"score": 0.0, "previous_score": 0.0}
        )

print(">>> Initialization complete.")
'@

$initScript | python manage.py shell

Write-Host "`n[4/5] Initialization done."

Write-Host "`n[5/5] Starting Django server..."
Write-Host "----------------------------------------"
Write-Host "Server URL: http://127.0.0.1:8000/"
Write-Host "----------------------------------------"

python manage.py runserver
