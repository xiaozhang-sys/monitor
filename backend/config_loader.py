import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    """统一配置加载器，确保前后端配置同步"""
    
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config = {}
        self.load_all_configs()
    
    def load_all_configs(self):
        """加载所有配置文件"""
        try:
            # 加载主配置
            with open(self.config_dir / "app_config.json", "r", encoding="utf-8") as f:
                self.config = json.load(f)
            logger.info("配置加载成功")
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            self.load_defaults()
    
    def load_defaults(self):
        """加载默认配置"""
        self.config = {
            "server": {
                "backend": {"host": "0.0.0.0", "port": 8000},
                "frontend": {"host": "0.0.0.0", "port": 5173},
                "webrtc": {"host": "0.0.0.0", "port": 8080}
            },
            "database": {
                "sqlite": {"path": "./data/devices.db"}
            },
            "security": {
                "jwt": {
                    "secret_key": os.getenv("JWT_SECRET_KEY", "default-secret-key-change-in-production"),
                    "algorithm": "HS256",
                    "access_token_expire_minutes": 30
                }
            },
            "logging": {
                "level": "INFO"
            }
        }
    
    def get(self, key_path, default=None):
        """获取配置值，支持点语法"""
        keys = key_path.split(".")
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_backend_config(self):
        """获取后端配置"""
        return {
            "host": self.get("server.backend.host", "0.0.0.0"),
            "port": self.get("server.backend.port", 8000),
            "cors_origins": self.get("server.backend.cors_origins", ["http://localhost:3000", "http://localhost:5173"])
        }
    
    def get_database_path(self):
        """获取数据库路径"""
        db_config = self.get("database.sqlite")
        if isinstance(db_config, dict):
            db_path = db_config.get("path", "./data/devices.db")
        else:
            db_path = "./data/devices.db"
            
        # 确保使用绝对路径
        if not os.path.isabs(db_path):
            db_path = os.path.join(os.path.dirname(__file__), "..", db_path)
        return os.path.abspath(db_path)
    
    def get_jwt_config(self):
        """获取JWT配置"""
        return {
            "secret_key": os.getenv("JWT_SECRET_KEY", self.get("security.jwt.secret_key")),
            "algorithm": self.get("security.jwt.algorithm", "HS256"),
            "access_token_expire_minutes": self.get("security.jwt.access_token_expire_minutes", 30)
        }

# 全局配置实例
config_loader = ConfigLoader()