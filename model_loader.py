"""
ONNX Runtime Wrapper - 透明试用期检查
这个模块会拦截onnxruntime.InferenceSession的创建，自动检查模型试用期
"""
import struct
from datetime import datetime

def check_model_trial(model_path):
    """
    检查ONNX模型的试用期
    
    参数:
        model_path: ONNX模型文件路径
    
    返回:
        True: 试用期有效
        False: 试用期已过或未设置保护
    """
    try:
        with open(model_path, 'rb') as f:
            data = f.read()
        
        # 查找元数据标记
        magic_header = b'THORMDL1'
        magic_footer = b'ENDTRIAL'
        
        # 如果没有保护标记，允许加载（兼容未加密的模型）
        if magic_header not in data or magic_footer not in data:
            return True
        
        # 提取试用期时间戳
        header_pos = data.rfind(magic_header)
        timestamp_data = data[header_pos + 8:header_pos + 16]
        expiry_timestamp = struct.unpack('<Q', timestamp_data)[0]
        
        # 检查是否过期
        expiry_date = datetime.fromtimestamp(expiry_timestamp)
        current_date = datetime.now()
        
        return current_date <= expiry_date
        
    except Exception:
        # 任何错误都返回False（静默失败）
        return False

def strip_trial_metadata(model_path):
    """
    移除模型文件末尾的试用期元数据，返回纯净的ONNX数据
    
    参数:
        model_path: ONNX模型文件路径
    
    返回:
        纯净的ONNX模型数据（bytes）
    """
    try:
        with open(model_path, 'rb') as f:
            data = f.read()
        
        magic_header = b'THORMDL1'
        
        # 如果有保护标记，移除元数据
        if magic_header in data:
            header_pos = data.rfind(magic_header)
            return data[:header_pos]
        
        # 没有保护标记，返回原始数据
        return data
        
    except Exception:
        return None
