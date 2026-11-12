import os
import shutil
import random

# 配置路径
image_dir = r"D:\oral_math_project\handwritten_data\images"
label_dir = r"D:\oral_math_project\handwritten_data\labels"
output_dir = r"D:\oral_math_project\handwritten_data\yolo_format"

# 创建输出目录
os.makedirs(os.path.join(output_dir, "images", "train"), exist_ok=True)
os.makedirs(os.path.join(output_dir, "images", "val"), exist_ok=True)
os.makedirs(os.path.join(output_dir, "labels", "train"), exist_ok=True)
os.makedirs(os.path.join(output_dir, "labels", "val"), exist_ok=True)

# 获取所有图片文件
images = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
images.sort()
print(f"找到 {len(images)} 张图片")

# 打乱顺序
random.seed(42)
random.shuffle(images)

# 划分训练集和验证集 (80% 训练, 20% 验证)
split_idx = int(len(images) * 0.8)
train_images = images[:split_idx]
val_images = images[split_idx:]

print(f"训练集: {len(train_images)} 张")
print(f"验证集: {len(val_images)} 张")

# 复制训练集
for img in train_images:
    # 复制图片
    src_img = os.path.join(image_dir, img)
    dst_img = os.path.join(output_dir, "images", "train", img)
    shutil.copy(src_img, dst_img)
    
    # 复制对应的标签文件
    label_name = img.replace('.png', '.txt').replace('.jpg', '.txt').replace('.jpeg', '.txt')
    src_label = os.path.join(label_dir, label_name)
    dst_label = os.path.join(output_dir, "labels", "train", label_name)
    if os.path.exists(src_label):
        shutil.copy(src_label, dst_label)
    else:
        print(f"警告: 找不到标签文件 {label_name}")

# 复制验证集
for img in val_images:
    src_img = os.path.join(image_dir, img)
    dst_img = os.path.join(output_dir, "images", "val", img)
    shutil.copy(src_img, dst_img)
    
    label_name = img.replace('.png', '.txt').replace('.jpg', '.txt').replace('.jpeg', '.txt')
    src_label = os.path.join(label_dir, label_name)
    dst_label = os.path.join(output_dir, "labels", "val", label_name)
    if os.path.exists(src_label):
        shutil.copy(src_label, dst_label)

print("转换完成！")
print(f"YOLO格式数据保存在: {output_dir}")