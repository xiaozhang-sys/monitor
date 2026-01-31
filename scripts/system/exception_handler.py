#!/usr/bin/env python3
"""
监控系统统一异常处理模块
提供统一的异常处理、日志记录和错误恢复机制
"""

import logging
import traceback
import functools
import time
from typing import Optional, Callable, Any, Tuple, Type, Union
from contextlib import contextmanager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class MonitorError(Exception):
    """监控系统基础异常类"""
    pass


class DeviceConnectionError(MonitorError):
    """设备连接异常"""
    pass


class StreamProcessingError(MonitorError):
    """流处理异常"""
    pass


class ResourceLimitError(MonitorError):
    """资源限制异常"""
    pass


class ConfigurationError(MonitorError):
    """配置错误异常"""
    pass


class RTSPConnectionError(DeviceConnectionError):
    """RTSP连接异常"""
    pass


class FrameCaptureError(StreamProcessingError):
    """帧捕获异常"""
    pass


class RetryManager:
    """重试管理器"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def retry(self, operation_name: str, catch_exceptions: Tuple[Type[Exception], ...] = (Exception,)):
        """装饰器形式的重试机制
        
        Args:
            operation_name: 操作名称
            catch_exceptions: 需要捕获并重试的异常类型元组
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                last_exception = None
                
                for attempt in range(self.max_retries):
                    try:
                        return func(*args, **kwargs)
                    except catch_exceptions as e:
                        last_exception = e
                        if attempt < self.max_retries - 1:  # 不是最后一次尝试
                            # 指数退避算法计算延迟时间
                            delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                            logger.warning(f"{operation_name} 失败 (第 {attempt + 1} 次尝试), {delay}秒后重试: {e}")
                            time.sleep(delay)
                        else:
                            logger.error(f"{operation_name} 在 {self.max_retries} 次尝试后仍然失败: {e}")
                
                # 所有重试都失败后抛出最后一个异常
                if last_exception:
                    raise last_exception
                    
            return wrapper
        return decorator


class ResourceManager:
    """资源管理器"""
    
    @staticmethod
    @contextmanager
    def managed_resource(resource: Any, release_func: Callable):
        """安全资源管理上下文
        
        Args:
            resource: 资源对象
            release_func: 资源释放函数
        """
        exception_occurred = False
        try:
            yield resource
        except Exception as e:
            logger.error(f"使用资源时出错: {e}")
            logger.debug(f"异常详情:\n{traceback.format_exc()}")
            exception_occurred = True
            # 重新抛出异常，让调用者处理
            raise
        finally:
            try:
                if resource is not None:
                    # 只有在使用过程中未发生异常时才释放资源
                    if not exception_occurred:
                        release_func(resource)
                    else:
                        logger.warning("资源使用过程中发生异常，跳过正常资源释放流程")
            except Exception as e:
                logger.error(f"释放资源时出错: {e}")
                logger.debug(f"异常详情:\n{traceback.format_exc()}")


class ErrorHandler:
    """错误处理器"""
    
    @staticmethod
    def handle_exception(e: Exception, context: str = "", reraise: bool = True):
        """统一异常处理
        
        Args:
            e: 异常对象
            context: 异常上下文信息
            reraise: 是否重新抛出异常
        """
        error_msg = f"异常发生在 {context}: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"异常详情:\n{traceback.format_exc()}")
        
        if reraise:
            raise

    @staticmethod
    def safe_execute(func: Callable, *args, default_return: Any = None, **kwargs) -> Any:
        """安全执行函数，捕获异常并返回默认值
        
        Args:
            func: 要执行的函数
            default_return: 默认返回值
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果或默认值
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"执行函数 {func.__name__} 时出错: {e}")
            logger.debug(f"异常详情:\n{traceback.format_exc()}")
            return default_return


# 全局实例
retry_manager = RetryManager()
error_handler = ErrorHandler()
resource_manager = ResourceManager()


def safe_operation(operation_name: str, default_return: Any = None):
    """安全操作装饰器
    
    Args:
        operation_name: 操作名称
        default_return: 默认返回值
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_exception(e, operation_name, reraise=False)
                return default_return
        return wrapper
    return decorator


# 使用示例和测试代码
if __name__ == "__main__":
    # 配置日志级别
    logging.getLogger().setLevel(logging.DEBUG)
    
    print("测试异常处理模块...")
    
    # 测试重试机制
    @retry_manager.retry("测试函数", (ValueError,))
    def test_function(fail_count=2):
        """测试函数"""
        global test_counter
        test_counter += 1
        print(f"  尝试 #{test_counter}")
        
        if test_counter <= fail_count:
            raise ValueError(f"模拟失败 #{test_counter}")
        
        print("  函数执行成功")
        return "success"
    
    # 测试1: 成功重试
    print("\n1. 测试重试机制:")
    test_counter = 0
    try:
        result = test_function(2)
        print(f"   结果: {result}")
    except Exception as e:
        print(f"   最终失败: {e}")
    
    # 测试2: 超过重试次数
    print("\n2. 测试超过重试次数:")
    test_counter = 0
    try:
        result = test_function(5)  # 超过默认重试次数3次
        print(f"   结果: {result}")
    except Exception as e:
        print(f"   正确捕获到最终失败: {e}")
    
    # 测试3: 安全执行
    print("\n3. 测试安全执行:")
    def risky_function():
        raise RuntimeError("模拟运行时错误")
    
    result = error_handler.safe_execute(risky_function, default_return="default_value")
    print(f"   安全执行结果: {result}")
    
    # 测试4: 资源管理
    print("\n4. 测试资源管理:")
    class MockResource:
        def __init__(self, name):
            self.name = name
            print(f"   创建资源: {self.name}")
        
        def close(self):
            print(f"   关闭资源: {self.name}")
    
    def release_resource(resource):
        if hasattr(resource, 'close'):
            resource.close()
        else:
            print(f"资源 {resource} 没有close方法")
    
    try:
        with resource_manager.managed_resource(MockResource("test_resource"), release_resource):
            print("   使用资源中...")
    except Exception as e:
        print(f"   使用资源时出错: {e}")
    
    print("\n所有测试完成")