from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from apps.datasets.models import Dataset, DatasetFollow

User = get_user_model()


class DatasetAPITests(APITestCase):

    def setUp(self):
        """初始化测试环境：创建用户 + 登录 + 创建数据集"""
        self.client = APIClient()

        # 创建普通用户
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            phone="13800000000",
            password="testpassword123"
        )

        # 登录获取 token
        login_res = self.client.post("/api/users/login/", {
            "username": "testuser",
            "password": "testpassword123"
        })

        self.assertEqual(login_res.status_code, 200)
        self.access = login_res.data["access"]

        # 设置 token 到 header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

        # 创建一个数据集
        self.dataset = Dataset.objects.create(
            name="Test Dataset",
            description="desc",
            category="image",
            file_format="csv",
            file_size=1.5,
            file_path="datasets/test.csv",
            sample_count=100,
            creator=self.user,
            is_public=True,
            is_verified=True
        )

    # ----------------------------------------
    # 基础 API 测试
    # ----------------------------------------

    def test_list_datasets(self):
        """测试数据集列表是否正常返回"""
        res = self.client.get("/api/datasets/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["code"], 200)
        self.assertTrue(len(res.data["data"]) >= 1)

    def test_retrieve_dataset(self):
        """测试数据集详情"""
        res = self.client.get(f"/api/datasets/{self.dataset.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["data"]["name"], "Test Dataset")

    # ----------------------------------------
    # 关注测试
    # ----------------------------------------

    def test_follow_dataset(self):
        """测试关注数据集"""
        res = self.client.post(f"/api/datasets/{self.dataset.id}/follow/")
        self.assertIn(res.status_code, [200, 201])

        # 数据库检查是否写入
        self.assertTrue(
            DatasetFollow.objects.filter(user=self.user, dataset=self.dataset).exists()
        )

    def test_unfollow_dataset(self):
        """测试取消关注"""
        # 先关注
        DatasetFollow.objects.create(user=self.user, dataset=self.dataset)

        res = self.client.delete(f"/api/datasets/{self.dataset.id}/unfollow/")
        self.assertEqual(res.status_code, 200)

        # 检查是否被删除
        self.assertFalse(
            DatasetFollow.objects.filter(user=self.user, dataset=self.dataset).exists()
        )

    def test_followed_list(self):
        """测试关注列表接口是否返回正确内容"""

        DatasetFollow.objects.create(user=self.user, dataset=self.dataset)

        res = self.client.get("/api/datasets/followed/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["data"]), 1)
        self.assertEqual(res.data["data"][0]["id"], self.dataset.id)

    # ----------------------------------------
    # 自己的数据集
    # ----------------------------------------

    def test_my_datasets(self):
        """测试我创建的数据集列表"""
        res = self.client.get("/api/datasets/my_datasets/")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.data["data"]) >= 1)
        self.assertEqual(res.data["data"][0]["creator"], self.user.id)
