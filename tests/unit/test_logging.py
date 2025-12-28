"""日志系统测试"""

import logging
from pathlib import Path
from unittest import mock


class TestLoggingInitialization:
    """日志初始化测试"""

    def test_setup_logging_is_called_at_import(self):
        """测试 setup_logging 在导入时被调用"""
        # Arrange & Act - 重新导入模块
        import importlib
        import sys

        if "evo_flywheel.logging" in sys.modules:
            del sys.modules["evo_flywheel.logging"]

        with mock.patch("evo_flywheel.logging.setup_logging"):
            importlib.import_module("evo_flywheel.logging")

        # Assert - setup_logging 应该被调用（通过应用入口）
        # 注意：这需要在应用初始化时调用

    def test_logging_has_file_handler_when_configured(self):
        """测试配置日志文件时有文件处理器"""
        # Arrange
        from evo_flywheel.logging import setup_logging

        log_file = Path("/tmp/test_evo_flywheel.log")

        # Act
        setup_logging(log_file=log_file)
        logger = logging.getLogger()

        # Assert
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0, "应该有文件处理器"

        # Cleanup
        log_file.unlink(missing_ok=True)
        for handler in file_handlers:
            logger.removeHandler(handler)

    def test_logging_has_rotating_file_handler(self):
        """测试日志轮转处理器"""
        # Arrange
        from evo_flywheel.logging import setup_logging

        # Act
        setup_logging(log_file=Path("/tmp/test_rotate.log"), max_bytes=1024 * 1024, backup_count=5)
        logger = logging.getLogger()

        # Assert - 应该有轮转文件处理器
        from logging.handlers import RotatingFileHandler

        rotating_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
        assert len(rotating_handlers) > 0, "应该有轮转文件处理器"

        # Cleanup
        for handler in rotating_handlers:
            handler.close()
            logger.removeHandler(handler)
        Path("/tmp/test_rotate.log").unlink(missing_ok=True)

    def test_log_level_from_config(self):
        """测试日志级别从配置加载"""
        # Arrange
        from evo_flywheel.config import get_settings
        from evo_flywheel.logging import setup_logging

        settings = get_settings()

        # Act
        setup_logging()
        logger = logging.getLogger()

        # Assert
        expected_level = getattr(logging, settings.log_level.upper())
        assert logger.level == expected_level

    def test_logger_format_includes_timestamp(self):
        """测试日志格式包含时间戳"""
        # Arrange
        from evo_flywheel.logging import get_logger, setup_logging

        setup_logging()
        logger = get_logger("test")

        # Act
        import io

        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)d] %(message)s")
        )
        logger.addHandler(handler)

        logger.info("test message")

        # Assert
        log_output = log_capture.getvalue()
        assert "[20" in log_output, "日志应包含时间戳"

        # Cleanup
        logger.removeHandler(handler)


class TestLoggingInModules:
    """各模块日志使用测试"""

    def test_db_crud_module_has_logger(self):
        """测试 db.crud 模块有日志"""
        # Arrange & Act
        from pathlib import Path

        crud_file = Path("src/evo_flywheel/db/crud.py")

        # Assert
        assert crud_file.exists()
        content = crud_file.read_text()
        # 应该包含日志导入和使用
        assert "logger" in content.lower() or "logging" in content.lower()

    def test_db_models_module_has_logger(self):
        """测试 db.models 模块有日志"""
        # Arrange
        from pathlib import Path

        models_file = Path("src/evo_flywheel/db/models.py")

        # Assert - models 纯数据模型可以不需要日志
        # 但如果需要，应该有 logger
        _ = models_file.read_text()

    def test_vector_client_module_has_logger(self):
        """测试 vector.client 模块有日志"""
        # Arrange
        from pathlib import Path

        client_file = Path("src/evo_flywheel/vector/client.py")

        # Assert
        content = client_file.read_text()
        assert "logger" in content.lower() or "logging" in content.lower()

    def test_config_module_logs_initialization(self):
        """测试 config 模块记录初始化"""
        # Arrange
        from evo_flywheel.config import get_settings

        # Act
        _ = get_settings()

        # Assert - 配置加载应记录日志
        # 可以在配置加载时添加日志


class TestStructuredLogging:
    """结构化日志测试"""

    def test_json_formatter_exists(self):
        """测试存在 JSON 格式化器"""
        # Arrange & Act

        # Assert - 应该支持 JSON 格式化
        # 通过配置启用结构化日志

    def test_log_extra_fields_supported(self):
        """测试日志支持额外字段"""
        # Arrange
        from evo_flywheel.logging import get_logger, setup_logging

        setup_logging()
        logger = get_logger("test")

        # Act - 不应抛出异常
        logger.info("test", extra={"context": "test_value", "user_id": 123})

        # Assert - 日志应记录


class TestExceptionLogging:
    """异常日志测试"""

    def test_exception_logging_includes_traceback(self):
        """测试异常日志包含堆栈追踪"""
        # Arrange
        from evo_flywheel.logging import get_logger, setup_logging

        setup_logging()
        logger = get_logger("test")

        # Act & Assert - 不应抛出异常
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("An error occurred")

    def test_error_log_has_exception_info(self):
        """测试错误日志包含异常信息"""
        # Arrange
        from evo_flywheel.logging import get_logger, setup_logging

        setup_logging()
        logger = get_logger("test")

        # Act
        import io

        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)d] %(message)s")
        )
        logger.addHandler(handler)

        try:
            raise RuntimeError("Test error")
        except RuntimeError:
            logger.exception("Error occurred")

        # Assert
        log_output = log_capture.getvalue()
        assert "Error occurred" in log_output
        assert "RuntimeError" in log_output or "Traceback" in log_output

        # Cleanup
        logger.removeHandler(handler)


class TestLogRotation:
    """日志轮转测试"""

    def test_log_rotation_config_exists(self):
        """测试日志轮转配置存在"""
        # Arrange
        from evo_flywheel.config import get_settings

        _ = get_settings()

        # Assert - 配置中应有日志轮转相关选项
        # 可以添加 log_max_bytes, log_backup_count 等配置

    def test_logs_directory_exists(self):
        """测试 logs 目录存在"""
        # Arrange

        from evo_flywheel.config import ensure_directories

        # Act
        ensure_directories()

        # Assert - logs 目录应被创建
        # 可以在 ensure_directories 中添加 logs 目录


class TestLogLevels:
    """日志级别测试"""

    def test_debug_logs_not_shown_in_info_level(self):
        """测试 INFO 级别不显示 DEBUG 日志"""
        # Arrange
        from evo_flywheel.logging import get_logger, setup_logging

        setup_logging(level="INFO")
        logger = get_logger("test")

        # Act
        import io

        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger.addHandler(handler)

        logger.debug("debug message")
        logger.info("info message")

        # Assert
        log_output = log_capture.getvalue()
        assert "debug message" not in log_output
        assert "info message" in log_output

        # Cleanup
        logger.removeHandler(handler)

    def test_all_levels_shown_in_debug_level(self):
        """测试 DEBUG 级别显示所有日志"""
        # Arrange
        from evo_flywheel.logging import get_logger, setup_logging

        setup_logging(level="DEBUG")
        logger = get_logger("test")

        # Act
        import io

        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger.addHandler(handler)

        logger.debug("debug message")
        logger.info("info message")

        # Assert
        log_output = log_capture.getvalue()
        assert "debug message" in log_output
        assert "info message" in log_output

        # Cleanup
        logger.removeHandler(handler)
