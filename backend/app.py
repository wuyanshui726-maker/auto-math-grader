from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from yolo_detect import YOLOv5Detector
import os

app = Flask(__name__)
CORS(app)

# 初始化检测器
print("正在初始化YOLOv5检测器...")
detector = YOLOv5Detector(weights_path='best.pt')
print("检测器初始化完成！")

@app.route('/')
def hello():
    return '口算批阅后端服务运行中 - YOLOv5已加载'

@app.route('/detect', methods=['POST'])
def detect():
    try:
        # 接收上传的图片
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': '没有上传图片'})
            
        file = request.files['image']
        image_bytes = file.read()
        
        # 执行检测
        detections = detector.detect_from_bytes(image_bytes)
        
        # 返回结果
        return jsonify({
            'success': True,
            'detections': detections,
            'count': len(detections)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/detect_url', methods=['POST'])
def detect_url():
    """通过图片URL检测（可选功能）"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        # TODO: 从URL下载图片
        # 这里简单起见先返回提示
        return jsonify({
            'success': False,
            'error': 'URL检测功能待实现'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)