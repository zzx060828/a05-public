import librosa
import numpy as np
import json
from typing import Dict, Optional


# ============ 1. 语音分析模块 ============
def analyze_speech_algorithm(audio_path: str, word_count: Optional[int] = None) -> Dict:
    """
    语音分析核心算法
    输入音频路径，返回包含'speed'和'pause_count'的字典。
    """
    try:
        # 1. 加载音频
        y, sr = librosa.load(audio_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)

        result = {}

        # 2. 计算语速 (如果提供了字数)
        if word_count is not None and duration > 0.5:  # 有效音频长度
            wpm = (word_count / duration) * 60
            if wpm < 160:
                result['speed'] = "较慢"
            elif wpm > 280:
                result['speed'] = "过快"
            else:
                result['speed'] = "正常"
        # 注意：如果没有提供word_count，result中将不包含'speed'键
        # 这符合接口的容错设计

        # 3. 计算卡顿次数
        # 这里使用基于能量的简单静音检测
        rms = librosa.feature.rms(y=y)[0]
        db = librosa.amplitude_to_db(rms, ref=np.max)

        # 找出能量低于阈值的静音段
        silent_regions = db < -40
        pause_count = 0

        # 简单的静音段计数逻辑
        is_silent = False
        silent_start = 0
        for i, silent in enumerate(silent_regions):
            if silent and not is_silent:
                is_silent = True
                silent_start = i
            elif not silent and is_silent:
                is_silent = False
                silent_duration = (i - silent_start) * (len(y) / len(rms)) / sr
                if silent_duration > 2.0:  # 超过1.5秒算卡顿
                    pause_count += 1

        result['pause_count'] = pause_count
        return result

    except Exception as e:
        print(f"语音分析算法出错: {e}")
        return {}  # 返回空字典，触发容错机制


# ============ 2. speech_meta参数 ============
def prepare_for_interview(audio_path: str, transcript_text: str = None) -> Dict:
    """
    集成了分析算法，并确保输出符合speech_meta格式。
    """
    # 计算字数（如果提供了文本）    =====================语音识别传入
    word_count = None
    if transcript_text:
        # 简单的中文字数统计（可根据需要调整）
        word_count = len([c for c in transcript_text if c.strip()])

    # 调用分析算法
    analysis_result = analyze_speech_algorithm(audio_path, word_count)

    # 这就是最终要传递给AI面试官的speech_meta参数！
    speech_meta = analysis_result

    # 打印调试信息
    print("=" * 50)
    print("语音分析完成，speech_meta参数已准备就绪：")
    print(f"音频文件: {audio_path}")
    print(f"识别文本: {transcript_text[:50]}..." if transcript_text else "识别文本: 无")
    print(f"分析结果: {json.dumps(speech_meta, ensure_ascii=False, indent=2)}")
    print("=" * 50)

    return speech_meta

# ============ 3. 测试示例 ============
'''if __name__ == "__main__":

    print("语音分析模块 + AI面试官接口对接演示")
    print("=" * 60)

    # 1：正常情况（有语音文件，有识别文本）
    print("\n示例1：完整分析流程")
    test_audio = "D:/A05/a05/STT/test.wav"  # 您的音频文件路径
    #=====传入识别文件======
    test_text = "从远处看，你还以为是飘落的花瓣呢。"



    # 这是需要调用的关键代码
    speech_meta_result = prepare_for_interview(test_audio, test_text)
    print(f"生成的speech_meta参数: {speech_meta_result}")


    #直接查看speech_meta参数的结构
    print("\nspeech_meta参数数据结构验证")
    test_cases = [
        {"speed": "正常", "pause_count": 0},
        {"speed": "过快", "pause_count": 5},
        {"pause_count": 2},  # 缺少speed字段
        {},  # 空字典
        {"speed": "较慢"},  # 缺少pause_count字段
    ]

    for i, test_case in enumerate(test_cases, 1):
        speed = test_case.get('speed', '正常')
        pauses = test_case.get('pause_count', 0)
        print(f"测试用例{i}: {test_case} -> 解析结果: 语速={speed}, 卡顿={pauses}")
'''
# ============ 4. 最简单的使用方式 ============

# 步骤1: 准备输入
audio_file = "D:/A05/a05/STT/test.wav"
recognized_text = "从远处看，你还以为是飘落的花瓣呢。"  # 如果没有，就传None

# 步骤2: 生成speech_meta参数
speech_meta_param = prepare_for_interview(audio_file, recognized_text)

# 步骤3: 将speech_meta_param传递给AI面试官接口
# 假设AI面试官接口函数是 ai_interview_api(speech_meta=speech_meta_param, ...)
# response = ai_interview_api(speech_meta=speech_meta_param, other_params...)

print(f"\n最终生成的speech_meta参数: {speech_meta_param}")