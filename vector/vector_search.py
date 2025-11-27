import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # 读取 OPENAI_API_KEY

openai_key = os.getenv("OPENAI_API_KEY")
openbase_url = os.getenv("OPENAI_BASE_URL")

client_openai = OpenAI(base_url=openbase_url, api_key=openai_key);

# 初始化 ChromaDB
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection("text_docs")


def get_openai_embedding(text: str):
    """调用 OpenAI Embedding 模型"""
    response = client_openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def store_txt_to_chroma(txt_path: str, chunk_size: int = 500):
    """
    使用 OpenAI embeddings 将 txt 文件切分后写入 ChromaDB。

    参数：
        txt_path: txt 文件路径
        chunk_size: 每段文本字符长度
    """

    # 1. 读取 txt
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. 按固定长度切分
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

    # 3. 生成 embedding
    embeddings = [get_openai_embedding(chunk) for chunk in chunks]

    # 4. 写入 ChromaDB
    ids = [f"{os.path.basename(txt_path)}_{i}" for i in range(len(chunks))]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=[{"source": txt_path}] * len(chunks)
    )

    print(f"📁 已成功写入 {txt_path}，共 {len(chunks)} 段文本。")
def search_in_chroma(query: str, top_k: int = 5):
    """
    在 ChromaDB 中搜索最相似文本。
    """
    query_embedding = get_openai_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    print("\n🔍 搜索结果：")
    for i in range(top_k):
        print("=" * 60)
        print(f"Rank {i+1}")
        print("📄 文本片段：")
        print(results["documents"][0][i])
        print("📎 来源文件：", results["metadatas"][0][i]["source"])
        print("📏 距离：", results["distances"][0][i])

    return results