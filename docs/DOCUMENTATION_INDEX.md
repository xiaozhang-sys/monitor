# 📚 项目文档索引

## 🎯 文档结构概览

本项目已重构为精简优化版本，所有文档都与当前SQLite + FastAPI + Vue 3 + WebRTC + HEVC兼容服务架构匹配。

## 📋 核心文档

### 🔍 项目总览
- **[README.md](README.md)** - 项目快速入门指南
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - 完整项目架构说明
- **[scripts/CLEANUP_REPORT.md](scripts/CLEANUP_REPORT.md)** - 脚本清理详情记录

### ⚙️ 技术文档
- **当前架构**: SQLite + FastAPI + Vue 3 + WebRTC + HEVC兼容服务
- **数据库**: 轻量级SQLite单文件存储
- **后端**: Python FastAPI框架
- **前端**: Vue 3 + Vite构建
- **流媒体**: WebRTC实时通信 + RTSP协议
- **HEVC支持**: 专用HEVC转H.264兼容服务

### 🔌 端口配置
- **后端API**: 8004
- **前端服务**: 5173
- **WebRTC服务**: 8081
- **HEVC兼容服务**: 8090

### 🎥 流媒体处理
- **[RTSP_STREAM_PROCESSING_GUIDE.md](RTSP_STREAM_PROCESSING_GUIDE.md)** - RTSP流处理完整指南
- **[RTSP_CHEATSHEET.md](RTSP_CHEATSHEET.md)** - RTSP流处理速查表（包含通道选择逻辑）
- **[WEBRTC_FIX_GUIDE.md](WEBRTC_FIX_GUIDE.md)** - WebRTC连接问题和音频功能修复指南
- **[HTTP_DEVICE_PATHS_GUIDE.md](HTTP_DEVICE_PATHS_GUIDE.md)** - HTTP设备路径配置指南

### 📋 配置和故障排除
- **[CONFIG_GUIDE.md](CONFIG_GUIDE.md)** - 配置指南
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - 故障排除指南
- **[troubleshooting/BLACK_SCREEN_SOLUTION.md](troubleshooting/BLACK_SCREEN_SOLUTION.md)** - 黑屏问题解决方案
- **[troubleshooting/LOGIN_TROUBLESHOOT.md](troubleshooting/LOGIN_TROUBLESHOOT.md)** - 登录问题排查

### 📊 项目文档
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API文档
- **[QUICK_START.md](QUICK_START.md)** - 快速入门指南
- **[HEVC_FIX_GUIDE.md](HEVC_FIX_GUIDE.md)** - HEVC修复指南
- **[PORT_FIX_SUMMARY.md](PORT_FIX_SUMMARY.md)** - 端口修复总结

## 🚀 快速开始路径

### 1️⃣ 环境检查
```bash
# 检查系统状态
python scripts/quick_check.py

# 查看设备状态
python scripts/device_status_checker.py
```

### 2️⃣ 系统启动
```bash
# Windows多终端启动（需要3个终端）
# 终端1: 启动后端服务
python backend/main.py
# 终端2: 启动前端服务
cd frontend && npm run dev
# 终端3: 启动HEVC兼容WebRTC服务器
python scripts/webrtc/hevc_compat_server.py --port 8090

# Linux/macOS多终端启动（需要3个终端）
# 终端1: 启动后端服务
python3 backend/main.py
# 终端2: 启动前端服务
cd frontend && npm run dev
# 终端3: 启动HEVC兼容WebRTC服务器
python3 scripts/webrtc/hevc_compat_server.py --port 8090
```

### 3️⃣ 设备管理
```bash
# 系统已内置测试设备，无需额外导入

# 查询设备
python scripts/query_devices.py
```

## 📊 脚本工具分类

### ✅ 保留的核心脚本（已验证）
| 分类 | 脚本文件 | 用途 |
|------|----------|------|
| **系统管理** | auto_setup.py | 自动配置设置 |
| | start_stable.bat | 一键启动服务 |
| | quick_check.py | 系统健康检查 |
| **设备管理** | query_devices.py | 查询设备信息 |
| | import_devices.py | CSV导入设备 |
| | device_status_checker.py | 设备状态监控 |
| **故障修复** | fix_port_mapping.py | 修复端口映射 |
| | fix_nvr_config.py | 修复NVR配置 |
| | exception_handler.py | 异常处理 |

### 🗑️ 已移除的冗余文件
- **check_devices.py** - 功能重复，被device_status_checker.py替代
- **start_clean.py** - 过时启动脚本
- **dev_tools.py** - PostgreSQL/Redis环境不匹配
- **测试文件** - 已移至backup目录归档

## 🎯 当前架构特点

### ✅ 优势
- **轻量级**: SQLite单文件数据库，无需复杂配置
- **跨平台**: 支持Windows/Linux/macOS
- **实时性**: WebRTC低延迟视频流
- **HEVC兼容**: 专用转换服务确保H.265视频正常播放
- **音频支持**: 完整的音视频同步传输
- **正确通道显示**: 修复的通道选择逻辑，确保不同通道显示正确画面
- **易维护**: 脚本工具齐全，一键诊断

### 📈 系统指标
- **启动时间**: < 30秒
- **设备支持**: 内置测试设备，无需额外配置
- **并发能力**: 支持多路视频同时监控
- **存储需求**: 最小100MB存储空间
- **HEVC处理**: 专用转换服务处理H.265编码视频

## 🔍 故障排查工具

### 📊 诊断命令
```bash
# 系统状态检查
python scripts/quick_check.py

# 数据库检查
python scripts/check_db.py

# 设备连接测试
python scripts/device_status_checker.py

# 异常处理
python scripts/exception_handler.py

# HEVC服务检查
python scripts/webrtc/hevc_compat_server.py --status
```

### 🚨 常见问题
1. **端口占用**: 使用fix_port_mapping.py修复
2. **设备离线**: 使用device_status_checker.py检查
3. **配置错误**: 使用fix_nvr_config.py修复
4. **数据库问题**: 使用db_manager.py管理
5. **HEVC黑屏**: 确保hevc_compat_server.py正在运行（端口8090），参考HEVC_FIX_GUIDE.md

## 📞 技术支持

### 📋 文档维护
- 所有文档与当前架构保持同步
- 定期更新清理报告
- 提供完整的技术栈说明

### 🔧 获取帮助
1. 查看[清理报告](scripts/CLEANUP_REPORT.md)了解架构
2. 使用`quick_check.py`进行系统诊断
3. 参考[项目结构](PROJECT_STRUCTURE.md)文档

---

*文档版本: v2.1 - HEVC兼容优化版*
*最后更新: 2025年9月*
*架构: SQLite + FastAPI + Vue 3 + WebRTC + HEVC兼容服务*