#!/usr/bin/env python3
"""
HEVC到H264兼容WebRTC服务器(增强版)
解决HEVC编码视频无法在浏览器中显示的问题，并提升连接稳定性
"""

import asyncio
import logging
import json
import uuid
import signal
import sys
from typing import Dict, Optional, Set, Any, Tuple
import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, AudioStreamTrack
from aiortc.contrib.media import MediaPlayer
from aiortc.rtcrtpsender import RTCRtpSender
from aiohttp import web
from aiohttp.web import middleware
from aiohttp.web_request import Request
from aiohttp.web_response import Response
import aiohttp_cors
import threading
import time
from fractions import Fraction
import traceback
import av

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("webrtc_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 全局配置 - 扩展版
config = {
    # 连接稳定性配置
    "heartbeat_interval": 10,  # 心跳间隔（秒）
    "heartbeat_timeout": 30,   # 心跳超时时间（秒）
    "max_reconnect_attempts": 3,  # 最大重连次数
    "reconnect_base_delay": 1.0,  # 重连基础延迟（秒）
    "reconnect_max_delay": 10.0,  # 重连最大延迟（秒）
    "cleanup_interval": 60,      # 资源清理间隔（秒）
    "max_connections": 20,       # 最大并发连接数
    "enable_low_bitrate_fallback": True,  # 是否启用低码率模式
    
    # 媒体参数配置
    "rtsp_buffer_size": 10,  # RTSP缓冲区大小
    "frame_drop_threshold": 100,  # 帧丢弃阈值
    "low_bitrate": 500000,  # 低码率模式（bps）
    "normal_bitrate": 1000000,  # 正常码率（bps）
    "low_bitrate_resolution": (640, 480),  # 低码率模式分辨率
    "rtsp_transport": 'udp',  # udp或tcp传输
    "frame_timeout": 5.0,     # 帧处理超时时间（秒）
    
    # ICE服务器配置
    "ice_servers": [
        {'urls': ['stun:stun.l.google.com:19302']},
        {'urls': ['stun:stun1.l.google.com:19302']}
    ]
}

# 为保持兼容性，同时定义GLOBAL_CONFIG变量
GLOBAL_CONFIG = config

class H264CompatVideoStreamTrack(VideoStreamTrack):
    """
    将HEVC/H265视频流转换为H264兼容格式
    增强版：添加自动重连、帧率控制和更健壮的错误处理
    """
    
    def __init__(self, rtsp_url: str, max_reconnect_attempts: int = 3, low_bitrate_mode: bool = False):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.player = None
        self.frame_count = 0
        self.last_frame = None
        self.cap = None
        self.width = 640
        self.height = 480
        self.fps = 25.0
        self.reconnect_attempts = 0
        self.last_reconnect_time = 0
        self.last_frame_time = 0
        
        # 使用传入的参数或全局配置
        self.max_reconnect_attempts = max_reconnect_attempts if max_reconnect_attempts is not None else config['max_reconnect_attempts']
        self.low_bitrate_mode = low_bitrate_mode if low_bitrate_mode is not None else config['enable_low_bitrate_fallback']
        self.frame_interval = 1.0 / 25.0  # 默认25fps
        # 初始化时就设置低码率模式状态，用于支持子码流
        self.is_low_bitrate_mode = self.low_bitrate_mode
        self.frame_skip_count = 0
        self.error_count = 0
        
        # 添加RTSP传输参数和缓冲区设置
        self.rtsp_options = {
            'rtsp_transport': 'tcp',
            'buffer_size': config["rtsp_buffer_size"]
        }
        
        # 启动捕获
        self._start_capture()
        
    def _start_capture(self):
        """启动RTSP捕获，添加更健壮的连接参数"""
        try:
            # 先清理现有连接
            self._cleanup()
            
            # 使用更稳定的RTSP连接参数
            # 针对HEVC流添加特殊处理
            self.cap = cv2.VideoCapture()
            self.cap.open(
                self.rtsp_url,
                cv2.CAP_FFMPEG
            )
            
            # 设置更好的缓冲区参数
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.rtsp_options['buffer_size'])
            self.cap.set(cv2.CAP_PROP_FPS, 25)  # 限制帧率以提高稳定性
            
            if not self.cap.isOpened():
                raise Exception("无法打开RTSP流，请检查URL和网络连接")
                
            # 获取视频信息
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
            self.frame_interval = 1.0 / self.fps
            
            # 重置统计信息
            self.reconnect_attempts = 0
            self.error_count = 0
            self.last_frame_time = time.time()
            
            logger.info(f"RTSP连接成功: {self.width}x{self.height} @ {self.fps}fps, URL: {self.rtsp_url}")
            logger.info(f"RTSP参数: 缓冲区大小={self.rtsp_options['buffer_size']}, 传输协议={self.rtsp_options['rtsp_transport']}")
            
        except Exception as e:
            logger.error(f"RTSP连接失败: {e}")
            logger.debug(f"连接失败详情: {traceback.format_exc()}")
            # 自动重连逻辑
            self._handle_connection_error(e)
    
    def _handle_connection_error(self, error):
        """处理连接错误，实现智能重连"""
        current_time = time.time()
        
        # 限制重连频率，避免频繁重连
        if current_time - self.last_reconnect_time < 5:
            return
        
        self.reconnect_attempts += 1
        self.last_reconnect_time = current_time
        
        if self.reconnect_attempts <= config["max_reconnect_attempts"]:
            logger.info(f"尝试第{self.reconnect_attempts}/{config['max_reconnect_attempts']}次重连...")
            
            # 随着重连次数增加，使用更保守的设置
            if self.reconnect_attempts > 1:
                self.is_low_bitrate_mode = True
                logger.info("启用低码率模式以提高连接稳定性")
            
            # 延迟重连，避免立即重试
            time.sleep(2)
            self._start_capture()
        else:
            logger.error(f"达到最大重连次数({config['max_reconnect_attempts']})，请检查RTSP源和网络连接")
    
    async def recv(self):
        """获取视频帧，添加帧率控制和智能错误恢复"""
        try:
            # 帧率控制：确保帧间隔合理
            current_time = time.time()
            elapsed = current_time - self.last_frame_time
            
            if elapsed < self.frame_interval * 0.5:
                # 太快了，稍微等待一下
                await asyncio.sleep(self.frame_interval * 0.5 - elapsed)
            
            # 检查连接状态并尝试重连
            if not self.cap or not self.cap.isOpened():
                logger.warning("检测到断开的连接，尝试重新连接...")
                self._start_capture()
                
            # 读取帧
            ret, frame = False, None
            try:
                if self.cap and self.cap.isOpened():
                    ret, frame = self.cap.read()
            except Exception as read_error:
                logger.error(f"读取帧时发生异常: {read_error}")
                ret = False
            
            # 处理成功读取的帧
            if ret and frame is not None and frame.size > 0:
                # 帧率控制：根据重连状态决定是否丢帧
                if self.is_low_bitrate_mode:
                    # 低码率模式（子码流）下每3帧丢2帧，大幅降低帧率
                    if self.frame_skip_count % 3 != 0:
                        self.frame_skip_count += 1
                        if self.last_frame:
                            return self.last_frame
                    
                self.error_count = 0  # 重置错误计数
                self.last_frame_time = current_time
                
                # 转换为RGB格式
                try:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                except Exception as color_error:
                    logger.error(f"颜色转换失败: {color_error}")
                    # 使用灰度图作为备选
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    frame = cv2.merge([frame, frame, frame])  # 转换为RGB格式
                
                # 确保frame是正确的numpy数组类型
                frame = np.asarray(frame, dtype=np.uint8)
                
                # 低码率模式（子码流）下大幅降低分辨率
                if self.is_low_bitrate_mode:
                    # 子码流模式下将分辨率降低到原来的50%
                    new_width = int(self.width * 0.5)
                    new_height = int(self.height * 0.5)
                    # 确保尺寸为偶数，避免编解码问题
                    new_width = new_width if new_width % 2 == 0 else new_width - 1
                    new_height = new_height if new_height % 2 == 0 else new_height - 1
                    frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
                
                # 创建视频帧
                try:
                    video_frame = av.VideoFrame.from_ndarray(frame.astype(np.uint8), format='rgb24')
                    # 子码流模式下降低帧率
                    fps_divider = 3 if self.is_low_bitrate_mode else 1
                    video_frame.pts = self.frame_count * int(90000 / (self.fps * fps_divider))
                    video_frame.time_base = Fraction(1, 90000)
                    
                    self.frame_count += 1
                    self.frame_skip_count += 1
                    self.last_frame = video_frame  # 缓存最后一帧用于错误恢复
                    return video_frame
                except Exception as frame_error:
                    logger.error(f"创建视频帧失败: {frame_error}")
                    # 继续使用缓存帧或创建黑屏帧
            
            # 错误处理：增加错误计数并尝试恢复
            self.error_count += 1
            if self.error_count > 10:
                logger.warning("连续10帧读取失败，尝试重新连接...")
                self._start_capture()
            
            # 如果没有新帧，返回最后一帧或创建黑屏帧
            if self.last_frame is None:
                # 创建黑屏帧
                black_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                try:
                    self.last_frame = av.VideoFrame.from_ndarray(black_frame, format='rgb24')
                    self.last_frame.time_base = Fraction(1, 90000)
                except Exception as black_frame_error:
                    logger.error(f"创建黑屏帧失败: {black_frame_error}")
                    # 使用固定尺寸作为备选
                    fallback_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    self.last_frame = av.VideoFrame.from_ndarray(fallback_frame, format='rgb24')
                    self.last_frame.time_base = Fraction(1, 90000)
                
            return self.last_frame
            
        except Exception as e:
            logger.error(f"获取视频帧失败: {e}")
            logger.debug(f"异常详情: {traceback.format_exc()}")
            
            # 增加错误计数并尝试恢复
            self.error_count += 1
            if self.error_count > 5:
                self._start_capture()
            
            # 返回最后一帧或黑屏帧
            if self.last_frame:
                return self.last_frame
            
            # 创建黑屏帧作为最终备选
            black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            try:
                video_frame = av.VideoFrame.from_ndarray(black_frame, format='rgb24')
                video_frame.time_base = Fraction(1, 90000)
                return video_frame
            except Exception as final_error:
                logger.error(f"创建最终备选帧失败: {final_error}")
                # 抛出更友好的错误
                raise Exception("视频处理失败，但已启用自动恢复机制")
    
    def _cleanup(self):
        """清理资源"""
        try:
            logger.info(f"开始清理RTSP连接资源: {self.rtsp_url}")
            if self.cap is not None:
                try:
                    self.cap.release()
                    logger.info(f"成功释放VideoCapture对象: {self.rtsp_url}")
                except Exception as release_error:
                    logger.error(f"释放VideoCapture时出错: {release_error}")
                finally:
                    self.cap = None
            logger.info(f"视频捕获资源已成功释放: {self.rtsp_url}")
        except Exception as e:
            logger.error(f"释放视频捕获资源时出错: {e}")
    
    def __del__(self):
        """清理资源"""
        try:
            self._cleanup()
        except:
            pass  # 避免析构函数中的异常

class H264CompatAudioStreamTrack(AudioStreamTrack):
    """
    音频流轨道 - 从RTSP流中提取音频
    增强版：添加自动重连和更健壮的错误处理
    """
    
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
        self.reconnect_attempts = 0
        self.last_reconnect_time = 0
        self.error_count = 0
        self.audio_enabled = True
        
        # 音频选项配置
        self.audio_options = {
            'rtsp_transport': 'tcp',
            'buffer_size': 4096
        }
        
        self._setup_audio()
        
    def _setup_audio(self):
        """设置音频捕获，添加错误恢复机制"""
        try:
            # 先清理现有连接
            self._cleanup()
            
            # 记录重连信息
            current_time = time.time()
            if self.reconnect_attempts > 0:
                logger.info(f"音频重连尝试 #{self.reconnect_attempts}, RTSP URL: {self.rtsp_url}")
            
            # 使用更稳定的参数打开RTSP流
            try:
                self.container = av.open(
                    self.rtsp_url, 
                    options=self.audio_options,
                    timeout=5.0  # 添加超时设置
                )
            except Exception as open_error:
                logger.error(f"无法打开RTSP流获取音频: {open_error}")
                # 如果连续失败多次，暂时禁用音频以避免频繁重连
                self.error_count += 1
                if self.error_count > 3:
                    logger.warning("音频连接失败多次，暂时禁用音频以提高稳定性")
                    self.audio_enabled = False
                return
            
            # 重置错误计数
            self.error_count = 0
            
            # 查找音频流
            for stream in self.container.streams:
                if stream.type == 'audio':
                    try:
                        self.audio_stream = stream
                        # 通过codec_context获取音频参数
                        codec_context = stream.codec_context
                        self.sample_rate = getattr(codec_context, 'sample_rate', 48000)
                        self.channels = getattr(codec_context, 'channels', 1)
                        logger.info(f"音频流设置完成: {self.sample_rate}Hz, {self.channels}声道, 编码: {codec_context.codec.name}")
                        self.audio_enabled = True  # 成功找到音频流，启用音频
                        break
                    except Exception as stream_error:
                        logger.error(f"获取音频流信息失败: {stream_error}")
                        self.audio_stream = None
            
            if not self.audio_stream:
                logger.warning("RTSP流中未找到音频轨道或音频轨道无法访问")
                self.audio_enabled = False
            
        except Exception as e:
            logger.error(f"音频捕获设置失败: {e}")
            logger.debug(f"音频设置失败详情: {traceback.format_exc()}")
            # 处理连接错误
            self._handle_connection_error(e)
    
    def _handle_connection_error(self, error):
        """处理音频连接错误，实现智能重试"""
        current_time = time.time()
        
        # 限制重连频率
        if current_time - self.last_reconnect_time < 3:
            return
        
        self.reconnect_attempts += 1
        self.last_reconnect_time = current_time
        
        # 渐进退避策略
        wait_time = min(2 * self.reconnect_attempts, 10)
        logger.info(f"音频连接失败，{wait_time}秒后尝试重连...")
        
        # 使用线程延迟重连，避免阻塞主事件循环
        def delayed_reconnect():
            time.sleep(wait_time)
            try:
                self._setup_audio()
            except Exception as e:
                logger.error(f"延迟重连失败: {e}")
        
        if self.reconnect_attempts <= 5:  # 音频重连次数限制
            threading.Thread(target=delayed_reconnect, daemon=True).start()
        else:
            logger.warning(f"音频重连达到最大次数({self.reconnect_attempts})，暂时禁用音频")
            self.audio_enabled = False
            self.reconnect_attempts = 0  # 重置重连计数，稍后可能会重试
    
    async def recv(self) -> av.AudioFrame:
        """获取音频帧，增强错误处理"""
        try:
            # 如果音频被禁用，直接返回静默帧
            if not self.audio_enabled:
                return self._create_silent_frame()
            
            # 检查连接状态
            if not self.container or not self.audio_stream:
                # 尝试重新设置音频
                if time.time() - self.last_reconnect_time > 5:  # 避免频繁重连
                    self._setup_audio()
                return self._create_silent_frame()
            
            # 读取音频包，添加超时和错误处理
            try:
                # 如果容器或音频流为空，则返回静默帧
                if self.container is None or self.audio_stream is None:
                    return self._create_silent_frame()
                    
                # 使用异步超时控制
                async def read_audio_packet():
                    try:
                        # 这里使用非阻塞方式读取，避免阻塞事件循环
                        # 注意：av库的demux是同步的，我们需要在异步环境中小心处理
                        if self.container is not None and self.audio_stream is not None:
                            for packet in self.container.demux(self.audio_stream):
                                for frame in packet.decode():
                                    # 确保我们处理的是AudioFrame
                                    if isinstance(frame, av.AudioFrame):
                                        return frame
                    except Exception as e:
                        logger.error(f"音频解码异常: {e}")
                        return None
                    return None
                
                # 尝试读取音频帧，添加超时保护
                try:
                    frame = await asyncio.wait_for(
                        read_audio_packet(), 
                        timeout=0.1  # 100ms超时
                    )
                except asyncio.TimeoutError:
                    logger.warning("音频帧读取超时")
                    return self._create_silent_frame()
                
                # 如果成功获取到帧
                if frame is not None:
                    try:
                        # 转换为WebRTC兼容的格式（PCM 16位，48kHz）
                        # 检查是否需要重采样
                        format_name = getattr(frame.format, 'name', str(frame.format))
                        layout_name = getattr(frame.layout, 'name', str(frame.layout)) if hasattr(frame.layout, 'name') else str(frame.layout)
                        
                        if (frame.sample_rate != self.sample_rate or 
                            format_name != 's16' or 
                            layout_name != 'mono'):
                            try:
                                resampler = av.AudioResampler(
                                    format='s16',
                                    layout='mono',
                                    rate=self.sample_rate
                                )
                                resampled_frames = resampler.resample(frame)
                                if resampled_frames:
                                    audio_frame = resampled_frames[0]
                                else:
                                    raise Exception("重采样返回空帧")
                            except Exception as resample_error:
                                logger.error(f"音频重采样失败: {resample_error}")
                                return self._create_silent_frame()
                        else:
                            audio_frame = frame
                        
                        # 设置时间戳
                        audio_frame.pts = self.current_pts
                        audio_frame.time_base = Fraction(1, self.sample_rate)
                        
                        # 更新下一个时间戳
                        self.current_pts += audio_frame.samples
                        
                        # 重置错误计数
                        self.error_count = 0
                        return audio_frame
                    except Exception as process_error:
                        logger.error(f"处理音频帧失败: {process_error}")
                        self.error_count += 1
                else:
                    self.error_count += 1
            except Exception as e:
                logger.error(f"读取音频帧失败: {e}")
                logger.debug(f"音频读取异常详情: {traceback.format_exc()}")
                self.error_count += 1
                
                # 如果连续失败，尝试重新连接
                if self.error_count > 3:
                    self._setup_audio()
            
            # 返回静默帧
            return self._create_silent_frame()
            
        except Exception as e:
            logger.error(f"获取音频失败: {e}")
            logger.debug(f"音频处理异常详情: {traceback.format_exc()}")
            
            # 避免频繁重连
            if time.time() - self.last_reconnect_time > 2:
                self.error_count += 1
                if self.error_count > 5:
                    self._setup_audio()
            
            return self._create_silent_frame()
            
    def _create_silent_frame(self) -> av.AudioFrame:
        """创建静默音频帧"""
        # 创建48kHz, 16位, 单声道的静默帧
        frame = av.AudioFrame(format='s16', layout='mono', samples=self.frame_duration)
        frame.sample_rate = self.sample_rate
        frame.pts = self.current_pts
        frame.time_base = Fraction(1, self.sample_rate)
        
        # 填充静默数据
        buf = frame.to_ndarray()
        buf.fill(0)  # 静默
        
        # 更新时间戳
        self.current_pts += self.frame_duration
        
        return frame
        
    def _cleanup(self):
        """清理音频资源"""
        try:
            if self.container is not None:
                self.container.close()
                self.container = None
                self.audio_stream = None
        except Exception as e:
            logger.error(f"清理音频资源时出错: {e}")
            
    def __del__(self):
        """清理资源"""
        self._cleanup()

class H264CompatWebRTCServer:
    """
    H264兼容WebRTC服务器 - 增强版
    添加连接管理、心跳机制和资源监控
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8090):
        self.host = host
        self.port = port
        self.pcs: Dict[str, RTCPeerConnection] = {}  # PeerConnection字典
        self.tracks: Dict[str, H264CompatVideoStreamTrack] = {}  # 视频轨道字典
        self.audio_tracks: Dict[str, H264CompatAudioStreamTrack] = {}  # 音频轨道字典
        self.connection_metadata: Dict[str, Dict] = {}  # 连接元数据
        self.heartbeat_timers: Dict[str, float] = {}  # 心跳时间记录
        self.app = web.Application()
        self._setup_routes()
        self._setup_cors()
        self.runner: Optional[web.AppRunner] = None
        self.start_time = time.time()
        self.cleanup_task: Optional[asyncio.Task] = None
    
    def _setup_routes(self):
        """
        设置路由 - 增加心跳和统计接口
        """
        self.app.router.add_get("/health", self.health_check)
        self.app.router.add_post("/api/offer", self.handle_offer)
        self.app.router.add_post("/api/stream/start", self.start_stream)
        self.app.router.add_post("/api/stream/stop", self.stop_stream)
        self.app.router.add_post("/api/heartbeat", self.handle_heartbeat)
        self.app.router.add_get("/api/stats", self.get_stats)
    
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
    
    async def health_check(self, request: Request) -> Response:
        """
        健康检查 - 增强版
        返回详细的服务状态信息
        """
        try:
            # 统计连接状态
            healthy_connections = 0
            ice_states = {}
            current_time = time.time()
            
            for pc_id, pc in self.pcs.items():
                state = pc.iceConnectionState
                ice_states[state] = ice_states.get(state, 0) + 1
                if state in ['connected', 'completed']:
                    healthy_connections += 1
            
            # 检查是否有超时连接
            timeout_count = 0
            for pc_id, last_heartbeat in list(self.heartbeat_timers.items()):
                if current_time - last_heartbeat > GLOBAL_CONFIG['heartbeat_timeout']:
                    timeout_count += 1
            
            return web.json_response({
                "status": "healthy" if healthy_connections >= 0 else "degraded",
                "total_connections": len(self.pcs),
                "healthy_connections": healthy_connections,
                "ice_states": ice_states,
                "timeout_connections": timeout_count,
                "uptime": current_time - self.start_time,
                "timestamp": current_time,
                "version": "1.0.1"
            })
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            logger.debug(f"异常详情: {traceback.format_exc()}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_heartbeat(self, request: Request) -> Response:
        """
        处理客户端心跳
        用于检测连接活性和防止超时断开
        """
        try:
            params = await request.json()
            pc_id = params.get("pc_id")
            
            if not pc_id or pc_id not in self.pcs:
                return web.json_response({"error": "无效的连接ID"}, status=400)
            
            # 更新心跳时间
            self.heartbeat_timers[pc_id] = time.time()
            
            # 检查连接状态
            pc = self.pcs[pc_id]
            if pc.iceConnectionState in ['disconnected']:
                logger.warning(f"检测到连接 {pc_id} 状态为disconnected")
            
            return web.json_response({
                "status": "ok",
                "pc_id": pc_id,
                "connection_state": pc.iceConnectionState,
                "timestamp": time.time()
            })
            
        except Exception as e:
            logger.error(f"处理心跳请求失败: {e}")
            logger.debug(f"异常详情: {traceback.format_exc()}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_stats(self, request: Request) -> Response:
        """
        获取详细统计信息
        """
        try:
            current_time = time.time()
            connection_details = {}
            
            for pc_id, pc in self.pcs.items():
                details = {
                    "connection_state": pc.iceConnectionState,
                    "connection_time": current_time - self.connection_metadata.get(pc_id, {}).get('connected_at', current_time),
                    "last_heartbeat": current_time - self.heartbeat_timers.get(pc_id, current_time),
                    "rtsp_url": self.connection_metadata.get(pc_id, {}).get('rtsp_url', 'unknown')
                }
                connection_details[pc_id] = details
            
            return web.json_response({
                "total_connections": len(self.pcs),
                "uptime": current_time - self.start_time,
                "timestamp": current_time,
                "connection_details": connection_details,
                "system": {
                    "cpu_percent": psutil.cpu_percent(interval=0.1),
                    "memory_percent": psutil.virtual_memory().percent
                }
            })
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            logger.debug(f"异常详情: {traceback.format_exc()}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_offer(self, request: Request) -> Response:
        """
        处理WebRTC offer - 增强版
        添加更健壮的错误处理、连接管理和超时保护
        """
        pc_id = None
        
        try:
            params = await request.json()
            offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
            
            # 获取并记录RTSP URL
            rtsp_url = params.get("rtsp_url", "rtsp://admin:Chang168@192.168.42.85:55401/Streaming/Channels/101")
            # 获取码流类型参数，默认为主码流
            stream_type = params.get("stream_type", "main")
            logger.info(f"接收到WebRTC offer请求，RTSP URL: {rtsp_url}, 码流类型: {stream_type}")
            
            # 检查连接数限制
            if len(self.pcs) >= GLOBAL_CONFIG['max_connections']:
                logger.warning("连接数达到上限")
                return web.json_response({"error": "服务器连接数已达上限"}, status=503)
            
            # 使用优化的ICE服务器配置
            pc_config = {
                'iceServers': GLOBAL_CONFIG['ice_servers']
            }
            
            # 创建新的PeerConnection和唯一ID
            pc = RTCPeerConnection()
            pc_id = str(uuid.uuid4())
            logger.info(f"创建新的PeerConnection: {pc_id}")
            self.pcs[pc_id] = pc
            
            # 记录连接元数据
            self.connection_metadata[pc_id] = {
                'connected_at': time.time(),
                'rtsp_url': rtsp_url,
                'stream_type': stream_type,
                'last_state': 'new'
            }
            
            # 更新心跳时间
            self.heartbeat_timers[pc_id] = time.time()
            
            # ICE连接状态回调 - 增强版
            @pc.on("iceconnectionstatechange")
            async def on_iceconnectionstatechange():
                try:
                    state = pc.iceConnectionState
                    logger.info(f"ICE连接状态: {pc_id} -> {state}")
                    
                    # 更新元数据
                    self.connection_metadata[pc_id]['last_state'] = state
                    
                    # 处理不同状态
                    if state == "failed":
                        logger.warning(f"连接失败: {pc_id}")
                        await self._cleanup_connection(pc_id)
                    elif state == "disconnected":
                        logger.warning(f"连接断开: {pc_id}")
                        # 对于disconnected状态，等待一段时间看是否能恢复
                        asyncio.create_task(self._check_reconnection(pc_id, 5.0))
                    elif state == "closed":
                        logger.info(f"连接已关闭: {pc_id}")
                        await self._cleanup_connection(pc_id)
                    elif state in ['connected', 'completed']:
                        logger.info(f"连接成功建立: {pc_id}")
                except Exception as e:
                    logger.error(f"处理ICE连接状态变化时出错: {e}")
                    logger.debug(f"异常详情: {traceback.format_exc()}")
            
            # ICE候选者收集回调
            @pc.on("icegatheringstatechange")
            def on_icegatheringstatechange():
                try:
                    logger.debug(f"ICE收集状态: {pc_id} -> {pc.iceGatheringState}")
                except Exception as e:
                    logger.error(f"处理ICE收集状态时出错: {e}")
            
            @pc.on("track")
            async def on_track(track):
                logger.info(f"收到轨道: {track.kind}, ID: {track.id}")
                
                @track.on("ended")
                async def on_ended():
                    logger.info(f"媒体轨道结束: {track.kind}, ID: {track.id}")
            
            # 添加视频轨道 - 使用配置参数
            try:
                logger.info(f"正在为RTSP URL: {rtsp_url} 创建视频轨道")
                # 根据码流类型设置不同参数
                is_sub_stream = stream_type == "sub"
                video_track = H264CompatVideoStreamTrack(
                    rtsp_url,
                    max_reconnect_attempts=GLOBAL_CONFIG['max_reconnect_attempts'],
                    low_bitrate_mode=is_sub_stream or GLOBAL_CONFIG['enable_low_bitrate_fallback']
                )
                self.tracks[pc_id] = video_track
                logger.info(f"为连接 {pc_id} 成功创建视频轨道")
                
                # 将视频轨道添加到PeerConnection
                pc.addTrack(video_track)
                logger.info(f"视频轨道已添加到PeerConnection: {pc_id}")
                
                # 添加音频轨道
                try:
                    logger.info(f"正在为RTSP URL: {rtsp_url} 创建音频轨道")
                    audio_track = H264CompatAudioStreamTrack(rtsp_url)
                    self.audio_tracks[pc_id] = audio_track
                    pc.addTrack(audio_track)
                    logger.info(f"音频轨道已添加到PeerConnection: {pc_id}")
                except asyncio.TimeoutError:
                    logger.error(f"添加音频轨道超时")
                except Exception as audio_error:
                    logger.error(f"添加音频轨道失败: {audio_error}")
                    # 音频失败不影响视频
            except Exception as track_error:
                logger.error(f"创建或添加视频轨道失败: {track_error}")
                await self._cleanup_connection(pc_id)
                return web.json_response({"error": f"创建视频轨道失败: {str(track_error)}"}, status=500)
            
            try:
                # 设置远程描述 - 带超时保护
                await asyncio.wait_for(
                    pc.setRemoteDescription(offer),
                    timeout=10.0
                )
                
                # 创建应答 - 带超时保护
                answer = await asyncio.wait_for(
                    pc.createAnswer(),
                    timeout=10.0
                )
                
                # 设置本地描述 - 带超时保护
                await asyncio.wait_for(
                    pc.setLocalDescription(answer),
                    timeout=10.0
                )
                
                logger.info(f"WebRTC会话建立成功: {pc_id}")
                
                return web.json_response({
                    "sdp": pc.localDescription.sdp,
                    "type": pc.localDescription.type,
                    "pc_id": pc_id,
                    "heartbeat_interval": GLOBAL_CONFIG['heartbeat_interval']
                })
                
            except asyncio.TimeoutError:
                logger.error(f"WebRTC会话建立超时: {pc_id}")
                await self._cleanup_connection(pc_id)
                return web.json_response({"error": "WebRTC会话建立超时"}, status=504)
            except Exception as sdp_error:
                logger.error(f"处理SDP失败: {sdp_error}")
                await self._cleanup_connection(pc_id)
                return web.json_response({"error": f"处理SDP失败: {str(sdp_error)}"}, status=500)
            
        except Exception as e:
            logger.error(f"处理offer失败: {e}")
            logger.debug(f"异常详情: {traceback.format_exc()}")
            
            # 清理资源
            if pc_id:
                await self._cleanup_connection(pc_id)
            
            return web.json_response({"error": str(e)}, status=500)
    
    async def start_stream(self, request: Request) -> Response:
        """启动视频流"""
        cap = None
        try:
            params = await request.json()
            rtsp_url = params.get("rtsp_url")
            stream_type = params.get("stream_type", "main")
            logger.info(f"启动流请求，RTSP URL: {rtsp_url}, 码流类型: {stream_type}")
            
            if not rtsp_url:
                return web.json_response({"error": "需要RTSP URL"}, status=400)
            
            # 测试RTSP连接
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                # 确保即使打开失败也释放资源
                cap.release()
                return web.json_response({"error": "无法连接到RTSP流"}, status=500)
            
            # 获取视频信息
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            
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
            
            # 释放资源
            cap.release()
            
            return web.json_response({
                "success": True,
                "video_info": {
                    "width": width,
                    "height": height,
                    "fps": fps,
                    "rtsp_url": rtsp_url,
                    "codec": "h264_compatible"
                },
                "has_audio": has_audio
            })
            
        except Exception as e:
            logger.error(f"启动流失败: {e}")
            logger.debug(f"异常详情: {traceback.format_exc()}")
            # 确保释放资源
            if cap is not None:
                try:
                    cap.release()
                except Exception as release_error:
                    logger.error(f"释放视频捕获资源时出错: {release_error}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def stop_stream(self, request: Request) -> Response:
        """
        停止视频流 - 增强版
        """
        try:
            params = await request.json()
            pc_id = params.get("pc_id")
            
            if not pc_id:
                return web.json_response({"error": "缺少pc_id参数"}, status=400)
            
            # 调用统一的清理方法
            await self._cleanup_connection(pc_id)
            
            return web.json_response({
                "success": True,
                "message": "流已成功停止",
                "pc_id": pc_id,
                "timestamp": time.time()
            })
            
        except Exception as e:
            logger.error(f"停止流失败: {e}")
            logger.debug(f"异常详情: {traceback.format_exc()}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _cleanup_connection(self, pc_id: str):
        """
        统一的连接清理方法
        安全地清理所有相关资源
        """
        try:
            logger.info(f"开始清理连接资源: {pc_id}")
            
            # 清理PeerConnection
            if pc_id in self.pcs:
                pc = self.pcs[pc_id]
                try:
                    await asyncio.wait_for(pc.close(), timeout=5.0)
                    logger.info(f"PeerConnection已关闭: {pc_id}")
                except asyncio.TimeoutError:
                    logger.warning(f"关闭PeerConnection超时: {pc_id}")
                except Exception as e:
                    logger.error(f"关闭PeerConnection时出错: {e}")
                finally:
                    del self.pcs[pc_id]
            
            # 清理视频轨道
            if pc_id in self.tracks:
                track = self.tracks[pc_id]
                try:
                    if hasattr(track, '_cleanup'):
                        track._cleanup()
                except Exception as e:
                    logger.error(f"清理视频轨道时出错: {e}")
                finally:
                    del self.tracks[pc_id]
            
            # 清理音频轨道
            if pc_id in self.audio_tracks:
                audio_track = self.audio_tracks[pc_id]
                try:
                    if hasattr(audio_track, '_cleanup'):
                        audio_track._cleanup()
                except Exception as e:
                    logger.error(f"清理音频轨道时出错: {e}")
                finally:
                    del self.audio_tracks[pc_id]
            
            # 清理元数据
            if pc_id in self.connection_metadata:
                del self.connection_metadata[pc_id]
            
            # 清理心跳记录
            if pc_id in self.heartbeat_timers:
                del self.heartbeat_timers[pc_id]
            
            logger.info(f"连接资源清理完成: {pc_id}")
            
        except Exception as e:
            logger.error(f"清理连接资源时发生异常: {e}")
            logger.debug(f"异常详情: {traceback.format_exc()}")
    
    async def _check_reconnection(self, pc_id: str, wait_time: float = 5.0):
        """
        检查连接是否能够自动重连
        """
        await asyncio.sleep(wait_time)
        
        if pc_id in self.pcs:
            pc = self.pcs[pc_id]
            if pc.iceConnectionState == 'disconnected':
                logger.warning(f"连接 {pc_id} 在等待后仍为disconnected状态，清理资源")
                await self._cleanup_connection(pc_id)
    
    async def _periodic_cleanup(self):
        """
        定期清理任务
        清理超时连接和僵尸资源
        """
        while True:
            try:
                current_time = time.time()
                logger.debug("执行定期清理任务...")
                
                # 检查超时的连接
                for pc_id, last_heartbeat in list(self.heartbeat_timers.items()):
                    if current_time - last_heartbeat > GLOBAL_CONFIG['heartbeat_timeout']:
                        logger.warning(f"连接 {pc_id} 心跳超时，准备清理")
                        await self._cleanup_connection(pc_id)
                
                # 检查僵尸连接
                for pc_id, pc in list(self.pcs.items()):
                    if pc.iceConnectionState == 'closed':
                        logger.warning(f"发现僵尸连接: {pc_id}")
                        await self._cleanup_connection(pc_id)
                
                # 等待下一次清理
                await asyncio.sleep(GLOBAL_CONFIG['cleanup_interval'])
                
            except asyncio.CancelledError:
                logger.info("定期清理任务已取消")
                break
            except Exception as e:
                logger.error(f"定期清理任务执行失败: {e}")
                logger.debug(f"异常详情: {traceback.format_exc()}")
                # 出错后等待一段时间再重试
                await asyncio.sleep(10.0)
    
    async def cleanup(self) -> None:
        """
        清理所有资源 - 增强版
        """
        logger.info("正在清理所有资源...")
        try:
            # 取消定期清理任务
            if self.cleanup_task and not self.cleanup_task.done():
                try:
                    self.cleanup_task.cancel()
                    await asyncio.wait_for(self.cleanup_task, timeout=5.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    logger.warning("取消定期清理任务超时")
            
            # 关闭所有PeerConnection
            close_coros = []
            for pc in list(self.pcs.values()):
                try:
                    close_coros.append(asyncio.wait_for(pc.close(), timeout=3.0))
                except Exception as e:
                    logger.error(f"准备关闭PeerConnection时出错: {e}")
            
            if close_coros:
                results = await asyncio.gather(*close_coros, return_exceptions=True)
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"关闭PeerConnection时出现异常: {result}")
            
            # 清理所有视频轨道
            for track in list(self.tracks.values()):
                try:
                    if track and hasattr(track, '_cleanup'):
                        track._cleanup()
                except Exception as e:
                    logger.error(f"清理视频轨道时出错: {e}")
            
            # 清理所有音频轨道
            for audio_track in list(self.audio_tracks.values()):
                try:
                    if audio_track and hasattr(audio_track, '_cleanup'):
                        audio_track._cleanup()
                except Exception as e:
                    logger.error(f"清理音频轨道时出错: {e}")
            
            # 清空所有字典
            self.pcs.clear()
            self.tracks.clear()
            self.audio_tracks.clear()
            self.connection_metadata.clear()
            self.heartbeat_timers.clear()
            
            # 停止服务器
            if self.runner:
                try:
                    await asyncio.wait_for(self.runner.cleanup(), timeout=10.0)
                    logger.info("服务器运行器已清理")
                except asyncio.TimeoutError:
                    logger.warning("清理服务器运行器超时")
                except Exception as e:
                    logger.error(f"清理服务器运行器时出错: {e}")
            
            logger.info("资源清理完成")
        except Exception as e:
            logger.error(f"清理资源时出错: {e}")
            logger.debug(f"异常详情: {traceback.format_exc()}")

    def run(self) -> None:
        """
        运行服务器 - 增强版
        添加定期清理任务和优雅退出
        """
        logger.info(f"HEVC兼容WebRTC服务器启动于 http://{self.host}:{self.port}")
        logger.info(f"配置信息: 最大连接数={GLOBAL_CONFIG['max_connections']}, "
                   f"心跳间隔={GLOBAL_CONFIG['heartbeat_interval']}秒, "
                   f"清理间隔={GLOBAL_CONFIG['cleanup_interval']}秒")
        
        # 使用更优雅的方式启动和停止服务器
        async def run_server():
            # 启动定期清理任务
            self.cleanup_task = asyncio.create_task(self._periodic_cleanup())
            
            # 启动服务器
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            site = web.TCPSite(self.runner, self.host, self.port)
            await site.start()
            
            logger.info(f"服务器启动成功，监听地址: {self.host}:{self.port}")
            
            try:
                # 等待中断信号
                while True:
                    await asyncio.sleep(3600)  # 每小时检查一次
            except KeyboardInterrupt:
                logger.info("收到中断信号，正在关闭服务器...")
            except Exception as e:
                logger.error(f"服务器运行出错: {e}")
                logger.debug(f"异常详情: {traceback.format_exc()}")
            finally:
                await self.cleanup()
        
        try:
            asyncio.run(run_server())
        except KeyboardInterrupt:
            logger.info("服务器已关闭")
        except Exception as e:
            logger.error(f"启动服务器失败: {e}")
            logger.debug(f"异常详情: {traceback.format_exc()}")

def setup_signal_handlers():
    """
    设置信号处理器
    用于优雅地关闭服务器
    """
    def signal_handler(sig, frame):
        logger.info(f"收到信号 {sig}，准备关闭服务器...")
        sys.exit(0)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # 终止信号
    
    # Windows不支持SIGUSR1和SIGUSR2
    if sys.platform != 'win32':
        signal.signal(signal.SIGUSR1, signal_handler)  # 用户信号1
        signal.signal(signal.SIGUSR2, signal_handler)  # 用户信号2

if __name__ == "__main__":
    import argparse
    
    # 设置信号处理器
    setup_signal_handlers()
    
    parser = argparse.ArgumentParser(description="HEVC兼容WebRTC服务器")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8090, help="监听端口")
    parser.add_argument("--debug", action="store_true", help="启用调试日志模式")
    
    args = parser.parse_args()
    
    # 如果启用调试模式，设置日志级别为DEBUG
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.info("已启用调试日志模式")
    
    # 添加psutil到导入
    try:
        import psutil
        logger.info("成功导入系统监控模块psutil")
    except ImportError:
        logger.warning("未安装psutil模块，系统监控功能将受限")
    
    logger.info(f"正在启动HEVC兼容WebRTC服务器，监听地址: {args.host}:{args.port}")
    logger.info(f"配置信息: 心跳间隔={config['heartbeat_interval']}秒, "
                f"最大重连次数={config['max_reconnect_attempts']}, "
                f"最大连接数={config['max_connections']}")
    
    try:
        server = H264CompatWebRTCServer(host=args.host, port=args.port)
        server.run()
    except KeyboardInterrupt:
        logger.info("接收到键盘中断，正在优雅退出...")
    except Exception as e:
        logger.error(f"服务器异常退出: {str(e)}")
        logger.debug(f"异常详情: {traceback.format_exc()}")
        sys.exit(1)