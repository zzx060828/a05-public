from datasets import load_dataset
import torch

import os
# ⚠️ 魔法指令：强制使用国内高速镜像站，突破网络封锁
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from datasets import load_dataset

def main():
    print("🚀 正在连接国内镜像，拉取 BAAI/Emotiontalk 中文情感数据集...")
    print("（第一次运行会自动下载真实的音频和文本，有 RTX 5060 加持和镜像，速度会很快！）")
    print("-" * 50)
    
    # 一键拉取智源研究院的中文多模态数据集！
    dataset = load_dataset("BAAI/Emotiontalk")
    
    print("✅ 数据集下载并加载成功！整体结构如下：")
    print(dataset)
    print("-" * 50)
    
    # 抽取训练集里的第一条真实数据，看看它里面到底装了什么
    sample = dataset["train"][0]
    print("👀 让我们看看第一条真实中文数据长什么样：")
    
    # 遍历打印出这条数据的所有字段（比如文本是什么、标签是什么、音频矩阵在哪）
    for key, value in sample.items():
        # 如果遇到音频数组，只打印形状，不然满屏幕都是数字
        if key == 'audio' or isinstance(value, dict) and 'array' in value:
            print(f" - {key}: [包含音频矩阵数据, 采样率等信息]")
        else:
            print(f" - {key}: {value}")

if __name__ == "__main__":
    main()