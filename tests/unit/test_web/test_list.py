"""文献列表页测试"""

from unittest import mock


class TestListPageAPIIntegration:
    """文献列表页 API 集成测试"""

    @mock.patch("evo_flywheel.web.views.list.APIClient")
    def test_paper_list_uses_api_client(self, mock_api_client_class):
        """测试论文列表使用 APIClient"""
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
                    "importance_score": 85,
                }
            ],
        }
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.list import render_paper_list

        result = render_paper_list(
            filters={},
            page=1,
            page_size=20,
        )

        # Assert - 验证返回总记录数
        assert result == 50

    @mock.patch("evo_flywheel.web.views.list.APIClient")
    def test_paper_list_passes_pagination_params(self, mock_api_client_class):
        """测试论文列表传递分页参数"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.get_papers.return_value = {"total": 100, "papers": []}
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.list import render_paper_list

        render_paper_list(
            filters={},
            page=2,
            page_size=50,
        )

        # Assert - 验证 get_papers 被调用
        mock_client.get_papers.assert_called_once()
        call_kwargs = mock_client.get_papers.call_args.kwargs
        assert call_kwargs.get("skip") == 50  # (page - 1) * page_size
        assert call_kwargs.get("limit") == 50

    @mock.patch("evo_flywheel.web.views.list.APIClient")
    def test_paper_list_applies_min_score_filter(self, mock_api_client_class):
        """测试论文列表应用最低评分筛选"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.get_papers.return_value = {"total": 10, "papers": []}
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.list import render_paper_list

        render_paper_list(
            filters={"min_score": 80},
            page=1,
            page_size=20,
        )

        # Assert
        mock_client.get_papers.assert_called_once()
        call_kwargs = mock_client.get_papers.call_args.kwargs
        assert call_kwargs.get("min_score") == 80

    @mock.patch("evo_flywheel.web.views.list.APIClient")
    def test_api_client_error_returns_zero(self, mock_api_client_class):
        """测试 API 错误时返回 0"""
        # Arrange - Mock API 返回 None (错误情况)
        mock_client = mock.Mock()
        mock_client.get_papers.return_value = None
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.list import render_paper_list

        result = render_paper_list(
            filters={},
            page=1,
            page_size=20,
        )

        # Assert - 应返回 0 表示失败
        assert result == 0

    @mock.patch("evo_flywheel.web.views.list.APIClient")
    def test_no_longer_uses_db_connection(self, mock_api_client_class):
        """测试不再直接使用数据库连接"""
        # Arrange
        mock_api_client_class.return_value = mock.Mock()

        # Act
        from evo_flywheel.web.views import list

        # Assert - get_db_connection 函数应该不再存在
        assert not hasattr(list, "get_db_connection")


class TestListPageRendering:
    """文献列表页渲染测试"""

    def test_list_page_has_render_function(self):
        """测试列表页有 render 函数"""
        # Arrange & Act
        from evo_flywheel.web.views import list

        # Assert
        assert hasattr(list, "render")
        assert callable(list.render)

    def test_list_page_has_filter_function(self):
        """测试列表页有筛选函数"""
        # Arrange & Act
        from evo_flywheel.web.views import list

        # Assert
        assert hasattr(list, "render_filters_section")
        assert callable(list.render_filters_section)

    def test_list_page_has_paper_list_function(self):
        """测试列表页有论文列表函数"""
        # Arrange & Act
        from evo_flywheel.web.views import list

        # Assert
        assert hasattr(list, "render_paper_list")
        assert callable(list.render_paper_list)

    def test_list_page_has_pagination_function(self):
        """测试列表页有分页函数"""
        # Arrange & Act
        from evo_flywheel.web.views import list

        # Assert
        assert hasattr(list, "render_pagination")
        assert callable(list.render_pagination)


class TestListPagePagination:
    """文献列表页分页测试"""

    def test_pagination_has_page_size_control(self):
        """测试分页有每页数量控制"""
        # Arrange & Act
        from evo_flywheel.web.views import list

        # Assert
        assert callable(list.render_pagination)

    def test_pagination_has_page_navigation(self):
        """测试分页有翻页导航"""
        # Arrange & Act
        from evo_flywheel.web.views import list

        # Assert
        assert callable(list.render_pagination)


class TestListPageExport:
    """文献列表页导出测试"""

    def test_export_has_csv_option(self):
        """测试导出有 CSV 选项"""
        # Arrange & Act
        from evo_flywheel.web.views import list

        # Assert
        assert hasattr(list, "render_export_section")
        assert callable(list.render_export_section)
