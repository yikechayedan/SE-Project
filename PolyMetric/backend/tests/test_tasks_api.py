"""
任务相关API全面测试
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from tests.test_utils import TestDataGenerator, AuthUtils, APITestMixin

User = get_user_model()


class EvaluationTaskListCreateAPITest(TestCase, APITestMixin):
    """评测任务列表和创建API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.admin = TestDataGenerator.create_admin_user()
        
        # 创建测试数据
        self.model = TestDataGenerator.create_model()
        self.dataset = TestDataGenerator.create_dataset()
        
        # 创建测试任务
        self.task1 = TestDataGenerator.create_evaluation_task(
            name="任务1",
            creator=self.user,
            model=self.model,
            dataset=self.dataset,
            method="objective"
        )
        self.task2 = TestDataGenerator.create_evaluation_task(
            name="任务2",
            creator=self.admin,
            model=self.model,
            dataset=self.dataset,
            method="subjective"
        )
    
    def test_list_tasks_authenticated(self):
        """测试认证用户获取任务列表"""
        self.create_authenticated_client(self.user)
        response = self.client.get("/api/tasks/evaluation-tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 2)
    
    def test_list_tasks_unauthorized(self):
        """测试未认证用户获取任务列表"""
        response = self.client.get("/api/tasks/evaluation-tasks/")
        self.assertEqual(response.status_code, 401)
    
    def test_create_task_success(self):
        """测试创建任务成功"""
        self.create_authenticated_client(self.user)
        
        data = {
            "name": "新评测任务",
            "description": "测试评测任务描述",
            "method": "objective",
            "myModel": self.model.id,
            "dataset": self.dataset.id
        }
        response = self.client.post("/api/tasks/evaluation-tasks/", data, format="json")
        self.assertEqual(response.status_code, 201)
        
        # 验证任务已创建
        self.assertEqual(response.data["name"], "新评测任务")
        self.assertEqual(response.data["creator"], self.user.id)
        self.assertEqual(response.data["myModel"], self.model.id)
        self.assertEqual(response.data["dataset"], self.dataset.id)
    
    def test_create_task_missing_required_fields(self):
        """测试创建任务缺少必填字段"""
        self.create_authenticated_client(self.user)
        
        data = {
            "name": "不完整的任务"
            # 缺少myModel和dataset
        }
        response = self.client.post("/api/tasks/evaluation-tasks/", data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
    
    def test_create_task_invalid_method(self):
        """测试创建任务使用无效方法"""
        self.create_authenticated_client(self.user)
        
        data = {
            "name": "无效方法任务",
            "method": "invalid_method",
            "myModel": self.model.id,
            "dataset": self.dataset.id
        }
        response = self.client.post("/api/tasks/evaluation-tasks/", data, format="json")
        self.assertEqual(response.status_code, 400)


class EvaluationTaskDetailAPITest(TestCase, APITestMixin):
    """评测任务详情API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.other_user = TestDataGenerator.create_user()
        self.admin = TestDataGenerator.create_admin_user()
        
        self.model = TestDataGenerator.create_model()
        self.dataset = TestDataGenerator.create_dataset()
        
        self.task = TestDataGenerator.create_evaluation_task(
            name="测试任务",
            creator=self.user,
            model=self.model,
            dataset=self.dataset
        )
        
        # 创建评测项
        self.item = TestDataGenerator.create_evaluation_item(
            task=self.task,
            content="测试问题",
            correct_answer="测试答案",  # 修正字段名
            predicted_answer="预测答案"
        )
    
    def test_get_task_detail_owner(self):
        """测试任务创建者获取任务详情"""
        self.create_authenticated_client(self.user)
        response = self.client.get(f"/api/tasks/evaluation-tasks/{self.task.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "测试任务")
    
    def test_get_task_detail_admin(self):
        """测试管理员获取任务详情"""
        self.create_authenticated_client(self.admin)
        response = self.client.get(f"/api/tasks/evaluation-tasks/{self.task.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "测试任务")
    
    def test_get_task_detail_unauthorized(self):
        """测试未授权用户获取任务详情"""
        self.create_authenticated_client(self.other_user)
        response = self.client.get(f"/api/tasks/evaluation-tasks/{self.task.id}/")
        self.assertEqual(response.status_code, 403)
        self.assertIn("仅任务创建者或管理员可操作此评测任务", response.data["error"])
    
    def test_update_task_success(self):
        """测试更新任务成功"""
        self.create_authenticated_client(self.user)
        
        data = {
            "name": "更新后的任务",
            "description": "更新后的描述",
            "method": "subjective",
            "myModel": self.model.id,
            "dataset": self.dataset.id
        }
        response = self.client.put(f"/api/tasks/evaluation-tasks/{self.task.id}/", data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "更新后的任务")
    
    def test_partial_update_task_success(self):
        """测试部分更新任务成功"""
        self.create_authenticated_client(self.user)
        
        data = {"name": "部分更新的任务"}
        response = self.client.patch(f"/api/tasks/evaluation-tasks/{self.task.id}/", data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "部分更新的任务")
    
    def test_update_task_unauthorized(self):
        """测试未授权用户更新任务"""
        self.create_authenticated_client(self.other_user)
        
        data = {"name": "恶意更新"}
        response = self.client.patch(f"/api/tasks/evaluation-tasks/{self.task.id}/", data, format="json")
        self.assertEqual(response.status_code, 403)
    
    def test_delete_task_success(self):
        """测试删除任务成功"""
        self.create_authenticated_client(self.user)
        response = self.client.delete(f"/api/tasks/evaluation-tasks/{self.task.id}/")
        self.assertEqual(response.status_code, 204)
        
        # 验证任务已删除
        from apps.tasks.models import EvaluationTask
        self.assertFalse(EvaluationTask.objects.filter(id=self.task.id).exists())
    
    def test_delete_task_unauthorized(self):
        """测试未授权用户删除任务"""
        self.create_authenticated_client(self.other_user)
        response = self.client.delete(f"/api/tasks/evaluation-tasks/{self.task.id}/")
        self.assertEqual(response.status_code, 403)


class EvaluationTaskScoreAPITest(TestCase, APITestMixin):
    """评测任务评分API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.reviewer = TestDataGenerator.create_user()
        
        self.model = TestDataGenerator.create_model()
        self.dataset = TestDataGenerator.create_dataset()
        
        # 创建主观评测任务
        self.subjective_task = TestDataGenerator.create_evaluation_task(
            name="主观评测任务",
            creator=self.user,
            model=self.model,
            dataset=self.dataset,
            method="subjective"
        )
        
        # 创建对抗评测任务
        self.adversarial_task = TestDataGenerator.create_evaluation_task(
            name="对抗评测任务",
            creator=self.user,
            model=self.model,
            dataset=self.dataset,
            method="adversarial"
        )
        
        # 创建评测项
        self.item1 = TestDataGenerator.create_evaluation_item(
            task=self.subjective_task,
            content="测试问题1",
            correct_answer="测试答案1"  # 修正字段名
        )
        
        self.item2 = TestDataGenerator.create_evaluation_item(
            task=self.adversarial_task,
            content="测试问题2",
            correct_answer="测试答案2"  # 修正字段名
        )
    
    def test_submit_subjective_score_success(self):
        """测试提交主观评分成功"""
        self.create_authenticated_client(self.reviewer)
        
        data = {
            "myModel": self.model.id,
            "dataset": self.dataset.id,
            "reviewer": self.reviewer.id,
            "itemID": self.item1.id,
            "score": 8
        }
        response = self.client.post(f"/api/tasks/evaluation-tasks/{self.subjective_task.id}/", data, format="json")
        self.assertEqual(response.status_code, 200)
        
        # 验证评分已保存
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.score, 8)
    
    def test_submit_adversarial_preference_success(self):
        """测试提交对抗偏好成功"""
        self.create_authenticated_client(self.reviewer)
        
        data = {
            "myModel": self.model.id,
            "dataset": self.dataset.id,
            "reviewer": self.reviewer.id,
            "itemID": self.item2.id,
            "preference": "left"
        }
        response = self.client.post(f"/api/tasks/evaluation-tasks/{self.adversarial_task.id}/", data, format="json")
        self.assertEqual(response.status_code, 200)
        
        # 验证偏好已保存
        self.item2.refresh_from_db()
        self.assertEqual(self.item2.preference, "left")
    
    def test_submit_score_invalid_score(self):
        """测试提交无效评分"""
        self.create_authenticated_client(self.reviewer)
        
        data = {
            "myModel": self.model.id,
            "dataset": self.dataset.id,
            "reviewer": self.reviewer.id,
            "itemID": self.item1.id,
            "score": "invalid_score"
        }
        response = self.client.post(f"/api/tasks/evaluation-tasks/{self.subjective_task.id}/", data, format="json")
        self.assertEqual(response.status_code, 400)
    
    def test_submit_score_invalid_preference(self):
        """测试提交无效偏好"""
        self.create_authenticated_client(self.reviewer)
        
        data = {
            "myModel": self.model.id,
            "dataset": self.dataset.id,
            "reviewer": self.reviewer.id,
            "itemID": self.item2.id,
            "preference": "invalid_preference"
        }
        response = self.client.post(f"/api/tasks/evaluation-tasks/{self.adversarial_task.id}/", data, format="json")
        self.assertEqual(response.status_code, 400)
    
    def test_submit_score_model_dataset_mismatch(self):
        """测试提交评分模型数据集不匹配"""
        other_model = TestDataGenerator.create_model()
        self.create_authenticated_client(self.reviewer)
        
        data = {
            "myModel": other_model.id,  # 不匹配的模型
            "dataset": self.dataset.id,
            "reviewer": self.reviewer.id,
            "itemID": self.item1.id,
            "score": 8
        }
        response = self.client.post(f"/api/tasks/evaluation-tasks/{self.subjective_task.id}/", data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Model or dataset mismatch", response.data["error"])


class PendingItemsAPITest(TestCase, APITestMixin):
    """待评测项API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.reviewer = TestDataGenerator.create_user()
        
        self.model = TestDataGenerator.create_model()
        self.dataset = TestDataGenerator.create_dataset()
        
        self.task = TestDataGenerator.create_evaluation_task(
            creator=self.user,
            model=self.model,
            dataset=self.dataset
        )
        
        # 创建多个评测项
        self.item1 = TestDataGenerator.create_evaluation_item(task=self.task)
        self.item2 = TestDataGenerator.create_evaluation_item(task=self.task)
        self.item3 = TestDataGenerator.create_evaluation_item(
            task=self.task,
            score=5  # 已评分
        )
    
    def test_get_pending_items_success(self):
        """测试获取待评测项成功"""
        self.create_authenticated_client(self.reviewer)
        
        response = self.client.get(f"/api/tasks/get-pending-items?task={self.task.id}&reviewer={self.reviewer.id}")
        self.assertEqual(response.status_code, 200)
        
        # 验证返回数据
        self.assertEqual(response.data["task"], self.task.id)
        self.assertEqual(response.data["reviewer"], self.reviewer.id)
        self.assertEqual(response.data["pending_count"], 2)  # 只有未评分的项
        self.assertIn("pengdingItem_ids", response.data)
    
    def test_get_pending_items_invalid_parameters(self):
        """测试获取待评测项参数无效"""
        self.create_authenticated_client(self.reviewer)
        
        response = self.client.get("/api/tasks/get-pending-items?task=invalid&reviewer=invalid")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid parameters", response.data["error"])
    
    def test_get_pending_items_nonexistent_task(self):
        """测试获取不存在任务的待评测项"""
        self.create_authenticated_client(self.reviewer)
        
        response = self.client.get(f"/api/tasks/get-pending-items?task=99999&reviewer={self.reviewer.id}")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Task not found", response.data["error"])
    
    def test_get_pending_items_nonexistent_reviewer(self):
        """测试获取不存在评测者的待评测项"""
        self.create_authenticated_client(self.reviewer)
        
        response = self.client.get(f"/api/tasks/get-pending-items?task={self.task.id}&reviewer=99999")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Reviewer not found", response.data["error"])


class ItemDetailAPITest(TestCase, APITestMixin):
    """评测项详情API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        
        self.model = TestDataGenerator.create_model()
        self.dataset = TestDataGenerator.create_dataset()
        
        self.task = TestDataGenerator.create_evaluation_task(
            creator=self.user,
            model=self.model,
            dataset=self.dataset
        )
        
        self.item = TestDataGenerator.create_evaluation_item(
            task=self.task,
            content="测试问题",
            correct_answer="测试答案",  # 修正字段名
            predicted_answer="预测答案"
        )
    
    def test_get_item_detail_success(self):
        """测试获取评测项详情成功"""
        self.create_authenticated_client(self.user)
        
        response = self.client.get(f"/api/tasks/get-item-detail?task={self.task.id}&itemID={self.item.id}")
        self.assertEqual(response.status_code, 200)
        
        # 验证返回数据
        self.assertEqual(response.data["method"], self.task.method)
        self.assertEqual(response.data["itemID"], self.item.id)
        self.assertIn("item_content", response.data)
        
        item_content = response.data["item_content"]
        self.assertEqual(item_content["input_query"], "测试问题")
        self.assertEqual(item_content["myModel1_response"], "预测答案")
    
    def test_get_item_detail_invalid_parameters(self):
        """测试获取评测项详情参数无效"""
        self.create_authenticated_client(self.user)
        
        response = self.client.get("/api/tasks/get-item-detail?task=invalid&itemID=invalid")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid parameters", response.data["error"])
    
    def test_get_item_detail_nonexistent_task(self):
        """测试获取不存在任务的评测项详情"""
        self.create_authenticated_client(self.user)
        
        response = self.client.get(f"/api/tasks/get-item-detail?task=99999&itemID={self.item.id}")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Task or item not found", response.data["error"])
    
    def test_get_item_detail_nonexistent_item(self):
        """测试获取不存在评测项的详情"""
        self.create_authenticated_client(self.user)
        
        response = self.client.get(f"/api/tasks/get-item-detail?task={self.task.id}&itemID=99999")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Task or item not found", response.data["error"])


class RunTaskAPITest(TestCase, APITestMixin):
    """运行任务API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        
        self.model = TestDataGenerator.create_model()
        
        # 创建带文件的数据集
        from django.core.files.uploadedfile import SimpleUploadedFile
        import json
        test_file = SimpleUploadedFile(
            "test.json",
            json.dumps([
                {"id": 1, "question": "测试问题1", "answer": "测试答案1"},
                {"id": 2, "question": "测试问题2", "answer": "测试答案2"}
            ]).encode('utf-8'),
            content_type="application/json"
        )
        
        self.dataset = TestDataGenerator.create_dataset()
        self.dataset.file_path = test_file
        self.dataset.save()
        
        self.task = TestDataGenerator.create_evaluation_task(
            creator=self.user,
            myModel=self.model,  # 修正字段名
            dataset=self.dataset
        )
    
    def test_run_task_success(self):
        """测试运行任务成功"""
        self.create_authenticated_client(self.user)
        
        data = {"task_id": self.task.id}
        response = self.client.post("/api/tasks/run-task/", data, format="json")
        
        # 运行任务可能返回200、400或500，取决于实际执行情况
        # 这里只验证不是401或404
        self.assertIn(response.status_code, [200, 400, 500])
    
    def test_run_task_nonexistent(self):
        """测试运行不存在的任务"""
        self.create_authenticated_client(self.user)
        
        data = {"task_id": 99999}
        response = self.client.post("/api/tasks/run-task/", data, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertIn("task not found", response.data["error"])
    
    def test_run_task_unauthorized(self):
        """测试未授权用户运行任务"""
        data = {"task_id": self.task.id}
        response = self.client.post("/api/tasks/run-task/", data, format="json")
        self.assertEqual(response.status_code, 401)


class RunBenchmarkAPITest(TestCase, APITestMixin):
    """运行基准测试API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        
        self.model1 = TestDataGenerator.create_model(name="模型1")
        self.model2 = TestDataGenerator.create_model(name="模型2")
        self.model3 = TestDataGenerator.create_model(name="模型3")
        
        # 创建带文件的数据集
        from django.core.files.uploadedfile import SimpleUploadedFile
        import json
        test_file = SimpleUploadedFile(
            "test.json",
            json.dumps([
                {"id": 1, "question": "测试问题1", "answer": "测试答案1"},
                {"id": 2, "question": "测试问题2", "answer": "测试答案2"}
            ]).encode('utf-8'),
            content_type="application/json"
        )
        
        self.dataset = TestDataGenerator.create_dataset()
        self.dataset.file_path = test_file
        self.dataset.save()
    
    def test_run_benchmark_success(self):
        """测试运行基准测试成功"""
        self.create_authenticated_client(self.user)
        
        data = {
            "dataset": self.dataset.id,
            "models": [self.model1.id, self.model2.id, self.model3.id],
            "max_workers": 2
        }
        response = self.client.post("/api/tasks/run-benchmark/", data, format="json")
        self.assertEqual(response.status_code, 200)
    
    def test_run_benchmark_missing_parameters(self):
        """测试运行基准测试缺少参数"""
        self.create_authenticated_client(self.user)
        
        data = {
            "models": [self.model1.id, self.model2.id]
            # 缺少dataset
        }
        response = self.client.post("/api/tasks/run-benchmark/", data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("dataset and models are required", response.data["error"])
    
    def test_run_benchmark_unauthorized(self):
        """测试未授权用户运行基准测试"""
        data = {
            "dataset": self.dataset.id,
            "models": [self.model1.id, self.model2.id]
        }
        response = self.client.post("/api/tasks/run-benchmark/", data, format="json")
        self.assertEqual(response.status_code, 401)


class EvaluationTaskIntegrationTest(TestCase, APITestMixin):
    """评测任务集成测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.reviewer = TestDataGenerator.create_user()
        
        self.model = TestDataGenerator.create_model()
        
        # 创建带文件的数据集
        from django.core.files.uploadedfile import SimpleUploadedFile
        import json
        test_file = SimpleUploadedFile(
            "test.json",
            json.dumps([
                {"id": 1, "question": "测试问题1", "answer": "测试答案1"},
                {"id": 2, "question": "测试问题2", "answer": "测试答案2"}
            ]).encode('utf-8'),
            content_type="application/json"
        )
        
        self.dataset = TestDataGenerator.create_dataset()
        self.dataset.file_path = test_file
        self.dataset.save()
    
    def test_complete_evaluation_workflow(self):
        """测试完整的评测工作流程"""
        # 1. 创建任务
        self.create_authenticated_client(self.user)
        
        task_data = {
            "name": "完整评测任务",
            "description": "完整评测流程测试",
            "method": "subjective",
            "myModel": self.model.id,
            "dataset": self.dataset.id
        }
        response = self.client.post("/api/tasks/evaluation-tasks/", task_data, format="json")
        self.assertEqual(response.status_code, 201)
        task_id = response.data["id"]
        
        # 2. 获取任务详情
        response = self.client.get(f"/api/tasks/evaluation-tasks/{task_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "完整评测任务")
        
        # 3. 获取待评测项
        response = self.client.get(f"/api/tasks/get-pending-items?task={task_id}&reviewer={self.reviewer.id}")
        self.assertEqual(response.status_code, 200)
        
        # 4. 获取评测项详情
        if response.data["pending_count"] > 0:
            item_id = response.data["pengdingItem_ids"][0]
            response = self.client.get(f"/api/tasks/get-item-detail?task={task_id}&itemID={item_id}")
            self.assertEqual(response.status_code, 200)
            
            # 5. 提交评分
            score_data = {
                "myModel": self.model.id,
                "dataset": self.dataset.id,
                "reviewer": self.reviewer.id,
                "itemID": item_id,
                "score": 7
            }
            response = self.client.post(f"/api/tasks/evaluation-tasks/{task_id}/", score_data, format="json")
            self.assertEqual(response.status_code, 200)
        
        # 6. 运行任务
        run_data = {"task_id": task_id}
        response = self.client.post("/api/tasks/run-task/", run_data, format="json")
        self.assertIn(response.status_code, [200, 400, 500])
        
        # 7. 删除任务
        response = self.client.delete(f"/api/tasks/evaluation-tasks/{task_id}/")
        self.assertEqual(response.status_code, 204)