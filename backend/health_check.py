#!/usr/bin/env python3
"""
自定义端口健康检查脚本
支持端口映射后的设备状态检测
"""

import sqlite3
import socket
import os
import sys
import subprocess
from datetime import datetime

DB_PATH = "./data/devices.db"

def test_port_with_timeout(ip, port, timeout=3):
    """测试端口连通性"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def test_rtsp_connection(ip, port, username, password):
    """测试RTSP连接"""
    try:
        rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}/Streaming/Channels/101"
        
        # 使用ffmpeg测试RTSP连接
        cmd = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", rtsp_url,
            "-vframes", "1",
            "-f", "null",
            "-",
            "-t", "3"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        return result.returncode == 0
    except:
        return False

def update_device_health_status():
    """更新所有设备健康状态"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ip, port, user, pwd FROM devices")
        devices = cursor.fetchall()
        
        for device_id, ip, port, username, password in devices:
            # 测试端口和RTSP连接
            port_ok = test_port_with_timeout(ip, port)
            rtsp_ok = test_rtsp_connection(ip, port, username, password)
            
            # 更新状态
            new_status = "online" if (port_ok and rtsp_ok) else "offline"
            cursor.execute("UPDATE devices SET status=? WHERE id=?", (new_status, device_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

if __name__ == "__main__":
    update_device_health_status()
