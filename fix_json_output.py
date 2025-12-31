# fix_json_output.py
import json
import re
import math
from datetime import datetime


class JSONFixer:

    @staticmethod
    def remove_trailing_commas(text: str) -> str:
        return re.sub(r',\s*(?=[}\]])', '', text)

    @staticmethod
    def fix_broken_strings(text: str) -> str:
        """
        修复破碎的字符串，特别是时间戳格式
        示例："2024-01-"01T00":"00":00" → "2024-01-01T00:00:00"
        """
        # 先修复时间戳格式（这是一个常见问题）
        # 匹配 "2024-01-"01T00":"00":00" 这种格式
        timestamp_pattern = r'"(\d{4}-\d{2}-)"(\d{2}T\d{2})"(:)"(\d{2})"(:)"(\d{2})"'
        
        def fix_timestamp(match):
            year_month = match.group(1).replace('"', '')[:-1]  # 去掉最后的引号和减号
            day_time = match.group(2).replace('"', '')
            hour_min = match.group(4).replace('"', '')
            sec = match.group(6).replace('"', '')
            return f'"{year_month}-{day_time}:{hour_min}:{sec}"'
        
        text = re.sub(timestamp_pattern, fix_timestamp, text)
        
        # 然后修复一般的破碎字符串
        prev = None
        while prev != text:
            prev = text
            text = re.sub(
                r'"([^"]*)"\s*"([^"]*)"',
                lambda m: '"' + m.group(1) + m.group(2) + '"',
                text
            )
        return text

    @staticmethod
    def eval_numeric_expressions(text: str) -> str:
        """
        仅处理 confidence 字段
        支持：
          1) a+b=c → 取右边数字
          2) a+b-c → 直接计算
        """

        # 形式一: a+b=c  （优先处理）
        pattern_eq = r'("confidence"\s*:\s*)([0-9\.\+\-\*\/\(\)\s]+)=\s*([0-9\.]+)'

        def repl_eq(match):
            prefix = match.group(1)
            rhs = match.group(3)
            return f'{prefix}{rhs}'

        text = re.sub(pattern_eq, repl_eq, text)

        # 形式二: 普通算式
        pattern_expr = r'("confidence"\s*:\s*)([0-9\.\+\-\*\/\(\)\s]+)'

        def repl_expr(match):
            prefix = match.group(1)
            expr = match.group(2)
            try:
                value = eval(expr)
                return f'{prefix}{round(float(value), 4)}'
            except:
                return match.group(0)

        return re.sub(pattern_expr, repl_expr, text)

    @staticmethod
    def fix_common_json_errors(text: str) -> str:
        """修复常见的JSON格式错误"""
        # 修复中文标点
        text = text.replace('，', ',')
        text = text.replace('：', ':')
        text = text.replace('；', ';')
        
        # 修复缺失的引号
        text = re.sub(r'(\s*)(\w+)(\s*):', 
                     lambda m: f'{m.group(1)}"{m.group(2)}"{m.group(3)}:', 
                     text)
        
        # 修复布尔值
        text = re.sub(r'"true"', 'true', text)
        text = re.sub(r'"false"', 'false', text)
        text = re.sub(r'"null"', 'null', text)
        
        return text

    @staticmethod
    def extract_and_fix_json(text: str) -> str:
        """从文本中提取并修复JSON"""
        # 去掉代码块标记
        if text.startswith('```'):
            lines = text.split('\n')
            # 移除第一行和最后一行（如果有代码块标记）
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            text = '\n'.join(lines)
        
        text = text.strip()
        
        # 查找第一个 { 和最后一个 }
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        
        if start_idx >= 0 and end_idx > start_idx:
            extracted = text[start_idx:end_idx+1]
            return extracted
        
        return text

    @staticmethod
    def safe_parse(text: str):
        """
        安全的JSON解析，增强metadata处理
        """
        t = text.strip()
        
        # 去掉代码块标记
        if t.startswith('```'):
            t = t.strip('`')
            if t.startswith('json'):
                t = t[4:]
        
        # 保存原始文本用于metadata恢复
        original_text = t
        
        # 先尝试直接解析（可能包含metadata）
        try:
            result = json.loads(t)
            print("【JSONFixer】直接解析成功")
            return result
        except json.JSONDecodeError as e1:
            print(f"【JSONFixer】直接解析失败: {e1}")
            
            # 尝试修复常见问题
            try:
                # 1. 移除尾逗号
                t = re.sub(r',\s*(?=[}\]])', '', t)
                
                # 2. 修复破碎的时间戳（模型常见问题）
                # 匹配 "timestamp": "2024-01-"01T00":"00:00""
                def fix_timestamp(match):
                    timestamp = match.group(1)
                    # 移除多余的引号
                    timestamp = timestamp.replace('"', '')
                    # 重新构建时间戳
                    return f'"timestamp": "{timestamp}"'
                
                t = re.sub(r'"timestamp"\s*:\s*"([^"]+)"', fix_timestamp, t)
                
                # 3. 处理数学表达式
                # 匹配 confidence 字段中的数学运算
                def fix_math(match):
                    expr = match.group(2)
                    try:
                        # 移除等号后面的部分
                        if '=' in expr:
                            expr = expr.split('=')[-1].strip()
                        value = eval(expr)
                        return f'{match.group(1)}{round(float(value), 4)}'
                    except:
                        return match.group(0)
                
                t = re.sub(r'("confidence"\s*:\s*)([0-9\.\+\-\*\/\(\)\s=]+)', fix_math, t)
                
                result = json.loads(t)
                print("【JSONFixer】修复后解析成功")
                
                # 确保metadata存在
                if "metadata" not in result:
                    result = JSONFixer._ensure_metadata(result, original_text)
                
                return result
                
            except json.JSONDecodeError as e2:
                print(f"【JSONFixer】修复后解析也失败: {e2}")
                
                # 尝试提取并合并重复的metadata
                try:
                    result = JSONFixer._handle_duplicate_metadata(t)
                    if result:
                        print("【JSONFixer】通过处理重复metadata成功")
                        return result
                except Exception as e3:
                    print(f"【JSONFixer】处理重复metadata失败: {e3}")
                
                # 返回默认结构
                return JSONFixer._get_default_structure(f"JSON解析失败: {str(e2)}")
    @staticmethod
    def _handle_duplicate_metadata(text: str):
        """
        处理重复的metadata字段（模型输出常见问题）
        示例：多次出现"metadata": {...}
        """
        # 查找所有metadata对象
        metadata_pattern = r'"metadata"\s*:\s*(\{[^}]*\}(?:\s*,\s*\{[^}]*\})*)'
        matches = re.findall(metadata_pattern, text, re.DOTALL)
        
        if matches:
            print(f"【JSONFixer】找到{len(matches)}个metadata字段")
            
            # 使用最后一个metadata
            last_metadata_str = matches[-1]
            
            # 清理可能的重复嵌套
            # 移除多余的大括号
            cleaned = last_metadata_str.strip()
            if cleaned.startswith('{') and cleaned.endswith('}'):
                try:
                    # 尝试直接解析
                    metadata = json.loads(cleaned)
                    
                    # 构建新的JSON文本
                    # 移除所有metadata字段，然后添加最后一个
                    text_without_metadata = re.sub(r'"metadata"\s*:\s*\{[^}]*\}(?:\s*,\s*\{[^}]*\})*', '', text, flags=re.DOTALL)
                    
                    # 移除可能的多余逗号
                    text_without_metadata = re.sub(r',\s*,\s*', ', ', text_without_metadata)
                    text_without_metadata = re.sub(r',\s*}', '}', text_without_metadata)
                    
                    # 构建最终JSON
                    if text_without_metadata.strip().endswith('}'):
                        text_without_metadata = text_without_metadata.strip()[:-1]
                        final_text = f'{text_without_metadata.strip()}, "metadata": {json.dumps(metadata)}}}'
                    else:
                        final_text = f'{text_without_metadata.strip()}, "metadata": {json.dumps(metadata)}}}'
                    
                    result = json.loads(final_text)
                    
                    # 确保必要的metadata字段
                    if "model" not in result.get("metadata", {}):
                        result["metadata"]["model"] = "deepseek-r1:7b"
                    if "timestamp" not in result.get("metadata", {}):
                        result["metadata"]["timestamp"] = datetime.now().isoformat()
                    
                    return result
                    
                except Exception as e:
                    print(f"【JSONFixer】处理metadata失败: {e}")
        
        return None
    
    @staticmethod
    def _ensure_metadata(result: dict, original_text: str) -> dict:
        """确保metadata字段存在"""
        if "metadata" in result:
            return result
        
        print("【JSONFixer】警告：解析后metadata字段不存在，尝试从原始文本恢复")
        
        # 尝试从原始文本提取metadata
        try:
            # 使用正则表达式查找metadata
            metadata_pattern = r'"metadata"\s*:\s*\{[^}]*\}'
            match = re.search(metadata_pattern, original_text, re.DOTALL)
            
            if match:
                metadata_str = match.group(0)
                # 提取metadata对象部分
                metadata_str = metadata_str.split(':', 1)[1].strip()
                
                try:
                    metadata = json.loads(metadata_str)
                    result["metadata"] = metadata
                    print("【JSONFixer】从原始文本恢复metadata成功")
                except:
                    # 如果解析失败，尝试清理后解析
                    metadata_str = metadata_str.replace('"model": "deepseek-r1:7b",', '"model": "deepseek-r1:7b",')
                    metadata_str = re.sub(r',\s*}', '}', metadata_str)
                    try:
                        metadata = json.loads(metadata_str)
                        result["metadata"] = metadata
                        print("【JSONFixer】清理后恢复metadata成功")
                    except:
                        print("【JSONFixer】恢复metadata失败，使用默认值")
                        result["metadata"] = JSONFixer._get_default_metadata()
            else:
                print("【JSONFixer】未找到metadata字段，使用默认值")
                result["metadata"] = JSONFixer._get_default_metadata()
                
        except Exception as e:
            print(f"【JSONFixer】确保metadata时出错: {e}")
            result["metadata"] = JSONFixer._get_default_metadata()
        
        return result
    
    @staticmethod
    def _get_default_metadata() -> dict:
        """获取默认的metadata"""
        return {
            "model": "deepseek-r1:7b",
            "timestamp": datetime.now().isoformat(),
            "note": "metadata由JSONFixer自动补充"
        }
    
    @staticmethod
    def _get_default_structure(error_msg: str) -> dict:
        """获取默认结构"""
        return {
            "final_decision": {
                "is_alarm": "否",
                "alarm_level": "无",
                "alarm_reason": f"JSON解析失败: {error_msg}",
                "confidence": 0.0
            },
            "analysis": {
                "risk_assessment": "JSON解析错误",
                "recommendation": "检查模型输出格式",
                "rules_applied": ["错误处理规则"]
            },
            "metadata": JSONFixer._get_default_metadata()
        }
    
# 测试函数
def test_json_fixer():
    """测试JSONFixer的功能"""
    
    print("开始测试JSONFixer...")
    
    test_cases = [
        # 测试用例1: 包含破碎时间戳的JSON
        '''
        {
          "final_decision": {
            "is_alarm": "是",
            "alarm_level": "一般",
            "alarm_reason": "人员未佩戴工牌",
            "confidence": 0.87
          },
          "analysis": {
            "risk_assessment": "存在身份验证风险",
            "recommendation": "通知安保人员核实",
            "rules_applied": ["工牌检查规则"]
          },
          "metadata": {
            "model": "推理模型",
            "timestamp": "2024-01-"01T00":"00":00"
          }
        }
        ''',
        
        # 测试用例2: 缺少metadata的JSON
        '''
        {
          "final_decision": {
            "is_alarm": "是",
            "alarm_level": "一般",
            "alarm_reason": "人员未佩戴工牌",
            "confidence": 0.8
          },
          "analysis": {
            "risk_assessment": "风险",
            "recommendation": "建议"
          }
        }
        ''',
        
        # 测试用例3: 包含代码块的JSON
        '''
        ```json
        {
          "final_decision": {
            "is_alarm": "是",
            "alarm_level": "一般",
            "alarm_reason": "人员未佩戴工牌",
            "confidence": 0.8728 + 0.8705 = 1.7433
          }
        }
        ```
        ''',
        
        # 测试用例4: 包含尾逗号的JSON
        '''
        {
          "final_decision": {
            "is_alarm": "是",
            "alarm_level": "一般",
            "alarm_reason": "人员未佩戴工牌",
            "confidence": 0.8,
          },
          "analysis": {
            "risk_assessment": "风险",
            "recommendation": "建议",
          },
        }
        ''',
        
        # 测试用例5: 完全正常的JSON
        '''
        {
          "final_decision": {
            "is_alarm": "是",
            "alarm_level": "一般",
            "alarm_reason": "人员未佩戴工牌",
            "confidence": 0.87
          },
          "analysis": {
            "risk_assessment": "存在身份验证风险",
            "recommendation": "通知安保人员核实",
            "rules_applied": ["工牌检查规则"]
          },
          "metadata": {
            "model": "推理模型",
            "timestamp": "2024-01-01T00:00:00"
          }
        }
        '''
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n{'='*50}")
        print(f"测试用例 {i+1}:")
        try:
            result = JSONFixer.safe_parse(test_case)
            print(f"✓ 解析成功")
            print(f"结果包含字段: {list(result.keys())}")
            print(f"是否有metadata: {'metadata' in result}")
            if 'metadata' in result:
                print(f"metadata内容: {result['metadata']}")
        except Exception as e:
            print(f"✗ 解析失败: {e}")


if __name__ == "__main__":
    test_json_fixer()