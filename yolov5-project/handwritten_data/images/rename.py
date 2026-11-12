import os

# 获取所有图片文件
files = [f for f in os.listdir('.') if f.endswith(('.png', '.jpg', '.jpeg'))]
files.sort()  # 按名称排序

# 重命名
for i, filename in enumerate(files, 1):
    # 获取文件扩展名
    ext = filename.split('.')[-1]
    # 新文件名：hw_001.png, hw_002.png ...
    new_name = f"hw_{i:03d}.{ext}"
    os.rename(filename, new_name)
    print(f"{filename} → {new_name}")

print("重命名完成！")