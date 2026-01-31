import requests
import json
import sqlite3
import time

def test_nvr2_stream():
    """测试录像机二的视频流连接"""
    
    print("=== 测试录像机二视频流连接 ===")
    
    # 1. 从数据库获取设备信息
    conn = sqlite3.connect('backend/data/devices.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, ip, port, user, pwd, status 
        FROM devices 
        WHERE name LIKE '%录像机二%' OR ip LIKE '%42.86%'
    """)
    devices = cursor.fetchall()
    conn.close()
    
    if not devices:
        print("❌ 未找到录像机二设备")
        return
    
    for device in devices:
        device_id, name, ip, port, user, pwd, status = device
        print(f"\n📹 设备信息:")
        print(f"   ID: {device_id}")
        print(f"   名称: {name}")
        print(f"   IP: {ip}:{port}")
        print(f"   用户: {user}")
        print(f"   密码: {pwd}")
        print(f"   状态: {status}")
        
        # 2. 构建RTSP URL
        rtsp_url = f"rtsp://{user}:{pwd}@{ip}:{port}/Streaming/Channels/101"
        print(f"   RTSP地址: {rtsp_url}")
        
        # 3. 测试设备连通性
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                print(f"✅ 设备端口连通: {ip}:{port}")
            else:
                print(f"❌ 设备端口不通: {ip}:{port}")
                
        except Exception as e:
            print(f"❌ 连接测试失败: {e}")
        
        # 4. 测试WebRTC服务
        try:
            webrtc_url = f"http://localhost:8090/api/stream/{device_id}"
            response = requests.get(webrtc_url, timeout=10)
            print(f"   WebRTC服务状态: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ WebRTC服务正常")
            else:
                print(f"❌ WebRTC服务异常: {response.text}")
                
        except Exception as e:
            print(f"❌ WebRTC服务测试失败: {e}")
    
    # 5. 检查后端API
    try:
        response = requests.post('http://localhost:8090/token', 
                               data={'username': 'admin', 'password': 'admin123'})
        if response.status_code == 200:
            token = response.json()['access_token']
            print(f"\n✅ 后端API正常，token: {token[:20]}...")
            
            # 检查设备状态API
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get('http://localhost:8090/devices', headers=headers)
            if response.status_code == 200:
                devices = response.json()
                print(f"✅ 设备API正常，共{len(devices)}个设备")
                
                for device in devices:
                    if '42.86' in str(device) or '录像机二' in str(device):
                        print(f"📱 录像机二API数据:")
                        print(json.dumps(device, indent=2, ensure_ascii=False))
                        break
        else:
            print(f"❌ 后端API异常: {response.text}")
            
    except Exception as e:
        print(f"❌ 后端API测试失败: {e}")

if __name__ == "__main__":
    test_nvr2_stream()