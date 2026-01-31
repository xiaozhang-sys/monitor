# 天眼系统

这是一个视音频流监控系统，支持RTSP、HTTP等多种协议的设备接入和实时监控。

## 安全配置说明

本项目包含一些默认的测试凭据，用于开发和测试目的。在生产环境中部署前，请务必按以下步骤清除敏感信息：

### 需要修改的敏感信息

1. **后端配置文件** (`config/apps/backend.json`)
   - `database.mysql.password`: MySQL数据库密码
   - `database.postgresql.password`: PostgreSQL数据库密码
   - `auth.jwt_secret`: JWT密钥

2. **前端配置文件** (`config/apps/frontend.json`)
   - `defaults.username`: 默认用户名
   - `defaults.password`: 默认密码

3. **后端代码** (`backend/main.py`)
   - 默认管理员用户的密码哈希值

4. **前端代码** (`frontend/src/views/Login.vue`)
   - 登录页面的默认凭据（如有）

### 清除敏感信息的步骤

1. 修改 `config/apps/backend.json` 中的数据库密码和JWT密钥
2. 修改 `config/apps/frontend.json` 中的默认凭据
3. 更新后端代码中的默认管理员密码
4. 检查并清除其他可能包含敏感信息的配置文件

### 环境变量配置

推荐使用环境变量管理敏感信息：

```bash
# 创建 .env 文件
cp .env.example .env

# 编辑 .env 文件，填入真实值
JWT_SECRET=your_very_secure_jwt_secret
DB_USER=your_db_username
DB_PASSWORD=your_secure_db_password
```

### 运行项目

```bash
# 启动后端服务
cd backend
python main.py

# 启动前端服务
cd frontend
npm run dev
```

## 注意事项

- 在将代码推送到公共仓库前，请务必检查并清除所有敏感信息
- 生产环境中不要使用默认的用户名和密码
- 定期更换密码和JWT密钥
- 使用强密码策略