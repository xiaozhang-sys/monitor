"""
统一配置加载器
支持多环境配置管理
"""
import os
import json
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    def __init__(self):
        self.config_base = Path(__file__).parent
        self.env = os.getenv('ENVIRONMENT', 'development')
        
    def load_app_config(self, app_name: str) -> Dict[str, Any]:
        """加载应用配置"""
        config_file = self.config_base / 'apps' / f'{app_name}.json'
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_env_config(self) -> Dict[str, str]:
        """加载环境变量配置"""
        env_file = self.config_base / 'environments' / f'{self.env}.env'
        config = {}
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        return config
    
    def get_server_config(self, server_type: str, env: str = None) -> str | None:
        """获取服务器配置文件路径"""
        target_env = env or self.env
        config_file = self.config_base / 'servers' / server_type
        
        # 优先查找环境特定配置
        specific_config = config_file / f'{server_type}.{target_env}.conf'
        if specific_config.exists():
            return str(specific_config)
        
        # 回退到通用配置
        general_config = config_file / f'{server_type}.conf'
        if general_config.exists():
            return str(general_config)
        
        return None
    
    def get_all_configs(self) -> Dict[str, Any]:
        """获取所有配置"""
        return {
            'backend': self.load_app_config('backend'),
            'frontend': self.load_app_config('frontend'),
            'webrtc': self.load_app_config('webrtc'),
            'environment': self.load_env_config(),
            'nginx_config': self.get_server_config('nginx'),
            'srs_config': self.get_server_config('srs')
        }

# 全局配置管理器实例
config_manager = ConfigManager()