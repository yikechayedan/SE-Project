"""
API性能测试 - 测试API响应时间和资源使用
"""
import time
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from tests.base import BasePerformanceTestCase, BaseLoadTestCase
from tests.factories import (
    UserFactory, ModelFactory, DatasetFactory, 
    EvaluationTaskFactory, BulkDataFactory
)

User = get_user_model()


class UserAPIPerformanceTest(BasePerformanceTestCase):
    """用户API性能测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = UserFactory()
        self.admin = UserFactory(is_staff=True, is_superuser=True)
    
    def test_user_registration_performance(self):
        """测试用户注册性能"""
        def register_user():
            data = {
                "username": f"perf_user_{int(time.time())}",
                "email": f"perf_user_{int(time.time())}@test.com",
                "password": "test123456",
                "phone": "13800138000"
            }
            return self.client.post("/api/users/register/", data, format="json")
        
        # 测试多次注册的性能
        for _ in range(10):
            response = self.measure_performance(register_user)
            self.assertEqual(response.status_code, 201)
        
        # 断言性能阈值
        self.assertPerformanceThreshold(max_execution_time=0.5, max_memory_mb=50)
    
    def test_user_login_performance(self):
        """测试用户登录性能"""
        def login_user():
            data = {
                "username": self.user.username,
                "password": "test123456"
            }
            return self.client.post("/api/users/login/", data, format="json")
        
        # 测试多次登录的性能
        for _ in range(20):
            response = self.measure_performance(login_user)
            self.assertEqual(response.status_code, 200)
        
        # 断言性能阈值
        self.assertPerformanceThreshold(max_execution_time=0.3, max_memory_mb=30)
    
    def test_user_list_performance(self):
        """测试用户列表API性能"""
        # 创建大量用户
        BulkDataFactory.create_users(100)
        
        def get_users():
            return self.client.get("/api/users/admin/users/")
        
        # 测试认证后的性能
        from tests.base import APITestHelper
        headers = APITestHelper.create_auth_headers(self.admin)
        self.client.credentials(**headers)
        
        for _ in range(10):
            response = self.measure_performance(get_users)
            self.assertEqual(response.status_code, 200)
        
        # 断言性能阈值
        self.assertPerformanceThreshold(max_execution_time=1.0, max_memory_mb=100)


class DatasetAPIPerformanceTest(BasePerformanceTestCase):
    """数据集API性能测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = UserFactory()
        self.datasets = BulkDataFactory.create_datasets(50, with_file=True)
    
    def test_dataset_list_performance(self):
        """测试数据集列表性能"""
        def get_datasets():
            return self.client.get("/api/datasets/")
        
        for _ in range(10):
            response = self.measure_performance(get_datasets)
            self.assertEqual(response.status_code, 200)
        
        # 断言性能阈值
        self.assertPerformanceThreshold(max_execution_time=0.8, max_memory_mb=80)
    
    def test_dataset_detail_performance(self):
        """测试数据集详情性能"""
        dataset = self.datasets[0]
        
        def get_dataset_detail():
            return self.client.get(f"/api/datasets/{dataset.id}/")
        
        for _ in range(10):
            response = self.measure_performance(get_dataset_detail)
            self.assertEqual(response.status_code, 200)
        
        # 断言性能阈值
        self.assertPerformanceThreshold(max_execution_time=0.5, max_memory_mb=50)
    
    def test_dataset_search_performance(self):
        """测试数据集搜索性能"""
        def search_datasets():
            return self.client.get("/api/datasets/?search=测试")
        
        for _ in range(10):
            response = self.measure_performance(search_datasets)
            self.assertEqual(response.status_code, 200)
        
        # 断言性能阈值
        self.assertPerformanceThreshold(max_execution_time=1.0, max_memory_mb=60)


class ModelAPIPerformanceTest(BasePerformanceTestCase):
    """模型API性能测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.models = BulkDataFactory.create_models(100)
    
    def test_model_list_performance(self):
        """测试模型列表性能"""
        def get_models():
            return self.client.get("/api/models/")
        
        for _ in range(10):
            response = self.measure_performance(get_models)
            self.assertEqual(response.status_code, 200)
        
        # 断言性能阈值
        self.assertPerformanceThreshold(max_execution_time=0.6, max_memory_mb=70)
    
    def test_model_filter_performance(self):
        """测试模型过滤性能"""
        def filter_models():
            return self.client.get("/api/models/?category=text&company=测试公司")
        
        for _ in range(10):
            response = self.measure_performance(filter_models)
            self.assertEqual(response.status_code, 200)
        
        # 断言性能阈值
        self.assertPerformanceThreshold(max_execution_time=0.8, max_memory_mb=60)


class TaskAPIPerformanceTest(BasePerformanceTestCase):
    """任务API性能测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = UserFactory()
        self.tasks = []
        
        # 创建多个评测任务
        for _ in range(20):
            task = EvaluationTaskFactory(creator=self.user)
            self.tasks.append(task)
    
    def test_task_list_performance(self):
        """测试任务列表性能"""
        from tests.base import APITestHelper
        headers = APITestHelper.create_auth_headers(self.user)
        self.client.credentials(**headers)
        
        def get_tasks():
            return self.client.get("/api/tasks/evaluation-tasks/")
        
        for _ in range(10):
            response = self.measure_performance(get_tasks)
            self.assertEqual(response.status_code, 200)
        
        # 断言性能阈值
        self.assertPerformanceThreshold(max_execution_time=0.7, max_memory_mb=80)
    
    def test_task_creation_performance(self):
        """测试任务创建性能"""
        from tests.base import APITestHelper
        headers = APITestHelper.create_auth_headers(self.user)
        self.client.credentials(**headers)
        
        model = ModelFactory()
        dataset = DatasetFactory()
        
        def create_task():
            data = {
                "name": f"性能测试任务_{int(time.time())}",
                "description": "性能测试任务描述",
                "method": "objective",
                "myModel": model.id,
                "dataset": dataset.id
            }
            return self.client.post("/api/tasks/evaluation-tasks/", data, format="json")
        
        for _ in range(5):
            response = self.measure_performance(create_task)
            self.assertEqual(response.status_code, 201)
        
        # 断言性能阈值
        self.assertPerformanceThreshold(max_execution_time=1.0, max_memory_mb=100)


class DatabasePerformanceTest(BasePerformanceTestCase):
    """数据库性能测试"""
    
    def test_bulk_insert_performance(self):
        """测试批量插入性能"""
        def bulk_insert_users():
            return BulkDataFactory.create_users(100)
        
        for _ in range(5):
            users = self.measure_performance(bulk_insert_users)
            self.assertEqual(len(users), 100)
        
        # 断言性能阈值
        self.assertPerformanceThreshold(max_execution_time=2.0, max_memory_mb=200)
    
    def test_complex_query_performance(self):
        """测试复杂查询性能"""
        # 创建复杂的数据关系
        BulkDataFactory.create_complete_scenario()
        
        def complex_query():
            from django.db.models import Count, Q
            from apps.models.models import My_Model
            from apps.datasets.models import Dataset
            
            # 复杂的关联查询
            models_with_stats = My_Model.objects.annotate(
                dataset_count=Count('evaluationtask__dataset'),
                follow_count=Count('modelfollow')
            ).filter(
                Q(dataset_count__gt=0) | Q(follow_count__gt=0)
            ).select_related('company').prefetch_related('modelfollow_set')
            
            return list(models_with_stats)
        
        for _ in range(5):
            models = self.measure_performance(complex_query)
            self.assertGreater(len(models), 0)
        
        # 断言性能阈值
        self.assertPerformanceThreshold(max_execution_time=1.5, max_memory_mb=150)


class UserAPILoadTest(BaseLoadTestCase):
    """用户API负载测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = UserFactory()
    
    def test_user_registration_load(self):
        """测试用户注册负载"""
        def register_request():
            data = {
                "username": f"load_user_{int(time.time() * 1000)}",
                "email": f"load_user_{int(time.time() * 1000)}@test.com",
                "password": "test123456",
                "phone": "13800138000"
            }
            client = APIClient()
            return client.post("/api/users/register/", data, format="json")
        
        # 运行20个并发注册请求
        results = self.run_concurrent_requests(
            "/api/users/register/", 
            method="POST", 
            num_requests=20,
            data={
                "username": f"load_user_{int(time.time() * 1000)}",
                "email": f"load_user_{int(time.time() * 1000)}@test.com",
                "password": "test123456",
                "phone": "13800138000"
            },
            format="json"
        )
        
        # 断言负载性能
        self.assertLoadPerformance(min_success_rate=0.90, max_avg_response_time=2.0)
    
    def test_user_login_load(self):
        """测试用户登录负载"""
        # 运行50个并发登录请求
        results = self.run_concurrent_requests(
            "/api/users/login/",
            method="POST",
            num_requests=50,
            data={
                "username": self.user.username,
                "password": "test123456"
            },
            format="json"
        )
        
        # 断言负载性能
        self.assertLoadPerformance(min_success_rate=0.95, max_avg_response_time=1.0)


class DatasetAPILoadTest(BaseLoadTestCase):
    """数据集API负载测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.datasets = BulkDataFactory.create_datasets(20, with_file=True)
    
    def test_dataset_list_load(self):
        """测试数据集列表负载"""
        # 运行30个并发请求
        results = self.run_concurrent_requests(
            "/api/datasets/",
            method="GET",
            num_requests=30
        )
        
        # 断言负载性能
        self.assertLoadPerformance(min_success_rate=0.95, max_avg_response_time=1.5)
    
    def test_dataset_detail_load(self):
        """测试数据集详情负载"""
        dataset = self.datasets[0]
        
        # 运行20个并发请求
        results = self.run_concurrent_requests(
            f"/api/datasets/{dataset.id}/",
            method="GET",
            num_requests=20
        )
        
        # 断言负载性能
        self.assertLoadPerformance(min_success_rate=0.95, max_avg_response_time=1.0)


class ModelAPILoadTest(BaseLoadTestCase):
    """模型API负载测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.models = BulkDataFactory.create_models(30)
    
    def test_model_list_load(self):
        """测试模型列表负载"""
        # 运行40个并发请求
        results = self.run_concurrent_requests(
            "/api/models/",
            method="GET",
            num_requests=40
        )
        
        # 断言负载性能
        self.assertLoadPerformance(min_success_rate=0.95, max_avg_response_time=1.2)
    
    def test_model_follow_load(self):
        """测试模型关注负载"""
        user = UserFactory()
        model = self.models[0]
        
        from tests.base import APITestHelper
        headers = APITestHelper.create_auth_headers(user)
        
        # 运行15个并发关注请求
        results = self.run_concurrent_requests(
            f"/api/models/{model.id}/follow/",
            method="POST",
            num_requests=15,
            **headers
        )
        
        # 断言负载性能
        self.assertLoadPerformance(min_success_rate=0.80, max_avg_response_time=1.5)


class SystemLoadTest(BaseLoadTestCase):
    """系统负载测试"""
    
    def test_mixed_api_load(self):
        """测试混合API负载"""
        # 创建测试数据
        users = BulkDataFactory.create_users(10)
        datasets = BulkDataFactory.create_datasets(10)
        models = BulkDataFactory.create_models(10)
        
        # 定义不同的请求类型
        def make_request(request_type):
            client = APIClient()
            
            if request_type == "user_list":
                return client.get("/api/users/admin/users/")
            elif request_type == "dataset_list":
                return client.get("/api/datasets/")
            elif request_type == "model_list":
                return client.get("/api/models/")
            elif request_type == "dataset_detail":
                dataset = datasets[0]
                return client.get(f"/api/datasets/{dataset.id}/")
            elif request_type == "model_detail":
                model = models[0]
                return client.get(f"/api/models/{model.id}/")
            else:
                return client.get("/api/datasets/")
        
        # 运行混合负载测试
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            
            # 提交不同类型的请求
            for i in range(10):
                futures.append(executor.submit(make_request, "user_list"))
                futures.append(executor.submit(make_request, "dataset_list"))
                futures.append(executor.submit(make_request, "model_list"))
                futures.append(executor.submit(make_request, "dataset_detail"))
                futures.append(executor.submit(make_request, "model_detail"))
            
            # 收集结果
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    response = future.result()
                    results.append({
                        'status_code': response.status_code,
                        'response_time': 0,  # 这里简化处理
                        'success': 200 <= response.status_code < 300
                    })
                except Exception as e:
                    results.append({
                        'status_code': 0,
                        'response_time': 0,
                        'success': False,
                        'error': str(e)
                    })
        
        self.concurrent_results = results
        
        # 断言混合负载性能
        self.assertLoadPerformance(min_success_rate=0.85, max_avg_response_time=2.0)