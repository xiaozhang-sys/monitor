#!/usr/bin/env python3
"""
分析HTTP设备类型和正确路径
"""

import requests
import sqlite3

def analyze_device():
    """分析设备"""
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
    
    print(f"设备: {ip}:{port}")
    
    # 测试基本连接
    try:
        response = requests.get(f'http://{ip}:{port}', timeout=5)
        print(f"状态: {response.status_code}")
        print(f"内容类型: {response.headers.get('content-type', '未知')}")
        
        # 检查响应内容
        content = response.text.lower()
        if 'brand_a' in content:  # 品牌A的特征标识
            print("检测到品牌A设备")
            return "brand_a"
        elif 'dahua' in content:
            print("检测到大华设备")
            return "dahua"
        elif 'login' in content or '登录' in response.text:
            print("检测到登录页面")
            return "login_required"
        else:
            print("前200字符:")
            print(response.text[:200])
            return "unknown"
            
    except Exception as e:
        print(f"连接失败: {e}")
        return "connection_failed"

if __name__ == "__main__":
    analyze_device()