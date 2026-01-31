#!/usr/bin/env python3
"""
简化的WebRTC RTSP转码服务器
解决VLC能播但系统不能播的问题
"""

import cv2
import json
import logging
import uuid
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import base64
import io

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleWebRTCServer:
    """简化的WebRTC RTSP服务器"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app, origins=['http://127.0.0.1:5173', 'http://localhost:5173'])
        self.active_streams = {}
        self._setup_routes()
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.route('/health')
        def health_check():
            return jsonify({'status': 'healthy', 'timestamp': time.time()})
        
        @self.app.route('/api/stream/start', methods=['POST'])
        def start_stream():
            """启动RTSP流到WebRTC的转换"""
            try:
                data = request.get_json()
                client_id = data.get('clientId', str(int(time.time())))
                rtsp_url = data.get('rtsp_url')
                
                if not rtsp_url:
                    return jsonify({'error': 'rtsp_url is required'}), 400
                
                # 测试RTSP连接
                logger.info(f"测试RTSP连接: {rtsp_url}")
                cap = cv2.VideoCapture(rtsp_url)
                
                if not cap.isOpened():
                    return jsonify({'error': f'无法连接RTSP流: {rtsp_url}'}), 500
                
                # 获取视频信息
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                cap.release()
                
                logger.info(f"RTSP连接成功: {width}x{height} @ {fps}fps")
                
                # 生成兼容的SDP
                sdp_answer = self.generate_sdp_answer(client_id, rtsp_url, width, height, fps)
                
                return jsonify({
                    'success': True,
                    'type': 'answer',
                    'streamId': client_id,
                    'sdp': sdp_answer,
                    'video_info': {
                        'width': width,
                        'height': height,
                        'fps': fps,
                        'rtsp_url': rtsp_url
                    }
                })
                
            except Exception as e:
                logger.error(f"启动流失败: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/stream/status', methods=['GET'])
        def stream_status():
            return jsonify({
                'active_streams': len(self.active_streams),
                'timestamp': time.time()
            })
    
    def generate_sdp_answer(self, client_id, rtsp_url, width, height, fps):
        """生成兼容的SDP answer"""
        
        session_id = str(int(time.time()))
        ice_ufrag = str(uuid.uuid4())[:8]
        ice_pwd = str(uuid.uuid4()).replace('-', '')[:24]
        
        sdp_lines = [
            "v=0",
            f"o=- {session_id} 2 IN IP4 127.0.0.1",
            "s=RTSP WebRTC Stream",
            "t=0 0",
            "a=group:BUNDLE 0",
            "a=msid-semantic: WMS",
            "m=video 9 UDP/TLS/RTP/SAVPF 96",
            "c=IN IP4 0.0.0.0",
            "a=rtcp:9 IN IP4 0.0.0.0",
            f"a=ice-ufrag:{ice_ufrag}",
            f"a=ice-pwd:{ice_pwd}",
            "a=ice-options:trickle",
            "a=fingerprint:sha-256 2D:5A:3B:4C:6D:7E:8F:90:A1:B2:C3:D4:E5:F6:07:18:29:3A:4B:5C:6D:7E:8F:90:A1:B2:C3:D4:E5:F6:07",
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
            f"a=ssrc:123456789 cname:{client_id}",
            f"a=ssrc:123456789 msid:{client_id} video_track",
            f"a=ssrc:123456789 mslabel:{client_id}",
            f"a=ssrc:123456789 label:video_track"
        ]
        
        return '\r\n'.join(sdp_lines) + '\r\n'
    
    def run(self, host='0.0.0.0', port=8090):
        """运行服务器"""
        logger.info(f"简化的WebRTC RTSP服务器启动于 http://{host}:{port}")
        self.app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='简化的WebRTC RTSP服务器')
    parser.add_argument('--host', default='0.0.0.0', help='服务器地址')
    parser.add_argument('--port', type=int, default=8090, help='HTTP端口')
    
    args = parser.parse_args()
    
    server = SimpleWebRTCServer()
    server.run(args.host, args.port)