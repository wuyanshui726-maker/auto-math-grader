import os
import random
import shutil

# 配置路径
image_dir = "images"
label_dir = "labels"
train_img_dir = "train/images"
val_img_dir = "val/images"
train_label_dir = "train/labels"
val_label_dir = "val/labels"

# 创建文件夹
os.makedirs(train_img_dir, exist_ok=True)
os.makedirs(val_img_dir, exist_ok=True)
os.makedirs(train_label_dir, exist_ok=True)
os.makedirs(val_label_dir, exist_ok=True)

# 获取所有图片
images = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
images.sort()
random.seed(42)
random.shuffle(images)

# 80%训练，20%验证
split_idx = int(len(images) * 0.8)
train_images = images[:split_idx]
val_images = images[split_idx:]

print(f"总图片数: {len(images)}")
print(f"训练集: {len(train_images)}张")
print(f"验证集: {len(val_images)}张")

# 复制训练集
for img in train_images:
    base_name = os.path.splitext(img)[0]
    # 复制图片
    shutil.copy(os.path.join(image_dir, img), os.path.join(train_img_dir, img))
    # 复制标注
    txt_file = base_name + '.txt'
    if os.path.exists(os.path.join(label_dir, txt_file)):
        shutil.copy(os.path.join(label_dir, txt_file), os.path.join(train_label_dir, txt_file))
    else:
        print(f"警告: 找不到标注文件 {txt_file}")

# 复制验证集
for img in val_images:
    base_name = os.path.splitext(img)[0]
    shutil.copy(os.path.join(image_dir, img), os.path.join(val_img_dir, img))
    txt_file = base_name + '.txt'
    if os.path.exists(os.path.join(label_dir, txt_file)):
        shutil.copy(os.path.join(label_dir, txt_file), os.path.join(val_label_dir, txt_file))
    else:
        print(f"警告: 找不到标注文件 {txt_file}")

print("数据集划分完成！")