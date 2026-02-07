"""
ONNX Runtime 补丁 - 自动试用期检查
将此文件放在项目根目录，在main.py最开始导入即可

使用方法:
在 main.py 的最顶部添加:
    import onnxruntime_patch  # 必须在导入onnxruntime之前
"""
import sys
import tempfile
import os

# 保存原始的onnxruntime模块（如果已经导入）
_original_onnxruntime = sys.modules.get('onnxruntime', None)

# 导入真正的onnxruntime
import onnxruntime as _ort

# 导入试用期检查函数
from model_loader import check_model_trial, strip_trial_metadata

# 保存原始的InferenceSession类
_OriginalInferenceSession = _ort.InferenceSession

class PatchedInferenceSession(_OriginalInferenceSession):
    """
    带试用期检查的InferenceSession
    """
    def __init__(self, path_or_bytes, sess_options=None, providers=None, provider_options=None, **kwargs):
        # 如果是文件路径（字符串）
        if isinstance(path_or_bytes, str):
            # 检查试用期
            if not check_model_trial(path_or_bytes):
                # 试用期已过，静默失败
                raise RuntimeError("Model initialization failed")
            
            # 移除试用期元数据，创建临时文件
            clean_data = strip_trial_metadata(path_or_bytes)
            if clean_data is None:
                raise RuntimeError("Model initialization failed")
            
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.onnx')
            temp_file.write(clean_data)
            temp_file.close()
            
            try:
                # 使用临时文件初始化
                super().__init__(temp_file.name, sess_options, providers, provider_options, **kwargs)
            finally:
                # 删除临时文件
                try:
                    os.remove(temp_file.name)
                except:
                    pass
        else:
            # 如果是字节数据，直接传递
            super().__init__(path_or_bytes, sess_options, providers, provider_options, **kwargs)

# 替换onnxruntime.InferenceSession
_ort.InferenceSession = PatchedInferenceSession
sys.modules['onnxruntime'].InferenceSession = PatchedInferenceSession
