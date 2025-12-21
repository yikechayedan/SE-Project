# PolyMetric API 测试使用说明

## 🚀 快速开始

### 环境准备

1. **安装依赖**:
```bash
pip install -r requirements.txt
```

2. **设置环境变量**:
```bash
# Windows
set DJANGO_SETTINGS_MODULE=PolyMetric.test_settings

# Linux/Mac
export DJANGO_SETTINGS_MODULE=PolyMetric.test_settings
```

3. **数据库迁移**:
```bash
python manage.py migrate --settings=PolyMetric.test_settings
```

## 🧪 运行测试

### 方法1: 使用高级测试运行器 (推荐)

```bash
# 运行所有测试
python run_advanced_tests.py

# 运行特定类别
python run_advanced_tests.py --categories unit integration

# 运行特定模块
python run_advanced_tests.py --modules tests.test_users_api tests.test_datasets_api

# 运行带覆盖率的测试
python run_advanced_tests.py --coverage --parallel

# 运行性能测试
python run_advanced_tests.py --categories performance --benchmark

# 健康检查
python run_advanced_tests.py --health

# 列出所有测试类别
python run_advanced_tests.py --list
```

### 方法2: 使用简化测试运行器

```bash
# 运行所有核心测试
python run_simple_tests.py
```

### 方法3: 使用Django内置测试运行器

```bash
# 运行所有测试
python manage.py test tests --settings=PolyMetric.test_settings --verbosity=2

# 运行特定模块
python manage.py test tests.test_users_api --settings=PolyMetric.test_settings --verbosity=2

# 运行特定测试类
python manage.py test tests.test_users_api.UserRegistrationAPITest --settings=PolyMetric.test_settings --verbosity=2

# 运行特定测试方法
python manage.py test tests.test_users_api.UserRegistrationAPITest.test_user_registration_success --settings=PolyMetric.test_settings --verbosity=2
```

### 方法4: 使用pytest

```bash
# 运行所有测试
pytest tests/ --settings=PolyMetric.test_settings

# 运行特定模块
pytest tests/test_users_api.py --settings=PolyMetric.test_settings

# 运行特定测试类
pytest tests/test_users_api.py::UserRegistrationAPITest --settings=PolyMetric.test_settings

# 运行特定测试方法
pytest tests/test_users_api.py::UserRegistrationAPITest::test_user_registration_success --settings=PolyMetric.test_settings

# 使用标记运行测试
pytest -m unit --settings=PolyMetric.test_settings          # 只运行单元测试
pytest -m integration --settings=PolyMetric.test_settings   # 只运行集成测试
pytest -m performance --settings=PolyMetric.test_settings  # 只运行性能测试
pytest -m "not slow" --settings=PolyMetric.test_settings # 排除慢速测试

# 并行运行测试
pytest -n auto --settings=PolyMetric.test_settings
```

## 📊 测试类别说明

### 1. 单元测试 (unit)
- **描述**: 测试单个功能点
- **模块**: 用户、数据集、模型、任务、排名、系统
- **命令**: `python run_advanced_tests.py --categories unit`
- **示例**: `pytest tests/test_users_api.py -m unit`

### 2. 集成测试 (integration)
- **描述**: 测试模块间交互
- **模块**: 跨模块交互测试
- **命令**: `python run_advanced_tests.py --categories integration`
- **示例**: `pytest tests/test_integration.py -m integration`

### 3. 性能测试 (performance)
- **描述**: 测试API响应时间和资源使用
- **模块**: 性能测试套件
- **命令**: `python run_advanced_tests.py --categories performance --benchmark`
- **示例**: `pytest tests/test_performance.py -m performance`

### 4. 端到端测试 (e2e)
- **描述**: 测试完整业务流程
- **模块**: E2E测试套件
- **命令**: `python run_advanced_tests.py --categories e2e`
- **示例**: `pytest tests/test_e2e.py -m e2e`

### 5. API契约测试 (contracts)
- **描述**: 验证API响应格式一致性
- **模块**: 契约测试套件
- **命令**: `python run_advanced_tests.py --categories contracts`
- **示例**: `pytest tests/test_contracts.py -m contracts`

## 🔧 高级测试选项

### 覆盖率测试

```bash
# 生成覆盖率报告
python run_advanced_tests.py --coverage

# 或使用pytest
pytest --cov=. --cov-report=html --cov-report=term-missing tests/ --settings=PolyMetric.test_settings
```

### 并行测试

```bash
# 使用所有CPU核心并行运行
pytest -n auto tests/ --settings=PolyMetric.test_settings

# 指定并行进程数
pytest -n 4 tests/ --settings=PolyMetric.test_settings
```

### 性能基准测试

```bash
# 运行性能基准测试
python run_advanced_tests.py --categories performance --benchmark

# 生成性能报告
pytest --benchmark-only --benchmark-json=benchmark.json tests/test_performance.py --settings=PolyMetric.test_settings
```

## 📋 测试报告

### 查看测试报告

测试完成后，报告会生成在 `test_reports/` 目录：

1. **HTML报告**: 可视化测试结果
   ```bash
   # 打开最新报告
   start test_reports/test_report_*.html
   ```

2. **JSON报告**: 机器可读的测试数据
   ```bash
   # 查看最新报告
   cat test_reports/test_report_*.json
   ```

3. **覆盖率报告**: 代码覆盖率统计
   ```bash
   # HTML格式
   start htmlcov/index.html
   
   # 终端格式
   coverage report --show-missing
   ```

## 🐛 常见问题解决

### 1. Django设置未配置

```bash
# 错误: Django settings not configured
# 解决方案:
set DJANGO_SETTINGS_MODULE=PolyMetric.test_settings
# 或在代码中设置
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.test_settings')
```

### 2. 数据库连接失败

```bash
# 错误: database connection failed
# 解决方案:
python manage.py migrate --settings=PolyMetric.test_settings
```

### 3. 模块导入错误

```bash
# 错误: ModuleNotFoundError: No module named 'xxx'
# 解决方案:
pip install -r requirements.txt
```

### 4. 测试数据冲突

```bash
# 错误: IntegrityError: UNIQUE constraint failed
# 解决方案: 测试中使用时间戳或随机数据
username = f"testuser_{int(time.time())}"
```

## 🔄 持续集成

### 本地开发测试

```bash
# 运行快速测试
python run_advanced_tests.py --categories unit --parallel

# 运行完整测试
python run_advanced_tests.py --coverage
```

### 提交前测试

```bash
# 运行所有测试确保没有回归
python run_advanced_tests.py

# 检查代码质量
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
black --check .
isort --check-only .
```

## 📚 测试最佳实践

### 1. 编写测试

```python
# 使用描述性的测试方法名
def test_user_registration_with_valid_data_succeeds(self):
    """测试用户注册成功场景"""
    pass

# 使用AAA模式 (Arrange, Act, Assert)
def test_user_registration(self):
    # Arrange - 准备测试数据
    user_data = {"username": "test", "email": "test@test.com"}
    
    # Act - 执行操作
    response = self.client.post("/api/users/register/", user_data)
    
    # Assert - 验证结果
    self.assertEqual(response.status_code, 201)
```

### 2. 使用测试工厂

```python
# 使用工厂创建测试数据
from tests.factories import UserFactory, ModelFactory

def test_user_workflow(self):
    user = UserFactory()
    model = ModelFactory()
    # 测试逻辑
```

### 3. 测试隔离

```python
# 每个测试应该独立运行
class MyTest(TestCase):
    def setUp(self):
        # 每个测试前执行
        pass
    
    def tearDown(self):
        # 每个测试后执行
        pass
```

## 🔍 调试测试

### 1. 详细输出

```bash
# 使用详细模式运行测试
python manage.py test tests.test_users_api --settings=PolyMetric.test_settings --verbosity=2

# 或使用pytest
pytest tests/test_users_api.py -v -s --settings=PolyMetric.test_settings
```

### 2. 调试模式

```python
# 在测试中添加断点
import pdb; pdb.set_trace()

# 或使用print调试
print(f"Response data: {response.data}")
print(f"Response status: {response.status_code}")
```

### 3. 数据库调试

```python
# 检查数据库状态
from apps.users.models import User
print(f"User count: {User.objects.count()}")

# 检查特定对象
user = User.objects.first()
print(f"User data: {user.__dict__}")
```

## 📊 性能测试

### 1. 运行性能测试

```bash
# 运行性能测试
python run_advanced_tests.py --categories performance

# 生成性能报告
pytest --benchmark-only tests/test_performance.py --settings=PolyMetric.test_settings
```

### 2. 性能阈值

- **API响应时间**: < 1秒 (简单操作), < 2秒 (复杂操作)
- **数据库查询**: < 100ms (简单查询), < 500ms (复杂查询)
- **内存使用**: < 100MB (普通测试)

## 🚨 故障排除

### 1. 测试失败

```bash
# 只运行失败的测试
pytest --lf --settings=PolyMetric.test_settings

# 运行上次失败的测试
pytest --lf --settings=PolyMetric.test_settings
```

### 2. 特定测试

```bash
# 运行特定测试文件
python manage.py test tests.test_users_api.UserRegistrationAPITest --settings=PolyMetric.test_settings

# 运行特定测试方法
python manage.py test tests.test_users_api.UserRegistrationAPITest.test_user_registration_success --settings=PolyMetric.test_settings
```

### 3. 测试数据库

```bash
# 重置测试数据库
python manage.py flush --settings=PolyMetric.test_settings --noinput

# 创建测试数据
python manage.py loaddata test_models_data.json --settings=PolyMetric.test_settings
```

## 📞 获取帮助

### 查看帮助信息

```bash
# 查看高级测试运行器帮助
python run_advanced_tests.py --help

# 查看pytest帮助
pytest --help

# 查看Django测试帮助
python manage.py test --help
```

### 查看可用测试

```bash
# 列出所有测试类别
python run_advanced_tests.py --list

# 列出特定模块的测试
pytest --collect-only tests/test_users_api.py --settings=PolyMetric.test_settings
```

---

## 📞 联系支持

如果遇到问题，请：

1. 查看测试文档: [`TESTING_GUIDELINES.md`](TESTING_GUIDELINES.md)
2. 检查测试报告: `test_reports/` 目录
3. 查看已知问题: [`test_reports/complete_test_report.md`](test_reports/complete_test_report.md)
4. 运行健康检查: `python run_advanced_tests.py --health`

**记住**: 好的测试是高质量代码的保证！