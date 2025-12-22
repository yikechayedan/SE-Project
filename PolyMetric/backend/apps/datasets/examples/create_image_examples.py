#!/usr/bin/env python
"""
创建包含图像的数据集样例
"""
import os
import json
import zipfile
from io import BytesIO

def create_simple_image_dataset():
    """创建简单的图像数据集样例"""
    dataset_data = [
        {
            "id": 1,
            "input": "请描述这张图片",
            "image": "image1.jpg",
            "reference": "这是一张展示自然风景的图片"
        },
        {
            "id": 2,
            "input": "这张图片中有什么动物？",
            "image": "image2.jpg",
            "reference": "图片中有一只猫在草地上"
        },
        {
            "id": 3,
            "input": "分析这张图片的色彩构成",
            "image": "image3.jpg",
            "reference": "这是一张色彩丰富的日落照片"
        }
    ]
    
    # 创建示例图片（简单的占位符）
    image1_data = b"fake_image_data_1"
    image2_data = b"fake_image_data_2"
    image3_data = b"fake_image_data_3"
    
    # 创建ZIP文件
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 添加JSON数据文件
        zip_file.writestr('data.json', json.dumps(dataset_data, ensure_ascii=False, indent=2))
        
        # 添加图片文件
        zip_file.writestr('image1.jpg', image1_data)
        zip_file.writestr('image2.jpg', image2_data)
        zip_file.writestr('image3.jpg', image3_data)
        
        # 添加README文件
        readme_content = """# 简单图像数据集样例

这是一个简单的图像数据集样例，用于测试图像上传功能。

## 文件结构
- data.json: 数据集的JSON文件，包含样本数据和图片引用
- image1.jpg: 示例图片1
- image2.jpg: 示例图片2
- image3.jpg: 示例图片3

## 数据格式
每个数据项包含：
- id: 唯一标识符
- input: 问题或指令
- image: 引用的图片文件名
- reference: 期望的答案或描述

## 使用方法
1. 将此ZIP文件上传到PolyMetric平台
2. 选择"图像"类别
3. 选择适当的测评类型（主观/客观/对抗）
4. 系统会自动识别图片数量和样本数量
"""
        zip_file.writestr('README.txt', readme_content)
    
    # 保存ZIP文件
    zip_filename = 'simple_image_dataset_example.zip'
    zip_path = os.path.join(os.path.dirname(__file__), zip_filename)
    
    with open(zip_path, 'wb') as f:
        f.write(zip_buffer.getvalue())
    
    print(f"简单图像数据集样例已创建: {zip_path}")
    print(f"文件大小: {os.path.getsize(zip_path)} 字节")
    
    return zip_path

def create_complex_image_dataset():
    """创建复杂的图像数据集样例（包含子目录）"""
    dataset_data = {
        "metadata": {
            "name": "复杂图像数据集样例",
            "description": "这是一个包含子目录的复杂图像数据集样例",
            "version": "1.0",
            "author": "PolyMetric Team"
        },
        "data": [
            {
                "id": 1,
                "input": "识别图片中的主要对象",
                "image": "images/cat1.jpg",
                "reference": "图片中有一只猫坐在沙发上"
            },
            {
                "id": 2,
                "input": "描述图片中的场景",
                "image": "images/landscape/nature1.jpg",
                "reference": "这是一张自然风景照片，有山脉和湖泊"
            },
            {
                "id": 3,
                "input": "分析图片的构图",
                "image": "images/portrait/person1.jpg",
                "reference": "这是一张人物肖像照片，采用三分法构图"
            },
            {
                "id": 4,
                "input": "检测图片中的文字",
                "image": "documents/sign1.png",
                "reference": "图片中包含'欢迎'文字"
            }
        ]
    }
    
    # 创建示例图片（简单的占位符）
    images_data = {
        'images/cat1.jpg': b"fake_cat_image_data",
        'images/landscape/nature1.jpg': b"fake_landscape_image_data",
        'images/portrait/person1.jpg': b"fake_portrait_image_data",
        'documents/sign1.png': b"fake_sign_image_data"
    }
    
    # 创建ZIP文件
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 添加JSON数据文件
        zip_file.writestr('data.json', json.dumps(dataset_data, ensure_ascii=False, indent=2))
        
        # 添加图片文件
        for filename, data in images_data.items():
            zip_file.writestr(filename, data)
        
        # 添加README文件
        readme_content = """# 复杂图像数据集样例

这是一个包含子目录的复杂图像数据集样例，用于测试图像上传功能。

## 文件结构
- data.json: 数据集的JSON文件，包含元数据和样本数据
- images/: 图片目录
  - cat1.jpg: 猫的图片
- images/landscape/: 风景图片目录
  - nature1.jpg: 自然风景图片
- images/portrait/: 人物图片目录
  - person1.jpg: 人物肖像图片
- documents/: 文档目录
  - sign1.png: 标志图片

## 数据格式
JSON文件包含：
- metadata: 数据集元信息
- data: 实际数据数组

每个数据项包含：
- id: 唯一标识符
- input: 问题或指令
- image: 引用的图片文件名（使用相对路径）
- reference: 期望的答案或描述

## 特点
- 支持子目录结构
- JSON包含metadata和data字段
- 图片路径使用相对路径
- 适用于复杂的数据集组织

## 使用方法
1. 将此ZIP文件上传到PolyMetric平台
2. 选择"图像"类别
3. 选择适当的测评类型（主观/客观/对抗）
4. 系统会自动识别图片数量和样本数量
5. 支持复杂的目录结构
"""
        zip_file.writestr('README.txt', readme_content)
    
    # 保存ZIP文件
    zip_filename = 'complex_image_dataset_example.zip'
    zip_path = os.path.join(os.path.dirname(__file__), zip_filename)
    
    with open(zip_path, 'wb') as f:
        f.write(zip_buffer.getvalue())
    
    print(f"复杂图像数据集样例已创建: {zip_path}")
    print(f"文件大小: {os.path.getsize(zip_path)} 字节")
    
    return zip_path

def create_objective_image_dataset():
    """创建客观测评的图像数据集样例"""
    dataset_data = [
        {
            "id": 1,
            "input": "这张图片中的数字是多少？",
            "image": "numbers/number1.jpg",
            "answer": "42"
        },
        {
            "id": 2,
            "input": "计算图片中几何图形的面积",
            "image": "shapes/geometry1.png",
            "answer": "64平方厘米"
        },
        {
            "id": 3,
            "input": "识别图片中的颜色",
            "image": "colors/color1.jpg",
            "answer": "红色、绿色和蓝色"
        }
    ]
    
    # 创建示例图片
    images_data = {
        'numbers/number1.jpg': b"fake_number_image_data",
        'shapes/geometry1.png': b"fake_geometry_image_data",
        'colors/color1.jpg': b"fake_color_image_data"
    }
    
    # 创建ZIP文件
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 添加JSON数据文件
        zip_file.writestr('data.json', json.dumps(dataset_data, ensure_ascii=False, indent=2))
        
        # 添加图片文件
        for filename, data in images_data.items():
            zip_file.writestr(filename, data)
        
        # 添加README文件
        readme_content = """# 客观测评图像数据集样例

这是一个用于客观测评的图像数据集样例。

## 数据格式
每个数据项包含：
- id: 唯一标识符
- input: 问题或指令
- image: 引用的图片文件名
- answer: 正确答案（客观测评必需）

## 特点
- 适用于客观测评场景
- 包含明确的问题和答案
- 支持子目录结构
"""
        zip_file.writestr('README.txt', readme_content)
    
    # 保存ZIP文件
    zip_filename = 'objective_image_dataset_example.zip'
    zip_path = os.path.join(os.path.dirname(__file__), zip_filename)
    
    with open(zip_path, 'wb') as f:
        f.write(zip_buffer.getvalue())
    
    print(f"客观测评图像数据集样例已创建: {zip_path}")
    print(f"文件大小: {os.path.getsize(zip_path)} 字节")
    
    return zip_path

def create_adversarial_image_dataset():
    """创建对抗测评的图像数据集样例"""
    dataset_data = [
        {
            "id": 1,
            "input": "请分析这张图片",
            "image": "adversarial/image1.jpg"
        },
        {
            "id": 2,
            "input": "识别图片中的异常",
            "image": "adversarial/anomaly1.png"
        },
        {
            "id": 3,
            "input": "检测图片中的对抗性攻击",
            "image": "adversarial/attack1.jpg"
        }
    ]
    
    # 创建示例图片
    images_data = {
        'adversarial/image1.jpg': b"fake_adversarial_image_data",
        'adversarial/anomaly1.png': b"fake_anomaly_image_data",
        'adversarial/attack1.jpg': b"fake_attack_image_data"
    }
    
    # 创建ZIP文件
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 添加JSON数据文件
        zip_file.writestr('data.json', json.dumps(dataset_data, ensure_ascii=False, indent=2))
        
        # 添加图片文件
        for filename, data in images_data.items():
            zip_file.writestr(filename, data)
        
        # 添加README文件
        readme_content = """# 对抗测评图像数据集样例

这是一个用于对抗测评的图像数据集样例。

## 数据格式
每个数据项包含：
- id: 唯一标识符
- input: 问题或指令（对抗测评通常只需要input）

## 特点
- 适用于对抗测评场景
- 只需要input字段，不需要reference或answer
- 支持子目录结构
"""
        zip_file.writestr('README.txt', readme_content)
    
    # 保存ZIP文件
    zip_filename = 'adversarial_image_dataset_example.zip'
    zip_path = os.path.join(os.path.dirname(__file__), zip_filename)
    
    with open(zip_path, 'wb') as f:
        f.write(zip_buffer.getvalue())
    
    print(f"对抗测评图像数据集样例已创建: {zip_path}")
    print(f"文件大小: {os.path.getsize(zip_path)} 字节")
    
    return zip_path

if __name__ == "__main__":
    print("开始创建图像数据集样例...\n")
    
    # 创建简单样例
    simple_example = create_simple_image_dataset()
    
    print("\n" + "="*50 + "\n")
    
    # 创建复杂样例
    complex_example = create_complex_image_dataset()
    
    print("\n" + "="*50 + "\n")
    
    # 创建客观测评样例
    objective_example = create_objective_image_dataset()
    
    print("\n" + "="*50 + "\n")
    
    # 创建对抗测评样例
    adversarial_example = create_adversarial_image_dataset()
    
    print("\n" + "="*50)
    print("所有图像数据集样例创建完成！")
    print("\n样例文件列表：")
    print(f"1. {simple_example}")
    print(f"2. {complex_example}")
    print(f"3. {objective_example}")
    print(f"4. {adversarial_example}")