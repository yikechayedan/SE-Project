# PolyMetric API 测试指南和最佳实践

## 📋 目录

1. [测试架构概述](#测试架构概述)
2. [测试分类](#测试分类)
3. [测试环境设置](#测试环境设置)
4. [编写测试的最佳实践](#编写测试的最佳实践)
5. [测试数据管理](#测试数据管理)
6. [性能测试指南](#性能测试指南)
7. [API契约测试](#api契约测试)
8. [端到端测试](#端到端测试)
9. [测试报告和监控](#测试报告和监控)
10. [持续集成](#持续集成)
11. [常见问题](#常见问题)

## 🏗️ 测试架构概述

PolyMetric的测试系统采用业界标准的分层架构：

```
tests/
├── base.py              # 测试基类和工具
├── factories.py          # 测试数据工厂
├── test_monitoring.py   # 测试监控和报告
├── test_contracts.py     # API契约测试
├── test_performance.py  # 性能和负载测试
├── test_e2e.py         # 端到端测试
├── test_*.py           # 各模块API测试
└── contracts/          # API契约文件
```

### 核心组件

1. **BaseAPITestCase**: 提供标准化的API测试功能
2. **BaseIntegrationTestCase**: 提供事务级别的集成测试
3. **BasePerformanceTestCase**: 提供性能测试工具
4. **BaseLoadTestCase**: 提供负载测试工具
5. **TestMonitor**: 测试监控和报告系统
6. **Factories**: 测试数据工厂模式

## 🏷️ 测试分类

### 1. 单元测试 (Unit Tests)
- **目的**: 测试单个功能点
- **特点**: 快速、隔离、可重复
- **示例**: 测试用户注册逻辑、数据验证等

```python
class UserRegistrationTest(BaseAPITestCase):
    def test_user_registration_success(self):
        """测试用户注册成功"""
        data = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "test123456"
        }
        response = self.client.post("/api/users/register/", data, format="json")
        self.assertAPISuccess(response, 201)
```

### 2. 集成测试 (Integration Tests)
- **目的**: 测试模块间的交互
- **特点**: 测试真实数据库交互
- **示例**: 测试用户创建数据集后的系统事件

```python
class UserDatasetIntegrationTest(BaseIntegrationTestCase):
    def test_user_dataset_workflow(self):
        """测试用户-数据集完整工作流程"""
        # 测试用户创建数据集的完整流程
```

### 3. 性能测试 (Performance Tests)
- **目的**: 测试API响应时间和资源使用
- **特点**: 监控性能指标
- **示例**: 测试API响应时间、内存使用

```python
class UserAPIPerformanceTest(BasePerformanceTestCase):
    def test_user_registration_performance(self):
        """测试用户注册性能"""
        def register_user():
            # 注册逻辑
            pass
        
        for _ in range(10):
            response = self.measure_performance(register_user)
            self.assertEqual(response.status_code, 201)
        
        self.assertPerformanceThreshold(max_execution_time=0.5)
```

### 4. 负载测试 (Load Tests)
- **目的**: 测试系统在负载下的表现
- **特点**: 并发请求测试
- **示例**: 测试API并发处理能力

```python
class UserAPILoadTest(BaseLoadTestCase):
    def test_user_registration_load(self):
        """测试用户注册负载"""
        results = self.run_concurrent_requests(
            "/api/users/register/",
            method="POST",
            num_requests=20
        )
        self.assertLoadPerformance(min_success_rate=0.90)
```

### 5. 端到端测试 (E2E Tests)
- **目的**: 测试完整的业务流程
- **特点**: 模拟真实用户场景
- **示例**: 测试用户从注册到创建评测任务的完整流程

### 6. 契约测试 (Contract Tests)
- **目的**: 验证API响应格式一致性
- **特点**: 确保API契约不变
- **示例**: 验证API响应结构

## 🛠️ 测试环境设置

### 本地开发环境

1. **安装依赖**:
```bash
pip install -r requirements.txt
pip install pytest pytest-django pytest-cov pytest-mock pytest-xdist
pip install factory-boy matplotlib pandas
```

2. **环境变量**:
```bash
export DJANGO_SETTINGS_MODULE=PolyMetric.test_settings
export DATABASE_URL=postgres://user:password@localhost:5432/polymetric_test
export REDIS_URL=redis://localhost:6379/0
```

3. **数据库设置**:
```bash
python manage.py migrate --settings=PolyMetric.test_settings
```

### 运行测试

1. **使用高级测试运行器**:
```bash
# 运行所有测试
python run_advanced_tests.py

# 运行特定类别
python run_advanced_tests.py --categories unit integration

# 运行带覆盖率的测试
python run_advanced_tests.py --coverage

# 并行运行测试
python run_advanced_tests.py --parallel

# 运行性能测试
python run_advanced_tests.py --categories performance --benchmark
```

2. **使用pytest**:
```bash
# 运行所有测试
pytest

# 运行特定模块
pytest tests/test_users_api.py

# 运行特定测试类
pytest tests/test_users_api.py::UserRegistrationTest

# 运行特定测试方法
pytest tests/test_users_api.py::UserRegistrationTest::test_user_registration_success

# 使用标记运行测试
pytest -m unit          # 只运行单元测试
pytest -m integration   # 只运行集成测试
pytest -m "not slow"   # 排除慢速测试
```

## ✍️ 编写测试的最佳实践

### 1. 测试命名规范

```python
# 好的命名
def test_user_registration_with_valid_data_succeeds(self):
def test_user_registration_with_duplicate_email_fails(self):
def test_user_login_with_invalid_credentials_returns_error(self):

# 避免的命名
def test_user_1(self):
def test_registration(self):
def test_login(self):
```

### 2. 测试结构 (AAA模式)

```python
def test_user_registration_success(self):
    # Arrange (准备)
    user_data = {
        "username": "testuser",
        "email": "test@test.com",
        "password": "test123456"
    }
    
    # Act (执行)
    response = self.client.post("/api/users/register/", user_data, format="json")
    
    # Assert (断言)
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.data["username"], "testuser")
```

### 3. 测试隔离

```python
class UserAPITest(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        # 每个测试方法前执行
        self.user = UserFactory()
    
    def tearDown(self):
        # 每个测试方法后执行
        super().tearDown()
```

### 4. 使用工厂模式

```python
# 好的做法 - 使用工厂
def test_user_with_profile(self):
    user = UserFactory(bio="测试用户简介")
    self.assertEqual(user.bio, "测试用户简介")

# 避免的做法 - 手动创建
def test_user_with_profile(self):
    user = User.objects.create(
        username="testuser",
        email="test@test.com",
        bio="测试用户简介"
    )
```

### 5. 测试断言

```python
# 使用专门的断言方法
self.assertAPISuccess(response, 201)
self.assertAPIError(response, 400)
self.assertAPIPerformance(max_response_time=1.0)

# 避免通用断言
self.assertEqual(response.status_code, 201)
self.assertIn("data", response.data)
```

## 🏭 测试数据管理

### 1. 使用工厂模式

```python
from tests.factories import UserFactory, ModelFactory, DatasetFactory

# 创建单个对象
user = UserFactory()
model = ModelFactory(category="text")
dataset = DatasetFactory(is_public=True)

# 批量创建
users = UserFactory.create_batch(10)
models = ModelFactory.create_batch(5, category="image")

# 创建关联对象
task = EvaluationTaskFactory(
    creator=UserFactory(),
    model=ModelFactory(),
    dataset=DatasetFactory()
)
```

### 2. 使用场景工厂

```python
from tests.factories import ScenarioFactory

# 创建完整测试场景
scenario = ScenarioFactory.create_complete_scenario()

# 创建特定场景
user_scenario = ScenarioFactory.create_user_registration_scenario()
```

### 3. 测试数据清理

```python
class BaseTestCase(TestCase):
    def setUp(self):
        self.data_manager = TestDataManager()
    
    def tearDown(self):
        self.data_manager.cleanup()
```

## ⚡ 性能测试指南

### 1. 性能指标

- **响应时间**: API请求的处理时间
- **吞吐量**: 单位时间处理的请求数
- **资源使用**: CPU、内存、数据库连接等
- **并发能力**: 同时处理的请求数

### 2. 性能阈值

```python
# 设置合理的性能阈值
self.assertPerformanceThreshold(
    max_execution_time=1.0,    # 最大执行时间1秒
    max_memory_mb=100           # 最大内存使用100MB
)

# 负载测试阈值
self.assertLoadPerformance(
    min_success_rate=0.95,      # 最小成功率95%
    max_avg_response_time=2.0   # 最大平均响应时间2秒
)
```

### 3. 性能测试最佳实践

1. **基准测试**: 建立性能基线
2. **回归测试**: 检测性能退化
3. **压力测试**: 找出系统极限
4. **监控**: 持续监控性能指标

## 📋 API契约测试

### 1. 契约定义

```json
{
  "endpoint": "/api/users/register/",
  "method": "POST",
  "request": {
    "username": "string",
    "email": "string",
    "password": "string"
  },
  "response": {
    "code": 201,
    "msg": "string",
    "data": {
      "id": "integer",
      "username": "string",
      "email": "string"
    }
  }
}
```

### 2. 契约验证

```python
def test_user_registration_contract(self):
    """测试用户注册API契约"""
    response = self.client.post("/api/users/register/", data, format="json")
    
    expected_schema = {
        "code": int,
        "msg": str,
        "data": {
            "id": int,
            "username": str,
            "email": str
        }
    }
    
    self._validate_contract(response.data, expected_schema)
```

## 🔄 端到端测试

### 1. E2E测试场景

- **用户注册流程**: 注册 → 登录 → 完善资料
- **数据集管理**: 创建 → 上传 → 审核 → 发布
- **模型评测**: 创建任务 → 运行评测 → 查看结果
- **关注系统**: 关注用户/模型/数据集 → 查看关注列表

### 2. E2E测试最佳实践

1. **真实场景**: 模拟真实用户行为
2. **完整流程**: 覆盖业务全流程
3. **数据验证**: 验证最终状态
4. **错误处理**: 测试异常情况

## 📊 测试报告和监控

### 1. 测试监控

```python
from tests.test_monitoring import get_monitor, get_reporter

# 获取监控器
monitor = get_monitor()
monitor.start_test_session()

# 记录测试结果
monitor.record_test_result("test_name", "PASSED", 0.5)

# 生成报告
reporter = get_reporter()
html_report = reporter.generate_html_report()
```

### 2. 报告类型

- **HTML报告**: 可视化测试结果
- **JSON报告**: 机器可读的测试数据
- **性能图表**: 性能趋势分析
- **覆盖率报告**: 代码覆盖率统计

### 3. 警报系统

```python
# 检查警报条件
alerts = alert_system.check_alerts()

# 自动发送警报
if alerts:
    alert_system.send_alerts(alerts)
```

## 🚀 持续集成

### 1. GitHub Actions配置

项目已配置完整的CI/CD流程：

- **多Python版本测试**: 3.9, 3.10, 3.11
- **并行测试**: 加速测试执行
- **代码质量检查**: flake8, black, isort
- **安全扫描**: bandit, safety
- **覆盖率报告**: codecov集成
- **性能基准**: 自动性能回归检测

### 2. CI触发条件

- **Push到主分支**: 运行完整测试套件
- **Pull Request**: 运行相关测试
- **定时任务**: 每日完整测试
- **手动触发**: 按需运行特定测试

### 3. 测试报告

- **测试结果**: JUnit XML格式
- **覆盖率**: HTML和XML格式
- **性能数据**: JSON格式
- **安全报告**: 静态分析结果

## ❓ 常见问题

### 1. 测试环境问题

**问题**: Django settings not configured
```bash
# 解决方案
export DJANGO_SETTINGS_MODULE=PolyMetric.test_settings
# 或在测试文件中设置
import django
django.setup()
```

**问题**: 数据库连接失败
```bash
# 解决方案
python manage.py migrate --settings=PolyMetric.test_settings
```

### 2. 测试数据问题

**问题**: 唯一约束冲突
```python
# 解决方案 - 使用时间戳
username = f"testuser_{int(time.time())}"

# 或使用factory的Sequence
username = factory.Sequence(lambda n: f"testuser_{n}")
```

**问题**: 测试数据污染
```python
# 解决方案 - 使用事务测试
class MyTest(TransactionTestCase):
    # 自动回滚事务
    pass
```

### 3. 性能测试问题

**问题**: 性能测试不稳定
```python
# 解决方案 - 多次测试取平均值
for _ in range(5):
    response = self.measure_performance(func)
    self.assertEqual(response.status_code, 200)

self.assertPerformanceThreshold(max_execution_time=1.0)
```

### 4. 并发测试问题

**问题**: 数据库锁竞争
```python
# 解决方案 - 使用测试数据库
# 确保每个测试使用独立的数据库连接
```

## 📚 扩展阅读

- [Django测试文档](https://docs.djangoproject.com/en/stable/topics/testing/)
- [pytest文档](https://docs.pytest.org/)
- [Factory Boy文档](https://factoryboy.readthedocs.io/)
- [API契约测试最佳实践](https://martinfowler.com/articles/consumerDrivenContracts.html)

## 🤝 贡献指南

1. **新增测试**: 遵循现有测试模式
2. **测试覆盖率**: 保持80%以上覆盖率
3. **性能测试**: 为新API添加性能测试
4. **文档更新**: 更新测试文档
5. **代码审查**: 所有测试代码需要审查

---

**注意**: 这个测试系统是持续更新的，以匹配API的最新变化。请定期更新测试代码以保持同步。