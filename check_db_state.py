import sqlite3
import os

# 检查数据库中当前的设备数量
db_path = 'd:/code/天眼系统/2025.10.17优化视音频流默认子码流读取手动切换主码流/Monitor/data/devices.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 统计设备数量
    cursor.execute('SELECT COUNT(*) FROM devices')
    count = cursor.fetchone()[0]
    print(f'当前数据库中设备数量: {count}')
    
    # 获取所有设备信息
    cursor.execute('SELECT id, name, ip FROM devices')
    devices = cursor.fetchall()
    print('当前设备列表:')
    for device in devices:
        print(f'  ID: {device[0]}, 名称: {device[1]}, IP: {device[2]}')
    
    conn.close()
else:
    print(f'数据库文件不存在: {db_path}')