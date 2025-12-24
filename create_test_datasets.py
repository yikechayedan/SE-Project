import os
import json
import zipfile
from PIL import Image, ImageDraw, ImageFont
import random

# 创建一些示例图片
def create_sample_image(text, filename, size=(400, 300), color=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))):
    """创建一个包含文本的示例图片"""
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    
    # 尝试使用默认字体
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # 计算文本位置以居中显示
    text_width, text_height = draw.textsize(text, font=font)
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    draw.text(position, text, fill="white", font=font)
    img.save(filename)
    return filename

# 创建主观测评ZIP数据集
def create_subjective_zip():
    """创建主观测评ZIP数据集"""
    # 创建图片目录
    img_dir = "temp_datasets/subjective_images"
    os.makedirs(img_dir, exist_ok=True)
    
    # 创建示例图片
    images = []
    for i in range(1, 6):
        img_path = os.path.join(img_dir, f"subjective_image_{i}.jpg")
        create_sample_image(f"主观测评图片 {i}", img_path)
        images.append(f"subjective_image_{i}.jpg")
    
    # 创建JSON数据文件
    data = []
    for i, img in enumerate(images, 1):
        item = {
            "id": i,
            "input": f"请描述图片 {img} 中的内容和场景",
            "image": img,
            "reference": f"这是第{i}张主观测评图片，包含了简单的图形和文字内容"
        }
        data.append(item)
    
    json_path = os.path.join(img_dir, "data.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 创建ZIP文件
    with zipfile.ZipFile("subjective_test_dataset.zip", 'w') as zipf:
        for root, dirs, files in os.walk(img_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, img_dir)
                zipf.write(file_path, arcname)
    
    print("主观测评ZIP数据集已创建: subjective_test_dataset.zip")

# 创建客观测评ZIP数据集
def create_objective_zip():
    """创建客观测评ZIP数据集"""
    # 创建图片目录
    img_dir = "temp_datasets/objective_images"
    os.makedirs(img_dir, exist_ok=True)
    
    # 创建示例图片
    images = []
    categories = ["猫", "狗", "鸟", "鱼", "花"]
    for i, category in enumerate(categories, 1):
        img_path = os.path.join(img_dir, f"objective_image_{i}.jpg")
        create_sample_image(category, img_path)
        images.append((f"objective_image_{i}.jpg", category))
    
    # 创建JSON数据文件
    data = []
    for i, (img, answer) in enumerate(images, 1):
        item = {
            "id": i,
            "input": "图片分类",
            "image": img,
            "answer": answer
        }
        data.append(item)
    
    json_path = os.path.join(img_dir, "data.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 创建ZIP文件
    with zipfile.ZipFile("objective_test_dataset.zip", 'w') as zipf:
        for root, dirs, files in os.walk(img_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, img_dir)
                zipf.write(file_path, arcname)
    
    print("客观测评ZIP数据集已创建: objective_test_dataset.zip")

# 创建对抗测评ZIP数据集
def create_adversarial_zip():
    """创建对抗测评ZIP数据集"""
    # 创建图片目录
    img_dir = "temp_datasets/adversarial_images"
    os.makedirs(img_dir, exist_ok=True)
    
    # 创建示例图片
    images = []
    questions = [
        "这张图片有什么异常？",
        "识别这张图片中的主要对象",
        "这张图片可能代表什么含义？",
        "分析这张图片的视觉特征",
        "这张图片适合用在什么场景？"
    ]
    
    for i, question in enumerate(questions, 1):
        img_path = os.path.join(img_dir, f"adversarial_image_{i}.jpg")
        create_sample_image(f"对抗图片 {i}", img_path, color=(random.randint(50, 150), random.randint(50, 150), random.randint(50, 150)))
        images.append((f"adversarial_image_{i}.jpg", question))
    
    # 创建JSON数据文件
    data = []
    for i, (img, question) in enumerate(images, 1):
        item = {
            "id": i,
            "input": question,
            "image": img
        }
        data.append(item)
    
    json_path = os.path.join(img_dir, "data.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 创建ZIP文件
    with zipfile.ZipFile("adversarial_test_dataset.zip", 'w') as zipf:
        for root, dirs, files in os.walk(img_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, img_dir)
                zipf.write(file_path, arcname)
    
    print("对抗测评ZIP数据集已创建: adversarial_test_dataset.zip")

if __name__ == "__main__":
    print("开始创建测试数据集...")
    
    try:
        create_subjective_zip()
        create_objective_zip()
        create_adversarial_zip()
        print("\n所有数据集创建完成！")
    except Exception as e:
        print(f"创建数据集时出错: {e}")