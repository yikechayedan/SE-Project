#!/usr/bin/env python
"""
快速SQLite测试运行器 - 非交互式版本
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.test_settings')

# 添加项目路径到Python路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

def run_test_command(test_labels, description):
    """运行测试命令"""
    print(f"\n{'='*80}")
    print(f"运行: {description}")
    print(f"命令: python manage.py test {' '.join(test_labels)}")
    print('='*80)
    
    cmd = [sys.executable, 'manage.py', 'test'] + test_labels + ['--verbosity=2', '--failfast', '--traceback']
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=False)
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n执行时间: {time.strftime('%H:%M:%S', time.gmtime(execution_time))}")
        print(f"返回码: {result.returncode}")
        
        if result.returncode == 0:
            print(f"[SUCCESS] {description} 成功完成")
        else:
            print(f"[WARNING] {description} 失败，但继续运行其他测试...")
        
        return result.returncode
    except KeyboardInterrupt:
        print(f"\n{description} 被用户中断")
        return 1
    except Exception as e:
        print(f"运行{description}时出错: {e}")
        return 1

def main():
    """主函数"""
    print("="*50)
    print("PolyMetric Backend Quick SQLite Test Runner")
    print("="*50)
    print("运行快速测试（跳过性能测试）...")
    print()
    
    # 快速测试
    test_results = []
    test_results.append(run_test_command(
        ['tests.test_utils', 'tests.base', 'tests.conftest'],
        "单元测试"
    ))
    test_results.append(run_test_command(
        ['tests.test_users_api', 'tests.test_datasets_api', 'tests.test_models_api', 
         'tests.test_tasks_api', 'tests.test_rankings_api', 'tests.test_system_api', 
         'tests.test_comments_api'],
        "API测试"
    ))
    test_results.append(run_test_command(
        ['tests.test_integration'],
        "集成测试"
    ))
    
    print(f"\n{'='*60}")
    print("快速测试结果摘要")
    print('='*60)
    
    test_names = ["单元测试", "API测试", "集成测试"]
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "PASS" if result == 0 else "FAIL"
        print(f"{name}: {status}")
    
    passed = sum(1 for r in test_results if r == 0)
    failed = len(test_results) - passed
    print(f"\n总计: {len(test_results)} 个测试套件")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    
    print("\nTests completed")

if __name__ == '__main__':
    main()