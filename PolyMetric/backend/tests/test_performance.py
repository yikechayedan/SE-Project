"""
API性能测试
测试各个API的性能和负载能力
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from tests.factories import TestDataGenerator
import time
import threading
import concurrent.futures
from unittest.mock import patch, MagicMock

User = get_user_model()


class APIPerformanceTest(TestCase):
    """API性能测试基类"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.admin = TestDataGenerator.create_admin_user()
        
        # 创建大量测试数据
        self.models = [
            TestDataGenerator.create_model(name=f"性能测试模型{i}")
            for i in range(50)
        ]
        
        self.datasets = [
            TestDataGenerator.create_dataset(name=f"性能测试数据集{i}")
            for i in range(30)
        ]
        
        self.tasks = []
        for i in range(20):
            task = TestDataGenerator.create_task(
                name=f"性能测试任务{i}",
                dataset=self.datasets[i % len(self.datasets)],
                model=self.models[i % len(self.models)]
            )
            self.tasks.append(task)
    
    def measure_response_time(self, url, method='GET', data=None, expected_status=200):
        """测量API响应时间"""
        start_time = time.time()
        
        if method == 'GET':
            response = self.client.get(url)
        elif method == 'POST':
            response = self.client.post(url, data, format='json')
        elif method == 'PUT':
            response = self.client.put(url, data, format='json')
        elif method == 'DELETE':
            response = self.client.delete(url)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, expected_status)
        return response_time
    
    def test_models_api_performance(self):
        """测试模型API性能"""
        # 1. 模型列表性能
        response_time = self.measure_response_time("/api/models/")
        self.assertLess(response_time, 1.0, f"模型列表API响应时间过长: {response_time}s")
        
        # 2. 模型详情性能
        model_id = self.models[0].id
        response_time = self.measure_response_time(f"/api/models/{model_id}/")
        self.assertLess(response_time, 0.5, f"模型详情API响应时间过长: {response_time}s")
        
        # 3. 模型统计性能
        response_time = self.measure_response_time("/api/models/stats/")
        self.assertLess(response_time, 1.0, f"模型统计API响应时间过长: {response_time}s")
        
        # 4. 模型搜索性能
        response_time = self.measure_response_time("/api/models/?search=性能测试")
        self.assertLess(response_time, 1.0, f"模型搜索API响应时间过长: {response_time}s")
    
    def test_datasets_api_performance(self):
        """测试数据集API性能"""
        # 1. 数据集列表性能
        response_time = self.measure_response_time("/api/datasets/")
        self.assertLess(response_time, 1.0, f"数据集列表API响应时间过长: {response_time}s")
        
        # 2. 数据集详情性能
        dataset_id = self.datasets[0].id
        response_time = self.measure_response_time(f"/api/datasets/{dataset_id}/")
        self.assertLess(response_time, 0.5, f"数据集详情API响应时间过长: {response_time}s")
        
        # 3. 数据集搜索性能
        response_time = self.measure_response_time("/api/datasets/?search=性能测试")
        self.assertLess(response_time, 1.0, f"数据集搜索API响应时间过长: {response_time}s")
    
    def test_tasks_api_performance(self):
        """测试任务API性能"""
        self.client.force_authenticate(user=self.user)
        
        # 1. 任务列表性能
        response_time = self.measure_response_time("/api/tasks/")
        self.assertLess(response_time, 1.0, f"任务列表API响应时间过长: {response_time}s")
        
        # 2. 任务详情性能
        task_id = self.tasks[0].id
        response_time = self.measure_response_time(f"/api/tasks/{task_id}/")
        self.assertLess(response_time, 0.5, f"任务详情API响应时间过长: {response_time}s")
        
        # 3. 任务项性能
        response_time = self.measure_response_time(f"/api/tasks/{task_id}/pending-items/")
        self.assertLess(response_time, 1.0, f"任务项API响应时间过长: {response_time}s")
    
    def test_rankings_api_performance(self):
        """测试排名API性能"""
        # 1. 排行榜性能
        response_time = self.measure_response_time("/api/rankings/leaderboard/")
        self.assertLess(response_time, 1.5, f"排行榜API响应时间过长: {response_time}s")
        
        # 2. 顶级模型性能
        dataset_id = self.datasets[0].id
        response_time = self.measure_response_time(f"/api/rankings/top/?dataset_id={dataset_id}")
        self.assertLess(response_time, 1.0, f"顶级模型API响应时间过长: {response_time}s")
        
        # 3. 模型排名历史性能
        model_id = self.models[0].id
        response_time = self.measure_response_time(f"/api/rankings/history/{model_id}/")
        self.assertLess(response_time, 1.0, f"排名历史API响应时间过长: {response_time}s")
    
    def test_system_api_performance(self):
        """测试系统API性能"""
        # 1. 新闻流性能
        response_time = self.measure_response_time("/api/system/news/")
        self.assertLess(response_time, 1.0, f"新闻流API响应时间过长: {response_time}s")
    
    def test_comments_api_performance(self):
        """测试评论API性能"""
        # 1. 评论列表性能
        model_id = self.models[0].id
        response_time = self.measure_response_time(f"/api/comments/?target_type=model&target_id={model_id}")
        self.assertLess(response_time, 1.0, f"评论列表API响应时间过长: {response_time}s")


class APILoadTest(TestCase):
    """API负载测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.users = [
            TestDataGenerator.create_user(username=f"负载测试用户{i}")
            for i in range(10)
        ]
        
        # 创建测试数据
        self.models = [
            TestDataGenerator.create_model(name=f"负载测试模型{i}")
            for i in range(20)
        ]
        
        self.datasets = [
            TestDataGenerator.create_dataset(name=f"负载测试数据集{i}")
            for i in range(10)
        ]
    
    def make_concurrent_requests(self, url, num_requests=10, method='GET', data=None):
        """并发请求测试"""
        results = []
        
        def make_request():
            start_time = time.time()
            if method == 'GET':
                response = self.client.get(url)
            elif method == 'POST':
                response = self.client.post(url, data, format='json')
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            end_time = time.time()
            results.append({
                'status_code': response.status_code,
                'response_time': end_time - start_time
            })
        
        # 使用线程池进行并发请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            concurrent.futures.wait(futures)
        
        return results
    
    def test_models_api_load(self):
        """测试模型API负载"""
        # 1. 模型列表负载测试
        results = self.make_concurrent_requests("/api/models/", num_requests=20)
        
        # 验证所有请求都成功
        self.assertEqual(len(results), 20)
        success_count = sum(1 for r in results if r['status_code'] == 200)
        self.assertEqual(success_count, 20)
        
        # 验证平均响应时间
        avg_response_time = sum(r['response_time'] for r in results) / len(results)
        self.assertLess(avg_response_time, 2.0, f"模型列表API平均响应时间过长: {avg_response_time}s")
        
        # 验证最大响应时间
        max_response_time = max(r['response_time'] for r in results)
        self.assertLess(max_response_time, 5.0, f"模型列表API最大响应时间过长: {max_response_time}s")
    
    def test_datasets_api_load(self):
        """测试数据集API负载"""
        # 1. 数据集列表负载测试
        results = self.make_concurrent_requests("/api/datasets/", num_requests=20)
        
        # 验证所有请求都成功
        self.assertEqual(len(results), 20)
        success_count = sum(1 for r in results if r['status_code'] == 200)
        self.assertEqual(success_count, 20)
        
        # 验证平均响应时间
        avg_response_time = sum(r['response_time'] for r in results) / len(results)
        self.assertLess(avg_response_time, 2.0, f"数据集列表API平均响应时间过长: {avg_response_time}s")
    
    def test_system_api_load(self):
        """测试系统API负载"""
        # 1. 新闻流负载测试
        results = self.make_concurrent_requests("/api/system/news/", num_requests=30)
        
        # 验证所有请求都成功
        self.assertEqual(len(results), 30)
        success_count = sum(1 for r in results if r['status_code'] == 200)
        self.assertEqual(success_count, 30)
        
        # 验证平均响应时间
        avg_response_time = sum(r['response_time'] for r in results) / len(results)
        self.assertLess(avg_response_time, 2.0, f"新闻流API平均响应时间过长: {avg_response_time}s")
    
    def test_rankings_api_load(self):
        """测试排名API负载"""
        # 1. 排行榜负载测试
        results = self.make_concurrent_requests("/api/rankings/leaderboard/", num_requests=15)
        
        # 验证所有请求都成功
        self.assertEqual(len(results), 15)
        success_count = sum(1 for r in results if r['status_code'] == 200)
        self.assertEqual(success_count, 15)
        
        # 验证平均响应时间
        avg_response_time = sum(r['response_time'] for r in results) / len(results)
        self.assertLess(avg_response_time, 3.0, f"排行榜API平均响应时间过长: {avg_response_time}s")


class APIStressTest(TestCase):
    """API压力测试"""
    
    def setUp(self):
        self.client = APIClient()
        
        # 创建大量测试数据
        self.models = [
            TestDataGenerator.create_model(name=f"压力测试模型{i}")
            for i in range(100)
        ]
        
        self.datasets = [
            TestDataGenerator.create_dataset(name=f"压力测试数据集{i}")
            for i in range(50)
        ]
    
    def test_sustained_load(self):
        """测试持续负载"""
        # 持续发送请求，模拟真实使用场景
        urls = [
            "/api/models/",
            "/api/datasets/",
            "/api/system/news/",
            "/api/rankings/leaderboard/"
        ]
        
        total_requests = 0
        failed_requests = 0
        total_response_time = 0
        
        # 持续测试30秒
        start_time = time.time()
        while time.time() - start_time < 30:
            for url in urls:
                request_start = time.time()
                response = self.client.get(url)
                request_end = time.time()
                
                total_requests += 1
                total_response_time += (request_end - request_start)
                
                if response.status_code != 200:
                    failed_requests += 1
        
        # 计算统计数据
        success_rate = (total_requests - failed_requests) / total_requests * 100
        avg_response_time = total_response_time / total_requests
        requests_per_second = total_requests / 30
        
        # 验证成功率
        self.assertGreaterEqual(success_rate, 95, f"API成功率过低: {success_rate}%")
        
        # 验证平均响应时间
        self.assertLess(avg_response_time, 2.0, f"API平均响应时间过长: {avg_response_time}s")
        
        # 验证吞吐量
        self.assertGreater(requests_per_second, 10, f"API吞吐量过低: {requests_per_second} req/s")
    
    def test_burst_load(self):
        """测试突发负载"""
        # 短时间内发送大量请求
        burst_size = 50
        url = "/api/models/"
        
        start_time = time.time()
        results = self.make_concurrent_requests(url, num_requests=burst_size)
        end_time = time.time()
        
        # 验证所有请求都成功
        success_count = sum(1 for r in results if r['status_code'] == 200)
        self.assertEqual(success_count, burst_size)
        
        # 验证总时间
        total_time = end_time - start_time
        self.assertLess(total_time, 10.0, f"突发负载处理时间过长: {total_time}s")
        
        # 验证最大响应时间
        max_response_time = max(r['response_time'] for r in results)
        self.assertLess(max_response_time, 5.0, f"突发负载下最大响应时间过长: {max_response_time}s")


class DatabasePerformanceTest(TestCase):
    """数据库性能测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.admin = TestDataGenerator.create_admin_user()
    
    def test_large_dataset_queries(self):
        """测试大数据集查询性能"""
        # 创建大量数据
        models = [
            TestDataGenerator.create_model(name=f"大数据集测试模型{i}")
            for i in range(200)
        ]
        
        datasets = [
            TestDataGenerator.create_dataset(name=f"大数据集测试数据集{i}")
            for i in range(100)
        ]
        
        # 测试复杂查询性能
        start_time = time.time()
        response = self.client.get("/api/models/?search=大数据集测试&limit=50")
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 2.0, "大数据集查询性能过差")
        
        # 测试分页查询性能
        start_time = time.time()
        response = self.client.get("/api/datasets/?page=1&page_size=20")
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 1.5, "分页查询性能过差")
    
    def test_concurrent_database_operations(self):
        """测试并发数据库操作"""
        self.client.force_authenticate(user=self.user)
        
        # 并发创建数据
        def create_dataset(index):
            data = {
                "name": f"并发测试数据集{index}",
                "description": "并发测试描述",
                "category": "text"
            }
            response = self.client.post("/api/datasets/", data, format="json")
            return response.status_code == 201
        
        # 使用线程池进行并发操作
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_dataset, i) for i in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 验证大部分操作成功
        success_count = sum(results)
        self.assertGreaterEqual(success_count, 18, "并发数据库操作失败率过高")


class CachePerformanceTest(TestCase):
    """缓存性能测试"""
    
    def setUp(self):
        self.client = APIClient()
        
        # 创建测试数据
        self.models = [
            TestDataGenerator.create_model(name=f"缓存测试模型{i}")
            for i in range(10)
        ]
    
    @patch('django.core.cache.cache.get')
    @patch('django.core.cache.cache.set')
    def test_cache_hit_performance(self, mock_cache_set, mock_cache_get):
        """测试缓存命中性能"""
        # 模拟缓存命中
        mock_cache_get.return_value = "cached_data"
        
        # 第一次请求（缓存未命中）
        start_time = time.time()
        response = self.client.get("/api/models/")
        first_request_time = time.time() - start_time
        
        # 第二次请求（缓存命中）
        start_time = time.time()
        response = self.client.get("/api/models/")
        second_request_time = time.time() - start_time
        
        # 验证缓存命中的性能提升
        self.assertEqual(response.status_code, 200)
        self.assertLess(second_request_time, first_request_time, "缓存未提供性能提升")
    
    def test_cache_invalidation_performance(self):
        """测试缓存失效性能"""
        # 这个测试需要根据实际的缓存实现来调整
        # 这里只是一个示例框架
        
        # 测试缓存失效操作的性能
        start_time = time.time()
        
        # 模拟缓存失效操作
        # 实际实现会根据具体的缓存策略而不同
        
        end_time = time.time()
        invalidation_time = end_time - start_time
        
        # 验证缓存失效时间合理
        self.assertLess(invalidation_time, 1.0, "缓存失效操作时间过长")