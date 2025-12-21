#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Django测试运行器 - 简单直接的Django测试执行
"""
import os
import sys
import subprocess
from pathlib import Path

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import locale
    import codecs
    # 尝试设置控制台编码
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    except:
        pass

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.test_settings')


def run_test_module(module_name, verbose=True):
    """运行单个测试模块"""
    verbosity = '2' if verbose else '1'
    cmd = [
        'python', 'manage.py', 'test',
        f'tests.{module_name}',
        f'--settings=PolyMetric.test_settings',
        f'--verbosity={verbosity}'
    ]
    
    print(f"运行测试模块: {module_name}")
    print(f"命令: {' '.join(cmd)}")
    print("-" * 60)
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"{module_name} 测试通过!")
    else:
        print(f"{module_name} 测试失败!")
    
    print("-" * 60)
    return result.returncode


def run_all_tests():
    """运行所有测试"""
    test_modules = [
        'test_users_api',
        'test_datasets_api',
        'test_models_api',
        'test_tasks_api',
        'test_rankings_api',
        'test_system_api',
        'test_integration'
    ]
    
    print("运行所有Django测试")
    print("=" * 60)
    
    all_passed = True
    for module in test_modules:
        if run_test_module(module, verbose=False) != 0:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("所有测试通过!")
        return 0
    else:
        print("部分测试失败!")
        return 1


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 运行指定模块
        module_name = sys.argv[1]
        return run_test_module(module_name)
    else:
        # 运行所有测试
        return run_all_tests()


if __name__ == "__main__":
    # 切换到项目目录
    os.chdir(project_root)
    sys.exit(main())