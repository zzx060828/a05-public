import torch
from sentence_transformers import SentenceTransformer, util, CrossEncoder

class SemanticDeduplicator:
    def __init__(self, bi_model_name: str = "all-mpnet-base-v2", cross_model_name: str = "BAAI/bge-reranker-base"):
        print("\n[系统启动] 正在加载查重 AI 模型 (这可能需要十几秒)...")
        self.bi_model = SentenceTransformer(bi_model_name)
        self.cross_model = CrossEncoder(cross_model_name)
        print("[系统启动] AI 模型加载完成！")

    def is_semantically_duplicate(self, query_text: str, candidate_texts: list[str], 
                                  bi_threshold: float = 0.85, cross_threshold: float = 0.95):
        # 1. 如果题库是空的，直接返回不重复
        if not candidate_texts:
            return False, 0.0, ""

        # ==========================================
        # 第一阶段：Bi-Encoder 粗筛 (速度快)
        # ==========================================
        query_embedding = self.bi_model.encode(query_text, convert_to_tensor=True)
        candidate_embeddings = self.bi_model.encode(candidate_texts, convert_to_tensor=True)

        # 计算余弦相似度
        bi_scores = util.cos_sim(query_embedding, candidate_embeddings)[0]

        potential_duplicates = []
        for i, score in enumerate(bi_scores):
            if score >= bi_threshold:
                potential_duplicates.append(candidate_texts[i])
        
        # 如果粗筛没发现相似的，直接返回不重复
        if not potential_duplicates:
            return False, 0.0, ""

        # ==========================================
        # 第二阶段：Cross-Encoder 精排 (精度高)
        # ==========================================
        # 构造 Cross-Encoder 输入对：[[新题, 疑似旧题1], [新题, 疑似旧题2]]
        cross_input_pairs = [[query_text, cand] for cand in potential_duplicates]
        cross_scores = self.cross_model.predict(cross_input_pairs)

        # 找到分数最高的那一道题
        best_score_idx = cross_scores.argmax() # 获取最高分的索引
        best_score = float(cross_scores[best_score_idx])
        best_match_text = potential_duplicates[best_score_idx]

        # 如果最高分超过了你设定的阈值，就判定为重复！
        if best_score >= cross_threshold:
            print(f"[AI查重] 发现重复: '{query_text}' <--> '{best_match_text}' (相似度: {best_score:.2f})")
            # 返回: (是否重复, 相似度分数, 匹配到的原题)
            return True, best_score, best_match_text
        
        # 分数不够，不算重复
        return False, 0.0, ""


# 🌟 关键点：在这里实例化一次！这样整个后端启动时只会加载一次模型
deduplicator_instance = SemanticDeduplicator()