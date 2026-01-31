# RTSP流处理速查表

## 🚀 快速测试命令

### 基础RTSP测试
```bash
# 测试RTSP连接
python tests/test_rtsp_simple.py rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101

# 获取流信息
python debug_webrtc_video.py --rtsp rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101
```

### WebRTC测试
```bash
# 启动WebRTC服务器
python scripts/webrtc/real_webrtc_server.py --port 8090

# 测试WebRTC连接
curl -X POST http://localhost:8090/api/offer \
  -H "Content-Type: application/json" \
  -d '{"rtsp_url": "rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101"}'
```

## 📋 标准RTSP URL格式

### 品牌A
```
rtsp://[username]:[password]@[ip]:[port]/Streaming/Channels/[channel]
示例: rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101
```

### 品牌B
```
rtsp://[username]:[password]@[ip]:[port]/cam/realmonitor?channel=[channel]&subtype=[type]
示例: rtsp://admin:Chang168@192.168.42.86:55401/cam/realmonitor?channel=1&subtype=0
```

### 通道号选择逻辑
```javascript
// 正确的通道号选择逻辑
const channelNumber = props.device.channel || props.device.chs || 1;
// 构建RTSP URL时使用上述通道号
```

> **重要提示**：确保在构建RTSP URL时使用实际选择的通道号(channel)，而不是总通道数(chs)，以避免所有通道显示相同画面的问题。

## 🔧 常用调试命令

### OpenCV测试
```python
import cv2
cap = cv2.VideoCapture('rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101')
if cap.isOpened():
    ret, frame = cap.read()
    print(f"帧大小: {frame.shape}")
    cap.release()
```

### FFmpeg测试
```bash
# 获取流信息
ffprobe -v quiet -print_format json -show_format -show_streams rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101

# 实时播放
ffplay rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101
```

## 🚨 常见错误速查

| 错误信息 | 可能原因 | 解决方案 |
|----------|----------|----------|
| `无法打开RTSP流` | 网络不通 | 检查IP和端口 |
| `认证失败` | 用户名/密码错误 | 验证凭据 |
| `超时` | 网络延迟 | 增加超时时间 |
| `解码错误` | 编码格式不支持 | 检查设备编码设置 |

## 📊 性能参数

### 推荐配置
- **帧率**: 15-25 FPS
- **分辨率**: 720p-1080p
- **编码**: H.264
- **缓冲区**: 1-3帧

### 优化参数
```python
# 减少延迟
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FPS, 25)
```

## 🔍 调试工具

### 浏览器测试
- `test_webrtc.html` - WebRTC连接测试
- `webrtc_test_page.html` - 完整测试页面

### 日志查看
```bash
# 查看WebRTC服务器日志
tail -f logs/webrtc_server.log

# 查看系统日志
cat logs/system.log | grep RTSP
```

## 🎯 一键测试脚本

### 完整测试流程
```bash
# 1. 检查设备状态
python scripts/device_status_checker.py

# 2. 测试RTSP连接
python tests/test_rtsp_simple.py

# 3. 启动WebRTC服务器
python scripts/webrtc/real_webrtc_server.py --port 8090

# 4. 浏览器测试
# 打开 http://localhost:5173/test_webrtc.html
```

## 📞 技术支持

### 获取帮助
1. 查看 [RTSP_STREAM_PROCESSING_GUIDE.md](RTSP_STREAM_PROCESSING_GUIDE.md)
2. 运行 `python scripts/quick_check.py`
3. 检查 `logs/webrtc_server.log`