#!/usr/bin/env python3
"""
检查实际运行的服务状态
"""

import requests
import time
import socket

def check_service(url, name):
    """检查单个服务状态"""
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return f"✅ {name}: {url} - 正常"
        else:
            return f"⚠️ {name}: {url} - 状态码 {response.status_code}"
    except requests.exceptions.ConnectionError:
        return f"❌ {name}: {url} - 连接失败"
    except requests.exceptions.Timeout:
        return f"⏰ {name}: {url} - 超时"
    except Exception as e:
        return f"❌ {name}: {url} - 错误: {e}"

def main():
    print("🔍 检查实际服务状态...")
    print("=" * 50)
    
    services = {
        "后端服务(主)": "http://localhost:8003/health",
        "后端服务(公共)": "http://localhost:8004/devices",
        "WebRTC服务": "http://localhost:8090/health",
        "前端服务": "http://127.0.0.1:5173",
    }
    
    for name, url in services.items():
        print(check_service(url, name))
    
    print("\n" + "=" * 50)
    print("🌐 访问地址:")
    print("   前端界面: http://127.0.0.1:5173")
    print("   后端API(认证): http://localhost:8003")
    print("   后端API(公共): http://localhost:8004")
    print("   WebRTC服务: http://localhost:8090")
    print("   调试页面: http://127.0.0.1:5173/debug_video.html")

if __name__ == "__main__":
    main()