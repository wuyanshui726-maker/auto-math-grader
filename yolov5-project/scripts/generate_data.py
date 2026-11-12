import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
import random
import xml.etree.ElementTree as ET
from xml.dom import minidom

# 配置参数
OUTPUT_DIR = r"D:\oral_math_project\data"
IMAGE_SIZE = (800, 600)  # 图像大小
FONT_SIZE = 40  # 字体大小
NUM_IMAGES = 100  # 生成图像数量

# 类别列表（15类）
CLASSES = ['0','1','2','3','4','5','6','7','8','9','+','-','×','÷','=']
CLASS_TO_ID = {cls:i for i, cls in enumerate(CLASSES)}

def create_dir(path):
    """创建目录"""
    if not os.path.exists(path):
        os.makedirs(path)

def draw_text(draw, text, position, font):
    """绘制文本"""
    draw.text(position, text, font=font, fill=(0,0,0))

def get_text_size(text, font):
    """获取文本尺寸"""
    img = Image.new('RGB', (1,1))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0,0), text, font=font)
    return bbox[2]-bbox[0], bbox[3]-bbox[1]

def generate_arithmetic():
    """生成一个算术题"""
    operators = ['+', '-', '×', '÷']
    op = random.choice(operators)
    
    if op == '+':
        a = random.randint(1, 50)
        b = random.randint(1, 50)
        result = a + b
    elif op == '-':
        a = random.randint(10, 50)
        b = random.randint(1, a)
        result = a - b
    elif op == '×':
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        result = a * b
    else:  # ÷
        b = random.randint(1, 10)
        result = random.randint(1, 10)
        a = b * result
    
    # 题目部分：a op b = （答案留空）
    question = f"{a}{op}{b}="
    # 答案部分：手写数字（这里用印刷体模拟，实际应用时可用MNIST）
    answer = str(result)
    
    return question, answer, op

def generate_one_image(idx):
    """生成一张图像"""
    # 创建白色背景
    img = Image.new('RGB', IMAGE_SIZE, (255,255,255))
    draw = ImageDraw.Draw(img)
    
    # 加载字体（如果没有SimHei，尝试其他字体）
    try:
        font = ImageFont.truetype("simhei.ttf", FONT_SIZE)
    except:
        font = ImageFont.load_default()
    
    # 生成3-6个算式
    num_questions = random.randint(3, 6)
    questions_data = []
    
    y_start = 50
    line_height = FONT_SIZE + 20
    
    for i in range(num_questions):
        question, answer, op = generate_arithmetic()
        
        # 随机x位置（避免重叠）
        x = random.randint(50, IMAGE_SIZE[0] - 300)
        y = y_start + i * line_height + random.randint(-5, 5)
        
        # 绘制题目（印刷体）
        draw_text(draw, question, (x, y), font)
        
        # 计算题目框位置（用于标注）
        q_width, q_height = get_text_size(question, font)
        
        # 记录每个字符的位置（用于标注）
        char_x = x
        for char in question:
            char_width, _ = get_text_size(char, font)
            char_bbox = [char_x, y, char_x + char_width, y + q_height]
            questions_data.append({
                'char': char,
                'bbox': char_bbox,
                'type': 'printed'
            })
            char_x += char_width
        
        # 绘制答案（用印刷体模拟手写，实际应用时可从MNIST粘贴）
        answer_x = x + q_width + 10
        # 随机旋转一点模拟手写
        answer_img = Image.new('RGBA', (100, 60), (255,255,255,0))
        answer_draw = ImageDraw.Draw(answer_img)
        answer_draw.text((10, 10), answer, font=font, fill=(0,0,0))
        answer_img = answer_img.rotate(random.uniform(-5,5), expand=1)
        
        # 粘贴到原图
        img.paste(answer_img, (answer_x, y), answer_img)
        
        # 记录答案字符位置
        for j, char in enumerate(answer):
            char_width, _ = get_text_size(char, font)
            char_bbox = [answer_x + j*char_width, y, 
                        answer_x + (j+1)*char_width, y + q_height]
            questions_data.append({
                'char': char,
                'bbox': char_bbox,
                'type': 'handwritten'
            })
    
    return img, questions_data

def save_voc_xml(annotations, img_filename, img_size, xml_path):
    """保存为VOC格式的XML标注"""
    root = ET.Element("annotation")
    
    # 文件夹
    folder = ET.SubElement(root, "folder")
    folder.text = "oral_math"
    
    # 文件名
    filename = ET.SubElement(root, "filename")
    filename.text = img_filename
    
    # 路径
    path = ET.SubElement(root, "path")
    path.text = os.path.join(OUTPUT_DIR, "images", img_filename)
    
    # 图像尺寸
    size = ET.SubElement(root, "size")
    width = ET.SubElement(size, "width")
    width.text = str(img_size[0])
    height = ET.SubElement(size, "height")
    height.text = str(img_size[1])
    depth = ET.SubElement(size, "depth")
    depth.text = "3"
    
    # 每个目标的标注
    for ann in annotations:
        obj = ET.SubElement(root, "object")
        name = ET.SubElement(obj, "name")
        name.text = ann['char']
        pose = ET.SubElement(obj, "pose")
        pose.text = "Unspecified"
        truncated = ET.SubElement(obj, "truncated")
        truncated.text = "0"
        difficult = ET.SubElement(obj, "difficult")
        difficult.text = "0"
        
        bndbox = ET.SubElement(obj, "bndbox")
        xmin = ET.SubElement(bndbox, "xmin")
        xmin.text = str(int(ann['bbox'][0]))
        ymin = ET.SubElement(bndbox, "ymin")
        ymin.text = str(int(ann['bbox'][1]))
        xmax = ET.SubElement(bndbox, "xmax")
        xmax.text = str(int(ann['bbox'][2]))
        ymax = ET.SubElement(bndbox, "ymax")
        ymax.text = str(int(ann['bbox'][3]))
    
    # 格式化输出
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_str)

def main():
    # 创建输出目录
    images_dir = os.path.join(OUTPUT_DIR, "images")
    annotations_dir = os.path.join(OUTPUT_DIR, "annotations")
    create_dir(images_dir)
    create_dir(annotations_dir)
    
    for i in range(NUM_IMAGES):
        # 生成图像
        img, questions_data = generate_one_image(i)
        
        # 保存图像
        img_filename = f"image_{i:04d}.jpg"
        img_path = os.path.join(images_dir, img_filename)
        img.save(img_path, "JPEG")
        
        # 准备标注
        annotations = []
        for data in questions_data:
            annotations.append({
                'char': data['char'],
                'bbox': data['bbox']
            })
        
        # 保存XML标注
        xml_filename = f"image_{i:04d}.xml"
        xml_path = os.path.join(annotations_dir, xml_filename)
        save_voc_xml(annotations, img_filename, IMAGE_SIZE, xml_path)
        
        if (i+1) % 10 == 0:
            print(f"已生成 {i+1}/{NUM_IMAGES} 张图像")
    
    print("数据生成完成！")

if __name__ == "__main__":
    main()