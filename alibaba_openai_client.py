# alibaba_openai_client.py
import os
import base64
from openai import OpenAI

class AlibabaOpenAIClient:
    """使用OpenAI官方库的阿里云兼容客户端"""
    def __init__(self, api_key: str = None, base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"):
        # 直接从环境变量读取，openai库会自动使用 OPENAI_API_KEY
        self.client = OpenAI(
            api_key=api_key,  # 如果调用时传入了api_key参数，则使用
            base_url=base_url
        )

    def call_multimodal_api(self, prompt: str, image_b64: str, model: str = "qwen-vl-max") -> str:
        """调用多模态模型API - 官方标准格式"""
        try:
            # 🎯 核心：按照官方示例构建消息体
            completion = self.client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                # ✅ 关键：使用正确的 data URI 格式
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }],
                temperature=0.1,
                timeout=30  # 设置超时
            )
            # 提取回复内容
            result = completion.choices[0].message.content
            print(f"【阿里云VL-API】调用成功，模型: {model}")
            return result
            
        except Exception as e:
            print(f"【ERROR】阿里云多模态API调用失败: {e}")
            raise

    def call_text_api(self, prompt: str, model: str = "qwen3-max") -> str:
        """调用纯文本模型API"""
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"【ERROR】阿里云文本API调用失败: {e}")
            raise