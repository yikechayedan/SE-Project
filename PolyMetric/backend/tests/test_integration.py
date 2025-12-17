"""
集成测试 - 测试各个模块之间的交互
"""
import json
import tempfile
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from tests.test_utils import TestDataGenerator, AuthUtils, APITestMixin

User = get_user_model()


class UserDatasetIntegrationTest(TestCase, APITestMixin):
    """用户和数据集集成测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = TestDataGenerator.create_user(username="user1", show_followed_datasets=True)
        self.user2 = TestDataGenerator.create_user(username="user2", show_followed_datasets=False)
        self.admin = TestDataGenerator.create_admin_user()
    
    def test_user_dataset_workflow(self):
        """测试用户-数据集完整工作流程"""
        # 1. 用户1创建数据集
        self.create_authenticated_client(self.user1)
        
        test_file = SimpleUploadedFile(
            "test.json", 
            json.dumps([
                {"id": 1, "question": "测试问题1", "answer": "测试答案1"},
                {"id": 2, "question": "测试问题2", "answer": "测试答案2"}
            ]).encode('utf-8'),
            content_type="application/json"
        )
        
        dataset_data = {
            "name": "用户1的数据集",
            "description": "用户1创建的测试数据集",
            "category": "text",
            "file_format": "json",
            "is_public": True,
            "file": test_file
        }
        response = self.client.post("/api/datasets/", dataset_data, format="multipart")
        self.assertAPISuccess(response, 201)
        dataset_id = response.data["data"]["id"]
        
        # 2. 用户2关注用户1的数据集
        self.create_authenticated_client(self.user2)
        response = self.client.post(f"/api/datasets/{dataset_id}/follow/")
        self.assertAPISuccess(response, 201)
        
        # 3. 用户2查看自己的关注列表
        response = self.client.get("/api/datasets/followed/")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["id"], dataset_id)
        
        # 4. 用户1查看用户2的关注列表（公开）
        self.create_authenticated_client(self.user1)
        response = self.client.get(f"/api/datasets/followed/?user_id={self.user2.id}")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]), 1)
        
        # 5. 用户2取消关注数据集
        self.create_authenticated_client(self.user2)
        response = self.client.delete(f"/api/datasets/{dataset_id}/follow/")
        self.assertAPISuccess(response, 200)
        
        # 6. 验证关注列表已更新
        response = self.client.get("/api/datasets/followed/")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]), 0)
    
    def test_dataset_privacy_settings(self):
        """测试数据集隐私设置"""
        # 1. 创建数据集
        self.create_authenticated_client(self.user1)
        dataset = TestDataGenerator.create_dataset(
            name="隐私测试数据集",
            creator=self.user1,
            is_public=False
        )
        
        # 2. 匿名用户无法访问私有数据集
        self.client.credentials()
        response = self.client.get(f"/api/datasets/{dataset.id}/")
        self.assertAPIError(response, 403)
        
        # 3. 其他用户无法访问私有数据集
        self.create_authenticated_client(self.user2)
        response = self.client.get(f"/api/datasets/{dataset.id}/")
        self.assertAPIError(response, 403)
        
        # 4. 创建者可以访问自己的私有数据集
        self.create_authenticated_client(self.user1)
        response = self.client.get(f"/api/datasets/{dataset.id}/")
        self.assertAPISuccess(response, 200)
        
        # 5. 管理员可以访问所有数据集
        self.create_authenticated_client(self.admin)
        response = self.client.get(f"/api/datasets/{dataset.id}/")
        self.assertAPISuccess(response, 200)


class UserModelIntegrationTest(TestCase, APITestMixin):
    """用户和模型集成测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = TestDataGenerator.create_user(username="user1", show_followed_models=True)
        self.user2 = TestDataGenerator.create_user(username="user2", show_followed_models=False)
        self.admin = TestDataGenerator.create_admin_user()
        
        self.model1 = TestDataGenerator.create_model(name="模型1", company="公司A")
        self.model2 = TestDataGenerator.create_model(name="模型2", company="公司B")
    
    def test_user_model_workflow(self):
        """测试用户-模型完整工作流程"""
        # 1. 用户1关注模型1
        self.create_authenticated_client(self.user1)
        response = self.client.post(f"/api/models/{self.model1.id}/follow/")
        self.assertIn(response.status_code, [200, 201])
        
        # 2. 用户1关注模型2
        response = self.client.post(f"/api/models/{self.model2.id}/follow/")
        self.assertIn(response.status_code, [200, 201])
        
        # 3. 用户1查看自己的关注列表
        response = self.client.get("/api/models/followed/")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]), 2)
        
        # 4. 用户2关注模型1
        self.create_authenticated_client(self.user2)
        response = self.client.post(f"/api/models/{self.model1.id}/follow/")
        self.assertIn(response.status_code, [200, 201])
        
        # 5. 用户1查看用户2的关注列表（私有）
        self.create_authenticated_client(self.user1)
        response = self.client.get(f"/api/models/followed/?user_id={self.user2.id}")
        self.assertAPISuccess(response, 200)
        self.assertEqual(response.data["msg"], "该用户未公开关注的模型")
        self.assertIsNone(response.data["data"])
        
        # 6. 用户2公开关注列表
        self.user2.show_followed_models = True
        self.user2.save()
        
        # 7. 用户1再次查看用户2的关注列表（公开）
        response = self.client.get(f"/api/models/followed/?user_id={self.user2.id}")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["id"], self.model1.id)
    
    def test_model_list_with_follow_status(self):
        """测试带关注状态的模型列表"""
        # 1. 用户1关注模型1
        self.create_authenticated_client(self.user1)
        response = self.client.post(f"/api/models/{self.model1.id}/follow/")
        self.assertIn(response.status_code, [200, 201])
        
        # 2. 获取带关注状态的模型列表
        response = self.client.get("/api/models/?with_follow=true")
        self.assertEqual(response.status_code, 200)
        
        # 3. 验证关注状态
        model1_data = next(m for m in response.data if m["id"] == self.model1.id)
        model2_data = next(m for m in response.data if m["id"] == self.model2.id)
        
        self.assertTrue(model1_data["is_followed"])
        self.assertFalse(model2_data["is_followed"])


class TaskDatasetModelIntegrationTest(TestCase, APITestMixin):
    """任务、数据集和模型集成测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.reviewer = TestDataGenerator.create_user()
        
        self.model = TestDataGenerator.create_model(name="评测测试模型")
        self.dataset = TestDataGenerator.create_dataset(
            name="评测测试数据集",
            creator=self.user
        )
        
        # 创建带文件的数据集
        temp_file = TestDataGenerator.create_temp_file()
        with open(temp_file, 'rb') as f:
            uploaded_file = SimpleUploadedFile(
                "test.json",
                f.read(),
                content_type="application/json"
            )
        
        self.dataset.file_path = uploaded_file
        self.dataset.save()
    
    def test_complete_evaluation_workflow(self):
        """测试完整的评测工作流程"""
        # 1. 创建评测任务
        self.create_authenticated_client(self.user)
        
        task_data = {
            "name": "集成评测任务",
            "description": "集成测试评测任务",
            "method": "objective",
            "myModel": self.model.id,
            "dataset": self.dataset.id
        }
        response = self.client.post("/api/tasks/evaluation-tasks/", task_data, format="json")
        self.assertAPISuccess(response, 201)
        task_id = response.data["id"]
        
        # 2. 获取任务详情
        response = self.client.get(f"/api/tasks/evaluation-tasks/{task_id}/")
        self.assertAPISuccess(response, 200)
        self.assertEqual(response.data["name"], "集成评测任务")
        
        # 3. 运行评测任务
        run_data = {"task_id": task_id}
        response = self.client.post("/api/tasks/run-task/", run_data, format="json")
        self.assertIn(response.status_code, [200, 400, 500])
        
        # 4. 获取待评测项
        response = self.client.get(f"/api/tasks/get-pending-items?task={task_id}&reviewer={self.reviewer.id}")
        self.assertEqual(response.status_code, 200)
        
        if response.data["pending_count"] > 0:
            item_id = response.data["pengdingItem_ids"][0]
            
            # 5. 获取评测项详情
            response = self.client.get(f"/api/tasks/get-item-detail?task={task_id}&itemID={item_id}")
            self.assertEqual(response.status_code, 200)
            
            # 6. 提交评分（如果是主观评测）
            if response.data["method"] == "subjective":
                score_data = {
                    "myModel": self.model.id,
                    "dataset": self.dataset.id,
                    "reviewer": self.reviewer.id,
                    "itemID": item_id,
                    "score": 8
                }
                response = self.client.post(f"/api/tasks/evaluation-tasks/{task_id}/", score_data, format="json")
                self.assertEqual(response.status_code, 200)
        
        # 7. 更新任务
        update_data = {"name": "更新后的集成评测任务"}
        response = self.client.patch(f"/api/tasks/evaluation-tasks/{task_id}/", update_data, format="json")
        self.assertAPISuccess(response, 200)
        
        # 8. 删除任务
        response = self.client.delete(f"/api/tasks/evaluation-tasks/{task_id}/")
        self.assertEqual(response.status_code, 204)


class SystemEventsIntegrationTest(TestCase, APITestMixin):
    """系统事件集成测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.admin = TestDataGenerator.create_admin_user()
    
    def test_system_events_from_all_modules(self):
        """测试所有模块产生的系统事件"""
        from apps.system.models import SystemEvent
        
        # 1. 创建数据集
        dataset = TestDataGenerator.create_dataset(
            name="集成测试数据集",
            creator=self.user
        )
        
        # 2. 创建模型
        model = TestDataGenerator.create_model(
            name="集成测试模型",
            company="集成测试公司"
        )
        
        # 3. 创建评测任务
        task = TestDataGenerator.create_evaluation_task(
            name="集成测试任务",
            creator=self.user,
            model=model,
            dataset=dataset
        )
        
        # 4. 获取新闻流
        response = self.client.get("/api/system/news/")
        self.assertEqual(response.status_code, 200)
        
        # 5. 验证事件存在
        events = response.data["data"]
        event_contents = [event.get("content", "") for event in events]
        
        # 验证数据集事件
        dataset_found = any(dataset.name in content for content in event_contents)
        self.assertTrue(dataset_found, "未找到数据集相关事件")
        
        # 验证模型事件
        model_found = any(model.name in content for content in event_contents)
        self.assertTrue(model_found, "未找到模型相关事件")
        
        # 6. 验证数据库中的事件
        dataset_events = SystemEvent.objects.filter(event_type='dataset_upload')
        model_events = SystemEvent.objects.filter(event_type='model_add')
        
        self.assertGreater(dataset_events.count(), 0)
        self.assertGreater(model_events.count(), 0)


class CrossModuleIntegrationTest(TestCase, APITestMixin):
    """跨模块集成测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = TestDataGenerator.create_user(username="user1")
        self.user2 = TestDataGenerator.create_user(username="user2")
        self.admin = TestDataGenerator.create_admin_user()
        
        self.model = TestDataGenerator.create_model(name="跨模块测试模型")
        self.dataset = TestDataGenerator.create_dataset(
            name="跨模块测试数据集",
            creator=self.user1
        )
    
    def test_user_follows_user_follows_dataset_follows_model(self):
        """测试用户关注用户，用户关注数据集，用户关注模型的完整流程"""
        # 1. 用户2关注用户1
        self.create_authenticated_client(self.user2)
        response = self.client.post(f"/api/users/{self.user1.id}/follow/")
        self.assertAPISuccess(response, 201)
        
        # 2. 用户2关注用户1的数据集
        response = self.client.post(f"/api/datasets/{self.dataset.id}/follow/")
        self.assertAPISuccess(response, 201)
        
        # 3. 用户2关注模型
        response = self.client.post(f"/api/models/{self.model.id}/follow/")
        self.assertIn(response.status_code, [200, 201])
        
        # 4. 验证所有关注关系
        # 用户关注关系
        from apps.users.models import UserFollow
        user_follow = UserFollow.objects.filter(
            follower=self.user2, 
            followed=self.user1
        ).exists()
        self.assertTrue(user_follow)
        
        # 数据集关注关系
        from apps.datasets.models import DatasetFollow
        dataset_follow = DatasetFollow.objects.filter(
            user=self.user2, 
            dataset=self.dataset
        ).exists()
        self.assertTrue(dataset_follow)
        
        # 模型关注关系
        from apps.models.models import ModelFollow
        model_follow = ModelFollow.objects.filter(
            user=self.user2, 
            model=self.model
        ).exists()
        self.assertTrue(model_follow)
        
        # 5. 获取用户2的所有关注列表
        followed_users_response = self.client.get("/api/users/followed/")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(followed_users_response["data"]), 1)
        
        followed_datasets_response = self.client.get("/api/datasets/followed/")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(followed_datasets_response["data"]), 1)
        
        followed_models_response = self.client.get("/api/models/followed/")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(followed_models_response["data"]), 1)
    
    def test_privacy_settings_across_modules(self):
        """测试隐私设置在各模块中的影响"""
        # 1. 设置用户2的隐私设置
        self.user2.show_followed_models = False
        self.user2.show_followed_datasets = False
        self.user2.save()
        
        # 2. 用户2关注一些内容
        self.create_authenticated_client(self.user2)
        
        # 关注数据集
        response = self.client.post(f"/api/datasets/{self.dataset.id}/follow/")
        self.assertAPISuccess(response, 201)
        
        # 关注模型
        response = self.client.post(f"/api/models/{self.model.id}/follow/")
        self.assertIn(response.status_code, [200, 201])
        
        # 3. 用户1尝试查看用户2的关注列表
        self.create_authenticated_client(self.user1)
        
        # 查看关注的数据集
        response = self.client.get(f"/api/datasets/followed/?user_id={self.user2.id}")
        self.assertAPISuccess(response, 200)
        self.assertEqual(response.data["msg"], "该用户未公开关注的数据集")
        self.assertIsNone(response.data["data"])
        
        # 查看关注的模型
        response = self.client.get(f"/api/models/followed/?user_id={self.user2.id}")
        self.assertAPISuccess(response, 200)
        self.assertEqual(response.data["msg"], "该用户未公开关注的模型")
        self.assertIsNone(response.data["data"])
        
        # 4. 用户2公开隐私设置
        self.user2.show_followed_models = True
        self.user2.show_followed_datasets = True
        self.user2.save()
        
        # 5. 用户1再次查看用户2的关注列表
        response = self.client.get(f"/api/datasets/followed/?user_id={self.user2.id}")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]), 1)
        
        response = self.client.get(f"/api/models/followed/?user_id={self.user2.id}")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]), 1)


class PerformanceIntegrationTest(TestCase, APITestMixin):
    """性能集成测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.users = [
            TestDataGenerator.create_user(username=f"perf_user{i}")
            for i in range(5)
        ]
        
        self.models = [
            TestDataGenerator.create_model(name=f"性能测试模型{i}")
            for i in range(10)
        ]
        
        self.datasets = [
            TestDataGenerator.create_dataset(
                name=f"性能测试数据集{i}",
                creator=self.users[i % len(self.users)]
            )
            for i in range(10)
        ]
    
    def test_bulk_operations_performance(self):
        """测试批量操作性能"""
        import time
        
        # 1. 批量关注模型
        start_time = time.time()
        self.create_authenticated_client(self.users[0])
        
        for model in self.models:
            response = self.client.post(f"/api/models/{model.id}/follow/")
            self.assertIn(response.status_code, [200, 201])
        
        follow_models_time = time.time() - start_time
        
        # 2. 批量关注数据集
        start_time = time.time()
        
        for dataset in self.datasets:
            response = self.client.post(f"/api/datasets/{dataset.id}/follow/")
            self.assertAPISuccess(response, 201)
        
        follow_datasets_time = time.time() - start_time
        
        # 3. 获取所有关注列表
        start_time = time.time()
        
        response = self.client.get("/api/models/followed/")
        self.assertAPISuccess(response, 200)
        
        response = self.client.get("/api/datasets/followed/")
        self.assertAPISuccess(response, 200)
        
        get_follows_time = time.time() - start_time
        
        # 验证性能在合理范围内（这些是宽松的限制）
        self.assertLess(follow_models_time, 10)  # 关注10个模型应该在10秒内完成
        self.assertLess(follow_datasets_time, 10)  # 关注10个数据集应该在10秒内完成
        self.assertLess(get_follows_time, 5)  # 获取关注列表应该在5秒内完成
        
        # 4. 验证数据一致性
        self.assertEqual(len(response.data["data"]), 10)  # 应该有10个关注的数据集
        
        models_response = self.client.get("/api/models/followed/")
        self.assertEqual(len(models_response.data["data"]), 10)  # 应该有10个关注的模型