# test_fix.py
from dotenv import load_dotenv
load_dotenv()
from reasoning_model import reasoning_model

def test_fix():
    """测试修复后的效果"""
    
    # 模拟视觉分析结果
    vision_facts = {
        "has_person": True,
        "badge_status": "无法确认",
        "enter_restricted_area": False,
        "has_fire_or_smoke": False,
        "has_electric_risk": False,
        "scene_summary": "一名男子在室内低头看东西，环境为普通房间。"
    }
    
    print("🧪 测试推理模型修正...")
    print(f"输入视觉事实: {vision_facts['scene_summary']}")
    
    result = reasoning_model.infer(vision_facts)
    
    print(f"\n📋 测试结果:")
    print(f"是否报警: {result['final_decision']['is_alarm']}")
    print(f"报警级别: {result['final_decision']['alarm_level']}")
    print(f"风险评估: {result['analysis']['risk_assessment']}")
    
    # 检查是否还有"正常案例"的幻觉
    if "正常案例" in str(result):
        print("❌ 测试失败：仍然存在'正常案例'幻觉")
    else:
        print("✅ 测试通过：已消除'正常案例'幻觉")

if __name__ == "__main__":
    test_fix()