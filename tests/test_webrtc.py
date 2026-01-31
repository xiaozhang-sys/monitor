#!/usr/bin/env python3
"""测试WebRTC端点的简单脚本"""

import requests
import json

# 测试数据
test_data = {
    "sdp": "v=0\r\no=- 1234567890 2 IN IP4 127.0.0.1\r\ns=Test\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\nc=IN IP4 0.0.0.0\r\na=ice-ufrag:test\r\na=ice-pwd:test123\r\na=fingerprint:sha-256 00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF\r\na=setup:actpass\r\na=mid:0\r\na=sendrecv\r\na=rtpmap:96 H264/90000\r\na=fmtp:96 profile-level-id=42e01f\r\na=rtcp-fb:96 nack pli\r\n",
    "rtsp_url": "rtsp://admin:admin123@192.168.1.100:554/Streaming/Channels/101",
    "type": "offer"
}

print("测试WebRTC /api/offer端点...")
try:
    response = requests.post('http://localhost:8090/api/offer', json=test_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
except Exception as e:
    print(f"错误: {e}")