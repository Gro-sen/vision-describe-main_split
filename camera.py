# camera.py
import cv2
import time
import threading
import config  # 改为导入整个模块
from model_infer import try_infer


def create_rtsp_capture(rtsp_url):
    """创建RTSP捕获对象，配置优化参数"""
    
    # 设置FFmpeg参数
    ffmpeg_options = {
        'rtsp_transport': 'tcp',  # 强制使用TCP（更稳定）
        'buffer_size': '1024000',  # 增加缓冲区
        'max_delay': '500000',  # 最大延迟500ms
        'stimeout': '5000000',  # 超时5秒（5000000微秒）
        'analyzeduration': '10000000',
        'probesize': '10000000',
    }
    
    # 构建FFmpeg参数字符串
    options = []
    for key, value in ffmpeg_options.items():
        options.append(f'{key}={value}')
    options_str = ' '.join(options)
    
    # 创建VideoCapture对象
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    
    # 尝试设置OpenCV属性
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
    cap.set(cv2.CAP_PROP_FPS, 15)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    
    return cap


def check_rtsp_health(cap, timeout=3.0):
    """检查RTSP连接健康状况"""
    try:
        # 尝试读取一帧，设置超时
        import threading
        
        result = [None]
        exception = [None]
        
        def read_frame():
            try:
                result[0] = cap.read()
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=read_frame)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            # 线程仍在运行，说明读取超时
            return False, "读取帧超时"
        elif exception[0] is not None:
            return False, f"读取异常: {exception[0]}"
        elif result[0][0] is False:
            return False, "读取帧失败"
        else:
            return True, "连接正常"
            
    except Exception as e:
        return False, f"检查异常: {e}"
class RTSPMonitor:
    """RTSP连接监控器"""
    
    def __init__(self):
        self.connection_start_time = None
        self.frames_received = 0
        self.connection_errors = 0
        self.last_error_time = None
        self.last_frame_time = None
    
    def on_connection_start(self):
        self.connection_start_time = time.time()
        self.frames_received = 0
        print(f"【MONITOR】连接开始: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def on_frame_received(self):
        self.frames_received += 1
        self.last_frame_time = time.time()
        
        # 每30秒打印一次统计信息
        if self.frames_received % 30 == 0:
            uptime = time.time() - self.connection_start_time
            fps = self.frames_received / uptime if uptime > 0 else 0
    
    def on_error(self, error_msg):
        self.connection_errors += 1
        self.last_error_time = time.time()
        print(f"【MONITOR】错误 #{self.connection_errors}: {error_msg}")
    
    def get_stats(self):
        """获取统计信息"""
        return {
            "frames_received": self.frames_received,
            "connection_errors": self.connection_errors,
            "uptime": time.time() - self.connection_start_time if self.connection_start_time else 0,
            "last_error_time": self.last_error_time,
            "last_frame_time": self.last_frame_time
        }
def capture_rtsp():
    last_infer_time_ref = [config.last_infer_time]
    frame_skip = 0
    reconnect_delay = 3
    max_reconnect_delay = 60
    
    # 创建监控器
    monitor = RTSPMonitor()
    
    while True:
        try:
            print(f"【RTSP】连接摄像头... (第{monitor.connection_errors + 1}次尝试)")
            
            # 创建连接
            cap = create_rtsp_capture(config.RTSP_URL)
            
            if not cap.isOpened():
                monitor.on_error("无法打开摄像头")
                time.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)
                continue
            
            monitor.on_connection_start()
            reconnect_delay = 3  # 重置重连延迟
            
            print("【RTSP】连接成功，开始接收帧...")
            
            last_frame_time = time.time()
            max_frame_interval = 5.0
            
            while True:
                # 检查连接健康状态
                if time.time() - last_frame_time > max_frame_interval:
                    monitor.on_error("帧接收超时")
                    break
                
                # 尝试读取帧
                ret, frame = cap.read()
                
                if ret:
                    monitor.on_frame_received()
                    last_frame_time = time.time()
                    
                    # 处理帧...
                    frame_skip = (frame_skip + 1) % 2
                    if frame_skip == 0:
                        continue
                    
                    resized_frame = cv2.resize(frame, (640, 360))
                    
                    # 写入缓冲区
                    config.frame_buffer.write(resized_frame.copy())
                    config.frame_buffer.swap()
                    
                    with config.latest_frame_lock:
                        config.latest_frame = resized_frame.copy()
                    
                    # 推理
                    current_time = time.time()
                    if current_time - last_infer_time_ref[0] >= config.INFER_INTERVAL:
                        try_infer(resized_frame.copy(), last_infer_time_ref)
                        
                else:
                    # 短暂等待后重试
                    time.sleep(0.05)
                    
        except KeyboardInterrupt:
            print("【RTSP】用户中断，退出摄像头线程")
            break
        except Exception as e:
            monitor.on_error(f"异常: {e}")
        finally:
            if 'cap' in locals():
                cap.release()
            
            # 打印统计信息
            stats = monitor.get_stats()
            print(f"【RTSP】连接断开，统计: 接收{stats['frames_received']}帧，错误{stats['connection_errors']}次")
            
            # 等待重连
            print(f"【RTSP】{reconnect_delay}秒后重新连接...")
            time.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)