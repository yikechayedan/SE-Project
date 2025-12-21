@echo off
chcp 65001 >nul
echo PolyMetric 测试运行器
echo ========================================

cd /d "%~dp0"

:: 检查参数
if "%1"=="--help" goto show_help
if "%1"=="-h" goto show_help
if "%1"=="/?" goto show_help

if "%1"=="--advanced" goto run_advanced
if "%1"=="--simple" goto run_simple
if "%1"=="--django" goto run_django
if "%1"=="--coverage" goto run_coverage
if "%1"=="--performance" goto run_performance

:: 默认运行Django测试
goto run_django

:show_help
echo.
echo 用法: run_tests.bat [选项]
echo.
echo 选项:
echo   --django       运行Django测试套件（默认）
echo   --advanced     运行高级测试套件
echo   --simple       运行简化测试套件
echo   --coverage     运行带覆盖率的测试
echo   --performance  运行性能测试
echo   --help, -h, /? 显示此帮助信息
echo.
echo 示例:
echo   run_tests.bat
echo   run_tests.bat --django
echo   run_tests.bat --advanced
echo   run_tests.bat --simple
echo   run_tests.bat --coverage
echo   run_tests.bat --performance
echo.
pause
exit /b 0

:run_django
echo.
echo 运行Django测试套件...
python run_django_tests.py
goto end

:run_advanced
echo.
echo 运行高级测试套件...
python run_advanced_tests.py
goto end

:run_simple
echo.
echo 运行简化测试套件...
python run_simple_tests.py
goto end

:run_coverage
echo.
echo 运行带覆盖率的测试...
python run_advanced_tests.py --coverage
goto end

:run_performance
echo.
echo 运行性能测试...
python run_advanced_tests.py --categories performance --benchmark
goto end

:end
echo.
echo ========================================
echo 测试完成！
echo ========================================
pause