#!/usr/bin/env python3
import requests
import json

def test_system():
    print('=== 系统功能测试 ===')
    
    # 1. 测试登录
    try:
        response = requests.post('http://localhost:8090/token', data={'username': 'admin', 'password': 'admin123'})
        if response.status_code == 200:
            token = response.json()['access_token']
            print('✅ 登录API正常')
        else:
            print(f'❌ 登录API异常: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ 登录测试失败: {e}')
        return False
    
    # 2. 测试设备列表
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('http://localhost:8090/devices', headers=headers)
        if response.status_code == 200:
            devices = response.json()
            print(f'✅ 设备列表API正常 - {len(devices)}个设备')
        else:
            print(f'❌ 设备列表API异常: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ 设备列表测试失败: {e}')
        return False
    
    # 3. 测试设备状态检查
    try:
        response = requests.post('http://localhost:8090/devices/check-all-status', headers=headers)
        if response.status_code == 200:
            print('✅ 设备状态检查API正常')
        else:
            print(f'❌ 设备状态检查API异常: {response.status_code}')
    except Exception as e:
        print(f'⚠️ 设备状态检查测试失败: {e}')
    
    # 4. 测试WebRTC服务
    try:
        response = requests.get('http://localhost:8081/api/health', timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f'✅ WebRTC服务正常 - 状态: {health["status"]}')
        else:
            print(f'⚠️ WebRTC服务异常: {response.status_code}')
    except Exception as e:
        print(f'⚠️ WebRTC服务测试失败: {e}')
    
    print('=== 所有核心服务测试完成 ===')
    return True

if __name__ == "__main__":
    test_system()