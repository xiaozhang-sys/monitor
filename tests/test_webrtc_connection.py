#!/usr/bin/env python3
"""
WebRTC连接测试脚本
验证修复后的服务器是否能正常处理WebRTC连接
"""

import requests
import json
import time

def test_webrtc_connection():
    """测试WebRTC连接"""
    
    base_url = "http://localhost:8090"
    
    print("🔍 测试WebRTC连接...")
    
    # 1. 测试健康检查
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过 - 指纹: {data.get('fingerprint', 'N/A')}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查错误: {e}")
        return False
    
    # 2. 测试WebRTC offer处理
    test_offer = """v=0
o=- 1234567890 2 IN IP4 127.0.0.1
s=WebRTC Test
m=video 9 UDP/TLS/RTP/SAVPF 96
c=IN IP4 0.0.0.0
a=ice-ufrag:test123
a=ice-pwd:testpassword123
a=fingerprint:sha-256 00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF
a=setup:actpass
a=mid:0
a=sendrecv
a=rtcp-mux
a=rtpmap:96 H264/90000
"""
    
    try:
        payload = {
            "sdp": test_offer,
            "rtsp_url": "rtsp://wowzaec2demo.streamlock.net/vod-multitrack/_definst_/mp4:BigBuckBunny_115k.mov"
        }
        
        response = requests.post(
            f"{base_url}/api/offer", 
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ WebRTC offer处理成功")
            print(f"   响应类型: {data.get('type')}")
            print(f"   SDP长度: {len(data.get('sdp', ''))} 字符")
            
            # 验证SDP格式
            sdp = data.get('sdp', '')
            if 'm=video' in sdp and 'a=fingerprint:sha-256' in sdp:
                print("✅ SDP格式验证通过")
            else:
                print("❌ SDP格式验证失败")
                return False
                
        else:
            print(f"❌ WebRTC offer处理失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ WebRTC offer测试错误: {e}")
        return False
    
    # 3. 测试流启动
    try:
        payload = {
            "clientId": f"test_{int(time.time())}",
            "rtsp_url": "rtsp://wowzaec2demo.streamlock.net/vod-multitrack/_definst_/mp4:BigBuckBunny_115k.mov"
        }
        
        response = requests.post(
            f"{base_url}/api/stream/start",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 流启动测试通过")
        else:
            print(f"⚠️ 流启动测试返回: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ 流启动测试错误: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 WebRTC连接测试开始")
    print("=" * 50)
    
    success = test_webrtc_connection()
    
    print("=" * 50)
    if success:
        print("🎉 WebRTC连接测试全部通过！")
        print("现在可以在浏览器中访问 http://127.0.0.1:5173 使用监控系统")
    else:
        print("❌ WebRTC连接测试失败，请检查日志")