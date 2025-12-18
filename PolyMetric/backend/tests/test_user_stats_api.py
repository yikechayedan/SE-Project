"""
用户统计API测试
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from tests.test_utils import TestDataGenerator, AuthUtils, APITestMixin

User = get_user_model()


class UserStatsAPITest(TestCase, APITestMixin):
    """用户统计API测试"""
    
    def setUp(self):
        self.client = APIClient()
        # 创建一些测试用户
        self.user1 = TestDataGenerator.create_user(username="user1")
        self.user2 = TestDataGenerator.create_user(username="user2")
        self.user3 = TestDataGenerator.create_user(username="user3")
    
    def test_user_stats_unauthenticated(self):
        """测试未认证用户访问统计API"""
        response = self.client.get("/api/users/stats/")
        self.assertAPISuccess(response, 200, expected_code=200)
        
        # 检查响应数据结构
        self.assertIn("data", response.data)
        self.assertIn("total_users", response.data["data"])
        self.assertIn("online_users", response.data["data"])
        
        # 验证总用户数
        self.assertEqual(response.data["data"]["total_users"], 3)
        
        # 验证在线用户数（应该是0，因为没有用户最近登录）
        self.assertEqual(response.data["data"]["online_users"], 0)
    
    def test_user_stats_authenticated(self):
        """测试已认证用户访问统计API"""
        self.create_authenticated_client(self.user1)
        
        response = self.client.get("/api/users/stats/")
        self.assertAPISuccess(response, 200, expected_code=200)
        
        # 检查响应数据结构
        self.assertIn("data", response.data)
        self.assertIn("total_users", response.data["data"])
        self.assertIn("online_users", response.data["data"])
        
        # 验证总用户数
        self.assertEqual(response.data["data"]["total_users"], 3)
        
        # 验证在线用户数（至少应该是1，因为当前用户正在访问）
        self.assertGreaterEqual(response.data["data"]["online_users"], 1)
    
    def test_user_stats_with_recent_login(self):
        """测试有用户最近登录的统计"""
        # 更新一个用户的最后登录时间为5分钟前
        recent_time = timezone.now() - timedelta(minutes=5)
        self.user1.last_login = recent_time
        self.user1.save()
        
        # 更新另一个用户的最后登录时间为20分钟前（应该不算在线）
        old_time = timezone.now() - timedelta(minutes=20)
        self.user2.last_login = old_time
        self.user2.save()
        
        response = self.client.get("/api/users/stats/")
        self.assertAPISuccess(response, 200, expected_code=200)
        
        # 验证总用户数
        self.assertEqual(response.data["data"]["total_users"], 3)
        
        # 验证在线用户数（应该是1，只有user1在15分钟内登录过）
        self.assertEqual(response.data["data"]["online_users"], 1)
    
    def test_user_stats_multiple_recent_logins(self):
        """测试多个用户最近登录的统计"""
        # 更新多个用户的最后登录时间为5分钟前
        recent_time = timezone.now() - timedelta(minutes=5)
        self.user1.last_login = recent_time
        self.user1.save()
        
        self.user2.last_login = recent_time
        self.user2.save()
        
        # 第三个用户的最后登录时间为20分钟前
        old_time = timezone.now() - timedelta(minutes=20)
        self.user3.last_login = old_time
        self.user3.save()
        
        response = self.client.get("/api/users/stats/")
        self.assertAPISuccess(response, 200, expected_code=200)
        
        # 验证总用户数
        self.assertEqual(response.data["data"]["total_users"], 3)
        
        # 验证在线用户数（应该是2，user1和user2在15分钟内登录过）
        self.assertEqual(response.data["data"]["online_users"], 2)
    
    def test_user_stats_response_format(self):
        """测试响应格式是否符合要求"""
        response = self.client.get("/api/users/stats/")
        
        # 检查响应格式
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["code"], 200)
        self.assertEqual(response.data["msg"], "success")
        
        # 检查data字段
        self.assertIn("data", response.data)
        data = response.data["data"]
        
        # 检查必需字段
        self.assertIn("total_users", data)
        self.assertIn("online_users", data)
        
        # 检查字段类型
        self.assertIsInstance(data["total_users"], int)
        self.assertIsInstance(data["online_users"], int)
        
        # 检查数值合理性
        self.assertGreaterEqual(data["total_users"], 0)
        self.assertGreaterEqual(data["online_users"], 0)
        self.assertLessEqual(data["online_users"], data["total_users"])