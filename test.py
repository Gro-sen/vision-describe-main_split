# test_all_cases_relevance.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_all_cases():
    """测试所有案例与当前查询的相关性"""
    
    from kb.retriever import query
    
    # 与你的测试相同的查询
    query_text = "人员 工牌异常 画面中有一名人员未佩戴工牌，在办公区域走动"
    
    print("="*80)
    print(f"测试查询: '{query_text}'")
    print("="*80)
    
    # 尝试不同的top_k值
    for top_k in [3, 5, 10]:
        print(f"\n🔍 使用 top_k={top_k}:")
        results = query(query_text, top_k=top_k, similarity_threshold=0.2)  # 降低阈值
        
        if results:
            print(f"  返回 {len(results)} 个结果:")
            for i, result in enumerate(results):
                source = result.get('source', '未知')
                score = result.get('score', 0)
                text_preview = result.get('text', '')[:80]
                
                if 'case_' in source:
                    type_str = "📁 历史案例"
                elif source.endswith('.md'):
                    type_str = "📚 规则文件"
                else:
                    type_str = "❓ 其他"
                
                print(f"    {i+1}. {type_str}: {source}")
                print(f"        相似度: {score:.4f}")
                if score < 0.3:
                    print(f"        ⚠️  相似度低于阈值 (0.3)")
                print(f"        预览: {text_preview}...")
        else:
            print("  没有结果")
    
    # 检查知识库中有多少案例文件
    print("\n" + "="*80)
    print("知识库源文件统计:")
    print("="*80)
    
    source_dir = "kb/source"
    if os.path.exists(source_dir):
        files = os.listdir(source_dir)
        case_files = [f for f in files if f.startswith('case_') and f.endswith('.md')]
        rule_files = [f for f in files if f.endswith('.md') and not f.startswith('case_')]
        
        print(f"总文件数: {len(files)}")
        print(f"历史案例文件: {len(case_files)}")
        print(f"规则文件: {len(rule_files)}")
        
        print("\n历史案例文件列表:")
        for case_file in sorted(case_files):
            filepath = os.path.join(source_dir, case_file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取案例标题或场景
            scene_summary = "未知"
            for line in content.split('\n'):
                if "场景概述" in line:
                    # 下一行通常是场景描述
                    lines = content.split('\n')
                    idx = lines.index(line)
                    if idx + 1 < len(lines):
                        scene_summary = lines[idx + 1].strip()
                        break
                elif "场景描述" in line:
                    scene_summary = line.split(":")[-1].strip()
                    break
            
            print(f"  📄 {case_file}")
            print(f"    场景: {scene_summary[:50]}...")

def check_case_content():
    """检查案例文件内容"""
    
    print("\n" + "="*80)
    print("检查案例文件内容")
    print("="*80)
    
    source_dir = "kb/source"
    case_files = [f for f in os.listdir(source_dir) if f.startswith('case_') and f.endswith('.md')]
    
    for case_file in case_files[:5]:  # 只检查前5个
        filepath = os.path.join(source_dir, case_file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n📄 {case_file}:")
        
        # 检查内容长度
        print(f"  文件大小: {len(content)} 字符")
        
        # 查找关键字段
        import re
        
        # 检查是否有报警级别
        alarm_match = re.search(r'报警级别\s*[:：]\s*(.+)', content)
        if alarm_match:
            print(f"  报警级别: {alarm_match.group(1).strip()}")
        
        # 检查是否有场景描述
        scene_match = re.search(r'场景概述\s*\n\s*(.+)', content)
        if scene_match:
            scene = scene_match.group(1).strip()
            print(f"  场景描述: {scene[:50]}...")
        
        # 检查是否有相似案例字段
        kb_match = re.search(r'参考了\s*(\d+)\s*个历史案例', content)
        if kb_match:
            print(f"  参考案例数: {kb_match.group(1)}")

if __name__ == "__main__":
    test_all_cases()
    check_case_content()