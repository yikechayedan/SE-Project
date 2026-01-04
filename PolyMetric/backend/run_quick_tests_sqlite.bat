@echo off
echo ========================================
echo PolyMetric Backend Quick SQLite Test Runner
echo ========================================
echo.

cd /d "%~dp0"

echo 运行快速测试（跳过性能测试）...
echo.

python run_quick_tests_sqlite.py

echo.
pause