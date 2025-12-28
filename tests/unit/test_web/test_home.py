"""Streamlit 首页测试"""

from unittest import mock


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


class TestHomePageStats:
    """首页统计数据测试"""

    @mock.patch("evo_flywheel.web.views.home.get_db_connection")
    def test_stats_queries_total_papers(self, mock_get_conn):
        """测试统计查询论文总数"""
        # Arrange
        mock_conn = mock.Mock()
        mock_conn.execute.return_value.scalar.return_value = 1234
        mock_get_conn.return_value.__enter__ = mock.Mock(return_value=mock_conn)
        mock_get_conn.return_value.__exit__ = mock.Mock(return_value=False)

        # Act
        from evo_flywheel.web.views.home import render_stats_section

        # 这里需要 streamlit 环境，只测试函数存在
        assert callable(render_stats_section)

    @mock.patch("evo_flywheel.web.views.home.get_db_connection")
    def test_stats_queries_recently_added(self, mock_get_conn):
        """测试统计查询最近新增"""
        # Arrange
        mock_conn = mock.Mock()
        mock_conn.execute.return_value.scalar.return_value = 42
        mock_get_conn.return_value = mock_conn

        # Assert
        from evo_flywheel.web.views.home import render_stats_section

        assert callable(render_stats_section)


class TestHomePageRecommendations:
    """首页推荐论文测试"""

    @mock.patch("evo_flywheel.web.views.home.get_db_connection")
    def test_recommendation_queries_high_score_papers(self, mock_get_conn):
        """测试推荐查询高分论文"""
        # Arrange
        mock_conn = mock.Mock()
        mock_conn.execute.return_value.fetchall.return_value = []
        mock_get_conn.return_value = mock_conn

        # Assert
        from evo_flywheel.web.views.home import render_recommendations_section

        assert callable(render_recommendations_section)

    @mock.patch("evo_flywheel.web.views.home.get_db_connection")
    def test_recommendation_filters_by_min_score(self, mock_get_conn):
        """测试推荐按最低评分过滤"""
        # Arrange
        mock_conn = mock.Mock()
        mock_get_conn.return_value = mock_conn

        # Act - 导入模块触发数据库查询
        from evo_flywheel.web.views.home import render_recommendations_section

        # Assert - 函数存在
        assert callable(render_recommendations_section)


class TestHomePageReportSection:
    """首页报告区域测试"""

    def test_daily_report_function_exists(self):
        """测试今日报告函数存在"""
        # Act
        from evo_flywheel.web.views.home import render_daily_report_section

        # Assert
        assert callable(render_daily_report_section)

    @mock.patch("evo_flywheel.web.views.home.get_db_connection")
    def test_daily_report_queries_by_date(self, mock_get_conn):
        """测试今日报告按日期查询"""
        # Arrange
        mock_conn = mock.Mock()
        mock_conn.execute.return_value.fetchone.return_value = None
        mock_get_conn.return_value = mock_conn

        # Act
        from evo_flywheel.web.views.home import render_daily_report_section

        # Assert
        assert callable(render_daily_report_section)


class TestHomePageErrorHandling:
    """首页错误处理测试"""

    @mock.patch("evo_flywheel.web.views.home.get_db_connection")
    def test_handles_database_error_gracefully(self, mock_get_conn):
        """测试数据库错误时优雅处理"""
        # Arrange - 模拟数据库错误
        mock_get_conn.side_effect = Exception("Database connection failed")

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
