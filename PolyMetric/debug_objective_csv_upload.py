#!/usr/bin/env python
"""
调试objective_test_dataset.csv上传失败问题
模拟上传过程，找出400错误的具体原因
"""
import os
import sys
import django
import tempfile
import csv
import json
from io import StringIO

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.settings')
django.setup()

from apps.datasets.models import Dataset
from apps.datasets.serializers import DatasetSerializer
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

def test_objective_csv_upload():
    """测试objective_test_dataset.csv上传"""
    print("=" * 60)
    print("测试objective_test_dataset.csv上传")
    print("=" * 60)
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username='testuser_objective',
        defaults={'email': 'testobjective@example.com', 'password': 'testpass123'}
    )
    
    try:
        # 读取objective_test_dataset.csv文件
        csv_path = "objective_test_dataset.csv"
        
        if not os.path.exists(csv_path):
            print(f"  ✗ 文件不存在: {csv_path}")
            return False
        
        with open(csv_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile(
                name="objective_test_dataset.csv",
                content=f.read(),
                content_type="text/csv"
            )
            
            request_data = {
                'name': '客观测评数据集测试',
                'description': '测试客观测评CSV数据集上传',
                'category': 'text',
                'evaluation_type': 'objective',
                'file_format': 'csv',
                'file_path': uploaded_file,
                'is_public': False
            }
            
            print(f"  请求数据: {json.dumps({k: v for k, v in request_data.items() if k != 'file_path'}, ensure_ascii=False, indent=2)}")
            
            # 创建序列化器并验证
            serializer = DatasetSerializer(
                data=request_data,
                context={'request': type('MockRequest', (), {'user': user})()}
            )
            
            print("\n  开始验证...")
            
            if serializer.is_valid():
                print("  ✓ 验证通过，开始创建数据集...")
                dataset = serializer.save()
                print(f"  ✓ 数据集创建成功，ID: {dataset.id}")
                print(f"    样本数量: {dataset.sample_count}")
                print(f"    能力标签: {dataset.capability_tag}")
                print(f"    验证状态: {dataset.is_verified}")
                
                # 清理测试数据
                if dataset.file_path and os.path.exists(dataset.file_path.path):
                    os.unlink(dataset.file_path.path)
                dataset.delete()
                return True
            else:
                print(f"  ✗ 验证失败:")
                for field, errors in serializer.errors.items():
                    print(f"    {field}: {errors}")
                return False
        
    except Exception as e:
        print(f"  ✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_csv_format():
    """分析CSV文件格式"""
    print("\n" + "=" * 60)
    print("分析objective_test_dataset.csv格式")
    print("=" * 60)
    
    csv_path = "objective_test_dataset.csv"
    
    if not os.path.exists(csv_path):
        print(f"  ✗ 文件不存在: {csv_path}")
        return
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"  文件大小: {len(content)} 字节")
            
            # 分析CSV结构
            reader = csv.DictReader(StringIO(content))
            headers = reader.fieldnames
            print(f"  表头: {headers}")
            
            rows = list(reader)
            print(f"  数据行数: {len(rows)}")
            
            # 检查每行数据
            for i, row in enumerate(rows[:5]):  # 只显示前5行
                print(f"  第{i+2}行: {row}")
                
                # 检查必需字段
                if 'input' not in row or not row['input'].strip():
                    print(f"    ✗ 第{i+2}行缺少或为空的input字段")
                
                if 'answer' not in row or not row['answer'].strip():
                    print(f"    ✗ 第{i+2}行缺少或为空的answer字段")
                
                # 检查答案格式
                if 'answer' in row:
                    answer = row['answer'].strip().upper()
                    if not re.match(r'^[A-Z]$', answer):
                        print(f"    ✗ 第{i+2}行答案格式错误: {answer} (应为单个字母)")
                
                # 检查选项
                if 'input' in row:
                    input_text = row['input']
                    options = re.findall(r'\b([A-Z])\.', input_text)
                    options = list(set([opt.upper() for opt in options]))
                    if len(options) < 2:
                        print(f"    ✗ 第{i+2}行选项不足: {options}")
                    else:
                        if 'answer' in row and row['answer'].strip().upper() not in options:
                            print(f"    ✗ 第{i+2}行答案不在选项中: 答案={row['answer']}, 选项={options}")
    
    except Exception as e:
        print(f"  ✗ 分析CSV格式时发生错误: {e}")
        import traceback
        traceback.print_exc()

def test_csv_validation_directly():
    """直接测试CSV验证逻辑"""
    print("\n" + "=" * 60)
    print("直接测试CSV验证逻辑")
    print("=" * 60)
    
    csv_path = "objective_test_dataset.csv"
    
    if not os.path.exists(csv_path):
        print(f"  ✗ 文件不存在: {csv_path}")
        return
    
    try:
        # 创建DatasetSerializer实例
        serializer = DatasetSerializer()
        
        with open(csv_path, 'rb') as f:
            from django.core.files.uploadedfile import SimpleUploadedFile
            uploaded_file = SimpleUploadedFile(
                name="objective_test_dataset.csv",
                content=f.read(),
                content_type="text/csv"
            )
            
            print("  开始验证数据集格式...")
            try:
                result = serializer.validate_dataset_format(uploaded_file, "objective", "text")
                print(f"  ✓ 验证结果: {result}")
            except Exception as e:
                print(f"  ✗ 验证失败: {e}")
                return False
    
    except Exception as e:
        print(f"  ✗ 直接验证时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

import re

def main():
    """主函数"""
    print("开始调试objective_test_dataset.csv上传问题...")
    
    # 分析CSV格式
    analyze_csv_format()
    
    # 直接测试验证逻辑
    validation_result = test_csv_validation_directly()
    
    # 测试完整上传流程
    if validation_result:
        upload_result = test_objective_csv_upload()
        
        if upload_result:
            print("\n✓ 所有测试通过，CSV上传应该正常工作")
        else:
            print("\n✗ 上传测试失败，需要进一步调查")
    else:
        print("\n✗ 验证逻辑测试失败，问题可能在验证阶段")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())