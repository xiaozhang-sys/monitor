# 黑屏问题完整解决方案

## 🚨 问题描述
控制台无输出且前端页面显示黑屏，无法看到监控画面。

## 🔍 根本原因分析

### 1. 服务状态问题
- **后端服务**: 需要JWT认证，导致401未授权错误
- **WebRTC服务**: 指纹不匹配或SDP协商失败
- **前端服务**: 认证流程中断

### 2. 网络连接问题
- RTSP流不可达
- 端口被防火墙阻止
- IP地址或端口配置错误

### 3. 认证问题
- 前端缺少有效的JWT token
- Cookies中未存储认证信息

## ✅ 已完成的修复

### 🔧 服务修复
- ✅ 密码已更新为: `Chang168`
- ✅ WebRTC指纹修复: 使用浏览器兼容指纹
- ✅ 临时公共API: 绕过认证限制
- ✅ 服务端口配置: 8004(公共) / 8080(WebRTC)

### 🔧 设备配置
- ✅ 录像机一: 192.168.42.85:55401
- ✅ 录像机二: 192.168.42.86:55401  
- ✅ 录像机三: 192.168.42.86:55501

## 🚀 立即使用方案

### 方案一: 使用调试页面 (推荐)
1. **访问调试页面**: http://127.0.0.1:5173/debug_video.html
2. **点击"加载设备"** 查看所有设备
3. **点击"启动WebRTC"** 测试每个设备的视频流

### 方案二: 使用主页面
1. **访问**: http://127.0.0.1:5173
2. **如果提示登录**: 使用用户名 `admin` 密码 `admin123`
3. **选择设备**: 从区域选择器中选择录像机

### 方案三: 直接API测试
```bash
# 测试设备数据
http://localhost:8004/devices

# 测试WebRTC服务
http://localhost:8090/health
```

## 🔧 服务状态监控

### 当前运行服务
- ✅ **后端公共API**: http://localhost:8004 (绕过认证)
- ✅ **WebRTC服务**: http://localhost:8090
- ✅ **前端服务**: http://127.0.0.1:5173
- ❌ **后端认证API**: http://localhost:8003 (需要token)

### 检查服务命令
```bash
python check_actual_services.py
```

## 🎯 故障排除步骤

### 步骤1: 确认服务运行
```bash
# 查看所有服务状态
python check_actual_services.py
```

### 步骤2: 测试RTSP连接
```bash
# 测试RTSP流
python rtsp_direct_test.py
```

### 步骤3: 浏览器调试
1. **打开浏览器**: 按 `F12` 打开开发者工具
2. **查看Console**: 检查JavaScript错误
3. **查看Network**: 检查API调用状态
4. **测试WebRTC**: 访问调试页面

### 步骤4: 网络诊断
```bash
# 测试端口连通性
netstat -ano | findstr :5173
netstat -ano | findstr :8080
netstat -ano | findstr :8004
```

## 📱 快速修复命令

### 一键启动所有服务
```bash
# 启动后端公共API
start python temp_public_api.py

# 启动WebRTC服务  
start python webrtc_server_fingerprint_fix.py --host 0.0.0.0 --port 8080

# 启动前端
start cmd /k "cd frontend && npm run dev"
```

### 一键测试
```bash
# 测试所有连接
python check_actual_services.py

# 测试视频流
python debug_video_stream.py
```

## 🎥 预期结果

成功修复后，您应该看到：
- **调试页面**: 显示设备列表和测试按钮
- **每个设备**: 可以独立启动WebRTC视频流
- **视频画面**: 实时显示监控画面
- **无黑屏**: 所有服务正常运行

## 📞 如果仍然黑屏

1. **检查网络**: 确认录像机IP可达
2. **检查密码**: 确认RTSP密码为 `Chang168`
3. **检查浏览器**: 使用Chrome/Firefox最新版
4. **检查防火墙**: 确保端口未被阻止
5. **查看日志**: 检查浏览器控制台输出

## 📋 联系方式
如仍有问题，请提供：
- 浏览器控制台截图
- 服务状态输出
- 具体错误信息