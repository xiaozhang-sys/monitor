#!/usr/bin/env python3
"""
设备心跳监测服务
定时检查设备在线状态，每10分钟执行一次
"""

import sqlite3
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
import sys
import os
import time
import subprocess
import platform

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_path)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('heartbeat_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 导入检查函数
try:
    from backend.main import check_device_online, get_db_connection
except ImportError as e:
    logger.error(f"导入检查函数失败: {e}")
    # 备用实现
    def check_device_online(ip, port, protocol):
        """简化的设备在线检查"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"设备连接检查异常: {e}")
            return False
            
    def get_db_connection():
        """获取数据库连接的备用实现"""
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
        return sqlite3.connect(db_path)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')

class HeartbeatService:
    def __init__(self, interval_minutes=10):
        self.interval_minutes = interval_minutes
        self.running = False
        
    async def check_device_status(self, device_id, ip, port, protocol):
        """检查单个设备状态"""
        try:
            is_online = check_device_online(ip, port or 554, protocol or 'rtsp')
            return {
                'device_id': device_id,
                'is_online': is_online,
                'status': 'online' if is_online else 'offline'
            }
        except Exception as e:
            logger.error(f"检查设备 {device_id} 失败: {e}")
            return {
                'device_id': device_id,
                'is_online': False,
                'status': 'offline'
            }
    
    async def check_all_devices(self):
        """检查所有设备状态"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 获取所有设备
            cursor.execute("SELECT id, ip, port, name, protocol FROM devices")
            devices = cursor.fetchall()
            
            if not devices:
                logger.info("没有设备需要检查")
                conn.close()
                return
            
            logger.info(f"开始检查 {len(devices)} 个设备的状态")
            
            # 并发检查所有设备
            tasks = []
            for device in devices:
                device_id, ip, port, name, protocol = device
                task = self.check_device_status(device_id, ip, port, protocol)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤掉异常结果
            valid_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"设备检查异常: {result}")
                else:
                    valid_results.append(result)
            
            # 更新数据库
            now = datetime.now()
            online_count = 0
            
            for result in valid_results:
                try:
                    device_id = result['device_id']
                    is_online = result['is_online']
                    new_status = result['status']
                    
                    if is_online:
                        cursor.execute(
                            "UPDATE devices SET status = ?, last_seen = ?, last_check = ?, check_count = check_count + 1 WHERE id = ?",
                            (new_status, now.isoformat(), now.isoformat(), device_id)
                        )
                        online_count += 1
                    else:
                        cursor.execute(
                            "UPDATE devices SET status = ?, last_check = ?, check_count = check_count + 1 WHERE id = ?",
                            (new_status, now.isoformat(), device_id)
                        )
                except Exception as e:
                    logger.error(f"更新设备 {result.get('device_id', 'unknown')} 状态时出错: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            logger.info(f"设备状态检查完成: 在线 {online_count}, 离线 {len(valid_results) - online_count}")
            
        except Exception as e:
            logger.error(f"检查设备状态失败: {e}")
    
    async def run(self):
        """运行心跳监测服务"""
        self.running = True
        logger.info(f"心跳监测服务启动，检查间隔: {self.interval_minutes} 分钟")
        
        while self.running:
            try:
                await self.check_all_devices()
                
                # 等待下一个检查周期
                await asyncio.sleep(self.interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("收到停止信号，正在关闭服务...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"心跳监测服务错误: {e}")
                await asyncio.sleep(60)  # 错误后等待1分钟再重试
    
    def stop(self):
        """停止服务"""
        self.running = False
        logger.info("心跳监测服务已停止")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='设备心跳监测服务')
    parser.add_argument('--interval', type=int, default=10, 
                       help='检查间隔（分钟）, 默认: 10')
    parser.add_argument('--once', action='store_true',
                       help='只运行一次检查，然后退出')
    
    args = parser.parse_args()
    
    service = HeartbeatService(args.interval)
    
    if args.once:
        # 运行一次检查
        logger.info("执行单次设备状态检查...")
        asyncio.run(service.check_all_devices())
    else:
        # 运行持续服务
        try:
            asyncio.run(service.run())
        except KeyboardInterrupt:
            service.stop()

if __name__ == "__main__":
    main()