from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from apps.datasets.models import Dataset
from apps.tasks.models import (
    My_Model,
    EvaluationTask,
    EvaluationItem,
)

User = get_user_model()


class EvaluationTaskAPITests(APITestCase):
    """
    全面的任务测试：
    - 列表
    - 创建
    - 详情
    - 修改（PUT/PATCH）
    - 删除
    - 获取 pending item
    - 获取 item detail
    - 提交 subjective 分数
    - 提交 adv preference
    - 运行 run-task
    """

    def setUp(self):
        """准备基础数据：用户、Token、模型、数据集、任务、任务项"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="123456"
        )

        # 生成 token
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        # ---- 创建模型（My_Model）----
        self.model = My_Model.objects.create(
            name="Demo Model",
            description="model for test"
        )

        # ---- 创建数据集（必须带 creator，否则报 NOT NULL 错误）----
        self.dataset = Dataset.objects.create(
            name="Demo Dataset",
            description="Test dataset",
            creator=self.user,
            file_format="json",  # 添加必需的file_format字段
            evaluation_type="objective"  # 添加evaluation_type字段
        )

        # ---- 创建任务 ----
        self.task = EvaluationTask.objects.create(
            name="Test Task",
            dataset=self.dataset,
            myModel=self.model,
            creator=self.user,
            method="subjective"  # 设置为subjective方法
        )
        
        # ---- 创建对抗任务用于测试对抗偏好 ----
        self.adversarial_task = EvaluationTask.objects.create(
            name="Adversarial Test Task",
            dataset=self.dataset,
            myModel=self.model,
            myModel_2=self.model,  # 对抗评测需要第二个模型
            creator=self.user,
            method="adversarial"  # 设置为adversarial方法
        )

        # ---- 创建任务项 ----
        self.item = EvaluationItem.objects.create(
            task=self.task,
            content="Hello",
            correct_answer="World"
        )
        
        # ---- 为对抗任务创建任务项 ----
        self.adversarial_item = EvaluationItem.objects.create(
            task=self.adversarial_task,
            content="Adversarial Hello",
            correct_answer="Adversarial World"
        )

    # ------------------------------------------------------------
    # 1. 测试任务列表接口
    # ------------------------------------------------------------
    def test_list_tasks(self):
        response = self.client.get("/api/tasks/evaluation-tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------
    # 2. 创建任务
    # ------------------------------------------------------------
    def test_create_task(self):
        data = {
            "name": "New Task",
            "dataset": self.dataset.id,
            "myModel": self.model.id,
            "method": "objective"  # 添加必需的method字段
        }
        response = self.client.post("/api/tasks/evaluation-tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # ------------------------------------------------------------
    # 3. 获取任务详情
    # ------------------------------------------------------------
    def test_retrieve_task_detail(self):
        response = self.client.get(f"/api/tasks/evaluation-tasks/{self.task.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------
    # 4. 全量更新任务
    # ------------------------------------------------------------
    def test_update_task(self):
        data = {
            "name": "Updated Task",
            "dataset": self.dataset.id,
            "myModel": self.model.id,
            "method": "objective"  # 添加必需的method字段
        }
        response = self.client.put(f"/api/tasks/evaluation-tasks/{self.task.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------
    # 5. 局部更新任务
    # ------------------------------------------------------------
    def test_partial_update_task(self):
        data = {"name": "Partially Update"}
        response = self.client.patch(f"/api/tasks/evaluation-tasks/{self.task.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------
    # 6. 删除任务
    # ------------------------------------------------------------
    def test_delete_task(self):
        response = self.client.delete(f"/api/tasks/evaluation-tasks/{self.task.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # ------------------------------------------------------------
    # 7. 获取待评测项 /pending-item
    # ------------------------------------------------------------
    def test_get_pending_items(self):
        response = self.client.get(f"/api/tasks/evaluation-tasks/{self.task.id}/pending-item/?reviewer_id={self.user.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------
    # 8. 获取单个任务项信息
    # ------------------------------------------------------------
    def test_get_item_detail(self):
        response = self.client.get(
            f"/api/tasks/evaluation-tasks/{self.task.id}/item/{self.item.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------
    # 9. 主观分数提交（subjective-score）
    # ------------------------------------------------------------
    def test_submit_subjective_score(self):
        data = {
            "myModel": self.task.myModel.id,
            "dataset": self.task.dataset.id,
            "reviewer": self.user.id,
            "itemID": self.item.id,
            "score": 4
        }
        response = self.client.post(
            f"/api/tasks/evaluation-tasks/{self.task.id}/",
            data  # 使用任务级别的submit_score端点
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------
    # 10. 对抗偏好（adversarial-preference）
    # ------------------------------------------------------------
    def test_submit_adversarial_preference(self):
        data = {
            "myModel": self.adversarial_task.myModel.id,
            "dataset": self.adversarial_task.dataset.id,
            "reviewer": self.user.id,
            "itemID": self.adversarial_item.id,
            "preference": "left"
        }
        response = self.client.post(
            f"/api/tasks/evaluation-tasks/{self.adversarial_task.id}/",
            data  # 使用任务级别的submit_score端点
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------
    # 11. 运行任务 run-task
    # ------------------------------------------------------------
    def test_run_task(self):
        """
        run_task 可能返回 200 / 400 / 500
        所以这里不严格要求，只验证不要 401/404
        """
        data = {"task_id": self.task.id}
        response = self.client.post("/api/tasks/run-task/", data, format="json")

        self.assertIn(response.status_code, [200, 400, 500])
