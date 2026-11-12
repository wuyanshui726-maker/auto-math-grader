import requests
import json
import cv2
from PIL import Image
import io

# 测试图片路径（换成你自己的测试图片）
img_path = r"D:\oral_math_project\data\images\image_0000.jpg"

# 读取图片
with open(img_path, 'rb') as f:
    img_bytes = f.read()

# 发送请求
files = {'image': img_bytes}
response = requests.post('http://127.0.0.1:5000/detect', files=files)

# 打印结果
result = response.json()
print(f"检测到 {result['count']} 个字符")
for det in result['detections']:
    print(f"类别: {det['class']}, 置信度: {det['confidence']:.2f}, 位置: {det['bbox']}")