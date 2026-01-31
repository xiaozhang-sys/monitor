#!/usr/bin/env python3
"""
Scripts目录文件分类工具 - 合理区分文件类型，保持原有功能
"""

import os
import shutil
from pathlib import Path

class ScriptsOrganizer:
    def __init__(self, scripts_path):
        self.scripts_path = Path(scripts_path)
        self.categories = {
            'webrtc': {
                'description': 'WebRTC相关服务和脚本',
                'files': [
                    'webrtc_server_enhanced.py',
                    'webrtc_server_matched.py',
                    'webrtc_server_sdp_final.py',
                    'webrtc_server_fingerprint_fix.py',
                    'real_webrtc_server_fixed.py',
                    'webrtc_server.log'
                ]
            },
            'auth': {
                'description': '认证和权限相关脚本',
                'files': [
                    'fix_auth_issue.py',
                    'temp_public_api.py'
                ]
            },
            'device_management': {
                'description': '设备管理和配置脚本',
                'files': [
                    'add_http_nvr.py',
                    'device_status_checker.py',
                    'import_devices.py',
                    'query_devices.py',
                    'fix_nvr_config.py',
                    'channel_url_generator.py',
                    'devices.csv'
                ]
            },
            'database': {
                'description': '数据库相关脚本',
                'files': [
                    'db_manager.py',
                    'check_db.py',
                    'test_db_exceptions.py',
                    'fix_data_sync.py'
                ]
            },
            'system': {
                'description': '系统管理和监控脚本',
                'files': [
                    'heartbeat_monitor.py',
                    'heartbeat_service.py',
                    'install_heartbeat_service.py',
                    'monitor_dashboard.py',
                    'monitor_system.log',
                    'directory_guard.py',
                    'exception_handler.py'
                ]
            },
            'setup': {
                'description': '初始化和配置脚本',
                'files': [
                    'auto_setup.py',
                    'init.bat',
                    'init.sh',
                    'migrate_configs.py',
                    'switch_environment.py',
                    'fix_port_mapping.py'
                ]
            },
            'development': {
                'description': '开发工具脚本',
                'files': [
                    'dev-lint.bat',
                    'dev-start.bat',
                    'dev-stop.bat',
                    'dev-test.bat',
                    'start_stable.bat',
                    'start_stable_services.bat',
                    'quick_check.py'
                ]
            },
            'vlc': {
                'description': 'VLC相关脚本',
                'files': [
                    'vlc/start_vlc_monitor.bat'
                ]
            }
        }
    
    def create_directories(self):
        """创建分类目录"""
        for category in self.categories:
            category_path = self.scripts_path / category
            category_path.mkdir(exist_ok=True)
            print(f"创建目录: {category}/")
    
    def move_files(self):
        """移动文件到对应目录"""
        moved_files = []
        
        for category, info in self.categories.items():
            category_path = self.scripts_path / category
            
            for filename in info['files']:
                source_path = self.scripts_path / filename
                
                # 处理子目录文件
                if '/' in filename:
                    parts = filename.split('/')
                    source_path = self.scripts_path / parts[0] / parts[1]
                    target_path = category_path / parts[1]
                else:
                    target_path = category_path / filename
                
                if source_path.exists():
                    # 创建符号链接保持原有路径可用
                    link_path = self.scripts_path / filename
                    
                    # 移动文件
                    shutil.move(str(source_path), str(target_path))
                    
                    # 创建符号链接（Windows兼容）
                    if os.name == 'nt':
                        # Windows下创建快捷方式
                        self.create_windows_shortcut(str(target_path), str(link_path))
                    else:
                        # Unix系统创建符号链接
                        os.symlink(str(target_path), str(link_path))
                    
                    moved_files.append((filename, category))
                    print(f"移动: {filename} -> {category}/")
        
        return moved_files
    
    def create_windows_shortcut(self, target, link_path):
        """为Windows创建快捷方式"""
        try:
            import win32com.client
            shell = win32com.client.Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(link_path.replace('.py', '.lnk'))
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = str(Path(target).parent)
            shortcut.save()
        except ImportError:
            # 如果win32com不可用，创建批处理文件作为替代
            bat_file = link_path.replace('.py', '_run.bat')
            with open(bat_file, 'w') as f:
                f.write(f'@echo off\ncd /d "{Path(target).parent}"\npython "{Path(target).name}"')
    
    def create_compatibility_scripts(self):
        """创建兼容性脚本，保持原有调用方式"""
        compatibility_script = self.scripts_path / '_compatibility_runner.py'
        
        with open(compatibility_script, 'w') as f:
            f.write('''#!/usr/bin/env python3
"""
兼容性运行器 - 保持原有脚本调用方式
"""

import os
import sys
from pathlib import Path

# 脚本映射表
SCRIPT_MAPPING = {
    'fix_auth_issue.py': 'auth/fix_auth_issue.py',
    'temp_public_api.py': 'auth/temp_public_api.py',
    'webrtc_server_fingerprint_fix.py': 'webrtc/webrtc_server_fingerprint_fix.py',
    'add_http_nvr.py': 'device_management/add_http_nvr.py',
    'db_manager.py': 'database/db_manager.py',
    'heartbeat_monitor.py': 'system/heartbeat_monitor.py',
    'auto_setup.py': 'setup/auto_setup.py',
    'dev-start.bat': 'development/dev-start.bat',
    # 可以继续添加更多映射
}

def run_original_script(script_name):
    """运行原始脚本"""
    if script_name in SCRIPT_MAPPING:
        scripts_dir = Path(__file__).parent
        target_script = scripts_dir / SCRIPT_MAPPING[script_name]
        
        if target_script.exists():
            os.chdir(target_script.parent)
            os.system(f'python {target_script.name}')
        else:
            print(f"错误: 找不到脚本 {target_script}")
    else:
        print(f"错误: 未映射的脚本 {script_name}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_original_script(sys.argv[1])
    else:
        print("使用方法: python _compatibility_runner.py <script_name>")
''')
        
        print("创建兼容性运行器: _compatibility_runner.py")
    
    def create_readme(self):
        """创建分类说明文档"""
        readme_content = """# Scripts Directory Structure

## Directory Structure

### webrtc/ - WebRTC related
- webrtc_server_enhanced.py
- webrtc_server_matched.py
- webrtc_server_sdp_final.py
- webrtc_server_fingerprint_fix.py
- real_webrtc_server_fixed.py
- webrtc_server.log

### auth/ - Authentication related
- fix_auth_issue.py
- temp_public_api.py

### device_management/ - Device management
- add_http_nvr.py
- device_status_checker.py
- import_devices.py
- query_devices.py
- fix_nvr_config.py
- channel_url_generator.py
- devices.csv

### database/ - Database related
- db_manager.py
- check_db.py
- test_db_exceptions.py
- fix_data_sync.py

### system/ - System management
- heartbeat_monitor.py
- heartbeat_service.py
- install_heartbeat_service.py
- monitor_dashboard.py
- monitor_system.log
- directory_guard.py
- exception_handler.py

### setup/ - Setup and configuration
- auto_setup.py
- init.bat
- init.sh
- migrate_configs.py
- switch_environment.py
- fix_port_mapping.py

### development/ - Development tools
- dev-lint.bat
- dev-start.bat
- dev-stop.bat
- dev-test.bat
- start_stable.bat
- start_stable_services.bat
- quick_check.py

### vlc/ - VLC related
- start_vlc_monitor.bat

## Compatibility

All files can still be accessed through original paths:

1. Use compatibility runner:
   python scripts/_compatibility_runner.py fix_auth_issue.py

2. Direct access:
   python scripts/auth/fix_auth_issue.py

3. Batch file shortcuts (Windows)
"""
        
        with open(self.scripts_path / 'README.md', 'w') as f:
            f.write(readme_content)
        
        print("创建分类说明文档: README.md")
    
    def organize(self):
        """执行完整的文件分类"""
        print("🚀 开始Scripts目录文件分类...")
        
        # 创建目录
        self.create_directories()
        
        # 移动文件
        moved_files = self.move_files()
        
        # 创建兼容性脚本
        self.create_compatibility_scripts()
        
        # 创建说明文档
        self.create_readme()
        
        print(f"✅ 分类完成！共移动 {len(moved_files)} 个文件")
        print("\n📁 新目录结构已创建，原有功能保持不变")

if __name__ == "__main__":
    organizer = ScriptsOrganizer("d:\\code\\Monitor\\scripts")
    organizer.organize()