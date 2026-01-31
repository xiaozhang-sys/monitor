#!/usr/bin/env python3
"""
直接测试RTSP流
验证RTSP流是否可访问
"""

import cv2
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rtsp_stream(rtsp_url, timeout=10):
    """测试RTSP流"""
    logger.info(f"正在测试RTSP流: {rtsp_url}")
    
    try:
        # 使用FFmpeg后端
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        
        if not cap.isOpened():
            logger.error("无法打开RTSP流")
            return False
        
        # 设置超时
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            ret, frame = cap.read()
            if ret:
                height, width = frame.shape[:2]
                logger.info(f"成功读取帧: {width}x{height}")
                cap.release()
                return True
            
            time.sleep(0.5)
        
        logger.error("读取帧超时")
        cap.release()
        return False
        
    except Exception as e:
        logger.error(f"测试RTSP流错误: {e}")
        return False

def test_all_devices():
    """测试所有设备"""
    devices = [
        {
            "name": "录像机一",
            "ip": "192.168.42.85",
            "port": 55401,
            "user": "admin",
            "pwd": "Chang168",
            "protocol": "rtsp"
        },
        {
            "name": "录像机二", 
            "ip": "192.168.42.86",
            "port": 55401,
            "user": "admin",
            "pwd": "Chang168",
            "protocol": "rtsp"
        }
    ]
    
    for device in devices:
        rtsp_url = f"rtsp://{device['user']}:{device['pwd']}@{device['ip']}:{device['port']}/Streaming/Channels/101"
        logger.info(f"\n测试设备: {device['name']}")
        
        success = test_rtsp_stream(rtsp_url)
        if success:
            logger.info(f"✅ {device['name']} - RTSP流正常")
        else:
            logger.error(f"❌ {device['name']} - RTSP流失败")

if __name__ == '__main__':
    test_all_devices()