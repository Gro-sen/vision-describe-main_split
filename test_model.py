# test_math_expressions.py
from fix_json_output import JSONFixer

def test_math_expressions():
    """测试各种数学表达式"""
    
    test_cases = [
        # 原始问题案例
        '''{
  "final_decision": {
    "is_alarm": "是",
    "alarm_level": "一般",
    "alarm_reason": "人员未佩戴工牌且处于办公区域",
    "confidence": 0.8728 + 0.8705 - 0.8560
  },
  "analysis": {
    "risk_assessment": "存在身份验证风险，员工可能未正常进入或核实身份",
    "recommendation": "通知安保人员核实人员身份和工牌状态",
    "rules_applied": ["工牌检查规则"]
  },
  "metadata": {
    "model": "deepseek-r1:7b",
    "timestamp": "2024-01-01T00:00:00"
  }
}''',
        
        # 其他可能的表达式
        '''{
  "final_decision": {
    "confidence": 0.5 + 0.3
  }
}''',
        
        '''{
  "final_decision": {
    "confidence": 0.8 - 0.2
  }
}''',
        
        '''{
  "final_decision": {
    "confidence": 0.6 * 0.7
  }
}''',
        
        '''{
  "final_decision": {
    "confidence": (0.5 + 0.3) * 0.8
  }
}''',
        
        # 包含等号的表达式
        '''{
  "final_decision": {
    "confidence": 0.8728 + 0.8705 = 1.7433
  }
}''',
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n{'='*60}")
        print(f"测试用例 {i+1}:")
        print(f"原始表达式: {test_case[test_case.find('confidence'):test_case.find('confidence')+100]}...")
        
        try:
            result = JSONFixer.safe_parse(test_case)
            if result and "final_decision" in result and "confidence" in result["final_decision"]:
                confidence = result["final_decision"]["confidence"]
                print(f"✓ 解析成功, confidence: {confidence} (类型: {type(confidence)})")
            else:
                print(f"✗ 解析失败或缺少字段")
        except Exception as e:
            print(f"✗ 解析失败: {e}")

if __name__ == "__main__":
    test_math_expressions()