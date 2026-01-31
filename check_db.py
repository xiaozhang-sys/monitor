import sqlite3
import os

# 检查数据库文件是否存在
db_path = 'd:/code/天眼系统/2025.10.17优化视音频流默认子码流读取手动切换主码流/Monitor/data/devices.db'

if not os.path.exists(db_path):
    print(f"数据库文件不存在: {db_path}")
else:
    print(f"数据库文件存在: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('\n数据库中的表:', [table[0] for table in tables])
    
    # 检查每个表的记录数
    for table in tables:
        table_name = table[0]
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            print(f'{table_name} 表中的记录数: {count}')
            
            # 如果是users表，显示具体数据
            if table_name == 'users':
                cursor.execute('SELECT * FROM users')
                users = cursor.fetchall()
                print(f'users表中的数据: {users}')
                
        except sqlite3.OperationalError as e:
            print(f'读取表 {table_name} 时出错: {e}')
    
    conn.close()