import json
import os
from openai import OpenAI
from tqdm import tqdm # 导入 tqdm 库
from dotenv import load_dotenv

import torch
from sentence_transformers import SentenceTransformer, util, CrossEncoder

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise RuntimeError("缺少环境变量 DEEPSEEK_API_KEY，请参考 .env.example 配置")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

MODEL_NAME = "deepseek-reasoner" # 或 deepseek-coder, 根据您的需求选择合适的模型

class SemanticDeduplicator:
    def __init__(self, bi_model_name: str = "all-mpnet-base-v2", cross_model_name: str = "BAAI/bge-reranker-base"):
        print("\n[语义去重模块] 正在初始化 SemanticDeduplicator...")
        print(f"[语义去重模块] 正在加载 Bi-Encoder 模型: {bi_model_name}...")
        self.bi_model = SentenceTransformer(bi_model_name)
        print(f"[语义去重模块] 正在加载 Cross-Encoder 模型: {cross_model_name}...")
        self.cross_model = CrossEncoder(cross_model_name)
        print("[语义去重模块] SemanticDeduplicator 初始化完成。")

    def is_semantically_duplicate(self, query_text: str, candidate_texts: list[str], 
                                  bi_threshold: float = 0.85, cross_threshold: float = 0.95) -> bool:
        if not candidate_texts:
            return False

        # Bi-Encoder 粗筛
        query_embedding = self.bi_model.encode(query_text, convert_to_tensor=True)
        candidate_embeddings = self.bi_model.encode(candidate_texts, convert_to_tensor=True)

        # 计算余弦相似度
        bi_scores = util.cos_sim(query_embedding, candidate_embeddings)[0]

        potential_duplicates = []
        for i, score in enumerate(bi_scores):
            if score >= bi_threshold:
                potential_duplicates.append(candidate_texts[i])
        
        if not potential_duplicates:
            return False

        # Cross-Encoder 精排
        # 构造 Cross-Encoder 输入对：[query, candidate]
        cross_input_pairs = [[query_text, cand] for cand in potential_duplicates]
        cross_scores = self.cross_model.predict(cross_input_pairs)

        for score in cross_scores:
            if score >= cross_threshold:
                print(f"[语义去重模块] 发现语义重复: '{query_text}' 与 '{potential_duplicates[cross_scores.tolist().index(score)]}' (Cross-Score: {score:.2f})")
                return True
        
        return False

def deepseek_r1_generate_resources(role: str, core_entity: str) -> str:
    prompt = f"""你是一名资深的技术专家和学习规划师。请为一名担任“{role}”的专业人士，针对核心技术实体“{core_entity}”，生成一份详细的学习资料推荐清单。
要求包含：
- **推荐网站**：至少2个相关的、高质量的网站链接（包括名称和URL）。
- **推荐书籍**：至少1本经典或最新的技术书籍（包括书名和作者）。
- **推荐在线教程**：至少3个优质的在线视频课程或平台推荐（注明平台和内容概述）。

请以清晰的Markdown格式输出，并确保所有推荐内容与“{core_entity}”高度相关，且适合“{role}”的专业学习。"""
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            stream=False # For a single, complete response
        )
        generated_text = response.choices[0].message.content
        return generated_text
    except Exception as e:
        print(f"调用 DeepSeek 模型失败: {e}")
        return f"未能通过 DeepSeek 模型为 {core_entity} 生成学习资料。错误：{e}"

def process_input_and_generate_resources(input_json_path: str, all_json_path: str, learning_resources_output_path: str):
    if not os.path.exists(input_json_path):
        print(f"错误：输入文件 '{input_json_path}' 不存在。")
        return

    print(f"[开始] 正在读取输入文件: {input_json_path}")
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data_from_input = json.load(f)
    print(f"[完成] 已读取 {len(data_from_input)} 条核心实体数据。")

    # 初始化语义去重器
    print("[主程序] 正在初始化语义去重器...")
    deduplicator = SemanticDeduplicator() 
    print("[主程序] 语义去重器初始化完成。")

    # 读取 all.json 中的现有数据 (只包含 role 和 core_entity)
    existing_all_data = [] # 存储所有唯一的 role 和 core_entity 对
    if os.path.exists(all_json_path):
        with open(all_json_path, 'r', encoding='utf-8') as f:
            try:
                existing_all_data = json.load(f)
            except json.JSONDecodeError:
                print(f"[警告] all.json 文件内容无效，将作为空文件处理: {all_json_path}")
                existing_all_data = []
    print(f"[完成] 已从 {all_json_path} 读取 {len(existing_all_data)} 条现有 role/core_entity 数据。")

    # 为语义去重准备现有文本列表
    existing_texts_for_semantic_check = [
        f"{item.get('role', '')}: {item.get('core_entity', '')}"
        for item in existing_all_data
    ]

    # 存储最终生成的学习资料，用于写入 learning_resources_output_path
    generated_learning_resources = []
    if os.path.exists(learning_resources_output_path):
        with open(learning_resources_output_path, 'r', encoding='utf-8') as f:
            try:
                generated_learning_resources = json.load(f)
            except json.JSONDecodeError:
                print(f"[警告] {learning_resources_output_path} 文件内容无效，将作为空文件处理。")
                generated_learning_resources = []
    print(f"[完成] 已从 {learning_resources_output_path} 读取 {len(generated_learning_resources)} 条现有学习资料数据。")

    # 辅助函数：检查是否已存在该 (role, core_entity) 的学习资料
    def has_generated_resource(role: str, core_entity: str, existing_resources: list) -> bool:
        for resource in existing_resources:
            if resource.get('role') == role and resource.get('core_entity') == core_entity:
                return True
        return False

    newly_added_to_all_json_count = 0
    newly_generated_resources_count = 0
    processed_items_count = 0

    print("[进行中] 正在处理输入并生成学习资料...")
    for item in tqdm(data_from_input, desc="处理输入并生成资料"):
        processed_items_count += 1
        role = item.get('role', '未知角色')
        core_entity = item.get('core_entity', '未知核心实体')
        
        if not role or not core_entity:
            tqdm.write(f"[警告] 忽略无效条目 (缺少 role 或 core_entity): {item}")
            continue

        query_text = f"{role}: {core_entity}"
        tqdm.write(f"  -> 正在检查新条目：[角色: {role}] [核心实体: {core_entity}]")

        # 首先检查当前项是否已经存在于 all.json 中（语义层面）
        is_duplicate = deduplicator.is_semantically_duplicate(query_text, existing_texts_for_semantic_check)

        if is_duplicate:
            tqdm.write(f"[已存在] 语义上重复: '{query_text}' 已存在于 {all_json_path} 中，跳过处理和生成资料。")
        else:
            # 如果不重复，则添加到 all.json 的内存表示中
            new_unique_pair = {'role': role, 'core_entity': core_entity}
            existing_all_data.append(new_unique_pair)
            existing_texts_for_semantic_check.append(query_text) # 更新去重检查列表
            newly_added_to_all_json_count += 1
            tqdm.write(f"[添加至 all.json] '{query_text}' 已标记为唯一。")

            # 在调用 DeepSeek 模型之前，检查是否已存在学习资料
            if has_generated_resource(role, core_entity, generated_learning_resources):
                tqdm.write(f"[已存在学习资料] 为 '{query_text}' 的学习资料已存在于 {learning_resources_output_path} 中，跳过生成。")
            else:
                tqdm.write(f"[准备生成] 为 '{query_text}' 调用大语言模型生成学习资料。")
                # 调用 DeepSeek 模型生成学习资料
                resources = deepseek_r1_generate_resources(role, core_entity)
                
                # 构建要添加到 learning_resources_output_path 的新条目
                new_learning_resource_entry = {
                    'role': role,
                    'core_entity': core_entity,
                    'learning_resources': resources
                }
                generated_learning_resources.append(new_learning_resource_entry)
                newly_generated_resources_count += 1
                tqdm.write(f"[资料生成成功] 为 '{query_text}' 生成了学习资料，已添加至 {learning_resources_output_path} 的内存表示。")
    
    print(f"\n[开始] 正在保存更新后的 {all_json_path}")
    with open(all_json_path, 'w', encoding='utf-8') as f:
        json.dump(existing_all_data, f, ensure_ascii=False, indent=4)
    print(f"[完成] {all_json_path} 已成功更新。共添加 {newly_added_to_all_json_count} 条唯一 role/core_entity 数据。")

    print(f"\n[开始] 正在保存生成的学习资料到 {learning_resources_output_path}")
    with open(learning_resources_output_path, 'w', encoding='utf-8') as f:
        json.dump(generated_learning_resources, f, ensure_ascii=False, indent=4)
    print(f"[完成] {learning_resources_output_path} 已成功更新。共生成 {newly_generated_resources_count} 条学习资料。")

    print(f"\n处理完成。共处理 {processed_items_count} 条输入数据。")

if __name__ == "__main__":
    input_file = "d:\\A05\\Repeat\\sample_input.json"
    all_file = "d:\\A05\\Repeat\\all.json"
    learning_resources_file = "d:\\A05\\Repeat\\learning_resources.json"
    process_input_and_generate_resources(input_file, all_file, learning_resources_file)
