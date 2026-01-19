from dotenv import load_dotenv
load_dotenv()
import os
import sys
import time
from datetime import datetime

def initialize_system():
    """系统初始化"""
    print("=" * 60)
    print("智能安防系统初始化")
    print("=" * 60)
    
    # 检查目录结构
    required_dirs = [
        "alarms",
        "sounds",
        "kb/source",
        "kb/index",
        "kb/cases",
        "static/css",
        "static/js"
    ]
    
    for dir_path in required_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ 确保目录存在: {dir_path}")
    
    # 检查声音文件
    sound_files = ["normal.mp3", "severe.mp3", "critical.mp3"]
    for sound_file in sound_files:
        path = os.path.join("sounds", sound_file)
        if not os.path.exists(path):
            print(f"⚠ 警告: 声音文件不存在 - {path}")
            # 创建空文件作为占位符
            with open(path, 'wb') as f:
                f.write(b'')
    
    # 检查知识库索引
    index_file = "kb/index/faiss_bge.index"
    if os.path.exists(index_file):
        print("✓ 知识库索引已存在")
    else:
        print("ℹ 知识库索引不存在，将在第一次查询时创建")
    
    # 检查模型可用性
    print("\n检查云服务连接性...")
try:
    # 导入你将要创建的阿里云客户端
    from alibaba_openai_client import AlibabaOpenAIClient
    
    # 1. 检查环境变量
    api_key = os.getenv('ALIBABA_CLOUD_API_KEY')
    if not api_key:
        print("❌ 环境变量 ALIBABA_CLOUD_API_KEY 未设置")
        print("   请设置: export ALIBABA_CLOUD_API_KEY='your-key' 或写入 .env 文件")
    else:
        print(f"✓ API密钥已从环境变量加载 (前4位: {api_key[:4]}...)")
    
    # 2. 创建客户端并发送一个最小化、低成本的测试请求
    client = AlibabaOpenAIClient(api_key=api_key)
    
    # 使用一个极其简单的提示词来测试文本模型连通性，控制成本
    test_prompt = "请回复'服务正常'。"
    
    # 注意：这里会实际产生一次API调用，有极小费用
    test_response = client.call_text_api(prompt=test_prompt, model="qwen3-max")  # 使用最轻量模型
    
    if "服务正常" in test_response:
        print("✅ 阿里云百炼API连接测试成功")
        print(f"   测试模型: qwen3-max")
        print(f"   响应: {test_response}")
    else:
        print(f"⚠️  连接测试返回意外响应: {test_response}")
        
except ImportError:
    print("❌ 阿里云客户端模块导入失败，请确保 alibaba_cloud_client.py 文件存在")
except Exception as e:
    print(f"❌ 阿里云服务连接检查失败: {e}")
    print("   可能原因: 1) API密钥无效 2) 网络不通 3) 服务端错误")
    
    # 初始化知识库索引
    try:
        from kb import kb
        stats = kb.get_statistics()
        if stats["index_exists"]:
            print(f"✓ 知识库索引状态正常")
        else:
            print("ℹ 知识库索引需要重建")
            if input("是否现在重建索引? (y/n): ").lower() == 'y':
                result = kb.update_index()
                print(f"重建结果: {result}")
    except Exception as e:
        print(f"⚠ 初始化知识库时出错: {e}")
    
    print("\n" + "=" * 60)
    print("系统初始化完成")
    print("启动命令: python main.py")
    print("访问地址: http://localhost:8000")
    print("=" * 60)

if __name__ == "__main__":
    initialize_system()