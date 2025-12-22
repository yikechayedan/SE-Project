"""
测试数据集格式与评测类型不匹配的验证结果
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.test_settings')
django.setup()

from apps.tasks.serializers import EvaluationTaskSerializer
from apps.datasets.models import Dataset
from apps.models.models import My_Model
from django.contrib.auth import get_user_model

User = get_user_model()

def test_validation():
    """测试验证逻辑"""
    print("Testing dataset format and evaluation type mismatch validation...")
    
    # 创建测试用户
    import time
    timestamp = int(time.time())
    user = User.objects.create_user(
        username=f'testuser_{timestamp}',
        email=f'test_{timestamp}@example.com',
        password='testpass123'
    )
    
    # 创建测试模型
    model = My_Model.objects.create(
        name='Test Model',
        description='Test model for evaluation',
        company='Test Company',
        category='text',
        parameter_size='10B',
        version='v1.0',
        official_url='https://api.test.com'
    )
    
    # 创建不同类型的数据集
    subjective_dataset = Dataset.objects.create(
        name='Subjective Dataset',
        description='Dataset for subjective evaluation',
        category='text',
        evaluation_type='subjective',
        file_format='json',
        creator=user,
        is_public=True
    )
    
    objective_dataset = Dataset.objects.create(
        name='Objective Dataset',
        description='Dataset for objective evaluation',
        category='text',
        evaluation_type='objective',
        file_format='json',
        creator=user,
        is_public=True
    )
    
    # 测试1: 主观测评任务使用客观评测数据集（应该失败）
    print("\nTest 1: Subjective task with objective dataset")
    serializer = EvaluationTaskSerializer(data={
        'name': 'Subjective Task',
        'description': 'This is a subjective task',
        'dataset': objective_dataset.id,
        'method': 'subjective',
        'myModel': model.id
    })
    
    is_valid = serializer.is_valid()
    print(f"Validation result: {'PASS' if is_valid else 'FAIL'}")
    if not is_valid:
        print(f"Error message: {serializer.errors}")
        if 'dataset_format_error' in serializer.errors:
            print("SUCCESS: Dataset format error detected")
        else:
            print("FAIL: Expected dataset format error not detected")
    else:
        print("FAIL: Validation should have failed but passed")
    
    # 测试2: 客观测评任务使用主观评测数据集（应该失败）
    print("\nTest 2: Objective task with subjective dataset")
    serializer = EvaluationTaskSerializer(data={
        'name': 'Objective Task',
        'description': 'This is an objective task',
        'dataset': subjective_dataset.id,
        'method': 'objective',
        'myModel': model.id
    })
    
    is_valid = serializer.is_valid()
    print(f"Validation result: {'PASS' if is_valid else 'FAIL'}")
    if not is_valid:
        print(f"Error message: {serializer.errors}")
        if 'dataset_format_error' in serializer.errors:
            print("SUCCESS: Dataset format error detected")
        else:
            print("FAIL: Expected dataset format error not detected")
    else:
        print("FAIL: Validation should have failed but passed")
    
    # 测试3: 主观测评任务使用主观评测数据集（应该成功）
    print("\nTest 3: Subjective task with subjective dataset")
    serializer = EvaluationTaskSerializer(data={
        'name': 'Subjective Task',
        'description': 'This is a subjective task',
        'dataset': subjective_dataset.id,
        'method': 'subjective',
        'myModel': model.id
    })
    
    is_valid = serializer.is_valid()
    print(f"Validation result: {'PASS' if is_valid else 'FAIL'}")
    if is_valid:
        print("SUCCESS: Matching dataset and evaluation type passed validation")
    else:
        print(f"FAIL: Validation failed: {serializer.errors}")
    
    # 测试4: 客观测评任务使用客观评测数据集（应该成功）
    print("\nTest 4: Objective task with objective dataset")
    serializer = EvaluationTaskSerializer(data={
        'name': 'Objective Task',
        'description': 'This is an objective task',
        'dataset': objective_dataset.id,
        'method': 'objective',
        'myModel': model.id
    })
    
    is_valid = serializer.is_valid()
    print(f"Validation result: {'PASS' if is_valid else 'FAIL'}")
    if is_valid:
        print("SUCCESS: Matching dataset and evaluation type passed validation")
    else:
        print(f"FAIL: Validation failed: {serializer.errors}")
    
    print("\nAll tests completed!")

if __name__ == '__main__':
    test_validation()