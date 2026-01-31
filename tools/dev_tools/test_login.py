import requests
import json

def test_login():
    print('=== 登录测试 ===')
    
    try:
        # 测试登录
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = requests.post('http://localhost:8004/token', data=login_data)
        print(f'状态码: {response.status_code}')
        
        if response.status_code == 200:
            token_data = response.json()
            print('✅ 登录成功')
            print(f'Token: {token_data.get("access_token", "无token")}')
            
            # 测试使用token访问设备列表
            if "access_token" in token_data:
                headers = {'Authorization': f'Bearer {token_data["access_token"]}'}
                devices_response = requests.get('http://localhost:8004/devices', headers=headers)
                print(f'设备列表状态: {devices_response.status_code}')
                if devices_response.status_code == 200:
                    devices = devices_response.json()
                    print(f'找到 {len(devices)} 个设备')
                else:
                    print(f'设备列表错误: {devices_response.text}')
        else:
            print(f'❌ 登录失败: {response.text}')
            
    except Exception as e:
        print(f'连接错误: {e}')

if __name__ == "__main__":
    test_login()