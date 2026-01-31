# 🔧 故障排查指南

## 🚨 常见问题速查表

### 问题1：服务无法启动
```bash
# 检查Docker状态
docker-compose ps

# 查看日志
docker-compose logs backend
docker-compose logs srs
docker-compose logs frontend

# 重启服务
docker-compose restart
```

### 问题2：无法访问Web界面
```bash
# 检查端口占用
netstat -tulnp | grep :80

# 检查防火墙
ufw status

# 测试网络连通性
curl http://localhost
curl http://localhost:8000/health
```

### 问题3：摄像头无法连接
```bash
# 检查设备连通性
ping 192.168.1.64

# 检查RTSP端口
telnet 192.168.1.64 554

# 测试RTSP流
ffmpeg -i rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101 -vframes 1 test.jpg
```

### 问题4：视频无法播放
```bash
# 检查SRS状态
curl http://localhost:8085/api/v1/summaries

# 检查流媒体日志
docker-compose logs srs

# 测试HTTP-FLV流
curl http://localhost:8085/live/test.flv
```

### 问题5：所有通道显示相同画面
**症状**：不同通道显示相同的视频画面

**根因分析**：
- RTSP URL构建逻辑错误，错误地使用了总通道数(chs)而非实际选择的通道号(channel)
- 前端组件在构建RTSP URL时未正确获取用户选择的通道号

**解决方案**：
1. 确认前端组件使用正确的通道号：`props.device.channel || props.device.chs || 1`
2. 重启前端开发服务器：`npm run dev`

### 问题6：视频没有声音
**症状**：视频可以正常播放，但没有声音

**根因分析**：
- WebRTC服务器未实现音频轨道处理功能
- 音频流未被正确捕获和转换

**解决方案**：
1. 确认使用最新的WebRTC服务器：`hevc_compat_server.py`
2. 检查WebRTC服务器是否正常运行：`python scripts/webrtc/hevc_compat_server.py --host 0.0.0.0 --port 8090`
3. 验证前端是否请求音频轨道：在`SmartVideoPlayer.vue`中确认`offerToReceiveAudio: true`

### 问题7：HEVC编码视频黑屏
**症状**：视频黑屏但有连接状态指示

**根因分析**：
- 摄像头使用HEVC/H.265编码格式，但大多数浏览器不支持HEVC编码的WebRTC视频流
- 未使用专用的HEVC兼容服务器

**解决方案**：
1. 停止当前的WebRTC服务
2. 启动HEVC兼容服务器：`python scripts/webrtc/hevc_compat_server.py --port 8090`
3. 刷新前端页面：http://localhost:5173
4. 查看WebRTC服务器日志确认HEVC转码状态

**验证步骤**：
- ✅ WebRTC服务器日志显示"ICE连接状态: completed"
- ✅ 浏览器控制台没有解码错误
- ✅ 视频画面正常显示

## 🔍 认证问题排查

### 401未授权错误
**症状**：设备管理页面提示"未授权访问，请检查登录状态"

**根因分析**：
1. 重复认证检查：多个页面独立处理401错误
2. 分散的认证逻辑：每个页面都有自己的axios实例和token获取逻辑
3. 错误处理不当：401错误在多个地方被处理

**解决方案**：
1. **统一认证处理**：使用路由守卫统一处理401错误
2. **统一API客户端**：所有页面使用同一个axios实例
3. **优化错误处理**：401错误不再显示提示，直接跳转登录页

**验证步骤**：
- ✅ 只需一次登录即可访问所有功能
- ✅ 无重复401错误提示
- ✅ 无重复认证检查

### 登录验证测试
```bash
# 测试认证API
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# 验证token
curl -X GET http://localhost:8000/api/devices \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔍 异常处理系统

### 系统架构
- **预防层**：资源监控和预警
- **检测层**：实时异常检测
- **响应层**：自动重试和降级
- **恢复层**：一键故障恢复

### 核心功能
- **自动重试机制**：连接失败5秒后自动重试
- **降级处理**：主摄像头故障自动切换到备用方案
- **资源监控**：实时监控CPU、内存、网络状态
- **故障转移**：WebRTC失败时自动切换到RTSP直连

### 一键恢复
```bash
# 方法1: 使用批处理脚本
double-click quick_recovery.bat

# 方法2: 使用Python工具
python recovery_tool.py quick

# 方法3: 完整恢复
python recovery_tool.py full
```

## 📊 详细排查步骤

### 1. 系统层面检查

#### 1.1 资源检查
```bash
# CPU使用率
top -p $(pgrep -f "docker")

# 内存使用率
free -h

# 磁盘使用率
df -h

# 网络状态
netstat -tulnp
```

#### 1.2 Docker检查
```bash
# Docker状态
systemctl status docker

# 容器状态
docker ps -a

# 镜像状态
docker images

# 网络状态
docker network ls
docker network inspect monitor_default
```

### 2. 后端服务检查

#### 2.1 API健康检查
```bash
# 基础健康检查
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# 详细API测试
curl -X GET http://localhost:8000/api/devices

# 认证测试
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

#### 2.2 数据库检查
```bash
# 进入容器
docker-compose exec backend bash

# 检查数据库
sqlite3 /app/data/monitor.db ".tables"
sqlite3 /app/data/monitor.db "SELECT COUNT(*) FROM devices"
sqlite3 /app/data/monitor.db "SELECT * FROM devices LIMIT 5"
```

#### 2.3 日志分析
```bash
# 实时日志
docker-compose logs -f backend

# 错误日志过滤
docker-compose logs backend 2>&1 | grep ERROR

# 访问日志
docker-compose logs backend 2>&1 | grep "GET\|POST\|PUT\|DELETE"
```

### 3. 流媒体服务检查

#### 3.1 SRS状态检查
```bash
# SRS API状态
curl http://localhost:8085/api/v1/summaries | jq

# 流列表
curl http://localhost:8085/api/v1/streams | jq

# 客户端列表
curl http://localhost:8085/api/v1/clients | jq
```

#### 3.2 流媒体测试
```bash
# 测试RTMP推流
ffmpeg -re -i test.mp4 -c copy -f flv rtmp://localhost:1935/live/test

# 测试HTTP-FLV播放
ffplay http://localhost:8085/live/test.flv

# 测试WebRTC
# 使用浏览器访问: http://localhost:8085/players/rtc_player.html
```

#### 3.3 端口检查
```bash
# 检查监听端口
ss -tulnp | grep :1935  # RTMP
ss -tulnp | grep :8085  # HTTP-FLV/WebRTC
ss -tulnp | grep :1985  # SRS API
```

### 4. 前端服务检查

#### 4.1 前端状态检查
```bash
# 检查Nginx状态
docker-compose logs nginx

# 测试静态资源
curl -I http://localhost/css/app.css
curl -I http://localhost/js/app.js

# 测试API代理
curl -I http://localhost/api/health
```

#### 4.2 浏览器调试
```javascript
// 浏览器控制台检查
console.log('Testing API connectivity...');
fetch('/api/health').then(r => r.json()).then(console.log);

// 检查WebSocket连接
console.log('Testing WebSocket...');
new WebSocket('ws://localhost:8085/ws');

// 检查视频播放
console.log('Testing video playback...');
const video = document.createElement('video');
video.src = 'http://localhost:8085/live/test.flv';
video.play().catch(console.error);
```

### 5. 网络层面检查

#### 5.1 网络连通性
```bash
# 内网连通性
ping 192.168.1.64

# 外网连通性
ping 8.8.8.8

# DNS解析
nslookup google.com
```

#### 5.2 端口连通性
```bash
# RTSP端口测试
telnet 192.168.1.64 554

# HTTP端口测试
telnet localhost 80

# SRS端口测试
telnet localhost 8085
```

## 📈 性能监控

### 关键性能指标
- **响应时间**: <500ms (优秀), 500ms-1s (良好), >1s (需要优化)
- **错误率**: <1% (优秀), 1-5% (可接受), >5% (需要处理)
- **可用性**: >99.9% (目标), 99-99.9% (可接受), <99% (需要修复)
- **恢复时间**: <30秒 (优秀), 30-60秒 (良好), >60秒 (需要优化)

### 实时监控
- **服务器状态**: 在线/离线/警告
- **摄像头连接**: 主码流/子码流状态
- **网络延迟**: 实时响应时间
- **错误计数**: 累计错误次数

## 🔍 故障诊断工具

### 健康检查
```bash
# 系统健康检查
http://localhost:8000/health

# SRS健康检查
http://localhost:8085/api/v1/summaries

# 摄像头测试
python scripts/test_camera.py 192.168.1.64
```

### 网络诊断
```bash
# 使用ping测试连接
ping -c 4 192.168.1.64

# 使用telnet测试端口
telnet 192.168.1.64 554

# 使用ffmpeg测试RTSP流
ffmpeg -i rtsp://admin:password@192.168.1.64/Streaming/Channels/101 -t 5 -f null -
```

### 日志分析
```bash
# 查看实时日志
tail -f logs/backend.log
tail -f logs/srs.log

# 搜索错误日志
grep "ERROR" logs/backend.log
grep "WARN" logs/srs.log
```

## 🎯 故障排除速查表

| 问题症状 | 可能原因 | 解决方案 | 检查命令 |
|---------|----------|----------|----------|
| 服务无法启动 | Docker未运行 | 启动Docker | `systemctl start docker` |
| 无法访问Web界面 | 端口占用 | 检查端口占用 | `netstat -tulnp` |
| 摄像头离线 | RTSP地址错误 | 验证RTSP地址 | `ffmpeg -i rtsp://...` |
| 频繁重连 | 系统资源不足 | 关闭其他程序 | `top` |
| 端口占用 | 其他程序占用 | 使用一键恢复 | `quick_recovery.bat` |
| 401错误 | 认证失败 | 重新登录 | 检查token有效性 |
| 视频卡顿 | 网络延迟 | 检查网络质量 | `ping 192.168.1.64` |

## 🚀 一键恢复系统

### 使用场景
- 服务异常无法启动
- 网络连接中断
- 认证系统故障
- 流媒体服务异常

### 恢复步骤
1. **自动检测**：系统自动检测常见问题
2. **一键修复**：执行标准化修复流程
3. **状态验证**：确认系统恢复正常
4. **报告生成**：生成详细的状态报告

### 恢复验证
- ✅ 所有服务正常启动
- ✅ 认证系统正常工作
- ✅ 摄像头连接正常
- ✅ 视频播放流畅
- ✅ 网络连接稳定

## 📞 技术支持

### 自助资源
- **监控面板**: http://localhost:8081/players/error_handler.html
- **恢复工具**: scripts/recovery_tool.py
- **测试脚本**: scripts/simple_exception_test.py
- **日志文件**: logs/recovery_log.txt

### 紧急联系
- **紧急恢复**: 运行quick_recovery.bat
- **技术支持**: 通过监控面板反馈问题
- **文档更新**: 定期检查最新文档版本

---

## 🎯 总结

本故障排查指南整合了认证问题、异常处理、性能监控等核心内容，提供：

1. **快速定位**：常见问题速查表
2. **详细步骤**：系统化排查流程
3. **一键恢复**：自动化故障处理
4. **实时监控**：24/7系统状态监控
5. **完整工具链**：从诊断到恢复的全套工具

**任何问题都能在5分钟内找到解决方案！**