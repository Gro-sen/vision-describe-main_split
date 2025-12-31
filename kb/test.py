from retriever import query

print("测试知识库检索系统:")
print("="*60)

test_queries = [
    "人员未佩戴工牌",
    "有人进入禁区",
    "发现火灾或烟雾",
    "电气设备有风险",
    "陌生人进入内部区域"
]

for q in test_queries:
    print(f"\n🔍 查询: '{q}'")
    
    try:
        results = query(q, top_k=3, similarity_threshold=0.3)
        
        if results:
            print(f"✅ 找到 {len(results)} 个结果:")
            for i, r in enumerate(results):
                print(f"  {i+1}. 相似度: {r['score']:.3f}")
                text_preview = r['text'][:80].replace('\n', ' ')
                print(f"      内容: {text_preview}...")
        else:
            print("⚠️  无相关结果")
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")

print("\n" + "="*60)
print("测试完成！")