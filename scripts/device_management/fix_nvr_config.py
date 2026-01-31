#!/usr/bin/env python3
"""
录像机配置修复工具
提供详细的排查和修复建议
"""

import sqlite3
import os

def update_device_status(device_id, status):
    """更新设备状态"""
    try:
        db_path = "../backend/data/devices.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE devices SET status=? WHERE id=?", (status, device_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"更新状态失败: {e}")
        return False

def get_device_details():
    """获取设备详细信息"""
    try:
        db_path = "../backend/data/devices.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, ip, port, user, pwd, region, store FROM devices")
        devices = cursor.fetchall()
        conn.close()
        return devices
    except Exception as e:
        print(f"获取设备信息失败: {e}")
        return []

def print_nvr_troubleshooting_guide():
    """打印NVR故障排查指南"""
    print("""
🔧 NVR离线问题排查指南
=====================================

📋 当前发现的问题:
1. 端口55401未开放（应该是554）
2. RTSP服务可能未启用
3. 需要检查NVR网络配置

🎯 解决步骤:

步骤1: 检查NVR网络配置
--------------------
1. 登录NVR的Web界面（通常是 http://192.168.42.86）
2. 进入：配置 → 网络 → 基本配置
3. 确认以下设置：
   - IP地址：192.168.42.86
   - 子网掩码：255.255.255.0
   - 网关：192.168.42.1

步骤2: 启用RTSP服务
-----------------
1. 进入：配置 → 网络 → 高级配置 → 集成协议
2. 勾选"启用RTSP"
3. 确认RTSP端口：554（不是55401）
4. 点击"保存"

步骤3: 检查用户权限
-----------------
1. 进入：配置 → 系统 → 用户管理
2. 确认admin用户有RTSP访问权限
3. 检查密码是否正确

步骤4: 验证RTSP地址
-----------------
正确的RTSP地址格式：
rtsp://admin:Chang168@192.168.42.86:554/Streaming/Channels/101

步骤5: 测试连接
-----------------
1. 使用VLC播放器测试：
   - 打开VLC → 媒体 → 打开网络串流
   - 输入：rtsp://admin:Chang168@192.168.42.86:554/Streaming/Channels/101

步骤6: 更新系统配置
-----------------
如果发现端口配置错误，需要：
1. 在设备管理中修改端口号为554
2. 重新测试连接

🚨 常见问题:
- 防火墙阻止：检查Windows防火墙或路由器设置
- 密码错误：确认NVR登录密码
- 网络不通：检查网线连接和网络设置
- 端口占用：确认554端口未被其他应用占用

💡 如果以上步骤都正确，设备状态应该变为"在线"
    """)

def main():
    print("🔧 NVR故障排查工具")
    print("=" * 40)
    
    devices = get_device_details()
    
    if not devices:
        print("❌ 未找到设备")
        return
    
    for device_id, name, ip, port, username, password, region, store in devices:
        print(f"\n📱 设备信息:")
        print(f"   名称: {name}")
        print(f"   IP地址: {ip}")
        print(f"   端口: {port}")
        print(f"   用户名: {username}")
        print(f"   区域: {region}")
        print(f"   门店: {store}")
        
        # 检查端口配置
        if port != 554:
            print(f"\n⚠️  端口配置错误!")
            print(f"   当前端口: {port}")
            print(f"   应该使用: 554")
            print(f"   建议：在设备管理中修改为554端口")
        
        # 更新状态为待验证
        update_device_status(device_id, "checking")
        print(f"\n✅ 设备状态已更新为: checking")
    
    print_nvr_troubleshooting_guide()

if __name__ == "__main__":
    main()