# 测试目录 (tests/)

## 📋 目录结构

```
tests/
├── README.md                 # 本说明文档
├── test_tools.py            # 统一测试入口
├── rtsp/
│   └── test_rtsp_direct.py   # RTSP流连接测试
├── webrtc/
│   └── test_webrtc_debug.py  # WebRTC黑屏问题调试
├── services/
│   └── test_service_health.py # 服务健康检查
├── *.html                   # 前端测试页面
└── *.py                     # 其他测试脚本
```

## 🎯 测试分类

### 1. 服务测试 (services/)
- **test_service_health.py** - 检查所有后端服务运行状态
- **test_tools.py** - 统一测试入口

### 2. 流媒体测试 (rtsp/)
- **test_rtsp_direct.py** - 直接测试RTSP流连接

### 3. WebRTC测试 (webrtc/)
- **test_webrtc_debug.py** - WebRTC黑屏问题专项调试

### 4. 前端测试 (*.html)
- **login_test.html** - 登录流程测试
- **webrtc_test.html** - WebRTC连接测试
- **test_monitor.html** - 监控功能测试

## 🚀 使用方法

### 快速测试
```bash
# 运行所有测试
python tests/test_tools.py

# 运行特定测试
python tests/services/test_service_health.py
python tests/rtsp/test_rtsp_direct.py
python tests/webrtc/test_webrtc_debug.py
```

### 前端测试
直接在浏览器中打开对应的HTML文件进行测试。

## 📊 测试覆盖范围

- ✅ 后端服务健康检查
- ✅ RTSP流连接测试
- ✅ WebRTC连接调试
- ✅ 前端功能测试
- ✅ 设备连接测试

## 🛠️ 添加新测试

1. 根据测试类型放入对应子目录
2. 遵循命名规范：`test_*.py`
3. 在test_tools.py中添加统一调用接口
4. 更新本README文档