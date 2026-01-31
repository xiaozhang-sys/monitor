#!/usr/bin/env python3
"""
设备状态检测工具
用于检测监控设备的在线状态
"""

import requests
import sqlite3
import threading
import time
import logging
from datetime import datetime
import subprocess
import socket

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/device_status.log'),
        logging.StreamHandler()
    ]
)

DB_PATH = "./data/devices.db"

class DeviceStatusChecker:
    def __init__(self):
        self.running = False
        self.check_interval = 30  # 每30秒检查一次
        
    def check_device_online(self, ip, port=554):
        """检测设备是否在线"""
        try:
            # 方法1: 使用socket连接检测端口
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                return True
                
            # 方法2: 使用ping命令
            try:
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', '3000', ip],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.returncode == 0
            except:
                return False
                
        except Exception as e:
            logging.error(f"检查设备 {ip} 状态时出错: {e}")
            return False
    
    def update_device_status(self, device_id, status):
        """更新设备状态到数据库"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE devices SET status = ? WHERE id = ?",
                (status, device_id)
            )
            conn.commit()
            conn.close()
            logging.info(f"设备 {device_id} 状态更新为: {status}")
        except Exception as e:
            logging.error(f"更新设备状态失败: {e}")
    
    def get_all_devices(self):
        """获取所有设备信息"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, ip, port, name FROM devices")
            devices = cursor.fetchall()
            conn.close()
            return devices
        except Exception as e:
            logging.error(f"获取设备列表失败: {e}")
            return []
    
    def check_all_devices(self):
        """检查所有设备状态"""
        devices = self.get_all_devices()
        
        for device in devices:
            device_id, ip, port, name = device
            is_online = self.check_device_online(ip, port or 554)
            
            new_status = "online" if is_online else "offline"
            self.update_device_status(device_id, new_status)
            
            logging.info(f"设备 {name}({ip}) 状态: {new_status}")
    
    def start_monitoring(self):
        """开始监控设备状态"""
        self.running = True
        logging.info("开始设备状态监控...")
        
        while self.running:
            try:
                self.check_all_devices()
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                self.running = False
                logging.info("设备状态监控已停止")
                break
            except Exception as e:
                logging.error(f"监控循环出错: {e}")
                time.sleep(5)  # 出错后等待5秒重试
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
    
    def run_once(self):
        """运行一次状态检查"""
        logging.info("执行一次设备状态检查...")
        self.check_all_devices()
        logging.info("设备状态检查完成")

def main():
    """主函数"""
    checker = DeviceStatusChecker()
    
    # 运行一次检查
    checker.run_once()
    
    # 询问是否开始持续监控
    print("\n是否开始持续监控设备状态？(y/n)")
    choice = input().lower()
    if choice == 'y':
        try:
            checker.start_monitoring()
        except KeyboardInterrupt:
            checker.stop_monitoring()

if __name__ == "__main__":
    main()