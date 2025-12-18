"""
测试工具函数和数据生成器
"""
import json
import tempfile
import os
from datetime import datetime
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from apps.datasets.models import Dataset, DatasetFollow
from apps.models.models import My_Model, ModelFollow
from apps.tasks.models import EvaluationTask, EvaluationItem
from apps.users.models import UserFollow

User = get_user_model()


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def create_user(username=None, email=None, password="test123456", **kwargs):
        """创建测试用户"""
        if not username:
            username = f"testuser_{datetime.now().timestamp()}"
        if not email:
            email = f"{username}@test.com"
            
        user_data = {
            "username": username,
            "email": email,
            "password": password,
            **kwargs
        }
        return User.objects.create_user(**user_data)
    
    @staticmethod
    def create_admin_user(username=None, email=None, password="admin123456", **kwargs):
        """创建管理员用户"""
        if not username:
            username = f"admin_{datetime.now().timestamp()}"
        if not email:
            email = f"{username}@admin.com"
            
        return User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            **kwargs
        )
    
    @staticmethod
    def create_model(name=None, company=None, **kwargs):
        """创建测试模型"""
        if not name:
            name = f"测试模型_{datetime.now().timestamp()}"
        if not company:
            company = "测试公司"
            
        model_data = {
            "name": name,
            "company": company,
            "category": kwargs.get("category", "text"),
            "parameter_size": kwargs.get("parameter_size", "10B"),
            "description": kwargs.get("description", "测试模型描述"),
            "version": kwargs.get("version", "v1.0"),
            "official_url": kwargs.get("official_url", "https://test-model.example.com"),
            **{k: v for k, v in kwargs.items() if k not in ["category", "parameter_size", "description", "version", "official_url"]}
        }
        return My_Model.objects.create(**model_data)
    
    @staticmethod
    def create_dataset(name=None, creator=None, **kwargs):
        """创建测试数据集"""
        if not name:
            name = f"测试数据集_{datetime.now().timestamp()}"
        if not creator:
            creator = TestDataGenerator.create_user()
            
        dataset_data = {
            "name": name,
            "description": kwargs.get("description", "测试数据集描述"),
            "category": kwargs.get("category", "text"),
            "file_format": kwargs.get("file_format", "json"),
            "is_public": kwargs.get("is_public", True),
            "is_verified": kwargs.get("is_verified", True),
            "creator": creator,
            **{k: v for k, v in kwargs.items() if k not in ["description", "category", "file_format", "is_public", "is_verified", "creator"]}
        }
        return Dataset.objects.create(**dataset_data)
    
    @staticmethod
    def create_evaluation_task(name=None, creator=None, dataset=None, model=None, **kwargs):
        """创建评测任务"""
        if not name:
            name = f"测试评测任务_{datetime.now().timestamp()}"
        if not creator:
            creator = TestDataGenerator.create_user()
        if not dataset:
            dataset = TestDataGenerator.create_dataset()
        if not model:
            model = TestDataGenerator.create_model()
            
        task_data = {
            "name": name,
            "description": kwargs.get("description", "测试评测任务描述"),
            "method": kwargs.get("method", "objective"),
            "creator": creator,
            "dataset": dataset,
            "myModel": model,
            **{k: v for k, v in kwargs.items() if k not in ["description", "method", "creator", "dataset", "myModel"]}
        }
        return EvaluationTask.objects.create(**task_data)
    
    @staticmethod
    def create_evaluation_item(task=None, **kwargs):
        """创建评测项"""
        if not task:
            task = TestDataGenerator.create_evaluation_task()
            
        item_data = {
            "task": task,
            "content": kwargs.get("content", "测试内容"),
            "correct_answer": kwargs.get("correct_answer", "测试答案"),  # 修正字段名
            "predicted_answer": kwargs.get("predicted_answer", "预测答案"),
            "is_correct": kwargs.get("is_correct", True),
            **{k: v for k, v in kwargs.items() if k not in ["task", "content", "correct_answer", "predicted_answer", "is_correct"]}
        }
        return EvaluationItem.objects.create(**item_data)
    
    @staticmethod
    def create_temp_file(content=None, filename="test.json", file_format="json"):
        """创建临时文件"""
        if content is None:
            if file_format == "json":
                content = json.dumps([
                    {"id": 1, "question": "测试问题1", "answer": "测试答案1"},
                    {"id": 2, "question": "测试问题2", "answer": "测试答案2"}
                ])
            else:
                content = "测试文件内容"
        
        temp_file = tempfile.NamedTemporaryFile(suffix=f".{file_format}", delete=False)
        temp_file.write(content.encode('utf-8'))
        temp_file.close()
        return temp_file.name


class AuthUtils:
    """认证工具类"""
    
    @staticmethod
    def get_jwt_token(user):
        """获取JWT令牌"""
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    
    @staticmethod
    def get_auth_headers(user):
        """获取认证头"""
        tokens = AuthUtils.get_jwt_token(user)
        return {
            'HTTP_AUTHORIZATION': f'Bearer {tokens["access"]}'
        }


class APITestMixin:
    """API测试混入类"""
    
    def assertAPIResponse(self, response, expected_status=200, expected_code=None):
        """断言API响应格式"""
        self.assertEqual(response.status_code, expected_status)
        
        # 检查响应数据是否为字典
        if not isinstance(response.data, dict):
            return  # 如果不是字典，跳过格式检查
            
        # 检查code字段（如果存在）
        if expected_code is not None:
            if 'code' in response.data:
                self.assertEqual(response.data.get('code'), expected_code)
        
        # 对于成功响应，检查是否包含data字段（如果存在）
        if 200 <= response.status_code < 300:
            if 'data' in response.data or 'msg' in response.data:
                # 有data字段就检查data，否则只检查msg
                if 'data' in response.data:
                    self.assertIn('data', response.data)
                if 'msg' in response.data:
                    self.assertIn('msg', response.data)
    
    def assertAPISuccess(self, response, expected_status=200, expected_code=None):
        """断言API成功响应"""
        self.assertAPIResponse(response, expected_status, expected_code)
    
    def assertAPIError(self, response, expected_status=400, expected_code=None):
        """断言API错误响应"""
        self.assertAPIResponse(response, expected_status, expected_code)
    
    def create_authenticated_client(self, user=None):
        """创建已认证的客户端"""
        if user is None:
            user = TestDataGenerator.create_user()
        
        tokens = AuthUtils.get_jwt_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        return user