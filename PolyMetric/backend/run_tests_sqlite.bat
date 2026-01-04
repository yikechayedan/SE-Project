@echo off
echo ========================================
echo PolyMetric Backend SQLite Test Runner
echo ========================================
echo.

cd /d "%~dp0"

echo 使用SQLite数据库运行测试...
echo.

python run_tests_sqlite.py %*

echo.
echo 测试完成
pause