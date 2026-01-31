"""
后端服务异常处理模块
定义各种自定义异常类和统一的异常处理机制
"""

import logging
from typing import Optional, Dict, Any
import traceback
from fastapi import HTTPException, status

# 配置日志
logger = logging.getLogger(__name__)


class BackendException(Exception):
    """后端服务基础异常类"""
    
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """将异常转换为字典格式"""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class DatabaseException(BackendException):
    """数据库相关异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATABASE_ERROR", details)


class AuthenticationException(BackendException):
    """认证相关异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHENTICATION_ERROR", details)


class AuthorizationException(BackendException):
    """授权相关异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class DeviceException(BackendException):
    """设备相关异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DEVICE_ERROR", details)


class ValidationException(BackendException):
    """数据验证相关异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class NetworkException(BackendException):
    """网络相关异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "NETWORK_ERROR", details)


class ConfigurationException(BackendException):
    """配置相关异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)


class ErrorHandler:
    """统一错误处理器"""
    
    @staticmethod
    def handle_exception(e: Exception, context: str = "", reraise: bool = True) -> Optional[Dict[str, Any]]:
        """统一处理异常
        
        Args:
            e: 异常对象
            context: 异常上下文信息
            reraise: 是否重新抛出异常
            
        Returns:
            错误信息字典或None
        """
        error_msg = f"异常发生在 {context}: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"异常详情:\n{traceback.format_exc()}")
        
        # 根据异常类型返回相应的HTTP状态码和错误信息
        if isinstance(e, BackendException):
            error_response = e.to_dict()
            if isinstance(e, AuthenticationException):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=error_response,
                    headers={"WWW-Authenticate": "Bearer"}
                )
            elif isinstance(e, AuthorizationException):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_response
                )
            elif isinstance(e, ValidationException):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_response
                )
            elif isinstance(e, DeviceException):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_response
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_response
                )
        elif isinstance(e, HTTPException):
            # 直接重新抛出FastAPI的HTTP异常
            if reraise:
                raise
        else:
            # 处理未预期的异常
            error_response = {
                "error": "内部服务器错误",
                "error_code": "INTERNAL_ERROR",
                "details": {"context": context}
            }
            logger.error(f"未处理的异常: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_response
            )
        
        return error_response if not reraise else None


class RetryManager:
    """重试管理器"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def retry(self, operation_name: str, catch_exceptions: tuple = (Exception,)):
        """重试装饰器
        
        Args:
            operation_name: 操作名称
            catch_exceptions: 需要捕获的异常类型元组
        """
        import time
        import functools
        
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(self.max_retries):
                    try:
                        return func(*args, **kwargs)
                    except catch_exceptions as e:
                        last_exception = e
                        if attempt < self.max_retries - 1:
                            delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                            logger.warning(
                                f"{operation_name} 失败 (第 {attempt + 1} 次尝试), "
                                f"{delay}秒后重试: {e}"
                            )
                            time.sleep(delay)
                        else:
                            logger.error(f"{operation_name} 在 {self.max_retries} 次尝试后仍然失败: {e}")
                
                # 所有重试都失败后抛出最后一个异常
                if last_exception:
                    raise last_exception
            return wrapper
        return decorator


# 全局实例
error_handler = ErrorHandler()
retry_manager = RetryManager()