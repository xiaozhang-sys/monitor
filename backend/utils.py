"""
后端服务工具模块
包含通用工具函数和装饰器
"""

import logging
import traceback
import functools
import sqlite3
from typing import Callable, Any
from fastapi import HTTPException, status

# 配置日志
logger = logging.getLogger(__name__)


def handle_exceptions(func: Callable) -> Callable:
    """统一异常处理装饰器
    
    用于包装API端点函数，自动处理各种异常并返回适当的HTTP响应
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # 重新抛出FastAPI的HTTP异常
            raise
        except sqlite3.Error as e:
            logger.error(f"数据库错误在 {func.__name__}: {e}")
            logger.debug(f"详细错误信息:\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="数据库操作失败"
            )
        except Exception as e:
            logger.error(f"未处理的异常在 {func.__name__}: {e}")
            logger.debug(f"详细错误信息:\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="服务器内部错误"
            )
    return wrapper


def retry_operation(max_retries: int = 3, delay: float = 1.0):
    """重试操作装饰器
    
    用于可能失败的操作，如网络请求或数据库操作
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"{func.__name__} 失败 (尝试 {attempt + 1}/{max_retries}): {e}"
                        )
                        import asyncio
                        await asyncio.sleep(delay * (2 ** attempt))  # 指数退避
                    else:
                        logger.error(
                            f"{func.__name__} 在 {max_retries} 次尝试后仍然失败: {e}"
                        )
                        logger.debug(f"详细错误信息:\n{traceback.format_exc()}")
            
            # 如果所有重试都失败了，抛出最后一个异常
            if last_exception:
                raise last_exception
            # 如果没有捕获到异常但仍然需要抛出，则抛出通用异常
            raise Exception(f"{func.__name__} 在 {max_retries} 次尝试后仍然失败")
        return wrapper
    return decorator