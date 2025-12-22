
import os
import django
import sys

# 设置 Django 环境
sys.path.append('/mnt/d/3_autumn/software_project/teamwork/SE-Project/PolyMetric/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.settings')
django.setup()

from apps.tasks.models import EvaluationTask, EvaluationItem

def monitor():
    target_ids = [82, 83, 84]
    tasks = EvaluationTask.objects.filter(id__in=target_ids).order_by('id')
    
    print(f"{'ID':<5} | {'Name':<12} | {'Status':<15} | {'Items':<6} | {'P1 Ready':<8} | {'P2 Ready':<8}")
    print("-" * 75)
    
    for t in tasks:
        items = t.items.all()
        total = items.count()
        p1_ready = items.filter(predicted_answer__isnull=False).exclude(predicted_answer="").count()
        p2_ready = items.filter(predicted_answer_2__isnull=False).exclude(predicted_answer_2="").count()
        
        print(f"{t.id:<5} | {t.name:<12} | {t.status:<15} | {total:<6} | {p1_ready}/{total:<6} | {p2_ready}/{total:<6}")

if __name__ == "__main__":
    monitor()
