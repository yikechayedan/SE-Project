# apps/models/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from rest_framework_simplejwt.tokens import RefreshToken  # 导入 JWT Token 生成工具
from .models import My_Model, ModelFollow

# 获取自定义用户模型（users.User）
User = get_user_model()

class ModelsAPITestCase(TestCase):
    def setUp(self):
        # 1. 创建测试用户
        self.user = User.objects.create_user(
            username='test_user',
            password='test123456',
            phone='13800138000'
        )
        
        # 2. 生成 JWT Token（核心：适配 settings.py 中的 JWT 认证）
        refresh = RefreshToken.for_user(self.user)  # 生成刷新令牌
        self.access_token = str(refresh.access_token)  # 获取访问令牌
        # 构造 JWT 请求头（格式：Bearer <token>）
        self.jwt_header = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        
        # 3. 创建测试模型数据
        self.model = My_Model.objects.create(
            name='测试大模型',
            company='测试公司',
            category='text',
            parameter_size='10B',
            description='测试描述',
            version='v1.0',
            official_url='https://test-model.example.com'
        )

    # 测试模型列表接口（匿名访问，无需 Token）
    def test_model_list_api(self):
        response = self.client.get('/api/models/')
        self.assertEqual(response.status_code, 200, "模型列表接口返回非200状态码")
        self.assertEqual(len(response.data), 1, "模型列表未返回测试数据")
        self.assertEqual(response.data[0]['name'], '测试大模型', "返回数据不匹配")

    # 测试关注模型接口（JWT 认证）
    def test_model_follow_api(self):
        # 发送 POST 请求，携带 JWT Token 头
        follow_url = f'/api/models/{self.model.id}/follow/'
        response = self.client.post(
            follow_url,
            {},  # POST 请求体（无参数则传空字典）
            **self.jwt_header  # 传入 JWT 认证头
        )
        
        # 验证接口返回成功状态码
        self.assertIn(
            response.status_code,
            [200, 201],
            f"关注接口返回非成功状态码：{response.status_code}，响应内容：{response.data}"
        )
        
        # 验证数据库中创建关注记录
        self.assertTrue(
            ModelFollow.objects.filter(user=self.user, model=self.model).exists(),
            "关注记录未创建"
        )
