#!/usr/bin/env python3
"""
环境切换脚本
快速切换开发、测试、生产环境配置
"""
import os
import json
import shutil
from pathlib import Path
import argparse

class EnvironmentSwitcher:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_root = self.project_root / "config"
        self.env_configs = {
            "development": {
                "env_file": self.config_root / "environments" / "development.env",
                "backend_config": self.config_root / "apps" / "backend.json",
                "frontend_config": self.config_root / "apps" / "frontend.json",
                "nginx_config": self.config_root / "servers" / "nginx" / "nginx.conf",
                "srs_config": self.config_root / "servers" / "srs" / "srs.conf"
            },
            "test": {
                "env_file": self.config_root / "environments" / "test.env",
                "backend_config": self.config_root / "apps" / "backend.test.json",
                "frontend_config": self.config_root / "apps" / "frontend.json",
                "nginx_config": self.config_root / "servers" / "nginx" / "nginx.conf",
                "srs_config": self.config_root / "servers" / "srs" / "srs.test.conf"
            },
            "production": {
                "env_file": self.config_root / "environments" / "production.env",
                "backend_config": self.config_root / "apps" / "backend.prod.json",
                "frontend_config": self.config_root / "apps" / "frontend.json",
                "nginx_config": self.config_root / "servers" / "nginx" / "nginx.prod.conf",
                "srs_config": self.config_root / "servers" / "srs" / "srs.conf"
            }
        }
    
    def switch_environment(self, env_name):
        """切换到指定环境"""
        if env_name not in self.env_configs:
            print(f"[ERROR] 不支持的环境: {env_name}")
            print(f"支持的环境: {list(self.env_configs.keys())}")
            return False
        
        print(f"[INFO] 切换到 {env_name} 环境...")
        
        # 检查配置文件是否存在
        missing_files = []
        for config_name, config_path in self.env_configs[env_name].items():
            if not config_path.exists():
                missing_files.append(str(config_path))
        
        if missing_files:
            print(f"[ERROR] 缺少配置文件:")
            for file in missing_files:
                print(f"  - {file}")
            return False
        
        # 复制环境变量文件
        env_file = self.env_configs[env_name]["env_file"]
        target_env = self.project_root / "frontend" / ".env"
        if target_env.exists():
            shutil.copy2(env_file, target_env)
            print(f"  [OK] 更新: {target_env}")
        
        # 创建环境标记文件
        env_marker = self.config_root / ".current_env"
        with open(env_marker, 'w') as f:
            f.write(env_name)
        
        print(f"  [OK] 环境标记: {env_marker}")
        print(f"  [OK] 当前环境: {env_name}")
        
        # 显示配置摘要
        self.show_config_summary(env_name)
        
        return True
    
    def show_config_summary(self, env_name):
        """显示配置摘要"""
        env_file = self.env_configs[env_name]["env_file"]
        
        print("\n📊 配置摘要:")
        print("-" * 30)
        
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key in ['BACKEND_HOST', 'BACKEND_PORT', 'FRONTEND_PORT', 'WEBRTC_PORT', 'ENVIRONMENT']:
                            print(f"  {key}: {value}")
        except Exception as e:
            print(f"  ❌ 读取配置失败: {e}")
    
    def get_current_env(self):
        """获取当前环境"""
        env_marker = self.config_root / ".current_env"
        if env_marker.exists():
            with open(env_marker, 'r') as f:
                return f.read().strip()
        return "development"
    
    def list_environments(self):
        """列出所有可用环境"""
        current = self.get_current_env()
        
        print("🌍 可用环境:")
        print("-" * 30)
        for env_name in self.env_configs.keys():
            marker = "👉" if env_name == current else "  "
            print(f"{marker} {env_name}")
    
    def validate_environment(self, env_name):
        """验证环境配置"""
        print(f"🔍 验证 {env_name} 环境配置...")
        
        configs = self.env_configs[env_name]
        all_valid = True
        
        for config_name, config_path in configs.items():
            if config_path.exists():
                print(f"  ✅ {config_name}: {config_path}")
            else:
                print(f"  ❌ {config_name}: {config_path} (缺失)")
                all_valid = False
        
        return all_valid

def main():
    parser = argparse.ArgumentParser(description="环境切换工具")
    parser.add_argument("environment", nargs="?", help="要切换到的环境名称")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有可用环境")
    parser.add_argument("--current", "-c", action="store_true", help="显示当前环境")
    parser.add_argument("--validate", "-v", help="验证指定环境配置")
    
    args = parser.parse_args()
    
    switcher = EnvironmentSwitcher()
    
    if args.list:
        switcher.list_environments()
    elif args.current:
        current = switcher.get_current_env()
        print(f"当前环境: {current}")
    elif args.validate:
        switcher.validate_environment(args.validate)
    elif args.environment:
        switcher.switch_environment(args.environment)
    else:
        # 交互式模式
        switcher.list_environments()
        env = input("\n选择要切换的环境: ").strip()
        if env:
            switcher.switch_environment(env)

if __name__ == "__main__":
    main()