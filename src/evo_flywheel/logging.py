"""日志配置模块

配置统一的日志格式和输出，支持文件轮转和结构化日志
"""

import json
import logging
import logging.handlers
import sys
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

from evo_flywheel.config import get_settings


class JSONFormatter(logging.Formatter):
    """JSON 结构化日志格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为 JSON

        Args:
            record: 日志记录

        Returns:
            str: JSON 格式的日志字符串
        """
        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, Mapping):
            log_data.update(record.extra_fields)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    level: str | None = None,
    log_file: Path | None = None,
    format_string: str | None = None,
    json_format: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """配置日志系统

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径 (可选)
        format_string: 自定义日志格式 (可选)
        json_format: 是否使用 JSON 格式 (默认 False)
        max_bytes: 日志轮转的最大字节数 (默认 10MB)
        backup_count: 保留的备份文件数量 (默认 5)
    """
    settings = get_settings()
    log_level = level or settings.log_level

    # 默认格式
    if format_string is None:
        format_string = "[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)d] %(message)s"

    # 创建 formatter
    formatter: logging.Formatter
    if json_format:
        formatter = JSONFormatter()
    else:
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

    # 文件 handler (带轮转)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
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


class LoggerAdapter(logging.LoggerAdapter):
    """日志适配器，支持额外的上下文字段"""

    def process(self, msg: Any, kwargs: Any) -> tuple[Any, Any]:
        """处理日志消息

        Args:
            msg: 日志消息
            kwargs: 额外的关键字参数

        Returns:
            tuple: 处理后的消息和参数
        """
        # 提取 extra 字段
        extra = kwargs.pop("extra", {})
        if extra:
            # 将 extra 字段添加到记录中
            if "extra" in kwargs:
                kwargs["extra"].update(extra)
            else:
                kwargs["extra"] = extra

        return msg, kwargs


def get_logger_with_context(name: str, **context: Any) -> logging.LoggerAdapter:
    """获取带上下文的日志记录器

    Args:
        name: 日志记录器名称
        **context: 上下文字段

    Returns:
        logging.LoggerAdapter: 带上下文的日志适配器
    """
    logger = get_logger(name)
    return LoggerAdapter(logger, context)


def init_logging() -> None:
    """初始化日志系统 (应用入口调用)

    从配置读取日志设置并初始化日志系统。
    应该在应用启动时调用此函数。
    """
    settings = get_settings()

    # 从环境变量或配置获取日志文件路径
    log_file_str = getattr(settings, "log_file", None)
    log_file: Path | None = Path(log_file_str) if log_file_str else None

    # 初始化日志系统
    setup_logging(
        log_file=log_file,
        max_bytes=getattr(settings, "log_max_bytes", 10 * 1024 * 1024),
        backup_count=getattr(settings, "log_backup_count", 5),
        json_format=getattr(settings, "log_json_format", False),
    )
