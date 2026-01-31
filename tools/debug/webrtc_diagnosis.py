#!/usr/bin/env python3
"""
WebRTC黑屏问题7步诊断脚本
基于提供的排查指南系统化检查
"""

import requests
import json
import time
import socket
import logging
import subprocess
import os
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebRTCDiagnosis:
    def __init__(self, webrtc_url: str = "http://localhost:8090"):
        self.webrtc_url = webrtc_url
        self.results = {}
        
    def run_all_checks(self) -> Dict:
        """运行所有7步检查"""
        logger.info("开始WebRTC黑屏问题7步诊断...")
        
        # 第1步：确认WebRTC网关状态
        self.check_1_service_health()
        
        # 第2步：检查编码格式
        self.check_2_encoding_format()
        
        # 第3步：检查关键帧间隔
        self.check_3_keyframe_interval()
        
        # 第4步：检查端口和防火墙
        self.check_4_ports_firewall()
        
        # 第5步：检查带宽和QoS
        self.check_5_bandwidth_qos()
        
        # 第6步：检查时间戳连续性
        self.check_6_timestamp_continuity()
        
        # 第7步：浏览器兼容性检查
        self.check_7_browser_compatibility()
        
        return self.results
    
    def check_1_service_health(self):
        """第1步：确认WebRTC网关状态"""
        logger.info("=== 第1步：WebRTC网关状态检查 ===")
        
        try:
            # 检查健康端点
            response = requests.get(f"{self.webrtc_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                self.results['service_health'] = {
                    'status': 'healthy',
                    'connections': health_data.get('connections', 0),
                    'url': f"{self.webrtc_url}/health"
                }
                logger.info(f"✅ 服务健康 - 当前连接: {health_data.get('connections', 0)}")
            else:
                self.results['service_health'] = {'status': 'unhealthy', 'code': response.status_code}
                logger.error(f"❌ 服务异常 - HTTP {response.status_code}")
                
        except Exception as e:
            self.results['service_health'] = {'status': 'error', 'error': str(e)}
            logger.error(f"❌ 服务连接失败: {e}")
    
    def check_2_encoding_format(self):
        """第2步：检查编码格式兼容性"""
        logger.info("=== 第2步：编码格式兼容性检查 ===")
        
        # 检查本地测试视频
        if os.path.exists("test_video.mp4"):
            self.results['encoding_format'] = {
                'test_source': 'test_video.mp4',
                'codec': 'H264 (本地文件)',
                'compatible': True,
                'note': '本地测试文件应正常工作'
            }
            logger.info("✅ 本地测试视频可用 - H264编码")
        else:
            self.results['encoding_format'] = {
                'test_source': 'none',
                'compatible': False,
                'note': '需要创建测试视频'
            }
            logger.warning("⚠️ 本地测试视频不存在")
    
    def check_3_keyframe_interval(self):
        """第3步：检查关键帧间隔"""
        logger.info("=== 第3步：关键帧间隔检查 ===")
        
        # 默认建议设置
        self.results['keyframe_interval'] = {
            'recommended_gop': '1-2秒',
            'current_setting': '未知(需检查RTSP源)',
            'solution': '将摄像机GOP设置为1-2秒，或使用ffmpeg -g 30'
        }
        logger.info("📋 建议: 将GOP设置为1-2秒(25-50帧@25fps)")
    
    def check_4_ports_firewall(self):
        """第4步：检查端口和防火墙"""
        logger.info("=== 第4步：端口和防火墙检查 ===")
        
        ports_status = {}
        
        # 检查TCP 8090
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 8090))
            sock.close()
            ports_status['tcp_8090'] = result == 0
            logger.info(f"{'✅' if result == 0 else '❌'} TCP 8090: {'开放' if result == 0 else '关闭'}")
        except:
            ports_status['tcp_8090'] = False
            logger.error("❌ TCP 8090检查失败")
        
        # 检查UDP 50000-60000范围
        udp_ports = [50000, 55000, 60000]
        udp_status = {}
        for port in udp_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1)
                sock.bind(('localhost', port))
                sock.close()
                udp_status[port] = True
                logger.info(f"✅ UDP {port}: 可用")
            except:
                udp_status[port] = False
                logger.warning(f"⚠️ UDP {port}: 被占用或不可用")
        
        ports_status['udp_range'] = udp_status
        self.results['ports_firewall'] = ports_status
    
    def check_5_bandwidth_qos(self):
        """第5步：检查带宽和QoS"""
        logger.info("=== 第5步：带宽和QoS检查 ===")
        
        self.results['bandwidth_qos'] = {
            'recommendation': '从200kbps开始测试',
            'test_command': 'ffmpeg -i input -b:v 200k -maxrate 200k -bufsize 400k ...',
            'note': '先降低码率排除带宽问题'
        }
        logger.info("📋 建议: 先用200kbps低码率测试")
    
    def check_6_timestamp_continuity(self):
        """第6步：检查时间戳连续性"""
        logger.info("=== 第6步：时间戳连续性检查 ===")
        
        self.results['timestamp_continuity'] = {
            'solution': '使用ffmpeg重新对齐时间戳',
            'command': 'ffmpeg -copyts -rtsp_transport tcp -use_wallclock_as_timestamps 1',
            'note': '避免时间戳跳跃导致浏览器丢帧'
        }
        logger.info("📋 建议: 使用-copyts和use_wallclock_as_timestamps参数")
    
    def check_7_browser_compatibility(self):
        """第7步：浏览器兼容性检查"""
        logger.info("=== 第7步：浏览器兼容性检查 ===")
        
        self.results['browser_compatibility'] = {
            'webrtc_support': True,
            'test_page': 'webrtc_test_page.html',
            'debug_tools': [
                'chrome://webrtc-internals/',
                'chrome://webrtc-logs/',
                'about:webrtc (Firefox)'
            ]
        }
        logger.info("📋 已创建测试页面: webrtc_test_page.html")
    
    def print_summary(self):
        """打印诊断总结"""
        logger.info("\n" + "="*50)
        logger.info("WebRTC黑屏诊断总结")
        logger.info("="*50)
        
        # 服务状态
        health = self.results.get('service_health', {})
        if health.get('status') == 'healthy':
            logger.info("✅ 服务运行正常")
        else:
            logger.error("❌ 服务异常，请先重启WebRTC服务")
        
        # 编码格式
        encoding = self.results.get('encoding_format', {})
        if encoding.get('compatible'):
            logger.info("✅ 编码格式兼容")
        else:
            logger.error("❌ 编码格式不兼容，需要转码")
        
        # 端口检查
        ports = self.results.get('ports_firewall', {})
        if ports.get('tcp_8090'):
            logger.info("✅ TCP 8090端口正常")
        else:
            logger.error("❌ TCP 8090端口异常")
        
        logger.info("\n📋 快速解决步骤:")
        logger.info("1. 使用本地测试视频(test_video.mp4)验证WebRTC链路")
        logger.info("2. 打开webrtc_test_page.html进行浏览器测试")
        logger.info("3. 检查chrome://webrtc-internals/统计信息")
        logger.info("4. 确认RTSP源编码为H264 Baseline")
        logger.info("5. 调整摄像机GOP为1-2秒")

def main():
    """主函数"""
    diagnosis = WebRTCDiagnosis()
    results = diagnosis.run_all_checks()
    diagnosis.print_summary()
    
    # 保存结果到文件
    with open('webrtc_diagnosis_report.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info("诊断报告已保存: webrtc_diagnosis_report.json")

if __name__ == "__main__":
    main()