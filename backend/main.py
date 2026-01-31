from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DeviceResponse(BaseModel):
    id: int
    region: str
    store: str
    ip: str
    port: int
    user: str
    pwd: str
    chs: int
    name: Optional[str] = None
    status: str
    protocol: str
    created_at: datetime
    
class DeviceStatsResponse(BaseModel):
    total_devices: int
    online_devices: int
    offline_devices: int
    online_rate: float
    recent_devices: List[DeviceResponse]
    timestamp: datetime
    
class DeviceStatusResponse(BaseModel):
    device_id: int
    name: str
    ip: str
    status: str
    checked_at: datetime
    is_online: bool
    
class BulkDeviceStatusResponse(BaseModel):
    checked_devices: int
    online_devices: int
    offline_devices: int
    results: List[DeviceStatusResponse]
    checked_at: datetime
    online_rate: float
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import hashlib
import jwt
from datetime import datetime, timedelta
import os
import socket
import threading
import time
import logging
import traceback
from typing import Any, Dict, List, Union

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_loader import config_manager
from backend.utils import handle_exceptions, retry_operation
from backend.exceptions import (
    AuthenticationException,
    AuthorizationException,
    DeviceException,
    ValidationException,
    NetworkException,
    ConfigurationException,
    error_handler
)

# 加载后端配置
backend_app_config = config_manager.load_app_config('backend')

# 配置日志
log_config = backend_app_config.get("logging", {})
log_level = log_config.get("level", "INFO")
if isinstance(log_level, str):
    logging.basicConfig(level=getattr(logging, log_level))
else:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="海康设备管理API", version="1.0.0")

# 获取配置
backend_config: Dict[str, Any] = backend_app_config.get("server", {})
jwt_config: Dict[str, Any] = backend_app_config.get("auth", {})
# 使用绝对路径指向根目录下的data/devices.db
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "devices.db")

# CORS配置 - 使用配置文件中的CORS设置
cors_origins = backend_config.get("cors_origins", [])
if not isinstance(cors_origins, list):
    cors_origins = ["http://localhost:3000", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT配置
SECRET_KEY = jwt_config.get("jwt_secret", os.getenv("JWT_SECRET_KEY", "default-secret-key-change-in-production"))
ALGORITHM = jwt_config.get("jwt_algorithm", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = jwt_config.get("access_token_expire_minutes", 30)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 数据模型
class Device(BaseModel):
    region: str
    store: str
    ip: str
    port: int = 554
    user: str
    pwd: str
    chs: int = 1
    name: Optional[str] = None
    protocol: str = "rtsp"  # rtsp, http, https

class DeviceUpdate(BaseModel):
    region: Optional[str] = None
    store: Optional[str] = None
    ip: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    pwd: Optional[str] = None
    chs: Optional[int] = None
    name: Optional[str] = None
    protocol: Optional[str] = None

class User(BaseModel):
    username: str
    password: str
    role: str = "user"  # user, admin

class Token(BaseModel):
    access_token: str
    token_type: str

# 异常处理类
class DatabaseException(Exception):
    """数据库异常"""
    pass

# 数据库连接管理
def get_db_connection():
    """获取数据库连接"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        return conn
    except sqlite3.Error as e:
        logger.error(f"数据库连接失败: {e}")
        raise Exception(f"无法连接到数据库: {str(e)}")
    except Exception as e:
        logger.error(f"数据库连接异常: {e}")
        raise Exception(f"数据库连接出现未知错误: {str(e)}")

# 数据库初始化
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 创建设备表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT NOT NULL,
                store TEXT NOT NULL,
                ip TEXT NOT NULL,
                port INTEGER DEFAULT 554,
                user TEXT NOT NULL,
                pwd TEXT NOT NULL,
                chs INTEGER DEFAULT 1,
                name TEXT,
                protocol TEXT DEFAULT 'rtsp',
                status TEXT DEFAULT 'offline',
                last_seen TIMESTAMP,
                last_check TIMESTAMP,
                check_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建默认管理员用户
        admin_hash = hashlib.sha256(os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123").encode()).hexdigest()
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, role) 
            VALUES (?, ?, ?)
        ''', ("admin", admin_hash, "admin"))
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        logger.debug(f"详细错误信息: {traceback.format_exc()}")
        raise

# 认证函数
def authenticate_user(username: str, password: str):
    """验证用户"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # 使用参数化查询防止SQL注入
        cursor.execute("SELECT username, password_hash, role FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and user[1] == hashlib.sha256(password.encode()).hexdigest():
            return user
        return None
    except Exception as e:
        logger.error(f"用户认证过程中出现错误: {e}")
        raise AuthenticationException(f"认证过程出现错误: {str(e)}")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"令牌创建过程中出现错误: {e}")
        raise AuthenticationException(f"令牌创建失败: {str(e)}")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前用户"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise AuthenticationException("令牌中缺少用户信息")
        return {"username": username, "role": payload.get("role", "user")}
    except jwt.ExpiredSignatureError:
        raise AuthenticationException("令牌已过期")
    except jwt.PyJWTError:
        raise AuthenticationException("令牌无效")

# API路由
@app.post("/token", response_model=Token)
@handle_exceptions
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise AuthenticationException("用户名或密码错误")
    access_token = create_access_token(data={"sub": user[0]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/import")
@handle_exceptions
async def import_device(device: Device, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO devices (region, store, ip, port, user, pwd, chs, name, protocol)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (device.region, device.store, device.ip, device.port, device.user, device.pwd, 
          device.chs, device.name or f"{device.region}-{device.store}", device.protocol))
    
    conn.commit()
    device_id = cursor.lastrowid
    conn.close()
    
    return {"status": "ok", "device_id": device_id}

@app.get("/devices")
@handle_exceptions
async def get_devices(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, region, store, ip, port, user, pwd, chs, name, status, protocol, created_at FROM devices ORDER BY created_at DESC")
    devices = cursor.fetchall()
    conn.close()
    
    result = []
    for device in devices:
        result.append({
            "id": device[0],
            "region": device[1],
            "store": device[2],
            "ip": device[3],
            "port": device[4],
            "user": device[5],
            "pwd": device[6],
            "chs": device[7],
            "name": device[8],
            "status": device[9],
            "protocol": device[10],
            "created_at": device[11]
        })
    return result

@app.post("/devices")
@handle_exceptions
async def create_device(device: Device, current_user: dict = Depends(get_current_user)):
    """创建新设备"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查IP地址是否已存在
    cursor.execute("SELECT id FROM devices WHERE ip=?", (device.ip,))
    if cursor.fetchone():
        conn.close()
        raise ValidationException("IP地址已存在")
    
    # 插入新设备
    cursor.execute("""
        INSERT INTO devices (region, store, ip, port, user, pwd, chs, name, status, protocol, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        device.region,
        device.store,
        device.ip,
        device.port,
        device.user,
        device.pwd,
        device.chs,
        device.name or f"设备_{device.ip}",
        "offline",  # 默认状态为离线
        device.protocol or "rtsp",
        datetime.now().isoformat()
    ))
    
    device_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # 返回创建的设备
    return {
        "id": device_id,
        "region": device.region,
        "store": device.store,
        "ip": device.ip,
        "port": device.port,
        "user": device.user,
        "pwd": device.pwd,
        "chs": device.chs,
        "name": device.name or f"设备_{device.ip}",
        "status": "offline",
        "protocol": device.protocol or "rtsp",
        "created_at": datetime.now().isoformat()
    }

@app.get("/devices/stats")
@handle_exceptions
async def get_device_stats(current_user: dict = Depends(get_current_user)):
    """获取设备统计信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取设备总数
    cursor.execute("SELECT COUNT(*) FROM devices")
    total_devices = cursor.fetchone()[0]
    
    # 获取在线设备数
    cursor.execute("SELECT COUNT(*) FROM devices WHERE status = 'online'")
    online_devices = cursor.fetchone()[0]
    
    # 获取离线设备数
    cursor.execute("SELECT COUNT(*) FROM devices WHERE status = 'offline'")
    offline_devices = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total": total_devices,
        "online": online_devices,
        "offline": offline_devices
    }

@app.get("/devices/{device_id}")
@handle_exceptions
async def get_device(device_id: int, current_user: dict = Depends(get_current_user)):
    """获取单个设备信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, region, store, ip, port, user, pwd, chs, name, status, protocol, created_at FROM devices WHERE id=?", (device_id,))
    device = cursor.fetchone()
    conn.close()
    
    if not device:
        raise DeviceException("设备不存在")
    
    return {
        "id": device[0],
        "region": device[1],
        "store": device[2],
        "ip": device[3],
        "port": device[4],
        "user": device[5],
        "pwd": device[6],
        "chs": device[7],
        "name": device[8],
        "status": device[9],
        "protocol": device[10],
        "created_at": device[11]
    }

@app.put("/devices/{device_id}")
@handle_exceptions
async def update_device(device_id: int, device: DeviceUpdate, 
                       current_user: dict = Depends(get_current_user)):
    """更新设备信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查设备是否存在
    cursor.execute("SELECT id FROM devices WHERE id=?", (device_id,))
    if not cursor.fetchone():
        conn.close()
        raise DeviceException("设备不存在")
    
    # 构建更新语句
    update_fields = []
    values = []
    
    field_mapping = {
        "region": device.region,
        "store": device.store,
        "ip": device.ip,
        "port": device.port,
        "user": device.user,
        "pwd": device.pwd,
        "chs": device.chs,
        "name": device.name,
        "protocol": device.protocol
    }
    
    for field, value in field_mapping.items():
        if value is not None:
            update_fields.append(f"{field}=?")
            values.append(value)
    
    if not update_fields:
        conn.close()
        raise ValidationException("没有提供要更新的字段")
    
    values.append(device_id)
    update_query = f"UPDATE devices SET {', '.join(update_fields)} WHERE id=?"
    
    cursor.execute(update_query, values)
    conn.commit()
    conn.close()
    
    return {"status": "ok"}

@app.delete("/devices/{device_id}")
@handle_exceptions
async def delete_device(device_id: int, current_user: dict = Depends(get_current_user)):
    """删除设备"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查设备是否存在
    cursor.execute("SELECT id FROM devices WHERE id=?", (device_id,))
    if not cursor.fetchone():
        conn.close()
        raise DeviceException("设备不存在")
    
    # 删除设备
    cursor.execute("DELETE FROM devices WHERE id=?", (device_id,))
    conn.commit()
    conn.close()
    
    return {"status": "ok"}

@app.post("/devices/{device_id}/connect")
@handle_exceptions
async def connect_device(device_id: int, current_user: dict = Depends(get_current_user)):
    """连接设备"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查设备是否存在
    cursor.execute("SELECT ip, port, user, pwd FROM devices WHERE id=?", (device_id,))
    device = cursor.fetchone()
    
    if not device:
        conn.close()
        raise DeviceException("设备不存在")
    
    # 这里应该实现实际的设备连接逻辑
    # 目前只是示例，简单地将状态更新为online
    cursor.execute("UPDATE devices SET status=? WHERE id=?", ("online", device_id))
    conn.commit()
    conn.close()
    
    return {"status": "connected"}

@app.post("/devices/{device_id}/disconnect")
@handle_exceptions
async def disconnect_device(device_id: int, current_user: dict = Depends(get_current_user)):
    """断开设备连接"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查设备是否存在
    cursor.execute("SELECT id FROM devices WHERE id=?", (device_id,))
    if not cursor.fetchone():
        conn.close()
        raise DeviceException("设备不存在")
    
    # 更新设备状态为offline
    cursor.execute("UPDATE devices SET status=? WHERE id=?", ("offline", device_id))
    conn.commit()
    conn.close()
    
    return {"status": "disconnected"}

def ping_device(ip: str, timeout: int = 3) -> bool:
    """使用ping命令检测设备是否可达"""
    import subprocess
    import platform
    
    try:
        system = platform.system().lower()
        if system == "windows":
            cmd = ['ping', '-n', '1', '-w', str(timeout * 1000), ip]
        else:
            cmd = ['ping', '-c', '1', '-W', str(timeout), ip]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)
        
        # 检查返回码和输出
        if result.returncode == 0:
            # 检查是否有TTL字段，表示设备响应
            output = result.stdout.lower()
            if 'ttl=' in output or 'time=' in output:
                return True
        return False
        
    except subprocess.TimeoutExpired:
        logger.debug(f"Ping超时 {ip}")
        return False
    except FileNotFoundError:
        logger.warning(f"Ping命令未找到 {ip}")
        return False
    except Exception as e:
        logger.error(f"Ping设备 {ip} 时出错: {e}")
        return False

def check_port_connectivity(ip: str, port: int, timeout: int = 3) -> bool:
    """检查端口连通性"""
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        return result == 0
    except socket.gaierror:
        logger.debug(f"无法解析主机名或IP地址 {ip}:{port}")
        return False
    except socket.timeout:
        logger.debug(f"连接超时 {ip}:{port}")
        return False
    except Exception as e:
        logger.error(f"检查端口 {ip}:{port} 时出错: {e}")
        return False
    finally:
        if sock:
            try:
                sock.close()
            except Exception as e:
                logger.debug(f"关闭套接字时出错 {ip}:{port}: {e}")

def check_device_online(ip: str, port: int = 554, protocol: str = 'rtsp') -> bool:
    """综合检查设备在线状态"""
    try:
        # 方法1: 先使用ping检查
        ping_success = False
        try:
            ping_success = ping_device(ip)
        except Exception as e:
            logger.debug(f"Ping检查失败 {ip}: {e}")
        
        # 方法2: 检查指定端口
        port_success = False
        try:
            port_success = check_port_connectivity(ip, port)
        except Exception as e:
            logger.debug(f"指定端口检查失败 {ip}:{port}: {e}")
        
        # 方法3: 检查HTTP端口（80端口）
        http_success = False
        try:
            http_success = check_port_connectivity(ip, 80)
        except Exception as e:
            logger.debug(f"HTTP端口检查失败 {ip}:80: {e}")
        
        # 方法4: 检查HTTPS端口（443端口）
        https_success = False
        try:
            https_success = check_port_connectivity(ip, 443)
        except Exception as e:
            logger.debug(f"HTTPS端口检查失败 {ip}:443: {e}")
        
        # 如果任一方法成功，则认为在线
        return ping_success or port_success or http_success or https_success
        
    except Exception as e:
        logger.error(f"检查设备 {ip} 状态时出错: {e}")
        return False

@app.post("/devices/{device_id}/check-status")
async def check_device_status(device_id: int, current_user: dict = Depends(get_current_user)):
    """检查单个设备状态"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, ip, port, name, protocol FROM devices WHERE id=?", (device_id,))
        device = cursor.fetchone()
        
        if not device:
            conn.close()
            raise HTTPException(status_code=404, detail="设备未找到")
        
        device_id, ip, port, name, protocol = device
        is_online = check_device_online(ip, port or 554, protocol or 'rtsp')
        new_status = "online" if is_online else "offline"
        
        # 更新状态和相关字段
        now = datetime.now()
        if is_online:
            cursor.execute(
                "UPDATE devices SET status = ?, last_seen = ?, last_check = ?, check_count = check_count + 1 WHERE id = ?",
                (new_status, now.isoformat(), now.isoformat(), device_id)
            )
        else:
            cursor.execute(
                "UPDATE devices SET status = ?, last_check = ?, check_count = check_count + 1 WHERE id = ?",
                (new_status, now.isoformat(), device_id)
            )
        
        conn.commit()
        conn.close()
        
        logger.info(f"手动检查设备 {name}({ip}) 状态: {new_status}")
        
        return {
            "device_id": device_id,
            "name": name or f"设备_{ip}",
            "ip": ip,
            "status": new_status,
            "checked_at": now.isoformat(),
            "is_online": is_online
        }
    except DatabaseException as e:
        logger.error(f"检查设备状态时数据库错误: {e}")
        raise HTTPException(status_code=500, detail="数据库操作失败")
    except HTTPException:
        raise  # 重新抛出已知的HTTP异常
    except Exception as e:
        logger.error(f"检查设备状态时出现未知错误: {e}")
        raise HTTPException(status_code=500, detail="设备状态检查失败")

@app.post("/devices/check-all-status")
async def check_all_devices_status(current_user: dict = Depends(get_current_user)):
    """检查所有设备状态"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, ip, port, name, protocol FROM devices")
        devices = cursor.fetchall()
        
        results = []
        online_count = 0
        now = datetime.now()
        
        for device in devices:
            try:
                device_id, ip, port, name, protocol = device
                is_online = check_device_online(ip, port or 554, protocol or 'rtsp')
                new_status = "online" if is_online else "offline"
                
                # 更新状态和相关字段
                if is_online:
                    cursor.execute(
                        "UPDATE devices SET status = ?, last_seen = ?, last_check = ?, check_count = check_count + 1 WHERE id = ?",
                        (new_status, now.isoformat(), now.isoformat(), device_id)
                    )
                    online_count += 1
                else:
                    cursor.execute(
                        "UPDATE devices SET status = ?, last_check = ?, check_count = check_count + 1 WHERE id = ?",
                        (new_status, now.isoformat(), device_id)
                    )
                
                results.append({
                    "device_id": device_id,
                    "name": name or f"设备_{ip}",
                    "ip": ip,
                    "status": new_status,
                    "is_online": is_online,
                    "checked_at": now.isoformat()
                })
                
                logger.info(f"检查设备 {name}({ip}) 状态: {new_status}")
            except Exception as e:
                logger.error(f"检查设备 {device} 时出错: {e}")
                # 即使单个设备检查失败，也继续处理其他设备
                continue
        
        conn.commit()
        conn.close()
        
        return {
            "checked_devices": len(results),
            "online_devices": online_count,
            "offline_devices": len(results) - online_count,
            "results": results,
            "checked_at": now.isoformat(),
            "online_rate": round(online_count / len(results) * 100, 2) if results else 0
        }
    except DatabaseException as e:
        logger.error(f"批量检查设备状态时数据库错误: {e}")
        raise HTTPException(status_code=500, detail="数据库操作失败")
    except Exception as e:
        logger.error(f"批量检查设备状态时出现未知错误: {e}")
        raise HTTPException(status_code=500, detail="设备状态检查失败")

@app.get("/health")
@handle_exceptions
async def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# 异常处理器
# 不需要再为DatabaseException定义单独的异常处理器，使用全局的error_handler即可

@app.exception_handler(AuthenticationException)
async def authentication_exception_handler(request: Request, exc: AuthenticationException):
    logger.error(f"认证异常: {exc}")
    return JSONResponse(
        status_code=401,
        content={"detail": "认证失败", "error": exc.message, "error_code": exc.error_code}
    )

@app.exception_handler(AuthorizationException)
async def authorization_exception_handler(request: Request, exc: AuthorizationException):
    logger.error(f"授权异常: {exc}")
    return JSONResponse(
        status_code=403,
        content={"detail": "权限不足", "error": exc.message, "error_code": exc.error_code}
    )

@app.exception_handler(DeviceException)
async def device_exception_handler(request: Request, exc: DeviceException):
    logger.error(f"设备异常: {exc}")
    return JSONResponse(
        status_code=404,
        content={"detail": "设备操作失败", "error": exc.message, "error_code": exc.error_code}
    )

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    logger.error(f"验证异常: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "数据验证失败", "error": exc.message, "error_code": exc.error_code}
    )

# 启动时初始化数据库
if __name__ == "__main__":
    import uvicorn
    try:
        init_db()
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        sys.exit(1)
    
    # 从配置加载端口
    port = backend_config.get("port", 8000)
    host = backend_config.get("host", "0.0.0.0")
    
    logger.info(f"启动后端服务: {host}:{port}")
    uvicorn.run(app, host=host, port=port)