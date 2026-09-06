import os
import json
import chromadb
from zhipuai import ZhipuAI


API_KEY = os.environ.get("ZHIPUAI_API_KEY", "")
client = ZhipuAI(api_key=API_KEY)


current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "my_vector_db")
chroma_client = chromadb.PersistentClient(path=db_path)


resource_collection = chroma_client.get_or_create_collection(name="learning_resources")
json_file_path = os.path.join(current_dir, "learning_resources.json")

try:
    with open(json_file_path, "r", encoding="utf-8") as f:
        resources_data = json.load(f)
    print(f"成功从外部文件加载了 {len(resources_data)} 条学习资源！准备入库...")
except Exception as e:
    print(f"读取 JSON 文件失败，请检查文件名和路径: {e}")
    exit() # 如果读取失败，直接停止运行

def get_embedding(text):
    """调用智谱大模型生成向量"""
    response = client.embeddings.create(model="embedding-2", input=text)
    return response.data[0].embedding

print(f"🚀 开始将 {len(resources_data)} 条学习资源灌入 ChromaDB 向量库...")

# 遍历数据，生成向量并入库
for idx, item in enumerate(resources_data):
    role = item["role"]
    core_entity = item["core_entity"]
    markdown_content = item["learning_resources"]
    
    # 架构核心：我们只把 core_entity（核心知识点）变成向量，这样搜索最精准！
    # 加上 role 前缀，能让搜索在向量空间里聚类得更好
    search_text = f"[{role}] 技术知识点：{core_entity}"
    vec = get_embedding(search_text)
    
    # 生成一个唯一 ID
    doc_id = f"resource_{role}_{idx}"
    
    try:
        resource_collection.add(
            ids=[doc_id],
            embeddings=[vec],
            documents=[core_entity], 
            metadatas=[{
                "role": role, 
                "markdown_content": markdown_content # 把那一大坨极其详细的 Markdown 全存在 metadata 里！
            }]
        )
        print(f"✅ 成功入库: {core_entity}")
    except Exception as e:
        print(f"❌ 入库失败 {core_entity}: {e}")

print("🎉 所有学习资源灌入完毕！系统 RAG 知识锦囊已就绪！")
