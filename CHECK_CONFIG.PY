# verify_kb_usage.py
import json
import os
from datetime import datetime

def verify_kb_usage():
    """验证知识库使用情况"""
    print("="*60)
    print("知识库使用情况验证")
    print("="*60)
    
    # 1. 检查推理日志
    print("\n1. 检查推理日志...")
    if os.path.exists("reasoning_debug.log"):
        with open("reasoning_debug.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            kb_mentions = [l for l in lines if "知识库" in l or "kb_cases" in l]
            print(f"  找到 {len(kb_mentions)} 处知识库相关记录")
            for line in kb_mentions[-5:]:  # 显示最近5条
                print(f"  - {line.strip()}")
    else:
        print("  未找到推理日志文件")
    
    # 2. 检查模型原始输出
    print("\n2. 检查模型原始输出...")
    if os.path.exists("model_raw_outputs.log"):
        with open("model_raw_outputs.log", "r", encoding="utf-8") as f:
            content = f.read()
            sections = content.split("="*60)
            latest_section = sections[-1] if sections else ""
            if "案例" in latest_section:
                print("  ✅ 最新推理中提到了案例")
            else:
                print("  ⚠️  最新推理中未明确提到案例")
    
    # 3. 检查知识库索引状态
    print("\n3. 检查知识库索引状态...")
    index_files = [
        "kb/index/faiss_bge.index",
        "kb/index/docs_bge.pkl"
    ]
    for file in index_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024  # KB
            print(f"  {file}: {size:.1f} KB")
        else:
            print(f"  {file}: 不存在")
    
    # 4. 检查知识库源文件
    print("\n4. 检查知识库源文件...")
    kb_source_dir = "kb/source"
    if os.path.exists(kb_source_dir):
        md_files = [f for f in os.listdir(kb_source_dir) if f.endswith(".md")]
        print(f"  找到 {len(md_files)} 个知识库源文件")
        
        # 分析最近的文件
        if md_files:
            md_files.sort(key=lambda x: os.path.getmtime(os.path.join(kb_source_dir, x)))
            recent_files = md_files[-3:]  # 最近3个文件
            print("  最近3个案例文件:")
            for file in recent_files:
                path = os.path.join(kb_source_dir, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "参考了" in content:
                        lines = content.split("\n")
                        for line in lines:
                            if "参考了" in line:
                                print(f"    {file}: {line.strip()}")
                                break
    
    # 5. 运行测试查询
    print("\n5. 运行测试查询...")
    try:
        from kb.retriever import query
        test_queries = ["人员未佩戴工牌", "进入禁区", "火灾烟雾"]
        for q in test_queries:
            results = query(q, top_k=2, similarity_threshold=0.3)
            print(f"  查询 '{q}': 返回 {len(results)} 个结果")
            if results:
                for i, r in enumerate(results):
                    print(f"    结果{i+1}: 相似度={r['score']:.4f}, "
                          f"来源={r['source']}")
    except Exception as e:
        print(f"  测试查询失败: {e}")
    
    print("\n" + "="*60)
    print("验证完成")

def analyze_case_usage():
    """分析案例使用模式"""
    print("\n" + "="*60)
    print("案例使用模式分析")
    print("="*60)
    
    # 从保存的案例中提取kb_cases_used信息
    case_stats = []
    kb_source_dir = "kb/source"
    
    if os.path.exists(kb_source_dir):
        for file in os.listdir(kb_source_dir):
            if file.endswith(".md"):
                path = os.path.join(kb_source_dir, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    # 提取案例ID
                    case_id = None
                    for line in content.split("\n"):
                        if "案例ID" in line:
                            parts = line.split(":")
                            if len(parts) > 1:
                                case_id = parts[1].strip()
                                break
                    
                    # 提取参考案例数
                    kb_used = 0
                    for line in content.split("\n"):
                        if "参考了" in line and "个历史案例" in line:
                            import re
                            match = re.search(r'参考了\s*(\d+)\s*个历史案例', line)
                            if match:
                                kb_used = int(match.group(1))
                                break
                    
                    if case_id:
                        case_stats.append({
                            "case_id": case_id,
                            "kb_used": kb_used,
                            "file": file
                        })
    
    if case_stats:
        print(f"分析 {len(case_stats)} 个案例:")
        
        # 统计
        total_cases = len(case_stats)
        cases_with_kb = sum(1 for s in case_stats if s["kb_used"] > 0)
        avg_kb_used = sum(s["kb_used"] for s in case_stats) / total_cases
        
        print(f"  - 总案例数: {total_cases}")
        print(f"  - 使用知识库的案例: {cases_with_kb} ({cases_with_kb/total_cases*100:.1f}%)")
        print(f"  - 平均参考案例数: {avg_kb_used:.2f}")
        
        # 显示使用知识库的案例
        print("\n  使用知识库的案例:")
        for stat in case_stats:
            if stat["kb_used"] > 0:
                print(f"    {stat['case_id']}: 参考了 {stat['kb_used']} 个案例")
    else:
        print("未找到案例统计信息")

if __name__ == "__main__":
    verify_kb_usage()
    analyze_case_usage()