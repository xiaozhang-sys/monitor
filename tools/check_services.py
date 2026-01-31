#!/usr/bin/env python3
"""
服务状态检查脚本
"""
import requests
import time

def check_service(name, url, timeout=5):
    """检查单个服务状态"""
    try:
        response = requests.get(url, timeout=timeout)
        print(f"✅ {name}: {response.status_code} - 运行正常")
        if response.status_code == 200 and 'application/json' in response.headers.get('content-type', ''):
            try:
                data = response.json()
                if 'status' in data:
                    print(f"   状态: {data.get('status', 'unknown')}")
                if 'active_connections' in data:
                    print(f"   活跃连接: {data.get('active_connections', 0)}")
            except:
                pass
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: 连接失败 - 无法连接到服务器")
    except requests.exceptions.Timeout:
        print(f"❌ {name}: 连接超时 - 服务器响应超时")
    except Exception as e:
        print(f"❌ {name}: 错误 - {str(e)}")
    return False

def main():
    print("🔍 正在检查服务状态...")
    print("-" * 50)
    
    # 检查后端服务
    backend_ok = check_service("后端服务", "http://localhost:8003/health")
    
    # 检查WebRTC服务
    webrtc_ok = check_service("WebRTC服务", "http://localhost:8090/health")
    
    # 检查前端服务
    frontend_ok = check_service("前端服务", "http://127.0.0.1:5173")
    
    print("-" * 50)
    
    # 测试WebRTC API
    if webrtc_ok:
        print("\n🧪 测试WebRTC API...")
        try:
            response = requests.post("http://localhost:8090/api/stream/start", 
                                   json={
                                       "clientId": "test_device_1",
                                       "rtsp_url": "test://demo/video",
                                       "type": "main"
                                   }, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ WebRTC API: 响应正常")
                    print(f"   SDP长度: {len(data.get('sdp', ''))} 字符")
                else:
                    print(f"❌ WebRTC API: {data.get('error', '未知错误')}")
            else:
                print(f"❌ WebRTC API: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ WebRTC API测试失败: {str(e)}")
    
    print("\n🌐 访问地址:")
    print("   前端界面: http://127.0.0.1:5173")
    print("   后端API: http://localhost:8003")
    print("   WebRTC服务: http://localhost:8090")
    
    if all([backend_ok, webrtc_ok, frontend_ok]):
        print("\n🎉 所有服务运行正常！")
    else:
        print("\n⚠️  部分服务异常，请检查相关日志")

if __name__ == "__main__":
    main()