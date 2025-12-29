"""首页管理面板测试"""

from unittest import mock


class TestHomeAdminPanel:
    """首页管理面板测试"""

    def test_home_has_render_admin_panel_function(self):
        """测试首页有管理面板渲染函数"""
        # Arrange & Act
        from evo_flywheel.web.views import home

        # Assert
        assert hasattr(home, "render_admin_panel")
        assert callable(home.render_admin_panel)

    @mock.patch("evo_flywheel.web.views.home.APIClient")
    def test_trigger_analysis_uses_api_client(self, mock_api_client_class):
        """测试触发分析使用 APIClient"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.trigger_analysis.return_value = {
            "analyzed": 10,
            "total": 10,
            "message": "已分析 10 篇论文",
        }
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.home import trigger_analysis

        result = trigger_analysis(limit=10)

        # Assert
        assert result is True

    @mock.patch("evo_flywheel.web.views.home.APIClient")
    def test_trigger_analysis_passes_limit(self, mock_api_client_class):
        """测试触发分析传递限制参数"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.trigger_analysis.return_value = {"analyzed": 5, "total": 5}
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.home import trigger_analysis

        trigger_analysis(limit=20)

        # Assert
        mock_client.trigger_analysis.assert_called_once()
        call_kwargs = mock_client.trigger_analysis.call_args.kwargs
        assert call_kwargs.get("limit") == 20

    @mock.patch("evo_flywheel.web.views.home.APIClient")
    def test_trigger_analysis_handles_api_error(self, mock_api_client_class):
        """测试触发分析处理 API 错误"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.trigger_analysis.return_value = None
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.home import trigger_analysis

        result = trigger_analysis(limit=10)

        # Assert
        assert result is False

    @mock.patch("evo_flywheel.web.views.home.APIClient")
    def test_rebuild_embeddings_uses_api_client(self, mock_api_client_class):
        """测试重建索引使用 APIClient"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.rebuild_embeddings.return_value = {
            "rebuilt": 50,
            "total": 50,
            "skipped": 0,
            "message": "成功向量化 50 篇论文",
        }
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.home import rebuild_embeddings

        result = rebuild_embeddings(force=False)

        # Assert
        assert result is True

    @mock.patch("evo_flywheel.web.views.home.APIClient")
    def test_rebuild_embeddings_passes_force_param(self, mock_api_client_class):
        """测试重建索引传递 force 参数"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.rebuild_embeddings.return_value = {"rebuilt": 10}
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.home import rebuild_embeddings

        rebuild_embeddings(force=True)

        # Assert
        mock_client.rebuild_embeddings.assert_called_once()
        call_kwargs = mock_client.rebuild_embeddings.call_args.kwargs
        assert call_kwargs.get("force") is True

    @mock.patch("evo_flywheel.web.views.home.APIClient")
    def test_rebuild_embeddings_handles_api_error(self, mock_api_client_class):
        """测试重建索引处理 API 错误"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.rebuild_embeddings.return_value = None
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.home import rebuild_embeddings

        result = rebuild_embeddings(force=False)

        # Assert
        assert result is False
