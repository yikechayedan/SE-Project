"""
专业测试基类 - 提供业界标准的测试基础设施
"""
import time
import json
import logging
import os
import concurrent.futures
import threading
import tempfile
import zipfile
from io import BytesIO
from typing import Dict, Any, Optional, List, Union
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from datetime import datetime
import pytest

# 尝试导入 psutil，如果失败则设置为 None
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

User = get_user_model()


class BaseAPITestCase(TestCase):
    """API测试基类 - 提供标准化的API测试功能"""
    
    @classmethod
    def setUpClass(cls):
        """类级别的设置"""
        super().setUpClass()
        cls.logger = logging.getLogger(cls.__name__)
        cls.performance_data = []
    
    def setUp(self):
        """每个测试方法的设置"""
        super().setUp()
        self.client = APIClient()
        self.start_time = None
        self.response_times = []
    
    def tearDown(self):
        """每个测试方法的清理"""
        super().tearDown()
        # 记录性能数据
        if hasattr(self, 'response_times') and self.response_times:
            avg_time = sum(self.response_times) / len(self.response_times)
            self.performance_data.append({
                'test': self._testMethodName,
                'avg_response_time': avg_time,
                'request_count': len(self.response_times),
                'timestamp': datetime.now().isoformat()
            })
    
    def timed_request(self, method: str, url: str, **kwargs) -> Any:
        """记录响应时间的请求方法"""
        self.start_time = time.time()
        method_func = getattr(self.client, method.lower())
        response = method_func(url, **kwargs)
        end_time = time.time()
        response_time = end_time - self.start_time
        self.response_times.append(response_time)
        
        # 记录慢请求
        if response_time > 1.0:  # 超过1秒的请求
            self.logger.warning(
                f"Slow request detected: {method} {url} took {response_time:.2f}s"
            )
        
        return response
    
    def assertAPIPerformance(self, max_response_time: float = 1.0):
        """断言API性能"""
        if not self.response_times:
            return
        
        avg_time = sum(self.response_times) / len(self.response_times)
        max_time = max(self.response_times)
        
        self.assertLess(
            avg_time, max_response_time,
            f"Average response time {avg_time:.2f}s exceeds {max_response_time}s"
        )
        self.assertLess(
            max_time, max_response_time * 2,
            f"Max response time {max_time:.2f}s exceeds {max_response_time * 2}s"
        )
    
    def assertAPISchema(self, response, expected_schema: Dict[str, Any]):
        """断言API响应模式"""
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 检查标准响应格式
        if isinstance(response.data, dict):
            self.assertIn("code", response.data)
            self.assertIn("msg", response.data)
            if "data" in response.data:
                data = response.data["data"]
            else:
                data = response.data
        else:
            data = response.data
        
        def validate_schema(data, schema):
            if isinstance(schema, dict):
                self.assertIsInstance(data, dict)
                for key, value_schema in schema.items():
                    self.assertIn(key, data)
                    validate_schema(data[key], value_schema)
            elif isinstance(schema, list):
                self.assertIsInstance(data, list)
                if schema:  # 如果列表有模式定义
                    for item in data:
                        validate_schema(item, schema[0])
            elif isinstance(schema, type):
                self.assertIsInstance(data, schema)
        
        validate_schema(data, expected_schema)
    
    def assertAPIPagination(self, response, expected_count: Optional[int] = None):
        """断言API分页响应"""
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 检查标准响应格式
        if isinstance(response.data, dict):
            self.assertIn("code", response.data)
            self.assertIn("msg", response.data)
            
            # DRF分页格式
            if 'count' in response.data and 'next' in response.data and 'previous' in response.data:
                # DRF标准分页格式
                if expected_count is not None:
                    self.assertEqual(response.data['count'], expected_count)
            # 自定义分页格式
            elif 'data' in response.data and 'pagination' in response.data:
                pagination = response.data['pagination']
                required_fields = ['page', 'page_size', 'total', 'total_pages']
                for field in required_fields:
                    self.assertIn(field, pagination)
                
                if expected_count is not None:
                    self.assertEqual(len(response.data['data']), expected_count)
            # 只有data字段，无分页
            elif 'data' in response.data:
                if expected_count is not None:
                    self.assertEqual(len(response.data['data']), expected_count)
        else:
            # 直接是数据列表
            if expected_count is not None:
                self.assertEqual(len(response.data), expected_count)


class BaseIntegrationTestCase(TransactionTestCase):
    """集成测试基类 - 提供事务级别的集成测试"""
    
    def setUp(self):
        super().setUp()
        self.setup_test_data()
    
    def setup_test_data(self):
        """设置测试数据 - 子类重写"""
        pass
    
    def assertDatabaseState(self, model_class, expected_count: int):
        """断言数据库状态"""
        self.assertEqual(model_class.objects.count(), expected_count)
    
    def assertEventTriggered(self, event_type: str, expected_count: int = 1):
        """断言事件已触发"""
        try:
            from apps.system.models import SystemEvent
            events = SystemEvent.objects.filter(event_type=event_type)
            self.assertEqual(events.count(), expected_count)
        except ImportError:
            self.skipTest("SystemEvent model not available")


class BasePerformanceTestCase(TestCase):
    """性能测试基类 - 提供性能测试工具"""
    
    def setUp(self):
        super().setUp()
        self.performance_metrics = []
    
    def measure_performance(self, func, *args, **kwargs):
        """测量函数执行性能"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        self.performance_metrics.append({
            'function': func.__name__,
            'execution_time': execution_time,
            'memory_usage': memory_usage,
            'timestamp': datetime.now().isoformat()
        })
        
        return result
    
    def _get_memory_usage(self):
        """获取内存使用量"""
        if not PSUTIL_AVAILABLE:
            return 0
        
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss
        except Exception:
            return 0
    
    def assertPerformanceThreshold(self, max_execution_time: float, max_memory_mb: float = None):
        """断言性能阈值"""
        if not self.performance_metrics:
            return
        
        avg_time = sum(m['execution_time'] for m in self.performance_metrics) / len(self.performance_metrics)
        max_time = max(m['execution_time'] for m in self.performance_metrics)
        
        self.assertLess(
            avg_time, max_execution_time,
            f"Average execution time {avg_time:.2f}s exceeds {max_execution_time}s"
        )
        self.assertLess(
            max_time, max_execution_time * 2,
            f"Max execution time {max_time:.2f}s exceeds {max_execution_time * 2}s"
        )
        
        if max_memory_mb is not None:
            avg_memory = sum(m['memory_usage'] for m in self.performance_metrics) / len(self.performance_metrics)
            max_memory = max(m['memory_usage'] for m in self.performance_metrics)
            
            avg_memory_mb = avg_memory / (1024 * 1024)
            max_memory_mb_actual = max_memory / (1024 * 1024)
            
            self.assertLess(
                avg_memory_mb, max_memory_mb,
                f"Average memory usage {avg_memory_mb:.2f}MB exceeds {max_memory_mb}MB"
            )
            self.assertLess(
                max_memory_mb_actual, max_memory_mb * 2,
                f"Max memory usage {max_memory_mb_actual:.2f}MB exceeds {max_memory_mb * 2}MB"
            )


class BaseLoadTestCase(TestCase):
    """负载测试基类 - 提供负载测试工具"""
    
    def setUp(self):
        super().setUp()
        self.concurrent_results = []
    
    def run_concurrent_requests(self, url: str, method: str = 'GET',
                              num_requests: int = 10, **kwargs):
        """运行并发请求"""
        
        def make_request():
            client = APIClient()
            method_func = getattr(client, method.lower())
            start_time = time.time()
            try:
                response = method_func(url, **kwargs)
                end_time = time.time()
                return {
                    'status_code': response.status_code,
                    'response_time': end_time - start_time,
                    'success': 200 <= response.status_code < 300
                }
            except Exception as e:
                end_time = time.time()
                return {
                    'status_code': 0,
                    'response_time': end_time - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        self.concurrent_results = results
        return results
    
    def assertLoadPerformance(self, min_success_rate: float = 0.95, 
                            max_avg_response_time: float = 2.0):
        """断言负载性能"""
        if not self.concurrent_results:
            return
        
        success_count = sum(1 for r in self.concurrent_results if r['success'])
        success_rate = success_count / len(self.concurrent_results)
        
        avg_response_time = sum(r['response_time'] for r in self.concurrent_results) / len(self.concurrent_results)
        max_response_time = max(r['response_time'] for r in self.concurrent_results)
        
        self.assertGreaterEqual(
            success_rate, min_success_rate,
            f"Success rate {success_rate:.2f} below {min_success_rate:.2f}"
        )
        
        self.assertLess(
            avg_response_time, max_avg_response_time,
            f"Average response time {avg_response_time:.2f}s exceeds {max_avg_response_time}s"
        )
        
        # 记录负载测试结果
        self.logger.info(f"Load test results: {len(self.concurrent_results)} requests, "
                        f"success rate: {success_rate:.2f}, "
                        f"avg response time: {avg_response_time:.2f}s, "
                        f"max response time: {max_response_time:.2f}s")


class BaseContractTestCase(TestCase):
    """API契约测试基类 - 验证API契约一致性"""
    
    def assertAPIContract(self, response, contract_file: str):
        """断言API契约"""
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 加载契约文件
        contract_path = f"tests/contracts/{contract_file}"
        with open(contract_path, 'r', encoding='utf-8') as f:
            contract = json.load(f)
        
        # 验证响应结构
        self._validate_contract(response.data, contract)
    
    def _validate_contract(self, data, contract):
        """验证契约结构"""
        if isinstance(contract, dict):
            self.assertIsInstance(data, dict)
            for key, value_contract in contract.items():
                self.assertIn(key, data, f"Missing key: {key}")
                if key in data:
                    self._validate_contract(data[key], value_contract)
        elif isinstance(contract, list):
            self.assertIsInstance(data, list)
            if contract:  # 如果列表有契约定义
                for item in data:
                    self._validate_contract(item, contract[0])
        elif isinstance(contract, type):
            self.assertIsInstance(data, contract)
        elif isinstance(contract, dict) and '$ref' in contract:
            # 处理引用
            ref_name = contract['$ref']
            # 这里可以实现引用解析逻辑
            pass


class TestDataManager:
    """测试数据管理器 - 提供专业的测试数据管理"""
    
    def __init__(self):
        self.created_objects = []
    
    def create_user(self, **kwargs):
        """创建用户并跟踪"""
        try:
            from tests.factories import UserFactory
            user = UserFactory.create(**kwargs)
            self.created_objects.append(('user', user))
            return user
        except ImportError:
            raise ImportError("tests.factories module not available. Please ensure factories.py exists.")
    
    def create_model(self, **kwargs):
        """创建模型并跟踪"""
        try:
            from tests.factories import ModelFactory
            model = ModelFactory.create(**kwargs)
            self.created_objects.append(('model', model))
            return model
        except ImportError:
            raise ImportError("tests.factories module not available. Please ensure factories.py exists.")
    
    def create_dataset(self, **kwargs):
        """创建数据集并跟踪"""
        try:
            from tests.factories import DatasetFactory
            dataset = DatasetFactory.create(**kwargs)
            self.created_objects.append(('dataset', dataset))
            return dataset
        except ImportError:
            raise ImportError("tests.factories module not available. Please ensure factories.py exists.")
    
    def cleanup(self):
        """清理创建的对象"""
        for obj_type, obj in reversed(self.created_objects):
            try:
                obj.delete()
            except Exception as e:
                print(f"Error cleaning up {obj_type}: {e}")
        self.created_objects.clear()


class APITestHelper:
    """API测试辅助类 - 提供常用的API测试方法"""
    
    @staticmethod
    def create_auth_headers(user):
        """创建认证头"""
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            return {
                'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'
            }
        except ImportError:
            raise ImportError("rest_framework_simplejwt not available. Please install djangorestframework-simplejwt.")
    
    @staticmethod
    def assert_standard_response(response, expected_status=200):
        """断言标准API响应格式"""
        assert response.status_code == expected_status
        assert isinstance(response.data, dict)
        
        # 检查标准响应字段
        if 200 <= response.status_code < 300:
            assert 'data' in response.data or 'msg' in response.data
        else:
            assert 'error' in response.data or 'msg' in response.data
    
    @staticmethod
    def create_test_file(content=None, filename="test.json", content_type="application/json"):
        """创建测试文件"""
        if content is None:
            content = json.dumps({"test": "data"})
        
        if isinstance(content, dict):
            content = json.dumps(content)
        
        return SimpleUploadedFile(
            filename,
            content.encode('utf-8'),
            content_type=content_type
        )


class DatasetTestHelper:
    """数据集测试辅助类"""
    
    @staticmethod
    def create_test_dataset_file(content=None, file_format="json", filename=None):
        """创建测试数据集文件"""
        
        if filename is None:
            filename = f"test_dataset.{file_format}"
        
        if content is None:
            if file_format == "json":
                content = [
                    {"id": 1, "input": "测试问题1", "reference": "测试答案1"},
                    {"id": 2, "input": "测试问题2", "reference": "测试答案2"}
                ]
            elif file_format == "csv":
                content = "id,input,reference\n1,测试问题1,测试答案1\n2,测试问题2,测试答案2"
            elif file_format == "zip":
                # 创建包含JSON文件的ZIP
                temp_file = BytesIO()
                with zipfile.ZipFile(temp_file, 'w') as zf:
                    json_content = json.dumps([
                        {"id": 1, "input": "测试问题1", "reference": "测试答案1"},
                        {"id": 2, "input": "测试问题2", "reference": "测试答案2"}
                    ], ensure_ascii=False)
                    zf.writestr('data.json', json_content)
                temp_file.seek(0)
                return SimpleUploadedFile(
                    filename,
                    temp_file.read(),
                    content_type="application/zip"
                )
        
        if isinstance(content, (list, dict)):
            content = json.dumps(content, ensure_ascii=False)
        
        return SimpleUploadedFile(
            filename,
            content.encode('utf-8') if isinstance(content, str) else content,
            content_type={
                "json": "application/json",
                "csv": "text/csv",
                "zip": "application/zip"
            }.get(file_format, "application/octet-stream")
        )
    
    @staticmethod
    def create_test_image_dataset_file():
        """创建测试图片数据集文件"""
        
        temp_file = BytesIO()
        with zipfile.ZipFile(temp_file, 'w') as zf:
            # 添加JSON数据文件
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
            zf.writestr('image1.jpg', b'fake image data 1')
            zf.writestr('image2.jpg', b'fake image data 2')
        
        temp_file.seek(0)
        return SimpleUploadedFile(
            "image_dataset.zip",
            temp_file.read(),
            content_type="application/zip"
        )


class TaskTestHelper:
    """任务测试辅助类"""
    
    @staticmethod
    def create_adversarial_task_data():
        """创建对抗评测任务数据"""
        return {
            "name": "对抗评测任务",
            "description": "测试对抗评测功能",
            "method": "adversarial",
            "judge_type": "human",
            "dataset": None,  # 需要在测试中设置
            "myModel": None,   # 需要在测试中设置
            "myModel_2": None  # 需要在测试中设置
        }
    
    @staticmethod
    def create_objective_task_data():
        """创建客观评测任务数据"""
        return {
            "name": "客观评测任务",
            "description": "测试客观评测功能",
            "method": "objective",
            "dataset": None,  # 需要在测试中设置
            "myModel": None    # 需要在测试中设置
        }
    
    @staticmethod
    def create_subjective_task_data():
        """创建主观评测任务数据"""
        return {
            "name": "主观评测任务",
            "description": "测试主观评测功能",
            "method": "subjective",
            "judge_type": "human",
            "dataset": None,  # 需要在测试中设置
            "myModel": None    # 需要在测试中设置
        }