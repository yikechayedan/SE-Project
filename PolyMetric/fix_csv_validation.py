#!/usr/bin/env python
"""
修复CSV验证中的选项匹配问题
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.settings')
django.setup()

def fix_csv_validation():
    """修复CSV验证中的选项匹配问题"""
    print("修复CSV验证中的选项匹配问题...")
    
    # 读取序列化器文件
    serializer_path = "apps/datasets/serializers.py"
    
    with open(serializer_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到需要修复的代码行
    old_pattern = 'option_pattern = re.compile(r"\\b([A-Z])\\.", re.IGNORECASE)'
    new_pattern = 'option_pattern = re.compile(r"\\\\n([A-Z])\\.", re.IGNORECASE)'
    
    if old_pattern in content:
        # 替换正则表达式模式
        content = content.replace(old_pattern, new_pattern)
        
        # 还需要在验证前处理转义的换行符
        # 找到验证函数中的input_text处理部分
        old_input_text = 'input_text = item["input"]'
        new_input_text = '''# 处理转义的换行符
                input_text = item["input"].replace('\\\\n', '\\n')'''
        
        content = content.replace(old_input_text, new_input_text)
        
        # 写回文件
        with open(serializer_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ 修复完成：")
        print("  1. 更新了正则表达式以匹配转义的换行符后的选项")
        print("  2. 添加了转义换行符的处理")
        return True
    else:
        print("✗ 未找到需要修复的代码模式")
        return False

def test_fixed_validation():
    """测试修复后的验证逻辑"""
    print("\n测试修复后的验证逻辑...")
    
    from apps.datasets.serializers import DatasetSerializer
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    csv_path = "../../objective_test_dataset.csv"
    
    if not os.path.exists(csv_path):
        print(f"文件不存在: {csv_path}")
        return False
    
    try:
        # 创建DatasetSerializer实例
        serializer = DatasetSerializer()
        
        with open(csv_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile(
                name="objective_test_dataset.csv",
                content=f.read(),
                content_type="text/csv"
            )
            
            print("开始验证数据集格式...")
            try:
                result = serializer.validate_dataset_format(uploaded_file, "objective", "text")
                print(f"✓ 验证成功: {result}")
                return True
            except Exception as e:
                print(f"✗ 验证失败: {e}")
                return False
    
    except Exception as e:
        print(f"测试验证时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始修复CSV验证问题...")
    
    # 应用修复
    fix_applied = fix_csv_validation()
    
    if fix_applied:
        # 测试修复后的验证
        test_result = test_fixed_validation()
        
        if test_result:
            print("\n✓ 修复成功！CSV验证现在应该可以正常工作")
            print("请重启Django服务器以应用更改")
        else:
            print("\n✗ 修复后验证仍然失败，需要进一步调查")
    else:
        print("\n✗ 修复失败，代码可能已经修改过")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())