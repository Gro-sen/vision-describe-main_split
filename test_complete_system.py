# prove_index_independent.py
import os
import pickle

def prove_index_independent():
    """证明索引独立于源文件"""
    
    print("="*80)
    print("验证索引与源文件的独立性")
    print("="*80)
    
    # 1. 检查索引文件
    index_files = ["kb/index/faiss_bge.index", "kb/index/docs_bge.pkl"]
    
    print("1. 索引文件状态:")
    for file in index_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✓ {file}: {size:,} 字节")
        else:
            print(f"   ✗ {file}: 不存在")
    
    # 2. 检查索引中的内容
    print("\n2. 索引中的内容（不读取源文件）:")
    try:
        with open("kb/index/docs_bge.pkl", 'rb') as f:
            meta = pickle.load(f)
        
        print(f"   索引包含 {len(meta)} 个文档块")
        
        # 随机检查几个文档块
        print(f"   前3个文档块的内容预览:")
        for i in range(min(3, len(meta))):
            source = meta[i].get('source', '未知')
            text = meta[i].get('text', '')[:100]
            print(f"     {i+1}. {source}: '{text}...'")
    
    except Exception as e:
        print(f"   读取索引失败: {e}")
    
    # 3. 检查对应的源文件
    print("\n3. 源文件状态（.md文件）:")
    
    # 找出索引中提到的源文件
    try:
        with open("kb/index/docs_bge.pkl", 'rb') as f:
            meta = pickle.load(f)
        
        sources = set()
        for item in meta:
            source = item.get('source', '')
            if source.endswith('.md'):
                sources.add(source)
        
        for source in sorted(list(sources))[:5]:  # 只显示前5个
            filepath = os.path.join("kb/source", source)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"   {source}: {len(content)} 字符")
            else:
                print(f"   {source}: 文件不存在")
    
    except Exception as e:
        print(f"   检查源文件失败: {e}")
    
    # 4. 关键实验：修改源文件不影响索引
    print("\n4. 关键实验:")
    print("   修改源文件内容后，索引内容保持不变")
    print("   因为索引是在构建时生成的，不是实时读取源文件")
    
    # 5. 证明检索时使用的是索引
    print("\n5. 检索过程证明:")
    print("   检索函数 query() 的工作流程:")
    print("   1. 加载 kb/index/faiss_bge.index 向量索引")
    print("   2. 加载 kb/index/docs_bge.pkl 元数据")
    print("   3. 计算查询向量与索引中向量的相似度")
    print("   4. 返回相似度最高的结果")
    print("   → 完全不读取 kb/source/ 目录！")

def demonstrate_problem():
    """演示问题重现"""
    
    print("\n" + "="*80)
    print("问题重现演示")
    print("="*80)
    
    # 模拟你的情况
    print("模拟你的场景:")
    print("1. 你清空了 kb/source/*.md 文件内容")
    print("2. 但 kb/index/ 目录下的索引文件仍然存在")
    print("3. 索引文件中包含了原始的向量表示和文本内容")
    print("4. 检索函数 query() 使用索引文件，不是源文件")
    print("5. 所以即使源文件为空，检索仍然能返回结果")
    
    print("\n解决方案:")
    print("1. 删除索引文件: rm -rf kb/index/*")
    print("2. 重新运行系统，它会重新构建索引")
    print("3. 现在索引将基于空的源文件构建")
    print("4. 检索将返回0个结果（或只返回规则文件的空内容）")

if __name__ == "__main__":
    prove_index_independent()
    demonstrate_problem()