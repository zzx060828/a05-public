import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
import torch
import torch.nn as nn
from transformers import AutoModel, WavLMModel

class EndToEndPaperGatedFusion(nn.Module):
    def __init__(self, num_classes=7, hidden_dim=768, num_heads=8):
        """
        🚀 终极端到端架构 (End-to-End)
        包含了 RoBERTa 和 WavLM 底层特征提取器，所有参数全程参与梯度计算（全量微调）
        """
        super(EndToEndPaperGatedFusion, self).__init__()
        
        # =================================================================
        # 0. 核心引擎：把两大预训练模型直接装进肚子里！
        # =================================================================
        print("⏳ 正在体内构建 RoBERTa 和 WavLM 神经元...")
        self.roberta = AutoModel.from_pretrained("hfl/chinese-roberta-wwm-ext")
        self.wavlm = WavLMModel.from_pretrained("microsoft/wavlm-base")

        # 💡 顶级算法工程师的保命 Trick：梯度检查点 (Gradient Checkpointing)
        # 这会牺牲一点点计算时间，但能节约将近 40% 的显存！让你在 3090 上能开更大的 Batch Size！
        self.roberta.gradient_checkpointing_enable()
        self.wavlm.gradient_checkpointing_enable()

        # =================================================================
        # 1. Attention Module (跨模态门控注意力)
        # =================================================================
        self.attn_tt = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=num_heads, batch_first=True) 
        self.attn_ta = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=num_heads, batch_first=True) 
        self.attn_aa = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=num_heads, batch_first=True) 
        self.attn_at = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=num_heads, batch_first=True) 

        # =================================================================
        # 2. Aggregation Module (融合降维)
        # =================================================================
        self.fc_combine_t = nn.Linear(hidden_dim * 2, hidden_dim)
        self.fc_combine_a = nn.Linear(hidden_dim * 2, hidden_dim)

        # =================================================================
        # 3. Gating Mechanism (动态门控权重)
        # =================================================================
        self.gate_t = nn.Sequential(nn.Linear(hidden_dim, hidden_dim), nn.Sigmoid())
        self.gate_a = nn.Sequential(nn.Linear(hidden_dim, hidden_dim), nn.Sigmoid())

        # =================================================================
        # 4. Classifiers (自蒸馏分类器)
        # =================================================================
        self.classifier_merge = nn.Sequential(
            nn.Linear(hidden_dim, 256), nn.ReLU(), nn.Dropout(0.3), nn.Linear(256, num_classes)
        )
        self.classifier_t = nn.Sequential(
            nn.Linear(hidden_dim, 256), nn.ReLU(), nn.Dropout(0.3), nn.Linear(256, num_classes)
        )
        self.classifier_a = nn.Sequential(
            nn.Linear(hidden_dim, 256), nn.ReLU(), nn.Dropout(0.3), nn.Linear(256, num_classes)
        )

    def forward(self, input_ids, attention_mask, audio_values):
        """
        🚨 前向传播：现在直接接收最原始的文字 token 和波形矩阵！
        """
        # --- 步骤 0: 动态提取特征 (全量微调的核心，这里是有梯度的！) ---
        # 文本过脑：提取 [CLS] (第 0 个位置) 汇聚全局语义
        text_out = self.roberta(input_ids=input_ids, attention_mask=attention_mask)
        text_features = text_out.last_hidden_state[:, 0, :] # 形状: [Batch, 768]
        
        # 声音过脑：提取全局平均池化汇聚全局声学
        audio_out = self.wavlm(audio_values)
        audio_features = audio_out.last_hidden_state.mean(dim=1) # 形状: [Batch, 768]

        # 套上序列维度伪装: [Batch, 1, 768] (为了兼容后面的注意力机制)
        v_t = text_features.unsqueeze(1)
        v_a = audio_features.unsqueeze(1)

        # --- 步骤 1: 自注意与跨界注意 ---
        v_tt, _ = self.attn_tt(query=v_t, key=v_t, value=v_t) 
        v_ta, _ = self.attn_ta(query=v_t, key=v_a, value=v_a) 
        v_aa, _ = self.attn_aa(query=v_a, key=v_a, value=v_a) 
        v_at, _ = self.attn_at(query=v_a, key=v_t, value=v_t) 

        # --- 步骤 2: 拼接与降维 ---
        u_t = self.fc_combine_t(torch.cat((v_tt, v_ta), dim=-1)).squeeze(1)
        u_a = self.fc_combine_a(torch.cat((v_aa, v_at), dim=-1)).squeeze(1)

        # --- 步骤 3: 计算门控权重 ---
        g_t = self.gate_t(u_t) 
        g_a = self.gate_a(u_a) 

        # --- 步骤 4: 动态融合 ---
        f_merge = (g_t * u_t) + (g_a * u_a)

        # --- 步骤 5: 终极考试，交答卷！ ---
        logits_merge = self.classifier_merge(f_merge) 
        logits_t = self.classifier_t(u_t)             
        logits_a = self.classifier_a(u_a)             
        
        return logits_merge, logits_t, logits_a