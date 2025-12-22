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
from apps.tasks.run_logic import find_existing_answer, prepare_evaluation_items

def cleanup():
    print("Cleaning up test data...")
    EvaluationTask.objects.filter(name__startswith="TestTask_").delete()
    Dataset.objects.filter(name="TestDataset_Repro").delete()
    My_Model.objects.filter(name__startswith="TestModel_").delete()
    User.objects.filter(username="testuser_repro").delete()

def run_repro():
    cleanup()
    
    print("Setting up data...")
    user = User.objects.create(username="testuser_repro")
    
    # Create Models
    model_a = My_Model.objects.create(name="TestModel_A", owner=user)
    model_b = My_Model.objects.create(name="TestModel_B", owner=user)
    model_c = My_Model.objects.create(name="TestModel_C", owner=user)
    
    # Create Dataset (Virtual file)
    dataset = Dataset.objects.create(
        name="TestDataset_Repro", 
        creator=user, 
        file_format="json",
        # We won't actually read the file in find_existing_answer, 
        # but prepare_evaluation_items needs it. 
        # For this specific test of find_existing_answer, we can manually populate items.
    )
    
    content_str = "What is the capital of France?"
    
    # --- Task 1: A vs B ---
    task1 = EvaluationTask.objects.create(
        name="TestTask_AvB",
        creator=user,
        dataset=dataset,
        method="adversarial",
        myModel=model_a,
        myModel_2=model_b,
        judge_type="human",
        status="completed"
    )
    
    # Create Item for Task 1 with answers
    EvaluationItem.objects.create(
        task=task1,
        content=content_str,
        predicted_answer="Paris (Model A)",
        predicted_answer_2="Paris is the capital (Model B)"
    )
    
    print(f"Task 1 (A vs B) created. Model A answer: 'Paris (Model A)'")
    
    # --- Task 2: B vs C ---
    task3 = EvaluationTask.objects.create(
        name="TestTask_BvC",
        creator=user,
        dataset=dataset,
        method="adversarial",
        myModel=model_b,
        myModel_2=model_c,
        judge_type="human",
        status="completed"
    )
    
    EvaluationItem.objects.create(
        task=task3,
        content=content_str,
        predicted_answer="Paris is the capital (Model B)",
        predicted_answer_2="It is Paris (Model C)"
    )
    
    print(f"Task 3 (B vs C) created. Model C answer: 'It is Paris (Model C)'")

    # --- Test find_existing_answer for New Task A vs C ---
    print("\n--- Testing find_existing_answer for New Task Context (A vs C) ---")
    
    # 1. Look for Model A's answer (Should come from Task 1)
    ans_a = find_existing_answer(model_a.id, dataset.id, content_str)
    print(f"Searching for Model A answer...")
    if ans_a == "Paris (Model A)":
        print("SUCCESS: Found correct Model A answer.")
    else:
        print(f"FAILURE: Expected 'Paris (Model A)', got '{ans_a}'")
        
    # 2. Look for Model C's answer (Should come from Task 3)
    ans_c = find_existing_answer(model_c.id, dataset.id, content_str)
    print(f"Searching for Model C answer...")
    if ans_c == "It is Paris (Model C)":
        print("SUCCESS: Found correct Model C answer.")
    else:
        print(f"FAILURE: Expected 'It is Paris (Model C)', got '{ans_c}'")

    cleanup()

if __name__ == "__main__":
    run_repro()
