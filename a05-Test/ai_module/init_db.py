import json
import chromadb
from zhipuai import ZhipuAI
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

api_key = os.getenv("ZHIPUAI_API_KEY")
if not api_key:
    raise RuntimeError("缺少环境变量 ZHIPUAI_API_KEY，请参考 .env.example 配置")
zhipu_client = ZhipuAI(api_key=api_key)
chroma_client = chromadb.PersistentClient(path="./my_vector_db")

try:
    chroma_client.delete_collection(name="interview_questions")
    chroma_client.delete_collection(name="behavior_questions") # 顺便清理旧的行为题库
except Exception:
    pass

tech_collection = chroma_client.get_or_create_collection(name="interview_questions")
behavior_collection = chroma_client.get_or_create_collection(name="behavior_questions")

def get_embedding(text): 
    # 计算向量
    response = zhipu_client.embeddings.create(
        model="embedding-2",
        input=text
    )
    return response.data[0].embedding


def import_to_collection(json_file_path: str, target_collection, collection_name: str):
    if not os.path.exists(json_file_path):
        print(f"⚠️ 找不到文件 {json_file_path}，跳过导入【{collection_name}】。")
        return

    with open(json_file_path, "r", encoding="utf-8") as f:  
        data = json.load(f)
        
    print(f"\n=========================================")
    print(f"🚀 正在向【{collection_name}】导入 {len(data)} 条数据 (来源: {json_file_path})...")
    print(f"=========================================")
    
    for item in data:
        vec = get_embedding(item["question"])
        meta = {
            "role": item.get("role", "General"), # 行为题如果没有特指岗位，可以默认 General
            "core_entity": item.get("core_entity", ""),
            "difficulty": item.get("difficulty", "未知"),
            "question_type": item.get("question_type", "knowledge"),
            "question": item.get("question", ""),
            "expression_analysis_hint": item.get("expression_analysis_hint", ""),
            "multimodal_hint": item.get("multimodal_hint", ""),
            # 复杂结构转为字符串
            "expected_answer_points": json.dumps(item.get("expected_answer_points", []), ensure_ascii=False),
            "entities": json.dumps(item.get("entities", []), ensure_ascii=False),
            "scoring_points": json.dumps(item.get("scoring_points", []), ensure_ascii=False),
            "follow_up_triggers": json.dumps(item.get("follow_up_triggers", {}), ensure_ascii=False)
        }
        
        target_collection.add(
            ids=[item["id"]],
            embeddings=[vec],
            documents=[item["answer"]],
            metadatas=[meta]
        )
        print(f"✅ 已成功导入: {item['id']}")

if __name__ == "__main__":
    # 3. 依次执行两次导入任务
    
    # 第一步：把技术题导入主库
    import_to_collection(
        json_file_path="all.json", 
        target_collection=tech_collection, 
        collection_name="interview_questions"
    )
    # 第二步：把行为题导入专用库
    import_to_collection(
        json_file_path="behavior_questions.json", 
        target_collection=behavior_collection, 
        collection_name="behavior_questions"
    )
    
    print("\n🎉 所有题库初始化并导入完成！")
