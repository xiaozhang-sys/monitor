#!/usr/bin/env python3
"""
配置验证脚本
验证所有配置文件的正确性和完整性
"""
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.config_loader import ConfigManager
except ImportError:
    # 如果导入失败，使用相对导入
    from pathlib import Path
    config_dir = Path(__file__).parent
    sys.path.insert(0, str(config_dir))
    from config_loader import ConfigManager

def validate_json_file(file_path):
    """验证JSON文件格式"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True, None
    except json.JSONDecodeError as e:
        return False, str(e)

def validate_config_structure():
    """验证配置结构完整性"""
    config_manager = ConfigManager()
    base_path = Path(__file__).parent
    
    required_files = [
        'apps/backend.json',
        'apps/frontend.json',
        'environments/development.env',
        'servers/nginx/nginx.conf',
        'servers/srs/srs.conf'
    ]
    
    missing_files = []
    invalid_files = []
    
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        elif file_path.endswith('.json'):
            valid, error = validate_json_file(full_path)
            if not valid:
                invalid_files.append((file_path, error))
    
    return missing_files, invalid_files

def main():
    """主验证函数"""
    print("🔍 开始验证配置结构...")
    
    missing, invalid = validate_config_structure()
    
    if missing:
        print("❌ 缺失的配置文件:")
        for file in missing:
            print(f"  - {file}")
    
    if invalid:
        print("❌ 格式错误的JSON文件:")
        for file, error in invalid:
            print(f"  - {file}: {error}")
    
    if not missing and not invalid:
        print("✅ 所有配置文件验证通过！")
        
        # 测试配置加载
        try:
            config_manager = ConfigManager()
            all_configs = config_manager.get_all_configs()
            print("\n📋 配置摘要:")
            print(f"  后端端口: {all_configs['backend']['server']['port']}")
            print(f"  前端端口: {all_configs['frontend']['server']['port']}")
            print(f"  环境: {config_manager.env}")
        except Exception as e:
            print(f"❌ 配置加载错误: {e}")
            return False
    
    return len(missing) == 0 and len(invalid) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)