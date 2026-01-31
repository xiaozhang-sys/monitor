#!/usr/bin/env python3
"""
简化版WebRTC服务器 - 解决HEVC兼容性问题
使用aiortc的标准媒体处理
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, Optional, Tuple
import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, AudioStreamTrack
from aiortc.contrib.media import MediaPlayer
from aiortc.mediastreams import MediaStreamError
from aiohttp import web
import aiohttp_cors
import time
from fractions import Fraction
import av

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleVideoStreamTrack(VideoStreamTrack):
    """简化的视频流轨道"""
    
    kind = "video"
    
    def __init__(self, rtsp_url: str):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.cap = None
        self.frame_count = 0
        self._setup_capture()
    
    def _setup_capture(self):
        """设置视频捕获"""
        try:
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            if not self.cap.isOpened():
                raise Exception("无法打开RTSP流")
            
            # 获取视频信息
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
            
            logger.info(f"视频捕获设置完成: {self.width}x{self.height} @ {self.fps}fps")
            
        except Exception as e:
            logger.error(f"视频捕获设置失败: {e}")
            # 创建默认黑屏
            self.width = 640
            self.height = 480
            self.fps = 25.0
    
    async def recv(self):
        """获取视频帧"""
        try:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                
                if ret and frame is not None:
                    # 转换颜色空间
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # 使用av库创建视频帧
                    try:
                        # 确保frame是uint8类型
                        if frame.dtype != np.uint8:
                            frame = frame.astype(np.uint8)
                        # 确保frame是正确的numpy数组类型
                        frame = np.asarray(frame, dtype=np.uint8)
                        video_frame = av.VideoFrame.from_ndarray(frame, format='rgb24')
                        video_frame.pts = self.frame_count * int(90000 / self.fps)
                        video_frame.time_base = Fraction(1, 90000)
                        
                        self.frame_count += 1
                        return video_frame
                        
                    except Exception as e:
                        logger.error(f"创建视频帧失败: {e}")
                        # 返回黑屏帧
                        black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                        video_frame = av.VideoFrame.from_ndarray(black_frame, format='rgb24')
                        video_frame.pts = self.frame_count * 3000
                        video_frame.time_base = Fraction(1, 90000)
                        self.frame_count += 1
                        return video_frame
            
            # 返回黑屏帧
            black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            video_frame = av.VideoFrame.from_ndarray(black_frame, format='rgb24')
            video_frame.pts = self.frame_count * 3000
            video_frame.time_base = Fraction(1, 90000)
            
            self.frame_count += 1
            return video_frame
            
        except Exception as e:
            logger.error(f"获取帧失败: {e}")
            # 返回黑屏
            black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            video_frame = av.VideoFrame.from_ndarray(black_frame, format='rgb24')
            video_frame.time_base = Fraction(1, 90000)
            return video_frame
    
    def __del__(self):
        """清理"""
        if self.cap:
            self.cap.release()

class SimpleAudioStreamTrack(AudioStreamTrack):
    """简化的音频流轨道"""
    
    kind = "audio"
    
    def __init__(self, rtsp_url: str):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.container = None
        self.audio_stream = None
        self.sample_rate = 48000  # WebRTC推荐的采样率
        self.channels = 1
        self.frame_duration = 960  # 20ms at 48kHz
        self.current_pts = 0
        self._setup_audio()
    
    def _setup_audio(self):
        """设置音频捕获"""
        try:
            # 使用av库直接打开RTSP流获取音频
            self.container = av.open(self.rtsp_url, options={'rtsp_transport': 'tcp'})
            
            # 查找音频流
            for stream in self.container.streams:
                if stream.type == 'audio':
                    self.audio_stream = stream
                    # 通过codec_context获取音频参数
                    codec_context = stream.codec_context
                    self.sample_rate = getattr(codec_context, 'sample_rate', 48000)
                    self.channels = getattr(codec_context, 'channels', 1)
                    logger.info(f"音频流设置完成: {self.sample_rate}Hz, {self.channels}声道, 编码: {codec_context.codec.name}")
                    break
            
            if not self.audio_stream:
                logger.warning("RTSP流中未找到音频轨道")
            
        except Exception as e:
            logger.error(f"音频捕获设置失败: {e}")
            self.container = None
    
    async def recv(self) -> av.AudioFrame:
        """获取音频帧"""
        try:
            if not self.container or not self.audio_stream:
                # 创建静默音频帧
                return self._create_silent_frame()
            
            # 读取音频包
            try:
                for packet in self.container.demux(self.audio_stream):
                    for frame in packet.decode():
                        # 确保我们处理的是AudioFrame而不是SubtitleSet
                        if not isinstance(frame, av.AudioFrame):
                            continue
                            
                        # 转换为WebRTC兼容的格式（PCM 16位，48kHz）
                        audio_frame = frame
                        
                        # 如果采样率不是48kHz，重采样
                        if frame.sample_rate != self.sample_rate:
                            resampler = av.AudioResampler(
                                format='s16',
                                layout='mono',
                                rate=self.sample_rate
                            )
                            audio_frame = resampler.resample(frame)[0]
                        
                        # 设置时间戳
                        audio_frame.pts = self.current_pts
                        audio_frame.time_base = Fraction(1, self.sample_rate)
                        
                        # 更新下一个时间戳
                        self.current_pts += audio_frame.samples
                        
                        return audio_frame
            except Exception as e:
                logger.error(f"读取音频帧失败: {e}")
                # 重新设置音频捕获
                self._setup_audio()
            
            # 返回静默帧
            return self._create_silent_frame()
            
        except Exception as e:
            logger.error(f"获取音频失败: {e}")
            return self._create_silent_frame()
    
    def _create_silent_frame(self):
        """创建静默音频帧"""
        # 创建音频帧
        frame = av.AudioFrame(format='s16', layout='mono', samples=self.frame_duration)
        frame.sample_rate = self.sample_rate
        frame.pts = self.current_pts
        frame.time_base = Fraction(1, self.sample_rate)
        
        # 填充静默数据
        for plane in frame.planes:
            plane.update(b'\x00' * plane.buffer_size)
        
        self.current_pts += self.frame_duration
        
        return frame
    
    def __del__(self):
        """清理"""
        if self.container:
            self.container.close()

class SimpleWebRTCServer:
    """简化版WebRTC服务器"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8090):
        self.host = host
        self.port = port
        self.pcs: Dict[str, RTCPeerConnection] = {}
        self.app = web.Application()
        self._setup_routes()
        self._setup_cors()
    
    def _setup_routes(self):
        """设置路由"""
        self.app.router.add_get("/health", self.health_check)
        self.app.router.add_post("/api/offer", self.handle_offer)
        self.app.router.add_post("/api/stream/start", self.start_stream)
        self.app.router.add_post("/api/stream/stop", self.stop_stream)
    
    def _setup_cors(self):
        """设置CORS"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def health_check(self, request):
        """健康检查"""
        return web.json_response({
            "status": "healthy",
            "connections": len(self.pcs),
            "timestamp": time.time()
        })
    
    async def handle_offer(self, request):
        """处理offer"""
        try:
            params = await request.json()
            offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
            
            pc = RTCPeerConnection()
            pc_id = str(uuid.uuid4())
            self.pcs[pc_id] = pc
            
            @pc.on("iceconnectionstatechange")
            async def on_iceconnectionstatechange():
                logger.info(f"ICE状态: {pc.iceConnectionState}")
                if pc.iceConnectionState == "failed":
                    await pc.close()
                    del self.pcs[pc_id]
            
            # 添加视频轨道和音频轨道
            rtsp_url = params.get("rtsp_url", "")
            if rtsp_url:
                try:
                    # 添加视频轨道
                    video_track = SimpleVideoStreamTrack(rtsp_url)
                    pc.addTrack(video_track)
                    logger.info(f"添加视频轨道: {rtsp_url}")
                except Exception as e:
                    logger.error(f"添加视频轨道失败: {e}")
                
                try:
                    # 添加音频轨道
                    audio_track = SimpleAudioStreamTrack(rtsp_url)
                    pc.addTrack(audio_track)
                    logger.info(f"添加音频轨道: {rtsp_url}")
                except Exception as e:
                    logger.error(f"添加音频轨道失败: {e}")
            
            await pc.setRemoteDescription(offer)
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            
            return web.json_response({
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type,
                "pc_id": pc_id
            })
            
        except Exception as e:
            logger.error(f"处理offer失败: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def start_stream(self, request):
        """启动流"""
        try:
            params = await request.json()
            rtsp_url = params.get("rtsp_url")
            
            if not rtsp_url:
                return web.json_response({"error": "需要RTSP URL"}, status=400)
            
            # 测试RTSP连接
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                return web.json_response({"error": "无法连接RTSP流"}, status=500)
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            cap.release()
            
            # 检查音频
            has_audio = False
            try:
                container = av.open(rtsp_url, options={'rtsp_transport': 'tcp'})
                for stream in container.streams:
                    if stream.type == 'audio':
                        has_audio = True
                        codec_context = stream.codec_context
                        sample_rate = getattr(codec_context, 'sample_rate', 0)
                        channels = getattr(codec_context, 'channels', 0)
                        logger.info(f"检测到音频流: {codec_context.codec.name}, {sample_rate}Hz, {channels}声道")
                        break
                container.close()
            except Exception as e:
                logger.error(f"检查音频流失败: {e}")
            
            return web.json_response({
                "success": True,
                "video_info": {
                    "width": width,
                    "height": height,
                    "fps": fps,
                    "rtsp_url": rtsp_url
                },
                "has_audio": has_audio
            })
            
        except Exception as e:
            logger.error(f"启动流失败: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def stop_stream(self, request):
        """停止流"""
        try:
            params = await request.json()
            pc_id = params.get("pc_id")
            
            if pc_id in self.pcs:
                await self.pcs[pc_id].close()
                del self.pcs[pc_id]
                
            return web.json_response({"success": True})
            
        except Exception as e:
            logger.error(f"停止流失败: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    def run(self):
        """运行服务器"""
        logger.info(f"简化版WebRTC服务器启动于 http://{self.host}:{self.port}")
        web.run_app(self.app, host=self.host, port=self.port)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="简化版WebRTC服务器")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8090, help="监听端口")
    
    args = parser.parse_args()
    
    server = SimpleWebRTCServer(host=args.host, port=args.port)
    server.run()