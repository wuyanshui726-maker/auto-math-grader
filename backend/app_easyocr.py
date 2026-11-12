from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import cv2
import numpy as np
import re

app = Flask(__name__)
CORS(app)

print("正在初始化 EasyOCR...")
reader = easyocr.Reader(['en'], gpu=False)
print("EasyOCR 初始化完成！")

@app.route('/')
def hello():
    return '口算批阅后端服务运行中 (EasyOCR版本)'

def clean_text(text):
    """清理识别文本"""
    text = text.replace('I', '1').replace('l', '1')
    text = text.replace('|', '1').replace('!', '1')
    text = text.replace('O', '0').replace('o', '0')
    text = text.replace('S', '5').replace('s', '5')
    text = text.replace('Z', '2').replace('z', '2')
    text = text.replace('×', 'x').replace('*', 'x')
    text = text.replace('÷', '/').replace(':', '/')
    text = text.replace('=', '=').replace('＝', '=')
    # 修复常见误识别
    text = text.replace('/2', '12')
    text = text.replace('//', '=')
    text = text.replace(' ', '')
    return text

def extract_arithmetic_from_line(line):
    """从单行中提取算式"""
    pattern = r'(\d+)([+\-x/])(\d+)=(\d+)'
    matches = re.findall(pattern, line)
    return matches

@app.route('/detect', methods=['POST'])
def detect():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': '没有上传图片'})
        
        file = request.files['image']
        img_bytes = file.read()
        
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        result = reader.readtext(img, detail=0)
        
        print(f"原始识别: {result}")
        
        cleaned_lines = []
        for line in result:
            cleaned = clean_text(line)
            if cleaned:
                cleaned_lines.append(cleaned)
        
        print(f"清理后: {cleaned_lines}")
        
        questions = []
        
        # 合并相邻行成完整算式
        i = 0
        while i < len(cleaned_lines):
            line = cleaned_lines[i]
            
            # 如果当前行包含等号但不包含答案
            if '=' in line and not re.search(r'=\d+', line):
                if i + 1 < len(cleaned_lines):
                    next_line = cleaned_lines[i + 1]
                    if next_line.isdigit():
                        full_formula = line + next_line
                        matches = extract_arithmetic_from_line(full_formula)
                        if matches:
                            for match in matches:
                                questions.append(parse_match(match))
                            i += 2
                            continue
            
            # 当前行本身是完整算式
            matches = extract_arithmetic_from_line(line)
            if matches:
                for match in matches:
                    questions.append(parse_match(match))
                i += 1
                continue
            
            i += 1
        
        # 备用方案：合并所有行
        if len(questions) == 0:
            full_text = ''.join(cleaned_lines)
            matches = extract_arithmetic_from_line(full_text)
            for match in matches:
                questions.append(parse_match(match))
        
        for q in questions:
            print(f"算式: {q['num1']}{q['operator']}{q['num2']}={q['answer']} -> {q['isCorrect']}")
        
        return jsonify({
            'success': True,
            'full_text': ' '.join(cleaned_lines),
            'lines': cleaned_lines,
            'questions': questions,
            'count': len(questions)
        })
        
    except Exception as e:
        print(f"错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

def parse_match(match):
    num1, operator, num2, answer = match
    n1 = int(num1)
    n2 = int(num2)
    ans = int(answer)
    
    if operator == 'x':
        operator = '×'
    elif operator == '/':
        operator = '÷'
    
    if operator == '+':
        correct = n1 + n2
    elif operator == '-':
        correct = n1 - n2
    elif operator == '×':
        correct = n1 * n2
    elif operator == '÷':
        correct = n1 / n2 if n2 != 0 else None
    else:
        correct = None
    
    is_correct = (correct == ans)
    
    return {
        'num1': num1,
        'operator': operator,
        'num2': num2,
        'answer': answer,
        'correct': correct,
        'isCorrect': is_correct
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
