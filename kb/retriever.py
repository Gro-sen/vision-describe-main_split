import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# 全局缓存
_cached_model = None
_cached_index = None
_cached_meta = None

def load_index(index_path='kb/index/faiss_bge.index', 
               meta_path='kb/index/docs_bge.pkl', 
               model_name='BAAI/bge-small-zh-v1.5'):
    """加载索引、元数据和模型"""
    global _cached_model, _cached_index, _cached_meta

    if _cached_index is not None and _cached_meta is not None and _cached_model is not None:
        return _cached_index, _cached_meta, _cached_model

    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise FileNotFoundError('Index or metadata not found. Run indexing first.')

    # 加载索引
    _cached_index = faiss.read_index(index_path)

    # 加载元数据
    with open(meta_path, 'rb') as f:
        _cached_meta = pickle.load(f)
    
    # 加载模型
    _cached_model = SentenceTransformer(model_name)

    return _cached_index, _cached_meta, _cached_model

def query(query_text: str, top_k=5, similarity_threshold=0.3):
    """
    查询相似文档
    query_text: 查询字符串
    top_k: 返回相似文档数量
    similarity_threshold: 相似度阈值
    """
    index, meta, model = load_index()
    
    # BGE模型建议的查询格式
    instruction = "为这个句子生成表示以用于检索相关文章："
    query_with_instruction = instruction + query_text
    
    # 计算查询向量
    q_emb = model.encode([query_with_instruction], convert_to_numpy=True).astype('float32')
    
    # 检索（使用内积距离）
    distances, indices = index.search(q_emb, top_k)
    
    results = []
    for distance, idx in zip(distances[0], indices[0]):
        if idx < 0 or idx >= len(meta):
            continue
        
        # 将内积距离转换为相似度（内积范围[-1,1]，转换为[0,1]）
        similarity = (distance + 1) / 2.0
        
        if similarity >= similarity_threshold:
            results.append({
                'score': float(similarity),
                'source': meta[idx]['source'],
                'text': meta[idx]['text'].strip(),
                'distance': float(distance)
            })
    
    print(f"【检索】查询 '{query_text[:30]}...' 返回 {len(results)} 个结果")
    return results