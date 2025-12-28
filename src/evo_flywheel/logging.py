"""日志配置模块

配置统一的日志格式和输出
"""

import logging
import sys
from pathlib import Path

from evo_flywheel.config import get_settings


def setup_logging(
    level: str | None = None,
    log_file: Path | None = None,
    format_string: str | None = None,
) -> None:
    """配置日志系统

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径 (可选)
        format_string: 自定义日志格式 (可选)
    """
    settings = get_settings()
    log_level = level or settings.log_level

    # 默认格式
    if format_string is None:
        format_string = "[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)d] %(message)s"

    # 创建 formatter
    formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 清除现有 handlers
    root_logger.handlers.clear()

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件 handler (可选)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器

    Args:
        name: 日志记录器名称 (通常使用 __name__)

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    return logging.getLogger(name)
