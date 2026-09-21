import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
import torch
from faster_whisper import WhisperModel
# 1. 全局加载模型 (极其重要)
# 写在函数外面，这样模型只会在程序刚启动时加载 1 次
# 如果写在函数里面，每次说话都要重新加载好几百兆模型，会卡死
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"
print(f"[STT 启动] 正在加载本地 Faster-Whisper 模型，使用设备: {device}...")
# 第一次运行会自动从 huggingface 下载 "small" 模型 (大约几百兆)
# 如果觉得慢，可以把 "small" 换成 "base" (速度更快，但准确率稍有下降)
model = WhisperModel("small", device=device, compute_type=compute_type)
print("[STT 启动] 本地语音识别模型就绪！")
def speech_to_text(audio_file_path: str) -> str:
    """识别音频文件为文字 (Faster-Whisper 本地脱机版)"""
    if not os.path.exists(audio_file_path):
        return "[识别失败]：音频文件不存在"

    try:
        # 2. 核心转录代码 (就是这么一行)
        # language="zh" 强制指定中文可以大幅提高识别速度和准确率
        # beam_size=5 类似于 AI 的“深思熟虑”程度，5 是效果最好的默认值
        segments, info = model.transcribe(audio_file_path, beam_size=5, language="zh")
        
        # 3. 拼接所有识别出来的文字
        # Whisper 会把长句子切成好几个 segment 返回，我们需要把它们拼成完整的一句话
        text = "".join([segment.text for segment in segments])
        
        return text.strip() if text else "[识别失败]：识别结果为空"
        
    except Exception as e:
        import traceback
        traceback.print_exc() # 在控制台打印详细报错，方便你调试
        return f"[识别失败]：本地模型报错 {str(e)}"