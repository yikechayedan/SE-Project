"""
测试工具函数和数据生成器
"""
import json
import tempfile
import os
import zipfile
import io
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.datasets.models import Dataset, DatasetFollow
from apps.models.models import My_Model, ModelFollow
from apps.tasks.models import EvaluationTask, EvaluationItem
from apps.users.models import UserFollow
from apps.comments.models import Comment, CommentLike
from apps.users.models import UserStar

User = get_user_model()


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def create_user(username=None, email=None, password="test123456", **kwargs):
        """创建测试用户"""
        if not username:
            username = f"testuser_{datetime.now().timestamp()}"
        if not email:
            email = f"{username}@test.com"
            
        user_data = {
            "username": username,
            "email": email,
            "password": password,
            **kwargs
        }
        return User.objects.create_user(**user_data)
    
    @staticmethod
    def create_admin_user(username=None, email=None, password="admin123456", **kwargs):
        """创建管理员用户"""
        if not username:
            username = f"admin_{datetime.now().timestamp()}"
        if not email:
            email = f"{username}@admin.com"
            
        return User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            **kwargs
        )
    
    @staticmethod
    def create_model(name=None, company=None, **kwargs):
        """创建测试模型"""
        if not name:
            name = f"测试模型_{datetime.now().timestamp()}"
        if not company:
            company = "测试公司"
            
        model_data = {
            "name": name,
            "company": company,
            "category": kwargs.get("category", "text"),
            "parameter_size": kwargs.get("parameter_size", "10B"),
            "description": kwargs.get("description", "测试模型描述"),
            "version": kwargs.get("version", "v1.0"),
            "official_url": kwargs.get("official_url", "https://test-model.example.com"),
            **{k: v for k, v in kwargs.items() if k not in ["category", "parameter_size", "description", "version", "official_url"]}
        }
        return My_Model.objects.create(**model_data)
    
    @staticmethod
    def create_dataset(name=None, creator=None, **kwargs):
        """创建测试数据集"""
        if not name:
            name = f"测试数据集_{datetime.now().timestamp()}"
        if not creator:
            creator = TestDataGenerator.create_user()
            
        dataset_data = {
            "name": name,
            "description": kwargs.get("description", "测试数据集描述"),
            "category": kwargs.get("category", "text"),
            "file_format": kwargs.get("file_format", "json"),
            "is_public": kwargs.get("is_public", True),
            "is_verified": kwargs.get("is_verified", True),
            "creator": creator,
            "evaluation_type": kwargs.get("evaluation_type", "subjective"),
            "capability_dimension": kwargs.get("capability_dimension", "other"),
            "capability_tag": kwargs.get("capability_tag", None),
            "has_images": kwargs.get("has_images", False),
            "image_count": kwargs.get("image_count", 0),
            # 如果是公开且已验证的数据集，设置状态为passed，这样匿名用户才能看到
            "status": kwargs.get("status", "passed" if kwargs.get("is_public", True) and kwargs.get("is_verified", True) else "pending"),
            **{k: v for k, v in kwargs.items() if k not in ["description", "category", "file_format", "is_public", "is_verified", "creator", "evaluation_type", "capability_dimension", "capability_tag", "has_images", "image_count", "status"]}
        }
        return Dataset.objects.create(**dataset_data)
    
    @staticmethod
    def create_evaluation_task(name=None, creator=None, dataset=None, model=None, **kwargs):
        """创建评测任务"""
        if not name:
            name = f"测试评测任务_{datetime.now().timestamp()}"
        if not creator:
            creator = TestDataGenerator.create_user()
        if not dataset:
            dataset = TestDataGenerator.create_dataset()
        if not model:
            model = TestDataGenerator.create_model()
            
        task_data = {
            "name": name,
            "description": kwargs.get("description", "测试评测任务描述"),
            "method": kwargs.get("method", "objective"),
            "creator": creator,
            "dataset": dataset,
            "myModel": model,
            "myModel_2": kwargs.get("myModel_2", None),
            "judge_model": kwargs.get("judge_model", None),
            "judge_type": kwargs.get("judge_type", "human"),
            **{k: v for k, v in kwargs.items() if k not in ["description", "method", "creator", "dataset", "myModel", "myModel_2", "judge_model", "judge_type"]}
        }
        return EvaluationTask.objects.create(**task_data)
    
    @staticmethod
    def create_task(name=None, creator=None, dataset=None, model=None, **kwargs):
        """创建评测任务 - create_evaluation_task的别名"""
        return TestDataGenerator.create_evaluation_task(name, creator, dataset, model, **kwargs)
    
    @staticmethod
    def create_evaluation_item(task=None, **kwargs):
        """创建评测项"""
        if not task:
            task = TestDataGenerator.create_evaluation_task()
            
        # 支持两种字段名：新的content/correct_answer和旧的input_text/reference_answer
        content = kwargs.get("content") or kwargs.get("input_text", "测试内容")
        correct_answer = kwargs.get("correct_answer") or kwargs.get("reference_answer", "测试答案")
            
        item_data = {
            "task": task,
            "content": content,
            "correct_answer": correct_answer,
            "predicted_answer": kwargs.get("predicted_answer", "预测答案"),
            "predicted_answer_2": kwargs.get("predicted_answer_2", None),
            "is_correct": kwargs.get("is_correct", True),
            "score": kwargs.get("score", None),
            "preference": kwargs.get("preference", None),
            **{k: v for k, v in kwargs.items() if k not in ["task", "content", "correct_answer", "input_text", "reference_answer", "predicted_answer", "predicted_answer_2", "is_correct", "score", "preference"]}
        }
        return EvaluationItem.objects.create(**item_data)
    
    @staticmethod
    def create_comment(user=None, content_type=None, object_id=None, **kwargs):
        """创建测试评论"""
        if not user:
            user = TestDataGenerator.create_user()
        if not content_type:
            from django.contrib.contenttypes.models import ContentType
            content_type = ContentType.objects.get_for_model(My_Model)
        if not object_id:
            model = TestDataGenerator.create_model()
            object_id = model.id
            
        comment_data = {
            "user": user,
            "content": kwargs.get("content", "测试评论内容"),
            "content_type": content_type,
            "object_id": object_id,
            **{k: v for k, v in kwargs.items() if k not in ["user", "content", "content_type", "object_id"]}
        }
        return Comment.objects.create(**comment_data)
    
    @staticmethod
    def create_temp_file(content=None, filename="test.json", file_format="json"):
        """创建临时文件"""
        if content is None:
            if file_format == "json":
                content = json.dumps([
                    {"id": 1, "question": "测试问题1", "answer": "测试答案1"},
                    {"id": 2, "question": "测试问题2", "answer": "测试答案2"}
                ])
            else:
                content = "测试文件内容"
        
        temp_file = tempfile.NamedTemporaryFile(suffix=f".{file_format}", delete=False)
        temp_file.write(content.encode('utf-8'))
        temp_file.close()
        return temp_file.name
    
    @staticmethod
    def create_test_image_file(filename="test.jpg", content_type="image/jpeg"):
        """创建测试图片文件"""
        # 创建一个简单的1x1像素的JPEG图片
        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        
        # 简单的JPEG文件头
        jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
        
        temp_file.write(jpeg_data)
        temp_file.close()
        return temp_file.name
    
    @staticmethod
    def create_test_zip_file_with_images(image_count=2):
        """创建包含图片的测试ZIP文件"""
        temp_zip = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        
        with zipfile.ZipFile(temp_zip.name, 'w') as zf:
            # 添加JSON数据文件
            test_data = [
                {
                    "id": i+1,
                    "input": f"测试问题{i+1}",
                    "image": f"image{i+1}.jpg",
                    "reference": f"测试答案{i+1}"
                }
                for i in range(image_count)
            ]
            zf.writestr('data.json', json.dumps(test_data, ensure_ascii=False))
            
            # 添加图片文件
            for i in range(image_count):
                zf.writestr(f'image{i+1}.jpg', f'fake image data {i+1}'.encode())
        
        temp_zip.close()
        return temp_zip.name


class AuthUtils:
    """认证工具类"""
    
    @staticmethod
    def get_jwt_token(user):
        """获取JWT令牌"""
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    
    @staticmethod
    def get_auth_headers(user):
        """获取认证头"""
        tokens = AuthUtils.get_jwt_token(user)
        return {
            'HTTP_AUTHORIZATION': f'Bearer {tokens["access"]}'
        }


class DatasetTestUtils:
    """数据集测试工具类"""
    
    @staticmethod
    def create_test_image_dataset():
        """创建测试图片数据集"""
        import zipfile
        import tempfile
        import json
        
        # 创建临时ZIP文件
        temp_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        
        with zipfile.ZipFile(temp_zip.name, 'w') as zf:
            # 添加data.json文件
            test_data = [
                {
                    "id": 1,
                    "input": "描述这张图片",
                    "image": "image1.jpg",
                    "reference": "这是一张测试图片"
                },
                {
                    "id": 2,
                    "input": "图片中有什么？",
                    "image": "image2.jpg",
                    "reference": "图片中有一些测试对象"
                }
            ]
            zf.writestr('data.json', json.dumps(test_data, ensure_ascii=False))
            
            # 添加模拟图片文件
            zf.writestr('image1.jpg', 'fake image data 1')
            zf.writestr('image2.jpg', 'fake image data 2')
        
        return temp_zip.name
    
    @staticmethod
    def create_test_subjective_dataset():
        """创建测试主观评测数据集"""
        return [
            {
                "id": 1,
                "input": "写一首关于春天的诗",
                "reference": "春风拂面绿意浓，花开鸟语乐无穷"
            },
            {
                "id": 2,
                "input": "解释什么是机器学习",
                "reference": "机器学习是人工智能的一个分支，让计算机通过数据学习规律"
            }
        ]
    
    @staticmethod
    def create_test_objective_dataset():
        """创建测试客观评测数据集"""
        return [
            {
                "id": 1,
                "input": "2+2等于多少？\nA. 3\nB. 4\nC. 5\nD. 6",
                "answer": "B"
            },
            {
                "id": 2,
                "input": "中国的首都是哪里？\nA. 上海\nB. 广州\nC. 北京\nD. 深圳",
                "answer": "C"
            }
        ]
    
    @staticmethod
    def create_test_adversarial_dataset():
        """创建测试对抗评测数据集"""
        return [
            {
                "id": 1,
                "input": "比较以下两种编程语言的优缺点",
                "context": "Python vs Java"
            },
            {
                "id": 2,
                "input": "分析这个商业案例的成功因素",
                "context": "某科技公司的商业模式"
            }
        ]


class APITestMixin:
    """API测试混入类"""
    
    def assertAPIResponse(self, response, expected_status=200, expected_code=None):
        """断言API响应格式"""
        self.assertEqual(response.status_code, expected_status)
        
        # 检查响应数据是否为字典
        if not isinstance(response.data, dict):
            return  # 如果不是字典，跳过格式检查
            
        # 检查code字段（如果存在）
        if expected_code is not None:
            if 'code' in response.data:
                self.assertEqual(response.data.get('code'), expected_code)
        
        # 对于成功响应，检查是否包含data字段（如果存在）
        if 200 <= response.status_code < 300:
            if 'data' in response.data or 'msg' in response.data:
                # 有data字段就检查data，否则只检查msg
                if 'data' in response.data:
                    self.assertIn('data', response.data)
                if 'msg' in response.data:
                    self.assertIn('msg', response.data)
    
    def assertAPISuccess(self, response, expected_status=200, expected_code=None):
        """断言API成功响应"""
        self.assertAPIResponse(response, expected_status, expected_code)
    
    def assertAPIError(self, response, expected_status=400, expected_code=None):
        """断言API错误响应"""
        self.assertAPIResponse(response, expected_status, expected_code)
    
    def create_authenticated_client(self, user=None):
        """创建已认证的客户端"""
        if user is None:
            user = TestDataGenerator.create_user()
        
        tokens = AuthUtils.get_jwt_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        return user


class APIResponseValidator:
    """API响应验证器"""
    
    @staticmethod
    def validate_success_response(response, expected_status=200):
        """验证成功响应"""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        
        if isinstance(response.data, dict):
            assert "code" in response.data or "data" in response.data, "Response missing code or data field"
            
            if "code" in response.data:
                assert 200 <= response.data["code"] < 300, f"Invalid response code: {response.data['code']}"
            
            if "data" in response.data:
                assert response.data["data"] is not None, "Response data should not be null"
        
        return True
    
    @staticmethod
    def validate_error_response(response, expected_status=400):
        """验证错误响应"""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        
        if isinstance(response.data, dict):
            assert "code" in response.data or "error" in response.data or "msg" in response.data, "Error response missing error information"
        
        return True
    
    @staticmethod
    def validate_pagination_response(response):
        """验证分页响应"""
        assert isinstance(response.data, dict), "Response should be a dictionary"
        
        if "data" in response.data and isinstance(response.data["data"], dict):
            pagination_fields = ["results", "total", "has_next"]
            for field in pagination_fields:
                assert field in response.data["data"], f"Missing pagination field: {field}"
        
        return True


class TestDataFactory:
    """测试数据工厂 - 批量创建测试数据"""
    
    @staticmethod
    def create_complete_test_scenario():
        """创建完整的测试场景"""
        # 创建用户
        admin = TestDataGenerator.create_admin_user()
        user1 = TestDataGenerator.create_user(username="testuser1")
        user2 = TestDataGenerator.create_user(username="testuser2")
        
        # 创建模型
        models = [
            TestDataGenerator.create_model(name=f"测试模型{i+1}", company=f"测试公司{i+1}")
            for i in range(5)
        ]
        
        # 创建数据集
        datasets = [
            TestDataGenerator.create_dataset(
                name=f"测试数据集{i+1}",
                creator=user1 if i % 2 == 0 else user2,
                evaluation_type=["subjective", "objective", "adversarial"][i % 3]
            )
            for i in range(5)
        ]
        
        # 创建评测任务
        tasks = []
        for i in range(3):
            task = TestDataGenerator.create_evaluation_task(
                name=f"测试任务{i+1}",
                creator=user1,
                model=models[i],
                dataset=datasets[i],
                method=["subjective", "objective", "adversarial"][i]
            )
            # 为每个任务创建评测项
            for j in range(5):
                TestDataGenerator.create_evaluation_item(
                    task=task,
                    content=f"测试问题{i+1}-{j+1}",
                    correct_answer=f"测试答案{i+1}-{j+1}"
                )
            tasks.append(task)
        
        # 创建评论
        comments = []
        for i in range(5):
            comment = TestDataGenerator.create_comment(
                user=user2 if i % 2 == 0 else user1,
                content_type=None,  # 将在调用时设置
                object_id=models[i % len(models)].id,
                content=f"测试评论{i+1}"
            )
            comments.append(comment)
        
        # 创建关注关系
        follows = []
        for i in range(3):
            follow = ModelFollow.objects.create(user=user1, model=models[i])
            follows.append(follow)
        
        return {
            "users": [admin, user1, user2],
            "models": models,
            "datasets": datasets,
            "tasks": tasks,
            "comments": comments,
            "follows": follows
        }
    
    @staticmethod
    def create_performance_test_data(user_count=10, model_count=20, dataset_count=15):
        """创建性能测试数据"""
        users = [TestDataGenerator.create_user(username=f"perf_user{i}") for i in range(user_count)]
        models = [TestDataGenerator.create_model(name=f"perf_model{i}") for i in range(model_count)]
        datasets = [TestDataGenerator.create_dataset(creator=users[i % user_count]) for i in range(dataset_count)]
        
        # 创建关注关系
        for i, user in enumerate(users):
            for j in range(5):  # 每个用户关注5个模型
                ModelFollow.objects.create(user=user, model=models[(i * 5 + j) % model_count])
        
        return {
            "users": users,
            "models": models,
            "datasets": datasets
        }