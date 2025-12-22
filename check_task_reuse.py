import os
import django
import sys

sys.path.append("PolyMetric/backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PolyMetric.settings")
django.setup()

from apps.tasks.models import EvaluationTask, EvaluationItem

def check_reuse():
    # 1. Get the latest adversarial task (The "A C D H" task user likely just created)
    latest_task = EvaluationTask.objects.filter(method="adversarial").order_by("-id").first()
    
    if not latest_task:
        print("No adversarial tasks found.")
        return

    print(f"Checking Task: {latest_task.name} (ID: {latest_task.id})")
    print(f"Models: A={latest_task.myModel.name}, B={latest_task.myModel_2.name if latest_task.myModel_2 else 'None'}")
    print(f"Status: {latest_task.status}")
    
    items = latest_task.items.all()
    total_items = items.count()
    print(f"Total Items: {total_items}")
    
    if total_items == 0:
        print("Task has no items yet.")
        return

    # 2. Get Reference Tasks
    # Based on previous context:
    # Task 82: A B D J (Baichuan-M2-128K vs Baichuan-M2) -> Contains answer for 'Baichuan-M2-128K' (Model A of new task)
    # Task 84: B C D H (Baichuan-M2 vs ERNIE-4.5-Turbo-128K) -> Contains answer for 'ERNIE-4.5-Turbo-128K' (Model B of new task)
    
    ref_task_a = EvaluationTask.objects.filter(id=82).first() # Source for New Model A
    ref_task_c = EvaluationTask.objects.filter(id=84).first() # Source for New Model B (C)

    # Build maps for quick lookup: content -> answer
    ref_map_a = {}
    if ref_task_a:
        print(f"Reference Task for Model A: {ref_task_a.name} (ID: 82)")
        for it in ref_task_a.items.all():
            # In Task 82, Baichuan-M2-128K is Model A (myModel)
            if ref_task_a.myModel.name == latest_task.myModel.name:
                ref_map_a[it.content.strip()] = it.predicted_answer
            elif ref_task_a.myModel_2 and ref_task_a.myModel_2.name == latest_task.myModel.name:
                ref_map_a[it.content.strip()] = it.predicted_answer_2
    else:
        print("Warning: Reference Task 82 not found.")

    ref_map_c = {}
    if ref_task_c:
        print(f"Reference Task for Model B (C): {ref_task_c.name} (ID: 84)")
        for it in ref_task_c.items.all():
             # In Task 84, ERNIE is likely Model B
             if ref_task_c.myModel_2 and ref_task_c.myModel_2.name == latest_task.myModel_2.name:
                 ref_map_c[it.content.strip()] = it.predicted_answer_2
             elif ref_task_c.myModel.name == latest_task.myModel_2.name:
                 ref_map_c[it.content.strip()] = it.predicted_answer
    else:
        print("Warning: Reference Task 84 not found.")

    # 3. Compare
    reused_count_a = 0
    reused_count_c = 0
    missing_a = 0
    missing_c = 0
    
    print("\n--- detailed Item Check ---")
    # Check first 5 items
    for i, item in enumerate(items):
        content_key = item.content.strip()
        
        # Check Model A Answer
        actual_a = item.predicted_answer
        expected_a = ref_map_a.get(content_key)
        
        is_a_reused = False
        if actual_a and expected_a and actual_a == expected_a:
            is_a_reused = True
            reused_count_a += 1
        elif not actual_a:
            missing_a += 1
            
        # Check Model B Answer
        actual_c = item.predicted_answer_2
        expected_c = ref_map_c.get(content_key)
        
        is_c_reused = False
        if actual_c and expected_c and actual_c == expected_c:
            is_c_reused = True
            reused_count_c += 1
        elif not actual_c:
            missing_c += 1

        if i < 3: # Print details for first 3
            print(f"\nItem {item.id}: {item.content[:30]}...")
            print(f"  Model A (New): {'✅ Reused' if is_a_reused else '❌ Not Reused/Match'}")
            if not is_a_reused:
                print(f"    - Actual: {actual_a[:20] if actual_a else 'None'}...")
                print(f"    - Source: {expected_a[:20] if expected_a else 'Not found in source'}...")
            
            print(f"  Model B (New): {'✅ Reused' if is_c_reused else '❌ Not Reused/Match'}")
            if not is_c_reused:
                print(f"    - Actual: {actual_c[:20] if actual_c else 'None'}...")
                print(f"    - Source: {expected_c[:20] if expected_c else 'Not found in source'}...")

    print("\n--- Summary ---")
    print(f"Model A Reused: {reused_count_a} / {total_items}")
    print(f"Model B Reused: {reused_count_c} / {total_items}")
    print(f"Missing A: {missing_a}")
    print(f"Missing B: {missing_c}")

if __name__ == "__main__":
    check_reuse()
