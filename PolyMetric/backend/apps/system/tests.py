from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import SystemEvent
from apps.datasets.models import Dataset
from apps.models.models import My_Model

User = get_user_model()


class SystemEventTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_news_feed_api(self):
        """测试新闻流API"""
        # 创建一些测试数据
        SystemEvent.objects.create(
            event_type='dataset_upload',
            actor_id=self.user.id,
            actor_name=self.user.username,
            target_name='测试数据集',
            message='用户 testuser 上传了新数据集「测试数据集」'
        )
        
        SystemEvent.objects.create(
            event_type='model_add',
            actor_name='系统管理员',
            target_name='测试模型',
            target_extra='测试公司',
            message='平台新收录模型：测试模型 (测试公司)'
        )
        
        # 调用API
        response = self.client.get('/api/system/news/')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)
        
        # 验证数据格式
        first_event = response.data['data'][0]
        self.assertIn('id', first_event)
        self.assertIn('content', first_event)
        self.assertIn('time', first_event)
        self.assertIn('type', first_event)
        self.assertIn('icon', first_event)
        
    def test_dataset_upload_signal(self):
        """测试数据集上传信号"""
        # 创建数据集
        dataset = Dataset.objects.create(
            name='测试数据集',
            description='这是一个测试数据集',
            category='text',
            file_format='json',
            creator=self.user,
            is_public=True
        )
        
        # 验证是否创建了系统事件
        event = SystemEvent.objects.filter(event_type='dataset_upload').first()
        self.assertIsNotNone(event)
        self.assertEqual(event.actor_id, self.user.id)
        self.assertEqual(event.target_name, '测试数据集')
        
    def test_model_add_signal(self):
        """测试模型添加信号"""
        # 创建模型
        model = My_Model.objects.create(
            name='测试模型',
            company='测试公司',
            category='text'
        )
        
        # 验证是否创建了系统事件
        event = SystemEvent.objects.filter(event_type='model_add').first()
        self.assertIsNotNone(event)
        self.assertEqual(event.target_name, '测试模型')
        self.assertEqual(event.target_extra, '测试公司')