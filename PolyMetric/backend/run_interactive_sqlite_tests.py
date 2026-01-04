#!/usr/bin/env python
"""
交互式SQLite测试运行器
"""
import os
import sys
import subprocess
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
    
    import time
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
    print("PolyMetric Backend SQLite Test Runner")
    print("="*50)
    print("使用SQLite数据库运行测试（无需PostgreSQL服务器）")
    print()
    
    while True:
        print("请选择测试类型:")
        print("1. 快速测试（推荐）")
        print("2. 单元测试")
        print("3. API测试")
        print("4. 集成测试")
        print("5. 端到端测试")
        print("6. 性能测试")
        print("7. 应用测试")
        print("8. 所有测试")
        print("9. 覆盖率测试")
        print("10. 运行特定测试")
        print("0. 退出")
        print()
        
        try:
            choice = input("请输入选择 (0-10): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n退出测试运行器")
            break
        
        if choice == '0':
            print("退出测试运行器")
            break
        elif choice == '1':
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
            test_results.append(run_test_command(
                ['tests.test_e2e'],
                "端到端测试"
            ))
        
            print(f"\n{'='*60}")
            print("快速测试结果摘要")
            print('='*60)
            
            test_names = ["单元测试", "API测试", "集成测试", "端到端测试"]
            for i, (name, result) in enumerate(zip(test_names, test_results)):
                status = "PASS" if result == 0 else "FAIL"
                print(f"{name}: {status}")
            
            passed = sum(1 for r in test_results if r == 0)
            failed = len(test_results) - passed
            print(f"\n总计: {len(test_results)} 个测试套件")
            print(f"通过: {passed}")
            print(f"失败: {failed}")
            
        elif choice == '2':
            # 单元测试
            run_test_command(
                ['tests.test_utils', 'tests.base', 'tests.conftest'],
                "单元测试"
            )
        elif choice == '3':
            # API测试
            run_test_command(
                ['tests.test_users_api', 'tests.test_datasets_api', 'tests.test_models_api', 
                 'tests.test_tasks_api', 'tests.test_rankings_api', 'tests.test_system_api', 
                 'tests.test_comments_api'],
                "API测试"
            )
        elif choice == '4':
            # 集成测试
            run_test_command(
                ['tests.test_integration'],
                "集成测试"
            )
        elif choice == '5':
            # 端到端测试
            run_test_command(
                ['tests.test_e2e'],
                "端到端测试"
            )
        elif choice == '6':
            # 性能测试
            run_test_command(
                ['tests.test_performance'],
                "性能测试"
            )
        elif choice == '7':
            # 应用测试
            print("\n可用的应用测试:")
            apps = ['users', 'datasets', 'models', 'tasks', 'rankings', 'system', 'comments']
            for i, app in enumerate(apps, 1):
                print(f"{i}. {app}")
            
            try:
                app_choice = input("请选择应用 (1-7): ").strip()
                if app_choice.isdigit() and 1 <= int(app_choice) <= 7:
                    app_name = apps[int(app_choice) - 1]
                    run_test_command(
                        [f'tests.test_{app_name}_api'],
                        f"{app_name}应用测试"
                    )
                else:
                    print("无效选择")
            except (EOFError, KeyboardInterrupt):
                print("\n返回主菜单")
                continue
                
        elif choice == '8':
            # 所有测试
            run_test_command(
                ['tests'],
                "所有测试"
            )
        elif choice == '9':
            # 覆盖率测试
            print("覆盖率测试需要安装coverage包")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'], 
                             cwd=BASE_DIR, check=True)
                
                # 运行覆盖率测试
                subprocess.run([sys.executable, '-m', 'coverage', 'run', 'manage.py', 'test', 'tests'],
                             cwd=BASE_DIR)
                subprocess.run([sys.executable, '-m', 'coverage', 'report'],
                             cwd=BASE_DIR)
                subprocess.run([sys.executable, '-m', 'coverage', 'html'],
                             cwd=BASE_DIR)
                print("覆盖率报告已生成到 htmlcov/ 目录")
            except subprocess.CalledProcessError:
                print("安装coverage包失败")
            except Exception as e:
                print(f"运行覆盖率测试时出错: {e}")
                
        elif choice == '10':
            # 运行特定测试
            test_name = input("请输入测试名称 (例如: tests.test_users_api.UserRegistrationAPITest): ").strip()
            if test_name:
                run_test_command(
                    [test_name],
                    f"特定测试: {test_name}"
                )
        else:
            print("无效选择，请重新输入")
        
        print("\n" + "="*50)
        input("请按任意键继续...")
        print()

if __name__ == '__main__':
    import time
    main()