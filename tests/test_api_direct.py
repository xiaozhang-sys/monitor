#!/usr/bin/env python3
"""
直接测试后端API并验证设备数据
"""

import requests
import sqlite3
import json

def get_devices_from_db():
    """直接从数据库获取设备"""
    conn = sqlite3.connect("backend/data/devices.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices ORDER BY id")
    devices = cursor.fetchall()
    conn.close()
    
    # 获取列名
    conn = sqlite3.connect("backend/data/devices.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(devices)")
    columns = [col[1] for col in cursor.fetchall()]
    conn.close()
    
    result = []
    for device in devices:
        device_dict = dict(zip(columns, device))
        result.append(device_dict)
    
    return result

def test_backend_api():
    """测试后端API"""
    print("🔍 测试后端API...")
    
    # 1. 先登录获取token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post("http://localhost:8090/token", data=login_data)
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print(f"✅ 登录成功，获取token: {token[:20]}...")
            
            # 2. 使用token获取设备列表
            headers = {"Authorization": f"Bearer {token}"}
            devices_response = requests.get("http://localhost:8090/devices", headers=headers)
            
            if devices_response.status_code == 200:
                api_devices = devices_response.json()
                print(f"✅ API返回 {len(api_devices)} 个设备")
                return api_devices
            else:
                print(f"❌ 获取设备失败: {devices_response.status_code}")
                return None
        else:
            print(f"❌ 登录失败: {login_response.status_code}")
            print(f"响应: {login_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return None

def compare_data():
    """比较数据库和API数据"""
    print("\n📊 数据对比分析:")
    print("=" * 50)
    
    # 获取数据库数据
    db_devices = get_devices_from_db()
    print(f"📁 数据库设备数: {len(db_devices)}")
    
    # 获取API数据
    api_devices = test_backend_api()
    
    if api_devices:
        print(f"🌐 API设备数: {len(api_devices)}")
        
        # 对比设备ID
        db_ids = {d['id'] for d in db_devices}
        api_ids = {d['id'] for d in api_devices}
        
        print(f"\n🎯 设备ID对比:")
        print(f"数据库独有: {db_ids - api_ids}")
        print(f"API独有: {api_ids - db_ids}")
        print(f"共同设备: {db_ids & api_ids}")
        
        # 导出数据对比
        with open('data_comparison.json', 'w', encoding='utf-8') as f:
            json.dump({
                'database_devices': db_devices,
                'api_devices': api_devices,
                'db_count': len(db_devices),
                'api_count': len(api_devices) if api_devices else 0
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 详细对比数据已导出到: data_comparison.json")
        
    else:
        print("❌ 无法获取API数据")
    
    return db_devices, api_devices

if __name__ == "__main__":
    print("🚀 开始设备数据同步验证...")
    
    # 对比数据
    db_data, api_data = compare_data()
    
    print("\n" + "=" * 50)
    print("📋 验证完成！")
    
    if db_data:
        print(f"✅ 数据库中有 {len(db_data)} 个真实设备")
        for device in db_data[:5]:  # 显示前5个
            print(f"  - {device['name']} ({device['ip']}:{device['port']})")
    
    if api_data:
        print(f"✅ API返回 {len(api_data)} 个设备")
    else:
        print("❌ API连接问题，需要检查后端服务")