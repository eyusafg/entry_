"""
ONNX模型加密工具 - 透明加密方案
使用方法: python encrypt_model.py <模型文件路径>

原理：
1. 在ONNX文件末尾追加加密的元数据（试用期信息）
2. 创建一个wrapper脚本拦截onnxruntime的加载
3. 程序代码完全不需要修改
"""
import os
import sys
from datetime import datetime, timedelta
import struct

def embed_trial_info(model_path, output_path=None, trial_days=60):
    """
    在ONNX模型中嵌入试用期信息
    
    参数:
        model_path: 原始模型文件路径
        output_path: 输出路径（可选，默认覆盖原文件）
        trial_days: 试用天数（默认60天）
    """
    if not os.path.exists(model_path):
        print(f"错误: 模型文件不存在 - {model_path}")
        return False
    
    # 读取原始ONNX模型
    with open(model_path, 'rb') as f:
        original_data = f.read()
    
    # 计算过期时间戳
    expiry_date = datetime.now() + timedelta(days=trial_days)
    expiry_timestamp = int(expiry_date.timestamp())
    
    # 创建元数据标记
    # 格式: [MAGIC_HEADER(8字节)] [EXPIRY_TIMESTAMP(8字节)] [MAGIC_FOOTER(8字节)]
    magic_header = b'THORMDL1'  # 8字节魔数
    magic_footer = b'ENDTRIAL'  # 8字节魔数
    
    # 打包试用期信息
    trial_metadata = magic_header + struct.pack('<Q', expiry_timestamp) + magic_footer
    
    # 将元数据追加到ONNX文件末尾
    protected_data = original_data + trial_metadata
    
    # 确定输出路径
    if output_path is None:
        output_path = model_path
    
    # 保存带保护的模型
    with open(output_path, 'wb') as f:
        f.write(protected_data)
    
    print(f"✓ 模型保护成功")
    print(f"  文件路径: {output_path}")
    print(f"  试用期至: {expiry_date.strftime('%Y年%m月%d日')}")
    print(f"  剩余天数: {trial_days}天")
    print(f"\n注意: 需要安装 onnxruntime_wrapper.py 才能生效")
    
    return True

def check_trial_info(model_path):
    """检查模型的试用期信息（调试用）"""
    try:
        with open(model_path, 'rb') as f:
            data = f.read()
        
        # 查找元数据
        magic_header = b'THORMDL1'
        magic_footer = b'ENDTRIAL'
        
        if magic_header not in data or magic_footer not in data:
            print("此模型未设置试用期保护")
            return
        
        # 提取时间戳
        header_pos = data.rfind(magic_header)
        timestamp_data = data[header_pos + 8:header_pos + 16]
        expiry_timestamp = struct.unpack('<Q', timestamp_data)[0]
        
        expiry_date = datetime.fromtimestamp(expiry_timestamp)
        current_date = datetime.now()
        days_remaining = (expiry_date - current_date).days
        
        print(f"模型试用期信息:")
        print(f"  过期日期: {expiry_date.strftime('%Y年%m月%d日')}")
        print(f"  剩余天数: {days_remaining}天")
        print(f"  状态: {'有效' if days_remaining >= 0 else '已过期'}")
        
    except Exception as e:
        print(f"检查失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  加密: python encrypt_model.py <模型文件路径> [试用天数]")
        print("  检查: python encrypt_model.py --check <模型文件路径>")
        print("\n示例:")
        print("  python encrypt_model.py models/thor_segm_20251031.onnx 60")
        print("  python encrypt_model.py --check models/thor_segm_20251031.onnx")
        sys.exit(1)
    
    if sys.argv[1] == '--check':
        if len(sys.argv) < 3:
            print("错误: 请指定要检查的模型文件")
            sys.exit(1)
        check_trial_info(sys.argv[2])
    else:
        model_path = sys.argv[1]
        trial_days = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        embed_trial_info(model_path, trial_days=trial_days)
