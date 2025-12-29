"""配置管理单元测试 - API 配置"""

from unittest.mock import patch


class TestAPIConfig:
    """API 配置测试"""

    @patch("evo_flywheel.config.get_settings")
    def test_api_client_has_api_base_url(self, mock_get_settings):
        """测试 APIClient 能够从 Settings 读取 api_base_url"""
        # Mock settings with api_base_url
        from evo_flywheel.config import Settings

        mock_settings = Settings(
            api_base_url="http://localhost:8000",
            database_url="sqlite:///test.db",
        )
        mock_get_settings.return_value = mock_settings

        from evo_flywheel.web.api_client import APIClient

        client = APIClient()

        assert client.base_url == "http://localhost:8000"

    @patch("evo_flywheel.config.get_settings")
    def test_api_client_fallback_to_default(self, mock_get_settings):
        """测试 APIClient 在没有 api_base_url 时使用默认值"""
        # Mock settings without api_base_url
        from evo_flywheel.config import Settings

        mock_settings = Settings(
            database_url="sqlite:///test.db",
        )
        mock_get_settings.return_value = mock_settings

        from evo_flywheel.web.api_client import APIClient

        client = APIClient()

        assert client.base_url == "http://localhost:8000"
