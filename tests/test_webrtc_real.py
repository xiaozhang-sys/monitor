#!/usr/bin/env python3
"""
测试真正的WebRTC媒体服务器
"""
import requests
import json

def test_real_webrtc():
    """测试真正的WebRTC媒体服务器"""
    print("🧪 测试真正的WebRTC媒体服务器...")
    
    try:
        # 测试健康检查
        print("1. 检查健康状态...")
        health = requests.get("http://localhost:8090/health", timeout=5)
        print(f"   健康检查: {health.status_code}")
        
        # 测试流启动
        print("2. 测试流启动API...")
        response = requests.post(
            "http://localhost:8090/api/stream/start",
            json={
                "clientId": "test_device_1",
                "rtsp_url": "test://demo/video",
                "type": "main"
            },
            timeout=10
        )
        
        print(f"   响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   成功: {data.get('success', False)}")
            print(f"   类型: {data.get('type', 'unknown')}")
            print(f"   SDP长度: {len(data.get('sdp', ''))}")
            print(f"   流ID: {data.get('streamId', 'none')}")
            print(f"   URL: {data.get('url', 'none')}")
            
            # 检查是否有实际的视频流处理
            if 'RTSPVideoStreamTrack' in str(data):
                print("   ✅ 检测到RTSP视频流轨道")
            else:
                print("   ⚠️  可能只是SDP生成")
                
        else:
            print(f"   ❌ 错误: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    test_real_webrtc()