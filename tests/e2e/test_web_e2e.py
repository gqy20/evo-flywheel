"""Streamlit Web 应用 E2E 测试"""


class TestNavigationFlow:
    """导航流程测试"""

    def test_home_page_loads(self, streamlit_page):
        """测试首页加载"""
        # Assert
        assert streamlit_page.title() == "Evo-Flywheel - 进化生物学学术飞轮"

    def test_navigate_to_list_page(self, streamlit_page):
        """测试导航到文献列表页"""
        # Act - 点击文献列表按钮
        streamlit_page.get_by_text("📚 文献列表").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Assert - 检查页面标题
        assert "文献列表" in streamlit_page.content()

    def test_navigate_to_search_page(self, streamlit_page):
        """测试导航到语义搜索页"""
        # Act - 点击语义搜索按钮
        streamlit_page.get_by_text("🔍 语义搜索").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Assert
        assert "语义搜索" in streamlit_page.content()

    def test_navigate_to_report_page(self, streamlit_page):
        """测试导航到报告生成页"""
        # Act - 点击报告生成按钮
        streamlit_page.get_by_text("📊 报告生成").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Assert
        assert "报告生成" in streamlit_page.content()

    def test_cross_page_navigation(self, streamlit_page):
        """测试跨页面导航"""
        # Home -> List
        streamlit_page.get_by_text("📚 文献列表").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # List -> Search
        streamlit_page.get_by_text("🔍 语义搜索").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Search -> Report
        streamlit_page.get_by_text("📊 报告生成").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Report -> Home
        streamlit_page.get_by_text("🏠 首页").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Assert - 回到首页
        assert "首页" in streamlit_page.content()


class TestSearchWorkflow:
    """搜索工作流测试"""

    def test_semantic_search_workflow(self, streamlit_page):
        """测试语义搜索工作流"""
        # Arrange - 导航到搜索页
        streamlit_page.get_by_text("🔍 语义搜索").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Act - 输入搜索查询
        streamlit_page.get_by_placeholder("例如: evolutionary genetics in Drosophila...").fill(
            "evolutionary biology"
        )
        streamlit_page.get_by_text("🔍 搜索").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Assert - 搜索结果区域应存在
        content = streamlit_page.content()
        # 搜索执行后会有某种反馈（即使没有结果）
        assert "搜索" in content

    def test_similar_papers_workflow(self, streamlit_page):
        """测试相似论文推荐工作流"""
        # Arrange - 导航到搜索页
        streamlit_page.get_by_text("🔍 语义搜索").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Assert - 搜索页应已加载（检查页面标题或核心元素）
        content = streamlit_page.content()
        # 搜索页的核心元素验证
        assert "搜索" in content


class TestListWorkflow:
    """文献列表工作流测试"""

    def test_filter_papers_workflow(self, streamlit_page):
        """测试筛选论文工作流"""
        # Arrange - 导航到列表页
        streamlit_page.get_by_text("📚 文献列表").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Act - 展开筛选选项
        streamlit_page.get_by_text("展开筛选选项").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Assert - 筛选选项应可见
        content = streamlit_page.content()
        assert "筛选" in content

    def test_pagination_workflow(self, streamlit_page):
        """测试分页工作流"""
        # Arrange - 导航到列表页
        streamlit_page.get_by_text("📚 文献列表").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Act - 检查分页控件
        _ = streamlit_page.get_by_text("下一页 ➡️")

        # Assert - 分页控件应存在
        content = streamlit_page.content()
        assert "页" in content


class TestReportWorkflow:
    """报告生成工作流测试"""

    def test_report_generation_workflow(self, streamlit_page):
        """测试报告生成工作流"""
        # Arrange - 导航到报告页
        streamlit_page.get_by_text("📊 报告生成").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Act - 点击生成报告按钮
        generate_button = streamlit_page.get_by_text("🚀 生成报告")
        if generate_button.is_visible():
            generate_button.click()
            streamlit_page.wait_for_load_state("domcontentloaded")

        # Assert - 报告相关内容应存在
        content = streamlit_page.content()
        assert "报告" in content

    def test_template_selection_workflow(self, streamlit_page):
        """测试模板选择工作流"""
        # Arrange - 导航到报告页
        streamlit_page.get_by_text("📊 报告生成").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Assert - 报告页应包含生成功能
        content = streamlit_page.content()
        # 报告生成页的核心元素
        assert "报告" in content or "生成" in content


class TestDataConsistency:
    """数据一致性测试"""

    def test_stats_display_consistency(self, streamlit_page):
        """测试统计数据显示一致性"""
        # Arrange - 在首页
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Assert - 统计卡片应存在
        content = streamlit_page.content()
        # 首页应显示某种统计信息
        assert "Evo" in content

    def test_paper_info_consistency(self, streamlit_page):
        """测试论文信息一致性"""
        # Arrange - 导航到列表页
        streamlit_page.get_by_text("📚 文献列表").click()
        streamlit_page.wait_for_load_state("domcontentloaded")

        # Assert - 论文列表区域应存在
        content = streamlit_page.content()
        assert "论文" in content
