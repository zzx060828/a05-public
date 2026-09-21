# 首先需要安装: pip install scipy
import numpy as np
from scipy.io import wavfile


def read_wav_file_scipy(file_path):
    """
    使用scipy.io.wavfile读取wav文件
    """
    try:
        # 读取音频文件和采样率
        sample_rate, audio_data = wavfile.read(file_path)

        print(f"采样率: {sample_rate} Hz")
        print(f"音频数据形状: {audio_data.shape}")
        print(f"音频数据类型: {audio_data.dtype}")
        print(f"音频时长: {len(audio_data) / sample_rate:.2f} 秒")

        return sample_rate, audio_data
    except Exception as e:
        print(f"读取wav文件时发生错误: {e}")
        return None, None


# 使用示例
sample_rate, audio_data = read_wav_file_scipy('example.wav')
if audio_data is not None:
    # 如果是立体声（多声道），音频数据将是二维数组
    if len(audio_data.shape) > 1:
        print(f"声道数: {audio_data.shape[1]}")