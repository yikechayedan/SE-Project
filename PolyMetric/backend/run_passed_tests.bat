@echo off
chcp 65001 >nul
echo PolyMetric API Test Runner (Passed Tests Only)
echo ============================================================

cd /d "%~dp0"

:: Check if a specific test module was requested
if "%1"=="" goto run_all
if /i "%1"=="users" goto run_users
if /i "%1"=="datasets" goto run_datasets
if /i "%1"=="models" goto run_models
if /i "%1"=="tasks" goto run_tasks
if /i "%1"=="user" goto run_users
if /i "%1"=="dataset" goto run_datasets
if /i "%1"=="model" goto run_models
if /i "%1"=="task" goto run_tasks

echo Error: Unknown module '%1'
echo Available modules: users, datasets, models, tasks
echo Usage: run_passed_tests.bat [module_name]
echo Examples:
echo   run_passed_tests.bat users
echo   run_passed_tests.bat datasets
echo   run_passed_tests.bat models
echo   run_passed_tests.bat tasks
pause
exit /b 1

:run_users
echo.
echo Running User API tests...
python manage.py test tests.test_users_api --settings=PolyMetric.test_settings --verbosity=1
if %errorlevel% neq 0 exit /b 1
goto end

:run_datasets
echo.
echo Running Dataset API tests...
python manage.py test tests.test_datasets_api --settings=PolyMetric.test_settings --verbosity=1
if %errorlevel% neq 0 exit /b 1
goto end

:run_models
echo.
echo Running Model API tests...
python manage.py test tests.test_models_api --settings=PolyMetric.test_settings --verbosity=1
if %errorlevel% neq 0 exit /b 1
goto end

:run_tasks
echo.
echo Running Task API tests...
python manage.py test tests.test_tasks_api --settings=PolyMetric.test_settings --verbosity=1
if %errorlevel% neq 0 exit /b 1
goto end

:run_all
echo.
echo Running User API tests...
python manage.py test tests.test_users_api --settings=PolyMetric.test_settings --verbosity=1
if %errorlevel% neq 0 exit /b 1

echo.
echo Running Dataset API tests...
python manage.py test tests.test_datasets_api --settings=PolyMetric.test_settings --verbosity=1
if %errorlevel% neq 0 exit /b 1

echo.
echo Running Model API tests...
python manage.py test tests.test_models_api --settings=PolyMetric.test_settings --verbosity=1
if %errorlevel% neq 0 exit /b 1

echo.
echo Running Task API tests...
python manage.py test tests.test_tasks_api --settings=PolyMetric.test_settings --verbosity=1
if %errorlevel% neq 0 exit /b 1

echo.
echo ============================================================
echo All passed tests completed!
echo ============================================================

:end
pause