# 根目录文件整理总结

## 🎯 整理概述

本次整理将根目录下的调试和测试文件按功能分类移动到合适的目录，保持根目录简洁，只保留核心项目文件。

## 📋 文件移动详情

### ✅ 已移动的文件

| 原位置 | 新位置 | 文件类型 | 用途 |
|--------|--------|----------|------|
| `check_rtsp_codec.py` | `tools/debug/check_rtsp_codec.py` | 调试工具 | RTSP编解码检查 |
| `debug_webrtc_video.py` | `tools/debug/debug_webrtc_video.py` | 调试工具 | WebRTC视频调试 |
| `webrtc_diagnosis.py` | `tools/debug/webrtc_diagnosis.py` | 诊断工具 | WebRTC诊断 |
| `webrtc_diagnosis.json` | `data/diagnosis/webrtc_diagnosis.json` | 数据文件 | 诊断数据 |
| `webrtc_diagnosis_report.json` | `data/diagnosis/webrtc_diagnosis_report.json` | 报告文件 | 诊断报告 |
| `webrtc_test_page.html` | `tests/webrtc_test_page.html` | 测试页面 | WebRTC测试页面 |

### 📁 保留的核心文件

| 文件名 | 类型 | 重要性 | 说明 |
|--------|------|--------|------|
| `README.md` | 📄 文档 | 核心 | 项目主文档 |
| `.env` | ⚙️ 配置 | 核心 | 环境变量配置 |
| `docker-compose.yml` | 🐳 部署 | 核心 | Docker部署配置 |
| `PORT_SYNC_REPORT.md` | 📊 报告 | 核心 | 端口统一变更记录 |
| `quick_restart.bat` | 🔄 脚本 | 核心 | 快速重启脚本 |

## 🗂️ 新的目录结构

```
d:\code\Monitor/
├── 📄 核心文件（5个）
│   ├── README.md
│   ├── .env
│   ├── docker-compose.yml
│   ├── PORT_SYNC_REPORT.md
│   └── quick_restart.bat
│
├── 📁 功能目录
│   ├── backend/           # 后端服务
│   ├── frontend/          # 前端界面
│   ├── config/           # 配置文件
│   ├── data/             # 数据文件
│   │   └── diagnosis/    # 诊断数据
│   ├── docs/             # 项目文档
│   ├── scripts/          # 脚本工具
│   ├── tests/            # 测试文件
│   └── tools/            # 辅助工具
│       └── debug/        # 调试工具
```

## 🎯 整理效果

### ✅ 优点
- **根目录简洁**：从11个文件减少到5个核心文件
- **功能清晰**：按用途分类存放，便于查找
- **维护方便**：调试工具集中管理
- **结构规范**：符合项目目录设计标准

### 📊 统计
- **根目录文件**：11 → 5（减少55%）
- **功能分类**：100%按用途存放
- **目录层级**：最大3层，保持简洁

## 🚀 使用方式

### 快速访问调试工具
```bash
# RTSP编解码检查
python tools/debug/check_rtsp_codec.py

# WebRTC视频调试
python tools/debug/debug_webrtc_video.py

# WebRTC诊断
python tools/debug/webrtc_diagnosis.py
```

### 测试页面访问
```bash
# WebRTC测试页面
http://localhost:8081/tests/webrtc_test_page.html
```

## 🔍 验证

所有移动的文件都已更新路径，相关引用已自动调整。根目录现在只包含项目运行必需的核心文件。