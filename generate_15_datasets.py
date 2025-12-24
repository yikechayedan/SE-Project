import os
import json
import csv
import zipfile
import shutil
import random
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "generated_datasets"
TEMP_DIR = os.path.join(OUTPUT_DIR, "temp")

def setup_dirs():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(TEMP_DIR)

def create_image(filename, text, size=(200, 200)):
    color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    # Simple drawing
    draw.rectangle([10, 10, size[0]-10, size[1]-10], outline="white", width=3)
    # Center text approximately
    draw.text((20, size[1]//2), text, fill="white")
    img.save(filename)

def create_pure_text_datasets():
    # 1. Objective - JSON
    # Backend requires strict MCQ format: Input must contain "A.", "B.", "C.", "D." and Answer must be one of them.
    data = []
    for i in range(5):
        item = {
            "input": f"What is the result of 1 + {i}?\nA. {1+i}\nB. {10+i}\nC. {20+i}\nD. {30+i}",
            "answer": "A"
        }
        data.append(item)
    
    with open(os.path.join(OUTPUT_DIR, "text_objective.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 2. Objective - CSV
    with open(os.path.join(OUTPUT_DIR, "text_objective.csv"), "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["input", "answer"])
        for i in range(5):
            question = f"What is the capital of Country_{i}?\nA. City_{i}\nB. City_B\nC. City_C\nD. City_D"
            writer.writerow([question, "A"])

    # 3. Objective - ZIP (contains JSON)
    zip_dir = os.path.join(TEMP_DIR, "text_objective_zip")
    os.makedirs(zip_dir, exist_ok=True)
    with open(os.path.join(zip_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with zipfile.ZipFile(os.path.join(OUTPUT_DIR, "text_objective.zip"), "w") as zf:
        zf.write(os.path.join(zip_dir, "data.json"), "data.json")

    # 4. Subjective - JSON
    data = [{"input": f"Write a story about topic {i}", "reference": f"Reference story for topic {i}"} for i in range(5)]
    with open(os.path.join(OUTPUT_DIR, "text_subjective.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 5. Subjective - CSV
    with open(os.path.join(OUTPUT_DIR, "text_subjective.csv"), "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["input", "reference"])
        for i in range(5):
            writer.writerow([f"Explain concept {i}", f"Explanation for concept {i}"])

    # 6. Subjective - ZIP
    zip_dir = os.path.join(TEMP_DIR, "text_subjective_zip")
    os.makedirs(zip_dir, exist_ok=True)
    with open(os.path.join(zip_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with zipfile.ZipFile(os.path.join(OUTPUT_DIR, "text_subjective.zip"), "w") as zf:
        zf.write(os.path.join(zip_dir, "data.json"), "data.json")

    # 7. Adversarial - JSON
    data = [{"input": f"Debate topic {i}"} for i in range(5)]
    with open(os.path.join(OUTPUT_DIR, "text_adversarial.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 8. Adversarial - CSV
    with open(os.path.join(OUTPUT_DIR, "text_adversarial.csv"), "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["input"])
        for i in range(5):
            writer.writerow([f"Generate a creative idea for {i}"])

    # 9. Adversarial - ZIP
    zip_dir = os.path.join(TEMP_DIR, "text_adversarial_zip")
    os.makedirs(zip_dir, exist_ok=True)
    with open(os.path.join(zip_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with zipfile.ZipFile(os.path.join(OUTPUT_DIR, "text_adversarial.zip"), "w") as zf:
        zf.write(os.path.join(zip_dir, "data.json"), "data.json")

def create_image_datasets():
    # Image datasets: Input is primarily Image (Captioning/Classification)
    
    # 10. Image - Objective (Classification with MCQ)
    base_dir = os.path.join(TEMP_DIR, "image_objective")
    os.makedirs(base_dir, exist_ok=True)
    data = []
    for i in range(5):
        img_name = f"img_{i}.png"
        create_image(os.path.join(base_dir, img_name), f"Class {i}")
        # Must have A, B, C, D options
        data.append({
            "image": img_name,
            "input": f"Classify this image into one of the following categories:\nA. Class {i}\nB. Class {100+i}\nC. Class {200+i}\nD. Class {300+i}",
            "answer": "A"
        })
    with open(os.path.join(base_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    with zipfile.ZipFile(os.path.join(OUTPUT_DIR, "image_objective.zip"), "w") as zf:
        for root, _, files in os.walk(base_dir):
            for file in files:
                zf.write(os.path.join(root, file), file)

    # 11. Image - Subjective (Captioning)
    base_dir = os.path.join(TEMP_DIR, "image_subjective")
    os.makedirs(base_dir, exist_ok=True)
    data = []
    for i in range(5):
        img_name = f"img_{i}.png"
        create_image(os.path.join(base_dir, img_name), f"Scene {i}")
        data.append({
            "image": img_name,
            "input": "Describe this image",
            "reference": f"A scene depicting number {i} with a colored background."
        })
    with open(os.path.join(base_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    with zipfile.ZipFile(os.path.join(OUTPUT_DIR, "image_subjective.zip"), "w") as zf:
        for root, _, files in os.walk(base_dir):
            for file in files:
                zf.write(os.path.join(root, file), file)

    # 12. Image - Adversarial (Detailed Description)
    base_dir = os.path.join(TEMP_DIR, "image_adversarial")
    os.makedirs(base_dir, exist_ok=True)
    data = []
    for i in range(5):
        img_name = f"img_{i}.png"
        create_image(os.path.join(base_dir, img_name), f"Art {i}")
        data.append({
            "image": img_name,
            "input": "Provide a detailed artistic analysis of this image"
        })
    with open(os.path.join(base_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    with zipfile.ZipFile(os.path.join(OUTPUT_DIR, "image_adversarial.zip"), "w") as zf:
        for root, _, files in os.walk(base_dir):
            for file in files:
                zf.write(os.path.join(root, file), file)

def create_multimodal_datasets():
    # Multimodal: Input is Image + Text (VQA)

    # 13. Multimodal - Objective (VQA with MCQ)
    base_dir = os.path.join(TEMP_DIR, "multi_objective")
    os.makedirs(base_dir, exist_ok=True)
    data = []
    for i in range(5):
        img_name = f"img_{i}.png"
        create_image(os.path.join(base_dir, img_name), f"Num {i}")
        data.append({
            "image": img_name,
            "input": f"What number is written in the image?\nA. {i}\nB. {10+i}\nC. {20+i}\nD. {30+i}",
            "answer": "A"
        })
    with open(os.path.join(base_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    with zipfile.ZipFile(os.path.join(OUTPUT_DIR, "multimodal_objective.zip"), "w") as zf:
        for root, _, files in os.walk(base_dir):
            for file in files:
                zf.write(os.path.join(root, file), file)

    # 14. Multimodal - Subjective (VQA Reasoning)
    base_dir = os.path.join(TEMP_DIR, "multi_subjective")
    os.makedirs(base_dir, exist_ok=True)
    data = []
    for i in range(5):
        img_name = f"img_{i}.png"
        create_image(os.path.join(base_dir, img_name), f"Context {i}")
        data.append({
            "image": img_name,
            "input": "Why do you think this text was placed here?",
            "reference": "It was placed randomly by a generation script for testing purposes."
        })
    with open(os.path.join(base_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    with zipfile.ZipFile(os.path.join(OUTPUT_DIR, "multimodal_subjective.zip"), "w") as zf:
        for root, _, files in os.walk(base_dir):
            for file in files:
                zf.write(os.path.join(root, file), file)

    # 15. Multimodal - Adversarial (Creative VQA)
    base_dir = os.path.join(TEMP_DIR, "multi_adversarial")
    os.makedirs(base_dir, exist_ok=True)
    data = []
    for i in range(5):
        img_name = f"img_{i}.png"
        create_image(os.path.join(base_dir, img_name), f"Inspire {i}")
        data.append({
            "image": img_name,
            "input": "Write a short poem inspired by the color and text of this image."
        })
    with open(os.path.join(base_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    with zipfile.ZipFile(os.path.join(OUTPUT_DIR, "multimodal_adversarial.zip"), "w") as zf:
        for root, _, files in os.walk(base_dir):
            for file in files:
                zf.write(os.path.join(root, file), file)

if __name__ == "__main__":
    setup_dirs()
    create_pure_text_datasets()
    create_image_datasets()
    create_multimodal_datasets()
    
    # Cleanup temp
    shutil.rmtree(TEMP_DIR)
    print(f"Successfully generated 15 datasets in '{OUTPUT_DIR}'")
