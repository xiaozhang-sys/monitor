# 🎥 Retail Eye - Simplified Optimized Version

A web-based multi-brand camera monitoring system supporting real-time video streams, device management, and anomaly alerts.

## 🚀 Quick Start

### 1️⃣ System Requirements
- Python 3.8+
- Node.js 16+
- Windows/Linux/macOS

### Current Port Configuration
- **Backend API**: 8004 (HTTP)
- **Frontend Service**: 5174 (HTTP)
- **WebRTC Service**: 8090 (HTTP) - HEVC/H.265 Compatible
- **WebSocket Monitoring**: 8080 (Backup)

### 2️⃣ One-Click Start
```bash
# Windows
scripts\start_stable.bat

# Manual Start Steps
# 1. Install backend dependencies
pip install -r backend/requirements.txt

# 2. Install frontend dependencies
cd frontend
npm install
cd ..

# 3. Start backend service
python backend/main.py

# 4. Start frontend service
cd frontend
npm run dev
cd ..

# 5. Start HEVC-compatible WebRTC server
python scripts/webrtc/hevc_compat_server.py --port 8090
```

### 3️⃣ Access System
- **Web Interface**: http://localhost:5174
- **API Documentation**: http://localhost:8004/docs
- **WebRTC Test**: http://localhost:8090/health

## 📁 Project Structure

```
Monitor/
├── backend/                 # Backend Service
│   ├── main.py             # Main Service Entry
│   ├── api/               # API Route Definitions
│   ├── models/            # Data Models
│   ├── database.py        # Database Operations
│   └── auth.py            # Authentication Module
├── frontend/              # Frontend Service
│   ├── src/               # Source Code
│   │   ├── components/    # Vue Components
│   │   ├── views/         # Page Views
│   │   ├── router/        # Routing Configuration
│   │   └── utils/         # Utility Functions
│   ├── public/            # Static Resources
│   ├── package.json       # Frontend Dependencies
│   └── vite.config.js     # Build Configuration
├── config/                # Configuration Files
│   └── apps/              # Application Configurations
│       ├── frontend.json  # Frontend Configuration
│       └── backend.json   # Backend Configuration
├── scripts/               # Script Files
│   ├── start_stable.bat   # Windows Startup Script
│   └── webrtc/            # WebRTC Related Scripts
└── data/                  # Data Storage
    └── devices.db         # SQLite Database
```

## ⚙️ Configuration Details

### Backend Configuration (config/apps/backend.json)
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

### Frontend Configuration (config/apps/frontend.json)
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

## 🎥 WebRTC Video Streaming Service

### Service Configuration
- **Port**: 8090
- **Protocol**: HTTP WebSocket
- **Encoding Support**: H.265/HEVC, H.264
- **Compatibility**: All modern browsers

### Startup Commands
```bash
# HEVC-compatible WebRTC Server
python scripts/webrtc/hevc_compat_server.py --port 8090

# Or Standard WebRTC Server
python scripts/webrtc/simple_webrtc_server.py --port 8090
```

## 🗄️ Database Configuration

### SQLite (Default)
- **Path**: ./data/devices.db
- **Driver**: aiomysql (async), sqlite3 (sync)
- **Connection Pool**: Auto-managed
- **Backup Strategy**: Automatic backup

### MySQL (Optional)
- **Host**: localhost:3306
- **User**: monitor_user
- **Password**: password123
- **Database**: retail_monitor

### PostgreSQL (Optional)
- **Host**: localhost:5432
- **User**: pg_monitor_user
- **Password**: pg_password123
- **Database**: retail_monitor_pg

## 🔐 Authentication & Security

### Default Credentials
- **Username**: admin
- **Password**: admin123
- **Token Expiration**: 30 minutes
- **JWT Algorithm**: HS256

### Security Measures
- JWT Token authentication
- HTTPS support
- CORS policy restrictions
- SQL injection protection
- Input validation filtering

## 🔄 API Endpoints

### Authentication Endpoints
- `POST /token` - Get access token
- `GET /verify` - Verify token validity

### Device Management Endpoints
- `GET /devices` - Get device list
- `POST /devices` - Add device
- `PUT /devices/{id}` - Update device
- `DELETE /devices/{id}` - Delete device
- `GET /devices/{id}/status` - Get device status

### Monitoring Endpoints
- `GET /stats` - System statistics
- `POST /devices/check-all-status` - Check all device statuses
- `GET /health` - Health check

## 📊 Logging & Monitoring

### Log Configuration
- **Level**: INFO
- **Format**: Timestamp - Module - Level - Message
- **Path**: ./logs/backend.log

### Monitoring Metrics
- Device online status
- Video stream quality
- System performance metrics
- Error statistics

## 🛠️ Troubleshooting

### Common Issues
1. **Cannot Connect to Database**
   - Check `./data/devices.db` permissions
   - Confirm SQLite driver installation

2. **Frontend Cannot Connect to Backend**
   - Check proxy configuration
   - Confirm port 8004 availability

3. **Video Stream Cannot Play**
   - Check WebRTC service status
   - Confirm RTSP address correctness

### Debug Mode
```bash
# Enable debug mode
DEBUG=true python backend/main.py
```

## 📄 License

Apache License 2.0

## 🤝 Contributing

Welcome to submit Issues and Pull Requests.

---

**Version**: 2.0.0  
**Last Updated**: January 31, 2025