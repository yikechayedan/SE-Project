"""
pytest配置文件 - 提供测试夹具和配置
"""
import pytest
import tempfile
import os
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from tests.test_utils import TestDataGenerator, AuthUtils

User = get_user_model()


@pytest.fixture
def api_client():
    """提供API客户端夹具"""
    return APIClient()


@pytest.fixture
def test_user():
    """提供测试用户夹具"""
    return TestDataGenerator.create_user()


@pytest.fixture
def admin_user():
    """提供管理员用户夹具"""
    return TestDataGenerator.create_admin_user()


@pytest.fixture
def authenticated_client(api_client, test_user):
    """提供已认证的客户端夹具"""
    tokens = AuthUtils.get_jwt_token(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """提供管理员认证的客户端夹具"""
    tokens = AuthUtils.get_jwt_token(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    return api_client


@pytest.fixture
def test_model():
    """提供测试模型夹具"""
    return TestDataGenerator.create_model()


@pytest.fixture
def test_dataset(test_user):
    """提供测试数据集夹具"""
    return TestDataGenerator.create_dataset(creator=test_user)


@pytest.fixture
def test_evaluation_task(test_user, test_model, test_dataset):
    """提供测试评测任务夹具"""
    return TestDataGenerator.create_evaluation_task(
        creator=test_user,
        model=test_model,
        dataset=test_dataset
    )


@pytest.fixture
def temp_file():
    """提供临时文件夹具"""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        f.write(b'{"test": "data"}')
        temp_path = f.name
    
    yield temp_path
    
    # 清理
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture(scope="session")
def django_db_setup():
    """设置测试数据库"""
    # 这里可以添加全局数据库设置
    pass


# 标记定义
pytest_plugins = []

# 自定义标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )


# 测试收集钩子
def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    for item in items:
        # 为API测试添加标记
        if "test_" in item.nodeid and any(x in item.nodeid for x in ["_api", "APITest"]):
            item.add_marker(pytest.mark.api)
        
        # 为集成测试添加标记
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # 为单元测试添加标记
        if not any(x in item.nodeid for x in ["integration", "api"]):
            item.add_marker(pytest.mark.unit)