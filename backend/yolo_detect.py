import sys
import os
import cv2
import numpy as np

# 添加YOLOv5路径到系统路径
yolov5_path = r"D:\oral_math_project\yolov5"
if yolov5_path not in sys.path:
    sys.path.append(yolov5_path)

from models.common import DetectMultiBackend
from utils.general import non_max_suppression, scale_boxes
from utils.augmentations import letterbox

class YOLOv5Detector:
    def __init__(self, weights_path='best.pt'):
        """初始化YOLOv5模型（使用本地YOLOv5）"""
        print(f"加载模型: {weights_path}")
        
        # 使用本地YOLOv5加载模型
        self.device = 'cpu'
        self.model = DetectMultiBackend(weights_path, device=self.device)
        self.stride = self.model.stride
        self.names = self.model.names
        self.conf_thres = 0.25
        self.iou_thres = 0.45
        self.img_size = 640
        
        # 类别名称（确保和训练一致）
        self.class_names = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
                           '+', '-', '×', '÷', '=']
        
        print("模型加载完成！")
        
    def detect(self, image):
        """检测图片中的字符"""
        # 预处理图片
        img = letterbox(image, self.img_size, stride=self.stride, auto=True)[0]
        img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        img = np.ascontiguousarray(img)
        
        # 转为tensor
        import torch
        img_tensor = torch.from_numpy(img).to(self.device)
        img_tensor = img_tensor.float() / 255.0
        if img_tensor.ndimension() == 3:
            img_tensor = img_tensor.unsqueeze(0)
            
        # 推理
        pred = self.model(img_tensor)
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres)
        
        # 解析结果
        detections = []
        for det in pred:
            if len(det):
                # 缩放坐标回原图
                det[:, :4] = scale_boxes(img_tensor.shape[2:], det[:, :4], image.shape).round()
                
                for *xyxy, conf, cls in reversed(det):
                    x1, y1, x2, y2 = [int(coord) for coord in xyxy]
                    print(f"检测到类别索引: {int(cls)}")  # ← 添加这一行
                    class_name = self.class_names[int(cls)]
                    detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'class': class_name,
                        'confidence': float(conf)
                    })
                    
        return detections
    
    def detect_from_bytes(self, image_bytes):
        """从字节数据检测"""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return self.detect(img)