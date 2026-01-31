# qianyan

零售天眼通 - 基于Web的多品牌摄像头监控系统，支持实时视频流、设备管理、异常告警等功能。

## 🚀 快速开始

### 1️⃣ 环境要求
- Python 3.8+
- Node.js 16+
- Windows/Linux/macOS

### 当前端口配置
- **后端API**: 8004 (HTTP)
- **前端服务**: 5174 (HTTP) 
- **WebRTC服务**: 8090 (HTTP) - HEVC/H.265兼容
- **WebSocket监控**: 8080 (备用)

### 2️⃣ 一键启动
```bash
# Windows
scripts\start_stable.bat

# 手动启动步骤
# 1. 安装后端依赖
pip install -r backend/requirements.txt

# 2. 安装前端依赖
cd frontend
npm install
cd ..

# 3. 启动后端服务
python backend/main.py

# 4. 启动前端服务
cd frontend
npm run dev
cd ..

# 5. 启动HEVC兼容WebRTC服务器
python scripts/webrtc/hevc_compat_server.py --port 8090
```

### 3️⃣ 访问系统
- **Web界面**: http://localhost:5174
- **API文档**: http://localhost:8004/docs
- **WebRTC测试**: http://localhost:8090/health

## 📁 项目结构

```
Monitor/
├── 📁 backend/          # Python后端服务
├── 📁 frontend/         # Vue 3前端界面
├── 📁 scripts/          # 管理脚本工具（已清理优化）
├── 📁 config/           # 配置文件
└── 📁 docs/            # 项目文档
```

## 🎯 功能特性

- ✅ **多品牌支持**: 兼容多种主流监控设备品牌
- ✅ **实时视频**: WebRTC低延迟播放
- ✅ **音频支持**: 实时音频流传输
- ✅ **正确通道显示**: 修复通道选择逻辑，确保不同通道显示正确画面
- ✅ **设备管理**: 批量导入、状态监控
- ✅ **异常告警**: 设备离线通知
- ✅ **跨平台**: Windows/Linux/macOS

## 📄 许可证

Apache License 2.0