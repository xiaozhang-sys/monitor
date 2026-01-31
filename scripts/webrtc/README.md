# WebRTC RTSP服务器

## 概述

这是监控系统使用的WebRTC RTSP转码服务器，将RTSP视频流转换为WebRTC格式，实现浏览器实时播放。目前系统默认使用HEVC兼容版本，以支持H.265编码视频。

## 文件结构

```
webrtc/
├── hevc_compat_server.py      # HEVC兼容WebRTC服务器（生产环境使用，推荐）
├── real_webrtc_server.py      # 旧版WebRTC服务器（不推荐，不支持H.265）
├── webrtc_simple_server.py    # 简化版WebRTC服务器（备用）
├── start_webrtc_server.bat    # Windows启动脚本
├── README.md                  # 本文档
└── webrtc_config.json         # 配置文件
```

## 为什么之前使用模拟服务器？

1. **历史原因**：项目初期为了快速验证WebRTC功能，使用了模拟服务器
2. **简化开发**：模拟服务器只返回SDP，不处理实际媒体流，便于调试
3. **依赖问题**：真正的WebRTC服务器需要aiortc等复杂依赖

## 当前状态

✅ **已解决**：系统默认使用HEVC兼容WebRTC服务器
✅ **已标准化**：所有启动脚本自动使用hevc_compat_server.py
✅ **已对接**：前端配置已指向正确的WebRTC端口8090
✅ **支持H.265**：能够处理H.265/HEVC编码的RTSP流

## 使用方法

### 启动WebRTC服务器

```bash
# Windows（推荐使用系统启动脚本）
quick_restart.bat
tools\start_all_services.bat

scripts\webrtc\start_webrtc_server.bat

# 单独启动HEVC兼容WebRTC服务器（推荐）
# Windows
python scripts/webrtc/hevc_compat_server.py --host 0.0.0.0 --port 8090

# Linux/Mac
python3 scripts/webrtc/hevc_compat_server.py --host 0.0.0.0 --port 8090
```

### 配置参数

- **端口**: 8090（前端已配置）
- **主机**: 0.0.0.0（允许外部访问）
- **CORS**: 允许前端跨域访问
- **HEVC支持**: 自动处理H.265编码视频流

### API端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/offer` | POST | WebRTC标准offer处理 |
| `/api/stream/start` | POST | 简化流启动 |
| `/api/stream/stop` | POST | 停止流 |

### 前端配置

前端已自动配置为连接端口8090：
- `VITE_WEBRTC_PORT=8090`
- `VITE_WEBRTC_BASE_URL=http://localhost:8090`

## 故障排除

### 依赖安装

```bash
pip install aiortc aiohttp aiohttp-cors av opencv-python
```

### 常见问题

1. **端口占用**：检查8090端口是否被占用
2. **RTSP连接失败**：验证RTSP地址和凭据
3. **WebRTC连接失败**：检查防火墙设置

### 日志查看

日志文件：`webrtc_server.log`

## 测试验证

访问以下地址测试WebRTC功能：
- 前端界面：http://localhost:5173
- WebRTC健康检查：http://localhost:8090/health
- 测试页面：http://localhost:5173/debug_video.html