# 🎥 零售天眼通 - 精简优化版

基于Web的多品牌摄像头监控系统，支持实时视频流、设备管理、异常告警等功能。

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

## 🔧 核心脚本（清理后）

### 📊 系统管理
- **auto_setup.py** - 自动配置设置
- **start_stable.bat** - 一键启动服务
- **quick_check.py** - 系统健康检查

### 🔍 设备管理
- **query_devices.py** - 查询设备信息
- **import_devices.py** - 从CSV导入设备
- **device_status_checker.py** - 设备状态监控

### 🛠️ 故障修复
- **fix_port_mapping.py** - 修复端口映射
- **fix_nvr_config.py** - 修复NVR配置
- **exception_handler.py** - 异常处理

## 📚 完整文档

- [📋 项目结构](PROJECT_STRUCTURE.md) - 完整项目架构说明
- [🎯 清理报告](scripts/CLEANUP_REPORT.md) - 脚本清理详情
- [⚙️ 配置指南](config/README.md) - 详细配置说明
- [🔧 WebRTC修复指南](docs/WEBRTC_FIX_GUIDE.md) - WebRTC连接问题和音频功能修复
- [🎥 RTSP使用速查表](docs/RTSP_CHEATSHEET.md) - RTSP流处理和通道选择指南
- [🛠️ 故障排除](docs/TROUBLESHOOTING.md) - 常见问题解决方案

## 🎯 功能特性

- ✅ **多品牌支持**: 兼容多种主流监控设备品牌
- ✅ **实时视频**: WebRTC低延迟播放
- ✅ **音频支持**: 实时音频流传输
- ✅ **正确通道显示**: 修复通道选择逻辑，确保不同通道显示正确画面
- ✅ **设备管理**: 批量导入、状态监控
- ✅ **异常告警**: 设备离线通知
- ✅ **跨平台**: Windows/Linux/macOS

## 🔍 常用命令

### 📊 设备管理
```bash
# 查看设备状态
python scripts/device_status_checker.py

# 导入设备数据
python scripts/import_devices.py devices.csv

# 查询设备信息
python scripts/query_devices.py
```

### 🛠️ 系统维护
```bash
# 系统健康检查
python scripts/quick_check.py

# 数据库管理
python scripts/db_manager.py --help

# 修复配置
python scripts/fix_nvr_config.py
```

## 📋 技术栈

- **数据库**: SQLite (轻量级)
- **后端**: Python FastAPI
- **前端**: Vue 3 + Vite
- **流媒体**: WebRTC + RTSP
- **监控**: 心跳检测 + 异常处理

## 📹 特别注意

**HEVC/H.265视频流支持:**
- 系统使用`hevc_compat_server.py`脚本将HEVC编码的RTSP流实时转换为浏览器兼容的H.264格式
- 此转换服务默认运行在端口8090
- 如遇黑屏问题，请确保此服务正常运行

## 🚨 技术支持

遇到问题请查看：
- [🎯 清理报告](scripts/CLEANUP_REPORT.md) - 了解当前架构
- [📋 项目结构](PROJECT_STRUCTURE.md) - 完整技术说明
- [🛠️ 系统检查](scripts/quick_check.py) - 诊断工具

---

*架构: SQLite + FastAPI + Vue 3 + WebRTC + HEVC兼容服务*
*清理版本: v2.1 - HEVC兼容优化版*