import torch
import torch.nn as nn
import torch.nn.functional as F  
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm
import math

# 🚀 引入混合精度训练 (AMP) 的超级加速模块
from torch.amp import autocast, GradScaler

from transformers import AutoTokenizer, Wav2Vec2FeatureExtractor
from dataset_loader import EmotionTalkDataset
from fusion_model import EndToEndPaperGatedFusion  

def main():
    # ⚠️ 云端相对路径（只要 train.py 和数据文件夹挨在一起就没问题！）
    TEXT_FOLDER = r"./Text/json" 
    AUDIO_FOLDER = r"./EmotionAudio/Audio/Audio/wav"

    print("🔥 [1/4] 正在唤醒云端顶级显卡与大模型处理器...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"✅ 当前计算设备: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    
    tokenizer = AutoTokenizer.from_pretrained("hfl/chinese-roberta-wwm-ext")
    audio_processor = Wav2Vec2FeatureExtractor.from_pretrained("microsoft/wavlm-base")

    full_dataset = EmotionTalkDataset(text_dir=TEXT_FOLDER, audio_dir=AUDIO_FOLDER)
    
    train_size = int(0.8 * len(full_dataset))
    test_size = len(full_dataset) - train_size
    generator = torch.Generator().manual_seed(42)
    train_dataset, test_dataset = torch.utils.data.random_split(full_dataset, [train_size, test_size], generator=generator)

    def custom_collate_fn(batch):
        texts = [item[0] for item in batch]
        waveforms = [item[1].squeeze(0).numpy() if item[1].dim() > 1 else item[1].numpy() for item in batch]
        labels = [item[2] for item in batch]

        text_encodings = tokenizer(texts, padding="longest", truncation=True, max_length=128, return_tensors="pt")
        audio_encodings = audio_processor(waveforms, sampling_rate=16000, padding=True, return_tensors="pt")
        labels_tensor = torch.tensor(labels, dtype=torch.long)

        return text_encodings['input_ids'], text_encodings['attention_mask'], audio_encodings['input_values'], labels_tensor

    num_emotions = 7
    model = EndToEndPaperGatedFusion(num_classes=num_emotions).to(device)

    # 🚀 榨干大法 1 & 2：Batch Size 飙升至 32，开启 4 线程极速喂饭，内存直通显卡！
    dataloader = DataLoader(train_dataset, batch_size=2, shuffle=True, collate_fn=custom_collate_fn, num_workers=4, pin_memory=True)

    counts = [7903, 1620, 1183, 3698, 1023, 1111, 2712]
    weights = [1.0 / math.sqrt(c) for c in counts]
    class_weights = torch.FloatTensor(weights).to(device)
    
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.AdamW(model.parameters(), lr=0.00002)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=4, gamma=0.5)
    temperature = 2.0 

    # 🚀 初始化 AMP 梯度缩放器（防止半精度计算时梯度消失）
    scaler = GradScaler()

    # ================= 2. 炼丹炉点火 (Training Loop) =================
    print(f"\n🚀 [2/4] 云端集训开始！使用 {len(train_dataset)} 条数据，开启全量微调与 AMP 混合精度！")
    model.train() 
    
    num_epochs = 15 
    training_history = [] 

    for epoch in range(num_epochs):
        print(f"\n======== 正在进行第 {epoch + 1}/{num_epochs} 轮炼丹 ========")
        progress_bar = tqdm(dataloader, desc=f"🔥 轮次 {epoch + 1}")

        epoch_t_loss, epoch_s_loss, epoch_dist_loss, epoch_total_loss = 0.0, 0.0, 0.0, 0.0

        for batch_idx, (input_ids, attention_mask, audio_values, labels_tensor) in enumerate(progress_bar):
            
            input_ids = input_ids.to(device)
            attention_mask = attention_mask.to(device)
            audio_values = audio_values.to(device) 
            labels_tensor = labels_tensor.to(device)

            optimizer.zero_grad()
            
            # 🚀 榨干大法 3：开启自动混合精度上下文 (光速前向传播)
            with autocast(device_type="cuda"):
                logits_merge, logits_t, logits_a = model(input_ids, attention_mask, audio_values)
                
                loss_sup_t = criterion(logits_merge, labels_tensor)
                loss_sup_s = criterion(logits_t, labels_tensor) + criterion(logits_a, labels_tensor)

                soft_targets = F.softmax(logits_merge / temperature, dim=1).detach()
                log_probs_t = F.log_softmax(logits_t / temperature, dim=1)
                log_probs_a = F.log_softmax(logits_a / temperature, dim=1)
                
                loss_dist = (F.kl_div(log_probs_t, soft_targets, reduction='batchmean') + 
                             F.kl_div(log_probs_a, soft_targets, reduction='batchmean')) * (temperature ** 2)

                loss = loss_sup_t + loss_sup_s + loss_dist
            
            # 🚀 搭配缩放器的高级反向传播
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            epoch_t_loss += loss_sup_t.item()
            epoch_s_loss += loss_sup_s.item()
            epoch_dist_loss += loss_dist.item()
            epoch_total_loss += loss.item()

            progress_bar.set_postfix({
                'T_Loss': f"{loss_sup_t.item():.2f}", 
                'S_Loss': f"{loss_sup_s.item():.2f}", 
                'Dist_L': f"{loss_dist.item():.2f}"   
            })
            
        num_batches = len(dataloader)
        training_history.append({
            'epoch': epoch + 1,
            't_loss': epoch_t_loss / num_batches,
            's_loss': epoch_s_loss / num_batches,
            'dist_loss': epoch_dist_loss / num_batches,
            'total_loss': epoch_total_loss / num_batches
        })
        scheduler.step()

    print("\n" + "=".center(60, "="))
    print("📈 AI 面试官 V3.0 (端到端 + AMP 完全体) 训练历程终极战报")
    print("=".center(60, "="))
    print(f"{'轮次':<6} | {'总误差':<10} | {'老师误差':<10} | {'学生误差':<10} | {'蒸馏误差':<10}")
    print("-" * 60)
    for h in training_history:
        print(f"第 {h['epoch']:02d} 轮 | {h['total_loss']:<9.4f} | {h['t_loss']:<9.4f} | {h['s_loss']:<9.4f} | {h['dist_loss']:<9.4f}")
    print("=".center(60, "="))

    print("\n🎉 端到端全量微调完毕！")
    torch.save(model.state_dict(), "ai_interviewer_brain_v3_e2e.pth")
    print("💾 宇宙最强形态的“智慧大脑”已经保存为 ai_interviewer_brain_v3_e2e.pth 文件！")

if __name__ == "__main__":
    main()