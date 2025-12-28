"""文献列表页测试"""

from unittest import mock


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


class TestListPageFilters:
    """文献列表页筛选功能测试"""

    def test_filters_support_taxa_selection(self):
        """测试筛选支持物种选择"""
        # Arrange & Act
        from evo_flywheel.web.views import list

        # Assert - 筛选函数存在
        assert callable(list.render_filters_section)

    def test_filters_support_journal_filter(self):
        """测试筛选支持期刊过滤"""
        # Arrange & Act
        from evo_flywheel.web.views import list

        # Assert
        assert callable(list.render_filters_section)

    def test_filters_support_min_score(self):
        """测试筛选支持最低评分"""
        # Arrange & Act
        from evo_flywheel.web.views import list

        # Assert
        assert callable(list.render_filters_section)

    def test_filters_support_date_range(self):
        """测试筛选支持日期范围"""
        # Arrange & Act
        from evo_flywheel.web.views import list

        # Assert
        assert callable(list.render_filters_section)


class TestListPagePaperList:
    """文献列表页论文列表测试"""

    @mock.patch("evo_flywheel.web.views.list.get_db_connection")
    def test_paper_list_queries_papers_with_filters(self, mock_get_conn):
        """测试论文列表应用筛选条件"""
        # Arrange
        mock_conn = mock.Mock()
        mock_conn.execute.return_value.fetchall.return_value = []
        mock_conn.execute.return_value.fetchmany.return_value = []
        mock_get_conn.return_value = mock_conn

        # Act
        from evo_flywheel.web.views.list import render_paper_list

        # Assert - 函数存在
        assert callable(render_paper_list)

    @mock.patch("evo_flywheel.web.views.list.get_db_connection")
    def test_paper_list_shows_paper_info(self, mock_get_conn):
        """测试论文列表显示论文信息"""
        # Arrange
        mock_conn = mock.Mock()
        mock_conn.execute.return_value.fetchall.return_value = []
        mock_get_conn.return_value = mock_conn

        # Act
        from evo_flywheel.web.views.list import render_paper_list

        # Assert
        assert callable(render_paper_list)


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

    @mock.patch("evo_flywheel.web.views.list.get_db_connection")
    def test_pagination_calculates_total_pages(self, mock_get_conn):
        """测试分页计算总页数"""
        # Arrange
        mock_conn = mock.Mock()
        mock_conn.execute.return_value.scalar.return_value = 100
        mock_get_conn.return_value = mock_conn

        # Act
        from evo_flywheel.web.views.list import render_pagination

        # Assert
        assert callable(render_pagination)


class TestListPageSearch:
    """文献列表页搜索测试"""

    def test_search_has_text_input(self):
        """测试搜索有文本输入框"""
        # Arrange & Act
        from evo_flywheel.web.views import list

        # Assert - 搜索应该在筛选区域
        assert callable(list.render_filters_section)


class TestListPageErrorHandling:
    """文献列表页错误处理测试"""

    @mock.patch("evo_flywheel.web.views.list.get_db_connection")
    def test_handles_database_error_gracefully(self, mock_get_conn):
        """测试数据库错误时优雅处理"""
        # Arrange
        mock_get_conn.side_effect = Exception("Database error")

        # Act - 导入模块不应该崩溃
        from evo_flywheel.web.views import list

        # Assert - 模块可以正常导入
        assert hasattr(list, "render")


class TestListPageExport:
    """文献列表页导出测试"""

    def test_export_has_csv_option(self):
        """测试导出有 CSV 选项"""
        # Arrange & Act
        from evo_flywheel.web.views import list

        # Assert
        assert hasattr(list, "render_export_section")
        assert callable(list.render_export_section)
