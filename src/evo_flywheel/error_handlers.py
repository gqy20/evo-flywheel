"""错误处理装饰器

提供统一的异常处理和日志记录
"""

import functools
from collections.abc import Callable
from logging import Logger, LoggerAdapter
from typing import Any, TypeVar

from evo_flywheel.logging import get_logger

T = TypeVar("T")


def handle_errors(
    operation_name: str,
    logger: LoggerAdapter | Logger | None = None,
    *,
    default_return: T | Callable[[], T] | None = None,
    reraise: bool = False,
    exception_types: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    """错误处理装饰器

    统一处理函数中的异常，记录日志并返回默认值

    Args:
        operation_name: 操作名称（用于日志记录）
        logger: 日志记录器实例，如果为 None 则使用模块级 logger
        default_return: 异常时返回的默认值，可以是：
            - None（默认）：返回 None
            - 静态值：直接返回
            - 可调用对象：调用后返回结果
        reraise: 是否重新抛出异常（默认 False）
        exception_types: 要处理的异常类型（默认处理所有 Exception）

    Returns:
        装饰后的函数

    Example:
        >>> @handle_errors("数据采集", logger, default_return=[])
        ... def collect_papers():
        ...     return fetch_papers()
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T | None]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T | None:
            # 使用传入的 logger 或创建新的
            _logger = logger or get_logger(func.__module__)

            try:
                return func(*args, **kwargs)
            except exception_types as e:
                # 记录错误日志
                _logger.error(f"{operation_name} failed: {e}")

                # 重新抛出异常（如果配置）
                if reraise:
                    raise

                # 返回默认值
                if callable(default_return):
                    return default_return()
                return default_return

        return wrapper

    return decorator
