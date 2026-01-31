#!/usr/bin/env python3
"""
目录规范守护脚本
防止在根目录随意创建文件
"""

import os
import sys
import shutil
from pathlib import Path
import json
from datetime import datetime

class DirectoryGuard:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.rules = self._load_rules()
        
    def _load_rules(self):
        """加载目录规则"""
        return {
            'allowed_root_files': [
                '.env', 'README.md', 'docker-compose.yml', 
                'PROJECT_STRUCTURE.md', 'devices_sample.csv', 'webrtc_server.log'
            ],
            'allowed_extensions': {
                'scripts': ['.py', '.bat', '.sh'],
                'tests': ['.py', '.html', '.json'],
                'config': ['.json', '.yml', '.yaml', '.conf'],
                'data': ['.db', '.sqlite', '.csv', '.json', '.backup'],
                'docs': ['.md', '.txt'],
                'logs': ['.log'],
                'tools': ['.bat', '.ps1']
            }
        }
    
    def check_and_migrate(self, file_path):
        """检查文件并迁移到正确目录"""
        file_path = Path(file_path)
        
        if file_path.parent == self.root_path:
            return self._handle_root_violation(file_path)
        
        return True, "文件已在正确目录"
    
    def _handle_root_violation(self, file_path):
        """处理根目录违规文件"""
        filename = file_path.name
        
        # 检查是否是允许的文件
        if filename in self.rules['allowed_root_files']:
            return True, "允许在根目录"
        
        # 根据文件类型确定目标目录
        target_dir = self._determine_target_dir(file_path)
        
        if target_dir:
            target_path = self.root_path / target_dir / filename
            
            # 确保目标目录存在
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 移动文件
            try:
                shutil.move(str(file_path), str(target_path))
                self._log_migration(file_path, target_path)
                return True, f"已迁移到 {target_dir}/{filename}"
            except Exception as e:
                return False, f"迁移失败: {e}"
        
        return False, "无法确定目标目录"
    
    def _determine_target_dir(self, file_path):
        """根据文件类型确定目标目录"""
        ext = file_path.suffix.lower()
        
        # 特殊规则
        if file_path.name.startswith('test'):
            return 'tests'
        elif ext == '.py':
            return 'scripts'
        elif ext == '.json':
            return 'config'
        elif ext in ['.csv', '.db', '.sqlite']:
            return 'data'
        elif ext == '.md':
            return 'docs'
        elif ext == '.log':
            return 'logs'
        elif ext == '.bat':
            return 'tools'
        
        # 根据扩展名匹配
        for dir_name, extensions in self.rules['allowed_extensions'].items():
            if ext in extensions:
                return dir_name
        
        return 'scripts'  # 默认目录
    
    def _log_migration(self, source, target):
        """记录迁移日志"""
        log_file = self.root_path / 'logs' / 'directory_guard.log'
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now()}] 迁移: {source.name} -> {target.parent.name}/{target.name}\n")
    
    def scan_violations(self):
        """扫描根目录违规文件"""
        violations = []
        
        for item in self.root_path.iterdir():
            if item.is_file() and item.name not in self.rules['allowed_root_files']:
                violations.append(item)
        
        return violations
    
    def auto_fix_violations(self):
        """自动修复所有违规"""
        violations = self.scan_violations()
        results = []
        
        for violation in violations:
            success, message = self.check_and_migrate(violation)
            results.append({
                'file': violation.name,
                'success': success,
                'message': message
            })
        
        return results

def main():
    """主函数"""
    guard = DirectoryGuard("d:\\code\\Monitor")
    
    print("🔍 扫描根目录违规文件...")
    violations = guard.scan_violations()
    
    if violations:
        print(f"发现 {len(violations)} 个违规文件:")
        for v in violations:
            print(f"  - {v.name}")
        
        print("\n🚀 自动修复中...")
        results = guard.auto_fix_violations()
        
        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['file']}: {result['message']}")
    else:
        print("✅ 未发现违规文件")

if __name__ == "__main__":
    main()