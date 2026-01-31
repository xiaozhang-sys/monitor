# 🚀 4小时极速部署指南

> 严格按照以下步骤，快速完成视频监控系统的本地部署

## ⏱️ 时间规划

| 阶段 | 时间 | 任务 |
|------|------|------|
| 环境准备 | 15分钟 | 安装Python和Node.js |
| 依赖安装 | 10分钟 | 安装前后端依赖 |
| 服务启动 | 5分钟 | 启动所有必要服务 |
| 设备测试 | 10分钟 | 查看监控画面并验证 |

## 🎯 第一步：环境准备（15分钟）

### Windows系统
```powershell
# 1. 安装Python 3.8+
# 访问：https://www.python.org/downloads/
# 安装时勾选"Add Python to PATH"

# 2. 验证Python安装
python --version

# 3. 安装Node.js 16+
# 访问：https://nodejs.org/en/download/

# 4. 验证Node.js安装
node --version
npm --version
```

### Linux系统（Ubuntu）
```bash
# 1. 安装Python 3.8+
sudo apt update
sudo apt install python3 python3-pip -y

# 2. 验证Python安装
python3 --version
pip3 --version

# 3. 安装Node.js 16+
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# 4. 验证Node.js安装
node --version
npm --version
```

## 🎯 第二步：依赖安装（10分钟）

### Windows系统
```powershell
# 在Monitor目录下执行

# 1. 安装后端依赖
pip install -r backend/requirements.txt

# 2. 安装前端依赖
cd frontend
npm install
cd ..
```

### Linux系统（Ubuntu）
```bash
# 在Monitor目录下执行

# 1. 安装后端依赖
pip3 install -r backend/requirements.txt

# 2. 安装前端依赖
cd frontend
npm install
cd ..
```

## 🎯 第三步：服务启动（5分钟）

### Windows手动启动
```powershell
# 在Monitor目录下打开多个终端窗口分别执行以下命令

# 终端1：启动后端服务
python backend/main.py

# 终端2：启动前端服务
cd frontend
npm run dev
cd ..

# 终端3：启动WebRTC服务器（HEVC兼容版本，已默认配置）
python scripts/webrtc/hevc_compat_server.py --port 8090

# （可选）终端4：启动HTTP测试服务器
python -m http.server 8081
```

### Linux手动启动
```bash
# 在Monitor目录下打开多个终端窗口分别执行以下命令

# 终端1：启动后端服务
python3 backend/main.py

# 终端2：启动前端服务
cd frontend
npm run dev
cd ..

# 终端3：启动WebRTC服务器（HEVC兼容版本，已默认配置）
python3 scripts/webrtc/hevc_compat_server.py --port 8090

# （可选）终端4：启动HTTP测试服务器
python3 -m http.server 8081
```

## ✅ 启动验证

访问以下地址确认服务正常：
- 🌐 前端页面：http://localhost:5173
- 📊 API文档：http://localhost:8004/docs
- 🔧 WebRTC服务器：http://localhost:8090

## 🎯 第四步：设备测试（10分钟）

### 4.1 系统内置设备测试

系统已预设了测试设备，无需额外配置即可查看实时监控画面：
- **录像机一**: rtsp://admin:Chang168@192.168.42.85:55401/Streaming/Channels/101
- **录像机二**: rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101
- **录像机三**: rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/102

### 4.2 浏览器测试
1. 打开 http://localhost:5173
2. 查看监控画面
3. 选择任意设备查看实时视频

## 📹 重要注意事项：HEVC/H.265视频支持

**关键要点：**
- 系统默认使用`hevc_compat_server.py`脚本将HEVC编码的RTSP流实时转换为浏览器兼容的H.264格式
- 所有启动脚本（quick_restart.bat、start_all_services.bat等）已自动配置为使用此兼容版本
- 此服务运行在端口8090
- 如果遇到视频黑屏问题，请确认系统是否正在使用HEVC兼容WebRTC服务器

**验证方法：**
```bash
# Windows
python scripts/webrtc/hevc_compat_server.py --port 8090

# Linux
python3 scripts/webrtc/hevc_compat_server.py --port 8090
```

**常见问题：**
- 如遇黑屏，请确认WebRTC服务器日志中显示"ICE连接状态: completed"
- 首次加载视频可能需要5-10秒的转码时间
- 如遇解码错误，检查HEVC兼容服务器是否正常运行

## 🎯 第五步：系统调优（可选）

### 5.1 性能优化

#### 调整WebRTC配置
编辑：`config/webrtc_config.json`
```json
{
  "rtsp_transport": "tcp",
  "buffer_size": 5,
  "frame_rate": 25,
  "max_bitrate": 2000000
}
```

#### 调整前端性能
在前端项目中添加以下配置到`vite.config.js`：
```javascript
import { defineConfig } from 'vite'

export default defineConfig({
  // ...现有配置
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return id.toString().split('node_modules/')[1].split('/')[0].toString();
          }
        }
      }
    }
  }
})
```

### 5.2 安全配置

#### 配置防火墙
```bash
# Windows PowerShell（以管理员身份运行）
New-NetFirewallRule -DisplayName "Monitor Backend" -Direction Inbound -Protocol TCP -LocalPort 8004 -Action Allow
New-NetFirewallRule -DisplayName "Monitor Frontend" -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow
New-NetFirewallRule -DisplayName "Monitor WebRTC" -Direction Inbound -Protocol TCP -LocalPort 8090 -Action Allow

# Ubuntu防火墙配置
sudo ufw allow 8004/tcp  # 后端API
sudo ufw allow 5173/tcp  # 前端服务
sudo ufw allow 8090/tcp  # WebRTC服务器
```

## 🚨 故障排查

### 常见问题速查表

| 问题现象 | 可能原因 | 解决方案 |
|----------|----------|----------|
| 页面无法访问 | 端口被占用 | 检查服务是否启动或修改端口配置 |
| 视频黑屏 | HEVC编码不兼容 | 确保`hevc_compat_server.py`正在运行 |
| 后端401错误 | 认证令牌过期 | 重新访问页面或清除浏览器缓存 |
| 延迟过高 | 网络带宽不足 | 降低视频分辨率或关闭其他占用带宽的程序 |
| WebRTC连接失败 | ICE连接超时 | 检查网络设置和防火墙配置 |

### 日志查看
```bash
# Windows PowerShell
# 查看后端服务日志（在运行后端的终端窗口中）
# 查看前端服务日志（在运行前端的终端窗口中）
# 查看WebRTC服务器日志（在运行WebRTC服务器的终端窗口中）

# 检查服务是否运行中
netstat -ano | findstr "8004 5173 8090"

# 查看进程
Get-Process -Name python,node | Format-Table -Property Name,Id
```

```bash
# Linux
sudo lsof -i :8004 -i :5173 -i :8090
ps aux | grep -E "python|npm"
```

## 📊 监控面板

### 系统状态检查
```bash
# Windows PowerShell - 创建系统状态检查脚本
$scriptContent = @"
Write-Host "=== 系统状态检查 ==="

Write-Host "服务端口状态："
netstat -ano | findstr "8004 5173 8090 8081"

Write-Host "\n资源使用："
Get-Process -Name python,node | Select-Object Name,Id,CPU,WS | Format-Table -AutoSize

Write-Host "\nWebRTC服务状态："
if ((Test-NetConnection -ComputerName localhost -Port 8090).TcpTestSucceeded) {
    Write-Host "✅ WebRTC服务器运行正常"
} else {
    Write-Host "❌ WebRTC服务器未运行，请启动：python scripts/webrtc/hevc_compat_server.py --port 8090"
}

Write-Host "\n前端服务状态："
if ((Test-NetConnection -ComputerName localhost -Port 5173).TcpTestSucceeded) {
    Write-Host "✅ 前端服务运行正常"
} else {
    Write-Host "❌ 前端服务未运行，请启动：cd frontend && npm run dev"
}

Write-Host "\n后端服务状态："
if ((Test-NetConnection -ComputerName localhost -Port 8004).TcpTestSucceeded) {
    Write-Host "✅ 后端服务运行正常"
} else {
    Write-Host "❌ 后端服务未运行，请启动：python backend/main.py"
}
"@

$scriptContent | Out-File -FilePath "check_status.ps1" -Encoding utf8

# 运行检查脚本
powershell -ExecutionPolicy Bypass -File check_status.ps1
```

```bash
# Linux - 创建系统状态检查脚本
echo '#!/bin/bash
echo "=== 系统状态检查 ==="
echo "\n服务端口状态："
sudo lsof -i :8004 -i :5173 -i :8090 -i :8081
echo "\n资源使用："
ps aux | grep -E "python|npm" | awk '{print $1, $2, $3, $4, $11}'
echo "\nWebRTC服务状态："
if nc -z localhost 8090; then
    echo "✅ WebRTC服务器运行正常"
else
    echo "❌ WebRTC服务器未运行，请启动：python3 scripts/webrtc/hevc_compat_server.py --port 8090"
fi
echo "\n前端服务状态："
if nc -z localhost 5173; then
    echo "✅ 前端服务运行正常"
else
    echo "❌ 前端服务未运行，请启动：cd frontend && npm run dev"
fi
echo "\n后端服务状态："
if nc -z localhost 8004; then
    echo "✅ 后端服务运行正常"
else
    echo "❌ 后端服务未运行，请启动：python3 backend/main.py"
fi' > check_status.sh

chmod +x check_status.sh
./check_status.sh
```

## 🎉 部署完成

恭喜！您的视频监控系统已成功部署：

- ✅ **设备管理**：内置测试设备，无需额外配置
- ✅ **实时监控**：WebRTC实时视频播放
- ✅ **HEVC支持**：专用转换服务确保所有编码格式兼容
- ✅ **低延迟**：优化的WebRTC传输确保流畅体验
- ✅ **跨平台**：支持Windows和Linux系统

## 📞 技术支持

如遇到问题，请按以下顺序排查：
1. **检查服务状态**：运行`check_status.ps1`或`check_status.sh`脚本
2. **查看终端日志**：检查各个服务的终端输出
3. **确认HEVC服务**：确保`hevc_compat_server.py`正在运行（端口8090）
4. **参考文档**：查看`docs/TROUBLESHOOTING.md`和`docs/HEVC_FIX_GUIDE.md`

**系统已就绪，开始享受您的智能监控体验吧！** 🚀