import json
import os
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from sentence_transformers import SentenceTransformer, util, CrossEncoder, losses, InputExample


BASE_DIR = Path(__file__).resolve().parent


def load_train_data(file_path: Path):
    """从 all_train_data.json 加载训练样本。"""
    if not file_path.exists():
        raise FileNotFoundError(f"找不到训练数据文件: {file_path}")
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    examples = []
    for item in data:
        texts = item.get("texts")
        label = item.get("label")
        if not isinstance(texts, list) or len(texts) != 2:
            continue
        if not isinstance(label, (int, float)):
            continue
        examples.append(InputExample(texts=texts, label=float(label)))
    return examples


def load_items(file_path: Path):
    """加载 QA 数据文件，返回 (items, questions)。"""
    if not file_path.exists():
        raise FileNotFoundError(f"找不到数据文件: {file_path}")
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    items = data if isinstance(data, list) else data.get("questions", data.get("data", []))
    if not isinstance(items, list):
        raise ValueError(f"{file_path} 格式不正确，预期为数组或包含 questions/data 字段。")
    questions = [str(it.get("question", "")).strip() for it in items if it.get("question")]
    return items, questions


def train_models(train_examples):
    """根据训练样本微调 Bi-Encoder 和 Cross-Encoder。"""
    print("正在加载预训练模型...")
    bi_model = SentenceTransformer("all-mpnet-base-v2")
    cross_model = CrossEncoder("BAAI/bge-reranker-base")

    if not train_examples:
        print("警告：训练样本为空，将直接使用原始预训练模型。")
        return bi_model, cross_model

    # Bi-Encoder：使用高置信度正样本进行 MNRL 训练
    bi_train_examples = [ex for ex in train_examples if ex.label > 0.8]
    if bi_train_examples:
        bi_train_dataloader = DataLoader(bi_train_examples, shuffle=True, batch_size=16)
        bi_train_loss = losses.MultipleNegativesRankingLoss(bi_model)
        print(f"正在使用 MNRL 微调 Bi-Encoder (样本数: {len(bi_train_examples)})...")
        bi_model.fit(
            train_objectives=[(bi_train_dataloader, bi_train_loss)],
            epochs=3,
            warmup_steps=max(1, len(bi_train_dataloader) // 10),
            show_progress_bar=True,
        )
    else:
        print("警告：没有 label>0.8 的样本，跳过 Bi-Encoder 微调。")

    # Cross-Encoder：使用所有样本进行分类训练
    cross_train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=8)
    print(f"正在微调 Cross-Encoder (样本数: {len(train_examples)})...")
    cross_model.fit(
        train_dataloader=cross_train_dataloader,
        epochs=3,
        warmup_steps=max(1, len(cross_train_dataloader) // 10),
        show_progress_bar=True,
    )

    return bi_model, cross_model


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
        else:
            self.parent[ry] = rx
            self.rank[rx] += 1


def merge_and_deduplicate(
    original_all_path,
    new_add_path,
    bi_model,
    cross_model,
    bi_threshold=0.91,
    cross_threshold=0.97,
    pairs_output=None,
):
    # 加载数据
    original_all_items, original_all_questions = load_items(original_all_path)
    new_add_items, new_add_questions = load_items(new_add_path)

    print(f"原始 all.json 问题数: {len(original_all_questions)}")
    print(f"待添加 add.json 问题数: {len(new_add_questions)}")

    original_all_len = len(original_all_questions)
    new_add_len = len(new_add_questions)

    if original_all_len + new_add_len == 0:
        print("没有可用于处理的问题，跳过。")
        return

    # Combine questions for semantic deduplication
    combined_questions = original_all_questions + new_add_questions
    total_combined_len = len(combined_questions)

    print(f"\n开始对 {total_combined_len} 条问题进行双层查重（all.json + add.json）...")

    # 第一层：Bi-Encoder 粗筛
    paraphrases = util.paraphrase_mining(bi_model, combined_questions, show_progress_bar=True, top_k=20)

    candidates = []
    bi_scores_map = {}
    for score, i, j in paraphrases:
        if score >= bi_threshold:
            candidates.append((i, j))
            bi_scores_map[(i, j)] = float(score)

    if not candidates:
        print("未发现初步相似的问题，all.json 不做修改。")
        return

    # 第二层：Cross-Encoder 精排
    print(f"精排模型介入，正在对比 {len(candidates)} 个候选对...")
    pairs = [[combined_questions[i], combined_questions[j]] for i, j in candidates]
    cross_scores = cross_model.predict(pairs)

    final_pairs = []
    for idx, final_score in enumerate(cross_scores):
        if final_score >= cross_threshold:
            i, j = candidates[idx]
            final_pairs.append(
                {
                    "confidence": round(float(final_score), 4),
                    "bi_score": round(bi_scores_map[(i, j)], 4),
                    "i": int(i),
                    "j": int(j),
                    "q1": combined_questions[i],
                    "q2": combined_questions[j],
                }
            )

    if not final_pairs:
        print("精排后未发现高置信度相似问题，all.json 不做修改。")
        return

    # 保存相似对结果，便于人工检查
    if pairs_output is not None:
        with pairs_output.open("w", encoding="utf-8") as f:
            json.dump(sorted(final_pairs, key=lambda x: x["confidence"], reverse=True), f, ensure_ascii=False, indent=2)
        print(f"相似问题对已保存至: {pairs_output}")

    # 基于相似对做聚类（并查集）
    uf = UnionFind(total_combined_len)
    for p in final_pairs:
        uf.union(p["i"], p["j"])

    clusters = {}
    for idx in range(total_combined_len):
        root = uf.find(idx)
        clusters.setdefault(root, []).append(idx)

    # 确定要添加哪些来自 new_add_items 的问题
    # 一个来自 new_add_items 的问题被保留，如果：
    # 1. 它不是 original_all_questions 中任何问题的重复。
    # 2. 它不是其他待添加的 new_add_questions 中的重复。
    
    kept_combined_indices = set() # 存储在 combined_questions 中要保留的索引

    for root, members in clusters.items():
        # 分离出 original_all_questions 和 new_add_questions 的成员
        current_original_all_members = [m for m in members if m < original_all_len]
        current_new_add_members = [m for m in members if m >= original_all_len]

        if current_original_all_members:
            # 如果簇中包含任何 original_all_question，则保留所有 original_all_questions
            # 并丢弃簇中所有 new_add_questions（它们是现有问题的重复）
            for idx in current_original_all_members:
                kept_combined_indices.add(idx)
        else:
            # 如果簇中只包含 new_add_questions，则只保留一个代表
            if current_new_add_members:
                # 选择索引最小的作为代表
                representative_idx = min(current_new_add_members)
                kept_combined_indices.add(representative_idx)
    
    # 过滤 new_add_items，只保留唯一的问题
    unique_new_add_items = []
    for i, item in enumerate(new_add_items):
        # 在 combined_questions 中，这个 new_add_item 的实际索引是 i + original_all_len
        combined_idx = i + original_all_len
        if combined_idx in kept_combined_indices:
            unique_new_add_items.append(item)

    # 构建最终的 all.json 数据
    final_all_items = list(original_all_items) + unique_new_add_items

    # 备份原 all.json 文件
    backup_path = original_all_path.with_name("all_backup_before_merge_add.json")
    if original_all_path.exists():
        os.replace(original_all_path, backup_path)
        print(f"原始 all.json 已备份至: {backup_path}")

    # 写回新的 all.json
    with original_all_path.open("w", encoding="utf-8") as f:
        json.dump(final_all_items, f, ensure_ascii=False, indent=2)

    print(f"\n合并与去重完成！")
    print(f"原始 all.json 问题数: {len(original_all_items)}")
    print(f"从 add.json 添加的唯一问题数: {len(unique_new_add_items)}")
    print(f"最终 all.json 问题数: {len(final_all_items)}")


def main():
    train_path = BASE_DIR / "all_train_data.json"
    all_path = BASE_DIR / "all.json"
    add_path = BASE_DIR / "add.json" # New file for added data
    pairs_output = BASE_DIR / "all_similar_pairs.json"

    print("1. 加载训练数据并微调模型...")
    train_examples = load_train_data(train_path)
    bi_model, cross_model = train_models(train_examples)

    print("\n2. 合并 add.json 中不重复的问题到 all.json 并进行去重...")
    merge_and_deduplicate(
        original_all_path=all_path,
        new_add_path=add_path,
        bi_model=bi_model,
        cross_model=cross_model,
        bi_threshold=0.91,
        cross_threshold=0.97,
        pairs_output=pairs_output,
    )


if __name__ == "__main__":
    main()

