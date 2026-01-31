#!/usr/bin/env python3
"""
设备心跳监测系统
自动检测设备在线/离线状态，支持定时监测和手动检查
"""

import sys
import os
import time
import threading
import sqlite3
import logging
import socket
import subprocess
from datetime import datetime, timedelta
import requests

# 添加后端目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/heartbeat_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = "./data/devices.db"

class HeartbeatMonitor:
    def __init__(self, check_interval=600):  # 默认10分钟检查一次
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        self.last_check_time = None
        
    def get_all_devices(self):
        """获取所有设备信息"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, ip, port, name, protocol FROM devices")
            devices = cursor.fetchall()
            conn.close()
            return devices
        except Exception as e:
            logger.error(f"获取设备列表失败: {e}")
            return []
    
    def ping_device(self, ip, timeout=3):
        """使用ping命令检测设备是否可达"""
        try:
            # Windows系统使用ping命令
            if os.name == 'nt':
                cmd = ['ping', '-n', '1', '-w', str(timeout * 1000), ip]
            else:
                # Unix系统使用ping命令
                cmd = ['ping', '-c', '1', '-W', str(timeout), ip]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)
            
            # 检查返回码
            if result.returncode == 0:
                # 检查是否有TTL字段，表示设备响应
                if 'TTL=' in result.stdout or 'ttl=' in result.stdout:
                    return True
                return True
            return False
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Ping {ip} 超时")
            return False
        except Exception as e:
            logger.error(f"Ping设备 {ip} 时出错: {e}")
            return False
    
    def check_port_connectivity(self, ip, port, timeout=3):
        """检查端口连通性"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.error(f"检查端口 {ip}:{port} 时出错: {e}")
            return False
    
    def check_device_online(self, ip, port=554, protocol='rtsp'):
        """综合检查设备在线状态"""
        try:
            # 方法1: 先使用ping检查
            ping_success = self.ping_device(ip)
            if not ping_success:
                logger.debug(f"设备 {ip} ping失败，尝试端口检查")
            
            # 方法2: 检查指定端口
            port_success = self.check_port_connectivity(ip, port)
            
            # 方法3: 检查HTTP端口（80端口）
            http_success = self.check_port_connectivity(ip, 80)
            
            # 如果ping成功或任一端口成功，则认为在线
            return ping_success or port_success or http_success
            
        except Exception as e:
            logger.error(f"检查设备 {ip} 状态时出错: {e}")
            return False
    
    def update_device_status(self, device_id, status, last_seen=None):
        """更新设备状态到数据库"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            if last_seen:
                cursor.execute(
                    "UPDATE devices SET status = ?, last_seen = ? WHERE id = ?",
                    (status, last_seen, device_id)
                )
            else:
                cursor.execute(
                    "UPDATE devices SET status = ? WHERE id = ?",
                    (status, device_id)
                )
            
            conn.commit()
            conn.close()
            logger.info(f"设备 {device_id} 状态更新为: {status}")
            return True
        except Exception as e:
            logger.error(f"更新设备状态失败: {e}")
            return False
    
    def check_single_device(self, device_id):
        """检查单个设备状态"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, ip, port, name, protocol FROM devices WHERE id=?", (device_id,))
            device = cursor.fetchone()
            conn.close()
            
            if not device:
                logger.error(f"设备 {device_id} 不存在")
                return None
            
            device_id, ip, port, name, protocol = device
            is_online = self.check_device_online(ip, port or 554, protocol)
            new_status = "online" if is_online else "offline"
            
            # 更新状态
            self.update_device_status(device_id, new_status, datetime.now().isoformat())
            
            logger.info(f"手动检查设备 {name}({ip}) 状态: {new_status}")
            
            return {
                "device_id": device_id,
                "name": name,
                "ip": ip,
                "status": new_status,
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"检查设备 {device_id} 时出错: {e}")
            return None
    
    def check_all_devices(self):
        """检查所有设备状态"""
        devices = self.get_all_devices()
        
        if not devices:
            logger.info("没有找到设备，跳过检查")
            return []
        
        logger.info(f"开始检查 {len(devices)} 个设备的状态...")
        
        results = []
        online_count = 0
        
        for device in devices:
            device_id, ip, port, name, protocol = device
            
            try:
                is_online = self.check_device_online(ip, port or 554, protocol)
                new_status = "online" if is_online else "offline"
                
                # 更新状态
                self.update_device_status(device_id, new_status, datetime.now().isoformat())
                
                results.append({
                    "device_id": device_id,
                    "name": name,
                    "ip": ip,
                    "status": new_status,
                    "checked_at": datetime.now().isoformat()
                })
                
                if is_online:
                    online_count += 1
                    logger.info(f"✓ {name}({ip}) - 在线")
                else:
                    logger.info(f"✗ {name}({ip}) - 离线")
                    
            except Exception as e:
                logger.error(f"检查设备 {name}({ip}) 时出错: {e}")
                results.append({
                    "device_id": device_id,
                    "name": name,
                    "ip": ip,
                    "status": "error",
                    "error": str(e),
                    "checked_at": datetime.now().isoformat()
                })
        
        self.last_check_time = datetime.now()
        logger.info(f"状态检查完成: {online_count}/{len(devices)} 设备在线")
        
        return results
    
    def start_monitoring(self):
        """开始定时监测"""
        if self.running:
            logger.warning("监测已在运行中")
            return
        
        self.running = True
        logger.info(f"开始设备心跳监测，检查间隔: {self.check_interval}秒")
        
        def monitoring_loop():
            while self.running:
                try:
                    self.check_all_devices()
                    
                    # 等待下一次检查
                    for _ in range(self.check_interval):
                        if not self.running:
                            break
                        time.sleep(1)
                        
                except KeyboardInterrupt:
                    self.running = False
                    logger.info("设备心跳监测已停止")
                    break
                except Exception as e:
                    logger.error(f"监测循环出错: {e}")
                    time.sleep(60)  # 出错后等待1分钟重试
        
        self.thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.thread.start()
    
    def stop_monitoring(self):
        """停止定时监测"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("设备心跳监测已停止")
    
    def get_status(self):
        """获取监测状态"""
        return {
            "running": self.running,
            "check_interval": self.check_interval,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "total_devices": len(self.get_all_devices())
        }
    
    def run_once(self):
        """运行一次完整的状态检查"""
        logger.info("执行一次完整设备状态检查...")
        results = self.check_all_devices()
        logger.info("设备状态检查完成")
        return results

# 全局监测器实例
monitor = HeartbeatMonitor()

def start_monitoring_service():
    """启动监测服务"""
    monitor.start_monitoring()

def stop_monitoring_service():
    """停止监测服务"""
    monitor.stop_monitoring()

def get_monitoring_status():
    """获取监测状态"""
    return monitor.get_status()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="设备心跳监测系统")
    parser.add_argument("--interval", type=int, default=600, 
                       help="检查间隔（秒），默认600秒（10分钟）")
    parser.add_argument("--once", action="store_true",
                       help="只运行一次检查")
    parser.add_argument("--device", type=int,
                       help="检查指定设备ID")
    
    args = parser.parse_args()
    
    if args.device:
        # 检查单个设备
        result = monitor.check_single_device(args.device)
        if result:
            print(f"设备状态: {result}")
    elif args.once:
        # 运行一次检查
        results = monitor.run_once()
        for result in results:
            print(f"{result['name']}({result['ip']}) - {result['status']}")
    else:
        # 启动持续监测
        monitor.check_interval = args.interval
        try:
            start_monitoring_service()
            print(f"设备心跳监测已启动，检查间隔: {args.interval}秒")
            print("按 Ctrl+C 停止监测...")
            
            # 保持程序运行
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            stop_monitoring_service()
            print("\n设备心跳监测已停止")