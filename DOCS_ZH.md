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
├── backend/                 # 后端服务
│   ├── main.py             # 主服务入口
│   ├── api/               # API路由定义
│   ├── models/            # 数据模型
│   ├── database.py        # 数据库操作
│   └── auth.py            # 认证模块
├── frontend/              # 前端服务
│   ├── src/               # 源代码
│   │   ├── components/    # Vue组件
│   │   ├── views/         # 页面视图
│   │   ├── router/        # 路由配置
│   │   └── utils/         # 工具函数
│   ├── public/            # 静态资源
│   ├── package.json       # 前端依赖
│   └── vite.config.js     # 构建配置
├── config/                # 配置文件
│   └── apps/              # 应用配置
│       ├── frontend.json  # 前端配置
│       └── backend.json   # 后端配置
├── scripts/               # 脚本文件
│   ├── start_stable.bat   # Windows启动脚本
│   └── webrtc/            # WebRTC相关脚本
└── data/                  # 数据存储
    └── devices.db         # SQLite数据库
```

## ⚙️ 配置详情

### 后端配置 (config/apps/backend.json)
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8004,
    "workers": 1,
    "reload": true,
    "log_level": "info"
  },
  "database": {
    "type": "sqlite",
    "sqlite": {
      "path": "./data/devices.db",
      "check_same_thread": false,
      "timeout": 10.0
    },
    "mysql": {
      "host": "localhost",
      "port": 3306,
      "user": "monitor_user",
      "password": "password123",
      "database": "retail_monitor"
    },
    "postgresql": {
      "host": "localhost",
      "port": 5432,
      "user": "pg_monitor_user",
      "password": "pg_password123",
      "database": "retail_monitor_pg"
    }
  },
  "auth": {
    "jwt_secret": "your-secret-key-here",
    "jwt_algorithm": "HS256",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 7
  }
}
```

### 前端配置 (config/apps/frontend.json)
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5174,
    "https": false
  },
  "proxy": {
    "api": {
      "target": "http://localhost:8004",
      "path_rewrite": "^/api"
    },
    "webrtc": {
      "target": "http://localhost:8090",
      "path_rewrite": "^/webrtc"
    }
  },
  "defaults": {
    "username": "admin",
    "password": "admin123"
  }
}
```

## 🎥 WebRTC 视频流服务

### 服务配置
- **端口**: 8090
- **协议**: HTTP WebSocket
- **编码支持**: H.265/HEVC, H.264
- **兼容性**: 所有现代浏览器

### 启动命令
```bash
# HEVC兼容WebRTC服务器
python scripts/webrtc/hevc_compat_server.py --port 8090

# 或者标准WebRTC服务器
python scripts/webrtc/simple_webrtc_server.py --port 8090
```

## 🗄️ 数据库配置

### SQLite (默认)
- **路径**: ./data/devices.db
- **驱动**: aiomysql (异步), sqlite3 (同步)
- **连接池**: 自动管理
- **备份策略**: 自动备份

### MySQL (可选)
- **主机**: localhost:3306
- **用户**: monitor_user
- **密码**: password123
- **数据库**: retail_monitor

### PostgreSQL (可选)
- **主机**: localhost:5432
- **用户**: pg_monitor_user
- **密码**: pg_password123
- **数据库**: retail_monitor_pg

## 🔐 认证与安全

### 默认凭据
- **用户名**: admin
- **密码**: admin123
- **Token过期时间**: 30分钟
- **JWT算法**: HS256

### 安全措施
- JWT Token认证
- HTTPS支持
- CORS策略限制
- SQL注入防护
- 输入验证过滤

## 🔄 API 接口

### 认证接口
- `POST /token` - 获取访问令牌
- `GET /verify` - 验证令牌有效性

### 设备管理接口
- `GET /devices` - 获取设备列表
- `POST /devices` - 添加设备
- `PUT /devices/{id}` - 更新设备
- `DELETE /devices/{id}` - 删除设备
- `GET /devices/{id}/status` - 获取设备状态

### 监控接口
- `GET /stats` - 系统统计信息
- `POST /devices/check-all-status` - 检查所有设备状态
- `GET /health` - 健康检查

## 📊 日志与监控

### 日志配置
- **级别**: INFO
- **格式**: 时间戳 - 模块 - 级别 - 消息
- **路径**: ./logs/backend.log

### 监控指标
- 设备在线状态
- 视频流质量
- 系统性能指标
- 错误统计

## 🛠️ 故障排除

### 常见问题
1. **无法连接数据库**
   - 检查 `./data/devices.db` 权限
   - 确认SQLite驱动安装

2. **前端无法连接后端**
   - 检查代理配置
   - 确认端口8004可用

3. **视频流无法播放**
   - 检查WebRTC服务状态
   - 确认摄像头RTSP地址正确

### 调试模式
```bash
# 启用调试模式
DEBUG=true python backend/main.py
```

## 📄 许可证

Apache License 2.0

## 🤝 贡献

欢迎提交Issue和Pull Request。

---

**版本**: 2.0.0  
**最后更新**: 2025年1月31日