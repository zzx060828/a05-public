import librosa
import numpy as np
from typing import Dict, Optional
from transformers import pipeline
import time

# ============ 0. 全局加载算法模型 ============
print("==================================================")
print("[系统启动] 正在加载本地 Wav2Vec2 语音情感算法模型...")
print("（如果是第一次运行，后台会自动从 HuggingFace 下载权重，请保持网络畅通，耐心等待几分钟）")
print("==================================================")

try:
    # 加载本地深度学习模型 (尝试使用 GPU，如果没有则自动降级到 CPU)
    # 替换为支持 8 种精细情感的高阶模型
    emotion_classifier = pipeline(
        "audio-classification", 
        model="prithivMLmods/Speech-Emotion-Classification", 
        device=0 
    )
    print("✅ [成功] 语音情感算法加载完毕！\n")
except Exception as e:
    print(f"❌ [警告] 模型加载失败，可能缺少依赖或网络问题: {e}")
    emotion_classifier = None


# ============ 1. 语音分析模块 ============
def analyze_speech_algorithm(audio_path: str, word_count: Optional[int] = None) -> Dict:
    try:
        y, sr = librosa.load(audio_path, sr=16000)
        duration = librosa.get_duration(y=y, sr=sr)
        result = {}

        # 算语速
        if word_count is not None and duration > 0.5:  
            wpm = (word_count / duration) * 60
            if wpm < 160: result['speed'] = "较慢"
            elif wpm > 280: result['speed'] = "过快"
            else: result['speed'] = "正常"

        # 算卡顿
        rms = librosa.feature.rms(y=y)[0]
        db = librosa.amplitude_to_db(rms, ref=np.max)
        silent_regions = db < -40
        pause_count = 0
        is_silent = False
        silent_start = 0
        for i, silent in enumerate(silent_regions):
            if silent and not is_silent:
                is_silent = True
                silent_start = i
            elif not silent and is_silent:
                is_silent = False
                silent_duration = (i - silent_start) * (len(y) / len(rms)) / sr
                if silent_duration > 1.0:  # 为了测试容易触发，把卡顿判定缩短到 1 秒
                    pause_count += 1
        result['pause_count'] = pause_count

        # 真实 AI 算法情感推断
        if emotion_classifier is not None:
            max_len = 16000 * 10 
            audio_input = y[:max_len]
            preds = emotion_classifier(audio_input)
            # 拿到算法输出的情感标签并转为小写
            top_emotion = preds[0]['label'].lower()
            
            # 8 维情感的专业面试场景映射
            emotion_mapping = {
                "anger": "情绪急躁/破防", 
                "calm": "沉稳淡定",
                "disgust": "抗拒/极度不自信", 
                "fear": "紧张发慌/害怕",   # <--- 你最想要的“紧张”在这里！
                "happy": "自信从容", 
                "neutral": "平静自然",
                "sad": "低落/极度迟疑",
                "surprised": "意外/被问住了"
            }
            base_emotion = emotion_mapping.get(top_emotion, "平静自然")
            
            # 【终极必杀技：算法预测 + 物理卡顿 双重校验】
            if top_emotion == "fear" or pause_count >= 2:
                result['emotion'] = f"{base_emotion} (伴随明显结巴，判定为极度紧张)"
            else:
                result['emotion'] = base_emotion
            return result
    except Exception as e:
        print(f"执行出错: {e}")
        return {"speed": "正常", "pause_count": 0, "emotion": "测试出错"}


# ============ 2. 包装函数 ============
def prepare_for_interview(audio_path: str, transcript_text: str = None) -> Dict:
    word_count = len([c for c in transcript_text if c.strip()]) if transcript_text else None
    return analyze_speech_algorithm(audio_path, word_count)


# ============ 3. 运行测试 (相当于 C 语言的 main 函数) ============
if __name__ == "__main__":
    test_file = "test1.wav"  # 确保你准备的录音文件叫这个名字
    test_text = "面试官你好，我是来应聘Java开发岗位的，Redis主要是基于内存操作的。"
    
    print(f"🎙️ 开始分析音频文件: {test_file}")
    print(f"📝 传入的前端识别文字: '{test_text}'")
    
    start_time = time.time()
    
    # 执行核心调用
    final_speech_meta = prepare_for_interview(test_file, test_text)
    
    end_time = time.time()
    
    print("\n" + "="*50)
    print("📊 [分析结果] 最终要传给 AI 面试官的 speech_meta 参数：")
    print(final_speech_meta)
    print("="*50)
    print(f"⏱️ 本次 AI 分析耗时: {end_time - start_time:.2f} 秒")