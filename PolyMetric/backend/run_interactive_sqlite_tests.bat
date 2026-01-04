@echo off
echo ========================================
echo PolyMetric Backend Interactive SQLite Test Runner
echo ========================================
echo.

cd /d "%~dp0"

echo 启动交互式SQLite测试运行器...
echo.

python run_interactive_sqlite_tests.py

echo.
echo 测试运行器已退出
pause