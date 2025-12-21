#!/usr/bin/env python
"""
高级测试运行器 - 提供业界标准的测试执行和报告功能
"""
import os
import sys
import argparse
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.test_settings')

import django
django.setup()

from tests.test_monitoring import start_test_monitoring, end_test_monitoring


class AdvancedTestRunner:
    """高级测试运行器"""
    
    def __init__(self):
        self.test_categories = {
            'unit': {
                'description': '单元测试 - 测试单个功能点',
                'modules': [
                    'tests.test_users_api',
                    'tests.test_datasets_api',
                    'tests.test_models_api',
                    'tests.test_tasks_api',
                    'tests.test_rankings_api',
                    'tests.test_system_api'
                ]
            },
            'integration': {
                'description': '集成测试 - 测试模块间交互',
                'modules': ['tests.test_integration']
            },
            'performance': {
                'description': '性能测试 - 测试API响应时间和资源使用',
                'modules': ['tests.test_performance']
            },
            'e2e': {
                'description': '端到端测试 - 测试完整业务流程',
                'modules': ['tests.test_e2e']
            },
            'contracts': {
                'description': '契约测试 - 验证API响应格式',
                'modules': ['tests.test_contracts']
            },
            'monitoring': {
                'description': '监控系统测试',
                'modules': ['tests.test_monitoring']
            }
        }
        
        self.report_dir = Path("test_reports")
        self.report_dir.mkdir(exist_ok=True)
    
    def run_tests(self, categories=None, modules=None, coverage=False, 
                 parallel=False, verbose=False, benchmark=False):
        """运行测试"""
        # 开始监控
        start_test_monitoring()
        
        try:
            # 确定要运行的测试
            if modules:
                test_modules = modules
            elif categories:
                test_modules = []
                for category in categories:
                    if category in self.test_categories:
                        test_modules.extend(self.test_categories[category]['modules'])
            else:
                # 运行所有测试
                test_modules = []
                for category_data in self.test_categories.values():
                    test_modules.extend(category_data['modules'])
            
            # 构建Django测试命令
            cmd = self._build_django_command(
                test_modules, coverage, parallel, verbose, benchmark
            )
            
            print(f"🚀 运行测试: {' '.join(cmd)}")
            print(f"📊 测试模块: {', '.join(test_modules)}")
            
            # 执行测试
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            end_time = time.time()
            
            # 输出结果
            print("📤 标准输出:")
            print(result.stdout)
            
            if result.stderr:
                print("❌ 错误输出:")
                print(result.stderr)
            
            # 计算执行时间
            execution_time = end_time - start_time
            print(f"⏱️  测试执行时间: {execution_time:.2f}秒")
            
            # 生成报告
            self._generate_additional_reports()
            
            # 结束监控
            end_test_monitoring()
            
            return result.returncode
            
        except Exception as e:
            print(f"❌ 测试运行出错: {e}")
            end_test_monitoring()
            return 1
    
    def _build_django_command(self, modules, coverage, parallel, verbose, benchmark):
        """构建Django测试命令"""
        cmd = ['python', 'manage.py', 'test']
        
        # 添加模块
        for module in modules:
            cmd.append(module)
        
        # 添加选项
        if verbose:
            cmd.append('--verbosity=2')
        else:
            cmd.append('--verbosity=1')
        
        # 添加测试设置
        cmd.append('--settings=PolyMetric.test_settings')
        
        # 如果需要覆盖率，使用coverage工具
        if coverage:
            # 使用coverage运行Django测试
            coverage_cmd = [
                'coverage', 'run', '--source=.', 'manage.py', 'test'
            ]
            for module in modules:
                coverage_cmd.append(module)
            coverage_cmd.extend(['--settings=PolyMetric.test_settings', '--verbosity=1'])
            return coverage_cmd
        
        return cmd
    
    def _generate_additional_reports(self):
        """生成额外报告"""
        # 生成API契约文件
        try:
            from tests.test_contracts import ContractFileGenerator
            ContractFileGenerator.generate_contract_files()
            print("📄 API契约文件已生成")
        except Exception as e:
            print(f"⚠️  生成API契约文件失败: {e}")
        
        # 生成测试数据示例
        try:
            self._generate_test_data_examples()
            print("📊 测试数据示例已生成")
        except Exception as e:
            print(f"⚠️  生成测试数据示例失败: {e}")
    
    def _generate_test_data_examples(self):
        """生成测试数据示例"""
        try:
            from tests.factories import ScenarioFactory
            
            examples_dir = self.report_dir / "examples"
            examples_dir.mkdir(exist_ok=True)
            
            # 生成完整场景示例
            scenario = ScenarioFactory.create_complete_scenario()
            
            example_data = {
                'users': [
                    {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                    for user in scenario['users']
                ],
                'models': [
                    {
                        'id': model.id,
                        'name': model.name,
                        'company': model.company,
                        'category': model.category
                    }
                    for model in scenario['models']
                ],
                'datasets': [
                    {
                        'id': dataset.id,
                        'name': dataset.name,
                        'category': dataset.category,
                        'is_public': dataset.is_public
                    }
                    for dataset in scenario['datasets']
                ],
                'tasks': [
                    {
                        'id': task.id,
                        'name': task.name,
                        'method': task.method,
                        'status': task.status
                    }
                    for task in scenario['tasks']
                ]
            }
            
            with open(examples_dir / "test_data_examples.json", 'w', encoding='utf-8') as f:
                json.dump(example_data, f, indent=2, ensure_ascii=False)
        except ImportError as e:
            print(f"⚠️  无法导入工厂模块: {e}")
        except Exception as e:
            print(f"⚠️  生成测试数据示例失败: {e}")
    
    def list_categories(self):
        """列出所有测试类别"""
        print("📋 可用的测试类别:")
        print("=" * 60)
        
        for category, data in self.test_categories.items():
            print(f"\n🏷️  {category}:")
            print(f"   📝 {data['description']}")
            print(f"   📦 模块: {', '.join(data['modules'])}")
        
        print("\n" + "=" * 60)
        print("💡 使用方法:")
        print("   python run_advanced_tests.py --categories unit integration")
        print("   python run_advanced_tests.py --modules tests.test_users_api")
    
    def run_health_check(self):
        """运行健康检查"""
        print("运行测试环境健康检查...")
        
        checks = []
        
        # 检查Django设置
        try:
            import django
            from django.conf import settings
            if settings.configured:
                checks.append(("Django设置", "✅ 已配置", True))
            else:
                checks.append(("Django设置", "❌ 未配置", False))
        except Exception as e:
            checks.append(("Django设置", f"❌ 错误: {e}", False))
        
        # 检查数据库连接
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            checks.append(("数据库连接", "✅ 正常", True))
        except Exception as e:
            checks.append(("数据库连接", f"❌ 错误: {e}", False))
        
        # 检查测试文件
        try:
            test_files = list(Path("tests").glob("test_*.py"))
            if test_files:
                checks.append(("测试文件", f"✅ 找到 {len(test_files)} 个", True))
            else:
                checks.append(("测试文件", "❌ 未找到", False))
        except Exception as e:
            checks.append(("测试文件", f"❌ 错误: {e}", False))
        
        # 检查依赖
        try:
            import pytest
            checks.append(("pytest", "✅ 已安装", True))
        except ImportError:
            checks.append(("pytest", "⚠️  未安装（可选）", True))
        
        try:
            import factory
            checks.append(("factory_boy", "✅ 已安装", True))
        except ImportError:
            checks.append(("factory_boy", "⚠️  未安装（可选）", True))
        
        # 输出检查结果
        print("\n健康检查结果:")
        print("=" * 60)
        
        all_passed = True
        for name, status, passed in checks:
            print(f"{status} {name}")
            if not passed:
                all_passed = False
        
        print("=" * 60)
        
        if all_passed:
            print("所有检查通过，测试环境准备就绪!")
            return 0
        else:
            print("存在问题，请检查环境配置")
            return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PolyMetric 高级测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 运行所有测试
  python run_advanced_tests.py
  
  # 运行特定类别
  python run_advanced_tests.py --categories unit integration
  
  # 运行特定模块
  python run_advanced_tests.py --modules tests.test_users_api
  
  # 运行带覆盖率的测试
  python run_advanced_tests.py --coverage
  
  # 并行运行测试
  python run_advanced_tests.py --parallel
  
  # 运行性能基准测试
  python run_advanced_tests.py --benchmark
  
  # 列出所有测试类别
  python run_advanced_tests.py --list
  
  # 健康检查
  python run_advanced_tests.py --health
        """
    )
    
    parser.add_argument(
        '--categories', '-c',
        nargs='+',
        choices=['unit', 'integration', 'performance', 'e2e', 'contracts', 'monitoring'],
        help='运行指定类别的测试'
    )
    
    parser.add_argument(
        '--modules', '-m',
        nargs='+',
        help='运行指定模块的测试'
    )
    
    parser.add_argument(
        '--coverage', '--cov',
        action='store_true',
        help='生成测试覆盖率报告'
    )
    
    parser.add_argument(
        '--parallel', '-p',
        action='store_true',
        help='并行运行测试'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出'
    )
    
    parser.add_argument(
        '--benchmark', '-b',
        action='store_true',
        help='运行性能基准测试'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='列出所有测试类别'
    )
    
    parser.add_argument(
        '--health', '-H',
        action='store_true',
        help='运行环境健康检查'
    )
    
    args = parser.parse_args()
    
    # 切换到项目目录
    os.chdir(project_root)
    
    # 创建测试运行器
    runner = AdvancedTestRunner()
    
    if args.list:
        runner.list_categories()
        return 0
    
    if args.health:
        return runner.run_health_check()
    
    # 运行测试
    return runner.run_tests(
        categories=args.categories,
        modules=args.modules,
        coverage=args.coverage,
        parallel=args.parallel,
        verbose=args.verbose,
        benchmark=args.benchmark
    )


if __name__ == "__main__":
    sys.exit(main())