"""
评论系统API全面测试
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from tests.test_utils import TestDataGenerator, AuthUtils, APITestMixin

User = get_user_model()


class CommentListAPITest(TestCase, APITestMixin):
    """评论列表API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = TestDataGenerator.create_user(username="user1")
        self.user2 = TestDataGenerator.create_user(username="user2")
        
        # 创建测试模型和数据集
        self.model1 = TestDataGenerator.create_model(name="模型1")
        self.model2 = TestDataGenerator.create_model(name="模型2")
        self.dataset1 = TestDataGenerator.create_dataset(name="数据集1", creator=self.user1)
        
        # 创建测试评论
        from apps.comments.models import Comment
        self.comment1 = Comment.objects.create(
            user=self.user1,
            content="这是模型1的评论1",
            object_id=self.model1.id,
            content_type=self.get_content_type('model')
        )
        self.comment2 = Comment.objects.create(
            user=self.user2,
            content="这是模型1的评论2",
            object_id=self.model1.id,
            content_type=self.get_content_type('model')
        )
        self.comment3 = Comment.objects.create(
            user=self.user1,
            content="这是数据集1的评论1",
            object_id=self.dataset1.id,
            content_type=self.get_content_type('dataset')
        )
        
        # 创建点赞
        from apps.comments.models import CommentLike
        CommentLike.objects.create(user=self.user1, comment=self.comment2)
        CommentLike.objects.create(user=self.user2, comment=self.comment1)
    
    def get_content_type(self, target_type):
        """获取ContentType对象"""
        from django.contrib.contenttypes.models import ContentType
        if target_type == 'model':
            return ContentType.objects.get(app_label='models', model='my_model')
        elif target_type == 'dataset':
            return ContentType.objects.get(app_label='datasets', model='dataset')
    
    def test_list_comments_model_success(self):
        """测试获取模型评论列表成功"""
        response = self.client.get("/api/comments/?target_type=model&target_id=" + str(self.model1.id))
        self.assertAPISuccess(response, 200)
        
        # 检查返回数据结构
        self.assertIn("data", response.data)
        self.assertIn("results", response.data["data"])
        self.assertIn("total", response.data["data"])
        self.assertIn("has_next", response.data["data"])
        
        # 检查评论数量
        self.assertEqual(len(response.data["data"]["results"]), 2)
        
        # 检查评论内容
        comments = response.data["data"]["results"]
        contents = [comment["content"] for comment in comments]
        self.assertIn("这是模型1的评论1", contents)
        self.assertIn("这是模型1的评论2", contents)
    
    def test_list_comments_dataset_success(self):
        """测试获取数据集评论列表成功"""
        response = self.client.get("/api/comments/?target_type=dataset&target_id=" + str(self.dataset1.id))
        self.assertAPISuccess(response, 200)
        
        # 检查评论数量
        self.assertEqual(len(response.data["data"]["results"]), 1)
        
        # 检查评论内容
        comment = response.data["data"]["results"][0]
        self.assertEqual(comment["content"], "这是数据集1的评论1")
    
    def test_list_comments_missing_params(self):
        """测试缺少必要参数的评论列表请求"""
        # 缺少target_type
        response = self.client.get("/api/comments/?target_id=" + str(self.model1.id))
        self.assertAPIError(response, 400)
        
        # 缺少target_id
        response = self.client.get("/api/comments/?target_type=model")
        self.assertAPIError(response, 400)
    
    def test_list_comments_invalid_target_type(self):
        """测试无效的target_type"""
        response = self.client.get("/api/comments/?target_type=invalid&target_id=" + str(self.model1.id))
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]["results"]), 0)
    
    def test_list_comments_nonexistent_target(self):
        """测试不存在的目标对象"""
        response = self.client.get("/api/comments/?target_type=model&target_id=99999")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]["results"]), 0)
    
    def test_list_comments_with_authentication(self):
        """测试认证用户获取评论列表"""
        self.create_authenticated_client(self.user1)
        
        response = self.client.get("/api/comments/?target_type=model&target_id=" + str(self.model1.id))
        self.assertAPISuccess(response, 200)
        
        # 检查is_liked和is_owner字段
        comments = response.data["data"]["results"]
        for comment in comments:
            self.assertIn("is_liked", comment)
            self.assertIn("is_owner", comment)
            self.assertIn("likes_count", comment)
            
            # 检查用户信息
            self.assertIn("user", comment)
            self.assertIn("id", comment["user"])
            self.assertIn("username", comment["user"])
    
    def test_list_comments_pagination(self):
        """测试评论分页"""
        # 创建更多评论
        from apps.comments.models import Comment
        for i in range(15):
            Comment.objects.create(
                user=self.user1,
                content=f"额外评论{i}",
                object_id=self.model1.id,
                content_type=self.get_content_type('model')
            )
        
        # 测试第一页
        response = self.client.get("/api/comments/?target_type=model&target_id=" + str(self.model1.id) + "&page=1&page_size=5")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]["results"]), 5)
        self.assertTrue(response.data["data"]["has_next"])
        
        # 测试第二页
        response = self.client.get("/api/comments/?target_type=model&target_id=" + str(self.model1.id) + "&page=2&page_size=5")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]["results"]), 5)


class CommentCreateAPITest(TestCase, APITestMixin):
    """评论创建API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.model = TestDataGenerator.create_model()
        self.dataset = TestDataGenerator.create_dataset()
    
    def test_create_comment_model_success(self):
        """测试创建模型评论成功"""
        self.create_authenticated_client(self.user)
        
        data = {
            "target_type": "model",
            "target_id": self.model.id,
            "content": "这是一个新的模型评论"
        }
        
        response = self.client.post("/api/comments/", data, format="json")
        self.assertAPISuccess(response, 201)
        
        # 检查返回数据
        self.assertEqual(response.data["msg"], "评论发布成功")
        self.assertEqual(response.data["data"]["content"], "这是一个新的模型评论")
        self.assertTrue(response.data["data"]["is_owner"])
        self.assertFalse(response.data["data"]["is_liked"])
        self.assertEqual(response.data["data"]["likes_count"], 0)
        
        # 验证数据库中的评论
        from apps.comments.models import Comment
        self.assertTrue(Comment.objects.filter(
            user=self.user,
            content="这是一个新的模型评论",
            object_id=self.model.id
        ).exists())
    
    def test_create_comment_dataset_success(self):
        """测试创建数据集评论成功"""
        self.create_authenticated_client(self.user)
        
        data = {
            "target_type": "dataset",
            "target_id": self.dataset.id,
            "content": "这是一个新的数据集评论"
        }
        
        response = self.client.post("/api/comments/", data, format="json")
        self.assertAPISuccess(response, 201)
        
        # 验证数据库中的评论
        from apps.comments.models import Comment
        from django.contrib.contenttypes.models import ContentType
        dataset_ct = ContentType.objects.get(app_label='datasets', model='dataset')
        self.assertTrue(Comment.objects.filter(
            user=self.user,
            content="这是一个新的数据集评论",
            object_id=self.dataset.id,
            content_type=dataset_ct
        ).exists())
    
    def test_create_comment_unauthorized(self):
        """测试未授权用户创建评论"""
        data = {
            "target_type": "model",
            "target_id": self.model.id,
            "content": "这是一个未授权的评论"
        }
        
        response = self.client.post("/api/comments/", data, format="json")
        self.assertEqual(response.status_code, 403)
    
    def test_create_comment_invalid_target_type(self):
        """测试创建评论时使用无效的target_type"""
        self.create_authenticated_client(self.user)
        
        data = {
            "target_type": "invalid_type",
            "target_id": self.model.id,
            "content": "这是一个无效目标类型的评论"
        }
        
        response = self.client.post("/api/comments/", data, format="json")
        self.assertAPIError(response, 400)
    
    def test_create_comment_nonexistent_target(self):
        """测试创建评论时使用不存在的目标对象"""
        self.create_authenticated_client(self.user)
        
        data = {
            "target_type": "model",
            "target_id": 99999,
            "content": "这是一个不存在目标的评论"
        }
        
        response = self.client.post("/api/comments/", data, format="json")
        self.assertAPIError(response, 400)
    
    def test_create_comment_empty_content(self):
        """测试创建空内容的评论"""
        self.create_authenticated_client(self.user)
        
        data = {
            "target_type": "model",
            "target_id": self.model.id,
            "content": ""
        }
        
        response = self.client.post("/api/comments/", data, format="json")
        self.assertAPIError(response, 400)


class CommentDeleteAPITest(TestCase, APITestMixin):
    """评论删除API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = TestDataGenerator.create_user(username="user1")
        self.user2 = TestDataGenerator.create_user(username="user2")
        self.model = TestDataGenerator.create_model()
        
        # 创建测试评论
        from apps.comments.models import Comment
        from django.contrib.contenttypes.models import ContentType
        model_ct = ContentType.objects.get(app_label='models', model='my_model')
        
        self.comment1 = Comment.objects.create(
            user=self.user1,
            content="用户1的评论",
            object_id=self.model.id,
            content_type=model_ct
        )
        self.comment2 = Comment.objects.create(
            user=self.user2,
            content="用户2的评论",
            object_id=self.model.id,
            content_type=model_ct
        )
    
    def test_delete_own_comment_success(self):
        """测试删除自己的评论成功"""
        self.create_authenticated_client(self.user1)
        
        response = self.client.delete(f"/api/comments/{self.comment1.id}/")
        self.assertAPISuccess(response, 200)
        self.assertEqual(response.data["msg"], "删除成功")
        
        # 验证评论已被删除
        from apps.comments.models import Comment
        self.assertFalse(Comment.objects.filter(id=self.comment1.id).exists())
    
    def test_delete_other_comment_forbidden(self):
        """测试删除他人评论被禁止"""
        self.create_authenticated_client(self.user1)
        
        response = self.client.delete(f"/api/comments/{self.comment2.id}/")
        self.assertAPIError(response, 403)
        self.assertEqual(response.data["msg"], "您只能删除自己的评论")
        
        # 验证评论未被删除
        from apps.comments.models import Comment
        self.assertTrue(Comment.objects.filter(id=self.comment2.id).exists())
    
    def test_delete_comment_unauthorized(self):
        """测试未授权用户删除评论"""
        response = self.client.delete(f"/api/comments/{self.comment1.id}/")
        self.assertEqual(response.status_code, 403)
    
    def test_delete_nonexistent_comment(self):
        """测试删除不存在的评论"""
        self.create_authenticated_client(self.user1)
        
        response = self.client.delete("/api/comments/99999/")
        self.assertEqual(response.status_code, 404)


class CommentLikeAPITest(TestCase, APITestMixin):
    """评论点赞API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = TestDataGenerator.create_user(username="user1")
        self.user2 = TestDataGenerator.create_user(username="user2")
        self.model = TestDataGenerator.create_model()
        
        # 创建测试评论
        from apps.comments.models import Comment
        from django.contrib.contenttypes.models import ContentType
        model_ct = ContentType.objects.get(app_label='models', model='my_model')
        
        self.comment = Comment.objects.create(
            user=self.user1,
            content="测试评论",
            object_id=self.model.id,
            content_type=model_ct
        )
    
    def test_like_comment_success(self):
        """测试点赞评论成功"""
        self.create_authenticated_client(self.user2)
        
        response = self.client.post(f"/api/comments/{self.comment.id}/like/")
        self.assertAPISuccess(response, 200)
        self.assertEqual(response.data["msg"], "点赞成功")
        self.assertTrue(response.data["data"]["is_liked"])
        self.assertEqual(response.data["data"]["likes_count"], 1)
        
        # 验证点赞记录
        from apps.comments.models import CommentLike
        self.assertTrue(CommentLike.objects.filter(
            user=self.user2,
            comment=self.comment
        ).exists())
    
    def test_unlike_comment_success(self):
        """测试取消点赞评论成功"""
        self.create_authenticated_client(self.user2)
        
        # 先点赞
        from apps.comments.models import CommentLike
        CommentLike.objects.create(user=self.user2, comment=self.comment)
        
        # 再取消点赞
        response = self.client.post(f"/api/comments/{self.comment.id}/like/")
        self.assertAPISuccess(response, 200)
        self.assertEqual(response.data["msg"], "取消点赞成功")
        self.assertFalse(response.data["data"]["is_liked"])
        self.assertEqual(response.data["data"]["likes_count"], 0)
        
        # 验证点赞记录已删除
        self.assertFalse(CommentLike.objects.filter(
            user=self.user2,
            comment=self.comment
        ).exists())
    
    def test_like_own_comment(self):
        """测试点赞自己的评论"""
        self.create_authenticated_client(self.user1)
        
        response = self.client.post(f"/api/comments/{self.comment.id}/like/")
        self.assertAPISuccess(response, 200)
        self.assertEqual(response.data["msg"], "点赞成功")
        self.assertTrue(response.data["data"]["is_liked"])
        self.assertEqual(response.data["data"]["likes_count"], 1)
    
    def test_like_comment_unauthorized(self):
        """测试未授权用户点赞评论"""
        response = self.client.post(f"/api/comments/{self.comment.id}/like/")
        self.assertEqual(response.status_code, 403)
    
    def test_like_nonexistent_comment(self):
        """测试点赞不存在的评论"""
        self.create_authenticated_client(self.user2)
        
        response = self.client.post("/api/comments/99999/like/")
        self.assertEqual(response.status_code, 404)


class CommentIntegrationAPITest(TestCase, APITestMixin):
    """评论系统集成测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = TestDataGenerator.create_user(username="user1")
        self.user2 = TestDataGenerator.create_user(username="user2")
        self.model = TestDataGenerator.create_model()
        self.dataset = TestDataGenerator.create_dataset()
    
    def test_comment_workflow(self):
        """测试完整的评论工作流程"""
        # 1. 用户1创建评论
        self.create_authenticated_client(self.user1)
        data = {
            "target_type": "model",
            "target_id": self.model.id,
            "content": "用户1的第一个评论"
        }
        response = self.client.post("/api/comments/", data, format="json")
        self.assertAPISuccess(response, 201)
        comment_id = response.data["data"]["id"]
        
        # 2. 获取评论列表
        response = self.client.get(f"/api/comments/?target_type=model&target_id={self.model.id}")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        
        # 3. 用户2点赞评论
        self.create_authenticated_client(self.user2)
        response = self.client.post(f"/api/comments/{comment_id}/like/")
        self.assertAPISuccess(response, 200)
        self.assertEqual(response.data["data"]["likes_count"], 1)
        
        # 4. 用户2创建评论
        data = {
            "target_type": "model",
            "target_id": self.model.id,
            "content": "用户2的回复"
        }
        response = self.client.post("/api/comments/", data, format="json")
        self.assertAPISuccess(response, 201)
        
        # 5. 验证评论列表
        response = self.client.get(f"/api/comments/?target_type=model&target_id={self.model.id}")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]["results"]), 2)
        
        # 6. 用户1删除自己的评论
        self.create_authenticated_client(self.user1)
        response = self.client.delete(f"/api/comments/{comment_id}/")
        self.assertAPISuccess(response, 200)
        
        # 7. 验证评论已删除
        response = self.client.get(f"/api/comments/?target_type=model&target_id={self.model.id}")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["results"][0]["content"], "用户2的回复")
    
    def test_multiple_targets_comments(self):
        """测试多个目标对象的评论"""
        # 为模型创建评论
        self.create_authenticated_client(self.user1)
        data = {
            "target_type": "model",
            "target_id": self.model.id,
            "content": "这是模型的评论"
        }
        response = self.client.post("/api/comments/", data, format="json")
        self.assertAPISuccess(response, 201)
        
        # 为数据集创建评论
        data = {
            "target_type": "dataset",
            "target_id": self.dataset.id,
            "content": "这是数据集的评论"
        }
        response = self.client.post("/api/comments/", data, format="json")
        self.assertAPISuccess(response, 201)
        
        # 验证模型评论
        response = self.client.get(f"/api/comments/?target_type=model&target_id={self.model.id}")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["results"][0]["content"], "这是模型的评论")
        
        # 验证数据集评论
        response = self.client.get(f"/api/comments/?target_type=dataset&target_id={self.dataset.id}")
        self.assertAPISuccess(response, 200)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["results"][0]["content"], "这是数据集的评论")