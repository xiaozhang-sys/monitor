#!/usr/bin/env python3
"""
项目清理工具 - 清理根目录临时文件并重新组织重要文件
"""

import os
import shutil
import glob
from pathlib import Path

class ProjectCleaner:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.temp_patterns = [
            '*.tmp',
            '*.log',
            '*.bak',
            '*~',
            '.DS_Store',
            'Thumbs.db'
        ]
        
    def move_important_files(self):
        """将重要文件移动到合适的目录"""
        important_files = {
            # 文档类
            'BLACK_SCREEN_SOLUTION.md': 'docs/troubleshooting/',
            'fix_auth_issue.py': 'scripts/',
            'temp_public_api.py': 'scripts/',
            'webrtc_server_fingerprint_fix.py': 'scripts/',
            'start_monitor_fix.bat': 'tools/',
            'check_actual_services.py': 'tools/',
            'check_services.py': 'tools/',
            
            # 测试文件
            'test_*.py': 'tests/',
            'debug_*.py': 'tests/',
            'test_*.html': 'tests/',
            'debug_*.html': 'tests/',
            
            # 临时测试文件
            'test_sdp_*.txt': 'tests/',
            'webrtc_test.html': 'tests/',
        }
        
        for pattern, target_dir in important_files.items():
            target_path = self.root_path / target_dir
            target_path.mkdir(parents=True, exist_ok=True)
            
            files = glob.glob(str(self.root_path / pattern))
            for file_path in files:
                file_path = Path(file_path)
                if file_path.is_file() and file_path.parent == self.root_path:
                    new_path = target_path / file_path.name
                    
                    # 如果目标文件已存在，添加时间戳
                    if new_path.exists():
                        timestamp = file_path.stat().st_mtime
                        new_name = f"{file_path.stem}_{int(timestamp)}{file_path.suffix}"
                        new_path = target_path / new_name
                    
                    print(f"移动: {file_path.name} -> {target_dir}")
                    shutil.move(str(file_path), str(new_path))
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        temp_files = []
        
        # 查找临时文件
        for pattern in self.temp_patterns:
            files = glob.glob(str(self.root_path / pattern))
            temp_files.extend(files)
        
        # 清理特定的临时文件
        specific_temp = [
            'test_sdp_response.txt',
            'webrtc_test.html',
            'debug_test.html',
            'test_webrtc_connection.py',
            'test_webrtc_real.py',
            'rtsp_direct_test.py',
            'black_screen_debug.py',
        ]
        
        for filename in specific_temp:
            file_path = self.root_path / filename
            if file_path.exists() and file_path.is_file():
                temp_files.append(str(file_path))
        
        # 删除临时文件
        for file_path in temp_files:
            try:
                Path(file_path).unlink()
                print(f"删除临时文件: {Path(file_path).name}")
            except Exception as e:
                print(f"无法删除 {file_path}: {e}")
    
    def create_backup(self):
        """创建备份目录"""
        backup_dir = self.root_path / 'config' / 'backups' / 'cleanup_backup'
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 备份重要文件
        important_backup = [
            'BLACK_SCREEN_SOLUTION.md',
            'fix_auth_issue.py',
            'temp_public_api.py',
            'webrtc_server_fingerprint_fix.py',
        ]
        
        for filename in important_backup:
            src = self.root_path / filename
            if src.exists():
                dst = backup_dir / filename
                shutil.copy2(str(src), str(dst))
                print(f"备份: {filename} -> {backup_dir}")
    
    def run_cleanup(self):
        """运行完整清理流程"""
        print("🚀 开始项目清理...")
        
        # 创建备份
        self.create_backup()
        
        # 移动重要文件
        self.move_important_files()
        
        # 清理临时文件
        self.cleanup_temp_files()
        
        print("✅ 清理完成！")
        print("\n📋 清理摘要:")
        print("- 重要文件已移动到合适的目录")
        print("- 临时文件已清理")
        print("- 备份已创建在 config/backups/cleanup_backup/")

if __name__ == "__main__":
    cleaner = ProjectCleaner("d:\\code\\Monitor")
    cleaner.run_cleanup()