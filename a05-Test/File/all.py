import os
import json
import wave
from wav import read_wav_file_wave
from json import read_json_file
from txt import read_txt_file
from wav_scipy import read_wav_file_scipy
from scipy.io import wavfile


def read_file(file_path):
    """
    根据文件扩展名自动选择合适的读取方式
    """
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在")
        return None

    # 获取文件扩展名
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        return read_txt_file(file_path)

    elif ext == '.json':
        return read_json_file(file_path)

    elif ext == '.wav':
        print("检测到.wav文件，选择读取方法:")
        print("1. 使用wave模块（标准库）")
        print("2. 使用scipy.io.wavfile（需安装）")

        #根据需要选择合适的读取方式
        #如果scipy已安装，优先使用它
        try:
            from scipy.io import wavfile
            sample_rate, audio_data = read_wav_file_scipy(file_path)
            return {'sample_rate': sample_rate, 'audio_data': audio_data}
        except ImportError:
            print("scipy未安装，使用wave模块")
            frames, params = read_wav_file_wave(file_path)
            return {'frames': frames, 'params': params}

    else:
        print(f"不支持的文件类型: {ext}")
        print("尝试作为文本文件读取...")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except:
            # 如果文本读取失败，尝试二进制读取
            with open(file_path, 'rb') as file:
                return file.read()


# 使用示例
file_content = read_file("D:\music\突然的自我,伍佰.wav")  # 会自动识别文件类型并读取