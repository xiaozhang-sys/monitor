import sqlite3
import hashlib
import os

def init_db():
    """初始化数据库"""
    db_path = 'backend/devices.db'
    
    # 确保backend目录存在
    os.makedirs('backend', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建设备表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region TEXT NOT NULL,
            store TEXT NOT NULL,
            ip TEXT NOT NULL,
            port INTEGER DEFAULT 554,
            user TEXT NOT NULL,
            pwd TEXT NOT NULL,
            chs INTEGER DEFAULT 1,
            name TEXT,
            protocol TEXT DEFAULT 'rtsp',
            status TEXT DEFAULT 'offline',
            last_seen TIMESTAMP,
            last_check TIMESTAMP,
            check_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建默认管理员用户
    admin_hash = hashlib.sha256("admin".encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, role) 
        VALUES (?, ?, ?)
    ''', ("admin", admin_hash, "admin"))
    
    # 插入测试设备数据
    test_devices = [
        ("南京", "六合店", "192.168.1.100", 554, "admin", "123456", 2, "录像机一"),
        ("南京", "六合店", "192.168.1.101", 554, "admin", "123456", 3, "录像机二"),
        ("南京", "六合店", "192.168.1.102", 554, "admin", "123456", 4, "录像机三"),
    ]
    
    for region, store, ip, port, user, pwd, chs, name in test_devices:
        cursor.execute('''
            INSERT OR IGNORE INTO devices (region, store, ip, port, user, pwd, chs, name, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (region, store, ip, port, user, pwd, chs, name, "online"))
    
    conn.commit()
    conn.close()
    print("数据库初始化完成")

if __name__ == "__main__":
    init_db()