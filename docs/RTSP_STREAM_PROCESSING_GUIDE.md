# RTSP流处理逻辑文档

## 📋 概述

本文档详细描述了Monitor项目中RTSP流的处理逻辑，包括连接测试、流捕获、WebRTC转换和错误处理机制。

## 🎯 RTSP流处理架构

### 架构图
```
RTSP设备 → RTSP连接测试 → 流捕获 → 格式转换 → WebRTC → 前端显示
```

### 核心组件
1. **RTSP连接测试** - 验证流可用性
2. **流捕获引擎** - OpenCV/ffmpeg处理
3. **WebRTC转换** - 实时媒体传输
4. **错误处理** - 多层级容错机制

## 🔧 RTSP连接测试逻辑

### 1. 基础连接测试
```python
def test_rtsp_stream(rtsp_url, timeout=10):
    """基础RTSP连接测试"""
    cap = cv2.VideoCapture(rtsp_url)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            return True, frame.shape
    return False, None
```

### 2. 详细流信息获取
```python
def get_rtsp_stream_info(rtsp_url):
    """获取RTSP流详细信息"""
    cap = cv2.VideoCapture(rtsp_url)
    info = {
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'codec': 'H264'  # 默认假设
    }
    cap.release()
    return info
```

### 3. 使用ffprobe获取精确信息
```bash
ffprobe -v quiet -print_format json -show_format -show_streams rtsp://...
```

## 🎥 流捕获处理逻辑

### 1. 多后端支持
项目支持多种捕获后端：
- **FFmpeg** (CAP_FFMPEG) - 首选，支持HEVC
- **GStreamer** (CAP_GSTREAMER) - 备选方案
- **OpenCV默认** - 通用支持

### 2. 捕获参数配置
```python
# 优化参数设置
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减少延迟
cap.set(cv2.CAP_PROP_FPS, 25)       # 固定帧率
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
```

### 3. 错误恢复机制
- 连接失败时自动重试
- 不同后端fallback
- 超时保护机制

## 🔄 WebRTC转换流程

### 1. 流验证阶段
```python
# 启动前验证
if not cap.isOpened():
    return {"error": "无法连接RTSP流"}

# 获取视频参数
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
```

### 2. 媒体轨道创建
```python
class RTSPVideoStreamTrack(MediaStreamTrack):
    """RTSP视频流轨道"""
    
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = cv2.VideoCapture(rtsp_url)
        
    async def recv(self):
        """获取下一帧"""
        ret, frame = self.cap.read()
        if ret:
            return self.create_video_frame(frame)
        return None
```

### 3. SDP生成逻辑
```python
def generate_sdp_answer(self, client_id, rtsp_url, width, height, fps):
    """生成WebRTC SDP答案"""
    sdp = f"""
    v=0
    o=- {client_id} 2 IN IP4 127.0.0.1
    s=RTSP Stream
    t=0 0
    m=video 9 UDP/TLS/RTP/SAVPF 96
    c=IN IP4 0.0.0.0
    a=rtpmap:96 H264/90000
    a=fmtp:96 profile-level-id=42e01f
    """
    return sdp
```

## 📊 错误处理策略

### 1. 连接错误处理
```python
try:
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        raise ConnectionError("RTSP连接失败")
except Exception as e:
    # 记录错误日志
    logger.error(f"RTSP连接失败: {e}")
    # 返回友好错误信息
    return {"error": f"无法连接到RTSP流: {e}"}
```

### 2. 流中断恢复
```python
async def handle_stream_interruption(self):
    """处理流中断"""
    if not self.cap.isOpened():
        logger.warning("RTSP流中断，尝试重连...")
        self.cap = cv2.VideoCapture(self.rtsp_url)
        return self.cap.isOpened()
```

### 3. 超时保护
```python
# 设置超时参数
cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 1000)
```

## 🔍 调试和测试工具

### 1. 命令行测试工具
```bash
# 测试RTSP连接
python tests/test_rtsp_simple.py rtsp://admin:pass@ip:port/stream

# 详细流信息
python debug_webrtc_video.py --rtsp rtsp://...

# WebRTC测试
python tests/test_webrtc.py
```

### 2. 浏览器测试
- `test_http_iframe.html` - HTTP设备测试
- `test_webrtc.html` - WebRTC连接测试
- `webrtc_test_page.html` - 完整测试页面

### 3. 实时调试
```python
# 启用详细日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('rtsp_processing')
```

## 📈 性能优化建议

### 1. 网络优化
- 使用有线网络连接
- 调整缓冲区大小
- 优化编码参数

### 2. 硬件加速
```python
# 启用硬件加速
if cv2.cuda.getCudaEnabledDeviceCount() > 0:
    # 使用CUDA加速
    pass
```

### 3. 内存管理
- 及时释放视频捕获资源
- 使用帧池减少内存分配
- 监控内存使用情况

## 🎯 实际使用示例

### 1. 标准RTSP URL格式
```
rtsp://username:password@ip:port/Streaming/Channels/101
rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101
```

### 2. 测试命令
```bash
# 测试单个RTSP流
python -c "
import cv2
cap = cv2.VideoCapture('rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101')
print('连接成功' if cap.isOpened() else '连接失败')
"

# 批量测试
python tests/rtsp/test_rtsp_direct.py
```

### 3. 集成测试
```bash
# 启动WebRTC服务器
python scripts/webrtc/real_webrtc_server.py --port 8090

# 测试WebRTC转换
curl -X POST http://localhost:8090/api/stream/start \
  -H "Content-Type: application/json" \
  -d '{"rtsp_url": "rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101"}'
```

## 📚 相关文件

### 服务器端实现
- `scripts/webrtc/real_webrtc_server.py` - 主要WebRTC服务器
- `scripts/webrtc/simple_webrtc_server.py` - 简化版本
- `scripts/webrtc/webrtc_compat_server.py` - 兼容性版本
- `debug_webrtc_video.py` - 调试工具

### 测试工具
- `tests/test_rtsp_simple.py` - 基础RTSP测试
- `tests/rtsp/test_rtsp_direct.py` - 直接RTSP测试
- `tests/test_webrtc.py` - WebRTC端点测试

### 配置文件
- `config/webrtc_config.json` - WebRTC配置
- `docs/WEBRTC_FIX_GUIDE.md` - WebRTC修复指南

## 🔧 故障排除

### 常见错误及解决方案

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 连接超时 | 网络问题 | 检查网络连接和端口 |
| 认证失败 | 用户名/密码错误 | 验证凭据 |
| 流不可用 | 设备离线 | 检查设备状态 |
| 解码失败 | 编码格式不支持 | 使用兼容编码 |

### 日志分析
```python
# 启用调试日志
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

通过以上文档，您可以全面了解Monitor项目中RTSP流的处理逻辑，包括连接测试、流捕获、WebRTC转换和错误处理机制。