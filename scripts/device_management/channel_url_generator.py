#!/usr/bin/env python3
"""
多品牌录像机通道URL生成器
支持多种品牌的通道地址格式
"""

import sqlite3
import json
from datetime import datetime

class ChannelURLGenerator:
    """通道URL生成器"""
    
    # 品牌对应的URL格式
    BRAND_FORMATS = {
        'brand_a': {
            'rtsp': 'rtsp://{username}:{password}@{ip}:{port}/Streaming/Channels/{channel}01',
            'http': 'http://{ip}:{port}/ISAPI/Streaming/channels/{channel}01',
            'https': 'https://{ip}:{port}/ISAPI/Streaming/channels/{channel}01'
        },
        'brand_b': {
            'rtsp': 'rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0',
            'http': 'http://{ip}:{port}/cgi-bin/snapshot.cgi?channel={channel}',
            'https': 'https://{ip}:{port}/cgi-bin/snapshot.cgi?channel={channel}'
        },
        'brand_c': {
            'rtsp': 'rtsp://{username}:{password}@{ip}:{port}/media/video{channel}',
            'http': 'http://{ip}:{port}/media/video{channel}',
            'https': 'https://{ip}:{port}/media/video{channel}'
        },
        'brand_d': {
            'rtsp': 'rtsp://{username}:{password}@{ip}:{port}/user=admin&password=&channel={channel}&stream=0.sdp',
            'http': 'http://{ip}:{port}/cgi-bin/snapshot.cgi?chn={channel}',
            'https': 'https://{ip}:{port}/cgi-bin/snapshot.cgi?chn={channel}'
        }
    }
    
    def __init__(self, db_path='backend/data/devices.db'):
        self.db_path = db_path
    
    def generate_channel_url(self, device, channel_num, stream_type='main'):
        """
        生成指定通道的URL
        
        Args:
            device: 设备信息字典
            channel_num: 通道号(1-16)
            stream_type: 码流类型('main'主码流, 'sub'子码流)
        
        Returns:
            dict: 包含不同协议的URL
        """
        
        brand = device.get('brand', 'brand_a')
        protocol = device.get('protocol', 'rtsp')
        
        # 根据码流类型调整通道号
        if stream_type == 'sub':
            channel_code = f"{channel_num}02"  # 子码流
        else:
            channel_code = f"{channel_num}01"  # 主码流
        
        # 获取URL格式
        format_dict = self.BRAND_FORMATS.get(brand, self.BRAND_FORMATS['brand_a'])
        
        # 生成URL
        url_template = format_dict.get(protocol, format_dict['rtsp'])
        
        url = url_template.format(
            username=device.get('username', 'admin'),
            password=device.get('password', 'password'),
            ip=device.get('ip', '127.0.0.1'),
            port=device.get('port', 554),
            channel=channel_code,
            channel_num=channel_num
        )
        
        return {
            'brand': brand,
            'protocol': protocol,
            'channel': channel_num,
            'stream_type': stream_type,
            'url': url,
            'main_url': self.generate_single_url(device, channel_num, 'main'),
            'sub_url': self.generate_single_url(device, channel_num, 'sub')
        }
    
    def generate_single_url(self, device, channel_num, stream_type):
        """生成单个URL"""
        brand = device.get('brand', 'brand_a')
        protocol = device.get('protocol', 'rtsp')
        
        if stream_type == 'sub':
            channel_code = f"{channel_num}02"
        else:
            channel_code = f"{channel_num}01"
        
        format_dict = self.BRAND_FORMATS.get(brand, self.BRAND_FORMATS['brand_a'])
        url_template = format_dict.get(protocol, format_dict['rtsp'])
        
        return url_template.format(
            username=device.get('username', 'admin'),
            password=device.get('password', 'password'),
            ip=device.get('ip', '127.0.0.1'),
            port=device.get('port', 554),
            channel=channel_code,
            channel_num=channel_num
        )
    
    def generate_all_channels(self, device_id):
        """生成设备的所有通道URL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
        device = cursor.fetchone()
        
        if not device:
            conn.close()
            return None
        
        # 转换为字典
        device_dict = {
            'id': device[0],
            'name': device[1],
            'ip': device[2],
            'port': device[3],
            'username': device[4],
            'password': device[5],
            'protocol': device[6],
            'chs': device[7],
            'brand': 'brand_a'  # 默认品牌
        }
        
        channels = []
        for ch in range(1, device_dict['chs'] + 1):
            channel_info = self.generate_channel_url(device_dict, ch)
            channels.append(channel_info)
        
        conn.close()
        
        return {
            'device': device_dict,
            'channels': channels,
            'total_channels': len(channels)
        }
    
    def update_device_brand(self, device_id, brand):
        """更新设备品牌"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 添加brand列（如果不存在）
        try:
            cursor.execute('ALTER TABLE devices ADD COLUMN brand TEXT DEFAULT "brand_a"')
        except sqlite3.OperationalError:
            pass  # 列已存在
        
        cursor.execute('UPDATE devices SET brand = ? WHERE id = ?', (brand, device_id))
        conn.commit()
        conn.close()
        
        print(f"✅ 设备 {device_id} 品牌已更新为: {brand}")

def main():
    """主函数"""
    generator = ChannelURLGenerator()
    
    print("🎯 多品牌录像机通道URL生成器")
    print("=" * 50)
    
    # 演示生成所有设备的通道URL
    conn = sqlite3.connect('backend/data/devices.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, chs FROM devices WHERE chs > 1')
    nvr_devices = cursor.fetchall()
    
    for device_id, name, chs in nvr_devices:
        print(f"\n📹 {name} (ID: {device_id}) - {chs}通道")
        print("-" * 40)
        
        channels = generator.generate_all_channels(device_id)
        if channels:
            for ch in channels['channels'][:3]:  # 显示前3个通道
                print(f"   通道{ch['channel']}:")
                print(f"     主码流: {ch['main_url']}")
                print(f"     子码流: {ch['sub_url']}")
                print()
    
    conn.close()
    
    print("\n📋 使用说明:")
    print("   • 系统已支持多种品牌的通道地址格式")
    print("   • 支持RTSP/HTTP/HTTPS多种协议")
    print("   • 支持主码流/子码流切换")
    print("   • 通道号1-16自动生成")

if __name__ == '__main__':
    main()