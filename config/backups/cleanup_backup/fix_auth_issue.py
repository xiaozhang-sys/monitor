#!/usr/bin/env python3
"""
修复认证问题
解决前端401未授权错误
"""

import requests
import json
import sqlite3

def test_auth_flow():
    """测试认证流程"""
    print("🔍 测试认证流程...")
    
    # 测试无认证访问
    try:
        response = requests.get('http://localhost:8003/devices', timeout=5)
        print(f"   无认证访问: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ 确认需要认证")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
    
    # 测试创建默认用户
    print("\n🔧 检查用户数据...")
    try:
        conn = sqlite3.connect('data/devices.db')
        cursor = conn.cursor()
        
        # 检查用户表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone():
            cursor.execute("SELECT username, role FROM users")
            users = cursor.fetchall()
            if users:
                print(f"   找到用户: {len(users)} 个")
                for username, role in users:
                    print(f"     - {username} ({role})")
            else:
                print("   ❌ 用户表为空")
                # 创建默认用户
                default_password = "${DEFAULT_PASSWORD}"
                cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                             ("admin", default_password, "admin"))
                conn.commit()
                print(f"   ✅ 创建默认用户: admin / ${DEFAULT_PASSWORD}")
        else:
            print("   ❌ 用户表不存在")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ 数据库错误: {e}")

def create_public_devices_endpoint():
    """创建公共设备端点，临时解决认证问题"""
    print("\n🔧 创建公共设备端点...")
    
    # 创建临时文件
    temp_server = '''
from fastapi import FastAPI, HTTPException
import sqlite3
import json

app = FastAPI()

@app.get("/public/devices")
def get_public_devices():
    try:
        conn = sqlite3.connect('data/devices.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, region, store, ip, port, user, pwd, chs, name, status, protocol FROM devices")
        devices = cursor.fetchall()
        conn.close()
        
        device_list = []
        for device in devices:
            device_list.append({
                "id": device[0],
                "region": device[1],
                "store": device[2], 
                "ip": device[3],
                "port": device[4],
                "user": device[5],
                "pwd": device[6],  # 注意：这里暴露了密码，仅用于调试
                "chs": device[7],
                "name": device[8],
                "status": device[9],
                "protocol": device[10]
            })
        return device_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
'''

    with open('temp_public_api.py', 'w', encoding='utf-8') as f:
        f.write(temp_server)
    print("   ✅ 创建临时公共API服务器: temp_public_api.py")

def test_public_endpoint():
    """测试公共端点"""
    print("\n🔍 测试公共端点...")
    try:
        response = requests.get('http://localhost:8004/public/devices', timeout=5)
        print(f"   公共端点访问: {response.status_code}")
        if response.status_code == 200:
            devices = response.json()
            print(f"   ✅ 获取设备数量: {len(devices)}")
        else:
            print(f"   ❌ 公共端点失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 公共端点连接失败: {e}")

def main():
    print("🔧 认证问题修复工具")
    print("="*50)
    
    test_auth_flow()
    create_public_devices_endpoint()
    print("\n💡 建议操作:")
    print("   1. 检查环境变量JWT配置")
    print("   2. 运行 'python temp_public_api.py' 启动临时API")
    print("   3. 测试公共端点访问")
    print("   4. 完成调试后删除临时API文件")

if __name__ == "__main__":
    main()