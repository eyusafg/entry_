"""
调试加密模型
"""
import struct

def debug_encrypted_model(model_path):
    """检查加密模型的结构"""
    with open(model_path, 'rb') as f:
        data = f.read()
    
    print(f"文件总大小: {len(data)} 字节")
    
    # 查找元数据标记
    magic_header = b'THORMDL1'
    magic_footer = b'ENDTRIAL'
    
    if magic_header in data:
        header_pos = data.rfind(magic_header)
        print(f"找到加密标记位置: {header_pos}")
        print(f"原始ONNX大小: {header_pos} 字节")
        
        # 检查元数据
        metadata = data[header_pos:]
        print(f"元数据大小: {len(metadata)} 字节")
        print(f"元数据内容: {metadata}")
        
        if magic_footer in metadata:
            print("✓ 元数据结构完整")
            
            # 提取时间戳
            timestamp_data = data[header_pos + 8:header_pos + 16]
            expiry_timestamp = struct.unpack('<Q', timestamp_data)[0]
            from datetime import datetime
            expiry_date = datetime.fromtimestamp(expiry_timestamp)
            print(f"过期日期: {expiry_date}")
        else:
            print("✗ 元数据结构不完整")
        
        # 测试移除元数据
        clean_data = data[:header_pos]
        print(f"\n移除元数据后大小: {len(clean_data)} 字节")
        
        # 检查ONNX文件头
        if clean_data[:4] == b'\x08\x03\x12\x02' or clean_data[:4] == b'\x08\x07\x12\x02':
            print("✓ ONNX文件头正确")
        else:
            print(f"✗ ONNX文件头异常: {clean_data[:20].hex()}")
            
    else:
        print("未找到加密标记")
        # 检查原始ONNX文件头
        if data[:4] == b'\x08\x03\x12\x02' or data[:4] == b'\x08\x07\x12\x02':
            print("✓ 这是一个未加密的ONNX文件")
        else:
            print(f"✗ 文件头异常: {data[:20].hex()}")

if __name__ == "__main__":
    print("=" * 60)
    print("调试加密模型")
    print("=" * 60)
    debug_encrypted_model("models/thor_segm_20251031.onnx")
