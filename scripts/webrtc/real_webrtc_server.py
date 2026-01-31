#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真正的WebRTC媒体服务器 - 使用aiortc实现RTSP到WebRTC的完整转换
支持H.264视频流的实时传输

这是生产环境使用的标准WebRTC服务器，替代之前的模拟服务器
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional
import cv2
import threading
import time
import os
import sys
import numpy as np

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaPlayer
from aiortc.rtcrtpsender import RTCRtpSender
import aiohttp_cors
from fractions import Fraction

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webrtc_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RTSPVideoStreamTrack(MediaStreamTrack):
    """RTSP视频流轨道"""
    
    kind = "video"
    
    def __init__(self, rtsp_url: str):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame_rate = 30
        self.frame_count = 0
        self.last_frame = None
        self._start_capture()
        
    def _start_capture(self):
        """启动RTSP流捕获"""
        try:
            logger.info(f"尝试连接到RTSP流: {self.rtsp_url}")
            
            # 使用FFmpeg参数优化HEVC解码
            self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
            
            if not self.cap.isOpened():
                logger.warning("FFmpeg连接失败，尝试GStreamer...")
                # 尝试使用GStreamer作为备选
                gst_pipeline = (
                    f'rtspsrc location={self.rtsp_url} latency=0 ! '
                    f'rtph265depay ! h265parse ! avdec_h265 ! '
                    f'videoconvert ! appsink'
                )
                self.cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
                if not self.cap.isOpened():
                    raise Exception(f"无法打开RTSP流: {self.rtsp_url}")
            
            # 设置缓冲区大小以减少延迟
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # 获取并记录视频信息
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"成功连接到RTSP流: {self.rtsp_url}")
            logger.info(f"视频参数: {width}x{height} @ {fps}fps")
            
        except Exception as e:
            logger.error(f"启动RTSP捕获失败: {e}")
            raise
    
    async def recv(self):
        """接收视频帧"""
        if not self.cap or not self.cap.isOpened():
            raise Exception("RTSP流未连接")
            
        try:
            ret, frame = self.cap.read()
            if not ret:
                raise Exception("无法从RTSP流读取帧")
            
            # 转换帧格式为WebRTC支持的格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 创建WebRTC视频帧
            from av import VideoFrame
            video_frame = VideoFrame.from_ndarray(frame_rgb.astype(np.uint8), format="rgb24")
            
            # 设置时间戳
            pts = self.frame_count * 3000  # 30fps = 3000时间单位
            video_frame.pts = pts
            video_frame.time_base = Fraction(3000, 1000)
            
            self.frame_count += 1
            return video_frame
            
        except Exception as e:
            logger.error(f"接收视频帧失败: {e}")
            raise
    
    def __del__(self):
        """清理资源"""
        if self.cap:
            self.cap.release()

class WebRTCServer:
    """WebRTC媒体服务器"""
    
    def __init__(self):
        self.pcs: Dict[str, RTCPeerConnection] = {}
        self.active_streams: Dict[str, RTSPVideoStreamTrack] = {}
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
        
        # 设置路由
        self.setup_routes()
        
        # 为所有路由添加CORS支持
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def setup_routes(self):
        """设置路由 - 兼容前端API"""
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/api/offer', self.handle_offer)
        self.app.router.add_post('/api/stream/start', self.handle_stream_start)
        self.app.router.add_post('/api/stream/stop', self.handle_stream_stop)
        self.app.router.add_get('/api/devices', self.list_devices)
    
    async def index(self, request):
        """根路径"""
        return web.json_response({
            "message": "WebRTC RTSP Server",
            "version": "1.0.0",
            "endpoints": [
                "/health",
                "/api/offer",
                "/api/stream/start",
                "/api/stream/stop"
            ]
        })
    
    async def health_check(self, request):
        """健康检查"""
        return web.json_response({
            "status": "healthy",
            "timestamp": time.time(),
            "active_connections": len(self.pcs),
            "active_streams": len(self.active_streams)
        })
    
    async def handle_offer(self, request):
        """处理WebRTC offer"""
        try:
            data = await request.json()
            sdp = data.get('sdp')
            rtsp_url = data.get('rtsp_url')
            
            if not sdp or not rtsp_url:
                return web.json_response({
                    "error": "缺少必需的参数: sdp 和 rtsp_url"
                }, status=400)
            
            # 创建PeerConnection
            pc = RTCPeerConnection()
            pc_id = str(uuid.uuid4())
            self.pcs[pc_id] = pc
            
            # 创建RTSP视频轨道
            video_track = RTSPVideoStreamTrack(rtsp_url)
            self.active_streams[pc_id] = video_track
            
            # 添加视频轨道
            pc.addTrack(video_track)
            
            # 设置远程描述
            offer = RTCSessionDescription(sdp=sdp, type='offer')
            await pc.setRemoteDescription(offer)
            
            # 创建应答
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            
            logger.info(f"WebRTC连接建立成功: {pc_id}")
            
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
        """启动流 - 简化API"""
        try:
            data = await request.json()
            client_id = data.get('clientId', str(uuid.uuid4()))
            rtsp_url = data.get('rtsp_url')
            
            if not rtsp_url:
                return web.json_response({
                    "error": "缺少必需的参数: rtsp_url"
                }, status=400)
            
            # 测试RTSP连接
            logger.info(f"测试RTSP连接: {rtsp_url}")
            test_cap = cv2.VideoCapture(rtsp_url)
            
            if not test_cap.isOpened():
                return web.json_response({
                    "error": f"无法连接RTSP流: {rtsp_url}"
                }, status=500)
            
            # 获取视频信息
            width = int(test_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(test_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = test_cap.get(cv2.CAP_PROP_FPS)
            test_cap.release()
            
            logger.info(f"RTSP测试成功: {width}x{height} @ {fps}fps")
            
            return web.json_response({
                "success": True,
                "type": "answer",
                "stream_id": client_id,
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
    
    async def handle_stream_stop(self, request):
        """停止流"""
        try:
            data = await request.json()
            stream_id = data.get('stream_id')
            
            if stream_id and stream_id in self.pcs:
                await self.pcs[stream_id].close()
                del self.pcs[stream_id]
                
                if stream_id in self.active_streams:
                    del self.active_streams[stream_id]
                
                logger.info(f"停止流: {stream_id}")
            
            return web.json_response({
                "success": True,
                "message": "流已停止"
            })
            
        except Exception as e:
            logger.error(f"停止流失败: {e}")
            return web.json_response({
                "error": str(e)
            }, status=500)
    
    async def list_devices(self, request):
        """列出设备 - 占位符API"""
        return web.json_response({
            "devices": [
                {"id": "5", "name": "录像机一", "rtsp_url": "rtsp://admin:Chang168@192.168.42.85:55401/Streaming/Channels/101"},
                {"id": "6", "name": "录像机二", "rtsp_url": "rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101"},
                {"id": "16", "name": "录像机三", "rtsp_url": "rtsp://admin:Chang168@192.168.42.86:55501/Streaming/Channels/101"}
            ]
        })
    
    async def run(self, host='0.0.0.0', port=8090):
        """运行服务器"""
        logger.info(f"WebRTC RTSP服务器启动于 http://{host}:{port}")
        
        # 启动服务器
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info("服务器已启动，按Ctrl+C停止")
        
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """清理资源"""
        logger.info("正在清理资源...")
        
        # 关闭所有PeerConnection
        coros = [pc.close() for pc in self.pcs.values()]
        await asyncio.gather(*coros, return_exceptions=True)
        
        # 清理所有视频轨道
        self.active_streams.clear()
        self.pcs.clear()
        
        logger.info("清理完成")

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WebRTC RTSP服务器')
    parser.add_argument('--host', default='0.0.0.0', help='服务器地址')
    parser.add_argument('--port', type=int, default=8090, help='HTTP端口')
    
    args = parser.parse_args()
    
    server = WebRTCServer()
    await server.run(args.host, args.port)

if __name__ == '__main__':
    asyncio.run(main())