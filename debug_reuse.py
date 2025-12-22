import os
import django
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'PolyMetric/backend'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PolyMetric.settings")
django.setup()

from apps.tasks.models import EvaluationItem, EvaluationTask
from apps.tasks.run_logic import find_existing_answer

def test_reuse_logic():
    print("Searching for items with answers...")
    # Find an item that has a predicted answer
    item = EvaluationItem.objects.filter(predicted_answer__isnull=False).first()
    
    if not item:
        print("No items with answers found in DB.")
        return

    print(f"Found item {item.id} with content length {len(item.content)}")
    print(f"Content preview: {item.content[:50]}...")
    print(f"Model ID: {item.task.myModel_id}")
    print(f"Dataset ID: {item.task.dataset_id}")
    print(f"Answer length: {len(item.predicted_answer)}")

    # Test find_existing_answer
    print("\nTesting find_existing_answer...")
    found_answer = find_existing_answer(item.task.myModel_id, item.task.dataset_id, item.content)
    
    if found_answer:
        print("SUCCESS: find_existing_answer found the answer.")
        if found_answer == item.predicted_answer:
            print("And it matches the item's answer.")
        else:
            print("But it returned a DIFFERENT answer (maybe from another item?).")
    else:
        print("FAILURE: find_existing_answer returned None.")
        
        # Debugging why
        clean_content = item.content.strip()
        print(f"\nDebug info:")
        print(f"clean_content[:50]: {clean_content[:50]}")
        
        from django.db.models import Q
        # Replicate the query in find_existing_answer
        qs = EvaluationItem.objects.filter(
            task__dataset_id=item.task.dataset_id,
            content__icontains=clean_content[:50]
        )
        print(f"Query with icontains count: {qs.count()}")
        
        matched_exact = False
        for it in qs:
            if it.content.strip() == clean_content:
                matched_exact = True
                print(f"  Item {it.id} matches exact strip content.")
                if it.task.myModel_id == item.task.myModel_id:
                     print(f"  Item {it.id} has matching model ID.")
                     if it.predicted_answer:
                         print(f"  Item {it.id} has predicted_answer.")
                     else:
                         print(f"  Item {it.id} has NO predicted_answer.")
            else:
                 pass
                 # print(f"  Item {it.id} does NOT match exact strip content.")
                 
        if not matched_exact:
            print("No item in the icontains result matched the exact content string.")

if __name__ == "__main__":
    test_reuse_logic()
