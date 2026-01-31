# 统一配置管理

本项目采用统一配置管理架构，所有配置文件集中在 `config/` 目录下。

## 📁 目录结构

```
config/
├── apps/                    # 应用配置
│   ├── backend.json        # 后端配置（开发环境）
│   ├── backend.prod.json   # 后端配置（生产环境）
│   ├── backend.test.json   # 后端配置（测试环境）
│   └── frontend.json       # 前端配置
├── environments/           # 环境配置
│   ├── development.env     # 开发环境
│   ├── production.env      # 生产环境
│   └── test.env           # 测试环境
├── servers/               # 服务器配置
│   ├── nginx/
│   │   ├── nginx.conf     # 开发环境nginx配置
│   │   └── nginx.prod.conf # 生产环境nginx配置
│   └── srs/
│       ├── srs.conf       # SRS配置
│       └── srs.test.conf  # 测试环境SRS配置
├── config_loader.py       # 配置加载器
├── validate_config.py     # 配置验证工具
├── migrate_configs.py     # 配置迁移脚本
├── switch_environment.py  # 环境切换工具
└── .current_env          # 当前环境标记

# 旧配置（已迁移）
├── app_config.json        # 主应用配置（已迁移到apps/）
├── docker_config.json     # Docker服务配置
├── environment_template.env # 环境变量模板
├── device_config.json     # 设备配置
├── port_config.json       # 端口配置
└── backups/              # 配置备份
```

## 🚀 快速开始

### 1. 查看当前环境
```bash
python scripts/switch_environment.py --current
```

### 2. 切换环境
```bash
# 切换到开发环境
python scripts/switch_environment.py development

# 切换到测试环境
python scripts/switch_environment.py test

# 切换到生产环境
python scripts/switch_environment.py production
```

### 3. 验证配置
```bash
# 验证当前环境配置
python config/validate_config.py

# 验证特定环境
python scripts/switch_environment.py --validate production
```

### 4. 迁移旧配置
```bash
python scripts/migrate_configs.py
```

## 🌍 环境配置对比

| 环境 | 后端端口 | 前端端口 | WebRTC端口 | 数据库类型 | 特点 |
|------|----------|----------|------------|------------|------|
| development | 8002 | 5173 | 8080 | SQLite | 调试模式，热重载 |
| test | 8003 | 5174 | 8081 | SQLite (测试库) | 测试专用，模拟数据 |
| production | 8000 | 80 | 8080 | MySQL/PostgreSQL | 生产优化，安全设置 |

## 数据库配置

### 支持的数据库类型
- **SQLite**: 单文件数据库，适合开发环境
- **MySQL**: 关系型数据库，适合生产环境
- **PostgreSQL**: 高级关系型数据库，适合企业级应用

### 数据库配置方法

#### 1. 快速配置
```bash
# 查看当前数据库配置
python scripts/db_manager.py --show

# 测试数据库连接
python scripts/db_manager.py --test

# 初始化数据库
python scripts/db_manager.py --init
```

#### 2. 环境变量配置
```bash
# SQLite (默认)
DB_TYPE=sqlite
DB_PATH=./data/devices.db

# MySQL
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=monitor_user
DB_PASSWORD=your_password
DB_NAME=monitor_db

# PostgreSQL
DB_TYPE=postgresql
PG_HOST=localhost
PG_PORT=5432
PG_USER=monitor_user
PG_PASSWORD=your_password
PG_NAME=monitor_db
```

#### 3. 配置文件设置
详见 [DATABASE_CONFIG.md](DATABASE_CONFIG.md) 获取完整数据库配置指南。

### 数据库连接字符串
- **SQLite**: `sqlite:///./data/devices.db`
- **MySQL**: `mysql+pymysql://user:password@host:port/database?charset=utf8mb4`
- **PostgreSQL**: `postgresql://user:password@host:port/database`

### 数据库管理工具
```bash
# 数据库状态检查
python scripts/db_manager.py --stats

# 连接测试
python scripts/db_manager.py --connections

# 备份数据库
python scripts/db_manager.py --backup
```

## 🔧 配置文件说明

### 后端配置 (apps/backend*.json)
- **server**: 服务器设置（host, port, workers）
- **database**: 数据库配置（path, backup）
- **auth**: 认证配置（JWT设置）
- **cors**: 跨域配置
- **monitoring**: 监控设置
- **security**: 安全配置（仅生产环境）
- **testing**: 测试专用配置（仅测试环境）

### 前端配置 (apps/frontend.json)
- **server**: 开发服务器设置
- **proxy**: API代理规则
- **build**: 构建设置
- **features**: 功能开关
- **ui**: UI配置

### 环境变量 (environments/*.env)
- 包含所有环境特定的变量
- 自动加载到对应环境
- 支持敏感信息配置

## 📝 最佳实践

1. **环境隔离**: 每个环境使用独立的配置文件
2. **敏感信息**: 使用环境变量存储敏感信息
3. **版本控制**: 避免提交生产环境的敏感配置
4. **备份**: 修改配置前创建备份
5. **验证**: 使用验证工具确保配置正确

## 🔄 迁移指南

### 从旧配置迁移
1. 运行迁移脚本：`python scripts/migrate_configs.py`
2. 检查生成的迁移报告
3. 验证新配置是否正常工作
4. 确认无误后删除旧配置文件

### 添加新环境
1. 创建新的环境文件：`config/environments/{env}.env`
2. 创建对应的应用配置：`config/apps/backend.{env}.json`
3. 更新环境切换脚本
4. 验证新环境配置

## 🚨 注意事项

- 生产环境的 `JWT_SECRET` 必须设置为强随机字符串
- 修改配置文件后需要重启相关服务
- 使用版本控制跟踪配置变更
- 定期备份生产环境配置

## 📊 配置优先级

1. 环境变量 (最高优先级)
2. 配置文件
3. 默认值 (最低优先级)

## 🔍 故障排除

### 配置加载失败
1. 检查文件路径是否正确
2. 验证JSON格式
3. 确认环境变量已设置

### 端口冲突
1. 检查端口占用情况
2. 修改对应环境的端口配置
3. 重启服务