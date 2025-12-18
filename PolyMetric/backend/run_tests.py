#!/usr/bin/env python
"""
测试运行脚本 - 用于执行项目的所有API测试
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path


def run_command(cmd, description=""):
    """运行命令并打印结果"""
    print(f"\n{'='*60}")
    if description:
        print(f"执行: {description}")
    print(f"命令: {cmd}")
    print('='*60)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("输出:")
        print(result.stdout)
    
    if result.stderr:
        print("错误:")
        print(result.stderr)
    
    return result.returncode


def run_specific_test(test_module, test_class=None, test_method=None):
    """运行特定的测试"""
    if test_method:
        test_path = f"tests.{test_module}.{test_class}.{test_method}"
    elif test_class:
        test_path = f"tests.{test_module}.{test_class}"
    else:
        test_path = f"tests.{test_module}"
    
    cmd = f"python manage.py test {test_path} --verbosity=2"
    return run_command(cmd, f"运行 {test_path}")


def run_all_tests():
    """运行所有测试"""
    test_modules = [
        "test_users_api",
        "test_datasets_api", 
        "test_models_api",
        "test_tasks_api",
        "test_rankings_api",
        "test_system_api",
        "test_integration"
    ]
    
    results = {}
    for module in test_modules:
        print(f"\n{'#'*60}")
        print(f"运行模块: {module}")
        print('#'*60)
        
        cmd = f"python manage.py test tests.{module} --verbosity=2"
        returncode = run_command(cmd, f"运行 {module} 模块测试")
        results[module] = returncode == 0
    
    # 打印测试结果摘要
    print(f"\n{'#'*60}")
    print("测试结果摘要")
    print('#'*60)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for module, success in results.items():
        status = "通过" if success else "失败"
        print(f"{module}: {status}")
    
    print(f"\n总计: {passed}/{total} 个模块通过")
    
    if passed == total:
        print("成功: 所有测试都通过了!")
        return 0
    else:
        print("错误: 部分测试失败，请检查上面的错误信息")
        return 1


def run_coverage():
    """运行测试并生成覆盖率报告"""
    print("运行测试并生成覆盖率报告...")
    
    # 安装coverage如果不存在
    install_cmd = "pip install coverage"
    run_command(install_cmd, "安装coverage工具")
    
    # 运行测试并收集覆盖率
    coverage_cmd = "coverage run --source='.' manage.py test tests --verbosity=2"
    run_command(coverage_cmd, "运行测试并收集覆盖率")
    
    # 生成覆盖率报告
    report_cmd = "coverage report --show-missing --omit='*/tests/*,*/migrations/*,*/venv/*,*/env/*'"
    run_command(report_cmd, "生成覆盖率报告")
    
    # 生成HTML覆盖率报告
    html_cmd = "coverage html --omit='*/tests/*,*/migrations/*,*/venv/*,*/env/*'"
    run_command(html_cmd, "生成HTML覆盖率报告")
    
    print("\n覆盖率报告已生成:")
    print("- 终端报告: 见上方输出")
    print("- HTML报告: htmlcov/index.html")


def check_environment():
    """检查测试环境"""
    print("检查测试环境...")
    
    # 检查Django设置
    try:
        import django
        from django.conf import settings
        if not settings.configured:
            print("错误: Django设置未配置")
            return False
        print("成功: Django设置已配置")
    except ImportError:
        print("错误: Django未安装")
        return False
    
    # 检查数据库
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("成功: 数据库连接正常")
    except Exception as e:
        print(f"错误: 数据库连接失败: {e}")
        return False
    
    # 检查测试文件
    test_dir = Path("tests")
    if not test_dir.exists():
        print("错误: 测试目录不存在")
        return False
    
    test_files = list(test_dir.glob("test_*.py"))
    if not test_files:
        print("错误: 没有找到测试文件")
        return False
    
    print(f"成功: 找到 {len(test_files)} 个测试文件")
    return True


def setup_test_environment():
    """设置测试环境"""
    print("设置测试环境...")
    
    # 运行数据库迁移
    migrate_cmd = "python manage.py migrate"
    run_command(migrate_cmd, "运行数据库迁移")
    
    # 收集静态文件
    collectstatic_cmd = "python manage.py collectstatic --noinput"
    run_command(collectstatic_cmd, "收集静态文件")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="PolyMetric API测试运行器")
    parser.add_argument("--module", "-m", help="运行特定模块的测试")
    parser.add_argument("--class", "-c", help="运行特定测试类")
    parser.add_argument("--method", "-f", help="运行特定测试方法")
    parser.add_argument("--coverage", action="store_true", help="运行测试并生成覆盖率报告")
    parser.add_argument("--check", action="store_true", help="检查测试环境")
    parser.add_argument("--setup", action="store_true", help="设置测试环境")
    parser.add_argument("--all", "-a", action="store_true", help="运行所有测试（默认）")
    
    args = parser.parse_args()
    
    # 切换到项目目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 设置环境变量
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.settings')
    
    if args.check:
        if not check_environment():
            sys.exit(1)
        return
    
    if args.setup:
        if not check_environment():
            print("环境检查失败，无法继续设置")
            sys.exit(1)
        setup_test_environment()
        return
    
    # 检查环境
    if not check_environment():
        print("环境检查失败，请先运行 --setup 或解决环境问题")
        sys.exit(1)
    
    if args.coverage:
        run_coverage()
        sys.exit(0)
    
    if args.module:
        returncode = run_specific_test(args.module, getattr(args, 'class'), args.method)
        sys.exit(returncode)
    
    # 默认运行所有测试
    returncode = run_all_tests()
    sys.exit(returncode)


if __name__ == "__main__":
    main()