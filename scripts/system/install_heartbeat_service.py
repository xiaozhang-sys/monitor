#!/usr/bin/env python3
"""
Windows心跳监测服务安装脚本
用于将设备心跳监测服务安装为Windows服务
"""

import os
import sys
import subprocess
import win32serviceutil
import win32service
import win32event
import servicemanager
import logging
import asyncio
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

class HeartbeatService(win32serviceutil.ServiceFramework):
    """Windows服务类"""
    _svc_name_ = "DeviceHeartbeatMonitor"
    _svc_display_name_ = "设备心跳监测服务"
    _svc_description_ = "定时检查设备在线状态的服务"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        
    def SvcStop(self):
        """停止服务"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False
        logger.info("设备心跳监测服务正在停止...")
        
    def SvcDoRun(self):
        """运行服务"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        logger.info("设备心跳监测服务已启动")
        
        try:
            # 导入心跳监测逻辑
            from heartbeat_service import HeartbeatService as HBService
            
            # 创建心跳服务实例
            hb_service = HBService(interval_minutes=10)
            
            # 运行心跳检查循环
            while self.running:
                try:
                    # 运行一次检查
                    asyncio.run(hb_service.check_all_devices())
                    
                    # 等待10分钟
                    for _ in range(600):  # 600 * 1秒 = 10分钟
                        if not self.running:
                            break
                        win32event.WaitForSingleObject(self.hWaitStop, 1000)
                        
                except Exception as e:
                    logger.error(f"心跳检查错误: {e}")
                    # 错误后等待1分钟再重试
                    for _ in range(60):
                        if not self.running:
                            break
                        win32event.WaitForSingleObject(self.hWaitStop, 1000)
                        
        except Exception as e:
            logger.error(f"服务运行错误: {e}")
            servicemanager.LogErrorMsg(str(e))
            
        logger.info("设备心跳监测服务已停止")

def install_service():
    """安装Windows服务"""
    try:
        # 获取当前脚本目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        service_script = os.path.join(script_dir, 'install_heartbeat_service.py')
        
        # 安装服务
        win32serviceutil.InstallService(
            HeartbeatService,
            HeartbeatService._svc_name_,
            HeartbeatService._svc_display_name_,
            startType='auto'
        )
        
        print("✅ 设备心跳监测服务安装成功！")
        print("📋 服务名称:", HeartbeatService._svc_name_)
        print("📋 显示名称:", HeartbeatService._svc_display_name_)
        print("\n🔧 使用说明:")
        print("  启动服务: net start DeviceHeartbeatMonitor")
        print("  停止服务: net stop DeviceHeartbeatMonitor")
        print("  卸载服务: python install_heartbeat_service.py --remove")
        
    except Exception as e:
        print(f"❌ 服务安装失败: {e}")
        print("请确保以管理员权限运行此脚本")

def remove_service():
    """卸载Windows服务"""
    try:
        win32serviceutil.RemoveService(HeartbeatService._svc_name_)
        print("✅ 设备心跳监测服务卸载成功！")
    except Exception as e:
        print(f"❌ 服务卸载失败: {e}")

def start_service():
    """启动服务"""
    try:
        win32serviceutil.StartService(HeartbeatService._svc_name_)
        print("✅ 设备心跳监测服务已启动！")
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")

def stop_service():
    """停止服务"""
    try:
        win32serviceutil.StopService(HeartbeatService._svc_name_)
        print("✅ 设备心跳监测服务已停止！")
    except Exception as e:
        print(f"❌ 服务停止失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) == 1:
        # 无参数时显示帮助
        print("设备心跳监测服务管理工具")
        print("\n使用方法:")
        print("  python install_heartbeat_service.py --install   # 安装服务")
        print("  python install_heartbeat_service.py --remove    # 卸载服务")
        print("  python install_heartbeat_service.py --start     # 启动服务")
        print("  python install_heartbeat_service.py --stop      # 停止服务")
        print("  python install_heartbeat_service.py --debug   # 调试运行")
    elif '--install' in sys.argv:
        install_service()
    elif '--remove' in sys.argv:
        remove_service()
    elif '--start' in sys.argv:
        start_service()
    elif '--stop' in sys.argv:
        stop_service()
    elif '--debug' in sys.argv:
        # 调试运行，不安装为服务
        from heartbeat_service import HeartbeatService as HBService
        
        print("🚀 开始调试运行心跳监测服务...")
        hb_service = HBService(interval_minutes=1)  # 调试模式1分钟检查一次
        
        try:
            asyncio.run(hb_service.run())
        except KeyboardInterrupt:
            print("\n⏹️ 调试运行已停止")
    else:
        # Windows服务模式
        win32serviceutil.HandleCommandLine(HeartbeatService)

if __name__ == '__main__':
    main()