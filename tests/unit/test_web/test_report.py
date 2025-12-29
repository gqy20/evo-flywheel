"""报告生成页测试"""

from unittest import mock


class TestReportPageAPIIntegration:
    """报告生成页 API 集成测试"""

    @mock.patch("evo_flywheel.web.views.report.APIClient")
    def test_generate_report_data_uses_api_client(self, mock_api_client_class):
        """测试生成报告数据使用 APIClient"""
        # Arrange - Mock API 返回
        mock_client = mock.Mock()
        mock_client.get_papers.return_value = {
            "total": 50,
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
        from datetime import date

        from evo_flywheel.web.views.report import generate_report_data

        result = generate_report_data(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
            min_score=80,
            max_papers=10,
        )

        # Assert - 验证结果结构
        assert isinstance(result, dict)
        assert "total_papers" in result
        assert "top_papers" in result

    @mock.patch("evo_flywheel.web.views.report.APIClient")
    def test_generate_report_data_filters_by_min_score(self, mock_api_client_class):
        """测试生成报告数据按最低评分过滤"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.get_papers.return_value = {"total": 10, "papers": []}
        mock_api_client_class.return_value = mock_client

        # Act
        from datetime import date

        from evo_flywheel.web.views.report import generate_report_data

        generate_report_data(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
            min_score=85,
            max_papers=10,
        )

        # Assert - 验证 get_papers 被调用
        mock_client.get_papers.assert_called_once()
        call_kwargs = mock_client.get_papers.call_args.kwargs
        assert call_kwargs.get("min_score") == 85

    @mock.patch("evo_flywheel.web.views.report.APIClient")
    def test_generate_report_data_limits_papers(self, mock_api_client_class):
        """测试生成报告数据限制论文数量"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.get_papers.return_value = {"total": 50, "papers": []}
        mock_api_client_class.return_value = mock_client

        # Act
        from datetime import date

        from evo_flywheel.web.views.report import generate_report_data

        generate_report_data(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
            min_score=80,
            max_papers=15,
        )

        # Assert
        mock_client.get_papers.assert_called_once()
        call_kwargs = mock_client.get_papers.call_args.kwargs
        # limit 应该是 max_papers 的值
        assert call_kwargs.get("limit") == 15

    @mock.patch("evo_flywheel.web.views.report.APIClient")
    def test_api_client_error_returns_empty_dict(self, mock_api_client_class):
        """测试 API 错误时返回空字典"""
        # Arrange - Mock API 返回 None (错误情况)
        mock_client = mock.Mock()
        mock_client.get_papers.return_value = None
        mock_api_client_class.return_value = mock_client

        # Act
        from datetime import date

        from evo_flywheel.web.views.report import generate_report_data

        result = generate_report_data(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
            min_score=80,
            max_papers=10,
        )

        # Assert - 应返回空字典或默认值
        assert isinstance(result, dict)

    @mock.patch("evo_flywheel.web.views.report.APIClient")
    def test_no_longer_uses_db_connection(self, mock_api_client_class):
        """测试不再直接使用数据库连接"""
        # Arrange
        mock_api_client_class.return_value = mock.Mock()

        # Act
        from evo_flywheel.web.views import report

        # Assert - get_db_connection 函数应该不再存在
        assert not hasattr(report, "get_db_connection")


class TestReportPageRendering:
    """报告生成页渲染测试"""

    def test_report_page_has_render_function(self):
        """测试报告页有 render 函数"""
        # Arrange & Act
        from evo_flywheel.web.views import report

        # Assert
        assert hasattr(report, "render")
        assert callable(report.render)

    def test_report_page_has_generation_controls(self):
        """测试报告页有生成控件"""
        # Arrange & Act
        from evo_flywheel.web.views import report

        # Assert
        assert hasattr(report, "render_generation_controls")
        assert callable(report.render_generation_controls)

    def test_report_page_has_report_display(self):
        """测试报告页有报告展示区域"""
        # Arrange & Act
        from evo_flywheel.web.views import report

        # Assert
        assert hasattr(report, "render_report_display")
        assert callable(report.render_report_display)


class TestReportPageStructure:
    """报告生成页结构测试"""

    def test_has_default_date_range_constant(self):
        """测试有默认日期范围常量"""
        # Arrange & Act
        from evo_flywheel.web.views import report

        # Assert
        assert hasattr(report, "DEFAULT_DATE_RANGE_DAYS")
        assert isinstance(report.DEFAULT_DATE_RANGE_DAYS, int)

    def test_has_report_templates(self):
        """测试有报告模板"""
        # Arrange & Act
        from evo_flywheel.web.views import report

        # Assert
        assert hasattr(report, "REPORT_TEMPLATES")
        assert isinstance(report.REPORT_TEMPLATES, dict)
        assert len(report.REPORT_TEMPLATES) > 0
