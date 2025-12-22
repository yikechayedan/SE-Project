"""
测试数据集格式与评测类型不匹配的情况
"""
from django.test import TestCase
from rest_framework import status
from tests.test_utils import TestDataGenerator, APITestMixin


class DatasetEvaluationTypeMismatchTest(TestCase, APITestMixin):
    """测试数据集格式与评测类型不匹配的情况"""
    
    def setUp(self):
        """设置测试环境"""
        self.user = TestDataGenerator.create_user()
        self.model = TestDataGenerator.create_model()
        
        # 创建不同类型的数据集
        self.create_test_datasets()
    
    def create_test_datasets(self):
        """创建测试数据集"""
        # 创建主观评测数据集
        self.subjective_dataset = TestDataGenerator.create_dataset(
            name='主观评测数据集',
            description='用于主观评测的数据集',
            category='text',
            evaluation_type='subjective',
            file_format='json',
            creator=self.user,
            is_public=True
        )
        
        # 创建客观评测数据集
        self.objective_dataset = TestDataGenerator.create_dataset(
            name='客观评测数据集',
            description='用于客观评测的数据集',
            category='text',
            evaluation_type='objective',
            file_format='json',
            creator=self.user,
            is_public=True
        )
        
        # 创建对抗评测数据集
        self.adversarial_dataset = TestDataGenerator.create_dataset(
            name='对抗评测数据集',
            description='用于对抗评测的数据集',
            category='text',
            evaluation_type='adversarial',
            file_format='json',
            creator=self.user,
            is_public=True
        )
    
    def test_subjective_task_with_objective_dataset_should_fail(self):
        """测试主观评测任务使用客观评测数据集应该失败"""
        self.create_authenticated_client(self.user)
        
        response = self.client.post('/api/tasks/evaluation-tasks/', {
            'name': '主观评测任务',
            'description': '这是一个主观评测任务',
            'dataset': self.objective_dataset.id,
            'method': 'subjective',
            'myModel': self.model.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dataset_format_error', response.data)
        self.assertIn('数据集格式错误', response.data['dataset_format_error'])
    
    def test_objective_task_with_subjective_dataset_should_fail(self):
        """测试客观评测任务使用主观评测数据集应该失败"""
        self.create_authenticated_client(self.user)
        
        response = self.client.post('/api/tasks/evaluation-tasks/', {
            'name': '客观评测任务',
            'description': '这是一个客观评测任务',
            'dataset': self.subjective_dataset.id,
            'method': 'objective',
            'myModel': self.model.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dataset_format_error', response.data)
        self.assertIn('数据集格式错误', response.data['dataset_format_error'])
    
    def test_adversarial_task_with_subjective_dataset_should_fail(self):
        """测试对抗评测任务使用主观评测数据集应该失败"""
        self.create_authenticated_client(self.user)
        
        response = self.client.post('/api/tasks/evaluation-tasks/', {
            'name': '对抗评测任务',
            'description': '这是一个对抗评测任务',
            'dataset': self.subjective_dataset.id,
            'method': 'adversarial',
            'myModel': self.model.id,
            'myModel_2': self.model.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dataset_format_error', response.data)
        self.assertIn('数据集格式错误', response.data['dataset_format_error'])
    
    def test_matching_task_and_dataset_should_succeed(self):
        """测试匹配的任务和数据集应该成功"""
        self.create_authenticated_client(self.user)
        
        # 主观测评任务 + 主观测评数据集
        response = self.client.post('/api/tasks/evaluation-tasks/', {
            'name': '主观评测任务',
            'description': '这是一个主观评测任务',
            'dataset': self.subjective_dataset.id,
            'method': 'subjective',
            'myModel': self.model.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 客观测评任务 + 客观测评数据集
        response = self.client.post('/api/tasks/evaluation-tasks/', {
            'name': '客观评测任务',
            'description': '这是一个客观评测任务',
            'dataset': self.objective_dataset.id,
            'method': 'objective',
            'myModel': self.model.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 对抗评测任务 + 对抗评测数据集
        response = self.client.post('/api/tasks/evaluation-tasks/', {
            'name': '对抗评测任务',
            'description': '这是一个对抗评测任务',
            'dataset': self.adversarial_dataset.id,
            'method': 'adversarial',
            'myModel': self.model.id,
            'myModel_2': self.model.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_task_update_with_mismatched_dataset_should_fail(self):
        """测试更新任务时使用不匹配的数据集应该失败"""
        # 先创建一个匹配的任务
        task = TestDataGenerator.create_evaluation_task(
            name='原始任务',
            description='原始描述',
            creator=self.user,
            dataset=self.subjective_dataset,
            method='subjective',
            model=self.model
        )
        
        self.create_authenticated_client(self.user)
        
        # 尝试更新为不匹配的数据集
        response = self.client.patch(f'/api/tasks/evaluation-tasks/{task.id}/', {
            'dataset': self.objective_dataset.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dataset_format_error', response.data)
        self.assertIn('数据集格式错误', response.data['dataset_format_error'])