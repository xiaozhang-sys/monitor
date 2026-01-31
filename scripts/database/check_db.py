#!/usr/bin/env python3
import sqlite3
import hashlib
import requests

def check_database():
    print("=== 检查数据库状态 ===")
    
    # 连接数据库
    conn = sqlite3.connect('d:/code/Monitor/backend/devices.db')
    cursor = conn.cursor()
    
    # 检查用户表
    cursor.execute("SELECT username, password_hash, role FROM users")
    users = cursor.fetchall()
    print("用户表数据:")
    for user in users:
        print(f"  用户名: {user[0]}")
        print(f"  密码哈希: {user[1]}")
        print(f"  角色: {user[2]}")
        
        # 检查密码哈希
        expected_hash = hashlib.sha256(os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123").encode()).hexdigest()
        print(f"  期望哈希: {expected_hash}")
        print(f"  哈希匹配: {user[1] == expected_hash}")
    
    # 检查设备数量
    cursor.execute("SELECT COUNT(*) FROM devices")
    device_count = cursor.fetchone()[0]
    print(f"\n设备数量: {device_count}")
    
    # 显示设备详细信息
    cursor.execute("SELECT id, name, ip, port, user, pwd, protocol FROM devices")
    devices = cursor.fetchall()
    print("\n设备表数据:")
    for device in devices:
        print(f"  ID: {device[0]}")
        print(f"  名称: {device[1]}")
        print(f"  IP: {device[2]}:{device[3]}")
        print(f"  用户名: {device[4]}")
        print(f"  密码: {device[5]}")
        print(f"  协议: {device[6]}")
        print("  -------")
    
    conn.close()

def test_login():
    print("\n=== 测试登录API ===")
    try:
        import urllib.parse
        data = urllib.parse.urlencode({
            'username': 'admin',
            'password': os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
        })
        
        response = requests.post(
            'http://localhost:8090/token',
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"响应状态: {response.status_code}")
        if response.status_code == 200:
            print("登录成功!")
            print(f"响应数据: {response.json()}")
        else:
            print("登录失败!")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"连接错误: {e}")

if __name__ == "__main__":
    check_database()
    test_login()