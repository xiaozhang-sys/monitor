#!/usr/bin/env python3
"""
测试HTTP设备URL构建
"""

import sqlite3
import json

def test_http_device_url():
    """测试HTTP设备URL构建"""
    conn = sqlite3.connect('data/devices.db')
    cursor = conn.cursor()
    
    # 获取HTTP设备
    cursor.execute('SELECT * FROM devices WHERE protocol = "http"')
    device = cursor.fetchone()
    conn.close()
    
    if not device:
        print("没有找到HTTP设备")
        return
    
    # 模拟设备数据
    device_dict = {
        'id': device[0],
        'region': device[1],
        'store': device[2],
        'ip': device[3],
        'port': device[4],
        'user': device[5],
        'pwd': device[6],
        'chs': device[7],
        'name': device[8],
        'status': device[9],
        'created_at': str(device[10]),
        'protocol': device[11]
    }
    
    print(f"设备信息: {json.dumps(device_dict, indent=2, ensure_ascii=False)}")
    
    # 构建HTTP URL
    ip = device_dict['ip']
    port = device_dict['port'] or 80
    user = device_dict['user']
    pwd = device_dict['pwd']
    protocol = device_dict['protocol']
    channel = device_dict['chs'] or 1
    
    # 主码流
    channel_code_main = channel * 100 + 1
    url_main = f"{protocol}://{user}:{pwd}@{ip}:{port}/Streaming/channels/{channel_code_main}"
    
    # 子码流
    channel_code_sub = channel * 100 + 2
    url_sub = f"{protocol}://{user}:{pwd}@{ip}:{port}/Streaming/channels/{channel_code_sub}"
    
    print(f"主码流URL: {url_main}")
    print(f"子码流URL: {url_sub}")
    
    # 测试URL访问
    import requests
    try:
        response = requests.get(url_main, timeout=5)
        print(f"URL测试状态: {response.status_code}")
    except Exception as e:
        print(f"URL测试失败: {e}")

if __name__ == "__main__":
    test_http_device_url()