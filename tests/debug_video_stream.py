#!/usr/bin/env python3
"""
视频流调试工具
检查WebRTC视频播放的完整链路
"""

import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoStreamDebugger:
    def __init__(self):
        self.backend_url = "http://localhost:8003"
        self.webrtc_url = "http://localhost:8090"
        self.frontend_url = "http://127.0.0.1:5173"
    
    def check_device_status(self):
        """检查设备状态"""
        print("🔍 检查设备状态...")
        try:
            response = requests.get(f"{self.backend_url}/devices", timeout=5)
            if response.status_code == 200:
                devices = response.json()
                print(f"✅ 发现 {len(devices)} 个设备")
                for device in devices:
                    print(f"   📹 {device.get('name', '未知设备')}: {device.get('rtsp_url', '无RTSP地址')}")
                return devices
            else:
                print(f"❌ 获取设备失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 设备检查错误: {e}")
            return []
    
    def test_webrtc_connection(self, device):
        """测试WebRTC连接"""
        print(f"\n🔗 测试WebRTC连接: {device.get('name')}")
        
        # 模拟浏览器offer
        test_offer = f"""v=0
o=- {int(time.time())} 2 IN IP4 127.0.0.1
s=WebRTC Test
m=video 9 UDP/TLS/RTP/SAVPF 96
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:test123
a=ice-pwd:testpassword123
a=ice-options:trickle
a=fingerprint:sha-256 00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF
a=setup:actpass
a=mid:0
a=sendrecv
a=rtcp-mux
a=rtcp-rsize
a=rtpmap:96 H264/90000
a=fmtp:96 profile-level-id=42e01f;packetization-mode=1
a=rtcp-fb:96 nack pli
a=rtcp-fb:96 transport-cc
a=rtcp-fb:96 goog-remb
"""
        
        try:
            payload = {
                "sdp": test_offer,
                "rtsp_url": device.get('rtsp_url')
            }
            
            response = requests.post(
                f"{self.webrtc_url}/api/offer",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                sdp = data.get('sdp', '')
                print(f"✅ WebRTC响应成功")
                print(f"   SDP长度: {len(sdp)} 字符")
                print(f"   包含H264: {'H264' in sdp}")
                print(f"   包含指纹: {'fingerprint' in sdp}")
                return True
            else:
                print(f"❌ WebRTC响应失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ WebRTC测试错误: {e}")
            return False
    
    def check_frontend_config(self):
        """检查前端配置"""
        print("\n🌐 检查前端配置...")
        try:
            # 检查前端是否能访问API
            response = requests.get(f"{self.frontend_url}", timeout=5)
            if response.status_code == 200:
                print("✅ 前端服务正常")
                
                # 检查CORS配置
                response = requests.get(f"{self.webrtc_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ WebRTC服务可访问")
                    return True
            return False
        except Exception as e:
            print(f"❌ 前端配置错误: {e}")
            return False
    
    def run_debug(self):
        """运行完整调试"""
        print("🚀 视频流调试开始")
        print("=" * 50)
        
        # 1. 检查设备
        devices = self.check_device_status()
        if not devices:
            print("❌ 没有可用设备")
            return
        
        # 2. 检查前端
        self.check_frontend_config()
        
        # 3. 测试每个设备的WebRTC
        for device in devices:
            self.test_webrtc_connection(device)
        
        print("\n" + "=" * 50)
        print("🔧 调试建议:")
        print("1. 如果WebRTC连接正常但无画面，检查浏览器控制台")
        print("2. 尝试使用不同浏览器测试")
        print("3. 检查RTSP流是否真的在传输数据")
        print("4. 查看前端是否有JavaScript错误")

if __name__ == "__main__":
    debugger = VideoStreamDebugger()
    debugger.run_debug()