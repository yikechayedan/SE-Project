
import os
import django
import sys

# 设置 Django 环境
sys.path.append('/mnt/d/3_autumn/software_project/teamwork/SE-Project/PolyMetric/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.settings')
django.setup()

from apps.tasks.models import EvaluationTask

def check_latest_tasks():
    tasks = EvaluationTask.objects.order_by('-id')[:3]
    print(f"{'ID':<5} | {'Name':<15} | {'Status':<15} | {'Model A':<8} | {'Model B':<8} | {'SharedFrom':<10}")
    print("-" * 75)
    for t in reversed(tasks):
        m2 = t.myModel_2_id if t.myModel_2_id else "None"
        sf = t.shared_from_id if t.shared_from_id else "None"
        print(f"{t.id:<5} | {t.name:<15} | {t.status:<15} | {t.myModel_id:<8} | {m2:<8} | {sf:<10}")

if __name__ == "__main__":
    check_latest_tasks()
