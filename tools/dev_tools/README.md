# 🔧 开发工具包 (Dev Tools)

这个目录包含开发过程中使用的工具和脚本，整合了原来根目录下的dev_tools内容。

## 🚀 启动脚本
- `start_all_services.bat` - 一键启动所有服务

## 🔍 检查工具
- `check_ports.bat` - 检查端口占用情况
- `check_frontend.js` - 检查前端状态
- `check_rtsp_config.py` - 检查RTSP配置
- `show_devices.py` - 显示设备信息

## 🧹 维护工具
- `cleanup_project.py` - 清理项目临时文件
- `init_db.py` - 初始化数据库

## 🧪 测试工具
- `test_login.py` - 测试登录功能
- `test_real_devices.py` - 测试真实设备

## 📁 目录结构
```
tools/dev_tools/
├── README.md              # 本说明文档
├── __init__.py           # Python模块初始化
├── start_all_services.bat # 一键启动所有服务
├── check_ports.bat       # 端口检查脚本
├── check_frontend.js     # 前端状态检查
├── check_rtsp_config.py  # RTSP配置检查
├── cleanup_project.py    # 项目清理工具
├── init_db.py           # 数据库初始化
├── show_devices.py      # 设备信息显示
├── test_login.py        # 登录测试
└── test_real_devices.py # 真实设备测试
```

## 🔧 使用方法

### 一键启动所有服务
```bash
# 在tools目录下执行
.\dev_tools\start_all_services.bat
```

### 检查端口状态
```bash
.\dev_tools\check_ports.bat
```

### 检查设备状态
```bash
python dev_tools\show_devices.py
```