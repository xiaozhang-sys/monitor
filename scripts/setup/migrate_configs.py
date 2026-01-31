#!/usr/bin/env python3
"""
配置迁移脚本
将旧配置文件逐步迁移到新结构
"""
import os
import shutil
import json
from pathlib import Path
from datetime import datetime

class ConfigMigrator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = self.project_root / "config" / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.old_configs = {
            "backend": {
                "config_loader": self.project_root / "backend" / "config_loader.py",
                "nginx": self.project_root / "backend" / "config" / "nginx",
                "srs": self.project_root / "backend" / "config" / "srs"
            },
            "frontend": {
                "env": self.project_root / "frontend" / ".env",
                "vite_config": self.project_root / "frontend" / "vite.config.js"
            },
            "root": {
                "app_config": self.project_root / "config" / "app_config.json",
                "docker_compose": self.project_root / "docker-compose.yml"
            }
        }
    
    def create_backup(self):
        """创建旧配置备份"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 创建备份目录: {self.backup_dir}")
        
        for category, configs in self.old_configs.items():
            for name, path in configs.items():
                if path.exists():
                    backup_path = self.backup_dir / f"{category}_{name}"
                    if path.is_file():
                        shutil.copy2(path, backup_path)
                    elif path.is_dir():
                        shutil.copytree(path, backup_path)
                    print(f"  ✅ 备份: {path.name} -> {backup_path}")
    
    def migrate_nginx_config(self):
        """迁移nginx配置"""
        old_nginx_dir = self.old_configs["backend"]["nginx"]
        new_nginx_dir = self.project_root / "config" / "servers" / "nginx"
        
        if old_nginx_dir.exists():
            # nginx.conf已经迁移，创建生产环境版本
            prod_nginx = new_nginx_dir / "nginx.prod.conf"
            if not prod_nginx.exists():
                shutil.copy2(new_nginx_dir / "nginx.conf", prod_nginx)
                print("  ✅ 创建nginx.prod.conf")
    
    def migrate_srs_config(self):
        """迁移srs配置"""
        old_srs_dir = self.old_configs["backend"]["srs"]
        new_srs_dir = self.project_root / "config" / "servers" / "srs"
        
        if old_srs_dir.exists():
            # srs.conf已经迁移，创建测试环境版本
            test_srs = new_srs_dir / "srs.test.conf"
            if not test_srs.exists():
                shutil.copy2(new_srs_dir / "srs.conf", test_srs)
                print("  ✅ 创建srs.test.conf")
    
    def migrate_app_config(self):
        """迁移旧的app_config.json"""
        old_config = self.old_configs["root"]["app_config"]
        if old_config.exists():
            try:
                with open(old_config, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                
                # 创建迁移报告
                migration_report = self.backup_dir / "migration_report.json"
                with open(migration_report, 'w', encoding='utf-8') as f:
                    json.dump({
                        "migrated_from": str(old_config),
                        "migrated_at": datetime.now().isoformat(),
                        "old_config": old_data,
                        "new_structure": {
                            "backend_config": "config/apps/backend.json",
                            "frontend_config": "config/apps/frontend.json",
                            "environment_config": "config/environments/development.env"
                        }
                    }, f, indent=2, ensure_ascii=False)
                
                print("  ✅ 创建迁移报告")
                
            except Exception as e:
                print(f"  ❌ 迁移app_config.json失败: {e}")
    
    def cleanup_old_configs(self):
        """清理旧配置（可选）"""
        print("\n🧹 清理旧配置...")
        print("⚠️  以下文件可以安全删除：")
        
        for category, configs in self.old_configs.items():
            for name, path in configs.items():
                if path.exists() and path != self.project_root / "config" / "servers" / "nginx" / "nginx.conf":
                    print(f"  - {path}")
        
        print("\n💡 建议：先确认新配置工作正常后再删除旧文件")
    
    def run_migration(self):
        """执行完整迁移"""
        print("🚀 开始配置迁移...")
        print("=" * 50)
        
        # 1. 创建备份
        self.create_backup()
        
        print("\n📦 迁移特定配置...")
        # 2. 迁移nginx
        self.migrate_nginx_config()
        
        # 3. 迁移srs
        self.migrate_srs_config()
        
        # 4. 迁移app_config
        self.migrate_app_config()
        
        print("\n✅ 迁移完成！")
        print("=" * 50)
        
        # 5. 显示清理建议
        self.cleanup_old_configs()

if __name__ == "__main__":
    migrator = ConfigMigrator()
    migrator.run_migration()