import requests
import json

print("简单测试后端API删除功能...")

# 登录
login_data = {"username": "admin", "password": "admin123"}
try:
    login_resp = requests.post("http://localhost:8004/token", data=login_data)
    if login_resp.status_code == 200:
        token = login_resp.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("✅ 登录成功")
        
        # 获取设备列表
        devices_resp = requests.get("http://localhost:8004/devices", headers=headers)
        if devices_resp.status_code == 200:
            devices = devices_resp.json()
            print(f"✅ 获取到 {len(devices)} 个设备")
            
            if devices:
                # 选择一个设备进行删除测试
                device = devices[0]
                device_id = device['id']
                device_name = device['name']
                print(f"准备删除设备: {device_name} (ID: {device_id})")
                
                # 执行删除
                delete_resp = requests.delete(f"http://localhost:8004/devices/{device_id}", headers=headers)
                print(f"删除响应: {delete_resp.status_code}")
                
                if delete_resp.status_code == 200:
                    print("✅ 后端删除功能正常工作!")
                else:
                    print(f"❌ 删除失败: {delete_resp.text}")
            else:
                print("⚠️ 没有设备可删除")
        else:
            print(f"❌ 获取设备列表失败: {devices_resp.status_code}")
    else:
        print(f"❌ 登录失败: {login_resp.status_code}")
except Exception as e:
    print(f"❌ 请求失败: {e}")