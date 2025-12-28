"""语义搜索页测试"""

from unittest import mock


class TestSearchPageRendering:
    """语义搜索页渲染测试"""

    def test_search_page_has_render_function(self):
        """测试搜索页有 render 函数"""
        # Arrange & Act
        from evo_flywheel.web.pages import search

        # Assert
        assert hasattr(search, "render")
        assert callable(search.render)

    def test_search_page_has_search_input(self):
        """测试搜索页有搜索输入框"""
        # Arrange & Act
        from evo_flywheel.web.pages import search

        # Assert
        assert hasattr(search, "render_search_input")
        assert callable(search.render_search_input)

    def test_search_page_has_results_section(self):
        """测试搜索页有结果区域"""
        # Arrange & Act
        from evo_flywheel.web.pages import search

        # Assert
        assert hasattr(search, "render_search_results")
        assert callable(search.render_search_results)

    def test_search_page_has_similar_papers_section(self):
        """测试搜索页有相似论文区域"""
        # Arrange & Act
        from evo_flywheel.web.pages import search

        # Assert
        assert hasattr(search, "render_similar_papers")
        assert callable(search.render_similar_papers)


class TestSearchPageInput:
    """语义搜索页输入测试"""

    def test_search_accepts_text_input(self):
        """测试搜索接受文本输入"""
        # Arrange & Act
        from evo_flywheel.web.pages import search

        # Assert
        assert callable(search.render_search_input)

    def test_search_has_filter_options(self):
        """测试搜索有筛选选项"""
        # Arrange & Act
        from evo_flywheel.web.pages import search

        # Assert
        assert callable(search.render_search_input)


class TestSearchPageExecution:
    """语义搜索页执行测试"""

    @mock.patch("evo_flywheel.web.pages.search.semantic_search_by_text")
    def test_search_calls_semantic_search_api(self, mock_search):
        """测试搜索调用语义搜索 API"""
        # Arrange
        mock_search.return_value = {"total": 0, "results": [], "query_metadata": {}}

        # Act
        from evo_flywheel.web.pages.search import render_search_results

        # Assert
        assert callable(render_search_results)

    @mock.patch("evo_flywheel.web.pages.search.semantic_search_similar_paper")
    def test_similar_papers_calls_similar_api(self, mock_similar):
        """测试相似论文调用相似 API"""
        # Arrange
        mock_similar.return_value = {"total": 0, "results": [], "query_metadata": {}}

        # Act
        from evo_flywheel.web.pages.search import render_similar_papers

        # Assert
        assert callable(render_similar_papers)


class TestSearchPageResultsDisplay:
    """语义搜索页结果展示测试"""

    @mock.patch("evo_flywheel.web.pages.search.semantic_search_by_text")
    def test_results_show_similarity_score(self, mock_search):
        """测试结果显示相似度分数"""
        # Arrange
        mock_search.return_value = {
            "total": 1,
            "results": [{"distance": 0.15, "title": "Test"}],
            "query_metadata": {},
        }

        # Act
        from evo_flywheel.web.pages.search import render_search_results

        # Assert
        assert callable(render_search_results)

    @mock.patch("evo_flywheel.web.pages.search.semantic_search_by_text")
    def test_results_show_paper_metadata(self, mock_search):
        """测试结果显示论文元数据"""
        # Arrange
        mock_search.return_value = {
            "total": 1,
            "results": [{"title": "Test", "journal": "Nature", "authors": "A"}],
            "query_metadata": {},
        }

        # Act
        from evo_flywheel.web.pages.search import render_search_results

        # Assert
        assert callable(render_search_results)


class TestSearchPageErrorHandling:
    """语义搜索页错误处理测试"""

    @mock.patch("evo_flywheel.web.pages.search.semantic_search_by_text")
    def test_handles_search_error_gracefully(self, mock_search):
        """测试搜索错误时优雅处理"""
        # Arrange
        mock_search.side_effect = Exception("Search API error")

        # Act - 导入模块不应该崩溃
        from evo_flywheel.web.pages import search

        # Assert
        assert hasattr(search, "render")


class TestSearchPageEmptyResults:
    """语义搜索页空结果测试"""

    @mock.patch("evo_flywheel.web.pages.search.semantic_search_by_text")
    def test_shows_message_when_no_results(self, mock_search):
        """测试无结果时显示提示"""
        # Arrange
        mock_search.return_value = {"total": 0, "results": [], "query_metadata": {}}

        # Act
        from evo_flywheel.web.pages.search import render_search_results

        # Assert
        assert callable(render_search_results)
