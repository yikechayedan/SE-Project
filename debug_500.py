
import os
import django
import sys
import traceback

# 设置 Django 环境
sys.path.append('/mnt/d/3_autumn/software_project/teamwork/SE-Project/PolyMetric/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.settings')
django.setup()

from apps.tasks.models import EvaluationTask, EvaluationItem
from apps.tasks.run_logic import reuse_task_items_model_aware
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

def debug_run_task(task_id):
    try:
        task = EvaluationTask.objects.get(id=task_id)
        print(f"Step 1: Get task {task_id} OK")

        one_hour_ago = timezone.now() - timedelta(hours=1)
        active_statuses = ['running', 'completed', 'awaiting_human_judge']
        
        upstream_search = EvaluationTask.objects.filter(
            dataset_id=task.dataset_id,
            created_at__gt=one_hour_ago,
            status__in=active_statuses,
            id__lt=task.id
        )

        model_q = Q(myModel_id=task.myModel_id) | Q(myModel_2_id=task.myModel_id)
        if task.method == 'adversarial':
            model_q |= Q(myModel_id=task.myModel_2_id) | Q(myModel_2_id=task.myModel_2_id)
        
        existing_runner = upstream_search.filter(model_q).order_by('status').first()
        print(f"Step 2: Upstream task is {existing_runner.id if existing_runner else 'None'}")

        if existing_runner:
            if existing_runner.status in ['completed', 'awaiting_human_judge']:
                print("Step 3: Attempting reuse_task_items_model_aware...")
                reuse_task_items_model_aware(existing_runner, task)
                print("Step 4: Reuse completed")
                
                if task.judge_type == 'human':
                    has_missing = task.items.filter(Q(predicted_answer__isnull=True) | Q(predicted_answer_2__isnull=True)).exists()
                    print(f"Step 5: Missing answers? {has_missing}")
            else:
                print(f"Step 3: Mounting to running task {existing_runner.id}")
        else:
            print("Step 2: No upstream found, normal start")

    except Exception:
        print("\n--- ERROR CAUGHT ---")
        traceback.print_exc()

if __name__ == "__main__":
    debug_run_task(86)
