"""
简单测试脚本，验证数据集格式与评测类型不匹配的验证逻辑
"""
import os
import sys
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
    print("开始测试数据集格式与评测类型不匹配的验证逻辑...")
    
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
        name='主观评测数据集',
        description='用于主观评测的数据集',
        category='text',
        evaluation_type='subjective',
        file_format='json',
        creator=user,
        is_public=True
    )
    
    objective_dataset = Dataset.objects.create(
        name='客观评测数据集',
        description='用于客观评测的数据集',
        category='text',
        evaluation_type='objective',
        file_format='json',
        creator=user,
        is_public=True
    )
    
    # 测试1: 主观测评任务使用客观评测数据集（应该失败）
    print("\n测试1: 主观测评任务使用客观评测数据集")
    serializer = EvaluationTaskSerializer(data={
        'name': '主观评测任务',
        'description': '这是一个主观评测任务',
        'dataset': objective_dataset.id,
        'method': 'subjective',
        'myModel': model.id
    })
    
    is_valid = serializer.is_valid()
    print(f"验证结果: {'通过' if is_valid else '失败'}")
    if not is_valid:
        print(f"错误信息: {serializer.errors}")
        if 'dataset_format_error' in serializer.errors:
            print("✓ 成功检测到数据集格式错误")
        else:
            print("✗ 未检测到预期的数据集格式错误")
    else:
        print("✗ 验证应该失败但却通过了")
    
    # 测试2: 客观测评任务使用主观评测数据集（应该失败）
    print("\n测试2: 客观测评任务使用主观评测数据集")
    serializer = EvaluationTaskSerializer(data={
        'name': '客观评测任务',
        'description': '这是一个客观评测任务',
        'dataset': subjective_dataset.id,
        'method': 'objective',
        'myModel': model.id
    })
    
    is_valid = serializer.is_valid()
    print(f"验证结果: {'通过' if is_valid else '失败'}")
    if not is_valid:
        print(f"错误信息: {serializer.errors}")
        if 'dataset_format_error' in serializer.errors:
            print("✓ 成功检测到数据集格式错误")
        else:
            print("✗ 未检测到预期的数据集格式错误")
    else:
        print("✗ 验证应该失败但却通过了")
    
    # 测试3: 主观测评任务使用主观评测数据集（应该成功）
    print("\n测试3: 主观测评任务使用主观评测数据集")
    serializer = EvaluationTaskSerializer(data={
        'name': '主观评测任务',
        'description': '这是一个主观评测任务',
        'dataset': subjective_dataset.id,
        'method': 'subjective',
        'myModel': model.id
    })
    
    is_valid = serializer.is_valid()
    print(f"验证结果: {'通过' if is_valid else '失败'}")
    if is_valid:
        print("✓ 匹配的数据集和评测类型验证通过")
    else:
        print(f"✗ 验证失败: {serializer.errors}")
    
    # 测试4: 客观测评任务使用客观评测数据集（应该成功）
    print("\n测试4: 客观测评任务使用客观评测数据集")
    serializer = EvaluationTaskSerializer(data={
        'name': '客观评测任务',
        'description': '这是一个客观评测任务',
        'dataset': objective_dataset.id,
        'method': 'objective',
        'myModel': model.id
    })
    
    is_valid = serializer.is_valid()
    print(f"验证结果: {'通过' if is_valid else '失败'}")
    if is_valid:
        print("✓ 匹配的数据集和评测类型验证通过")
    else:
        print(f"✗ 验证失败: {serializer.errors}")
    
    print("\n测试完成!")

if __name__ == '__main__':
    test_validation()