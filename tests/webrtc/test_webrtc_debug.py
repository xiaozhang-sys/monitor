#!/usr/bin/env python3
"""
WebRTC黑屏问题专项调试工具
用于诊断WebRTC连接成功但无画面的问题
"""

import asyncio
import json
import logging
import requests
import sys
import time
from datetime import datetime
import subprocess
import cv2

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebRTCBlackScreenDebugger:
    def __init__(self):
        self.webrtc_base_url = "http://localhost:8090"
        self.test_devices = [
            {
                "name": "录像机一",
                "rtsp_url": "rtsp://admin:Chang168@192.168.42.85:55401/Streaming/Channels/101"
            },
            {
                "name": "录像机二", 
                "rtsp_url": "rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101"
            }
        ]
    
    def check_webrtc_health(self):
        """检查WebRTC服务器健康状态"""
        try:
            response = requests.get(f"{self.webrtc_base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ WebRTC服务器健康: {health_data}")
                return True
            else:
                logger.error(f"❌ WebRTC服务器异常: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ WebRTC服务器连接失败: {e}")
            return False
    
    def test_rtsp_with_opencv(self, rtsp_url):
        """使用OpenCV直接测试RTSP流"""
        logger.info(f"正在测试RTSP流: {rtsp_url}")
        try:
            cap = cv2.VideoCapture(rtsp_url)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    height, width = frame.shape[:2]
                    logger.info(f"✅ OpenCV成功读取帧: {width}x{height}")
                    cap.release()
                    return True, f"{width}x{height}"
                else:
                    logger.error("❌ OpenCV无法读取帧")
                    cap.release()
                    return False, "无法读取帧"
            else:
                logger.error("❌ OpenCV无法打开RTSP流")
                return False, "无法打开流"
        except Exception as e:
            logger.error(f"❌ OpenCV测试失败: {e}")
            return False, str(e)
    
    def test_webrtc_stream_start(self, rtsp_url, device_name):
        """测试WebRTC流启动"""
        client_id = f"debug_{int(time.time())}"
        payload = {
            "clientId": client_id,
            "rtsp_url": rtsp_url
        }
        
        logger.info(f"正在启动WebRTC流: {device_name}")
        try:
            response = requests.post(
                f"{self.webrtc_base_url}/api/stream/start",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ WebRTC流启动成功: {result}")
                return True, result
            else:
                logger.error(f"❌ WebRTC流启动失败: {response.status_code} - {response.text}")
                return False, response.text
                
        except requests.exceptions.Timeout:
            logger.error("❌ WebRTC流启动超时")
            return False, "启动超时"
        except Exception as e:
            logger.error(f"❌ WebRTC流启动异常: {e}")
            return False, str(e)
    
    def check_stream_status(self, client_id):
        """检查流状态"""
        try:
            response = requests.get(f"{self.webrtc_base_url}/api/stream/status")
            if response.status_code == 200:
                status_data = response.json()
                logger.info(f"📊 流状态: {status_data}")
                return status_data
            else:
                logger.error(f"❌ 无法获取流状态: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ 获取流状态失败: {e}")
            return None
    
    def test_ffmpeg_rtsp(self, rtsp_url):
        """使用FFmpeg测试RTSP流"""
        logger.info(f"使用FFmpeg测试RTSP流: {rtsp_url}")
        cmd = [
            "ffmpeg", "-i", rtsp_url,
            "-vframes", "1", "-f", "image2",
            "-vcodec", "png", "-"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            if result.returncode == 0:
                logger.info("✅ FFmpeg成功读取RTSP流")
                return True, "FFmpeg读取成功"
            else:
                logger.error(f"❌ FFmpeg读取失败: {result.stderr.decode()}")
                return False, result.stderr.decode()
        except subprocess.TimeoutExpired:
            logger.error("❌ FFmpeg测试超时")
            return False, "测试超时"
        except Exception as e:
            logger.error(f"❌ FFmpeg测试异常: {e}")
            return False, str(e)
    
    def run_full_diagnosis(self):
        """运行完整诊断"""
        logger.info("🚀 开始WebRTC黑屏问题诊断")
        
        # 1. 检查WebRTC服务器
        print("\n" + "="*50)
        print("1. 检查WebRTC服务器状态")
        print("="*50)
        self.check_webrtc_health()
        
        # 2. 测试每个设备
        for device in self.test_devices:
            print(f"\n" + "="*50)
            print(f"2. 测试设备: {device['name']}")
            print("="*50)
            
            # RTSP流测试
            success, info = self.test_rtsp_with_opencv(device['rtsp_url'])
            if success:
                # WebRTC流测试
                webrtc_success, webrtc_info = self.test_webrtc_stream_start(
                    device['rtsp_url'], device['name']
                )
                
                if webrtc_success:
                    # 检查流状态
                    time.sleep(2)
                    self.check_stream_status(f"debug_{int(time.time())}")
            
            # FFmpeg测试
            self.test_ffmpeg_rtsp(device['rtsp_url'])
        
        print("\n" + "="*50)
        print("诊断完成！请查看日志分析结果")
        print("="*50)

if __name__ == "__main__":
    debugger = WebRTCBlackScreenDebugger()
    debugger.run_full_diagnosis()