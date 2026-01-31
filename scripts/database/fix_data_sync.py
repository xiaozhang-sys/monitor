#!/usr/bin/env python3
"""
设备数据同步修复脚本
用于修复前后端设备数据不同步的问题
"""

import sqlite3
import requests
import json
import os
from datetime import datetime

def check_database_devices():
    """检查数据库中的真实设备数据"""
    db_path = "backend/data/devices.db"
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, region, store, ip, port, user, pwd, chs, name, status, protocol FROM devices ORDER BY id")
        devices = cursor.fetchall()
        
        print("📊 数据库中的真实设备数据:")
        print("-" * 80)
        
        device_list = []
        for device in devices:
            device_info = {
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
                'protocol': device[10]
            }
            device_list.append(device_info)
            
            print(f"ID: {device[0]} | 名称: {device[8]} | IP: {device[3]}:{device[4]} | "
                  f"协议: {device[10]} | 通道: {device[7]} | 状态: {device[9]}")
        
        print(f"\n✅ 总计: {len(device_list)} 个设备")
        return device_list
        
    except Exception as e:
        print(f"❌ 查询数据库失败: {e}")
        return []
    finally:
        conn.close()

def check_backend_api():
    """检查后端API是否返回正确数据"""
    try:
        # 先尝试无认证访问
        response = requests.get('http://localhost:8090/devices', timeout=5)
        if response.status_code == 401:
            print("🔒 需要认证，尝试使用默认token...")
            headers = {'Authorization': 'Bearer admin-token'}
            response = requests.get('http://localhost:8090/devices', headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 后端API返回: {len(data)} 个设备")
            return data
        else:
            print(f"❌ 后端API返回错误: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 无法连接后端API: {e}")
        return None

def generate_sync_report():
    """生成数据同步报告"""
    print("🔄 设备数据同步检查报告")
    print("=" * 50)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查数据库
    db_devices = check_database_devices()
    
    # 检查后端API
    api_devices = check_backend_api()
    
    print("\n" + "=" * 50)
    
    if len(db_devices) > 0:
        print("🎯 解决方案:")
        print("1. 确保前端正确调用后端API")
        print("2. 检查前端认证token")
        print("3. 验证API端点配置")
        print("4. 清除浏览器缓存和localStorage")
        
        # 创建设备数据JSON文件供前端使用
        with open('real_devices.json', 'w', encoding='utf-8') as f:
            json.dump(db_devices, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 已导出真实设备数据到: real_devices.json")
        
    else:
        print("❌ 数据库中没有设备数据")

def test_api_endpoints():
    """测试所有相关API端点"""
    endpoints = [
        'http://localhost:8090/devices',
            'http://localhost:8090/devices/stats',
            'http://localhost:8090/api/devices',
            'http://localhost:8090/api/devices/stats'
    ]
    
    print("\n🔍 测试API端点:")
    print("-" * 30)
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=3)
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: 无法连接 ({e})")

if __name__ == "__main__":
    print("🚀 开始设备数据同步检查...")
    
    # 生成同步报告
    generate_sync_report()
    
    # 测试API端点
    test_api_endpoints()
    
    print("\n📋 完成！请查看上面的报告并采取相应措施。")