import os
import django
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'PolyMetric/backend'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PolyMetric.settings")
django.setup()

from apps.users.models import User
from apps.models.models import My_Model
from apps.datasets.models import Dataset
from apps.tasks.models import EvaluationTask, EvaluationItem
from apps.tasks.run_logic import find_existing_answer

def test_whitespace_matching():
    # Cleanup
    EvaluationTask.objects.filter(name="TestTask_WS").delete()
    Dataset.objects.filter(name="TestDataset_WS").delete()
    My_Model.objects.filter(name="TestModel_WS").delete()
    User.objects.filter(username="testuser_ws").delete()

    user = User.objects.create(username="testuser_ws", email="test_ws@example.com")
    model = My_Model.objects.create(name="TestModel_WS") # No owner field
    dataset = Dataset.objects.create(name="TestDataset_WS", creator=user, file_format="json")
    
    task = EvaluationTask.objects.create(
        name="TestTask_WS",
        creator=user,
        dataset=dataset,
        method="objective",
        myModel=model,
        status="completed"
    )

    # 1. Insert Item with double space
    content_db = "What is  the capital?"
    EvaluationItem.objects.create(
        task=task,
        content=content_db,
        predicted_answer="Paris"
    )
    
    print(f"Inserted item with content: '{content_db}'")
    
    # 2. Search with single space
    content_input = "What is the capital?"
    print(f"Searching with content: '{content_input}'")
    
    ans = find_existing_answer(model.id, dataset.id, content_input)
    
    if ans:
        print(f"SUCCESS: Found answer '{ans}' despite whitespace diff?")
    else:
        print("FAILURE: Did not find answer (expected if strictly matching).")
        
    # 3. Search with exact match
    print(f"Searching with content: '{content_db}'")
    ans_exact = find_existing_answer(model.id, dataset.id, content_db)
    if ans_exact:
        print(f"SUCCESS: Found answer '{ans_exact}' with exact match.")
    else:
        print("FAILURE: Did not find answer even with exact match!")

    # Cleanup
    task.delete()
    dataset.delete()
    model.delete()
    user.delete()

if __name__ == "__main__":
    test_whitespace_matching()
