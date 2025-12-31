# 🎥 智能视频识别系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

这是一个基于**FastAPI**的智能视频识别系统，集成了**Ollama大模型**，能够实时处理RTSP视频流并提供AI驱动的内容识别功能。系统采用现代化的Web界面设计，支持多终端访问，为视频监控和内容分析提供了强大的解决方案。


## 核心特性

###  核心功能
- **实时视频流处理**：支持RTSP协议视频流的实时捕获和展示
- **AI智能识别**：集成Ollama Qwen2.5-VL大模型，提供精准的图像内容识别
- **实时通信**：基于WebSocket的实时数据推送，零延迟获取识别结果
- **历史记录**：智能存储和管理识别历史，支持数据回溯

### 性能特点
- **异步处理**：基于asyncio和ThreadPoolExecutor的高并发架构
- **智能跳帧**：可配置的帧处理策略，优化系统资源使用
- **队列管理**：缓冲队列机制，确保视频流的稳定性
- **自动重连**：网络异常时自动重连RTSP流，保证服务稳定性

### 主界面
- **左侧**：实时视频流展示区域，支持全屏查看
- **右侧**：AI识别结果展示区域，支持Markdown格式渲染
- **顶部**：系统状态栏，显示连接状态和系统信息

## 🛠️ 技术架构

### 后端技术栈
- **Web框架**：FastAPI - 高性能异步Web框架
- **视频处理**：OpenCV - 专业级视频处理库
- **AI模型**：Ollama + Qwen2.5-VL - 多模态大语言模型
- **实时通信**：WebSocket - 双向实时数据传输
- **异步处理**：asyncio + ThreadPoolExecutor - 高并发处理

### 前端技术栈
- **基础技术**：HTML5 + CSS3 + JavaScript
- **UI设计**：现代化毛玻璃效果，渐变背景
- **响应式布局**：支持移动端和桌面端适配
- **Markdown渲染**：marked.js + highlight.js

### 系统架构图
```

```

### 环境要求

- **Python版本**：3.8 或更高版本
- **操作系统**：Windows / Linux / macOS
- **内存要求**：建议8GB以上（运行大模型需要）
- **网络要求**：支持RTSP协议的网络摄像头或视频源

### 安装步骤

**安装Python依赖**

```bash
pip install -r requirements.txt
```

**启动Ollama服务：**
```bash
ollama serve
```

**下载所需模型：**

```bash
ollama pull qwen2.5vl:7b
ollama pull deepseek-r1:7b
```

**配置RTSP视频源**

在`main.py`文件中修改RTSP地址为您的摄像头地址：

```python
rtsp_url = "rtsp://用户名:密码@IP地址:端口/路径"
```

**启动应用**
方式一：直接运行
```bash
python main.py
```
式二：使用uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**访问应用**

打开浏览器访问：
- **本地访问**：http://localhost:8000
- **局域网访问**：http://您的IP地址:8000

## 项目结构

```

```
## 🔧 高级配置

### 性能优化建议

1. **硬件要求**
   ```
   CPU: 4核心以上（推荐8核心）
   内存: 8GB以上（推荐16GB）
   GPU: 可选，但建议使用NVIDIA GPU加速大模型推理
   网络: 千兆以太网，低延迟
   ```

2. **系统优化参数**
   ```python
   # 针对高分辨率视频流
   frame_skip = 15  # 增加跳帧数，降低CPU占用
   
   # 针对低性能设备
   frame_queue_size = 5  # 减少队列大小，降低内存占用
   
   # 针对网络不稳定环境
   reconnect_interval = 3  # 设置重连间隔
   ```

## 🐛 常见问题解决

### 问题1：AI识别响应慢
**解决方案：**
- 增加`frame_skip`参数值
- 减少识别频率（调整识别间隔）
- 确保Ollama服务正常运行
- 考虑使用GPU加速

### 问题2：视频画面卡顿
**解决方案：**
- 调整视频分辨率设置
- 增加帧队列大小
- 检查网络带宽是否充足
