# test_full_reasoning.py
from dotenv import load_dotenv
load_dotenv()
from reasoning_model import reasoning_model
import json

def test_reasoning_with_kb():
    """测试推理模型使用知识库"""
    
    print("测试推理模型 + 知识库检索")
    print("="*60)
    
    # 模拟视觉分析结果
    vision_facts = {
        "has_person": True,
        "badge_status": "未佩戴",
        "enter_restricted_area": False,
        "has_fire_or_smoke": False,
        "has_electric_risk": False,
        "scene_summary": "画面中有一名人员未佩戴工牌，在办公区域走动",
        "object_details": {
            "person_count": 1,
            "person_positions": ["画面中央"],
            "environment_status": "正常"
        }
    }
    
    print("视觉分析结果:")
    print(json.dumps(vision_facts, indent=2, ensure_ascii=False))
    print()
    
    # 执行推理
    print("开始推理...")
    result = reasoning_model.infer(vision_facts)
    
    print("\n推理结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 检查是否使用了知识库
    kb_cases_used = result.get("metadata", {}).get("kb_cases_used", 0)
    if kb_cases_used > 0:
        print(f"\n✅ 成功使用了 { kb_cases_used} 个知识库案例")
    else:
        print("\n⚠️  未使用知识库案例")
    
    return result

if __name__ == "__main__":
    test_reasoning_with_kb()