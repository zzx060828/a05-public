import wave
def read_wav_file_wave(file_path):
    """
    使用wave模块读取wav文件
    """
    try:
        with wave.open(file_path, 'rb') as wav_file:
            # 获取音频参数
            params = wav_file.getparams()
            frames = wav_file.readframes(params.nframes)

            print("音频参数:")
            print(f"  声道数: {params.nchannels}")
            print(f"  采样宽度: {params.sampwidth} 字节")
            print(f"  采样率: {params.framerate} Hz")
            print(f"  帧数: {params.nframes}")
            print(f"  时长: {params.nframes / params.framerate:.2f} 秒")

            return frames, params
    except Exception as e:
        print(f"读取wav文件时发生错误: {e}")
        return None, None


# 使用示例
audio_frames, audio_params = read_wav_file_wave("D:\FFOutput\程响-可能.wav")