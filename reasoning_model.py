import re
import json
import ollama
from typing import Dict, Any, List
from kb import KnowledgeBase
from datetime import datetime
from config import model_config
from alibaba_openai_client import AlibabaOpenAIClient
class ReasoningModel:
    """推理语言大模型"""
    def __init__(self, model_name: str = "qwen3-max"): 
        self.model_name = model_name 
        self.kb = KnowledgeBase()
        # 初始化阿里云客户端
        self.cloud_client = AlibabaOpenAIClient()
    def generate_prompt(self, vision_facts: Dict[str, Any], 
                   similar_cases: List[Dict] = None) -> str:
        """生成推理模型的提示词"""
    
        # 视觉事实总结
        vision_summary = f"""
视觉分析结果：
- 有人员：{vision_facts.get('has_person', '未知')}
- 工牌状态：{vision_facts.get('badge_status', '未知')}
- 进入禁区：{vision_facts.get('enter_restricted_area', '未知')}
- 火灾/烟雾：{vision_facts.get('has_fire_or_smoke', '未知')}
- 电气风险：{vision_facts.get('has_electric_risk', '未知')}
- 场景描述：{vision_facts.get('scene_summary', '无描述')}
"""
    
        # 知识库案例
        kb_context = ""
        if similar_cases and len(similar_cases) > 0:
            kb_context = "\n相关历史案例：\n"
            for i, case in enumerate(similar_cases[:3], 1):
                source = case.get('source', '未知')
                text = case.get('text', '')[:150]
                score = case.get('score', 0)
                kb_context += f"{i}. 来源：{source}\n"
                kb_context += f"   内容：{text}...\n"
                kb_context += f"   相似度：{score:.4f}\n"
        else:
            kb_context = "\n相关历史案例：无相关历史案例\n"
        
        prompt = f"""你是一个专业的安防专家，负责分析监控画面并做出报警决策。

## 重要指令：
- 你只能输出 JSON 格式，不能有任何其他文字
- JSON 必须严格符合指定的格式
- 所有数值必须是纯数字
- confidence 字段必须是 0.0 到 1.0 之间的纯数字
- 不要解释，不要注释，不要多余的空格

## 分析要求：
1. 基于视觉分析结果进行综合判断
2. 考虑公司安防政策和风险评估
3. 输出明确的报警决策

## 输入信息：
{vision_summary}
{kb_context}

## 输出格式（必须严格遵守，这是有效的JSON示例）：
{{
  "final_decision": {{
    "is_alarm": "是" 或 "否",
    "alarm_level": "无" 或 "一般" 或 "严重" 或 "紧急",
    "alarm_reason": "详细的报警原因说明",
    "confidence": 0.85  # 注意：必须是0.0到1.0之间的数字，不要进行计算
  }},
  "analysis": {{
    "risk_assessment": "风险评估描述",
    "recommendation": "处置建议",
    "rules_applied": ["规则1", "规则2"]
  }},
  "metadata": {{
    "model": "{self.model_name}",  # 直接使用模型名称
    "timestamp": "2024-01-01T00:00:00"
  }}
}}



## 特别注意：
- confidence字段必须是0.0到1.0之间的数字，例如0.75、0.85
- 不要进行数学运算（不要写+、-、=等符号）
- 不要添加任何额外的文本、注释或解释

现在，基于以上信息，输出你的决策JSON："""
    
        return prompt
    
    def query_knowledge_base(self, vision_facts: Dict[str, Any]) -> List[Dict]:
        """查询知识库获取相关案例"""
        # 构建查询字符串
        query_parts = []
        
        if vision_facts.get('has_person'):
            query_parts.append("人员")
            if vision_facts.get('badge_status') in ['未佩戴', '无法确认']:
                query_parts.append("工牌异常")
            if vision_facts.get('enter_restricted_area'):
                query_parts.append("禁区进入")
        
        if vision_facts.get('has_fire_or_smoke'):
            query_parts.append("火灾烟雾")
        if vision_facts.get('has_electric_risk'):
            query_parts.append("电气风险")
        
        query_text = " ".join(query_parts) + " " + vision_facts.get('scene_summary', '')
        
        # 查询知识库
        similar_cases = self.kb.get_similar_cases(
            query_text, 
            top_k=3, 
            similarity_threshold=0.3
        )
        
        return similar_cases
    
    def infer(self, vision_facts: Dict[str, Any]) -> Dict[str, Any]:
        """执行推理，增强错误处理"""
        
        # 查询知识库
        similar_cases = self.query_knowledge_base(vision_facts)
        
                # 区分类型
        rule_files = []
        history_cases = []
        
        for case in similar_cases:
            source = case.get('source', '')
            if 'case_' in source:
                history_cases.append(case)
            elif source.endswith('.md'):
                rule_files.append(case)
            else:
                history_cases.append(case)  # 默认
        
        kb_total = len(similar_cases)  # 总参考文档数
        kb_rules = len(rule_files)     # 规则文件数
        kb_history = len(history_cases) # 历史案例数
        
        print(f"【知识库】检索结果: {kb_total} 个文档")
        print(f"  - 规则文件: {kb_rules} 个")
        print(f"  - 历史案例: {kb_history} 个")
        
        # 详细来源
        if similar_cases:
            print("  具体来源:")
            for i, case in enumerate(similar_cases):
                source = case.get('source', '未知')
                score = case.get('score', 0)
                if 'case_' in source:
                    type_str = "📁 历史案例"
                elif source.endswith('.md'):
                    type_str = "📚 规则文件"
                else:
                    type_str = "❓ 其他"
                print(f"    {i+1}. {type_str}: {source} (相似度: {score:.4f})")
                
        # 生成提示词
        prompt = self.generate_prompt(vision_facts, similar_cases)
        
        try:
            # 获取原始文本
            print(f"【推理模型】调用阿里云API，模型: {self.model_name}")
            raw_text = self.cloud_client.call_text_api(
                prompt=prompt, 
                model=self.model_name
            )
            print(f"【DEBUG】模型原始输出:\n{raw_text}\n")
            
            # 保存原始输出用于调试
            with open("model_raw_outputs.log", "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"时间: {datetime.now().isoformat()}\n")
                f.write(f"模型: {self.model_name}\n")
                f.write(f"输出:\n{raw_text}\n")
            
            # 使用JSONFixer解析
            from fix_json_output import JSONFixer
            result = JSONFixer.safe_parse(raw_text)
            
            # 验证结果格式
            if not self._validate_result_format(result):
                print("【WARN】模型输出格式不正确，使用后备决策")
                return self.get_fallback_decision(vision_facts, similar_cases)
            
            # 确保metadata包含必要信息
            if "metadata" not in result:
                result["metadata"] = {}
            
            metadata = result["metadata"]
            metadata["kb_total_references"] = kb_total
            metadata["kb_rule_files"] = kb_rules
            metadata["kb_history_cases"] = kb_history
            metadata["kb_cases_used"] = kb_history  # 保持向后兼容
            
            # 如果原始输出中有模型信息，保留它
            if "original_model" not in metadata and "model" in raw_text:
                # 尝试提取原始模型名称
                import re
                model_match = re.search(r'"model"\s*:\s*"([^"]+)"', raw_text)
                if model_match and model_match.group(1) != self.model_name:
                    metadata["original_model_output"] = model_match.group(1)
            
            # 确保confidence在0-1范围内
            if "final_decision" in result and "confidence" in result["final_decision"]:
                try:
                    confidence = float(result["final_decision"]["confidence"])
                    if confidence > 1.0:
                        result["final_decision"]["confidence"] = 0.99
                    elif confidence < 0.0:
                        result["final_decision"]["confidence"] = 0.01
                except:
                    result["final_decision"]["confidence"] = 0.5
            
            return result
            
        except Exception as e:
            print(f"【ERROR】推理模型错误: {e}")
            import traceback
            traceback.print_exc()
            return self.get_fallback_decision(vision_facts, similar_cases)
        
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """从文本中提取JSON"""
        if not text:
            raise ValueError("模型返回空文本")
        
        print(f"【DEBUG】开始提取JSON，文本长度: {len(text)}")
        print(f"【DEBUG】前500字符: {text[:500]}")
        
        # 方法1: 清理文本中的代码块标记
        text_clean = text.strip()
        
        # 移除常见的代码块标记
        if text_clean.startswith('```json'):
            text_clean = text_clean[7:]  # 移除 ```json
        elif text_clean.startswith('```'):
            text_clean = text_clean[3:]  # 移除 ```
        
        if text_clean.endswith('```'):
            text_clean = text_clean[:-3]  # 移除结尾的 ```
        
        text_clean = text_clean.strip()
        # 进一步清理可能的多余字符
        text_clean = self._fix_json_errors(text_clean)

        # 方法2: 尝试直接解析清理后的文本
        try:
            result = json.loads(text_clean)
            print("【DEBUG】方法1: 直接解析成功")
            return result
        except json.JSONDecodeError as e:
            print(f"【DEBUG】方法1失败: {e.msg}, 位置: {e.pos}")
        
        # 方法3: 查找第一个 { 和最后一个 }
        try:
            start = text_clean.find('{')
            end = text_clean.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = text_clean[start:end]
                print(f"【DEBUG】提取的JSON字符串: {json_str[:200]}...")
                result = json.loads(json_str)
                print("【DEBUG】方法2: 提取{}成功")
                return result
        except Exception as e:
            print(f"【DEBUG】方法2失败: {e}")
        
        # 方法4: 使用正则表达式提取JSON
        try:
            # 匹配可能包含嵌套的JSON对象
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, text_clean, re.DOTALL)
            
            if matches:
                print(f"【DEBUG】找到{len(matches)}个可能的JSON对象")
                for i, match in enumerate(matches):
                    try:
                        result = json.loads(match)
                        print(f"【DEBUG】方法3: 第{i+1}个匹配解析成功")
                        return result
                    except json.JSONDecodeError as e:
                        print(f"【DEBUG】第{i+1}个匹配解析失败: {e.msg}")
                        continue
        except Exception as e:
            print(f"【DEBUG】方法3失败: {e}")
        
        # 方法5: 尝试修复不完整的JSON
        try:
            # 尝试补全可能缺失的括号
            json_str = text_clean
            
            # 统计括号
            open_braces = json_str.count('{')
            close_braces = json_str.count('}')
            
            if open_braces > close_braces:
                # 补全缺失的闭合括号
                json_str += '}' * (open_braces - close_braces)
                print(f"【DEBUG】补全了{open_braces - close_braces}个闭合括号")
            
            result = json.loads(json_str)
            print("【DEBUG】方法4: 补全括号后解析成功")
            return result
        except Exception as e:
            print(f"【DEBUG】方法4失败: {e}")
        
        # 所有方法都失败
        raise ValueError(f"无法从模型输出中提取有效的JSON。文本前200字符: {text[:200]}")
    
    def _fix_json_errors(self, text: str) -> str:
        """修复常见的JSON格式错误"""
        
        # 1. 修复数学表达式（如 "0.8728 + 0.8705 = 1.7433" -> "1.7433"）
        import re
        
        # 匹配数学表达式并计算结果
        math_pattern = r'(\d+\.?\d*)\s*\+\s*(\d+\.?\d*)\s*=\s*(\d+\.?\d*)'
        
        def calculate_math(match):
            try:
                # 计算结果
                a = float(match.group(1))
                b = float(match.group(2))
                result = a + b
                return str(round(result, 4))
            except:
                # 如果计算失败，使用等号右边的值
                return match.group(3)
        
        text = re.sub(math_pattern, calculate_math, text)
        
        # 2. 修复缺失的引号
        # 匹配类似: confidence: 0.85 这样的错误（缺少双引号）
        key_value_pattern = r'(\s*)(\w+)(\s*):(\s*)([^",\}\]\s]+)'
        
        def fix_key_value(match):
            key = match.group(2)
            value = match.group(5)
            
            # 如果是布尔值或null，保持原样
            if value in ['true', 'false', 'null', 'True', 'False', 'None']:
                return f'{match.group(1)}"{key}"{match.group(3)}:{match.group(4)}{value.lower()}'
            
            # 如果是数字，保持原样
            try:
                float(value)
                return f'{match.group(1)}"{key}"{match.group(3)}:{match.group(4)}{value}'
            except ValueError:
                # 如果是字符串，添加引号
                return f'{match.group(1)}"{key}"{match.group(3)}:{match.group(4)}"{value}"'
        
        text = re.sub(key_value_pattern, fix_key_value, text)
        
        # 3. 修复中文逗号、中文冒号
        text = text.replace('，', ',')
        text = text.replace('：', ':')
        
        # 4. 修复单引号（替换为双引号）
        text = text.replace("'", '"')
        
        # 5. 修复注释（移除//和#注释）
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # 移除行尾注释
            line = re.sub(r'//.*$', '', line)
            line = re.sub(r'#.*$', '', line)
            cleaned_lines.append(line)
        text = '\n'.join(cleaned_lines)
        
        print(f"【DEBUG】修复后的JSON文本: {text[:500]}...")
        return text
    def _validate_result_format(self, result: Dict) -> bool:
        """验证结果格式是否正确，增强容错性"""
        try:
            print(f"【DEBUG】开始验证结果格式，可用字段: {list(result.keys())}")
            original_metadata = result.get("metadata", {})
            # 检查必需字段
            required_sections = ["final_decision", "analysis"]
            for section in required_sections:
                if section not in result:
                    print(f"【ERROR】缺少必需字段: {section}")
                    print(f"【ERROR】可用字段: {list(result.keys())}")
                    return False
            
            # 检查 final_decision 字段
            final_decision = result["final_decision"]
            required_decisions = ["is_alarm", "alarm_level", "alarm_reason"]
            for field in required_decisions:
                if field not in final_decision:
                    print(f"【ERROR】final_decision 缺少字段: {field}")
                    print(f"【ERROR】final_decision字段: {list(final_decision.keys())}")
                    return False
            
            # 验证报警等级
            valid_levels = ["无", "一般", "严重", "紧急"]
            alarm_level = final_decision.get("alarm_level")
            if alarm_level not in valid_levels:
                print(f"【ERROR】无效的报警等级: {alarm_level}")
                print(f"【ERROR】有效等级应为: {valid_levels}")
                return False
            
            # 验证是否报警
            is_alarm = final_decision.get("is_alarm")
            if is_alarm not in ["是", "否"]:
                print(f"【ERROR】无效的是否报警: {is_alarm}")
                return False
            
            # 确保confidence在0-1范围内
            if "confidence" in final_decision:
                try:
                    confidence = float(final_decision["confidence"])
                    if confidence > 1.0:
                        final_decision["confidence"] = 0.99
                    elif confidence < 0.0:
                        final_decision["confidence"] = 0.01
                except:
                    final_decision["confidence"] = 0.5
            
            # 如果缺少metadata，添加默认值（增强容错）
            if "metadata" not in result:
                print("【WARN】缺少metadata字段，自动添加")
                from datetime import datetime
                result["metadata"] = {
                    "model": self.model_name,
                    "timestamp": datetime.now().isoformat(),
                    "kb_cases_used": 0
                }
            else:
                # 确保metadata有必要的字段
                if "timestamp" not in result["metadata"]:
                    from datetime import datetime
                    result["metadata"]["timestamp"] = datetime.now().isoformat()
                if "model" not in result["metadata"]:
                    result["metadata"]["model"] = self.model_name
                if "kb_cases_used" not in result["metadata"]:
                    result["metadata"]["kb_cases_used"] = 0
            
            print("【DEBUG】结果格式验证通过")
            if original_metadata:
                if "model" in original_metadata:
                    result["metadata"]["original_model"] = original_metadata["model"]
                if "timestamp" in original_metadata:
                    # 保留原始时间戳作为参考
                    result["metadata"]["original_timestamp"] = original_metadata["timestamp"]
            return True
            
        except Exception as e:
            print(f"【ERROR】验证结果格式失败: {e}")
            import traceback
            traceback.print_exc()
            return False


    def get_fallback_decision(self, vision_facts: Dict[str, Any], 
                             similar_cases: List[Dict]) -> Dict[str, Any]:
        """后备决策（当模型出错时使用）"""
        from rules import decide_alarm
        
        # 使用原始规则
        is_alarm, level, reason = decide_alarm(vision_facts)
        
        return {
            "final_decision": {
                "is_alarm": is_alarm,
                "alarm_level": level,
                "alarm_reason": reason,
                "confidence": 0.5
            },
            "analysis": {
                "risk_assessment": "使用规则引擎后备决策",
                "recommendation": "检查推理模型",
                "similar_case_reference": f"后备决策，参考了{len(similar_cases)}个案例",
                "rules_applied": ["后备规则引擎"]
            },
            "metadata": {
                "model": "后备规则引擎",
                "timestamp": datetime.now().isoformat(),
                "kb_cases_used": len(similar_cases)
            }
        }

# 全局推理模型实例
reasoning_model = ReasoningModel()