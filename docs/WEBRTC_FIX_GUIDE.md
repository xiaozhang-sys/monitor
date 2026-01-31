# WebRTC连接问题修复指南

## 🚨 当前问题总结

用户遇到的WebRTC连接错误：
- `SDP设置失败: InvalidAccessError: Failed to execute 'setRemoteDescription'`
- `视频加载失败: WebRTC连接失败`
- `所有SDP修复尝试都失败: OperationError: Session error code: ERROR_CONTENT`
- `视频没有声音: WebRTC音频轨道缺失`

## 🔧 已实施的修复方案

### 1. 服务器端修复
✅ **已部署兼容WebRTC服务器** (`hevc_compat_server.py`)
- 解决了SDP指纹验证问题
- 提供标准兼容的SDP格式
- 支持RTSP流捕获和WebRTC转换
- 添加了音频轨道处理功能，支持音频流传输

### 2. 前端修复
✅ **已更新前端连接逻辑** (`SmartVideoPlayer.vue`)
- 修复了API端点调用
- 增强了SDP格式处理
- 添加了兼容性修复机制
- 修复了RTSP通道选择逻辑，确保使用正确的通道号

### 3. 测试工具
✅ **已创建完整测试工具** (`test_webrtc.html`)
- 支持所有服务状态检查
- 提供RTSP连接测试
- 实时WebRTC连接验证
- 支持音频流测试

## 🚀 快速修复步骤

### 步骤1: 验证服务状态
```bash
# 打开测试页面
start d:\code\Monitor\test_webrtc.html
```
或访问：`http://localhost:5173/test_webrtc.html`

### 步骤2: 使用测试工具
1. **检查所有服务状态** - 点击"检查所有服务"
2. **测试RTSP连接** - 输入RTSP URL并点击测试
3. **启动WebRTC连接** - 点击"启动WebRTC"

### 步骤3: 验证修复效果
- ✅ 如果看到绿色"✅ WebRTC连接成功"表示修复成功
- ❌ 如果仍然失败，查看详细错误日志

## 📋 手动测试命令

### 测试WebRTC服务器
```bash
curl -X POST http://localhost:8090/api/offer \
  -H "Content-Type: application/json" \
  -d '{
    "sdp": "v=0\r\no=- 123456789 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\nc=IN IP4 0.0.0.0\r\na=sendonly\r\na=rtpmap:96 H264/90000\r\n",
    "rtsp_url": "rtsp://admin:12345@192.168.1.64:554/Streaming/Channels/101",
    "type": "offer"
  }'
```

### 测试RTSP流
```bash
curl -X POST http://localhost:8090/api/stream/start \
  -H "Content-Type: application/json" \
  -d '{"rtsp_url": "rtsp://admin:12345@192.168.1.64:554/Streaming/Channels/101"}'
```

## 🔄 重启服务

### 停止所有WebRTC服务
```bash
# 在终端中执行
netstat -ano | findstr :8090
taskkill /PID [PID] /F
```

### 启动兼容WebRTC服务器
```bash
# 在项目目录中执行
cd d:\code\Monitor
python scripts\webrtc\hevc_compat_server.py --host 0.0.0.0 --port 8090
```

## 🔍 常见问题排查

### 1. 端口占用问题
```bash
# 检查8090端口
Get-NetTCPConnection -LocalPort 8090
```

### 2. 依赖问题
```bash
# 安装依赖
pip install aiortc aiohttp aiohttp-cors av opencv-python numpy
```

### 3. 防火墙问题
- 确保Windows防火墙允许8090端口
- 检查杀毒软件是否阻止连接

### 4. 浏览器兼容性
- 使用Chrome 88+ 或 Firefox 84+
- 确保浏览器支持WebRTC
- 清除浏览器缓存

## 📊 验证修复成功

### 成功指标
1. ✅ WebRTC服务器响应 `/health` 端点
2. ✅ RTSP连接测试返回视频信息
3. ✅ WebRTC连接建立并显示视频
4. ✅ 前端监控系统正常显示视频流

### 预期输出
```json
{
  "status": "healthy",
  "timestamp": 1634567890,
  "connections": 1
}
```

## 🆘 如果仍然失败

### 收集调试信息
1. 使用测试工具导出完整日志
2. 检查浏览器控制台错误
3. 查看服务器端日志

### 联系支持
提供以下信息：
- 测试工具导出的日志文件
- 浏览器控制台错误截图
- 操作系统和浏览器版本
- 具体的RTSP URL格式

## 📁 相关文件位置

- **兼容服务器**: `scripts/webrtc/hevc_compat_server.py`
- **前端组件**: `frontend/src/components/SmartVideoPlayer.vue`
- **测试工具**: `test_webrtc.html`
- **配置文件**: `config/webrtc_config.json`
- **启动脚本**: `scripts/webrtc/start_webrtc_server.bat`