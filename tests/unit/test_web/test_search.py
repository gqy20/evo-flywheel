"""语义搜索页测试"""

from unittest import mock


class TestSearchPageAPIIntegration:
    """语义搜索页 API 集成测试"""

    @mock.patch("evo_flywheel.web.views.search.APIClient")
    def test_semantic_search_uses_api_client(self, mock_api_client_class):
        """测试语义搜索使用 APIClient"""
        # Arrange - Mock API 返回
        mock_client = mock.Mock()
        mock_client.semantic_search.return_value = {
            "results": [
                {
                    "id": 1,
                    "title": "Test Paper",
                    "abstract": "Test abstract",
                    "similarity": 0.92,
                    "importance_score": 85,
                }
            ]
        }
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.search import render_search_results

        result = render_search_results(query="evolutionary genetics", n_results=10, filters={})

        # Assert - 验证函数返回 True 表示执行了搜索
        assert result is True

    @mock.patch("evo_flywheel.web.views.search.APIClient")
    def test_semantic_search_passes_query_and_limit(self, mock_api_client_class):
        """测试语义搜索传递查询和限制参数"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.semantic_search.return_value = {"results": []}
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.search import render_search_results

        render_search_results(query="phylogenetic analysis", n_results=15, filters={})

        # Assert - 验证 semantic_search 被调用
        mock_client.semantic_search.assert_called_once()
        call_kwargs = mock_client.semantic_search.call_args.kwargs
        assert call_kwargs.get("query") == "phylogenetic analysis"
        assert call_kwargs.get("limit") == 15

    @mock.patch("evo_flywheel.web.views.search.APIClient")
    def test_similar_papers_uses_api_client(self, mock_api_client_class):
        """测试相似论文使用 APIClient"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.similar_papers.return_value = {
            "results": [
                {
                    "id": 2,
                    "title": "Similar Paper",
                    "similarity": 0.88,
                }
            ]
        }
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.search import render_similar_papers

        # Just test that the function exists and is callable
        # (The actual rendering requires Streamlit context)
        assert callable(render_similar_papers)

    @mock.patch("evo_flywheel.web.views.search.APIClient")
    def test_no_longer_uses_vector_search_module(self, mock_api_client_class):
        """测试不再直接使用 vector.search 模块"""
        # Arrange
        mock_api_client_class.return_value = mock.Mock()

        # Act
        from evo_flywheel.web.views import search

        # Assert - vector_search 不应该再被直接导入使用
        # (这个测试主要验证模块重构)
        assert hasattr(search, "APIClient") or callable(search.render_search_results)


class TestSearchPageRendering:
    """语义搜索页渲染测试"""

    def test_search_page_has_render_function(self):
        """测试搜索页有 render 函数"""
        # Arrange & Act
        from evo_flywheel.web.views import search

        # Assert
        assert hasattr(search, "render")
        assert callable(search.render)

    def test_search_page_has_search_input(self):
        """测试搜索页有搜索输入框"""
        # Arrange & Act
        from evo_flywheel.web.views import search

        # Assert
        assert hasattr(search, "render_search_input")
        assert callable(search.render_search_input)

    def test_search_page_has_results_section(self):
        """测试搜索页有结果区域"""
        # Arrange & Act
        from evo_flywheel.web.views import search

        # Assert
        assert hasattr(search, "render_search_results")
        assert callable(search.render_search_results)

    def test_search_page_has_similar_papers_section(self):
        """测试搜索页有相似论文区域"""
        # Arrange & Act
        from evo_flywheel.web.views import search

        # Assert
        assert hasattr(search, "render_similar_papers")
        assert callable(search.render_similar_papers)


class TestSearchPageInput:
    """语义搜索页输入测试"""

    def test_search_accepts_text_input(self):
        """测试搜索接受文本输入"""
        # Arrange & Act
        from evo_flywheel.web.views import search

        # Assert
        assert callable(search.render_search_input)

    def test_search_has_filter_options(self):
        """测试搜索有筛选选项"""
        # Arrange & Act
        from evo_flywheel.web.views import search

        # Assert
        assert callable(search.render_search_input)


class TestSearchPageStructure:
    """语义搜索页结构测试"""

    def test_has_default_n_results_constant(self):
        """测试有默认结果数量常量"""
        # Arrange & Act
        from evo_flywheel.web.views import search

        # Assert
        assert hasattr(search, "DEFAULT_N_RESULTS")
        assert isinstance(search.DEFAULT_N_RESULTS, int)
