# SQLite 测试使用指南

## 概述

由于原测试配置需要PostgreSQL服务器，而开发环境中PostgreSQL服务器可能没有运行，我们创建了使用SQLite数据库的测试脚本。这些脚本可以在不需要外部数据库服务器的情况下运行测试。

## 文件说明

### 1. `run_tests_sqlite.py`
基本的SQLite测试运行脚本，支持命令行参数。

### 2. `run_tests_sqlite.bat`
Windows批处理文件，用于快速运行SQLite测试。

### 3. `run_interactive_sqlite_tests.py`
交互式测试运行器，提供菜单选择不同的测试类型。

### 4. `run_interactive_sqlite_tests.bat`
Windows批处理文件，用于启动交互式测试运行器。

## 使用方法

### 方法1：使用命令行脚本

```bash
# 运行所有测试
python run_tests_sqlite.py

# 运行快速测试
python run_tests_sqlite.py --quick

# 运行特定测试
python run_tests_sqlite.py tests.test_users_api

# 运行单元测试
python run_tests_sqlite.py --unit

# 运行API测试
python run_tests_sqlite.py --api

# 运行集成测试
python run_tests_sqlite.py --integration

# 运行特定应用的测试
python run_tests_sqlite.py --app users

# 查看帮助
python run_tests_sqlite.py --help
```

### 方法2：使用批处理文件（Windows）

```bash
# 基本测试运行器
run_tests_sqlite.bat

# 交互式测试运行器
run_interactive_sqlite_tests.bat
```

### 方法3：使用交互式测试运行器

运行 `run_interactive_sqlite_tests.py` 或 `run_interactive_sqlite_tests.bat`，然后按照菜单提示选择：

1. **快速测试（推荐）** - 运行单元测试、API测试和集成测试
2. **单元测试** - 运行基础工具测试
3. **API测试** - 运行所有API接口测试
4. **集成测试** - 运行系统集成测试
5. **性能测试** - 运行性能相关测试
6. **应用测试** - 运行特定应用的测试
7. **所有测试** - 运行项目中所有测试
8. **覆盖率测试** - 生成测试覆盖率报告
9. **运行特定测试** - 运行指定的测试用例
0. **退出** - 退出测试运行器

## 测试配置

SQLite测试使用 `PolyMetric/test_settings.py` 配置文件，主要特点：

- 使用SQLite内存数据库，无需外部数据库服务器
- 禁用邮件功能，使用控制台输出
- 禁用Celery任务队列，使用同步执行
- 简化中间件配置
- 使用内存缓存提高性能

## 常见问题

### 1. 测试找不到

如果提示 "Found 0 test(s)"，请检查：
- 测试文件名是否正确
- 测试类是否继承自 `django.test.TestCase`
- 测试方法名是否以 `test_` 开头

### 2. 数据库错误

如果遇到数据库相关错误，确保：
- 使用了正确的测试配置文件
- 没有其他进程在使用测试数据库文件
- 有足够的磁盘空间

### 3. 导入错误

如果遇到模块导入错误，检查：
- 是否在正确的目录下运行脚本
- Python路径是否包含项目根目录
- 虚拟环境是否正确激活

## 示例输出

```
========================================
PolyMetric Backend SQLite Test Runner
========================================
使用SQLite数据库运行测试...

请选择测试类型:
1. 快速测试（推荐）
2. 单元测试
3. API测试
4. 集成测试
5. 性能测试
6. 应用测试
7. 所有测试
8. 覆盖率测试
9. 运行特定测试
0. 退出

请输入选择 (0-9): 1

================================================================================
运行: 单元测试
命令: python manage.py test tests.test_utils tests.base tests.conftest
================================================================================
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Found 38 test(s).
...
----------------------------------------------------------------------
Ran 38 tests in 26.093s

OK (skipped=6)
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...

[SUCCESS] 单元测试 成功完成
```

## 性能优化

1. **使用内存数据库** - 测试使用SQLite内存数据库，大大提高测试速度
2. **并行测试** - 可以使用 `--parallel` 参数并行运行测试
3. **保持数据库** - 使用 `--keepdb` 参数避免重复创建数据库
4. **快速失败** - 使用 `--failfast` 参数在第一个失败时停止

## 与原测试的对比

| 特性 | 原测试（PostgreSQL） | SQLite测试 |
|------|---------------------|------------|
| 数据库要求 | 需要PostgreSQL服务器 | 无需外部服务器 |
| 设置复杂度 | 需要配置数据库连接 | 开箱即用 |
| 测试速度 | 较慢（网络I/O） | 快速（内存数据库） |
| 适用场景 | 生产环境测试 | 开发和CI/CD |
| 数据一致性 | 与生产环境一致 | 可能有细微差异 |

## 建议

1. **开发阶段** - 使用SQLite测试，快速验证功能
2. **CI/CD** - 使用SQLite测试，提高构建速度
3. **预发布** - 使用PostgreSQL测试，确保与生产环境一致
4. **性能测试** - 使用PostgreSQL测试，获得真实的性能数据

## 相关文件

- `PolyMetric/test_settings.py` - 测试配置文件
- `tests/` - 测试文件目录
- `run_tests_sqlite.py` - SQLite测试运行脚本
- `run_interactive_sqlite_tests.py` - 交互式测试运行器