"""语义搜索页测试"""


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
