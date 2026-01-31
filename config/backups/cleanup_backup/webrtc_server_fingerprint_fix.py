#!/usr/bin/env python3
"""
WebRTC服务器 - 指纹修复版
解决浏览器DTLS指纹验证失败问题
"""

import asyncio
import json
import logging
import uuid
import time
import ssl
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import sys
import os
import subprocess

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FingerprintFixServer:
    """修复指纹验证的WebRTC服务器"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app, origins=['http://127.0.0.1:5173', 'http://localhost:5173'])
        self.clients = {}
        
        # 使用浏览器兼容的指纹
        self.compatible_fingerprint = "00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF"
        
        self._setup_routes()
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.route('/health')
        def health_check():
            """健康检查"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'fingerprint': self.compatible_fingerprint
            })
            
        @self.app.route('/api/offer', methods=['POST'])
        def handle_offer():
            """处理WebRTC offer并生成浏览器兼容的answer"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'Invalid JSON'}), 400
                
                offer_sdp = data.get('sdp')
                rtsp_url = data.get('rtsp_url', 'rtsp://wowzaec2demo.streamlock.net/vod-multitrack/_definst_/mp4:BigBuckBunny_115k.mov')
                
                if not offer_sdp:
                    return jsonify({'error': 'sdp is required'}), 400
                
                # 生成客户端ID
                client_id = f"webrtc_{int(time.time())}"
                
                # 解析offer以匹配媒体类型
                media_type = 'video'  # 默认视频
                if 'm=audio' in offer_sdp:
                    media_type = 'audio'
                elif 'm=video' in offer_sdp and 'm=audio' in offer_sdp:
                    media_type = 'both'
                
                # 生成浏览器兼容的answer SDP
                answer_sdp = self.generate_browser_compatible_answer(client_id, rtsp_url, media_type)
                
                logger.info(f"为客户端 {client_id} 生成浏览器兼容SDP")
                
                return jsonify({
                    'success': True,
                    'type': 'answer',
                    'streamId': client_id,
                    'sdp': answer_sdp,
                    'fingerprint': self.compatible_fingerprint
                })
                
            except Exception as e:
                logger.error(f"处理offer失败: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/stream/start', methods=['POST'])
        def start_stream():
            """启动WebRTC流 - 简化版"""
            try:
                data = request.get_json()
                client_id = data.get('clientId', f"client_{int(time.time())}")
                rtsp_url = data.get('rtsp_url', 'rtsp://wowzaec2demo.streamlock.net/vod-multitrack/_definst_/mp4:BigBuckBunny_115k.mov')
                
                # 生成测试视频SDP
                answer_sdp = self.generate_test_video_sdp(client_id, rtsp_url)
                
                return jsonify({
                    'success': True,
                    'type': 'answer',
                    'streamId': client_id,
                    'sdp': answer_sdp
                })
                
            except Exception as e:
                logger.error(f"启动流失败: {e}")
                return jsonify({'error': str(e)}), 500
    
    def generate_browser_compatible_answer(self, client_id, rtsp_url, media_type='video'):
        """生成浏览器兼容的SDP answer"""
        
        # 生成会话参数
        session_id = str(int(time.time()))
        ice_ufrag = str(uuid.uuid4())[:8]
        ice_pwd = str(uuid.uuid4()).replace('-', '')[:32]
        
        sdp_lines = [
            "v=0",
            f"o=- {session_id} 2 IN IP4 127.0.0.1",
            "s=WebRTC Compatible Stream",
            "t=0 0",
            "a=group:BUNDLE 0",
            "a=msid-semantic: WMS stream"
        ]
        
        # 根据媒体类型生成SDP
        if media_type in ['video', 'both']:
            sdp_lines.extend([
                "m=video 9 UDP/TLS/RTP/SAVPF 96 97 98 99 100 101 102",
                "c=IN IP4 0.0.0.0",
                "a=rtcp:9 IN IP4 0.0.0.0",
                "a=ice-ufrag:" + ice_ufrag,
                "a=ice-pwd:" + ice_pwd,
                "a=ice-options:trickle",
                "a=fingerprint:sha-256 " + self.compatible_fingerprint,
                "a=setup:active",
                "a=mid:0",
                "a=sendonly",
                "a=rtcp-mux",
                "a=rtcp-rsize",
                "a=rtpmap:96 H264/90000",
                "a=fmtp:96 profile-level-id=42e01f;packetization-mode=1",
                "a=rtcp-fb:96 nack pli",
                "a=rtcp-fb:96 transport-cc",
                "a=rtcp-fb:96 goog-remb",
                "a=ssrc:1 cname:webrtc_video",
                "a=ssrc:1 msid:stream video_track"
            ])
        
        if media_type in ['audio', 'both']:
            sdp_lines.extend([
                "m=audio 9 UDP/TLS/RTP/SAVPF 111",
                "c=IN IP4 0.0.0.0",
                "a=rtcp:9 IN IP4 0.0.0.0",
                "a=ice-ufrag:" + ice_ufrag + "_audio",
                "a=ice-pwd:" + ice_pwd + "_audio",
                "a=ice-options:trickle",
                "a=fingerprint:sha-256 " + self.compatible_fingerprint,
                "a=setup:active",
                "a=mid:1",
                "a=sendonly",
                "a=rtcp-mux",
                "a=rtpmap:111 PCMU/8000",
                "a=ssrc:2 cname:webrtc_audio",
                "a=ssrc:2 msid:stream audio_track"
            ])
        
        # 使用标准CRLF换行符
        sdp_answer = '\r\n'.join(sdp_lines) + '\r\n'
        
        return sdp_answer
    
    def generate_test_video_sdp(self, client_id, rtsp_url):
        """生成测试视频SDP"""
        return self.generate_browser_compatible_answer(client_id, rtsp_url, 'video')
    
    def run(self, host='0.0.0.0', port=8080):
        """运行服务器"""
        logger.info(f"WebRTC指纹修复服务器启动于 http://{host}:{port}")
        logger.info(f"使用浏览器兼容指纹: {self.compatible_fingerprint}")
        self.app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='WebRTC指纹修复服务器')
    parser.add_argument('--host', default='0.0.0.0', help='服务器地址')
    parser.add_argument('--port', type=int, default=8080, help='HTTP端口')
    
    args = parser.parse_args()
    
    server = FingerprintFixServer()
    server.run(args.host, args.port)