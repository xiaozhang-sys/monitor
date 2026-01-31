# 配置指南 - 简洁明了

## 快速开始

### 1. 环境配置 (30秒)
```bash
# 复制环境模板
copy config\environment_template.env .env

# 编辑.env文件（只需修改关键配置）
notepad .env
```

### 2. 启动服务 (选择一种)

**开发模式：**
```bash
python streaming\start_webrtc.py
```

**Docker模式：**
```bash
docker-compose up -d
```

**一键启动：**
```bash
scripts\start_stable.bat
```

## 关键配置速查

| 服务 | 配置文件 | 默认端口 | 修改位置 |
|---|---|---|---|
| WebRTC | `config/app_config.json` | 8080 | `server.webrtc.port` |
| 后端API | `config/app_config.json` | 8000 | `server.backend.port` |
| 前端页面 | `config/app_config.json` | 3000 | `server.frontend.port` |
| 数据库 | `config/app_config.json` | - | `database.sqlite.path` |

## 常用配置修改

### 修改端口
编辑 `config/app_config.json`：
```json
{
  "server": {
    "backend": {"port": 新端口},
    "frontend": {"port": 新端口},
    "webrtc": {"port": 新端口}
  }
}
```

### 添加设备
编辑 `config/device_config.json`：
```json
{
  "devices": [
    {
      "id": "camera_01",
      "name": "前门摄像头",
      "rtsp_url": "rtsp://user:pass@ip:port/stream",
      "type": "brand_a"
    }
  ]
}
```

### 环境变量
复制 `.env` 并修改：
```bash
# 重要：修改JWT密钥
JWT_SECRET_KEY=your-secret-key-here

# 数据库路径
DATABASE_URL=sqlite:///./data/devices.db

# 日志级别
LOG_LEVEL=INFO
```

## 故障排查

**端口冲突：**
- 检查 `config/app_config.json` 中的端口设置
- 使用 `tools/check_ports.bat` 查看端口占用

**数据库问题：**
- 检查 `data/devices.db` 是否存在
- 运行 `tools/dev_tools/init_db.py` 初始化数据库

**配置验证：**
```bash
# 检查配置文件格式
python -c "import json; json.load(open('config/app_config.json'))"

# 测试端口连通性
tools/check_ports.bat
```

## 文件说明

- **app_config.json** - 主应用配置（推荐修改）
- **environment_template.env** - 环境变量模板
- **docker_config.json** - Docker服务配置
- **device_config.json** - 设备连接信息
- **port_config.json** - 端口映射表

## 一键脚本

```bash
tools/                # 工具脚本目录
├── start_all_services.bat    # 启动所有服务
├── check_ports.bat          # 检查端口
├── test_current_device.bat  # 测试设备连接
└── repair.bat              # 自动修复
```