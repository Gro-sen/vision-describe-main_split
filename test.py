# test_minimal_retrieval.py
import sys

def minimal_test():
    """最小化测试，排除所有可能的干扰"""
    print("最小化知识库检索测试")
    print("="*50)
    
    try:
        # 直接导入retriever模块
        sys.path.insert(0, '.')
        from kb.retriever import query
        
        print("1. 导入模块成功")
        
        # 设置超时
        import threading
        import queue
        
        result_queue = queue.Queue()
        error_queue = queue.Queue()
        
        def run_query():
            try:
                results = query("人员未佩戴工牌", top_k=3)
                result_queue.put(results)
            except Exception as e:
                error_queue.put(e)
        
        print("2. 启动查询线程...")
        thread = threading.Thread(target=run_query)
        thread.daemon = True
        thread.start()
        
        # 等待30秒
        print("3. 等待查询完成...")
        for i in range(30):
            if not thread.is_alive():
                break
            print(f"   等待 {i+1}/30 秒...")
            thread.join(timeout=1)
        
        if thread.is_alive():
            print("❌ 查询超时（30秒）")
            return
        
        if not error_queue.empty():
            error = error_queue.get()
            print(f"❌ 查询错误: {error}")
            return
        
        results = result_queue.get()
        print(f"✅ 查询成功！")
        print(f"   返回 {len(results)} 个结果")
        
        for i, r in enumerate(results):
            print(f"   {i+1}. {r['source']} - {r['score']:.3f}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    minimal_test()