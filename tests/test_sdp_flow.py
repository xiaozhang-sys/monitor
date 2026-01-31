#!/usr/bin/env python3
"""
测试WebRTC SDP交换流程
"""
import requests
import json
import re

def test_sdp_exchange():
    """测试SDP交换流程"""
    print("🔍 测试WebRTC SDP交换流程...")
    
    try:
        # 测试健康检查
        health = requests.get("http://localhost:8090/health", timeout=5)
        print(f"✅ 健康检查: {health.status_code}")
        
        # 测试offer/answer交换
        offer_sdp = """v=0
o=- 123456789 1 IN IP4 127.0.0.1
s=WebRTC Client
t=0 0
a=group:BUNDLE 0
a=msid-semantic: WMS
m=video 9 UDP/TLS/RTP/SAVPF 96
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:test123
a=ice-pwd:testpassword123456789
a=ice-options:trickle
a=fingerprint:sha-256 11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF
a=setup:actpass
a=mid:0
a=extmap:1 urn:ietf:params:rtp-hdrext:toffset
a=extmap:2 http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time
a=sendrecv
a=rtcp-mux
a=rtcp-rsize
a=rtpmap:96 H264/90000
a=rtcp-fb:96 nack pli
a=rtcp-fb:96 transport-cc
a=rtcp-fb:96 goog-remb"""

        response = requests.post("http://localhost:8090/api/offer", json={
            "sdp": offer_sdp,
            "rtsp_url": "rtsp://demo/test",
            "type": "main"
        }, timeout=10)
        
        print(f"✅ /api/offer响应: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   成功: {data.get('success', False)}")
            print(f"   类型: {data.get('type', 'unknown')}")
            
            # 检查SDP中的指纹
            sdp = data.get('sdp', '')
            if 'fingerprint:sha-256' in sdp:
                # 提取指纹
                fingerprint_match = re.search(r'a=fingerprint:sha-256 ([0-9A-F:]{95})', sdp)
                if fingerprint_match:
                    fingerprint = fingerprint_match.group(1)
                    print(f"   🔑 指纹: {fingerprint}")
                else:
                    print("   ⚠️  找到指纹但格式异常")
            else:
                print("   ❌ 未找到指纹")
                
            print(f"   SDP长度: {len(sdp)}")
            
            # 保存测试响应
            with open("test_sdp_response.txt", "w", encoding="utf-8") as f:
                f.write(sdp)
            print("   💾 SDP响应已保存到 test_sdp_response.txt")
            
        else:
            print(f"   ❌ 错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_sdp_exchange()