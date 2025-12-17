from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.datasets.models import Dataset, DatasetFollow

class DatasetFollowedAPITest(APITestCase):
    """测试数据集关注列表扩展功能（user_id 参数 + 隐私校验）"""
    def setUp(self):
        # 创建测试用户
        self.user1 = User.objects.create_user(
            username="user1", password="123456", 
            show_followed_datasets=True  # 公开数据集关注列表
        )
        self.user2 = User.objects.create_user(
            username="user2", password="123456", 
            show_followed_datasets=False  # 不公开
        )
        self.user3 = User.objects.create_user(username="user3", password="123456")
        
        # 创建数据集并关注
        self.dataset1 = Dataset.objects.create(name="测试数据集1", creator=self.user3)
        DatasetFollow.objects.create(user=self.user1, dataset=self.dataset1)
        DatasetFollow.objects.create(user=self.user2, dataset=self.dataset1)
        
        # 登录 user1
        self.client.force_authenticate(user=self.user1)

    def test_get_others_followed_datasets_public(self):
        """测试查询公开数据集关注列表的用户"""
        url = reverse("dataset-followed") + "?user_id=" + str(self.user1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)  # 能看到user1的关注列表

    def test_get_others_followed_datasets_private(self):
        """测试查询不公开数据集关注列表的用户"""
        url = reverse("dataset-followed") + "?user_id=" + str(self.user2.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["msg"], "该用户未公开关注的数据集")
        self.assertEqual(response.data["data"], None)

    def test_get_own_followed_datasets(self):
        """测试查询自己的数据集关注列表（无user_id）"""
        url = reverse("dataset-followed")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)  # 能看到自己的关注列表