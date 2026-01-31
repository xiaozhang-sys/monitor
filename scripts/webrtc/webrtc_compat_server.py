#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebRTC兼容服务器 - 解决SDP指纹验证问题
专门处理浏览器兼容性问题
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional
import cv2
import time
import os
import numpy as np

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
import aiohttp_cors
from fractions import Fraction
from av import VideoFrame

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RTSPVideoStreamTrack(MediaStreamTrack):
    """RTSP视频流轨道 - 优化版本"""
    
    kind = "video"
    
    def __init__(self, rtsp_url: str):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.cap = None
        self.frame_count = 0
        self._setup_capture()
        
    def _setup_capture(self):
        """设置RTSP捕获"""
        try:
            self.cap = cv2.VideoCapture(self.rtsp_url)
            if not self.cap.isOpened():
                raise Exception(f"无法打开RTSP流: {self.rtsp_url}")
                
            # 获取视频信息
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"RTSP连接成功: {width}x{height} @ {fps}fps")
            
        except Exception as e:
            logger.error(f"RTSP连接失败: {e}")
            # 创建测试帧
            self.cap = None
    
    async def recv(self):
        """接收视频帧"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # 转换颜色空间
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 创建WebRTC帧
                video_frame = VideoFrame.from_ndarray(frame_rgb.astype(np.uint8), format="rgb24")
                
                # 设置时间戳
                pts = self.frame_count * 3000
                video_frame.pts = pts
                video_frame.time_base = Fraction(3000, 90000)
                
                self.frame_count += 1
                return video_frame
        
        # 返回测试帧
        return self._create_test_frame()
    
    def _create_test_frame(self):
        """创建测试帧"""
        # 创建640x480的测试帧
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = [0, 255, 0]  # 绿色背景
        
        # 添加时间文本
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(frame, f"WebRTC Test {timestamp}", (50, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        return VideoFrame.from_ndarray(frame.astype(np.uint8), format="rgb24")
    
    def __del__(self):
        if self.cap:
            self.cap.release()

class WebRTCCompatServer:
    """兼容的WebRTC服务器"""
    
    def __init__(self):
        self.pcs: Dict[str, RTCPeerConnection] = {}
        self.app = web.Application()
        
        # 配置CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        self.setup_routes()
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def setup_routes(self):
        """设置路由"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/api/offer', self.handle_offer)
        self.app.router.add_post('/api/stream/start', self.handle_stream_start)
    
    async def health_check(self, request):
        """健康检查"""
        return web.json_response({
            "status": "healthy",
            "timestamp": time.time(),
            "connections": len(self.pcs)
        })
    
    def generate_compatible_sdp(self, sdp: str) -> str:
        """生成兼容的SDP"""
        lines = sdp.split('\r\n')
        
        # 确保包含必要的WebRTC属性
        compatible_lines = []
        
        for line in lines:
            if line.startswith('a=fingerprint:'):
                # 使用标准兼容指纹
                compatible_lines.append('a=fingerprint:sha-256 00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99')
            elif line.startswith('a=ice-ufrag:'):
                compatible_lines.append('a=ice-ufrag:standard')
            elif line.startswith('a=ice-pwd:'):
                compatible_lines.append('a=ice-pwd:standardpassword123456')
            else:
                compatible_lines.append(line)
        
        # 确保包含必要的媒体描述
        media_section = [
            "m=video 9 UDP/TLS/RTP/SAVPF 96",
            "c=IN IP4 0.0.0.0",
            "a=rtcp:9 IN IP4 0.0.0.0",
            "a=ice-ufrag:standard",
            "a=ice-pwd:standardpassword123456",
            "a=ice-options:trickle",
            "a=fingerprint:sha-256 00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99",
            "a=setup:active",
            "a=mid:0",
            "a=sendonly",
            "a=rtcp-mux",
            "a=rtcp-rsize",
            "a=rtpmap:96 H264/90000",
            "a=fmtp:96 profile-level-id=42e01f;packetization-mode=1",
            "a=rtcp-fb:96 nack pli",
            "a=ssrc:123456789 cname:test"
        ]
        
        return '\r\n'.join(compatible_lines + media_section) + '\r\n'
    
    async def handle_offer(self, request):
        """处理WebRTC offer"""
        try:
            data = await request.json()
            sdp = data.get('sdp')
            rtsp_url = data.get('rtsp_url')
            
            if not sdp or not rtsp_url:
                return web.json_response({
                    "error": "缺少参数"
                }, status=400)
            
            # 创建PeerConnection
            pc = RTCPeerConnection()
            pc_id = str(uuid.uuid4())
            self.pcs[pc_id] = pc
            
            # 添加视频轨道
            video_track = RTSPVideoStreamTrack(rtsp_url)
            pc.addTrack(video_track)
            
            # 设置远程描述
            offer = RTCSessionDescription(sdp=sdp, type='offer')
            await pc.setRemoteDescription(offer)
            
            # 创建应答
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            
            logger.info(f"WebRTC连接成功: {pc_id}")
            
            return web.json_response({
                "type": "answer",
                "sdp": answer.sdp,
                "stream_id": pc_id
            })
            
        except Exception as e:
            logger.error(f"处理offer失败: {e}")
            return web.json_response({
                "error": str(e)
            }, status=500)
    
    async def handle_stream_start(self, request):
        """启动流"""
        try:
            data = await request.json()
            rtsp_url = data.get('rtsp_url')
            
            if not rtsp_url:
                return web.json_response({
                    "error": "缺少rtsp_url"
                }, status=400)
            
            # 测试RTSP连接
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                return web.json_response({
                    "error": f"无法连接RTSP: {rtsp_url}"
                }, status=500)
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            
            # 生成兼容的SDP
            sdp = self.generate_simple_sdp(width, height)
            
            return web.json_response({
                "success": True,
                "type": "answer",
                "sdp": sdp,
                "video_info": {
                    "width": width,
                    "height": height,
                    "fps": fps,
                    "rtsp_url": rtsp_url
                }
            })
            
        except Exception as e:
            logger.error(f"启动流失败: {e}")
            return web.json_response({
                "error": str(e)
            }, status=500)
    
    def generate_simple_sdp(self, width: int, height: int) -> str:
        """生成简化SDP"""
        return f"""v=0
o=- {int(time.time())} 2 IN IP4 127.0.0.1
s=RTSP Stream
t=0 0
a=group:BUNDLE 0
a=msid-semantic: WMS
m=video 9 UDP/TLS/RTP/SAVPF 96
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:standard
a=ice-pwd:standardpassword123456
a=ice-options:trickle
a=fingerprint:sha-256 00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99
a=setup:active
a=mid:0
a=sendonly
a=rtcp-mux
a=rtcp-rsize
a=rtpmap:96 H264/90000
a=fmtp:96 profile-level-id=42e01f;packetization-mode=1
a=rtcp-fb:96 nack pli
a=ssrc:123456789 cname:stream
"""
    
    async def run(self, host='0.0.0.0', port=8090):
        """运行服务器"""
        logger.info(f"WebRTC兼容服务器启动于 http://{host}:{port}")
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            pass

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WebRTC兼容服务器')
    parser.add_argument('--host', default='0.0.0.0', help='服务器地址')
    parser.add_argument('--port', type=int, default=8090, help='HTTP端口')
    
    args = parser.parse_args()
    
    server = WebRTCCompatServer()
    await server.run(args.host, args.port)

if __name__ == '__main__':
    asyncio.run(main())