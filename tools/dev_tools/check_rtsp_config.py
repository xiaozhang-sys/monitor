#!/usr/bin/env python3
import sqlite3
import json

# 连接到数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 查询所有设备
cursor.execute("SELECT * FROM devices")
devices = cursor.fetchall()

# 获取列名
columns = [description[0] for description in cursor.description]

# 转换为字典格式
device_list = []
for device in devices:
    device_dict = dict(zip(columns, device))
    device_list.append(device_dict)

print("=== 设备数据检查 ===")
print(f"找到 {len(device_list)} 个设备")

for device in device_list:
    print(f"\n设备: {device['name']} (ID: {device['id']})")
    print(f"  区域: {device['region']}")
    print(f"  门店: {device['store']}")
    print(f"  IP: {device['ip']}")
    print(f"  端口: {device['port']}")
    print(f"  用户名: {device['user']}")
    print(f"  密码: {device['pwd']}")
    print(f"  通道数: {device['chs']}")
    print(f"  协议: {device['protocol']}")
    print(f"  状态: {device['status']}")
    
    # 构建RTSP URL
    rtsp_url = f"rtsp://{device['user']}:{device['pwd']}@{device['ip']}:{device['port']}/Streaming/Channels/101"
    print(f"  RTSP URL: {rtsp_url}")

conn.close()

# 保存为JSON供前端检查
with open('device_config.json', 'w', encoding='utf-8') as f:
    json.dump(device_list, f, ensure_ascii=False, indent=2)

print("\n=== 配置已保存到 device_config.json ===")