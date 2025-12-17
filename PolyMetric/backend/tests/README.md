# PolyMetric API 测试套件

这是一个全面的API测试套件，用于测试PolyMetric项目的所有API端点。

## 📋 目录结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # pytest配置和夹具
├── test_utils.py            # 测试工具函数和数据生成器
├── test_users_api.py       # 用户相关API测试
├── test_datasets_api.py     # 数据集相关API测试
├── test_models_api.py       # 模型相关API测试
├── test_tasks_api.py        # 任务相关API测试
├── test_rankings_api.py     # 排名相关API测试
├── test_system_api.py       # 系统相关API测试
├── test_integration.py      # 集成测试
└── README.md              # 本文档
```

## 🚀 快速开始

### 1. 环境准备

确保你已经安装了所有必要的依赖：

```bash
# 安装项目依赖
pip install -r requirements.txt

# 安装测试依赖
pip install pytest pytest-django coverage
```

### 2. 环境检查

运行测试前，检查环境是否正确配置：

```bash
python run_tests.py --check
```

### 3. 设置测试环境

如果需要设置测试环境：

```bash
python run_tests.py --setup
```

## 🧪 运行测试

### 使用简化测试运行器（推荐）

```bash
# 运行所有已通过的测试
python run_passed_tests.py

# 运行特定模块的测试
python run_passed_tests.py users      # 运行用户API测试
python run_passed_tests.py datasets    # 运行数据集API测试
python run_passed_tests.py models      # 运行模型API测试
python run_passed_tests.py tasks       # 运行任务API测试

# 或者使用批处理文件（Windows）
run_passed_tests.bat                  # 运行所有已通过的测试
run_passed_tests.bat users            # 运行用户API测试
run_passed_tests.bat datasets          # 运行数据集API测试
run_passed_tests.bat models            # 运行模型API测试
run_passed_tests.bat tasks             # 运行任务API测试
```

### 使用自定义测试运行器

```bash
# 运行所有测试
python run_tests.py

# 运行特定模块的测试
python run_tests.py --module test_users_api

# 运行特定测试类
python run_tests.py --module test_users_api --class UserRegistrationAPITest

# 运行特定测试方法
python run_tests.py --module test_users_api --class UserRegistrationAPITest --method test_user_registration_success

# 运行测试并生成覆盖率报告
python run_tests.py --coverage
```

### 使用Django内置测试运行器

```bash
# 运行所有测试
python manage.py test tests --settings=PolyMetric.test_settings

# 运行特定模块
python manage.py test tests.test_users_api --settings=PolyMetric.test_settings

# 运行特定测试类
python manage.py test tests.test_users_api.UserRegistrationAPITest --settings=PolyMetric.test_settings

# 运行特定测试方法
python manage.py test tests.test_users_api.UserRegistrationAPITest.test_user_registration_success --settings=PolyMetric.test_settings

# 运行已通过的测试
python manage.py test tests.test_users_api tests.test_datasets_api tests.test_models_api tests.test_tasks_api --settings=PolyMetric.test_settings --verbosity=2
```

### 使用pytest

```bash
# 运行所有测试
pytest

# 运行特定模块
pytest tests/test_users_api.py

# 运行特定测试类
pytest tests/test_users_api.py::UserRegistrationAPITest

# 运行特定测试方法
pytest tests/test_users_api.py::UserRegistrationAPITest::test_user_registration_success

# 使用标记运行测试
pytest -m api          # 只运行API测试
pytest -m integration   # 只运行集成测试
pytest -m "not slow"   # 排除慢速测试
```

### Windows用户

1. **运行所有测试**：双击运行 `run_passed_tests.bat` 文件
2. **运行特定测试**：
   - 在命令行中运行：`run_passed_tests.bat users`
   - 或者在命令行中运行：`python run_passed_tests.py users`

3. **可用模块**：
   - `users` - 用户API测试（28个测试）
   - `datasets` - 数据集API测试（33个测试）
   - `models` - 模型API测试（18个测试）
   - `tasks` - 任务API测试（22个测试）

注意：
- 如果遇到"Django settings not configured"错误，请使用 `run_passed_tests.bat` 或 `run_passed_tests.py`

## 📊 测试覆盖率

生成测试覆盖率报告：

```bash
# 使用自定义脚本
python run_tests.py --coverage

# 或使用coverage命令
coverage run --source='.' manage.py test tests
coverage report --show-missing
coverage html
```

覆盖率报告将生成在 `htmlcov/index.html`。

## 🏗️ 测试架构

### 测试工具类

1. **TestDataGenerator**: 生成测试数据
   - `create_user()`: 创建测试用户
   - `create_admin_user()`: 创建管理员用户
   - `create_model()`: 创建测试模型
   - `create_dataset()`: 创建测试数据集
   - `create_evaluation_task()`: 创建评测任务
   - `create_evaluation_item()`: 创建评测项

2. **AuthUtils**: 认证工具
   - `get_jwt_token()`: 获取JWT令牌
   - `get_auth_headers()`: 获取认证头

3. **APITestMixin**: API测试混入类
   - `assertAPIResponse()`: 断言API响应格式
   - `assertAPISuccess()`: 断言API成功响应
   - `assertAPIError()`: 断言API错误响应
   - `create_authenticated_client()`: 创建已认证的客户端

### 测试分类

1. **单元测试**: 测试单个功能点
2. **API测试**: 测试API端点的各种情况
3. **集成测试**: 测试模块间的交互
4. **性能测试**: 测试系统在负载下的表现

## 📝 测试覆盖的API

### 用户模块 (`/api/users/`)
- ✅ 用户注册
- ✅ 用户登录/登出
- ✅ 用户资料管理
- ✅ 密码修改/重置
- ✅ 用户关注/取消关注
- ✅ 隐私设置
- ✅ 头像上传
- ✅ 管理员功能

### 数据集模块 (`/api/datasets/`)
- ✅ 数据集CRUD操作
- ✅ 数据集上传/下载
- ✅ 数据集预览
- ✅ 数据集关注/取消关注
- ✅ 数据集审核
- ✅ 权限控制
- ✅ 分页和过滤

### 模型模块 (`/api/models/`)
- ✅ 模型列表/详情
- ✅ 模型关注/取消关注
- ✅ 关注列表查询
- ✅ 隐私设置
- ✅ 模型过滤和搜索

### 任务模块 (`/api/tasks/`)
- ✅ 评测任务CRUD操作
- ✅ 任务执行
- ✅ 评分提交
- ✅ 待评测项查询
- ✅ 基准测试
- ✅ 权限控制

### 排名模块 (`/api/rankings/`)
- ✅ 排名更新
- ✅ 顶级模型查询
- ✅ 排名历史查询
- ✅ 管理员权限

### 系统模块 (`/api/system/`)
- ✅ 新闻流API
- ✅ 系统事件
- ✅ 信号处理
- ✅ 事件记录

## 🔧 自定义测试

### 添加新测试

1. 在相应的测试文件中添加新的测试方法
2. 使用 `TestDataGenerator` 创建测试数据
3. 使用 `APITestMixin` 的断言方法
4. 遵循命名规范: `test_<功能>_<场景>`

### 示例测试

```python
from tests.test_utils import TestDataGenerator, APITestMixin

class MyAPITest(TestCase, APITestMixin):
    def setUp(self):
        self.client = APIClient()
        self.user = TestDataGenerator.create_user()
        self.create_authenticated_client(self.user)
    
    def test_my_api_success(self):
        """测试我的API成功场景"""
        response = self.client.get("/api/my-endpoint/")
        self.assertAPISuccess(response, 200)
        self.assertEqual(response.data["data"]["field"], "expected_value")
```

## 🐛 调试测试

### 调试失败的测试

1. 查看详细的错误信息：
   ```bash
   python manage.py test tests.test_users_api --verbosity=2
   ```

2. 使用pdb调试：
   ```python
   import pdb; pdb.set_trace()
   ```

3. 打印响应内容：
   ```python
   print(response.data)
   print(response.status_code)
   ```

### 常见问题

1. **Django settings not configured**：
   - 使用 `run_passed_tests.bat` 或 `run_passed_tests.py`
   - 或者手动设置环境变量：`set DJANGO_SETTINGS_MODULE=PolyMetric.test_settings`
   - 确保在 `PolyMetric/backend` 目录中运行测试

2. **数据库错误**: 确保运行了迁移
   ```bash
   python manage.py migrate --settings=PolyMetric.test_settings
   ```

3. **认证错误**: 确保正确设置了JWT令牌
   ```python
   self.create_authenticated_client(self.user)
   ```

4. **文件上传错误**: 确保使用了正确的文件格式
   ```python
   SimpleUploadedFile("test.json", content, content_type="application/json")
   ```

5. **中文乱码**：
   - 使用 `run_passed_tests.bat` 或 `run_passed_tests.py`

## 📈 最佳实践

1. **测试命名**: 使用描述性的测试方法名
2. **测试隔离**: 每个测试应该独立运行
3. **数据清理**: 使用 `setUp` 和 `tearDown` 方法
4. **断言清晰**: 使用具体的断言而不是通用的
5. **测试覆盖**: 确保测试正常和异常情况
6. **性能考虑**: 避免在测试中使用大量数据

## 🤝 贡献指南

1. 为新功能添加相应的测试
2. 确保所有测试通过
3. 保持测试覆盖率在80%以上
4. 为复杂测试添加文档注释
5. 遵循现有的代码风格

## 📞 支持

如果遇到问题，请：

1. 检查本文档的常见问题部分
2. 查看测试输出中的错误信息
3. 确保环境正确配置
4. 联系开发团队

---

**注意**: 这个测试套件是持续更新的，以匹配API的最新变化。请定期更新测试代码以保持同步。