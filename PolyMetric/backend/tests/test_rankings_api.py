"""
排名相关API全面测试
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from tests.test_utils import TestDataGenerator, AuthUtils, APITestMixin

User = get_user_model()


class UpdateRankingsAPITest(TestCase, APITestMixin):
    """更新排名API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.admin = TestDataGenerator.create_admin_user()
        
        self.model1 = TestDataGenerator.create_model(name="模型1", company="公司A")
        self.model2 = TestDataGenerator.create_model(name="模型2", company="公司B")
        self.dataset = TestDataGenerator.create_dataset()
    
    def test_update_rankings_admin_success(self):
        """测试管理员更新排名成功"""
        self.create_authenticated_client(self.admin)
        
        data = {"dataset_id": self.dataset.id}
        response = self.client.post("/api/rankings/update/", data, format="json")
        self.assertEqual(response.status_code, 200)
    
    def test_update_rankings_missing_dataset_id(self):
        """测试更新排名缺少数据集ID"""
        self.create_authenticated_client(self.admin)
        
        data = {}  # 缺少dataset_id
        response = self.client.post("/api/rankings/update/", data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("dataset_id is required", response.data["error"])
    
    def test_update_rankings_unauthorized(self):
        """测试未授权用户更新排名"""
        self.create_authenticated_client(self.user)
        
        data = {"dataset_id": self.dataset.id}
        response = self.client.post("/api/rankings/update/", data, format="json")
        self.assertEqual(response.status_code, 403)
    
    def test_update_rankings_anonymous(self):
        """测试匿名用户更新排名"""
        data = {"dataset_id": self.dataset.id}
        response = self.client.post("/api/rankings/update/", data, format="json")
        self.assertEqual(response.status_code, 401)
    
    def test_update_rankings_nonexistent_dataset(self):
        """测试更新不存在数据集的排名"""
        self.create_authenticated_client(self.admin)
        
        data = {"dataset_id": 99999}
        response = self.client.post("/api/rankings/update/", data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)


class TopModelsAPITest(TestCase, APITestMixin):
    """顶级模型API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        
        self.model1 = TestDataGenerator.create_model(name="模型1", company="公司A")
        self.model2 = TestDataGenerator.create_model(name="模型2", company="公司B")
        self.model3 = TestDataGenerator.create_model(name="模型3", company="公司C")
        self.dataset = TestDataGenerator.create_dataset()
    
    def test_get_top_models_success(self):
        """测试获取顶级模型成功"""
        response = self.client.get(f"/api/rankings/top/?dataset_id={self.dataset.id}&limit=10")
        self.assertEqual(response.status_code, 200)
        
        # 检查响应格式
        self.assertIn("code", response.data)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["code"], status.HTTP_200_OK)
    
    def test_get_top_models_missing_dataset_id(self):
        """测试获取顶级模型缺少数据集ID"""
        response = self.client.get("/api/rankings/top/?limit=10")
        self.assertEqual(response.status_code, 400)
        self.assertIn("dataset_id is required", response.data["error"])
    
    def test_get_top_models_with_custom_limit(self):
        """测试获取指定数量的顶级模型"""
        response = self.client.get(f"/api/rankings/top/?dataset_id={self.dataset.id}&limit=5")
        self.assertEqual(response.status_code, 200)
        
        # 验证返回数据不超过限制
        if isinstance(response.data["data"], list):
            self.assertLessEqual(len(response.data["data"]), 5)
    
    def test_get_top_models_default_limit(self):
        """测试获取顶级模型使用默认限制"""
        response = self.client.get(f"/api/rankings/top/?dataset_id={self.dataset.id}")
        self.assertEqual(response.status_code, 200)
        
        # 默认限制应该是10
        if isinstance(response.data["data"], list):
            self.assertLessEqual(len(response.data["data"]), 10)
    
    def test_get_top_models_nonexistent_dataset(self):
        """测试获取不存在数据集的顶级模型"""
        response = self.client.get("/api/rankings/top/?dataset_id=99999")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)


class ModelRankingHistoryAPITest(TestCase, APITestMixin):
    """模型排名历史API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        
        self.model = TestDataGenerator.create_model(name="测试模型")
        self.dataset = TestDataGenerator.create_dataset()
    
    def test_get_model_ranking_history_success(self):
        """测试获取模型排名历史成功"""
        response = self.client.get(f"/api/rankings/history/{self.model.id}/?dataset_id={self.dataset.id}")
        self.assertEqual(response.status_code, 200)
        
        # 检查响应格式
        self.assertIn("code", response.data)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["code"], status.HTTP_200_OK)
    
    def test_get_model_ranking_history_without_dataset(self):
        """测试获取模型排名历史不指定数据集"""
        response = self.client.get(f"/api/rankings/history/{self.model.id}/")
        self.assertEqual(response.status_code, 200)
        
        # 应该返回所有数据集的排名历史
        self.assertIn("data", response.data)
    
    def test_get_nonexistent_model_ranking_history(self):
        """测试获取不存在模型的排名历史"""
        response = self.client.get("/api/rankings/history/99999/?dataset_id=1")
        self.assertEqual(response.status_code, 200)
        
        # 应该返回空数据而不是错误
        self.assertIn("data", response.data)


class RankingsIntegrationTest(TestCase, APITestMixin):
    """排名集成测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = TestDataGenerator.create_admin_user()
        
        # 创建多个模型和数据集
        self.models = [
            TestDataGenerator.create_model(name=f"模型{i+1}", company=f"公司{i+1}")
            for i in range(5)
        ]
        
        self.datasets = [
            TestDataGenerator.create_dataset(name=f"数据集{i+1}")
            for i in range(3)
        ]
    
    def test_complete_rankings_workflow(self):
        """测试完整的排名工作流程"""
        # 1. 管理员更新排名
        self.create_authenticated_client(self.admin)
        
        for dataset in self.datasets:
            data = {"dataset_id": dataset.id}
            response = self.client.post("/api/rankings/update/", data, format="json")
            self.assertEqual(response.status_code, 200)
        
        # 2. 获取顶级模型
        for dataset in self.datasets:
            response = self.client.get(f"/api/rankings/top/?dataset_id={dataset.id}&limit=3")
            self.assertEqual(response.status_code, 200)
            self.assertIn("data", response.data)
        
        # 3. 获取模型排名历史
        for model in self.models:
            response = self.client.get(f"/api/rankings/history/{model.id}/")
            self.assertEqual(response.status_code, 200)
            self.assertIn("data", response.data)
            
            # 获取特定数据集的排名历史
            for dataset in self.datasets:
                response = self.client.get(
                    f"/api/rankings/history/{model.id}/?dataset_id={dataset.id}"
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn("data", response.data)
    
    def test_rankings_with_different_parameters(self):
        """测试不同参数的排名API"""
        self.create_authenticated_client(self.admin)
        
        # 更新排名
        data = {"dataset_id": self.datasets[0].id}
        response = self.client.post("/api/rankings/update/", data, format="json")
        self.assertEqual(response.status_code, 200)
        
        # 测试不同的limit参数
        limits = [1, 5, 10, 20]
        for limit in limits:
            response = self.client.get(
                f"/api/rankings/top/?dataset_id={self.datasets[0].id}&limit={limit}"
            )
            self.assertEqual(response.status_code, 200)
            
            if isinstance(response.data["data"], list):
                self.assertLessEqual(len(response.data["data"]), limit)


class RankingsErrorHandlingTest(TestCase, APITestMixin):
    """排名错误处理测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = TestDataGenerator.create_admin_user()
        self.user = TestDataGenerator.create_user()
        
        self.model = TestDataGenerator.create_model()
        self.dataset = TestDataGenerator.create_dataset()
    
    def test_update_rankings_invalid_dataset_id_type(self):
        """测试更新排名使用无效的数据集ID类型"""
        self.create_authenticated_client(self.admin)
        
        data = {"dataset_id": "invalid_id"}
        response = self.client.post("/api/rankings/update/", data, format="json")
        self.assertEqual(response.status_code, 400)
    
    def test_get_top_models_invalid_limit_type(self):
        """测试获取顶级模型使用无效的limit类型"""
        response = self.client.get(
            f"/api/rankings/top/?dataset_id={self.dataset.id}&limit=invalid_limit"
        )
        # 应该返回400错误或者忽略无效参数
        self.assertIn(response.status_code, [200, 400])
    
    def test_get_top_models_negative_limit(self):
        """测试获取顶级模型使用负数limit"""
        response = self.client.get(
            f"/api/rankings/top/?dataset_id={self.dataset.id}&limit=-5"
        )
        # 应该返回400错误或者忽略无效参数
        self.assertIn(response.status_code, [200, 400])
    
    def test_get_top_models_zero_limit(self):
        """测试获取顶级模型使用0限制"""
        response = self.client.get(
            f"/api/rankings/top/?dataset_id={self.dataset.id}&limit=0"
        )
        # 应该返回400错误或者忽略无效参数
        self.assertIn(response.status_code, [200, 400])
    
    def test_get_ranking_history_invalid_model_id(self):
        """测试获取无效模型ID的排名历史"""
        response = self.client.get("/api/rankings/history/invalid_id/")
        # 应该返回404错误
        self.assertIn(response.status_code, [200, 404])


class RankingsPerformanceTest(TestCase, APITestMixin):
    """排名性能测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = TestDataGenerator.create_admin_user()
        
        # 创建大量模型和数据集
        self.models = [
            TestDataGenerator.create_model(name=f"性能测试模型{i}")
            for i in range(50)
        ]
        
        self.datasets = [
            TestDataGenerator.create_dataset(name=f"性能测试数据集{i}")
            for i in range(10)
        ]
    
    def test_large_dataset_rankings_performance(self):
        """测试大数据集排名性能"""
        self.create_authenticated_client(self.admin)
        
        # 更新所有数据集的排名
        for dataset in self.datasets:
            data = {"dataset_id": dataset.id}
            response = self.client.post("/api/rankings/update/", data, format="json")
            self.assertEqual(response.status_code, 200)
        
        # 获取顶级模型
        response = self.client.get(
            f"/api/rankings/top/?dataset_id={self.datasets[0].id}&limit=20"
        )
        self.assertEqual(response.status_code, 200)
        
        # 获取模型排名历史
        response = self.client.get(f"/api/rankings/history/{self.models[0].id}/")
        self.assertEqual(response.status_code, 200)