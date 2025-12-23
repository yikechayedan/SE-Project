#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.test_settings')
django.setup()

from apps.users.models import User
from rest_framework.authtoken.models import Token
from apps.tasks.models import EvaluationTask, EvaluationItem

def main():
    print("=== 任务系统检查 ===")
    
    # 1. 创建测试用户
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"[OK] 创建新用户: {user.username}")
    else:
        print(f"[OK] 使用现有用户: {user.username}")
    
    # 2. 获取或创建token
    token, created = Token.objects.get_or_create(user=user)
    print(f"[OK] 认证Token: {token.key}")
    print(f"[OK] 用户ID: {user.id}")
    
    # 3. 检查任务数据
    print("\n=== 任务数据统计 ===")
    tasks = EvaluationTask.objects.all()
    print(f"总任务数: {tasks.count()}")
    
    for task in tasks:
        print(f"\n任务 ID: {task.id}")
        print(f"  名称: {task.name}")
        print(f"  状态: {task.status}")
        print(f"  方法: {task.method}")
        print(f"  创建者: {task.creator.username if task.creator else 'None'}")
        print(f"  数据集: {task.dataset.name if task.dataset else 'None'}")
        print(f"  模型A: {task.myModel.name if task.myModel else 'None'}")
        print(f"  模型B: {task.myModel_2.name if task.myModel_2 else 'None'}")
        print(f"  创建时间: {task.created_at}")
        
        # 检查评测条目
        items = EvaluationItem.objects.filter(task=task)
        print(f"  评测条目数: {items.count()}")
        
        if items.exists():
            completed = items.exclude(score__isnull=True, preference__isnull=True).count()
            pending = items.filter(score__isnull=True, preference__isnull=True).count()
            print(f"    已完成: {completed}")
            print(f"    待评测: {pending}")
    
    # 4. API访问示例
    print(f"\n=== API访问示例 ===")
    print(f"获取任务列表:")
    print(f"curl -H 'Authorization: Token {token.key}' http://127.0.0.1:8003/api/tasks/evaluation-tasks/")
    
    return token.key

if __name__ == '__main__':
    token = main()