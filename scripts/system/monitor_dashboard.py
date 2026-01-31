#!/usr/bin/env python3
"""
监控系统实时仪表板
功能：
1. 实时系统状态监控
2. 设备在线状态
3. 流媒体状态
4. 资源使用率
5. 告警通知
"""

import time
import requests
import json
import os
import psutil
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich.text import Text
import threading
import queue

console = Console()

class MonitorDashboard:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.srs_url = "http://localhost:8085"
        self.running = True
        self.data_queue = queue.Queue()
        
    def get_system_info(self):
        """获取系统信息"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / 1024 / 1024 / 1024  # GB
            memory_total = memory.total / 1024 / 1024 / 1024  # GB
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used = disk.used / 1024 / 1024 / 1024  # GB
            disk_total = disk.total / 1024 / 1024 / 1024  # GB
            
            # 网络I/O
            net_io = psutil.net_io_counters()
            bytes_sent = net_io.bytes_sent / 1024 / 1024  # MB
            bytes_recv = net_io.bytes_recv / 1024 / 1024  # MB
            
            return {
                "cpu": cpu_percent,
                "memory": {
                    "percent": memory_percent,
                    "used": round(memory_used, 2),
                    "total": round(memory_total, 2)
                },
                "disk": {
                    "percent": disk_percent,
                    "used": round(disk_used, 2),
                    "total": round(disk_total, 2)
                },
                "network": {
                    "sent": round(bytes_sent, 2),
                    "recv": round(bytes_recv, 2)
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_backend_status(self):
        """获取后端状态"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {"status": "error"}
    
    def get_device_status(self):
        """获取设备状态"""
        try:
            response = requests.get(f"{self.base_url}/api/devices/stats", timeout=2)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {"total": 0, "online": 0, "offline": 0}
    
    def get_srs_status(self):
        """获取SRS状态"""
        try:
            response = requests.get(f"{self.srs_url}/api/v1/summaries", timeout=2)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "running" if data.get("code") == 0 else "error",
                    "streams": len(data.get("streams", [])),
                    "clients": len(data.get("clients", []))
                }
        except:
            pass
        return {"status": "error", "streams": 0, "clients": 0}
    
    def get_docker_status(self):
        """获取Docker容器状态"""
        try:
            import subprocess
            result = subprocess.run(
                ["docker-compose", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                cwd="/code/Monitor"
            )
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        containers.append(json.loads(line))
                return containers
        except:
            pass
        return []
    
    def create_layout(self):
        """创建仪表板布局"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        layout["left"].split_column(
            Layout(name="system"),
            Layout(name="docker")
        )
        layout["right"].split_column(
            Layout(name="devices"),
            Layout(name="media")
        )
        return layout
    
    def create_system_panel(self, data):
        """创建系统信息面板"""
        if "error" in data:
            return Panel("系统信息获取失败", title="系统状态", border_style="red")
        
        system_info = data
        content = f"""
🖥️  CPU: {system_info['cpu']:.1f}%
💾  内存: {system_info['memory']['used']}GB / {system_info['memory']['total']}GB ({system_info['memory']['percent']:.1f}%)
💿  磁盘: {system_info['disk']['used']}GB / {system_info['disk']['total']}GB ({system_info['disk']['percent']:.1f}%)
🌐  网络: ↑{system_info['network']['sent']}MB ↓{system_info['network']['recv']}MB
        """
        return Panel(content.strip(), title="系统状态", border_style="green")
    
    def create_devices_panel(self, data):
        """创建设备状态面板"""
        total = data.get("total", 0)
        online = data.get("online", 0)
        offline = data.get("offline", 0)
        
        if total == 0:
            content = "📹 暂无设备"
            border_style = "yellow"
        else:
            online_rate = (online / total * 100) if total > 0 else 0
            content = f"""
📹  总设备: {total}
🟢  在线: {online} ({online_rate:.1f}%)
🔴  离线: {offline}
            """
            border_style = "green" if online_rate > 90 else "yellow"
        
        return Panel(content.strip(), title="设备状态", border_style=border_style)
    
    def create_media_panel(self, data):
        """创建媒体流面板"""
        status = data.get("status", "error")
        streams = data.get("streams", 0)
        clients = data.get("clients", 0)
        
        if status == "running":
            content = f"""
🎥  SRS状态: 运行中
📡  流数量: {streams}
👥  客户端: {clients}
            """
            border_style = "green"
        else:
            content = "🎥 SRS状态: 未运行"
            border_style = "red"
        
        return Panel(content.strip(), title="媒体流", border_style=border_style)
    
    def create_docker_panel(self, containers):
        """创建Docker面板"""
        if not containers:
            return Panel("Docker容器信息获取失败", title="容器状态", border_style="red")
        
        content = ""
        for container in containers:
            name = container.get("Service", "unknown")
            status = container.get("State", "unknown")
            health = container.get("Health", "")
            
            if status == "running":
                icon = "🟢"
                status_text = "运行中"
            else:
                icon = "🔴"
                status_text = "已停止"
            
            content += f"{icon} {name}: {status_text}\n"
        
        return Panel(content.strip(), title="容器状态", border_style="blue")
    
    def update_dashboard(self, layout):
        """更新仪表板"""
        try:
            # 获取所有数据
            system_data = self.get_system_info()
            backend_data = self.get_backend_status()
            device_data = self.get_device_status()
            srs_data = self.get_srs_status()
            docker_data = self.get_docker_status()
            
            # 更新布局
            layout["header"].update(
                Panel(
                    Align.center(
                        Text("🎯 零售天眼通 - 实时仪表板", style="bold cyan")
                    ),
                    style="on blue"
                )
            )
            
            layout["system"].update(self.create_system_panel(system_data))
            layout["devices"].update(self.create_devices_panel(device_data))
            layout["media"].update(self.create_media_panel(srs_data))
            layout["docker"].update(self.create_docker_panel(docker_data))
            
            # 更新时间
            layout["footer"].update(
                Panel(
                    Align.center(
                        Text(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                             style="dim")
                    )
                )
            )
            
        except Exception as e:
            layout["header"].update(
                Panel(f"更新失败: {str(e)}", style="red")
            )
    
    def run(self):
        """运行仪表板"""
        console.print("🎯 启动监控系统仪表板...")
        
        layout = self.create_layout()
        
        with Live(layout, refresh_per_second=1, console=console) as live:
            while self.running:
                self.update_dashboard(layout)
                time.sleep(2)  # 每2秒更新一次
    
    def stop(self):
        """停止仪表板"""
        self.running = False

def main():
    """主函数"""
    dashboard = MonitorDashboard()
    
    try:
        dashboard.run()
    except KeyboardInterrupt:
        console.print("\n👋 仪表板已停止")
        dashboard.stop()

if __name__ == "__main__":
    main()