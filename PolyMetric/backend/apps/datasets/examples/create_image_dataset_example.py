"""
创建图片数据集示例脚本

这个脚本演示如何创建一个包含图片的数据集示例ZIP文件，
用于测试和演示图片数据集上传功能。
"""

import os
import json
import zipfile
from io import BytesIO

def create_image_dataset_example():
    """创建一个包含图片的数据集示例"""
    
    # 创建示例数据
    dataset_data = [
        {
            "id": 1,
            "input": "请描述这张图片的内容",
            "image": "sample1.jpg",
            "reference": "这是一张示例图片，显示了美丽的风景"
        },
        {
            "id": 2,
            "input": "这张图片中的主要对象是什么？",
            "image": "sample2.png",
            "reference": "图片中主要是一个建筑物"
        },
        {
            "id": 3,
            "input": "分析这张图片的风格",
            "image": "sample3.gif",
            "reference": "这是一张现代风格的图片"
        }
    ]
    
    # 创建ZIP文件
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 添加JSON数据文件
        zip_file.writestr('data.json', json.dumps(dataset_data, ensure_ascii=False, indent=2))
        
        # 创建示例图片文件（实际使用中，这些应该是真实的图片文件）
        # 这里我们创建简单的文本文件作为占位符
        sample_images = {
            'sample1.jpg': '这是一个JPEG图片文件的占位符',
            'sample2.png': '这是一个PNG图片文件的占位符',
            'sample3.gif': '这是一个GIF图片文件的占位符'
        }
        
        for filename, content in sample_images.items():
            zip_file.writestr(filename, content)
        
        # 添加README文件
        readme_content = """# 图片数据集示例

这是一个包含图片的数据集示例，用于演示如何上传图片数据集。

## 文件结构
- data.json: 数据集的JSON文件，包含样本数据和图片引用
- sample1.jpg: 示例图片1
- sample2.png: 示例图片2
- sample3.gif: 示例图片3

## 使用方法
1. 将此ZIP文件上传到PolyMetric平台
2. 系统会自动识别图片数量和样本数量
3. 上传成功后可以通过API访问图片文件

## 注意事项
- 实际使用时，请替换为真实的图片文件
- 确保JSON中的image字段与实际文件名匹配
- 图片文件大小应适中，避免上传过大的文件
"""
        zip_file.writestr('README.txt', readme_content)
    
    # 保存ZIP文件
    zip_filename = 'image_dataset_example.zip'
    zip_path = os.path.join(os.path.dirname(__file__), zip_filename)
    
    with open(zip_path, 'wb') as f:
        f.write(zip_buffer.getvalue())
    
    print(f"图片数据集示例已创建: {zip_path}")
    print(f"文件大小: {os.path.getsize(zip_path)} 字节")
    
    # 显示ZIP文件内容
    print("\nZIP文件内容:")
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        for file_info in zip_file.filelist:
            print(f"  {file_info.filename} ({file_info.file_size} 字节)")
    
    return zip_path

def create_complex_image_dataset_example():
    """创建一个更复杂的图片数据集示例，包含子目录"""
    
    # 创建示例数据
    dataset_data = {
        "metadata": {
            "name": "复杂图片数据集示例",
            "description": "这是一个包含子目录的复杂图片数据集示例",
            "version": "1.0"
        },
        "data": [
            {
                "id": 1,
                "input": "描述这张图片",
                "image": "images/cat1.jpg",
                "reference": "这是一张猫的图片"
            },
            {
                "id": 2,
                "input": "识别图片中的对象",
                "image": "images/dog1.png",
                "reference": "这是一张狗的图片"
            },
            {
                "id": 3,
                "input": "分析这张图片",
                "image": "subdir/bird1.gif",
                "reference": "这是一张鸟的图片"
            }
        ]
    }
    
    # 创建ZIP文件
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 添加JSON数据文件
        zip_file.writestr('data.json', json.dumps(dataset_data, ensure_ascii=False, indent=2))
        
        # 创建示例图片文件
        sample_images = {
            'images/cat1.jpg': '这是一个猫的JPEG图片',
            'images/dog1.png': '这是一个狗的PNG图片',
            'subdir/bird1.gif': '这是一个鸟的GIF图片'
        }
        
        for filename, content in sample_images.items():
            zip_file.writestr(filename, content)
        
        # 添加README文件
        readme_content = """# 复杂图片数据集示例

这是一个包含子目录的复杂图片数据集示例。

## 文件结构
- data.json: 数据集的JSON文件
- images/: 图片目录
  - cat1.jpg: 猫的图片
  - dog1.png: 狗的图片
- subdir/: 子目录
  - bird1.gif: 鸟的图片

## 特点
- 支持子目录结构
- JSON数据包含metadata和data字段
- 图片路径使用相对路径
"""
        zip_file.writestr('README.txt', readme_content)
    
    # 保存ZIP文件
    zip_filename = 'complex_image_dataset_example.zip'
    zip_path = os.path.join(os.path.dirname(__file__), zip_filename)
    
    with open(zip_path, 'wb') as f:
        f.write(zip_buffer.getvalue())
    
    print(f"复杂图片数据集示例已创建: {zip_path}")
    print(f"文件大小: {os.path.getsize(zip_path)} 字节")
    
    # 显示ZIP文件内容
    print("\nZIP文件内容:")
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        for file_info in zip_file.filelist:
            print(f"  {file_info.filename} ({file_info.file_size} 字节)")
    
    return zip_path

if __name__ == "__main__":
    print("创建图片数据集示例...")
    
    # 创建简单示例
    simple_example = create_image_dataset_example()
    
    print("\n" + "="*50 + "\n")
    
    # 创建复杂示例
    complex_example = create_complex_image_dataset_example()
    
    print("\n" + "="*50)
    print("示例创建完成！")
    print("可以使用这些ZIP文件测试图片数据集上传功能。")