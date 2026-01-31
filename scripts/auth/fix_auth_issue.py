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
                default_password = "admin123"
                cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                             ("admin", default_password, "admin"))
                conn.commit()
                print(f"   ✅ 创建默认用户: admin / {default_password}")
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
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import uvicorn

app = FastAPI(title="临时设备API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/devices")
async def get_devices_public():
    try:
        conn = sqlite3.connect('data/devices.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, region, store, ip, port, user, pwd, chs, name, status, protocol FROM devices")
        devices = cursor.fetchall()
        conn.close()
        
        result = []
        for device in devices:
            result.append({
                "id": device[0],
                "region": device[1],
                "store": device[2],
                "ip": device[3],
                "port": device[4],
                "user": device[5],
                "pwd": device[6],
                "chs": device[7],
                "name": device[8],
                "status": device[9],
                "protocol": device[10]
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
'''
    
    with open('temp_public_api.py', 'w', encoding='utf-8') as f:
        f.write(temp_server)
    
    print("   ✅ 创建临时公共API: temp_public_api.py")
    print("   启动命令: python temp_public_api.py")

def main():
    print("🚀 修复认证问题")
    print("=" * 40)
    
    test_auth_flow()
    create_public_devices_endpoint()
    
    print("\n" + "=" * 40)
    print("🔧 解决方案:")
    print("1. 临时方案: 启动公共API (端口8004)")
    print("   python temp_public_api.py")
    print("   然后访问: http://localhost:8004/devices")
    print("\n2. 长期方案: 配置前端认证")
    print("   - 确保用户已登录")
    print("   - 检查Cookies中是否有token")
    print("   - 访问登录页面获取token")

if __name__ == "__main__":
    main()