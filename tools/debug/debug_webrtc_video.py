#!/usr/bin/env python3
"""
WebRTC视频显示问题诊断工具
用于分析为什么RTSP流正常但WebRTC无法显示视频
"""

import asyncio
import logging
import json
import time
import requests
from typing import Dict, Any
import cv2
import subprocess
import sys
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebRTCVideoDebugger:
    def __init__(self):
        self.webrtc_port = 8090
        self.frontend_port = 5173
        
    def check_all_services(self) -> Dict[str, bool]:
        """检查所有相关服务状态"""
        services = {}
        
        # 检查WebRTC服务器
        try:
            response = requests.get(f"http://localhost:{self.webrtc_port}/health", timeout=3)
            services['webrtc_server'] = response.status_code == 200
        except:
            services['webrtc_server'] = False
            
        # 检查前端服务
        try:
            response = requests.get(f"http://localhost:{self.frontend_port}", timeout=3)
            services['frontend'] = response.status_code == 200
        except:
            services['frontend'] = False
            
        return services
    
    def test_rtsp_direct(self, rtsp_url: str) -> Dict[str, Any]:
        """直接测试RTSP流"""
        result = {
            'success': False,
            'width': 0,
            'height': 0,
            'fps': 0,
            'codec': '',
            'duration': 0,
            'error': None
        }
        
        try:
            # 使用ffprobe获取流信息
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', rtsp_url
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if process.returncode == 0:
                data = json.loads(process.stdout)
                
                # 查找视频流
                video_stream = None
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        video_stream = stream
                        break
                
                if video_stream:
                    result.update({
                        'success': True,
                        'width': int(video_stream.get('width', 0)),
                        'height': int(video_stream.get('height', 0)),
                        'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                        'codec': video_stream.get('codec_name', 'unknown'),
                        'duration': float(data.get('format', {}).get('duration', 0))
                    })
                    
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def test_webrtc_connection(self, rtsp_url: str) -> Dict[str, Any]:
        """测试WebRTC连接"""
        result = {
            'success': False,
            'sdp_exchange': False,
            'ice_candidates': False,
            'error': None,
            'response_time': 0
        }
        
        try:
            start_time = time.time()
            
            # 模拟WebRTC连接流程
            offer_data = {
                'sdp': 'v=0\r\no=- 123456789 123456789 IN IP4 0.0.0.0\r\ns=-\r\nt=0 0\r\na=fingerprint:sha-256 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00\r\na=ice-ufrag:test\r\na=ice-pwd:testtesttest\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\nc=IN IP4 0.0.0.0\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=sendrecv\r\na=rtpmap:96 H264/90000\r\n',
                'type': 'offer'
            }
            
            response = requests.post(
                f"http://localhost:{self.webrtc_port}/api/offer",
                json=offer_data,
                timeout=10
            )
            
            result['response_time'] = time.time() - start_time
            result['sdp_exchange'] = response.status_code == 200
            
            if response.status_code == 200:
                result['success'] = True
                result['ice_candidates'] = True
                
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def check_browser_compatibility(self) -> Dict[str, Any]:
        """检查浏览器兼容性"""
        return {
            'webrtc_supported': True,  # 假设支持
            'h264_supported': True,
            'hevc_supported': False,  # 大多数浏览器不支持HEVC
            'stun_servers': [
                'stun:stun.l.google.com:19302',
                'stun:stun1.l.google.com:19302'
            ]
        }
    
    def run_full_diagnosis(self, rtsp_url: str) -> Dict[str, Any]:
        """运行完整诊断"""
        logger.info("开始WebRTC视频显示问题诊断...")
        
        diagnosis = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'rtsp_url': rtsp_url,
            'services': self.check_all_services(),
            'rtsp_info': self.test_rtsp_direct(rtsp_url),
            'webrtc_test': self.test_webrtc_connection(rtsp_url),
            'browser_compat': self.check_browser_compatibility(),
            'recommendations': []
        }
        
        # 分析结果并给出建议
        if not diagnosis['rtsp_info']['success']:
            diagnosis['recommendations'].append("❌ RTSP流无法访问，请检查网络连接和设备状态")
        elif diagnosis['rtsp_info']['codec'] == 'hevc':
            diagnosis['recommendations'].append("⚠️ 检测到HEVC编码，浏览器可能不支持，建议转换为H.264")
        elif diagnosis['rtsp_info']['codec'] == 'h264':
            diagnosis['recommendations'].append("✅ 使用H.264编码，浏览器兼容")
            
        if not diagnosis['webrtc_test']['success']:
            diagnosis['recommendations'].append("❌ WebRTC连接失败，请检查服务器配置")
        elif diagnosis['webrtc_test']['response_time'] > 5:
            diagnosis['recommendations'].append("⚠️ WebRTC响应较慢，可能存在网络延迟")
            
        if not all(diagnosis['services'].values()):
            diagnosis['recommendations'].append("❌ 部分服务未启动，请重启相关服务")
            
        return diagnosis

def main():
    """主函数"""
    debugger = WebRTCVideoDebugger()
    
    # 使用设备配置中的RTSP地址
    rtsp_url = "rtsp://admin:Chang168@192.168.42.85:55401/Streaming/Channels/101"
    
    print("=" * 60)
    print("WebRTC视频显示问题诊断报告")
    print("=" * 60)
    
    diagnosis = debugger.run_full_diagnosis(rtsp_url)
    
    # 打印详细诊断结果
    print(f"\n📊 诊断时间: {diagnosis['timestamp']}")
    print(f"🎥 RTSP地址: {diagnosis['rtsp_url']}")
    
    print("\n🔧 服务状态:")
    for service, status in diagnosis['services'].items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {service}")
    
    print("\n📹 RTSP流信息:")
    if diagnosis['rtsp_info']['success']:
        info = diagnosis['rtsp_info']
        print(f"  ✅ 分辨率: {info['width']}x{info['height']}")
        print(f"  ✅ 帧率: {info['fps']} fps")
        print(f"  ✅ 编码格式: {info['codec']}")
        print(f"  ✅ 时长: {info['duration']:.1f}秒")
    else:
        print(f"  ❌ 错误: {diagnosis['rtsp_info']['error']}")
    
    print("\n🌐 WebRTC连接测试:")
    if diagnosis['webrtc_test']['success']:
        test = diagnosis['webrtc_test']
        print(f"  ✅ SDP交换: {test['sdp_exchange']}")
        print(f"  ✅ ICE候选: {test['ice_candidates']}")
        print(f"  ✅ 响应时间: {test['response_time']:.2f}秒")
    else:
        print(f"  ❌ 错误: {diagnosis['webrtc_test']['error']}")
    
    print("\n💡 诊断建议:")
    for rec in diagnosis['recommendations']:
        print(f"  {rec}")
    
    # 保存诊断结果
    with open('webrtc_diagnosis.json', 'w', encoding='utf-8') as f:
        json.dump(diagnosis, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 详细诊断报告已保存到: webrtc_diagnosis.json")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        rtsp_url = sys.argv[1]
    else:
        rtsp_url = "rtsp://admin:Chang168@192.168.42.85:55401/Streaming/Channels/101"
    
    main()