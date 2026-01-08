# test_with_real_image.py
import cv2
import base64
from alibaba_openai_client import AlibabaOpenAIClient
from dotenv import load_dotenv
load_dotenv()
# 1. 读取一张真实人物图像
real_image_path = "D:\\code\\python\\git\\vision-describe-main_split\\alarms\\20260106_135606_025_980a96f7_severe.jpg"  # 替换为你的图片路径
frame = cv2.imread(real_image_path)
if frame is None:
    print("❌ 无法读取图像，请检查路径")
    exit()

# 2. 转换为Base64
def frame_to_base64(frame):
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return base64.b64encode(buf).decode('utf-8')

image_b64 = frame_to_base64(frame)

# 3. 使用极简但强制的prompt
test_prompt = """你是一个安防系统。分析图像，只输出JSON，格式必须如下：
{
"has_person": true或false,
"badge_status": "佩戴"或"未佩戴"或"无法确认"或"不适用",
"scene_summary": "一句话描述画面"
}
如果看到人，has_person必须为true。"""

client = AlibabaOpenAIClient()
result = client.call_multimodal_api(test_prompt, image_b64, model="qwen-vl-max")
print("最终测试结果：", result)