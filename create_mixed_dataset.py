import json
from PIL import Image, ImageDraw

# 1. Generate Images
def create_shape(filename, shape, color):
    img = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    if shape == 'circle':
        draw.ellipse([50, 50, 150, 150], fill=color, outline='black')
    elif shape == 'square':
        draw.rectangle([50, 50, 150, 150], fill=color, outline='black')
    elif shape == 'triangle':
        draw.polygon([(100, 50), (50, 150), (150, 150)], fill=color, outline='black')
        
    img.save(f"temp_dataset/images/{filename}")

create_shape('circle.png', 'circle', 'red')
create_shape('square.png', 'square', 'blue')
create_shape('triangle.png', 'triangle', 'green')

# 2. Create data.json
data = [
    {
        "input": "What color is the shape in the image?\nA. Blue\nB. Red\nC. Green\nD. Yellow",
        "image": "images/circle.png",
        "answer": "B"
    },
    {
        "input": "Which planet is known as the Red Planet?\nA. Mars\nB. Venus\nC. Jupiter\nD. Saturn",
        "answer": "A"
    },
    {
        "input": "What shape is shown in the image?\nA. Circle\nB. Square\nC. Triangle\nD. Rectangle",
        "image": "images/square.png",
        "answer": "B"
    },
    {
        "input": "What is the result of 2 + 2?\nA. 3\nB. 4\nC. 5\nD. 6",
        "answer": "B"
    },
    {
        "input": "How many corners does the shape in the image have?\nA. 3\nB. 4\nC. 5\nD. 0",
        "image": "images/triangle.png",
        "answer": "A"
    }
]

with open('temp_dataset/data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
