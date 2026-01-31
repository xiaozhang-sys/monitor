#!/usr/bin/env python3
"""
检查RTSP流的编码格式和关键帧信息
"""

import cv2
import subprocess
import json
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_rtsp_info(rtsp_url):
    """使用ffprobe检查RTSP流信息"""
    try:
        # 使用ffprobe获取流信息
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_streams', '-select_streams', 'v:0',
            rtsp_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            info = json.loads(result.stdout)
            if 'streams' in info and len(info['streams']) > 0:
                stream = info['streams'][0]
                return {
                    'codec_name': stream.get('codec_name', 'unknown'),
                    'profile': stream.get('profile', 'unknown'),
                    'level': stream.get('level', 0),
                    'width': stream.get('width', 0),
                    'height': stream.get('height', 0),
                    'pix_fmt': stream.get('pix_fmt', 'unknown'),
                    'r_frame_rate': stream.get('r_frame_rate', '0/0'),
                    'gop_size': stream.get('gop_size', 0)
                }
        
        return None
        
    except Exception as e:
        logger.error(f"检查RTSP流失败: {e}")
        return None

def test_opencv_capture(rtsp_url):
    """测试OpenCV能否捕获RTSP流"""
    try:
        cap = cv2.VideoCapture(rtsp_url)
        
        if not cap.isOpened():
            logger.error("OpenCV无法打开RTSP流")
            return False
            
        # 读取几帧测试
        ret, frame = cap.read()
        if ret and frame is not None:
            height, width = frame.shape[:2]
            fps = cap.get(cv2.CAP_PROP_FPS)
            logger.info(f"OpenCV捕获成功: {width}x{height} @ {fps}fps")
            cap.release()
            return True
        else:
            logger.error("OpenCV无法读取帧")
            cap.release()
            return False
            
    except Exception as e:
        logger.error(f"OpenCV测试失败: {e}")
        return False

def main():
    """主函数"""
    # 测试公共RTSP流
    test_urls = [
        "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov",
        "rtsp://admin:admin123@192.168.1.100:554/h264/ch1/main/av_stream"  # 示例IPC地址
    ]
    
    for rtsp_url in test_urls:
        logger.info(f"\n=== 检查RTSP流: {rtsp_url} ===")
        
        # 检查编码信息
        codec_info = check_rtsp_info(rtsp_url)
        if codec_info:
            logger.info(f"编码格式: {codec_info['codec_name']} (profile: {codec_info['profile']})")
            logger.info(f"分辨率: {codec_info['width']}x{codec_info['height']}")
            logger.info(f"帧率: {codec_info['r_frame_rate']}")
            logger.info(f"像素格式: {codec_info['pix_fmt']}")
            
            # 检查是否WebRTC兼容
            if codec_info['codec_name'].lower() == 'h264':
                profile = codec_info['profile']
                if 'baseline' in str(profile).lower():
                    logger.info("✅ H264 Baseline - WebRTC兼容")
                elif 'main' in str(profile).lower():
                    logger.warning("⚠️ H264 Main - 可能兼容，建议转Baseline")
                elif 'high' in str(profile).lower():
                    logger.error("❌ H264 High - WebRTC不兼容，需要转码")
            elif codec_info['codec_name'].lower() in ['vp8', 'vp9', 'av1']:
                logger.info("✅ WebRTC原生支持")
            else:
                logger.error(f"❌ {codec_info['codec_name']} - WebRTC不支持，需要转码")
        
        # 测试OpenCV捕获
        test_opencv_capture(rtsp_url)

if __name__ == "__main__":
    main()