#!/usr/bin/env python
"""
使用SQLite数据库运行Django测试
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.test_settings')

# 添加项目路径到Python路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

def run_tests(test_labels=None, verbosity=2, keepdb=False, parallel=False):
    """
    运行Django测试
    """
    cmd = [
        sys.executable, 'manage.py', 'test'
    ]
    
    if test_labels:
        cmd.extend(test_labels)
    
    cmd.extend([
        f'--verbosity={verbosity}',
        '--failfast',
        '--traceback',
    ])
    
    if keepdb:
        cmd.append('--keepdb')
    
    if parallel:
        cmd.append(f'--parallel={parallel}')
    
    print(f"运行命令: {' '.join(cmd)}")
    print("=" * 80)
    
    try:
        result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        return 1
    except Exception as e:
        print(f"运行测试时出错: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description='运行Django测试（使用SQLite）')
    parser.add_argument(
        'test_labels',
        nargs='*',
        help='要运行的测试标签（例如：tests.test_models）'
    )
    parser.add_argument(
        '--verbosity', '-v',
        type=int,
        default=2,
        choices=[0, 1, 2, 3],
        help='输出详细程度（0-3）'
    )
    parser.add_argument(
        '--keepdb',
        action='store_true',
        help='保留测试数据库'
    )
    parser.add_argument(
        '--parallel', '-p',
        type=int,
        help='并行运行测试的进程数'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='运行快速测试（单元测试、API测试、集成测试）'
    )
    parser.add_argument(
        '--unit',
        action='store_true',
        help='只运行单元测试'
    )
    parser.add_argument(
        '--api',
        action='store_true',
        help='只运行API测试'
    )
    parser.add_argument(
        '--integration',
        action='store_true',
        help='只运行集成测试'
    )
    parser.add_argument(
        '--app',
        type=str,
        help='运行特定应用的测试（例如：users）'
    )
    
    args = parser.parse_args()
    
    # 根据参数确定要运行的测试
    test_labels = args.test_labels
    
    if args.quick:
        test_labels = [
            'tests.test_utils',
            'tests.base',
            'tests.conftest',
            'tests.test_users_api',
            'tests.test_datasets_api',
            'tests.test_models_api',
            'tests.test_tasks_api',
            'tests.test_rankings_api',
            'tests.test_system_api',
            'tests.test_comments_api',
            'tests.test_integration'
        ]
    elif args.unit:
        test_labels = [
            'tests.test_utils',
            'tests.base',
            'tests.conftest'
        ]
    elif args.api:
        test_labels = [
            'tests.test_users_api',
            'tests.test_datasets_api',
            'tests.test_models_api',
            'tests.test_tasks_api',
            'tests.test_rankings_api',
            'tests.test_system_api',
            'tests.test_comments_api'
        ]
    elif args.integration:
        test_labels = ['tests.test_integration']
    elif args.app:
        test_labels = [f'tests.{args.app}']
    
    # 运行测试
    return_code = run_tests(
        test_labels=test_labels,
        verbosity=args.verbosity,
        keepdb=args.keepdb,
        parallel=args.parallel
    )
    
    if return_code == 0:
        print("\n[SUCCESS] 测试成功完成！")
    else:
        print(f"\n[FAILED] 测试失败，返回码: {return_code}")
    
    return return_code

if __name__ == '__main__':
    sys.exit(main())