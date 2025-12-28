"""Streamlit 首页测试"""

from unittest import mock

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def home_app() -> AppTest:
    """创建首页测试实例"""
    from evo_flywheel.web.app import main as app

    at = AppTest.from_string(app)
    return at


class TestHomePageRendering:
    """首页渲染测试"""

    def test_home_page_title_displayed(self, home_app):
        """测试首页标题显示"""
        # Act
        home_app.run()

        # Assert
        assert len(home_app.title) > 0
        assert "Evo-Flywheel" in home_app.title[0].value or "进化生物学" in str(home_app.title)

    def test_home_page_has_stats_section(self, home_app):
        """测试首页有统计数据区域"""
        # Act
        home_app.run()

        # Assert - 应该有统计数据展示
        metrics = home_app.metric
        assert len(metrics) >= 3  # 至少 3 个统计指标

    def test_home_page_has_recommendation_section(self, home_app):
        """测试首页有推荐论文区域"""
        # Act
        home_app.run()

        # Assert - 应该有推荐论文卡片
        # 推荐论文通常以 expander 或 card 形式展示
        assert len(home_app.expander) > 0 or len(home_app.columns) > 0


class TestHomePageStats:
    """首页统计数据测试"""

    @mock.patch("evo_flywheel.db.crud.get_papers_count")
    def test_stats_shows_total_papers(self, mock_get_count, home_app):
        """测试统计显示论文总数"""
        # Arrange
        mock_get_count.return_value = 1234

        # Act
        home_app.run()

        # Assert - 统计数据应该包含 1234
        metrics = home_app.metric
        total_papers_found = any("1234" in str(m.value) or m.value == 1234 for m in metrics)
        assert total_papers_found, "未找到论文总数统计"

    @mock.patch("evo_flywheel.db.crud.get_papers_count")
    def test_stats_shows_recently_added(self, mock_get_count, home_app):
        """测试统计显示最近新增"""
        # Arrange
        mock_get_count.return_value = 42

        # Act
        home_app.run()

        # Assert
        metrics = home_app.metric
        assert any("新增" in str(m.label) or "recent" in str(m.label).lower() for m in metrics)


class TestHomePageRecommendations:
    """首页推荐论文测试"""

    @mock.patch("evo_flywheel.db.crud.get_papers")
    def test_recommendation_shows_top_papers(self, mock_get_papers, home_app):
        """测试推荐显示高分论文"""
        # Arrange - 模拟高分论文
        mock_paper = mock.Mock()
        mock_paper.id = 1
        mock_paper.title = "High impact evolutionary biology paper"
        mock_paper.abstract = "This is a test abstract"
        mock_paper.importance_score = 95
        mock_paper.journal = "Nature"
        mock_paper.publication_date = "2024-01-15"
        mock_paper.authors = "Author One, Author Two"

        mock_get_papers.return_value = [mock_paper]

        # Act
        home_app.run()

        # Assert - 应该显示推荐论文
        # 检查是否有论文标题或摘要内容
        text_content = str(home_app.main)
        assert "High impact" in text_content or "evolutionary" in text_content.lower()

    @mock.patch("evo_flywheel.db.crud.get_papers")
    def test_recommendation_filters_by_min_score(self, mock_get_papers, home_app):
        """测试推荐按最低评分过滤"""
        # Arrange
        mock_get_papers.return_value = []

        # Act
        home_app.run()

        # Assert - CRUD 应该被调用且包含 min_importance_score 过滤
        mock_get_papers.assert_called_once()
        call_kwargs = mock_get_papers.call_args.kwargs
        assert "min_importance_score" in call_kwargs
        assert call_kwargs["min_importance_score"] >= 80


class TestHomePageReportSection:
    """首页报告区域测试"""

    def test_home_has_daily_report_section(self, home_app):
        """测试首页有今日报告区域"""
        # Act
        home_app.run()

        # Assert - 应该有报告相关内容
        text_content = str(home_app.main)
        assert "报告" in text_content or "report" in text_content.lower()

    @mock.patch("evo_flywheel.db.crud.get_daily_report")
    def test_daily_report_shows_summary(self, mock_get_report, home_app):
        """测试今日报告显示摘要"""
        # Arrange
        mock_report = mock.Mock()
        mock_report.date = "2024-01-15"
        mock_report.top_papers = []
        mock_report.summary = "今日新增 10 篇高质量论文"
        mock_get_report.return_value = mock_report

        # Act
        home_app.run()

        # Assert
        text_content = str(home_app.main)
        assert "今日新增" in text_content or "10" in text_content


class TestHomePageErrorHandling:
    """首页错误处理测试"""

    @mock.patch("evo_flywheel.db.crud.get_papers")
    def test_handles_database_error_gracefully(self, mock_get_papers, home_app):
        """测试数据库错误时优雅处理"""
        # Arrange - 模拟数据库错误
        mock_get_papers.side_effect = Exception("Database connection failed")

        # Act - 应该不抛出异常
        home_app.run()

        # Assert - 页面仍然有内容（优雅降级）
        assert len(home_app.main) > 0


class TestHomePageNavigation:
    """首页导航测试"""

    def test_has_navigation_to_other_pages(self, home_app):
        """测试有导航到其他页面"""
        # Act
        home_app.run()

        # Assert - 应该有导航链接或按钮
        # Streamlit 使用 navigation 或 tabs
        assert hasattr(home_app, "navigation") or len(home_app.tabs) > 0
