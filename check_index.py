# test_accurate_kb_count.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def simulate_retrieval():
    """模拟检索结果"""
    
    # 模拟检索结果（基于你的索引内容）
    simulated_results = [
        {
            'source': 'personnel.md',
            'score': 0.8621,
            'text': '# 人员安防监测规则...'
        },
        {
            'source': 'restricted.md', 
            'score': 0.8176,
            'text': '# 禁区与越界行为监测规则...'
        },
        {
            'source': 'environment.md',
            'score': 0.7771,
            'text': '# 环境与安全风险监测规则...'
        }
    ]
    
    print("模拟检索结果:")
    print("="*80)
    
    rule_files = []
    history_cases = []
    
    for result in simulated_results:
        source = result['source']
        if 'case_' in source:
            history_cases.append(result)
            type_str = "📁 历史案例"
        elif source.endswith('.md'):
            rule_files.append(result)
            type_str = "📚 规则文件"
        else:
            history_cases.append(result)
            type_str = "❓ 其他"
        
        print(f"{type_str}: {source} (相似度: {result['score']:.4f})")
    
    print(f"\n统计:")
    print(f"  总文档数: {len(simulated_results)}")
    print(f"  规则文件: {len(rule_files)}")
    print(f"  历史案例: {len(history_cases)}")
    
    # 建议的显示方式
    print(f"\n建议显示:")
    print(f"  ❌ 旧方式: '参考了 {len(simulated_results)} 个历史案例' (不准确)")
    print(f"  ✅ 新方式: '参考了 {len(rule_files)} 个规则文件' (准确)")
    
    if len(history_cases) > 0:
        print(f"  ✅ 新方式: '参考了 {len(history_cases)} 个历史案例和 {len(rule_files)} 个规则文件'")

if __name__ == "__main__":
    simulate_retrieval()