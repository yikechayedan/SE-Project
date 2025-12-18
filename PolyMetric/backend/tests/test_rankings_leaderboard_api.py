"""
排行榜API测试
"""
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from rest_framework import status
from tests.test_utils import TestDataGenerator, APITestMixin
from apps.rankings.models import ModelDimensionScore
from apps.users.models import UserStar


class LeaderboardAPITest(TestCase, APITestMixin):
    """排行榜API测试"""
    
    def setUp(self):
        self.client = APIClient()
        
        # 创建测试模型
        self.model1 = TestDataGenerator.create_model(
            name="GPT-4o",
            company="OpenAI",
            category="text"
        )
        self.model2 = TestDataGenerator.create_model(
            name="Claude 3.5",
            company="Anthropic",
            category="text"
        )
        self.model3 = TestDataGenerator.create_model(
            name="Gemini Pro",
            company="Google",
            category="multimodal"
        )
        
        # 为模型创建维度分数
        # Model1 - GPT-4o (最高分)
        ModelDimensionScore.objects.create(
            model=self.model1,
            dimension='overall',
            score=92.5,
            previous_score=90.0
        )
        ModelDimensionScore.objects.create(
            model=self.model1,
            dimension='language',
            score=94.0,
            previous_score=93.0
        )
        ModelDimensionScore.objects.create(
            model=self.model1,
            dimension='math',
            score=91.0,
            previous_score=91.0
        )
        ModelDimensionScore.objects.create(
            model=self.model1,
            dimension='code',
            score=93.5,
            previous_score=92.0
        )
        ModelDimensionScore.objects.create(
            model=self.model1,
            dimension='multimodal',
            score=88.0,
            previous_score=87.0
        )
        
        # Model2 - Claude 3.5 (第二名)
        ModelDimensionScore.objects.create(
            model=self.model2,
            dimension='overall',
            score=91.2,
            previous_score=92.0
        )
        ModelDimensionScore.objects.create(
            model=self.model2,
            dimension='language',
            score=93.5,
            previous_score=93.0
        )
        ModelDimensionScore.objects.create(
            model=self.model2,
            dimension='math',
            score=89.5,
            previous_score=89.0
        )
        ModelDimensionScore.objects.create(
            model=self.model2,
            dimension='code',
            score=91.8,
            previous_score=91.0
        )
        ModelDimensionScore.objects.create(
            model=self.model2,
            dimension='multimodal',
            score=90.2,
            previous_score=90.0
        )
        
        # Model3 - Gemini Pro (第三名)
        ModelDimensionScore.objects.create(
            model=self.model3,
            dimension='overall',
            score=89.8,
            previous_score=89.8
        )
        ModelDimensionScore.objects.create(
            model=self.model3,
            dimension='language',
            score=90.5,
            previous_score=90.5
        )
        ModelDimensionScore.objects.create(
            model=self.model3,
            dimension='math',
            score=88.0,
            previous_score=88.0
        )
        ModelDimensionScore.objects.create(
            model=self.model3,
            dimension='code',
            score=87.5,
            previous_score=87.5
        )
        ModelDimensionScore.objects.create(
            model=self.model3,
            dimension='multimodal',
            score=92.0,
            previous_score=91.0
        )
        
        # 为模型添加点赞
        model_content_type = ContentType.objects.get_for_model(self.model1)
        UserStar.objects.create(
            user=TestDataGenerator.create_user(username="user1"),
            content_type=model_content_type,
            object_id=self.model1.id
        )
        UserStar.objects.create(
            user=TestDataGenerator.create_user(username="user2"),
            content_type=model_content_type,
            object_id=self.model1.id
        )
        
        model2_content_type = ContentType.objects.get_for_model(self.model2)
        UserStar.objects.create(
            user=TestDataGenerator.create_user(username="user3"),
            content_type=model2_content_type,
            object_id=self.model2.id
        )
    
    def test_leaderboard_success(self):
        """测试获取排行榜成功"""
        response = self.client.get("/api/rankings/leaderboard/")
        self.assertAPISuccess(response, 200)
        
        # 检查响应数据结构
        self.assertIn("data", response.data)
        self.assertEqual(len(response.data["data"]), 3)
        
        # 检查排名顺序（按overall分数降序）
        leaderboard = response.data["data"]
        self.assertEqual(leaderboard[0]["name"], "GPT-4o")
        self.assertEqual(leaderboard[0]["rank"], 1)
        self.assertEqual(leaderboard[1]["name"], "Claude 3.5")
        self.assertEqual(leaderboard[1]["rank"], 2)
        self.assertEqual(leaderboard[2]["name"], "Gemini Pro")
        self.assertEqual(leaderboard[2]["rank"], 3)
    
    def test_leaderboard_data_structure(self):
        """测试排行榜数据结构"""
        response = self.client.get("/api/rankings/leaderboard/")
        self.assertAPISuccess(response, 200)
        
        leaderboard = response.data["data"]
        first_item = leaderboard[0]
        
        # 检查必需字段
        required_fields = ["rank", "model_id", "name", "company", "category", "star_count", "scores", "trends"]
        for field in required_fields:
            self.assertIn(field, first_item)
        
        # 检查分数字段
        scores = first_item["scores"]
        required_dimensions = ["overall", "language", "math", "code", "multimodal"]
        for dimension in required_dimensions:
            self.assertIn(dimension, scores)
        
        # 检查趋势字段
        trends = first_item["trends"]
        for dimension in required_dimensions:
            self.assertIn(dimension, trends)
            self.assertIn(trends[dimension], ["up", "down", "stable"])
    
    def test_leaderboard_trends_calculation(self):
        """测试趋势计算"""
        response = self.client.get("/api/rankings/leaderboard/")
        self.assertAPISuccess(response, 200)
        
        leaderboard = response.data["data"]
        
        # GPT-4o: overall分数从90.0上升到92.5，应该是"up"
        gpt_trends = leaderboard[0]["trends"]
        self.assertEqual(gpt_trends["overall"], "up")
        self.assertEqual(gpt_trends["language"], "up")
        self.assertEqual(gpt_trends["math"], "stable")  # 分数没变
        self.assertEqual(gpt_trends["code"], "up")
        self.assertEqual(gpt_trends["multimodal"], "up")
        
        # Claude 3.5: overall分数从92.0下降到91.2，应该是"down"
        claude_trends = leaderboard[1]["trends"]
        self.assertEqual(claude_trends["overall"], "down")
        self.assertEqual(claude_trends["language"], "up")
        self.assertEqual(claude_trends["math"], "up")
        self.assertEqual(claude_trends["code"], "up")
        self.assertEqual(claude_trends["multimodal"], "up")
        
        # Gemini Pro: 所有分数都没变，应该是"stable"
        gemini_trends = leaderboard[2]["trends"]
        self.assertEqual(gemini_trends["overall"], "stable")
        self.assertEqual(gemini_trends["language"], "stable")
        self.assertEqual(gemini_trends["math"], "stable")
        self.assertEqual(gemini_trends["code"], "stable")
        self.assertEqual(gemini_trends["multimodal"], "up")
    
    def test_leaderboard_star_count(self):
        """测试点赞数统计"""
        response = self.client.get("/api/rankings/leaderboard/")
        self.assertAPISuccess(response, 200)
        
        leaderboard = response.data["data"]
        
        # GPT-4o有2个点赞
        self.assertEqual(leaderboard[0]["star_count"], 2)
        
        # Claude 3.5有1个点赞
        self.assertEqual(leaderboard[1]["star_count"], 1)
        
        # Gemini Pro没有点赞
        self.assertEqual(leaderboard[2]["star_count"], 0)
    
    def test_leaderboard_empty_data(self):
        """测试空数据情况"""
        # 删除所有维度分数
        ModelDimensionScore.objects.all().delete()
        
        response = self.client.get("/api/rankings/leaderboard/")
        self.assertAPISuccess(response, 200)
        
        # 应该返回空列表
        self.assertEqual(len(response.data["data"]), 0)
    
    def test_leaderboard_model_without_overall_score(self):
        """测试没有overall分数的模型不出现在排行榜中"""
        # 创建一个没有overall分数的模型
        model_without_overall = TestDataGenerator.create_model(
            name="Test Model",
            company="Test Company"
        )
        ModelDimensionScore.objects.create(
            model=model_without_overall,
            dimension='language',
            score=85.0
        )
        
        response = self.client.get("/api/rankings/leaderboard/")
        self.assertAPISuccess(response, 200)
        
        # 应该仍然只有3个模型（不包括没有overall分数的模型）
        self.assertEqual(len(response.data["data"]), 3)
        
        # 确认没有overall分数的模型不在排行榜中
        model_names = [item["name"] for item in response.data["data"]]
        self.assertNotIn("Test Model", model_names)