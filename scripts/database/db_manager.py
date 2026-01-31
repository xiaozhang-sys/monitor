#!/usr/bin/env python3
"""
数据库连接管理工具
支持 SQLite、MySQL、PostgreSQL 数据库连接和配置管理
"""

import os
import sqlite3
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# MySQL连接器
MYSQL_AVAILABLE = False
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    # 如果导入失败，将mysql设为None以避免后续属性访问错误
    mysql = None

# PostgreSQL连接器
POSTGRES_AVAILABLE = False
try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    psycopg2 = None

class DatabaseManager:
    """数据库连接管理器"""
    
    def __init__(self, config_path: str = "config/apps/backend.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载数据库配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件不存在: {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            return {}
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        db_config = self.config.get("database", {})
        db_type = db_config.get("type", "sqlite")
        
        if db_type == "sqlite":
            return db_config.get("sqlite", {})
        elif db_type == "mysql":
            return db_config.get("mysql", {})
        elif db_type == "postgresql":
            return db_config.get("postgresql", {})
        else:
            return db_config
    
    def get_connection_string(self) -> str:
        """获取数据库连接字符串"""
        db_config = self.config.get("database", {})
        db_type = db_config.get("type", "sqlite")
        
        if db_type == "sqlite":
            sqlite_config = db_config.get("sqlite", {})
            db_path = sqlite_config.get("path", "./data/devices.db")
            # 使用绝对路径
            if not os.path.isabs(db_path):
                db_path = os.path.join(os.getcwd(), db_path)
            return f"sqlite:///{db_path}"
        
        elif db_type == "mysql":
            mysql_config = db_config.get("mysql", {})
            host = mysql_config.get("host", "localhost")
            port = mysql_config.get("port", 3306)
            user = mysql_config.get("user", "")
            password = mysql_config.get("password", "")
            database = mysql_config.get("database", "")
            charset = mysql_config.get("charset", "utf8mb4")
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}"
        
        elif db_type == "postgresql":
            pg_config = db_config.get("postgresql", {})
            host = pg_config.get("host", "localhost")
            port = pg_config.get("port", 5432)
            user = pg_config.get("user", "")
            password = pg_config.get("password", "")
            database = pg_config.get("database", "")
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        else:
            return f"sqlite:///./data/devices.db"
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        db_config = self.config.get("database", {})
        db_type = db_config.get("type", "sqlite")
        
        # 确保有默认配置
        if not db_config:
            db_config = {"type": "sqlite", "sqlite": {"path": "./data/devices.db"}}
            db_type = "sqlite"
        
        try:
            if db_type == "sqlite":
                return self._test_sqlite_connection(db_config)
            elif db_type == "mysql":
                return self._test_mysql_connection(db_config)
            elif db_type == "postgresql":
                return self._test_postgresql_connection(db_config)
            else:
                print(f"❌ 不支持的数据库类型: {db_type}")
                return False
        except Exception as e:
            print(f"❌ 数据库连接测试失败: {type(e).__name__}: {e}")
            return False
    
    def _test_sqlite_connection(self, db_config: Dict[str, Any]) -> bool:
        """测试SQLite连接"""
        try:
            sqlite_config = db_config.get("sqlite", {})
            db_path = sqlite_config.get("path", "./data/devices.db")
            
            # 使用绝对路径
            if not os.path.isabs(db_path):
                db_path = os.path.join(os.getcwd(), db_path)
            
            # 检查父目录是否存在且可写
            db_dir = os.path.dirname(db_path)
            if not os.path.exists(db_dir):
                try:
                    os.makedirs(db_dir, exist_ok=True)
                except (OSError, PermissionError) as e:
                    print(f"❌ 无法创建数据库目录: {e}")
                    return False
            
            # 检查文件权限（如果文件已存在）
            if os.path.exists(db_path) and not os.access(db_path, os.R_OK | os.W_OK):
                print(f"❌ 数据库文件无读写权限: {db_path}")
                return False
            
            # 测试连接
            conn = None
            try:
                conn = sqlite3.connect(db_path, timeout=10.0)
                conn.execute("SELECT 1")
                print(f"✅ SQLite连接成功: {db_path}")
                return True
            except sqlite3.Error as e:
                print(f"❌ SQLite数据库错误: {e}")
                return False
            finally:
                if conn:
                    conn.close()
                    
        except (OSError, PermissionError) as e:
            print(f"❌ 文件系统错误: {e}")
            return False
        except Exception as e:
            print(f"❌ SQLite连接异常: {type(e).__name__}: {e}")
            return False
    
    def _test_mysql_connection(self, db_config: Dict[str, Any]) -> bool:
        """测试MySQL连接"""
        if not MYSQL_AVAILABLE:
            print("❌ MySQL连接器未安装: pip install mysql-connector-python")
            return False
        
        mysql_config = db_config.get("mysql", {})
        
        # 验证必要参数
        required_fields = ["host", "port", "user", "password", "database"]
        missing_fields = [field for field in required_fields if not mysql_config.get(field)]
        
        if missing_fields:
            print(f"❌ MySQL配置缺少: {', '.join(missing_fields)}")
            return False
        
        conn = None
        cursor = None
        try:
            # 建立连接
            if MYSQL_AVAILABLE and mysql and mysql.connector:
                conn = mysql.connector.connect(
                    host=mysql_config.get("host"),
                    port=int(mysql_config.get("port", 3306)),
                    user=mysql_config.get("user"),
                    password=mysql_config.get("password"),
                    database=mysql_config.get("database"),
                    charset=mysql_config.get("charset", "utf8mb4"),
                    connect_timeout=10,
                    autocommit=True
                )
            else:
                raise Exception("MySQL连接器不可用")
            
            # 测试查询
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            print(f"✅ MySQL连接成功: {mysql_config['host']}:{mysql_config['port']}")
            return True
            
        except Exception as e:
            # 通过字符串匹配检查异常类型，避免在模块未导入时访问其属性
            if "mysql.connector" in str(type(e)):
                if "DatabaseError" in str(type(e)):
                    # 数据库相关错误
                    error_code = getattr(e, 'errno', None)
                    sqlstate = getattr(e, 'sqlstate', None)
                    print(f"❌ MySQL数据库错误: [{error_code}] {e} (SQLState: {sqlstate})")
                    return False
                elif "InterfaceError" in str(type(e)):
                    # 接口错误（如连接问题）
                    print(f"❌ MySQL连接错误: {e}")
                    return False
            
            # 其他异常
            print(f"❌ MySQL连接异常: {type(e).__name__}: {e}")
            return False
            
        finally:
            # 确保资源被正确清理
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
    
    def _test_postgresql_connection(self, db_config: Dict[str, Any]) -> bool:
        """测试PostgreSQL连接"""
        if not POSTGRES_AVAILABLE:
            print("❌ PostgreSQL连接器未安装: pip install psycopg2-binary")
            return False
        
        pg_config = db_config.get("postgresql", {})
        
        # 验证必要参数
        required_fields = ["host", "port", "user", "password", "database"]
        missing_fields = [field for field in required_fields if not pg_config.get(field)]
        
        if missing_fields:
            print(f"❌ PostgreSQL配置缺少: {', '.join(missing_fields)}")
            return False
        
        conn = None
        cursor = None
        try:
            if POSTGRES_AVAILABLE and psycopg2:
                conn = psycopg2.connect(
                    host=pg_config.get("host", "localhost"),
                    port=int(pg_config.get("port", 5432)),
                    user=pg_config.get("user", ""),
                    password=pg_config.get("password", ""),
                    database=pg_config.get("database", ""),
                    connect_timeout=10
                )
            else:
                raise Exception("PostgreSQL连接器不可用")
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            print(f"✅ PostgreSQL连接成功: {pg_config['host']}:{pg_config['port']}")
            return True
            
        except Exception as e:
            # 通过字符串匹配检查异常类型，避免在模块未导入时访问其属性
            if "psycopg2" in str(type(e)):
                if "OperationalError" in str(type(e)):
                    # 操作错误（连接失败等）
                    print(f"❌ PostgreSQL连接失败: {e}")
                    return False
                elif "DatabaseError" in str(type(e)):
                    # 数据库错误
                    print(f"❌ PostgreSQL数据库错误: {e}")
                    return False
            
            # 其他异常
            print(f"❌ PostgreSQL连接异常: {type(e).__name__}: {e}")
            return False
            
        finally:
            # 确保资源被正确清理
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def show_config(self):
        """显示当前数据库配置"""
        db_config = self.config.get("database", {})
        db_type = db_config.get("type", "sqlite")
        
        print("📊 数据库配置信息")
        print("=" * 50)
        print(f"数据库类型: {db_type}")
        print(f"连接字符串: {self.get_connection_string()}")
        
        if db_type == "sqlite":
            sqlite_config = db_config.get("sqlite", {})
            print(f"数据库路径: {sqlite_config.get('path', './data/devices.db')}")
            print(f"超时时间: {sqlite_config.get('timeout', 10.0)}秒")
        
        elif db_type == "mysql":
            mysql_config = db_config.get("mysql", {})
            print(f"主机: {mysql_config.get('host', 'localhost')}:{mysql_config.get('port', 3306)}")
            print(f"数据库: {mysql_config.get('database', '')}")
            print(f"用户: {mysql_config.get('user', '')}")
        
        elif db_type == "postgresql":
            pg_config = db_config.get("postgresql", {})
            print(f"主机: {pg_config.get('host', 'localhost')}:{pg_config.get('port', 5432)}")
            print(f"数据库: {pg_config.get('database', '')}")
            print(f"用户: {pg_config.get('user', '')}")
        
        print(f"备份路径: {db_config.get('backup_path', './data/backups/')}")
        print(f"自动备份: {db_config.get('auto_backup', True)}")
        print(f"连接池大小: {db_config.get('connection_pool_size', 20)}")
        print("=" * 50)
    
    def init_database(self):
        """初始化数据库"""
        db_config = self.config.get("database", {})
        db_type = db_config.get("type", "sqlite")
        
        if db_type == "sqlite":
            sqlite_config = db_config.get("sqlite", {})
            db_path = sqlite_config.get("path", "./data/devices.db")
            if not os.path.isabs(db_path):
                db_path = os.path.join(os.getcwd(), db_path)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # 初始化数据库结构
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 创建设备表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT NOT NULL,
                    store TEXT NOT NULL,
                    ip TEXT NOT NULL,
                    port INTEGER DEFAULT 554,
                    user TEXT NOT NULL,
                    pwd TEXT NOT NULL,
                    chs INTEGER DEFAULT 1,
                    name TEXT,
                    protocol TEXT DEFAULT 'rtsp',
                    status TEXT DEFAULT 'offline',
                    last_seen TIMESTAMP,
                    last_check TIMESTAMP,
                    check_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    source TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 插入默认管理员用户
            import hashlib
            admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password_hash, role) 
                VALUES (?, ?, ?)
            ''', ("admin", admin_hash, "admin"))
            
            conn.commit()
            conn.close()
            print("✅ 数据库初始化完成")
        else:
            print(f"📝 请手动初始化 {db_type} 数据库")

def main():
    parser = argparse.ArgumentParser(description="数据库连接管理工具")
    parser.add_argument("--config", default="config/apps/backend.json", help="配置文件路径")
    parser.add_argument("--test", action="store_true", help="测试数据库连接")
    parser.add_argument("--init", action="store_true", help="初始化数据库")
    parser.add_argument("--show", action="store_true", help="显示配置信息")
    
    args = parser.parse_args()
    
    manager = DatabaseManager(args.config)
    
    if args.test:
        manager.test_connection()
    elif args.init:
        manager.init_database()
    elif args.show:
        manager.show_config()
    else:
        manager.show_config()
        manager.test_connection()

if __name__ == "__main__":
    main()