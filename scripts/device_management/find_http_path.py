#!/usr/bin/env python3
"""
查找HTTP设备的正确视频路径
"""

import sqlite3
import requests
from requests.auth import HTTPBasicAuth

def find_http_device_path():
    """查找HTTP设备的视频路径"""
    conn = sqlite3.connect('data/devices.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices WHERE protocol = 'http'")
    device = cursor.fetchone()
    conn.close()
    
    if not device:
        print("没有找到HTTP设备")
        return
    
    ip = device[3]
    port = device[4]
    user = device[5]
    pwd = device[6]
    
    print(f"设备: {ip}:{port}")
    print(f"用户: {user}")
    
    # 常见的HTTP视频路径
    test_paths = [
        # 品牌A路径格式
        '/ISAPI/Streaming/channels/101',
        '/ISAPI/Streaming/channels/102',
        '/ISAPI/Streaming/channels/201',
        '/ISAPI/Streaming/channels/202',
        '/Streaming/channels/101',
        '/Streaming/channels/102',
        
        # 品牌B路径格式
        '/cam/realmonitor?channel=1&subtype=0',
        '/cam/realmonitor?channel=1&subtype=1',
        '/cgi-bin/snapshot.cgi?chn=1',
        
        # 通用路径
        '/h264/ch1/main/av_stream',
        '/h264/ch1/sub/av_stream',
        '/video1',
        '/video2',
        '/mjpg/video.mjpg',
        '/axis-cgi/mjpg/video.cgi'
    ]
    
    base_url = f'http://{user}:{pwd}@{ip}:{port}'
    
    print("\n测试视频路径:")
    for path in test_paths:
        url = base_url + path
        print(f"\n测试: {url}")
        try:
            response = requests.head(url, timeout=3)
            print(f"  状态: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ 找到有效路径: {path}")
                return path
        except Exception as e:
            print(f"  错误: {e}")
    
    # 尝试获取设备信息
    try:
        print("\n尝试获取设备信息...")
        response = requests.get(f'http://{user}:{pwd}@{ip}:{port}/ISAPI/System/deviceInfo', timeout=5)
        if response.status_code == 200:
            print(f"设备信息: {response.text[:300]}...")
        else:
            print(f"设备信息接口状态: {response.status_code}")
    except Exception as e:
        print(f"获取设备信息失败: {e}")

if __name__ == "__main__":
    find_http_device_path()