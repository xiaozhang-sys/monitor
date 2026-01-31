#!/usr/bin/env python3
"""
快速配置检查脚本
"""
import os
import sys
import json
from pathlib import Path

def check_file(file_path):
    """检查文件是否存在"""
    return Path(file_path).exists()

def main():
    print("配置检查开始...")
    print("-" * 30)
    
    config_dir = Path("config")
    
    # 检查环境配置文件
    environments = ["development", "test", "production"]
    for env in environments:
        env_file = config_dir / "environments" / f"{env}.env"
        if check_file(env_file):
            print(f"[OK] {env}.env 存在")
        else:
            print(f"[MISSING] {env}.env 不存在")
    
    # 检查应用配置
    app_configs = [
        "apps/backend.json",
        "apps/backend.prod.json", 
        "apps/backend.test.json",
        "apps/frontend.json"
    ]
    
    for config in app_configs:
        config_path = config_dir / config
        if check_file(config_path):
            print(f"[OK] {config} 存在")
        else:
            print(f"[MISSING] {config} 不存在")
    
    # 检查服务器配置
    server_configs = [
        "servers/nginx/nginx.conf",
        "servers/nginx/nginx.prod.conf",
        "servers/srs/srs.conf",
        "servers/srs/srs.test.conf"
    ]
    
    for config in server_configs:
        config_path = config_dir / config
        if check_file(config_path):
            print(f"[OK] {config} 存在")
        else:
            print(f"[MISSING] {config} 不存在")
    
    # 显示当前环境
    current_env_file = config_dir / ".current_env"
    if check_file(current_env_file):
        with open(current_env_file, 'r') as f:
            current_env = f.read().strip()
        print(f"[INFO] 当前环境: {current_env}")
    else:
        print("[INFO] 当前环境: development (默认)")
    
    print("-" * 30)
    print("配置检查完成！")

if __name__ == "__main__":
    main()