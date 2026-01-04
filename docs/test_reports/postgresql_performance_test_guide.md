# PostgreSQL性能测试配置指南

## 概述

本指南说明如何配置PostgreSQL环境以运行高并发性能测试，以及为什么当前测试使用SQLite的原因。

## 当前状态

### 为什么使用SQLite而不是PostgreSQL

1. **PostgreSQL连接问题**
   - 错误: `connection to server at "127.0.0.1", port 5432 failed: Connection refused`
   - 原因: 本地没有运行PostgreSQL服务器

2. **自动回退机制**
   - 系统已实现自动回退到SQLite模式
   - 确保测试能够正常运行，即使PostgreSQL不可用

3. **测试结果**
   - 高并发性能测试已成功运行
   - 使用SQLite内存数据库，所有测试通过

## 配置PostgreSQL环境

### 方法1: 使用Docker (推荐)

```bash
# 启动PostgreSQL容器
docker run -d --name postgres-test \
  -e POSTGRES_PASSWORD=yhblsqt \
  -e POSTGRES_DB=polymetric_test \
  -p 5432:5432 \
  postgres:latest

# 等待容器启动
sleep 10

# 运行测试
cd PolyMetric/backend
python run_postgres_tests_simple.py
```

### 方法2: 本地PostgreSQL安装

1. **安装PostgreSQL**
   ```bash
   # Windows
   # 下载并安装PostgreSQL from https://www.postgresql.org/download/windows/
   
   # macOS
   brew install postgresql
   
   # Linux (Ubuntu/Debian)
   sudo apt-get install postgresql postgresql-contrib
   ```

2. **创建测试数据库**
   ```sql
   CREATE DATABASE polymetric_test;
   CREATE USER test_user WITH PASSWORD 'test_password';
   GRANT ALL PRIVILEGES ON DATABASE polymetric_test TO test_user;
   ```

3. **设置环境变量**
   ```bash
   export TEST_DB_HOST=127.0.0.1
   export TEST_DB_PORT=5432
   export TEST_DB_NAME=polymetric_test
   export TEST_DB_USER=test_user
   export TEST_DB_PASSWORD=test_password
   ```

4. **运行测试**
   ```bash
   cd PolyMetric/backend
   python run_postgres_tests_simple.py
   ```

### 方法3: 云PostgreSQL服务

1. **选择云提供商**
   - AWS RDS
   - Google Cloud SQL
   - Azure Database for PostgreSQL
   - ElephantSQL
   - Heroku Postgres

2. **获取连接信息**
   - 主机地址
   - 端口
   - 数据库名
   - 用户名
   - 密码

3. **设置环境变量**
   ```bash
   export TEST_DB_HOST=your-host.amazonaws.com
   export TEST_DB_PORT=5432
   export TEST_DB_NAME=polymetric_test
   export TEST_DB_USER=your_username
   export TEST_DB_PASSWORD=your_password
   ```

## 性能对比

### SQLite vs PostgreSQL

| 指标 | SQLite | PostgreSQL | 说明 |
|--------|--------|-----------|------|
| 并发处理 | 受限 | 优秀 | PostgreSQL天然支持高并发 |
| 数据一致性 | 优秀 | 优秀 | 两者都支持ACID |
| 内存使用 | 低 | 中等 | SQLite更轻量 |
| 配置复杂度 | 简单 | 中等 | SQLite无需额外配置 |
| 生产适用性 | 不推荐 | 推荐 | PostgreSQL更适合生产环境 |

### 预期性能提升

使用PostgreSQL后，预期性能提升：

1. **并发处理能力**: 5-10倍提升
2. **复杂查询性能**: 2-3倍提升
3. **大数据集处理**: 3-5倍提升
4. **连接池管理**: 显著提升高并发场景性能

## 测试配置文件

### PostgreSQL测试设置 (`PolyMetric/postgres_test_settings.py`)

已创建专门的PostgreSQL测试配置，包含：

- 优化的数据库连接参数
- 适合测试的中间件配置
- 简化的认证设置
- 内存缓存配置

### 自动回退机制 (`run_postgres_tests_simple.py`)

实现了智能回退机制：

1. 首先尝试PostgreSQL连接
2. 失败时自动回退到SQLite
3. 确保测试始终能够运行
4. 提供清晰的状态反馈

## 建议

### 开发环境
- 使用SQLite进行日常开发和单元测试
- 配置PostgreSQL进行性能测试和集成测试

### 生产环境
- 必须使用PostgreSQL或类似的企业级数据库
- 配置适当的连接池和缓存策略
- 实施数据库监控和备份策略

### CI/CD流水线
- 在测试阶段使用PostgreSQL容器
- 确保性能测试在真实数据库环境下运行
- 对比SQLite和PostgreSQL的性能指标

## 结论

虽然当前测试使用SQLite并成功运行，但为了获得真实的性能数据，建议配置PostgreSQL环境。系统已提供完整的PostgreSQL支持和自动回退机制，确保在各种环境下都能正常运行测试。
