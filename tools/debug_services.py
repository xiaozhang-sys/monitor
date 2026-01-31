#!/usr/bin/env python3
"""
服务调试工具 - 检查所有端口和服务状态
"""

import requests
import socket
import time
import json
from typing import Dict, List

def check_port(host: str, port: int) -> bool:
    """检查端口是否开放"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex((host, port)) == 0
    except:
        return False

def check_http_endpoint(url: str) -> Dict:
    """检查HTTP端点"""
    try:
        response = requests.get(url, timeout=2)
        return {
            'url': url,
            'status': response.status_code,
            'ok': response.status_code == 200,
            'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:200]
        }
    except Exception as e:
        return {
            'url': url,
            'status': None,
            'ok': False,
            'error': str(e)
        }

def main():
    """主函数"""
    print("🔍 服务调试工具")
    print("=" * 50)
    
    # 检查端口
    ports = {
        'WebRTC服务器': 8080,
        '后端API': 8001,
        '前端服务': 5173,
        '测试服务器': 8080
    }
    
    print("\n📡 端口检查:")
    for name, port in ports.items():
        status = "✅ 开放" if check_port('localhost', port) else "❌ 关闭"
        print(f"  {name} (端口 {port}): {status}")
    
    # 检查HTTP端点
    endpoints = [
        'http://localhost:8090/api/health',
        'http://localhost:8090/api/stream/status',
        'http://localhost:8001/devices',
        'http://localhost:5173',
        'http://localhost:8090/tests/webrtc_api_test.html'
    ]
    
    print("\n🔗 HTTP端点检查:")
    for url in endpoints:
        result = check_http_endpoint(url)
        if result['ok']:
            print(f"  ✅ {url}")
        else:
            print(f"  ❌ {url} - {result.get('error', 'HTTP错误')}")
    
    # 测试WebRTC服务器API
    print("\n🎯 WebRTC服务器测试:")
    try:
        # 测试健康检查
        health = requests.get('http://localhost:8090/api/health', timeout=2)
        if health.status_code == 200:
            data = health.json()
            print(f"  ✅ 健康检查: {data}")
        
        # 测试设备列表
        devices = requests.get('http://localhost:8090/api/devices', timeout=2)
        if devices.status_code == 200:
            data = devices.json()
            print(f"  ✅ 设备列表: {len(data.get('devices', []))} 个设备")
        
    except Exception as e:
        print(f"  ❌ WebRTC服务器测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("调试完成！")

if __name__ == '__main__':
    main()