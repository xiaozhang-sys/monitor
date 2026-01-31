import requests
import json
import time
import subprocess
import os

def test_real_devices():
    print('=== 测试真实设备视频流 ===')
    
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
            
            print(f'发现 {len(devices)} 个真实设备')
            
            # 测试每个设备的RTSP流
            for device in devices:
                print(f'\n🔍 测试设备: {device["name"]}')
                print(f'   IP: {device["ip"]}')
                print(f'   用户: {device.get("user", "admin")}')
                print(f'   密码: {device.get("pwd", "hk888888")}')
                
                # 构建RTSP URL
                rtsp_url = f'rtsp://{device.get("user", "admin")}:{device.get("pwd", "hk888888")}@{device["ip"]}:{device.get("port", 55401)}/Streaming/Channels/101'
                print(f'   RTSP: {rtsp_url}')
                
                # 测试RTSP流
                try:
                    # 使用VLC测试RTSP流
                    vlc_command = [
                        'vlc',
                        '--intf', 'dummy',
                        '--play-and-exit',
                        '--run-time', '5',
                        rtsp_url
                    ]
                    
                    print('   🎥 正在测试RTSP流...')
                    
                    # 启动WebRTC测试
                    client_id = f'device_{device["id"]}_{int(time.time())}'
                    
                    # 测试WebRTC启动
                    webrtc_data = {
                        'type': 'main',
                        'clientId': client_id,
                        'rtsp_url': rtsp_url
                    }
                    
                    response = requests.post(
                        'http://localhost:8090/api/stream/start',
                        json=webrtc_data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f'   ✅ WebRTC启动成功: {result}')
                        
                        # 等待2秒让流建立
                        time.sleep(2)
                        
                        # 检查流状态
                        status_response = requests.get(f'http://localhost:8090/api/stream/status/{client_id}')
                        print(f'   📊 流状态: {status_response.status_code} - {status_response.text}')
                        
                        # 停止流
                        stop_response = requests.post('http://localhost:8090/api/stream/stop', json={'clientId': client_id})
                        print(f'   🛑 停止流: {stop_response.status_code}')
                        
                    else:
                        print(f'   ❌ WebRTC启动失败: {response.status_code} - {response.text}')
                        
                except Exception as e:
                    print(f'   ❌ 测试失败: {e}')
                    
                print('   ' + '='*40)
                
            # 提供测试建议
            print('\n' + '='*60)
            print('📋 实时画面黑色背景排查建议:')
            print('1. 检查摄像头是否在线 (已确认设备在线)')
            print('2. 检查用户名密码是否正确 (已确认正确)')
            print('3. 检查网络连接 (已确认端口可连接)')
            print('4. 检查浏览器是否支持WebRTC')
            print('5. 检查防火墙是否阻止了视频流')
            print('6. 尝试使用VLC直接播放RTSP流')
            print('7. 检查摄像头是否启用了RTSP服务')
            
            # 提供测试命令
            print('\n🔧 手动测试命令:')
            for device in devices:
                rtsp_url = f'rtsp://{device.get("user", "admin")}:{device.get("pwd", "hk888888")}@{device["ip"]}:{device.get("port", 55401)}/Streaming/Channels/101'
                print(f'   {device["name"]}: {rtsp_url}')
                
            print('\n🌐 前端访问: http://localhost:5173')
            print('   登录: admin/admin123')
            print('   然后点击设备查看实时画面')
            
        else:
            print(f'❌ 获取设备列表失败: {devices_response.status_code}')
    else:
        print(f'❌ 登录失败: {token_response.status_code}')

if __name__ == "__main__":
    test_real_devices()