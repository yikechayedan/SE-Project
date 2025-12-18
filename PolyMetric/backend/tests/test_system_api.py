"""
系统相关API全面测试
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from tests.test_utils import TestDataGenerator, AuthUtils, APITestMixin

User = get_user_model()


class SystemNewsFeedAPITest(TestCase, APITestMixin):
    """系统新闻流API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.admin = TestDataGenerator.create_admin_user()
        
        # 创建测试数据
        self.model = TestDataGenerator.create_model(name="测试模型")
        self.dataset = TestDataGenerator.create_dataset(name="测试数据集", creator=self.user)
    
    def test_news_feed_anonymous(self):
        """测试匿名用户获取新闻流"""
        response = self.client.get("/api/system/news/")
        self.assertEqual(response.status_code, 200)
        
        # 检查响应格式
        self.assertIn("code", response.data)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["code"], status.HTTP_200_OK)
        
        # 检查数据是列表格式
        self.assertIsInstance(response.data["data"], list)
    
    def test_news_feed_authenticated(self):
        """测试认证用户获取新闻流"""
        self.create_authenticated_client(self.user)
        response = self.client.get("/api/system/news/")
        self.assertEqual(response.status_code, 200)
        
        # 检查响应格式
        self.assertIn("code", response.data)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["code"], status.HTTP_200_OK)
    
    def test_news_feed_data_structure(self):
        """测试新闻流数据结构"""
        response = self.client.get("/api/system/news/")
        self.assertEqual(response.status_code, 200)
        
        # 如果有数据，检查每个事件的结构
        if response.data["data"]:
            event = response.data["data"][0]
            required_fields = ["id", "content", "time", "type", "icon"]
            
            for field in required_fields:
                self.assertIn(field, event, f"缺少字段: {field}")
    
    def test_news_feed_after_dataset_creation(self):
        """测试创建数据集后的新闻流"""
        # 创建数据集
        dataset = TestDataGenerator.create_dataset(
            name="新闻测试数据集",
            creator=self.user
        )
        
        # 获取新闻流
        response = self.client.get("/api/system/news/")
        self.assertEqual(response.status_code, 200)
        
        # 验证数据集创建事件
        if response.data["data"]:
            dataset_events = [
                event for event in response.data["data"]
                if "数据集" in event.get("content", "")
            ]
            self.assertGreater(len(dataset_events), 0)
    
    def test_news_feed_after_model_creation(self):
        """测试创建模型后的新闻流"""
        # 创建模型
        model = TestDataGenerator.create_model(
            name="新闻测试模型",
            company="新闻测试公司"
        )
        
        # 获取新闻流
        response = self.client.get("/api/system/news/")
        self.assertEqual(response.status_code, 200)
        
        # 验证模型创建事件
        if response.data["data"]:
            model_events = [
                event for event in response.data["data"]
                if "模型" in event.get("content", "")
            ]
            self.assertGreater(len(model_events), 0)


class SystemEventAPITest(TestCase, APITestMixin):
    """系统事件API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.admin = TestDataGenerator.create_admin_user()
    
    def test_system_event_creation(self):
        """测试系统事件创建"""
        from apps.system.models import SystemEvent
        
        # 手动创建系统事件
        event = SystemEvent.objects.create(
            event_type='test_event',
            actor_id=self.user.id,
            actor_name=self.user.username,
            target_name='测试目标',
            message='测试系统事件消息'
        )
        
        # 验证事件已创建
        self.assertEqual(event.event_type, 'test_event')
        self.assertEqual(event.actor_id, self.user.id)
        self.assertEqual(event.actor_name, self.user.username)
        self.assertEqual(event.target_name, '测试目标')
        self.assertEqual(event.message, '测试系统事件消息')
    
    def test_system_event_str_representation(self):
        """测试系统事件字符串表示"""
        from apps.system.models import SystemEvent
        
        event = SystemEvent.objects.create(
            event_type='test_event',
            actor_name='测试用户',
            target_name='测试目标',
            message='测试消息'
        )
        
        # 验证字符串表示
        str_repr = str(event)
        self.assertIn('test_event', str_repr)
    
    def test_system_event_ordering(self):
        """测试系统事件排序"""
        from apps.system.models import SystemEvent
        from datetime import datetime, timedelta
        
        # 创建多个事件
        event1 = SystemEvent.objects.create(
            event_type='event1',
            actor_name='用户1',
            target_name='目标1',
            message='消息1'
        )
        
        # 延迟一秒创建第二个事件
        import time
        time.sleep(1)
        
        event2 = SystemEvent.objects.create(
            event_type='event2',
            actor_name='用户2',
            target_name='目标2',
            message='消息2'
        )
        
        # 获取新闻流
        response = self.client.get("/api/system/news/")
        self.assertEqual(response.status_code, 200)
        
        # 验证事件按时间降序排列
        if len(response.data["data"]) >= 2:
            first_event_time = response.data["data"][0].get("time")
            second_event_time = response.data["data"][1].get("time")
            
            # 第一个事件应该比第二个事件新
            self.assertIsNotNone(first_event_time)
            self.assertIsNotNone(second_event_time)


class SystemSignalTest(TestCase, APITestMixin):
    """系统信号测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.admin = TestDataGenerator.create_admin_user()
    
    def test_dataset_upload_signal(self):
        """测试数据集上传信号"""
        from apps.system.models import SystemEvent
        
        # 创建数据集
        dataset = TestDataGenerator.create_dataset(
            name="信号测试数据集",
            creator=self.user
        )
        
        # 验证系统事件已创建
        events = SystemEvent.objects.filter(event_type='dataset_upload')
        self.assertGreater(events.count(), 0)
        
        # 查找相关事件
        related_event = events.filter(
            actor_id=self.user.id,
            target_name=dataset.name
        ).first()
        
        self.assertIsNotNone(related_event)
        self.assertIn(dataset.name, related_event.message)
    
    def test_model_add_signal(self):
        """测试模型添加信号"""
        from apps.system.models import SystemEvent
        
        # 创建模型
        model = TestDataGenerator.create_model(
            name="信号测试模型",
            company="信号测试公司"
        )
        
        # 验证系统事件已创建
        events = SystemEvent.objects.filter(event_type='model_add')
        self.assertGreater(events.count(), 0)
        
        # 查找相关事件
        related_event = events.filter(
            target_name=model.name,
            target_extra=model.company
        ).first()
        
        self.assertIsNotNone(related_event)
        self.assertIn(model.name, related_event.message)
        self.assertIn(model.company, related_event.message)
    
    def test_multiple_events_creation(self):
        """测试多个事件创建"""
        from apps.system.models import SystemEvent
        
        # 创建多个数据集和模型
        datasets = [
            TestDataGenerator.create_dataset(
                name=f"多事件测试数据集{i}",
                creator=self.user
            )
            for i in range(3)
        ]
        
        models = [
            TestDataGenerator.create_model(
                name=f"多事件测试模型{i}",
                company=f"多事件测试公司{i}"
            )
            for i in range(3)
        ]
        
        # 验证所有事件都已创建
        dataset_events = SystemEvent.objects.filter(event_type='dataset_upload')
        model_events = SystemEvent.objects.filter(event_type='model_add')
        
        self.assertGreaterEqual(dataset_events.count(), 3)
        self.assertGreaterEqual(model_events.count(), 3)


class SystemIntegrationTest(TestCase, APITestMixin):
    """系统集成测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = TestDataGenerator.create_user(username="user1")
        self.user2 = TestDataGenerator.create_user(username="user2")
        self.admin = TestDataGenerator.create_admin_user()
    
    def test_complete_system_workflow(self):
        """测试完整的系统工作流程"""
        from apps.system.models import SystemEvent
        
        # 1. 初始状态：获取新闻流
        response = self.client.get("/api/system/news/")
        self.assertEqual(response.status_code, 200)
        initial_count = len(response.data["data"])
        
        # 2. 创建数据集
        dataset = TestDataGenerator.create_dataset(
            name="集成测试数据集",
            creator=self.user1
        )
        
        # 3. 创建模型
        model = TestDataGenerator.create_model(
            name="集成测试模型",
            company="集成测试公司"
        )
        
        # 4. 再次获取新闻流
        response = self.client.get("/api/system/news/")
        self.assertEqual(response.status_code, 200)
        
        # 5. 验证新事件已添加
        self.assertGreater(len(response.data["data"]), initial_count)
        
        # 6. 验证事件内容
        event_contents = [event.get("content", "") for event in response.data["data"]]
        dataset_found = any(dataset.name in content for content in event_contents)
        model_found = any(model.name in content for content in event_contents)
        
        self.assertTrue(dataset_found, "未找到数据集相关事件")
        self.assertTrue(model_found, "未找到模型相关事件")
    
    def test_system_permissions(self):
        """测试系统API权限"""
        # 新闻流API应该允许匿名访问
        response = self.client.get("/api/system/news/")
        self.assertEqual(response.status_code, 200)
        
        # 也应该允许认证用户访问
        self.create_authenticated_client(self.user1)
        response = self.client.get("/api/system/news/")
        self.assertEqual(response.status_code, 200)
        
        # 管理员也应该能访问
        self.create_authenticated_client(self.admin)
        response = self.client.get("/api/system/news/")
        self.assertEqual(response.status_code, 200)
    
    def test_system_data_consistency(self):
        """测试系统数据一致性"""
        from apps.system.models import SystemEvent
        
        # 创建多个用户、数据集和模型
        users = [self.user1, self.user2, self.admin]
        datasets = []
        models = []
        
        for i, user in enumerate(users):
            datasets.append(TestDataGenerator.create_dataset(
                name=f"一致性测试数据集{i}",
                creator=user
            ))
            models.append(TestDataGenerator.create_model(
                name=f"一致性测试模型{i}",
                company=f"一致性测试公司{i}"
            ))
        
        # 获取新闻流
        response = self.client.get("/api/system/news/")
        self.assertEqual(response.status_code, 200)
        
        # 验证每个创建的对象都有对应的事件
        event_contents = [event.get("content", "") for event in response.data["data"]]
        
        for i, dataset in enumerate(datasets):
            dataset_found = any(dataset.name in content for content in event_contents)
            self.assertTrue(dataset_found, f"未找到数据集{i}相关事件")
        
        for i, model in enumerate(models):
            model_found = any(model.name in content for content in event_contents)
            self.assertTrue(model_found, f"未找到模型{i}相关事件")


class SystemPerformanceTest(TestCase, APITestMixin):
    """系统性能测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.users = [
            TestDataGenerator.create_user(username=f"perf_user{i}")
            for i in range(10)
        ]
    
    def test_news_feed_performance_with_many_events(self):
        """测试大量事件的新闻流性能"""
        from apps.system.models import SystemEvent
        
        # 创建大量数据集和模型
        for i in range(50):
            TestDataGenerator.create_dataset(
                name=f"性能测试数据集{i}",
                creator=self.users[i % len(self.users)]
            )
            TestDataGenerator.create_model(
                name=f"性能测试模型{i}",
                company=f"性能测试公司{i}"
            )
        
        # 获取新闻流
        response = self.client.get("/api/system/news/")
        self.assertEqual(response.status_code, 200)
        
        # 验证返回数据量合理（应该有限制）
        self.assertLessEqual(len(response.data["data"]), 50)
        
        # 验证数据格式正确
        if response.data["data"]:
            event = response.data["data"][0]
            required_fields = ["id", "content", "time", "type", "icon"]
            for field in required_fields:
                self.assertIn(field, event)
    
    def test_concurrent_news_feed_access(self):
        """测试并发访问新闻流"""
        import threading
        import time
        
        results = []
        
        def access_news_feed():
            response = self.client.get("/api/system/news/")
            results.append(response.status_code)
        
        # 创建多个线程同时访问
        threads = []
        for i in range(10):
            thread = threading.Thread(target=access_news_feed)
            threads.append(thread)
        
        # 启动所有线程
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # 验证所有请求都成功
        self.assertEqual(len(results), 10)
        self.assertTrue(all(status == 200 for status in results))
        
        # 验证响应时间合理（应该在几秒内完成）
        self.assertLess(end_time - start_time, 10)