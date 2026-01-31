import requests
import json

def show_devices():
    print('=== 设备详细配置 ===')
    
    # 获取token
    login_data = {'username': 'admin', 'password': 'admin123'}
    token_response = requests.post('http://localhost:8003/token', data=login_data)
    
    if token_response.status_code == 200:
        token = token_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 获取设备详情
        devices_response = requests.get('http://localhost:8003/devices', headers=headers)
        if devices_response.status_code == 200:
            devices = devices_response.json()
            
            print(f'找到 {len(devices)} 个设备:\n')
            
            for i, device in enumerate(devices, 1):
                print(f'设备 {i}: {device["name"]}')
                print(f'  设备ID: {device["id"]}')
                print(f'  IP地址: {device["ip"]}')
                print(f'  端口: {device.get("port", "55401")}')
                print(f'  用户名: {device.get("user", "admin")}')
                print(f'  密码: {device.get("pwd", "hk888888")}')
                print(f'  通道数: {device.get("chs", 1)}')
                print(f'  状态: {device.get("status", "unknown")}')
                print(f'  区域: {device.get("region", "未知")}')
                print(f'  门店: {device.get("store", "未知")}')
                
                # 生成RTSP URL
                rtsp_url = f'rtsp://{device.get("user", "admin")}:{device.get("pwd", "hk888888")}@{device["ip"]}:{device.get("port", 55401)}/Streaming/Channels/101'
                print(f'  RTSP地址: {rtsp_url}')
                print()
                
                # 测试设备连接
                import socket
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    port = int(device.get('port', 55401))
                    result = sock.connect_ex((device['ip'], port))
                    sock.close()
                    
                    if result == 0:
                        print('  ✅ 端口连接正常')
                    else:
                        print('  ❌ 端口无法连接')
                except Exception as e:
                    print(f'  ❌ 连接测试失败: {e}')
                
                print('-' * 50)
                
            return devices
        else:
            print(f'❌ 获取设备列表失败: {devices_response.status_code}')
    else:
        print(f'❌ 登录失败: {token_response.status_code}')
    
    return []

if __name__ == "__main__":
    devices = show_devices()