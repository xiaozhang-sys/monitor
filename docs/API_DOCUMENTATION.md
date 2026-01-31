# 📚 API 文档

## 🚀 快速开始

### 基础信息
- **Base URL**: `http://localhost:8004/api/v1`
- **前端访问**: `http://localhost:5173`
- **认证方式**: Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

### 认证示例
```bash
# 获取Token
curl -X POST http://localhost:8004/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# 使用Token
curl -X GET http://localhost:8004/api/devices \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📋 API 端点

### 🔐 认证相关

#### 用户登录
```http
POST /api/auth/login
```

**请求参数**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "is_active": true
  }
}
```

#### 用户注册
```http
POST /api/auth/register
```

**请求参数**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "user"
}
```

#### Token刷新
```http
POST /api/auth/refresh
```

**请求参数**:
```json
{
  "refresh_token": "string"
}
```

#### 获取当前用户信息
```http
GET /api/users/me
```

**响应示例**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin",
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T12:00:00Z"
}
```

### 📹 设备管理

#### 获取设备列表
```http
GET /api/devices
```

**查询参数**:
- `skip` (integer): 分页起始位置，默认0
- `limit` (integer): 每页数量，默认100
- `status` (string): 设备状态筛选 (online/offline/all)
- `search` (string): 设备名称搜索

**响应示例**:
```json
{
  "items": [
    {
      "id": 1,
      "name": "门口摄像头",
      "ip_address": "192.168.1.64",
      "rtsp_url": "rtsp://admin:pass@192.168.1.64:554/stream1",
      "status": "online",
      "last_seen": "2024-01-01T12:00:00Z",
      "stream_url": "http://localhost:8085/live/camera1.flv",
      "thumbnail": "http://localhost:8004/static/thumbs/camera1.jpg",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "size": 20
}
```

#### 获取单个设备
```http
GET /api/devices/{device_id}
```

**响应示例**:
```json
{
  "id": 1,
  "name": "门口摄像头",
  "ip_address": "192.168.1.64",
  "rtsp_url": "rtsp://admin:pass@192.168.1.64:554/stream1",
  "username": "admin",
  "password": "pass",
  "port": 554,
  "channel": 1,
  "status": "online",
  "last_seen": "2024-01-01T12:00:00Z",
  "stream_url": "http://localhost:8081/webrtc/camera1",
  "webrtc_url": "http://localhost:8081/webrtc/camera1",
  "hevc_compat_url": "http://localhost:8090/webrtc/camera1",
  "thumbnail": "http://localhost:8004/static/thumbs/camera1.jpg",
  "settings": {
    "resolution": "1920x1080",
    "fps": 25,
    "bitrate": 4000,
    "codec": "H.264/H.265"
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

#### 创建设备
```http
POST /api/devices
```

**请求参数**:
```json
{
  "name": "string",
  "ip_address": "string",
  "username": "string",
  "password": "string",
  "port": 554,
  "channel": 1,
  "resolution": "1920x1080",
  "fps": 25,
  "bitrate": 4000
}
```

#### 更新设备
```http
PUT /api/devices/{device_id}
```

#### 删除设备
```http
DELETE /api/devices/{device_id}
```

#### 设备发现
```http
POST /api/devices/discover
```

**响应示例**:
```json
{
  "task_id": "uuid-123456",
  "status": "processing",
  "discovered": [
    {
      "ip_address": "192.168.1.65",
      "mac_address": "00:11:22:33:44:55",
      "model": "DS-2CD3T46WD-I3",
      "firmware": "V5.5.0",
      "status": "online"
    }
  ]
}
```

### 📊 数据统计

#### 设备统计
```http
GET /api/devices/stats
```

**响应示例**:
```json
{
  "total": 50,
  "online": 45,
  "offline": 5,
  "by_model": {
    "DS-2CD3T46WD-I3": 20,
    "DS-2CD2347G2-LU": 15,
    "DS-2DE4425IW-DE": 15
  },
  "by_status": {
    "online": 45,
    "offline": 5
  },
  "recent_activity": [
    {
      "device_id": 1,
      "device_name": "门口摄像头",
      "event": "online",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ]
}
```

#### 系统状态
```http
GET /api/system/status
```

**响应示例**:
```json
{
  "server": {
    "uptime": "3 days, 12 hours",
    "cpu_usage": 45.2,
    "memory_usage": 65.8,
    "disk_usage": 78.5
  },
  "streaming": {
    "active_streams": 45,
    "total_clients": 120,
    "bandwidth_usage": "125.5 Mbps"
  },
  "database": {
    "size": "256 MB",
    "connections": 12,
    "query_time": "0.05s"
  }
}
```

### 🎥 流媒体相关

#### 获取流媒体信息
```http
GET /api/streaming/info/{device_id}
```

**响应示例**:
```json
{
  "device_id": 1,
  "stream_key": "camera1",
  "rtmp_url": "rtmp://localhost:1935/live/camera1",
  "http_flv_url": "http://localhost:8085/live/camera1.flv",
  "webrtc_url": "http://localhost:8085/rtc/v1/play/?app=live&stream=camera1",
  "hls_url": "http://localhost:8085/live/camera1.m3u8",
  "status": "active",
  "clients": 5,
  "bitrate": 4000,
  "fps": 25,
  "resolution": "1920x1080",
  "uptime": "2 hours, 30 minutes"
}
```

#### 启动/停止流媒体
```http
POST /api/streaming/start/{device_id}
```

```http
POST /api/streaming/stop/{device_id}
```

#### 获取截图
```http
GET /api/devices/{device_id}/snapshot
```

**响应示例**:
```json
{
  "device_id": 1,
  "snapshot_url": "http://localhost:8004/static/snapshots/camera1_20240101_120000.jpg",
  "timestamp": "2024-01-01T12:00:00Z",
  "size": "245 KB",
  "resolution": "1920x1080"
}
```

### 👥 用户管理

#### 获取用户列表
```http
GET /api/users
```

**响应示例**:
```json
{
  "items": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 10
}
```

#### 创建用户
```http
POST /api/users
```

#### 更新用户
```http
PUT /api/users/{user_id}
```

#### 删除用户
```http
DELETE /api/users/{user_id}
```

### ⚙️ 系统配置

#### 获取系统配置
```http
GET /api/settings
```

**响应示例**:
```json
{
  "general": {
    "site_name": "监控系统",
    "timezone": "Asia/Shanghai",
    "language": "zh-CN"
  },
  "streaming": {
    "max_bitrate": 8000,
    "default_resolution": "1920x1080",
    "default_fps": 25,
    "keyframe_interval": 2
  },
  "storage": {
    "retention_days": 30,
    "max_storage_gb": 1000,
    "backup_enabled": true,
    "backup_time": "02:00"
  },
  "notifications": {
    "email_enabled": true,
    "sms_enabled": false,
    "webhook_url": "https://example.com/webhook"
  }
}
```

#### 更新系统配置
```http
PUT /api/settings
```

## 🚨 错误处理

### 错误响应格式
```json
{
  "error": {
    "code": "DEVICE_NOT_FOUND",
    "message": "设备不存在",
    "details": "设备ID: 999",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 错误码列表
| 错误码 | HTTP状态 | 描述 |
|--------|----------|------|
| INVALID_CREDENTIALS | 401 | 用户名或密码错误 |
| TOKEN_EXPIRED | 401 | Token已过期 |
| DEVICE_NOT_FOUND | 404 | 设备不存在 |
| DEVICE_OFFLINE | 400 | 设备离线 |
| INVALID_IP_FORMAT | 400 | IP地址格式错误 |
| DUPLICATE_DEVICE | 409 | 设备已存在 |
| STREAM_NOT_FOUND | 404 | 流媒体不存在 |
| SYSTEM_ERROR | 500 | 系统内部错误 |

## 🧪 测试示例

### 使用curl测试
```bash
# 1. 登录获取Token
TOKEN=$(curl -s -X POST http://localhost:8004/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | jq -r '.access_token')

# 2. 获取设备列表
curl -X GET http://localhost:8004/api/devices \
  -H "Authorization: Bearer $TOKEN"

# 3. 创建设备
curl -X POST http://localhost:8004/api/devices \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试摄像头",
    "ip_address": "192.168.1.100",
    "username": "admin",
    "password": "password",
    "port": 554,
    "channel": 1
  }'
```

### 使用Python测试
```python
import requests

# 基础配置
BASE_URL = "http://localhost:8004/api"

# 登录获取token
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin"
})
token = login_response.json()["access_token"]

# 设置认证头
headers = {"Authorization": f"Bearer {token}"}

# 获取设备列表
devices = requests.get(f"{BASE_URL}/devices", headers=headers).json()
print(f"设备总数: {devices['total']}")

# 创建设备
new_device = requests.post(f"{BASE_URL}/devices", 
    headers=headers,
    json={
        "name": "新摄像头",
        "ip_address": "192.168.1.101",
        "username": "admin",
        "password": "admin"
    }
).json()
print(f"创建成功: {new_device['id']}")
```

### 使用JavaScript测试
```javascript
// API客户端封装
class MonitorAPI {
  constructor(baseURL = 'http://localhost:8004/api') {
    this.baseURL = baseURL;
    this.token = null;
  }

  async login(username, password) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    this.token = data.access_token;
    return data;
  }

  async getDevices() {
    const response = await fetch(`${this.baseURL}/devices`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return response.json();
  }

  async createDevice(deviceData) {
    const response = await fetch(`${this.baseURL}/devices`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify(deviceData)
    });
    return response.json();
  }
}

// 使用示例
const api = new MonitorAPI();
await api.login('admin', 'admin');
const devices = await api.getDevices();
console.log('设备列表:', devices);
```

## 📊 WebSocket API

### 实时通知
```javascript
// 连接WebSocket
const ws = new WebSocket('ws://localhost:8004/ws')

ws.onopen = () => {
  console.log('WebSocket连接成功')
  // 订阅设备状态
  ws.send(JSON.stringify({
    action: 'subscribe',
    channel: 'device_status'
  }))
}

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log('收到消息:', data)
  
  switch(data.type) {
    case 'device_online':
      console.log(`设备 ${data.device_id} 上线`)
      break
    case 'device_offline':
      console.log(`设备 ${data.device_id} 离线`)
      break
    case 'motion_detected':
      console.log(`设备 ${data.device_id} 检测到移动`)
      break
  }
}
```

### 消息格式
```json
{
  "type": "device_online",
  "device_id": 1,
  "device_name": "门口摄像头",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "ip_address": "192.168.1.64",
    "signal_strength": 85
  }
}
```

## 🔗 SDK示例

### Python SDK
```python
from monitor_sdk import MonitorClient

client = MonitorClient('http://localhost:8004')

# 登录
client.login('admin', 'admin')

# 获取设备列表
devices = client.get_devices()
for device in devices:
    print(f"{device['name']}: {device['status']}")

# 创建新设备
new_device = client.create_device({
    'name': '新摄像头',
    'ip_address': '192.168.1.101',
    'username': 'admin',
    'password': 'password'
})

# 获取实时流地址
stream_url = client.get_stream_url(new_device['id'])
print(f"流地址: {stream_url}")
```

### JavaScript SDK
```javascript
import { MonitorClient } from 'monitor-sdk'

const client = new MonitorClient('http://localhost:8004')

// 使用async/await
async function main() {
  await client.login('admin', 'admin')
  
  const devices = await client.getDevices()
  console.log('设备列表:', devices)
  
  // 监听实时更新
  client.onDeviceStatusChange((device) => {
    console.log('设备状态变化:', device)
  })
}

main()
```

---

## 📞 技术支持

**遇到问题？**
- 📧 邮箱: api@monitor-system.com
- 💬 QQ群: 123456789
- 📱 微信: monitor-system
- 🐛 Issues: GitHub Issues

**API测试工具推荐**:
- [Postman](https://www.postman.com/)
- [Thunder Client](https://www.thunderclient.com/)
- [curl](https://curl.se/)
- [httpie](https://httpie.io/)