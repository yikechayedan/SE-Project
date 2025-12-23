#!/usr/bin/env python
"""
启动Celery Worker脚本
用于处理异步任务，包括数据集能力分析
"""
import os
import sys
import subprocess
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.settings')
django.setup()

def start_celery_worker():
    """启动Celery Worker"""
    print("启动Celery Worker...")
    
    # 构建Celery命令
    cmd = [
        sys.executable, '-m', 'celery', 
        '-A', 'PolyMetric.celery',
        'worker',
        '--loglevel=info',
        '--concurrency=2',  # 限制并发数，避免过多API调用
        '--max-tasks-per-child=10'  # 防止内存泄漏
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    # 启动Worker
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nCelery Worker已停止")
    except subprocess.CalledProcessError as e:
        print(f"启动Celery Worker失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_celery_worker()