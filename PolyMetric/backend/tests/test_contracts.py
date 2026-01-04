"""
API契约测试 - 验证API响应格式和契约一致性
"""
import json
import os
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from tests.base import BaseContractTestCase
from tests.factories import (
    UserFactory, ModelFactory, DatasetFactory, 
    EvaluationTaskFactory, ScenarioFactory
)

User = get_user_model()


class UserAPIContractTest(BaseContractTestCase):
    """用户API契约测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = UserFactory()
        self.admin = UserFactory(is_staff=True, is_superuser=True)
    
    def test_user_registration_contract(self):
        """测试用户注册API契约"""
        data = {
            "username": f"contract_user_{int(time.time())}",
            "email": f"contract_user_{int(time.time())}@test.com",
            "password": "test123456",
            "phone": "13800138000"
        }
        response = self.client.post("/api/users/register/", data, format="json")
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 201)
        
        # 验证响应结构
        expected_schema = {
            "code": int,
            "msg": str,
            "data": {
                "id": int,
                "username": str,
                "email": str,
                "phone": str,
                "bio": str,
                "avatar": str,
                "show_followed_models": bool,
                "show_followed_datasets": bool,
                "created_at": str,
                "updated_at": str
            }
        }
        
        self.assertAPIResponse(response, 201)
        self._validate_contract(response.data, expected_schema)
    
    def test_user_login_contract(self):
        """测试用户登录API契约"""
        data = {
            "username": self.user.username,
            "password": "test123456"
        }
        response = self.client.post("/api/users/login/", data, format="json")
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证响应结构
        expected_schema = {
            "access": str,
            "refresh": str
        }
        
        self._validate_contract(response.data, expected_schema)
    
    def test_user_profile_contract(self):
        """测试用户资料API契约"""
        from tests.base import APITestHelper
        headers = APITestHelper.create_auth_headers(self.user)
        self.client.credentials(**headers)
        
        response = self.client.get("/api/users/me/")
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证响应结构
        expected_schema = {
            "code": int,
            "msg": str,
            "data": {
                "id": int,
                "username": str,
                "email": str,
                "phone": str,
                "bio": str,
                "avatar": str,
                "show_followed_models": bool,
                "show_followed_datasets": bool,
                "followers_count": int,
                "following_count": int,
                "created_at": str,
                "updated_at": str
            }
        }
        
        self.assertAPIResponse(response, 200)
        self._validate_contract(response.data, expected_schema)


class DatasetAPIContractTest(BaseContractTestCase):
    """数据集API契约测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = UserFactory()
        self.dataset = DatasetFactory(creator=self.user, with_file=True)
    
    def test_dataset_list_contract(self):
        """测试数据集列表API契约"""
        response = self.client.get("/api/datasets/")
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证响应结构
        expected_schema = {
            "code": int,
            "msg": str,
            "data": [
                {
                    "id": int,
                    "name": str,
                    "description": str,
                    "category": str,
                    "file_format": str,
                    "is_public": bool,
                    "is_verified": bool,
                    "file_size": int,
                    "sample_count": int,
                    "creator": {
                        "id": int,
                        "username": str
                    },
                    "created_at": str,
                    "updated_at": str
                }
            ]
        }
        
        self.assertAPIResponse(response, 200)
        self._validate_contract(response.data, expected_schema)
    
    def test_dataset_detail_contract(self):
        """测试数据集详情API契约"""
        response = self.client.get(f"/api/datasets/{self.dataset.id}/")
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证响应结构
        expected_schema = {
            "code": int,
            "msg": str,
            "data": {
                "id": int,
                "name": str,
                "description": str,
                "category": str,
                "file_format": str,
                "is_public": bool,
                "is_verified": bool,
                "file_size": int,
                "sample_count": int,
                "creator": {
                    "id": int,
                    "username": str,
                    "bio": str
                },
                "created_at": str,
                "updated_at": str
            }
        }
        
        self.assertAPIResponse(response, 200)
        self._validate_contract(response.data, expected_schema)
    
    def test_dataset_preview_contract(self):
        """测试数据集预览API契约"""
        from tests.base import APITestHelper
        headers = APITestHelper.create_auth_headers(self.user)
        self.client.credentials(**headers)
        
        response = self.client.get(f"/api/datasets/{self.dataset.id}/preview/")
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证响应结构
        expected_schema = {
            "code": int,
            "msg": str,
            "data": {
                "format": str,
                "headers": [str],
                "rows": [
                    {
                        "id": int,
                        "question": str,
                        "answer": str
                    }
                ],
                "total": int,
                "preview_count": int
            }
        }
        
        self.assertAPIResponse(response, 200)
        self._validate_contract(response.data, expected_schema)


class ModelAPIContractTest(BaseContractTestCase):
    """模型API契约测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.models = ModelFactory.create_batch(3)
    
    def test_model_list_contract(self):
        """测试模型列表API契约"""
        response = self.client.get("/api/models/")
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证响应结构
        expected_schema = [
            {
                "id": int,
                "name": str,
                "company": str,
                "category": str,
                "parameter_size": str,
                "description": str,
                "version": str,
                "official_url": str,
                "paper_url": str,
                "github_url": str,
                "license": str,
                "created_at": str,
                "updated_at": str
            }
        ]
        
        self._validate_contract(response.data, expected_schema)
    
    def test_model_detail_contract(self):
        """测试模型详情API契约"""
        model = self.models[0]
        response = self.client.get(f"/api/models/{model.id}/")
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证响应结构
        expected_schema = {
            "id": int,
            "name": str,
            "company": str,
            "category": str,
            "parameter_size": str,
            "description": str,
            "version": str,
            "official_url": str,
            "paper_url": str,
            "github_url": str,
            "license": str,
            "created_at": str,
            "updated_at": str
        }
        
        self._validate_contract(response.data, expected_schema)
    
    def test_model_follow_contract(self):
        """测试模型关注API契约"""
        user = UserFactory()
        from tests.base import APITestHelper
        headers = APITestHelper.create_auth_headers(user)
        self.client.credentials(**headers)
        
        model = self.models[0]
        response = self.client.post(f"/api/models/{model.id}/follow/")
        
        # 验证响应状态码
        self.assertIn(response.status_code, [200, 201])
        
        # 验证响应结构
        expected_schema = {
            "msg": str
        }
        
        self._validate_contract(response.data, expected_schema)


class TaskAPIContractTest(BaseContractTestCase):
    """任务API契约测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = UserFactory()
        self.task = EvaluationTaskFactory(creator=self.user)
    
    def test_task_list_contract(self):
        """测试任务列表API契约"""
        from tests.base import APITestHelper
        headers = APITestHelper.create_auth_headers(self.user)
        self.client.credentials(**headers)
        
        response = self.client.get("/api/tasks/evaluation-tasks/")
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证响应结构
        expected_schema = [
            {
                "id": int,
                "name": str,
                "description": str,
                "method": str,
                "status": str,
                "progress": int,
                "creator": {
                    "id": int,
                    "username": str
                },
                "dataset": {
                    "id": int,
                    "name": str
                },
                "myModel": {
                    "id": int,
                    "name": str
                },
                "created_at": str,
                "updated_at": str
            }
        ]
        
        self._validate_contract(response.data, expected_schema)
    
    def test_task_detail_contract(self):
        """测试任务详情API契约"""
        from tests.base import APITestHelper
        headers = APITestHelper.create_auth_headers(self.user)
        self.client.credentials(**headers)
        
        response = self.client.get(f"/api/tasks/evaluation-tasks/{self.task.id}/")
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证响应结构
        expected_schema = {
            "id": int,
            "name": str,
            "description": str,
            "method": str,
            "status": str,
            "progress": int,
            "creator": {
                "id": int,
                "username": str,
                "email": str
            },
            "dataset": {
                "id": int,
                "name": str,
                "category": str
            },
            "myModel": {
                "id": int,
                "name": str,
                "company": str
            },
            "created_at": str,
            "updated_at": str
        }
        
        self._validate_contract(response.data, expected_schema)


class ErrorContractTest(BaseContractTestCase):
    """错误响应契约测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
    
    def test_validation_error_contract(self):
        """测试验证错误响应契约"""
        # 测试无效的用户注册数据
        data = {
            "username": "",  # 空用户名
            "email": "invalid-email",  # 无效邮箱
            "password": "123"  # 密码太短
        }
        response = self.client.post("/api/users/register/", data, format="json")
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 400)
        
        # 验证错误响应结构
        expected_schema = {
            "code": int,
            "msg": str,
            "error": str
        }
        
        self._validate_contract(response.data, expected_schema)
    
    def test_not_found_error_contract(self):
        """测试404错误响应契约"""
        response = self.client.get("/api/datasets/99999/")
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 404)
        
        # 验证错误响应结构
        expected_schema = {
            "code": int,
            "msg": str,
            "error": str
        }
        
        self._validate_contract(response.data, expected_schema)
    
    def test_unauthorized_error_contract(self):
        """测试未授权错误响应契约"""
        response = self.client.get("/api/tasks/evaluation-tasks/")
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 403)
        
        # 验证错误响应结构
        expected_schema = {
            "code": int,
            "msg": str,
            "error": str
        }
        
        self._validate_contract(response.data, expected_schema)
    
    def test_forbidden_error_contract(self):
        """测试禁止访问错误响应契约"""
        user = UserFactory()
        other_user = UserFactory()
        
        from tests.base import APITestHelper
        headers = APITestHelper.create_auth_headers(user)
        self.client.credentials(**headers)
        
        # 尝试访问其他用户的私有资源
        private_dataset = DatasetFactory(creator=other_user, is_public=False)
        response = self.client.get(f"/api/datasets/{private_dataset.id}/")
        
        # 验证响应状态码
        self.assertIn(response.status_code, [403, 404])
        
        # 验证错误响应结构
        expected_schema = {
            "code": int,
            "msg": str,
            "error": str
        }
        
        self._validate_contract(response.data, expected_schema)


class PaginationContractTest(BaseContractTestCase):
    """分页响应契约测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        # 创建大量数据
        DatasetFactory.create_batch(25)
    
    def test_pagination_contract(self):
        """测试分页响应契约"""
        response = self.client.get("/api/datasets/?page=1&page_size=10")
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证分页响应结构
        expected_schema = {
            "code": int,
            "msg": str,
            "data": [
                {
                    "id": int,
                    "name": str,
                    "description": str,
                    "category": str,
                    "file_format": str,
                    "is_public": bool,
                    "is_verified": bool,
                    "creator": {
                        "id": int,
                        "username": str
                    },
                    "created_at": str,
                    "updated_at": str
                }
            ],
            "pagination": {
                "page": int,
                "page_size": int,
                "total": int,
                "total_pages": int,
                "has_next": bool,
                "has_previous": bool
            }
        }
        
        self.assertAPIResponse(response, 200)
        self._validate_contract(response.data, expected_schema)
        
        # 验证分页数据
        pagination = response.data["pagination"]
        self.assertEqual(pagination["page"], 1)
        self.assertEqual(pagination["page_size"], 10)
        self.assertEqual(len(response.data["data"]), 10)
        self.assertGreaterEqual(pagination["total"], 25)
        self.assertGreaterEqual(pagination["total_pages"], 3)
        self.assertTrue(pagination["has_next"])
        self.assertFalse(pagination["has_previous"])


class ContractFileGenerator:
    """契约文件生成器 - 生成API契约文档"""
    
    @staticmethod
    def generate_contract_files():
        """生成所有API的契约文件"""
        contracts_dir = "tests/contracts"
        os.makedirs(contracts_dir, exist_ok=True)
        
        # 用户API契约
        user_registration_contract = {
            "endpoint": "/api/users/register/",
            "method": "POST",
            "request": {
                "username": "string",
                "email": "string",
                "password": "string",
                "phone": "string"
            },
            "response": {
                "code": 201,
                "msg": "string",
                "data": {
                    "id": "integer",
                    "username": "string",
                    "email": "string",
                    "phone": "string",
                    "bio": "string",
                    "avatar": "string",
                    "show_followed_models": "boolean",
                    "show_followed_datasets": "boolean",
                    "created_at": "string",
                    "updated_at": "string"
                }
            }
        }
        
        with open(f"{contracts_dir}/user_registration.json", "w", encoding="utf-8") as f:
            json.dump(user_registration_contract, f, indent=2, ensure_ascii=False)
        
        # 数据集API契约
        dataset_list_contract = {
            "endpoint": "/api/datasets/",
            "method": "GET",
            "response": {
                "code": 200,
                "msg": "string",
                "data": [
                    {
                        "id": "integer",
                        "name": "string",
                        "description": "string",
                        "category": "string",
                        "file_format": "string",
                        "is_public": "boolean",
                        "is_verified": "boolean",
                        "file_size": "integer",
                        "sample_count": "integer",
                        "creator": {
                            "id": "integer",
                            "username": "string"
                        },
                        "created_at": "string",
                        "updated_at": "string"
                    }
                ]
            }
        }
        
        with open(f"{contracts_dir}/dataset_list.json", "w", encoding="utf-8") as f:
            json.dump(dataset_list_contract, f, indent=2, ensure_ascii=False)
        
        # 模型API契约
        model_list_contract = {
            "endpoint": "/api/models/",
            "method": "GET",
            "response": [
                {
                    "id": "integer",
                    "name": "string",
                    "company": "string",
                    "category": "string",
                    "parameter_size": "string",
                    "description": "string",
                    "version": "string",
                    "official_url": "string",
                    "paper_url": "string",
                    "github_url": "string",
                    "license": "string",
                    "created_at": "string",
                    "updated_at": "string"
                }
            ]
        }
        
        with open(f"{contracts_dir}/model_list.json", "w", encoding="utf-8") as f:
            json.dump(model_list_contract, f, indent=2, ensure_ascii=False)
        
        # 任务API契约
        task_list_contract = {
            "endpoint": "/api/tasks/evaluation-tasks/",
            "method": "GET",
            "response": [
                {
                    "id": "integer",
                    "name": "string",
                    "description": "string",
                    "method": "string",
                    "status": "string",
                    "progress": "integer",
                    "creator": {
                        "id": "integer",
                        "username": "string"
                    },
                    "dataset": {
                        "id": "integer",
                        "name": "string"
                    },
                    "myModel": {
                        "id": "integer",
                        "name": "string"
                    },
                    "created_at": "string",
                    "updated_at": "string"
                }
            ]
        }
        
        with open(f"{contracts_dir}/task_list.json", "w", encoding="utf-8") as f:
            json.dump(task_list_contract, f, indent=2, ensure_ascii=False)
        
        # 错误响应契约
        error_contract = {
            "error_response": {
                "code": "integer",
                "msg": "string",
                "error": "string"
            }
        }
        
        with open(f"{contracts_dir}/error_response.json", "w", encoding="utf-8") as f:
            json.dump(error_contract, f, indent=2, ensure_ascii=False)
        
        # 分页响应契约
        pagination_contract = {
            "pagination_response": {
                "code": "integer",
                "msg": "string",
                "data": "array",
                "pagination": {
                    "page": "integer",
                    "page_size": "integer",
                    "total": "integer",
                    "total_pages": "integer",
                    "has_next": "boolean",
                    "has_previous": "boolean"
                }
            }
        }
        
        with open(f"{contracts_dir}/pagination_response.json", "w", encoding="utf-8") as f:
            json.dump(pagination_contract, f, indent=2, ensure_ascii=False)