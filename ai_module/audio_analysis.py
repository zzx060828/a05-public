import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
import librosa
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, Wav2Vec2FeatureExtractor
from typing import Dict, Optional
import time
import os
from fusion_model import EndToEndPaperGatedFusion


class LocalMultimodalBrain:
    def __init__(self, model_path="ai_interviewer_brain_v3_e2e.pth"):
        """
        单例模式加载模型，避免每次推理重复把 1GB 塞进显存
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[硬件资源] 分配计算设备: {self.device}")
        
        self.label_map = {
            0: '平静',      # neutral
            1: '开心/自信', # happy
            2: '悲伤/迟疑', # sad
            3: '愤怒/破防', # angry
            4: '害怕/发慌', # fearful
            5: '厌恶/抗拒', # disgusted
            6: '惊讶/意外'  # surprised
        }
        
        # 英文映射，用于主程序提取数学概率
        self.key_map = {0: 'neutral', 1: 'happy', 2: 'sad', 3: 'angry', 4: 'fearful', 5: 'disgusted', 6: 'surprised'}

        try:
            # 实例化7分类网络
            self.model = EndToEndPaperGatedFusion(num_classes=7)
            
            #加载权重
            if os.path.exists(model_path):
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                print("[系统启动] V3 模型权重加载成功！")
            else:
                print(f"[严重警告] 找不到权重文件 {model_path}，请检查路径！")
                
            self.model.to(self.device)
            self.model.eval() # 切换为推理模式

            # 初始化文本和音频预处理器
            self.tokenizer = AutoTokenizer.from_pretrained("hfl/chinese-roberta-wwm-ext")
            self.audio_extractor = Wav2Vec2FeatureExtractor.from_pretrained("microsoft/wavlm-base")
            self.is_ready = True
            
        except Exception as e:
            print(f"[致命错误] 多模态大脑初始化失败: {e}")
            self.is_ready = False

    def process_long_audio(self, waveform, sr, transcript_text, window_sec=8.0):
        """
        核心推断逻辑：滑动窗口 + 概率池化
        """
        # 兜底字典，防止报错
        fallback_dict = {k: 0.0 for k in self.key_map.values()}
        fallback_dict["neutral"] = 1.0
        
        if not self.is_ready:
            return "平静 (V3模型未就绪)", fallback_dict

        # 文本预处理 (RoBERTa 提取全局语义)
        text_inputs = self.tokenizer(
            transcript_text if transcript_text else "这是一段面试回答", 
            return_tensors="pt", padding="max_length", truncation=True, max_length=128
        ).to(self.device)

        total_duration = librosa.get_duration(y=waveform, sr=sr)
        all_probs = []

        # 滑动窗口切片 (防显存溢出)
        for start_time in np.arange(0, total_duration, window_sec):
            end_time = min(start_time + window_sec, total_duration)
            
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            audio_slice = waveform[start_sample:end_sample]
            
            if len(audio_slice) < sr * 1.0: # 太短跳过
                continue

            audio_inputs = self.audio_extractor(
                audio_slice, sampling_rate=sr, return_tensors="pt"
            ).input_values.to(self.device)

            with torch.no_grad():
                logits_merge, _, _ = self.model(
                    input_ids=text_inputs["input_ids"], 
                    attention_mask=text_inputs["attention_mask"], 
                    audio_values=audio_inputs
                )
                
            probs = F.softmax(logits_merge, dim=1).cpu().numpy()[0]
            all_probs.append(probs)

        if not all_probs:
            return "平静 (音频太短)", fallback_dict

        # 概率池化：计算所有切片的平均概率
        avg_probs = np.mean(all_probs, axis=0)
        
        # 组装概率字典 (送给主程序算分)
        prob_dict = {self.key_map[i]: float(avg_probs[i]) for i in range(7)}
        
        # 生成大模型能看懂的文字描述
        top1_idx = np.argmax(avg_probs)
        top1_emotion = self.label_map[top1_idx]
        text_desc = f"【{top1_emotion}】(核心置信度 {avg_probs[top1_idx]*100:.1f}%)"
        
        # 捕获情绪突变
        # 全链路时序情绪追踪 
        if len(all_probs) >= 2:
            # 提取所有时间窗口的主导情绪索引
            traj_indices = [np.argmax(p) for p in all_probs]
            
            # 压缩轨迹 (例如把连续的 [平静, 平静, 恐惧, 恐惧, 平静] 压缩为 [平静 ➔ 恐惧 ➔ 平静])
            compressed_traj = [traj_indices[0]]
            for idx in traj_indices[1:]:
                if idx != compressed_traj[-1]:
                    compressed_traj.append(idx)
                    
            # 寻找情绪波峰：在所有切片中，挑出“恐惧(4)”和“悲伤/迟疑(2)”的最高瞬时概率
            max_fear_prob = max([p[4] for p in all_probs])
            max_sad_prob = max([p[2] for p in all_probs])
            
            #组装时序汇报
            if len(compressed_traj) > 1:
                traj_names = " ➔ ".join([self.label_map[i] for i in compressed_traj])
                text_desc = f"总体【{top1_emotion}】。微观情绪轨迹：{traj_names}。"
                
                # 触发瞬时破防警报 (只要中间有哪怕 8 秒的恐慌概率超过 40%)
                if max_fear_prob > 0.4:
                    text_desc += f" (⚠️系统捕获到瞬时高压/发慌，峰值概率达 {max_fear_prob*100:.1f}%)"
                elif max_sad_prob > 0.4:
                    text_desc += f" (⚠️系统捕获到瞬时迟疑/不自信，峰值概率达 {max_sad_prob*100:.1f}%)"
        return text_desc, prob_dict

# 全局单例实例化
v3_brain = LocalMultimodalBrain()

# ============ 1. 语音分析模块 ============
def analyze_speech_algorithm(audio_path: str, transcript_text: str = None, word_count: Optional[int] = None) -> Dict:
    try:
        y, sr = librosa.load(audio_path, sr=16000)
        duration = librosa.get_duration(y=y, sr=sr)
        result = {}
        
        # 计算语速
        if word_count is not None and duration > 0.5:
            wpm = (word_count / duration) * 60
            result['speed'] = "较慢" if wpm < 160 else "过快" if wpm > 280 else "正常"
        else:
            result['speed'] = "正常"
            
        # 寻找物理卡顿
        rms = librosa.feature.rms(y=y)[0]
        db = librosa.amplitude_to_db(rms, ref=np.max)
        silent_regions = db < -40
        pause_count = 0
        is_silent, silent_start = False, 0
        
        for i, silent in enumerate(silent_regions):
            if silent and not is_silent:
                is_silent, silent_start = True, i
            elif not silent and is_silent:
                is_silent = False
                if (i - silent_start) * (len(y) / len(rms)) / sr > 1.5:  
                    pause_count += 1
        result['pause_count'] = pause_count

        #呼叫 V3 大脑
        emotion_desc, prob_dict = v3_brain.process_long_audio(y, sr, transcript_text, window_sec=8.0)
        
        if pause_count >= 4:
            result['emotion'] = f"{emotion_desc} (注：伴随严重物理结巴)"
        else:
            result['emotion'] = emotion_desc
            
        # 暴露连续概率供 interviewer.py 提取
        result['emotion_probs'] = prob_dict
        
        print(f"[V3 大脑分析完毕] 综合情感: {result['emotion']}")
        return result

    except Exception as e:
        import traceback
        print(f"语音分析算法出错: {e}")
        fallback = {k: 0.0 for k in v3_brain.key_map.values()}
        fallback["neutral"] = 1.0
        return {"speed": "正常", "pause_count": 0, "emotion": "平静 (兜底机制)", "emotion_probs": fallback}

# ============ 2. speech_meta参数 ============
def prepare_for_interview(audio_path: str, transcript_text: str = None) -> Dict:
    word_count = len([c for c in transcript_text if c.strip()]) if transcript_text else None
    return analyze_speech_algorithm(audio_path, transcript_text, word_count)

if __name__ == "__main__":
    test_file = "test.wav" 
    test_text = "面试官你好，我是来面试java开发岗位的，redis主要是基于内层操作的。"
    
    if os.path.exists(test_file):
        print("\n========== 第一次测试：冷启动 ==========")
        start_time = time.time()
        res = prepare_for_interview(test_file, test_text)
        print(f"描述输出: {res['emotion']}")
        print(f"概率字典: {res['emotion_probs']}")
        print(f"⏱️ 耗时: {time.time() - start_time:.2f} 秒\n")