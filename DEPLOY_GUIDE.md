# 零售天眼通 - 快速部署指南

## 环境准备

### 系统要求
- **操作系统**: Windows 7+, Linux (Ubuntu 18.04+/CentOS 7+), macOS 10.14+
- **内存**: 最低 2GB RAM，推荐 4GB+
- **磁盘**: 至少 500MB 可用空间
- **网络**: 稳定的互联网连接

### 软件依赖
```bash
# Python 3.8+ (推荐 3.9-3.11)
python --version

# Node.js 16+ (推荐 18+)
node --version

# npm (随Node.js一起安装)
npm --version
```

## 快速部署

### 1. 克隆项目
```bash
git clone <repository-url>
cd Monitor
```

### 2. 后端部署
```bash
# 进入后端目录
cd backend

# 安装Python依赖
pip install -r requirements.txt

# 返回项目根目录
cd ..
```

### 3. 前端部署
```bash
# 进入前端目录
cd frontend

# 安装Node.js依赖
npm install

# 返回项目根目录
cd ..
```

### 4. 数据库初始化
```bash
# 确保data目录存在
mkdir -p data
mkdir -p logs

# 系统会在首次启动时自动创建数据库
```

## 服务启动

### Windows启动
```bash
# 方法1: 使用批处理脚本 (推荐)
scripts\start_stable.bat

# 方法2: 手动启动
# 终端1: 启动后端
cd backend
python main.py

# 终端2: 启动前端
cd frontend
npm run dev
```

### Linux/macOS启动
```bash
# 启动后端 (在后台运行)
cd backend && nohup python main.py > ../logs/backend.log 2>&1 &

# 启动前端 (在后台运行)
cd frontend && nohup npm run dev > ../logs/frontend.log 2>&1 &
```

## 服务配置

### 端口配置
- **后端API**: 8004
- **前端服务**: 5174
- **WebRTC服务**: 8090

### 配置文件
- **后端配置**: `config/apps/backend.json`
- **前端配置**: `config/apps/frontend.json`

## 访问系统

### Web界面
打开浏览器访问: [http://localhost:5174](http://localhost:5174)

### 登录凭据
- **用户名**: admin
- **密码**: admin123

### API文档
- **文档地址**: [http://localhost:8004/docs](http://localhost:8004/docs)

## Docker部署 (可选)

### 构建Docker镜像
```bash
# 构建后端镜像
docker build -f docker/Dockerfile.backend -t retail-eye-backend .

# 构建前端镜像
docker build -f docker/Dockerfile.frontend -t retail-eye-frontend .
```

### 运行容器
```bash
# 启动后端容器
docker run -d --name backend -p 8004:8004 retail-eye-backend

# 启动前端容器
docker run -d --name frontend -p 5174:5174 --link backend retail-eye-frontend
```

## 环境变量配置

### 后端环境变量
```bash
# 设置环境变量
export DEBUG=true
export DATABASE_URL=sqlite:///./data/devices.db
export JWT_SECRET=your-super-secret-jwt-key
```

### 前端环境变量
在 `frontend/.env` 文件中配置:
```bash
VITE_API_BASE_URL=http://localhost:8004
VITE_WEBSOCKET_URL=ws://localhost:8080
VITE_WEBRTC_PORT=8090
```

## 系统维护

### 日志管理
```bash
# 查看后端日志
tail -f logs/backend.log

# 查看前端日志
# 前端日志主要在浏览器控制台查看
```

### 数据备份
```bash
# 备份数据库
cp data/devices.db data/devices.db.backup.$(date +%Y%m%d_%H%M%S)
```

### 服务重启
```bash
# 停止服务 (Windows)
# 关闭运行服务的终端窗口

# 停止服务 (Linux/macOS)
pkill -f "python main.py"
pkill -f "npm run dev"
```

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   netstat -an | grep :8004  # Windows
   lsof -i :8004            # Linux/macOS
   
   # 更改端口配置
   # 修改 config/apps/backend.json 和 config/apps/frontend.json
   ```

2. **数据库连接失败**
   - 检查 `data/devices.db` 文件权限
   - 确认SQLite驱动已安装

3. **前端无法连接后端**
   - 检查代理配置
   - 确认后端服务正在运行

4. **视频流无法播放**
   - 检查WebRTC服务状态
   - 确认摄像头RTSP地址正确

### 性能优化
- 定期清理日志文件
- 监控内存使用情况
- 优化数据库查询

## 安全设置

### 生产环境安全建议
1. 更改默认登录凭据
2. 使用HTTPS加密传输
3. 配置防火墙规则
4. 定期更新依赖包
5. 备份重要数据

### 访问控制
- 限制API访问频率
- 实施IP白名单
- 使用强密码策略

## 升级指南

### 从旧版本升级
1. 备份现有数据 (`data/devices.db`)
2. 拉取最新代码
3. 更新依赖包
4. 检查配置文件兼容性
5. 重启服务

### 验证升级
- 检查服务是否正常启动
- 验证登录功能
- 测试设备管理功能
- 确认视频流正常

## 技术支持

### 社区支持
- GitHub Issues
- 官方文档
- 示例代码

### 联系方式
- 邮箱: support@example.com
- 论坛: https://community.example.com

---

**部署指南版本**: 1.0  
**最后更新**: 2025年1月31日