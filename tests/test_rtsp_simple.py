#!/usr/bin/env python3
"""
简化版RTSP流测试
"""

import cv2
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rtsp_stream(rtsp_url, timeout=10):
    """测试RTSP流"""
    logger.info(f"测试RTSP流: {rtsp_url}")
    
    try:
        cap = cv2.VideoCapture(rtsp_url)
        
        if not cap.isOpened():
            logger.error("❌ 无法打开RTSP流")
            return False
            
        # 获取视频信息
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        logger.info(f"视频信息: {width}x{height} @ {fps}fps")
        
        # 尝试读取几帧
        success_count = 0
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            ret, frame = cap.read()
            if ret and frame is not None:
                success_count += 1
                if success_count == 1:
                    logger.info(f"✅ 成功读取第1帧，形状: {frame.shape}")
                elif success_count == 5:
                    logger.info(f"✅ 成功读取5帧，RTSP流正常")
                    break
            else:
                logger.warning("⚠️ 读取帧失败")
                
        cap.release()
        
        if success_count > 0:
            logger.info(f"总计读取 {success_count} 帧")
            return True
        else:
            logger.error("❌ 无法读取任何帧")
            return False
            
    except Exception as e:
        logger.error(f"测试失败: {e}")
        return False

def main():
    """测试本地视频文件和RTSP流"""
    
    # 测试本地视频文件
    logger.info("=== 测试本地视频文件 ===")
    test_rtsp_stream("test_video.mp4")
    
    # 测试公共RTSP流
    logger.info("\n=== 测试公共RTSP流 ===")
    test_rtsp_stream("rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov")

if __name__ == "__main__":
    main()