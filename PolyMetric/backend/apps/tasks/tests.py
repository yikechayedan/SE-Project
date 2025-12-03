from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tasks.models import EvaluationTask, EvaluationItem, EvaluationModel
from apps.datasets.models import Dataset



User = get_user_model()


class APIDocTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 创建用户
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="123456"
        )

        # 获取 JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access = str(refresh.access_token)

        # 所有请求都加上 JWT
        self.headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.access}"
        }

        # 创建模型
        self.model = EvaluationModel.objects.create(
            name="GPT-4V",
            description="Vision model"
        )

        # 创建数据集（注意 dataset 必须有 creator）
        self.dataset = Dataset.objects.create(
            name="COCO 2017",
            description="Image dataset",
            creator=self.user   # 🔥 必须有 creator，避免 NOT NULL 报错
        )

        # 创建评测任务（用于 detail / update / delete 测试）
        self.task = EvaluationTask.objects.create(
            name="Test Task",
            description="desc",
            creator=self.user,
            dataset=self.dataset,
            method="objective",
            model=self.model
        )

        # 创建条目
        self.item = EvaluationItem.objects.create(
            task=self.task,
            content="1+1=?",
            correct_answer="2"
        )


    # ----------------------------------------------------------
    # 1 创建评测任务
    # ----------------------------------------------------------
    def test_01_create_task(self):
        res = self.client.post(
            "/api/tasks/evaluation-tasks/",
            {
                "name": "GPT-4V 图像分类评测",
                "description": "使用 COCO 数据集测试 GPT-4V 的图像分类能力",
                "method": "objective",
                "model": self.model.id,
                "dataset": self.dataset.id
            },
            format="json",
            **self.headers
        )

        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["name"], "GPT-4V 图像分类评测")
        self.assertEqual(res.data["creator_username"], "testuser")

        # 保存任务 ID 用于后续测试
        self.task_id = res.data["id"]

    # ----------------------------------------------------------
    # 2 查看任务列表
    # ----------------------------------------------------------
    def test_02_get_task_list(self):
        task = EvaluationTask.objects.create(
            name="Test Task",
            description="Desc",
            method="objective",
            creator=self.user,
            model=self.model,
            dataset=self.dataset,
        )
        res = self.client.get(
            "/api/tasks/evaluation-tasks/",
            **self.headers
        )

        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.data), 1)

    # ----------------------------------------------------------
    # 3 查看任务详情
    # ----------------------------------------------------------
    def test_03_get_task_detail(self):
        task = EvaluationTask.objects.create(
            name="Test Task",
            description="Desc",
            method="objective",
            creator=self.user,
            model=self.model,
            dataset=self.dataset,
        )

        # 添加2条测试条目
        EvaluationItem.objects.create(
            task=task, content="1+1=?", predicted_answer="2", correct_answer="2"
        )
        EvaluationItem.objects.create(
            task=task, content="鸡兔同笼", predicted_answer="D", correct_answer="C"
        )

        res = self.client.get(
            f"/api/tasks/evaluation-tasks/{task.id}/",
            **self.headers
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn("data", res.data)
        self.assertEqual(len(res.data["data"]), 2)

    # ----------------------------------------------------------
    # 4 全量更新任务
    # ----------------------------------------------------------
    def test_04_update_task(self):
        task = EvaluationTask.objects.create(
            name="Old Name",
            description="Old",
            method="objective",
            creator=self.user,
            model=self.model,
            dataset=self.dataset,
        )

        res = self.client.put(
            f"/api/tasks/evaluation-tasks/{task.id}/",
            {
                "name": "New Name",
                "description": "Updated Desc",
                "method": "objective",
                "model": self.model.id,
                "dataset": self.dataset.id
            },
            format="json",
            **self.headers
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["name"], "New Name")

    # ----------------------------------------------------------
    # 5 部分更新任务
    # ----------------------------------------------------------
    def test_05_partial_update_task(self):
        task = EvaluationTask.objects.create(
            name="Old Name",
            description="Old",
            method="objective",
            creator=self.user,
            model=self.model,
            dataset=self.dataset,
        )

        res = self.client.patch(
            f"/api/tasks/evaluation-tasks/{task.id}/",
            {"name": "Final Name"},
            format="json",
            **self.headers
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["name"], "Final Name")

    # ----------------------------------------------------------
    # 6 删除任务
    # ----------------------------------------------------------
    def test_06_delete_task(self):
        task = EvaluationTask.objects.create(
            name="To Delete",
            description="Desc",
            method="objective",
            creator=self.user,
            model=self.model,
            dataset=self.dataset,
        )

        res = self.client.delete(
            f"/api/tasks/evaluation-tasks/{task.id}/",
            **self.headers
        )

        self.assertEqual(res.status_code, 204)

    # ----------------------------------------------------------
    # 7 提交主观评分
    # ----------------------------------------------------------
    def test_07_submit_subjective_score(self):
        task = EvaluationTask.objects.create(
            name="Subjective Task",
            description="Desc",
            method="subjective",
            creator=self.user,
            model=self.model,
            dataset=self.dataset,
        )

        item = EvaluationItem.objects.create(
            task=task, content="Q1"
        )

        res = self.client.post(
            f"/api/tasks/evaluation-tasks/{task.id}/",
            {
                "method": "subjective",
                "model": self.model.id,
                "dataset": self.dataset.id,
                "reviewer": self.user.id,
                "time_stamp": "2025-11-30T10:00:00Z",
                "itemID": item.id,
                "score": 6
            },
            format="json",
            **self.headers
        )

        self.assertEqual(res.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.score, 6)

    # ----------------------------------------------------------
    # 8 提交对抗偏好
    # ----------------------------------------------------------
    def test_08_submit_adversarial(self):
        task = EvaluationTask.objects.create(
            name="Adv Task",
            description="Desc",
            method="adversarial",
            creator=self.user,
            model=self.model,
            dataset=self.dataset,
        )

        item = EvaluationItem.objects.create(task=task, content="Q1")

        res = self.client.post(
            f"/api/tasks/evaluation-tasks/{task.id}/",
            {
                "method": "adversarial",
                "model": self.model.id,
                "dataset": self.dataset.id,
                "reviewer": self.user.id,
                "time_stamp": "2025-11-30T10:00:00Z",
                "itemID": item.id,
                "preference": "left"
            },
            format="json",
            **self.headers
        )

        self.assertEqual(res.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.preference, "left")

    # ----------------------------------------------------------
    # 9 请求待测条目列表
    # ----------------------------------------------------------
    def test_09_get_pending_items(self):
        task = EvaluationTask.objects.create(
            name="Pending Task",
            description="Desc",
            method="subjective",
            creator=self.user,
            model=self.model,
            dataset=self.dataset,
        )

        item1 = EvaluationItem.objects.create(task=task, content="A")
        item2 = EvaluationItem.objects.create(task=task, content="B")

        url = f"/api/tasks/get-pending-items?task={task.id}&reviewer={self.user.id}"

        res = self.client.get(url, **self.headers)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["pending_count"], 2)
        self.assertIn("pengdingItem_ids", res.data)

    # ----------------------------------------------------------
    # 10 请求条目详情
    # ----------------------------------------------------------
    def test_10_get_item_detail(self):
        task = EvaluationTask.objects.create(
            name="Detail Task",
            description="Desc",
            method="subjective",
            creator=self.user,
            model=self.model,
            dataset=self.dataset,
        )

        item = EvaluationItem.objects.create(
            task=task,
            content="Explain quantum entanglement",
            predicted_answer="Answer",
        )

        res = self.client.get(
            "/api/tasks/get-item-detail",
            {
                "task": task.id,
                "itemID": item.id
            },
            **self.headers
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["method"], "subjective")
        self.assertEqual(res.data["itemID"], item.id)
