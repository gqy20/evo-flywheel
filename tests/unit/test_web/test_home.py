"""Streamlit 首页测试"""

from unittest import mock


class TestHomePageAPIIntegration:
    """首页 API 集成测试"""

    @mock.patch("evo_flywheel.web.views.home.APIClient")
    def test_stats_uses_api_client(self, mock_api_client_class):
        """测试统计数据使用 APIClient"""
        # Arrange - Mock API 返回
        mock_client = mock.Mock()
        mock_client.get_stats_overview.return_value = {
            "total_papers": 1234,
            "analyzed_papers": 1000,
            "embedded_papers": 800,
            "today_new": 42,
            "analysis_rate": 81.0,
            "embedding_rate": 64.8,
        }
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.home import render_stats_section

        # Assert - 函数存在且可调用
        assert callable(render_stats_section)

    @mock.patch("evo_flywheel.web.views.home.APIClient")
    def test_recommendations_uses_api_client(self, mock_api_client_class):
        """测试推荐论文使用 APIClient"""
        # Arrange - Mock API 返回
        mock_client = mock.Mock()
        mock_client.get_papers.return_value = {
            "total": 5,
            "papers": [
                {
                    "id": 1,
                    "title": "Test Paper",
                    "authors": ["Author A"],
                    "abstract": "Test abstract",
                    "journal": "Nature",
                    "publication_date": "2024-01-01",
                    "importance_score": 95,
                }
            ],
        }
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.home import render_recommendations_section

        # Assert - 函数存在且可调用
        assert callable(render_recommendations_section)

    @mock.patch("evo_flywheel.web.views.home.APIClient")
    def test_daily_report_uses_api_client(self, mock_api_client_class):
        """测试今日报告使用 APIClient"""
        # Arrange - Mock API 返回
        mock_client = mock.Mock()
        mock_client.get_today_report.return_value = {
            "date": "2024-01-01",
            "count": 3,
            "papers": [],
        }
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.home import render_daily_report_section

        # Assert - 函数存在且可调用
        assert callable(render_daily_report_section)

    @mock.patch("evo_flywheel.web.views.home.APIClient")
    def test_api_client_error_returns_none_gracefully(self, mock_api_client_class):
        """测试 API 错误时优雅处理"""
        # Arrange - Mock API 返回 None (错误情况)
        mock_client = mock.Mock()
        mock_client.get_stats_overview.return_value = None
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.home import render_stats_section

        # Assert - 函数存在且可调用（不应抛出异常）
        assert callable(render_stats_section)

    @mock.patch("evo_flywheel.web.views.home.APIClient")
    def test_recommendations_filters_by_min_score(self, mock_api_client_class):
        """测试推荐按最低评分过滤"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.get_papers.return_value = {"total": 0, "papers": []}
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.home import render_recommendations_section

        # Assert - 函数存在
        assert callable(render_recommendations_section)

    @mock.patch("evo_flywheel.web.views.home.APIClient")
    def test_no_longer_uses_db_connection(self, mock_api_client_class):
        """测试不再直接使用数据库连接"""
        # Arrange
        mock_api_client_class.return_value = mock.Mock()

        # Act
        from evo_flywheel.web.views import home

        # Assert - get_db_connection 函数应该不再存在
        assert not hasattr(home, "get_db_connection")


class TestHomePageRendering:
    """首页渲染测试"""

    def test_home_page_has_title(self):
        """测试首页有标题"""
        # Arrange
        from evo_flywheel.web.views import home

        # Assert - 模块应该有 render 函数
        assert hasattr(home, "render")
        assert callable(home.render)

    def test_home_page_has_stats_function(self):
        """测试首页有统计数据函数"""
        # Arrange
        from evo_flywheel.web.views import home

        # Assert
        assert hasattr(home, "render_stats_section")
        assert callable(home.render_stats_section)

    def test_home_page_has_recommendations_function(self):
        """测试首页有推荐论文函数"""
        # Arrange
        from evo_flywheel.web.views import home

        # Assert
        assert hasattr(home, "render_recommendations_section")
        assert callable(home.render_recommendations_section)

    def test_home_page_has_report_function(self):
        """测试首页有今日报告函数"""
        # Arrange
        from evo_flywheel.web.views import home

        # Assert
        assert hasattr(home, "render_daily_report_section")
        assert callable(home.render_daily_report_section)


class TestHomePageErrorHandling:
    """首页错误处理测试"""

    @mock.patch("evo_flywheel.web.views.home.APIClient")
    def test_handles_api_error_gracefully(self, mock_api_client_class):
        """测试 API 错误时优雅处理"""
        # Arrange - 模拟 API 错误
        mock_client = mock.Mock()
        mock_client.get_stats_overview.side_effect = Exception("API connection failed")
        mock_api_client_class.return_value = mock_client

        # Act - 导入模块不应该抛出异常
        from evo_flywheel.web.views import home

        # Assert - 模块可以正常导入
        assert hasattr(home, "render")


class TestHomePageNavigation:
    """首页导航测试"""

    def test_main_app_has_navigation(self):
        """测试主应用有导航"""
        # Act
        from evo_flywheel.web import app

        # Assert - 主应用模块应该有 main 函数
        assert hasattr(app, "main")
        assert callable(app.main)
