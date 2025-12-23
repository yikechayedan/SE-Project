import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.settings')
django.setup()

from apps.tasks.models import EvaluationTask

def delete_all_tasks():
    count = EvaluationTask.objects.count()
    print(f"Found {count} tasks. Deleting...")
    EvaluationTask.objects.all().delete()
    print("All tasks have been deleted.")

if __name__ == "__main__":
    delete_all_tasks()
