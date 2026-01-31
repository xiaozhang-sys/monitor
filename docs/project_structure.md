# 📋 监控系统 - 项目结构规范文档

## 🏗️ 项目架构概览

本项目是一个基于Web的多品牌摄像头监控系统，支持实时视频监控、设备管理、异常处理等功能。采用前后端分离架构，后端使用Python Flask，前端使用Vue 3，流媒体处理使用WebRTC和RTSP协议。

## 📁 目录结构规范

**核心原则：所有开发必须严格按照此目录结构放置文件，确保项目架构一致性。**

```
d:\code\Monitor/
├── 📄 .env                      # 全局环境变量配置 (核心配置，请勿随意修改)
├── 📄 README.md                 # 项目主说明文档
├── 📄 PORT_SYNC_REPORT.md       # 端口同步报告
├── 📄 quick_restart.bat         # 快速重启脚本 (核心启动工具)
├── 📁 backend/                  # 后端服务 (Python Flask)
│   ├── 📄 main.py              # 后端主入口
│   ├── 📄 config_loader.py     # 配置加载器
│   ├── 📄 requirements.txt     # Python依赖列表
│   └── 📄 Dockerfile           # 容器化配置
├── 📁 frontend/                 # 前端界面 (Vue 3 + Vite)
│   ├── 📄 .env                 # 前端环境变量
│   ├── 📄 package.json         # NPM依赖配置
│   ├── 📁 src/                 # 前端源码
│   └── 📁 public/              # 静态资源
├── 📁 scripts/                  # 脚本工具集
│   ├── 📁 auth/                # 认证相关脚本
│   ├── 📁 database/            # 数据库管理脚本
│   ├── 📁 development/         # 开发环境脚本
│   ├── 📁 device_management/   # 设备管理脚本
│   ├── 📁 setup/               # 系统设置脚本
│   ├── 📁 system/              # 系统维护脚本
│   └── 📁 webrtc/              # WebRTC相关脚本
├── 📁 config/                   # 配置文件中心
│   ├── 📄 app_config.json      # 应用配置
│   ├── 📄 device_config.json   # 设备配置
│   ├── 📄 port_config.json     # 端口配置 (固定端口，禁止修改)
│   └── 📁 environments/        # 多环境配置
├── 📁 data/                     # 数据存储目录
│   ├── 📄 devices.db           # 设备数据库
│   └── 📁 http_device_paths/   # HTTP设备路径数据
├── 📁 docs/                     # 项目文档
│   ├── 📄 DOCUMENTATION_INDEX.md # 文档索引
│   ├── 📄 PROJECT_SUMMARY.md   # 项目说明
│   └── 📄 project_structure.md # 本目录结构文档
├── 📁 tests/                    # 测试文件
│   ├── 📁 rtsp/                # RTSP测试
│   └── 📁 webrtc/              # WebRTC测试
└── 📁 tools/                    # 辅助工具集
    ├── 📁 debug/               # 调试工具
    └── 📁 dev_tools/           # 开发工具
```

## 📝 目录详细说明

### 🌐 根目录 (d:\code\Monitor/)
- **.env**: 全局环境变量配置文件，包含数据库连接、API密钥等核心配置，所有开发人员必须严格遵守配置规范。
- **README.md**: 项目主说明文档，提供项目概述、快速开始指南和关键功能介绍。
- **PORT_SYNC_REPORT.md**: 端口同步报告，记录所有服务端口的分配和使用情况。
- **quick_restart.bat**: 快速重启脚本，用于一键重启所有服务。

### ⚙️ 后端服务 (backend/)
- **main.py**: 后端主入口文件，包含API路由和业务逻辑。
- **config_loader.py**: 配置加载器，负责从.env和config目录加载配置。
- **requirements.txt**: Python依赖列表，用于安装项目所需的Python包。
- **Dockerfile**: 容器化配置文件，用于构建Docker镜像。

### 🎨 前端界面 (frontend/)
- **.env**: 前端环境变量文件，定义前端开发和运行时配置。
- **package.json**: NPM依赖配置文件，包含前端项目的依赖和脚本。
- **src/**: 前端源码目录，包含Vue组件、路由和状态管理。
- **public/**: 静态资源目录，存放HTML模板、图标等不经过编译的资源。

### 🛠️ 脚本工具集 (scripts/)
- **auth/**: 认证相关脚本，处理用户登录、权限验证等功能。
- **database/**: 数据库管理脚本，提供数据库备份、恢复和迁移功能。
- **development/**: 开发环境脚本，包含启动、停止和测试开发环境的工具。
- **device_management/**: 设备管理脚本，用于添加、删除和配置监控设备。
- **setup/**: 系统设置脚本，处理初始安装和配置任务。
- **system/**: 系统维护脚本，提供日志清理、资源监控等功能。
- **webrtc/**: WebRTC相关脚本，用于处理实时视频流传输。

### 📋 配置文件中心 (config/)
- **app_config.json**: 应用配置文件，定义应用的核心参数和行为。
- **device_config.json**: 设备配置文件，存储监控设备的参数和设置。
- **port_config.json**: 端口配置文件，**严格定义所有服务的固定端口，禁止修改**。
- **environments/**: 多环境配置目录，包含开发、测试和生产环境的特定配置。

### 💾 数据存储目录 (data/)
- **devices.db**: 设备数据库文件，存储设备信息和状态数据。
- **http_device_paths/**: HTTP设备路径数据目录，存放HTTP设备的访问路径信息。

### 📚 项目文档 (docs/)
- **DOCUMENTATION_INDEX.md**: 文档索引，提供所有项目文档的导航和概述。
- **PROJECT_SUMMARY.md**: 项目说明文档，详细介绍项目的功能、架构和技术栈。
- **project_structure.md**: 项目结构规范文档，定义项目的目录结构和文件组织规则。

### 🧪 测试文件 (tests/)
- **rtsp/**: RTSP测试目录，包含RTSP协议相关的测试脚本和工具。
- **webrtc/**: WebRTC测试目录，包含WebRTC协议相关的测试脚本和工具。

### 🧰 辅助工具集 (tools/)
- **debug/**: 调试工具目录，提供开发过程中的调试和排错工具。
- **dev_tools/**: 开发工具目录，包含代码生成、格式化等开发辅助工具。

## 🔧 文件放置规范

**所有开发人员必须严格遵守以下文件放置规范：**

1. **新增Python代码**: 放入backend/目录，确保遵循Flask应用结构。
2. **新增前端代码**: 放入frontend/src/目录，遵循Vue 3组件化开发规范。
3. **新增配置项**: 根据类型放入config/下相应文件，**禁止在代码中硬编码配置**。
4. **新增工具脚本**: 放入scripts/下对应功能子目录，遵循"功能分类"原则。
5. **新增设备支持**: 设备配置放入config/device_config.json，路径信息放入data/http_device_paths/。
6. **新增文档**: 放入docs/目录，并在DOCUMENTATION_INDEX.md中更新索引。
7. **新增测试**: 放入tests/下对应协议或功能目录。

## 🚫 禁止行为

- 禁止在代码中硬编码配置项，必须使用环境变量或配置文件。
- 禁止修改已定义的端口配置，必须使用port_config.json中指定的端口。
- 禁止随意创建新的顶层目录，必须遵循现有目录结构。
- 禁止将临时文件、日志文件或构建产物提交到代码库。

## 📌 版本控制要求

- 所有配置文件（如.env、config/*.json）都应添加到.gitignore中，**禁止将敏感配置提交到代码库**。
- 只提交源代码、文档和必要的配置模板。
- 确保所有新增文件都有适当的注释和文档。

## 🔧 核心组件说明

### 1. 后端服务 (Python Flask)
- **主要功能**: 提供RESTful API接口，处理业务逻辑、数据存储和设备管理。
- **技术栈**: Python 3.9+, Flask 2.0+, SQLAlchemy ORM。
- **关键模块**:
  - **main.py**: 后端主入口，定义API路由和请求处理逻辑。
  - **config_loader.py**: 统一配置加载模块，支持多环境配置切换。
  - **device_manager.py**: 设备管理核心模块，处理设备的添加、删除和状态监控。
  - **stream_handler.py**: 流媒体处理模块，负责视频流的接收和转发。

### 2. 前端界面 (Vue 3 + Vite)
- **主要功能**: 提供用户友好的Web界面，支持设备监控、配置管理和系统状态查看。
- **技术栈**: Vue 3, Vite 4, ElementPlus, Axios。
- **关键模块**:
  - **设备管理面板**: 设备列表展示、添加和配置界面。
  - **视频监控页面**: 实时视频流播放、截图和录像功能。
  - **系统配置页面**: 系统参数设置和用户管理功能。
  - **告警中心**: 设备异常和系统告警的展示和处理。

### 3. 流媒体服务
- **主要功能**: 处理实时视频流的传输、转码和存储。
- **技术栈**: WebRTC, RTSP, FFmpeg。
- **关键组件**:
  - **WebRTC服务器**: 提供低延迟的实时视频流传输。
  - **RTSP转换器**: 将传统监控设备的RTSP流转换为Web可访问格式。
  - **流媒体存储**: 支持视频片段的录制和回放功能。

### 4. 数据管理
- **主要功能**: 存储设备信息、系统配置和操作日志。
- **技术栈**: SQLite (默认), 支持MySQL/PostgreSQL扩展。
- **关键组件**:
  - **设备数据库**: 存储设备基本信息、连接参数和状态历史。
  - **配置存储**: 以JSON格式存储系统配置和用户偏好设置。
  - **日志系统**: 记录系统操作、错误信息和设备状态变更。

### 5. 设备支持模块
- **主要功能**: 支持多种品牌和类型的监控设备接入。
- **支持协议**: RTSP, HTTP, ONVIF, WebRTC。
- **设备类型**:
  - **监控摄像头**: 支持多种品牌的网络摄像头。
  - **HTTP设备**: 支持标准HTTP协议的网络视频设备。
  - **ONVIF设备**: 支持ONVIF协议的网络监控设备。
  - **WebRTC设备**: 支持WebRTC协议的现代IP摄像头。

## 📊 项目规模与复杂度

### 代码量统计
- **后端**: 约10,000行Python代码，包含API接口、业务逻辑和数据处理。
- **前端**: 约8,000行Vue/JavaScript代码，包含UI组件和交互逻辑。
- **脚本**: 约5,000行工具脚本，涵盖设备管理、系统维护和开发辅助。
- **配置文件**: 约500行配置定义，集中管理系统参数和设备配置。

### 功能模块分布
- **设备管理**: 30% - 设备添加、配置、状态监控和异常处理。
- **实时监控**: 40% - 视频流接收、传输、播放和录制。
- **系统管理**: 20% - 配置管理、用户权限和系统维护。
- **辅助工具**: 10% - 开发测试、调试诊断和数据导入导出。

### 系统依赖关系
- **前端依赖后端**: 前端通过Axios调用后端API获取数据和控制设备。
- **后端依赖流媒体**: 后端管理流媒体服务的启动、停止和参数配置。
- **所有组件依赖配置**: 所有服务和组件都从统一的配置中心获取运行参数。

## 🚀 开发工作流规范

1. **分支管理**: 采用Git Flow工作流，主分支为master，开发分支为develop，功能分支从develop创建。
2. **代码风格**: Python遵循PEP 8规范，JavaScript遵循ESLint规范，前端组件遵循Vue 3最佳实践。
3. **提交规范**: 提交信息必须包含类型、范围和简短描述（例如：feat(backend): 添加设备批量导入功能）。
4. **测试要求**: 所有新功能必须编写单元测试，关键路径必须通过集成测试。
5. **文档更新**: 代码变更必须同步更新相关文档，确保文档与代码的一致性。

## 📋 配置管理规范

1. **配置分级**: 系统配置分为全局配置(.env)、应用配置(app_config.json)和设备配置(device_config.json)三个级别。
2. **环境隔离**: 开发、测试和生产环境使用独立的配置文件，存放在config/environments/目录下。
3. **配置优先级**: 环境变量 > 命令行参数 > 配置文件 > 默认值。
4. **敏感信息**: 所有敏感信息（如密码、API密钥）必须通过环境变量提供，禁止硬编码在配置文件中。

## 🔍 问题排查指南

1. **设备连接失败**: 检查设备网络连接、账号密码和端口配置是否正确。
2. **视频流中断**: 检查网络带宽、流媒体服务状态和设备状态。
3. **API请求错误**: 查看后端日志，确认请求参数和权限设置是否正确。
4. **系统启动失败**: 检查环境变量配置、依赖包安装和端口占用情况。
5. **数据库连接问题**: 确认数据库文件权限和连接字符串配置。

## 📌 总结

本项目采用模块化、分层架构设计，确保系统的可扩展性、可维护性和可靠性。所有开发活动必须严格遵循本规范文档中定义的目录结构、文件放置规则和开发工作流，以保持项目的一致性和稳定性。

**更新日期**: 2023-12-15
**版本号**: 1.0.0

## 🗄️ 数据库结构

### 设备表 (devices)
```sql
CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region TEXT NOT NULL,           -- 区域
    store TEXT NOT NULL,            -- 门店
    ip TEXT NOT NULL,               -- IP地址
    port INTEGER DEFAULT 554,       -- 端口
    user TEXT NOT NULL,             -- 用户名
    pwd TEXT NOT NULL,              -- 密码
    chs INTEGER DEFAULT 1,          -- 通道数
    name TEXT,                      -- 设备名称
    protocol TEXT DEFAULT 'rtsp',   -- 协议
    status TEXT DEFAULT 'offline',  -- 状态
    last_seen TIMESTAMP,            -- 最后在线时间
    last_check TIMESTAMP,           -- 最后检查时间
    check_count INTEGER DEFAULT 0,  -- 检查次数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 用户表 (users)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 配置文件

### 📁 config/ 目录结构
```
config/
├── 📁 apps/                     # 应用配置
│   ├── backend.json            # 后端配置
│   ├── backend.test.json       # 测试环境
│   └── backend.prod.json       # 生产环境
├── 📁 environments/             # 环境配置
│   ├── development.env         # 开发环境
│   ├── test.env               # 测试环境
│   └── production.env         # 生产环境
├── 📁 servers/                # 服务器配置
│   ├── nginx/                 # Nginx配置
│   └── srs/                   # SRS流媒体配置
├── DATABASE_CONFIG.md         # 数据库配置指南
└── README.md                  # 配置说明
```

### 🔑 环境变量配置

#### 开发环境 (development.env)
```bash
# 数据库配置
DB_TYPE=sqlite
DB_PATH=./data/devices.db
DB_CONNECTION_TIMEOUT=10
DB_POOL_SIZE=5

# 服务配置
BACKEND_PORT=8000
FRONTEND_PORT=3000
WEBRTC_PORT=8080

# 监控配置
HEARTBEAT_INTERVAL=30
LOG_LEVEL=INFO
```

## 🚀 快速开始

### 1️⃣ 环境检查
```bash
# 检查系统状态
python scripts/quick_check.py

# 显示当前配置
python scripts/db_manager.py --show

# 测试数据库连接
python scripts/db_manager.py --test
```

### 2️⃣ 初始化数据库
```bash
# 初始化数据库结构
python scripts/db_manager.py --init
```

### 3️⃣ 启动服务
```bash
# 一键启动所有服务
scripts/start_stable.bat

# 或手动启动
python backend/main.py
npm run dev --prefix frontend
```

### 4️⃣ 设备管理
```bash
# 查看所有设备
python scripts/query_devices.py

# 导入设备数据
python scripts/import_devices.py devices.csv

# 检查设备状态
python scripts/device_status_checker.py
```

## 🎯 功能特性

### 📹 视频流支持
- ✅ **RTSP协议** - 标准监控协议
- ✅ **WebRTC** - 浏览器实时通信
- ✅ **HLS** - HTTP直播流
- ✅ **FLV** - Flash视频格式

### 🔧 设备管理
- ✅ **多品牌支持** - 兼容多种主流监控设备品牌
- ✅ **批量导入** - CSV文件导入
- ✅ **状态监控** - 实时设备状态
- ✅ **异常告警** - 设备离线通知

### 🛡️ 系统特性
- ✅ **异常处理** - 完善的错误处理
- ✅ **心跳监控** - 服务健康检查
- ✅ **日志记录** - 详细操作日志
- ✅ **配置管理** - 环境配置切换

### 🌐 跨平台支持
- ✅ **Windows** - 完整支持
- ✅ **Linux** - Docker部署
- ✅ **macOS** - 开发环境

## 📊 监控指标

### 📈 系统状态
- **设备在线率** - 实时监控设备状态
- **视频流畅度** - 流媒体质量监控
- **系统资源** - CPU、内存使用率
- **网络状态** - 延迟、丢包率

### 🚨 告警机制
- **设备离线** - 立即通知
- **视频中断** - 自动重连
- **系统异常** - 日志记录
- **配置错误** - 提示修复

## 🔍 故障排查

### 📋 常见问题
1. **设备连接失败** - 检查网络配置
2. **视频无法播放** - 验证RTSP地址
3. **服务启动失败** - 查看日志文件
4. **数据库错误** - 检查配置路径

### 🛠️ 诊断工具
```bash
# 检查端口占用
python scripts/fix_port_mapping.py

# 修复NVR配置
python scripts/fix_nvr_config.py

# 数据同步修复
python scripts/fix_data_sync.py

# 查看系统日志
tail -f logs/system.log
```

## 📚 文档索引

### 📖 核心文档
- [📋 项目说明](README.md)
- [⚙️ 配置指南](config/README.md)
- [🗄️ 数据库配置](config/DATABASE_CONFIG.md)
- [🚀 快速开始](docs/QUICK_START.md)

### 🔧 技术文档
- [📊 API文档](docs/API_DOCUMENTATION.md)
- [🏗️ 架构设计](docs/ARCHITECTURE.md)
- [🛠️ 故障排查](docs/TROUBLESHOOTING.md)

### 📱 前端文档
- [🎨 前端说明](frontend/README.md)
- [⚡ 开发指南](frontend/vite.config.js)

### 🎥 流媒体文档
- [🎬 WebRTC配置](streaming/README.md)
- [📡 SRS配置](streaming/webrtc/config.py)

## 🔄 维护指南

### 📝 日常维护
1. **定期检查** - 每周运行系统检查
2. **日志清理** - 定期清理旧日志
3. **数据备份** - 定期备份数据库
4. **更新检查** - 检查系统更新

### 🚨 应急处理
1. **服务重启** - 使用一键启动脚本
2. **配置恢复** - 从备份恢复配置
3. **数据修复** - 使用数据修复工具
4. **联系支持** - 查看文档或寻求帮助

---

*最后更新: 2024年项目重构后*
*文档版本: v2.0*