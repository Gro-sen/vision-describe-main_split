import os
import json
from typing import List, Dict, Any
from datetime import datetime

class KnowledgeBase:
    """知识库管理类"""
    def __init__(self, base_dir="kb"):
        self.base_dir = base_dir
        self.source_dir = os.path.join(base_dir, "source")
        self.index_dir = os.path.join(base_dir, "index")
        self.cases_dir = os.path.join(base_dir, "cases")
        
        # 创建目录
        for dir_path in [self.source_dir, self.index_dir, self.cases_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def add_case(self, case_data: Dict[str, Any]) -> str:
        """添加报警案例到知识库"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        case_id = f"case_{timestamp}"
        
        case_file = os.path.join(self.cases_dir, f"{case_id}.json")
        
        # 添加元数据
        case_data.update({
            "case_id": case_id,
            "created_at": datetime.now().isoformat(),
            "reviewed": False,
            "review_result": None
        })
        
        with open(case_file, 'w', encoding='utf-8') as f:
            json.dump(case_data, f, ensure_ascii=False, indent=2)
        
        # 同时写入Markdown格式（供索引）
        from .auto_writer import write_alarm_case_to_kb
        write_alarm_case_to_kb(case_data)
        
        return case_id
    
    def get_similar_cases(self, query_text: str, top_k: int = 3, similarity_threshold: float = 0.3):
        """
        检索相似案例
        query_text: 查询文本
        top_k: 返回数量
        similarity_threshold: 相似度阈值
        """
        from .retriever import query
        
        results = query(query_text, top_k=top_k, similarity_threshold=similarity_threshold)
        
        # 转换为期望的格式
        formatted_results = []
        for result in results:
            formatted_results.append({
                "text": result.get("text", ""),
                "source": result.get("source", ""),
                "score": result.get("score", 0.0),
                "metadata": {
                    "chunk_type": "rule_chunk",
                    "retrieved_at": datetime.now().isoformat()
                }
            })
        
        return formatted_results
        
    def update_index(self):
        """更新知识库索引"""
        from .indexing import build_index
        result = build_index()
        return result
    
    def get_statistics(self) -> Dict:
        """获取知识库统计信息"""
        stats = {
            "total_cases": len([f for f in os.listdir(self.cases_dir) if f.endswith('.json')]) if os.path.exists(self.cases_dir) else 0,
            "total_documents": len([f for f in os.listdir(self.source_dir) if f.endswith('.md')]) if os.path.exists(self.source_dir) else 0,
            "index_exists": os.path.exists(os.path.join(self.index_dir, "faiss_bge.index")) if os.path.exists(self.index_dir) else False,
            "last_update": None,
            "status": "ready"
        }
        
        # 获取最后更新时间
        index_file = os.path.join(self.index_dir, "faiss_bge.index")
        if os.path.exists(index_file):
            stats["last_update"] = datetime.fromtimestamp(
                os.path.getmtime(index_file)
            ).strftime("%Y-%m-%d %H:%M:%S")
        
        return stats
    
    def check_index_health(self):
        """检查索引健康状况"""
        import os
        
        index_file = os.path.join(self.index_dir, "faiss_bge.index")
        meta_file = os.path.join(self.index_dir, "docs_bge.pkl")
        
        if not os.path.exists(index_file) or not os.path.exists(meta_file):
            return {"status": "missing", "message": "索引文件不存在"}
        
        try:
            from .retriever import load_index
            index, meta, model = load_index()
            return {
                "status": "healthy",
                "index_size": index.ntotal,
                "meta_count": len(meta) if meta else 0
            }
        except Exception as e:
            return {"status": "corrupted", "message": str(e)}

# 创建全局知识库实例
kb_instance = KnowledgeBase()

# 导出常用别名
KnowledgeBase = KnowledgeBase
kb = kb_instance