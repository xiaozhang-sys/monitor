# 登录问题排查指南

## 🎯 当前服务状态

所有服务已正确配置并运行：

| 服务类型 | 端口 | 状态 | 访问地址 | 说明 |
|---------|------|------|----------|------|
| 前端Vue应用 | 5173 | ✅ 运行中 | http://localhost:5173 | 用户界面 |
| 后端API | 8001 | ✅ 运行中 | http://localhost:8001 | 登录/设备管理 |
| WebRTC服务 | 8090 | ✅ 运行中 | http://localhost:8090 | 视频流处理 |
| 心跳监控 | - | ✅ 运行中 | 后台服务 | 设备状态监控 |

## 🔐 登录验证

### 正确的登录信息
- **用户名**: `admin`
- **密码**: `admin123`
- **登录接口**: `http://localhost:8001/token`

### 测试验证
```bash
# 测试登录接口
curl -X POST http://localhost:8001/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

预期返回：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

## 🚀 使用步骤

### 1. 直接访问
- **前端界面**: http://localhost:5173
- **API文档**: http://localhost:8001/docs
- **WebRTC测试**: http://localhost:8090/sdp_test.html

### 2. 登录流程
1. 打开 http://localhost:5173
2. 输入用户名: `admin`
3. 输入密码: `admin123`
4. 点击登录

### 3. 故障排查

#### 如果登录失败：

**检查服务状态**:
```bash
# 检查端口占用
Get-NetTCPConnection -State Listen | Where-Object {$_.LocalPort -in 5173,8001,8080}
```

**检查网络连接**:
- 确保所有服务都在本地运行
- 检查防火墙设置
- 确认端口未被其他应用占用

**浏览器调试**:
1. 按F12打开开发者工具
2. 查看Network标签中的登录请求
3. 检查Console中的错误信息

#### 常见错误及解决：

| 错误现象 | 可能原因 | 解决方案 |
|---------|----------|----------|
| 404错误 | 后端API未启动 | 确认8001端口服务运行 |
| 401错误 | 用户名密码错误 | 使用admin/admin123 |
| 网络错误 | 端口被占用 | 检查服务端口配置 |
| 跨域错误 | CORS配置问题 | 确认后端CORS已配置 |

## 📋 服务启动顺序

如果服务异常，按以下顺序重启：

1. **停止所有服务**
2. **启动后端API**:
   ```bash
   cd d:\code\Monitor\backend
   python main.py
   ```

3. **启动WebRTC**:
   ```bash
   cd d:\code\Monitor\streaming\tools
   python webrtc_server_sdp_final.py
   ```

4. **启动前端**:
   ```bash
   cd d:\code\Monitor\frontend
   npm run dev -- --host=0.0.0.0 --port=5173
   ```

5. **启动心跳监控**:
   ```bash
   cd d:\code\Monitor\scripts
   python heartbeat_service.py
   ```

## 🎉 成功标志

- ✅ 前端页面正常加载
- ✅ 登录接口返回200状态码
- ✅ 获取到JWT令牌
- ✅ 能够访问受保护的路由

所有服务已就绪，现在可以正常登录使用！