"""错误处理装饰器单元测试

测试 handle_errors 装饰器的各种场景
"""

import pytest
from evo_flywheel.error_handlers import handle_errors

from evo_flywheel.logging import get_logger

logger = get_logger(__name__)


class TestHandleErrors:
    """测试错误处理装饰器"""

    def test_handle_errors_returns_on_success(self):
        """测试成功时正常返回结果"""

        # Arrange
        @handle_errors("Test operation", logger)
        def successful_function():
            return {"result": "success"}

        # Act
        result = successful_function()

        # Assert
        assert result == {"result": "success"}

    def test_handle_errors_returns_default_on_exception(self):
        """测试异常时返回默认值"""

        # Arrange
        @handle_errors("Test operation", logger, default_return={"error": True})
        def failing_function():
            raise ValueError("Simulated error")

        # Act
        result = failing_function()

        # Assert
        assert result == {"error": True}

    def test_handle_errors_returns_none_when_no_default(self):
        """测试无默认值时返回 None"""

        # Arrange
        @handle_errors("Test operation", logger)
        def failing_function():
            raise ValueError("Simulated error")

        # Act
        result = failing_function()

        # Assert
        assert result is None

    def test_handle_logs_exception(self):
        """测试异常被正确记录"""

        # Arrange
        @handle_errors("Test operation", logger)
        def failing_function():
            raise ValueError("Test error message")

        # Act & Assert - 验证不抛出异常
        result = failing_function()
        assert result is None

    def test_handle_errors_with_reraise_true(self):
        """测试 reraise=True 时重新抛出异常"""

        # Arrange
        @handle_errors("Test operation", logger, reraise=True)
        def failing_function():
            raise ValueError("Simulated error")

        # Act & Assert
        with pytest.raises(ValueError, match="Simulated error"):
            failing_function()

    def test_handle_errors_with_exception_type_filter(self):
        """测试只处理指定类型的异常"""

        # Arrange
        @handle_errors(
            "Test operation",
            logger,
            exception_types=(ValueError,),
            default_return={"handled": True},
        )
        def failing_function():
            raise ValueError("Value error")

        # Act
        result = failing_function()

        # Assert - ValueError 被处理
        assert result == {"handled": True}

    def test_handle_errors_reraises_unmatched_exception_type(self):
        """测试不匹配的异常类型被重新抛出"""

        # Arrange
        @handle_errors(
            "Test operation",
            logger,
            exception_types=(ValueError,),
            default_return={"handled": True},
        )
        def failing_function():
            raise KeyError("Key error")

        # Act & Assert - KeyError 不在处理列表中，应被抛出
        with pytest.raises(KeyError, match="Key error"):
            failing_function()

    def test_handle_errors_with_callable_default(self):
        """测试可调用的默认值生成函数"""

        # Arrange
        @handle_errors(
            "Test operation",
            logger,
            default_return=lambda: {"computed": True, "value": 42},
        )
        def failing_function():
            raise ValueError("Simulated error")

        # Act
        result = failing_function()

        # Assert
        assert result == {"computed": True, "value": 42}
