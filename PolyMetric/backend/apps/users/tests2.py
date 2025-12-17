from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.users.models import UserFollow

User = get_user_model()

class UserFollowListAndPrivacyTest(APITestCase):
    """测试API4（关注用户列表）、API5（隐私设置）、API6（/me返回隐私字段）"""
    def setUp(self):
        # 创建测试用户
        self.current_user = User.objects.create_user(
            username="current", password="123456",
            show_followed_models=True, show_followed_datasets=True,
            bio="测试用户", email="current@test.com"
        )
        self.user1 = User.objects.create_user(username="user1", password="123456", bio="用户1")
        self.user2 = User.objects.create_user(username="user2", password="123456", bio="用户2")
        
        # 关注关系
        UserFollow.objects.create(follower=self.current_user, followed=self.user1)
        UserFollow.objects.create(follower=self.current_user, followed=self.user2)
        
        # 登录当前用户
        self.client.force_authenticate(user=self.current_user)

    # === API4: 获取当前用户关注的用户列表 ===
    def test_get_followed_users_list(self):
        url = reverse("user-followed-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 200)
        self.assertEqual(len(response.data["data"]), 2)
        
        # 验证返回字段
        item = response.data["data"][0]
        self.assertIn("id", item)
        self.assertIn("username", item)
        self.assertIn("avatar", item)
        self.assertIn("bio", item)
        self.assertIn("show_followed_models", item)
        self.assertIn("show_followed_datasets", item)
        self.assertIn("followed_at", item)

    # === API5: 更新隐私设置 ===
    def test_update_privacy_settings(self):
        url = reverse("user-privacy-update")
        data = {
            "show_followed_models": False,
            "show_followed_datasets": True
        }
        response = self.client.put(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 200)
        self.assertEqual(response.data["data"]["show_followed_models"], False)
        self.assertEqual(response.data["data"]["show_followed_datasets"], True)
        
        # 验证数据库已更新
        self.current_user.refresh_from_db()
        self.assertEqual(self.current_user.show_followed_models, False)
        self.assertEqual(self.current_user.show_followed_datasets, True)

    # === API6: /api/users/me/ 返回隐私设置 ===
    def test_user_me_returns_privacy_fields(self):
        url = reverse("user-me")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 从嵌套的data中查找隐私字段（核心修复）
        self.assertIn("show_followed_models", response.data["data"])
        self.assertIn("show_followed_datasets", response.data["data"])
        self.assertEqual(response.data["data"]["show_followed_models"], True)
        self.assertEqual(response.data["data"]["show_followed_datasets"], True)

class UserPublicAndFollowTest(APITestCase):
    """测试API1（公开信息）、API2（关注）、API3（取消关注）"""
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="123456",
            show_followed_models=True, show_followed_datasets=False,
            bio="测试用户1", email="user1@test.com"
        )
        self.user2 = User.objects.create_user(username="user2", password="123456")

    def test_user_public_info(self):
        """测试获取用户公开信息"""
        # 未登录状态
        url = reverse("user-public", args=[self.user1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["is_followed"], False)
        self.assertEqual(response.data["data"]["show_followed_models"], True)
        self.assertEqual(response.data["data"]["show_followed_datasets"], False)
        
        # 登录状态
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        self.assertEqual(response.data["data"]["is_followed"], False)
        
        # 关注后
        UserFollow.objects.create(follower=self.user2, followed=self.user1)
        response = self.client.get(url)
        self.assertEqual(response.data["data"]["is_followed"], True)

    def test_follow_user(self):
        """测试关注用户"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("user-follow", args=[self.user1.id])
        
        # 关注成功
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["msg"], "关注成功")
        
        # 重复关注
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["msg"], "已关注该用户")
        
        # 关注自己
        url = reverse("user-follow", args=[self.user2.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["msg"], "不能关注自己")

    def test_unfollow_user(self):
        """测试取消关注"""
        self.client.force_authenticate(user=self.user2)
        # 创建关注关系
        UserFollow.objects.create(follower=self.user2, followed=self.user1)