#!/usr/bin/env python3
"""
批量添加HTTP NVR设备
"""

import requests
import json
import time
import os

def add_device(device_data):
    """添加单个设备"""
    url = 'http://localhost:8000/devices'
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(device_data))
        if response.status_code == 200:
            print(f"✅ 成功添加设备: {device_data['name']} - {device_data['ip']}")
            return True
        else:
            print(f"❌ 添加失败: {device_data['name']} - {response.status_code}")
            print(f"   错误详情: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 连接错误: {device_data['name']} - {e}")
        return False

def add_http_nvr_devices():
    """添加HTTP NVR设备"""
    devices = [
        {
            'region': '北京',
            'store': '朝阳店',
            'ip': '192.168.1.100',
            'port': 80,
            'username': 'admin',
            'password': os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123"),
            'protocol': 'http',
            'chs': 16,  # 16通道录像机
            'name': 'HTTP NVR-01'
        },
        {
            'region': '上海',
            'store': '浦东店',
            'ip': '192.168.1.101',
            'port': 80,
            'username': 'admin',
            'password': os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123"),
            'protocol': 'http',
            'chs': 16,
            'name': 'HTTP NVR-02'
        },
        {
            'region': '广州',
            'store': '天河店',
            'ip': '192.168.1.102',
            'port': 80,
            'username': 'admin',
            'password': os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123"),
            'protocol': 'http',
            'chs': 16,
            'name': 'HTTP NVR-03'
        }
    ]
    
    print("🔄 开始添加HTTP NVR设备...")
    success_count = 0
    
    for device in devices:
        if add_device(device):
            success_count += 1
        time.sleep(0.5)  # 避免请求过于频繁
    
    print(f"\n📊 添加完成: {success_count}/{len(devices)} 个设备")

if __name__ == '__main__':
    add_http_nvr_devices()