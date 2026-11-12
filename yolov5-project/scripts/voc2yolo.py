import os
import random
import xml.etree.ElementTree as ET
from tqdm import tqdm

# ==================== 配置参数 ====================
# 你的数据路径
project_dir = r"D:\oral_math_project"
image_dir = os.path.join(project_dir, "data", "images")
xml_dir = os.path.join(project_dir, "data", "annotations")
output_dir = os.path.join(project_dir, "data", "yolo_labels")

# 创建输出文件夹
os.makedirs(output_dir, exist_ok=True)

# 你的15个类别（和生成数据时保持一致）
classes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
           '+', '-', '×', '÷', '=']

# 数据集划分比例
train_ratio = 0.8   # 训练集80%
val_ratio = 0.2     # 验证集20%
# ==================================================

def convert_voc_to_yolo(xml_file, output_txt):
    """将单个XML文件转换为YOLO格式的TXT文件"""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # 获取图像尺寸
    size = root.find('size')
    img_width = int(size.find('width').text)
    img_height = int(size.find('height').text)
    
    with open(output_txt, 'w') as f:
        for obj in root.findall('object'):
            # 获取类别
            class_name = obj.find('name').text
            if class_name not in classes:
                continue
            class_id = classes.index(class_name)
            
            # 获取边界框坐标 (VOC格式: xmin, ymin, xmax, ymax)
            bbox = obj.find('bndbox')
            xmin = float(bbox.find('xmin').text)
            ymin = float(bbox.find('ymin').text)
            xmax = float(bbox.find('xmax').text)
            ymax = float(bbox.find('ymax').text)
            
            # 转换为YOLO格式: <class_id> <x_center> <y_center> <width> <height>
            # 坐标需要归一化到0-1之间
            x_center = (xmin + xmax) / 2.0 / img_width
            y_center = (ymin + ymax) / 2.0 / img_height
            width = (xmax - xmin) / img_width
            height = (ymax - ymin) / img_height
            
            # 写入文件
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

def main():
    # 获取所有XML文件
    xml_files = [f for f in os.listdir(xml_dir) if f.endswith('.xml')]
    xml_files.sort()  # 排序，确保顺序一致
    
    print(f"找到 {len(xml_files)} 个标注文件")
    
    # 打乱顺序并划分数据集
    random.seed(42)  # 固定随机种子，保证每次划分一致
    random.shuffle(xml_files)
    
    train_files = xml_files[:int(len(xml_files) * train_ratio)]
    val_files = xml_files[int(len(xml_files) * train_ratio):]
    
    print(f"训练集: {len(train_files)} 个文件")
    print(f"验证集: {len(val_files)} 个文件")
    
    # 转换训练集
    print("正在转换训练集...")
    train_txt_path = os.path.join(project_dir, "data", "train.txt")
    with open(train_txt_path, 'w') as train_list:
        for xml_file in tqdm(train_files):
            # 获取图片文件名（将xml后缀改为jpg）
            img_name = xml_file.replace('.xml', '.jpg')
            img_path = os.path.join(image_dir, img_name)
            
            # 写入训练集列表
            train_list.write(img_path + '\n')
            
            # 转换标注
            xml_path = os.path.join(xml_dir, xml_file)
            txt_name = xml_file.replace('.xml', '.txt')
            txt_path = os.path.join(output_dir, txt_name)
            convert_voc_to_yolo(xml_path, txt_path)
    
    # 转换验证集
    print("正在转换验证集...")
    val_txt_path = os.path.join(project_dir, "data", "val.txt")
    with open(val_txt_path, 'w') as val_list:
        for xml_file in tqdm(val_files):
            img_name = xml_file.replace('.xml', '.jpg')
            img_path = os.path.join(image_dir, img_name)
            val_list.write(img_path + '\n')
            
            xml_path = os.path.join(xml_dir, xml_file)
            txt_name = xml_file.replace('.xml', '.txt')
            txt_path = os.path.join(output_dir, txt_name)
            convert_voc_to_yolo(xml_path, txt_path)
    
    print("转换完成！")
    print(f"YOLO标签保存在: {output_dir}")
    print(f"训练集列表: {train_txt_path}")
    print(f"验证集列表: {val_txt_path}")

if __name__ == "__main__":
    main()