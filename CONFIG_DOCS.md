# 配置文件说明文档

## 概述
本文档详细说明零售天眼通系统的各项配置文件及其用途。

## 配置文件位置

### 主配置目录
```
config/
└── apps/
    ├── frontend.json    # 前端应用配置
    └── backend.json     # 后端应用配置
```

## 后端配置详解 (config/apps/backend.json)

### 服务器配置
```json
{
  "server": {
    "host": "0.0.0.0",           // 监听地址，0.0.0.0表示所有接口
    "port": 8004,                // 服务端口
    "workers": 1,                // 工作进程数
    "reload": true,              // 开发模式下自动重载
    "log_level": "info"          // 日志级别
  }
}
```

### 数据库配置
```json
{
  "database": {
    "type": "sqlite",            // 数据库类型：sqlite/mysql/postgresql
    
    // SQLite 配置
    "sqlite": {
      "path": "./data/devices.db",      // 数据库文件路径
      "check_same_thread": false,       // 多线程访问设置
      "timeout": 10.0                   // 连接超时时间(秒)
    },
    
    // MySQL 配置
    "mysql": {
      "host": "localhost",              // MySQL主机地址
      "port": 3306,                     // MySQL端口
      "user": "monitor_user",           // 用户名
      "password": "password123",        // 密码
      "database": "retail_monitor"      // 数据库名
    },
    
    // PostgreSQL 配置
    "postgresql": {
      "host": "localhost",              // PostgreSQL主机地址
      "port": 5432,                     // PostgreSQL端口
      "user": "pg_monitor_user",        // 用户名
      "password": "pg_password123",     // 密码
      "database": "retail_monitor_pg"   // 数据库名
    }
  }
}
```

### 认证配置
```json
{
  "auth": {
    "jwt_secret": "your-secret-key-here",    // JWT密钥
    "jwt_algorithm": "HS256",               // 加密算法
    "access_token_expire_minutes": 30,      // 访问令牌过期时间(分钟)
    "refresh_token_expire_days": 7          // 刷新令牌过期时间(天)
  }
}
```

### 日志配置
```json
{
  "logging": {
    "level": "INFO",                                    // 日志级别
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",  // 日志格式
    "file": "./logs/backend.log"                       // 日志文件路径
  }
}
```

## 前端配置详解 (config/apps/frontend.json)

### 服务器配置
```json
{
  "server": {
    "host": "0.0.0.0",      // 监听地址
    "port": 5174,           // 服务端口
    "https": false          // 是否启用HTTPS
  }
}
```

### 代理配置
```json
{
  "proxy": {
    "api": {
      "target": "http://localhost:8004",    // API代理目标
      "path_rewrite": "^/api"               // 路径重写规则
    },
    "webrtc": {
      "target": "http://localhost:8090",    // WebRTC代理目标
      "path_rewrite": "^/webrtc"            // 路径重写规则
    }
  }
}
```

### 构建配置
```json
{
  "build": {
    "output_dir": "dist",          // 输出目录
    "assets_dir": "assets",        // 静态资源目录
    "sourcemap": false,            // 是否生成源码映射
    "minify": "terser",            // 压缩工具
    "css_minify": true             // 是否压缩CSS
  }
}
```

### 开发配置
```json
{
  "dev": {
    "cors": {
      "allowed_origins": ["*"],                              // 允许的源
      "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  // 允许的方法
      "allowed_headers": ["Content-Type", "Authorization"]   // 允许的头部
    }
  }
}
```

### 默认配置
```json
{
  "defaults": {
    "username": "admin",        // 默认用户名
    "password": "admin123"      // 默认密码
  }
}
```

## 环境变量配置

### 前端环境变量 (frontend/.env)
```bash
# 端口配置
VITE_PORT=5174
VITE_HOST=localhost

# API配置
VITE_API_BASE_URL=http://localhost:8004
VITE_API_PREFIX=/api

# WebRTC配置
VITE_WEBRTC_PORT=8090
VITE_WEBRTC_BASE_URL=http://localhost:8090

# 开发模式
VITE_DEBUG_MODE=true
```

## 数据库迁移说明

### SQLite数据库
- **位置**: `./data/devices.db`
- **备份**: 系统会自动创建备份文件
- **权限**: 确保对data目录有读写权限

### MySQL迁移
如果要从SQLite迁移到MySQL，请执行以下步骤：
1. 修改backend.json中的数据库配置
2. 运行数据库迁移脚本
3. 重启后端服务

### PostgreSQL迁移
如果要从SQLite迁移到PostgreSQL，请执行以下步骤：
1. 修改backend.json中的数据库配置
2. 创建PostgreSQL数据库和用户
3. 运行数据库迁移脚本
4. 重启后端服务

## 安全配置

### JWT密钥管理
- 生产环境中应使用强随机密钥
- 定期更换密钥
- 不要在代码中硬编码密钥

### CORS策略
- 在生产环境中限制允许的域名
- 避免使用"*"通配符
- 仅允许必要的HTTP方法

## 故障排除

### 常见配置问题
1. **端口冲突**: 检查端口是否被其他服务占用
2. **数据库连接失败**: 检查数据库服务是否运行
3. **代理配置错误**: 检查目标URL是否正确
4. **权限问题**: 检查文件和目录权限

### 日志查看
- 后端日志: `./logs/backend.log`
- 前端控制台: 浏览器开发者工具
- 系统日志: 根据操作系统查看相应日志

## 版本兼容性

### 配置文件版本
- 配置文件格式向后兼容
- 新版本会自动升级旧配置
- 建议备份配置文件后再升级

### API兼容性
- API版本: v1
- 向后兼容: 是
- 弃用策略: 提前通知

---
**文档版本**: 1.0  
**最后更新**: 2025年1月31日