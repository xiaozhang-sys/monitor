#!/usr/bin/env python3
"""查询设备信息"""

import sqlite3
import os

def query_devices():
    """查询所有设备"""
    
    # 尝试多个可能的数据库路径
    db_paths = [
        'backend/data/devices.db',
        'data/devices.db',
        '../backend/data/devices.db',
        '../data/devices.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("未找到数据库文件")
        return
    
    print(f"使用数据库: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询所有设备
    cursor.execute('SELECT id, name, ip, protocol, port, chs FROM devices ORDER BY id')
    devices = cursor.fetchall()
    
    print(f"\n找到 {len(devices)} 个设备:")
    print("-" * 60)
    
    for device in devices:
        device_id, name, ip, protocol, port, chs = device
        print(f"ID: {device_id}")
        print(f"名称: {name}")
        print(f"IP: {ip}")
        print(f"端口: {port}")
        print(f"通道: {chs}")
        print(f"协议: {protocol}")
        
        # 构建URL
        if protocol == 'http':
            url = f"http://{ip}:{port}/Streaming/Channels/{chs}01"
        elif protocol == 'https':
            url = f"https://{ip}:{port}/Streaming/Channels/{chs}01"
        else:  # rtsp
            url = f"rtsp://admin:password@{ip}:{port}/Streaming/Channels/{chs}01"
        
        print(f"URL: {url}")
        print("-" * 40)
    
    # 按协议分组
    cursor.execute('SELECT protocol, COUNT(*) FROM devices GROUP BY protocol')
    protocol_counts = cursor.fetchall()
    
    print("\n按协议分组:")
    for protocol, count in protocol_counts:
        print(f"{protocol.upper()}: {count} 个设备")
    
    conn.close()

if __name__ == "__main__":
    query_devices()