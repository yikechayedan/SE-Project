"""
测试在线用户统计修复
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from tests.test_utils import TestDataGenerator, AuthUtils, APITestMixin
import json

User = get_user_model()


class OnlineUsersFixTest(TransactionTestCase, APITestMixin):
    """测试在线用户统计修复"""
    
    def setUp(self):
        self.client = APIClient()
        # 创建一些测试用户
        self.user1 = TestDataGenerator.create_user(username="user1", password="password123")
        self.user2 = TestDataGenerator.create_user(username="user2", password="password123")
        self.user3 = TestDataGenerator.create_user(username="user3", password="password123")
    
    def test_custom_login_view_updates_last_login(self):
        """测试自定义登录视图是否更新最后登录时间"""
        # 记录登录前的last_login
        old_last_login = self.user1.last_login
        
        # 使用自定义登录视图登录
        response = self.client.post("/api/users/login/", {
            "username": "user1",
            "password": "password123"
        }, format="json")
        
        # 验证登录成功
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["code"], 200)
        
        # 刷新用户对象，检查last_login是否更新
        self.user1.refresh_from_db()
        
        # 验证last_login已更新
        self.assertIsNotNone(self.user1.last_login)
        if old_last_login:
            self.assertGreater(self.user1.last_login, old_last_login)
    
    def test_middleware_updates_last_login_on_activity(self):
        """测试中间件是否在用户活跃时更新最后登录时间"""
        # 先登录用户
        self.create_authenticated_client(self.user1)
        
        # 设置一个较早的last_login时间
        old_time = timezone.now() - timedelta(minutes=10)
        User.objects.filter(id=self.user1.id).update(last_login=old_time)
        
        # 刷新用户对象
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.last_login, old_time)
        
        # 发起一个API请求（应该触发中间件更新last_login）
        response = self.client.get("/api/users/stats/")
        
        # 验证请求成功
        self.assertEqual(response.status_code, 200)
        
        # 刷新用户对象，检查last_login是否更新
        self.user1.refresh_from_db()
        
        # 验证last_login已更新
        self.assertGreater(self.user1.last_login, old_time)
    
    def test_online_users_count_after_login(self):
        """测试登录后在线用户数统计"""
        # 确保初始状态下没有用户最近登录
        old_time = timezone.now() - timedelta(hours=1)
        User.objects.all().update(last_login=old_time)
        
        # 检查初始在线用户数
        response = self.client.get("/api/users/stats/")
        self.assertEqual(response.data["data"]["online_users"], 0)
        
        # 登录用户1
        self.client.post("/api/users/login/", {
            "username": "user1",
            "password": "password123"
        }, format="json")
        
        # 检查在线用户数（应该至少是1）
        response = self.client.get("/api/users/stats/")
        self.assertGreaterEqual(response.data["data"]["online_users"], 1)
    
    def test_multiple_users_online_count(self):
        """测试多个用户在线的统计"""
        # 登录用户1
        self.client.post("/api/users/login/", {
            "username": "user1",
            "password": "password123"
        }, format="json")
        
        # 使用新的客户端登录用户2
        client2 = APIClient()
        client2.post("/api/users/login/", {
            "username": "user2",
            "password": "password123"
        }, format="json")
        
        # 检查在线用户数（应该至少是2）
        response = self.client.get("/api/users/stats/")
        self.assertGreaterEqual(response.data["data"]["online_users"], 2)
    
    def test_online_users_timeout(self):
        """测试用户超时后不计入在线用户"""
        # 登录用户1
        self.client.post("/api/users/login/", {
            "username": "user1",
            "password": "password123"
        }, format="json")
        
        # 设置一个超过15分钟的last_login时间
        old_time = timezone.now() - timedelta(minutes=20)
        User.objects.filter(id=self.user1.id).update(last_login=old_time)
        
        # 检查在线用户数（应该是0，因为用户1已经超时）
        response = self.client.get("/api/users/stats/")
        self.assertEqual(response.data["data"]["online_users"], 0)