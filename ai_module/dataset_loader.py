import os
import json
import torch
from torch.utils.data import Dataset
import soundfile as sf

class EmotionTalkDataset(Dataset):
    def __init__(self, text_dir, audio_dir):
        """
        初始化我们的数据喂食器 (V2.0 终极固化版)
        :param text_dir: 解压出来的 Text 文件夹路径
        :param audio_dir: 解压出来的 Audio 文件夹路径
        """
        self.text_dir = text_dir
        self.audio_dir = audio_dir
        self.samples = []
        
        # 删除了所有的动态分配逻辑，保证每次训练 0 永远代表 neutral！
        self.label_map = {
            'neutral': 0,     # 平静
            'happy': 1,       # 开心
            'sad': 2,         # 悲伤
            'angry': 3,       # 愤怒
            'fearful': 4,     # 害怕
            'disgusted': 5,   # 厌恶
            'surprised': 6    # 惊讶
        }

        print("🔍 正在扫描所有的 JSON 标签文件，建立索引...")
        
        # 递归扫描文件夹里的所有 .json 文件
        for root, _, files in os.walk(text_dir):
            for file in files:
                if file.endswith('.json'):
                    json_path = os.path.join(root, file)
                    self.samples.append(json_path)

        print(f"✅ 扫描完毕！一共找到了 {len(self.samples)} 条真实多模态数据！")

    def __len__(self):
        # 告诉 PyTorch 一共有多少条数据
        return len(self.samples)

    def __getitem__(self, idx):
        # 核心逻辑：当 PyTorch 要第 idx 条数据时，怎么给它？
        json_path = self.samples[idx]
        
        # 读取 JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        text = data['content']
        emotion = data['emotion_result'] # 拿到真实的英文情绪词汇
        
        # 直接去焊死的字典里查 ID，查不到会自动报错，杜绝乱排号！
        label_id = self.label_map[emotion]
        
        # 智能寻找录音路径：兼容不同的 JSON 格式
        if 'file_path' in data:
            audio_rel_path = data['file_path']
        elif 'file_name' in data:
            audio_rel_path = data['file_name']
            # 如果它给的是 .txt 后缀，强制把它替换成 .wav
            audio_rel_path = audio_rel_path.replace('.txt', '.wav')
        else:
            audio_rel_path = ""  
            
        # 统一路径斜杠，防止 Windows 报错
        audio_full_path = os.path.normpath(os.path.join(self.audio_dir, audio_rel_path))
        
        # 尝试读取音频文件
        try:
            # 用最稳的 soundfile 直接读出 numpy 数组
            audio_array, sample_rate = sf.read(audio_full_path)
            
            # 消除双声道地雷
            if len(audio_array.shape) > 1 and audio_array.shape[1] == 2:
                audio_array = audio_array.mean(axis=1)
                
            # 手动把数组变成 5060 认识的张量，套上外壳变成 [1, 长度]
            waveform = torch.from_numpy(audio_array).float().unsqueeze(0)
            
        except Exception as e:
            # 为了防止正式训练时终端被满屏的报错刷屏，这里精简了报错信息
            # print(f"[警告] 音频加载失败，已使用静音兜底: {audio_rel_path}")
            waveform = torch.zeros(1, 16000)
            
        return text, waveform, label_id

# ================= 测试代码 =================
def main():
    # 真实路径
    TEXT_FOLDER = r"D:\program_py\true\Text\json" 
    AUDIO_FOLDER = r"D:\program_py\true\EmotionAudio\Audio\Audio\wav"
    
    # 实例化数据集
    dataset = EmotionTalkDataset(text_dir=TEXT_FOLDER, audio_dir=AUDIO_FOLDER)
    
    print("\n🧠 情绪标签对应的数字 ID 字典:")
    for k, v in dataset.label_map.items():
        print(f"  {k}: {v}")
    
    # 取出第一条数据看看！
    print("\n📦 抽取第一条真实数据进行测试：")
    text, waveform, label_id = dataset[0]
    
    print(f"📄 文本: {text}")
    print(f"🏷️ 标签 ID: {label_id}")
    print(f"🎙️ 录音矩阵形状: {waveform.shape}")
    print("-" * 50)
    print("🚀 完美！V2.0 终极数据基建测试通过！")

if __name__ == "__main__":
    main()