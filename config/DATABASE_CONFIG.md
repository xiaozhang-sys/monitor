# 数据库连接配置指南

## 支持的数据库类型

本系统支持三种数据库类型，可根据环境需求灵活选择：

- **SQLite** (默认): 单文件数据库，适合开发和小型部署
- **MySQL**: 关系型数据库，适合生产环境
- **PostgreSQL**: 高级关系型数据库，适合企业级应用

## 配置方法

### 1. SQLite 配置 (默认)

**环境变量配置:**
```bash
# 在 .env 文件中设置
DB_TYPE=sqlite
DB_PATH=./data/devices.db
DB_BACKUP_PATH=./data/backups/
DB_CONNECTION_TIMEOUT=30
DB_POOL_SIZE=20
```

**配置文件 (config/apps/backend.json):**
```json
{
  "database": {
    "type": "sqlite",
    "sqlite": {
      "path": "./data/devices.db",
      "check_same_thread": false,
      "timeout": 10.0
    }
  }
}
```

### 2. MySQL 配置

**环境变量配置:**
```bash
# 在 .env 文件中设置
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=monitor_user
DB_PASSWORD=your_secure_password
DB_NAME=monitor_db
DB_CHARSET=utf8mb4
```

**配置文件:**
```json
{
  "database": {
    "type": "mysql",
    "mysql": {
      "host": "localhost",
      "port": 3306,
      "user": "monitor_user",
      "password": "your_secure_password",
      "database": "monitor_db",
      "charset": "utf8mb4"
    }
  }
}
```

**安装依赖:**
```bash
pip install mysql-connector-python
# 或
pip install pymysql
```

### 3. PostgreSQL 配置

**环境变量配置:**
```bash
# 在 .env 文件中设置
DB_TYPE=postgresql
PG_HOST=localhost
PG_PORT=5432
PG_USER=monitor_user
PG_PASSWORD=your_secure_password
PG_NAME=monitor_db
```

**配置文件:**
```json
{
  "database": {
    "type": "postgresql",
    "postgresql": {
      "host": "localhost",
      "port": 5432,
      "user": "monitor_user",
      "password": "your_secure_password",
      "database": "monitor_db"
    }
  }
}
```

**安装依赖:**
```bash
pip install psycopg2-binary
```

## 环境切换配置

### 开发环境 (development.env)
```bash
# 使用 SQLite (默认)
DB_TYPE=sqlite
DB_PATH=./data/devices.db

# 或使用 MySQL
DB_TYPE=mysql
DB_HOST=localhost
DB_USER=monitor_user
DB_PASSWORD=dev_password
DB_NAME=monitor_dev
```

### 测试环境 (test.env)
```bash
# 使用独立测试数据库
DB_TYPE=sqlite
DB_PATH=./data/test_devices.db

# 或使用 MySQL 测试库
DB_TYPE=mysql
DB_HOST=localhost
DB_USER=test_user
DB_PASSWORD=test_password
DB_NAME=test_monitor_db
```

### 生产环境 (production.env)
```bash
# 使用 MySQL (推荐)
DB_TYPE=mysql
DB_HOST=mysql
DB_USER=monitor_user
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=monitor_db

# 或使用 PostgreSQL
DB_TYPE=postgresql
DB_HOST=postgres
DB_USER=monitor_user
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=monitor_db
```

## 数据库初始化

### 自动初始化
```bash
# 使用数据库管理工具
python scripts/db_manager.py --init

# 测试连接
python scripts/db_manager.py --test

# 显示配置
python scripts/db_manager.py --show
```

### 手动初始化

**SQLite:**
```bash
# 创建数据库目录
mkdir -p data

# 初始化数据库
sqlite3 data/devices.db < scripts/init.sql
```

**MySQL:**
```sql
-- 创建数据库
CREATE DATABASE monitor_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户并授权
CREATE USER 'monitor_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON monitor_db.* TO 'monitor_user'@'localhost';
FLUSH PRIVILEGES;
```

**PostgreSQL:**
```sql
-- 创建数据库
CREATE DATABASE monitor_db;

-- 创建用户并授权
CREATE USER monitor_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE monitor_db TO monitor_user;
```

## 数据库连接字符串

根据当前配置自动生成连接字符串：

- **SQLite**: `sqlite:///./data/devices.db`
- **MySQL**: `mysql+pymysql://user:password@host:port/database?charset=utf8mb4`
- **PostgreSQL**: `postgresql://user:password@host:port/database`

## 备份配置

### 自动备份
```json
{
  "database": {
    "backup_path": "./data/backups/",
    "auto_backup": true,
    "backup_retention_days": 7,
    "backup_interval": 3600
  }
}
```

### 手动备份
```bash
# SQLite 备份
cp data/devices.db data/backups/devices_$(date +%Y%m%d_%H%M%S).db

# MySQL 备份
mysqldump -u monitor_user -p monitor_db > backups/monitor_$(date +%Y%m%d_%H%M%S).sql

# PostgreSQL 备份
pg_dump -U monitor_user -d monitor_db > backups/monitor_$(date +%Y%m%d_%H%M%S).sql
```

## 性能优化

### 连接池配置
```json
{
  "database": {
    "connection_pool_size": 20,
    "connection_timeout": 30,
    "pool_recycle": 3600
  }
}
```

### 索引优化
```sql
-- 设备表索引
CREATE INDEX idx_devices_ip ON devices(ip);
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_region_store ON devices(region, store);

-- 用户表索引
CREATE INDEX idx_users_username ON users(username);
```

## 故障排查

### 常见问题

**连接失败:**
```bash
# 检查数据库服务状态
python scripts/db_manager.py --test

# 检查端口占用
netstat -an | grep 3306  # MySQL
netstat -an | grep 5432  # PostgreSQL
```

**权限问题:**
```bash
# MySQL 权限检查
mysql -u monitor_user -p -e "SHOW GRANTS;"

# PostgreSQL 权限检查
psql -U monitor_user -d monitor_db -c "\du"
```

**字符编码问题:**
```bash
# MySQL 字符集检查
mysql -u monitor_user -p -e "SHOW VARIABLES LIKE 'character_set%';"

# PostgreSQL 编码检查
psql -U monitor_user -d monitor_db -c "SHOW SERVER_ENCODING;"
```

## Docker 配置

### docker-compose.yml 数据库服务

**MySQL 服务:**
```yaml
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: monitor_db
      MYSQL_USER: monitor_user
      MYSQL_PASSWORD: monitor_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
```

**PostgreSQL 服务:**
```yaml
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: monitor_db
      POSTGRES_USER: monitor_user
      POSTGRES_PASSWORD: monitor_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## 监控和日志

### 数据库监控
```bash
# 查看数据库大小
python scripts/db_manager.py --stats

# 查看连接数
python scripts/db_manager.py --connections

# 查看慢查询日志
python scripts/db_manager.py --slow-queries
```